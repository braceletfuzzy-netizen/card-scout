import json, time, urllib.request, urllib.parse, re

# Phase 4: fill missing abstracts via OpenAlex (inverted-index), PubMed (retmode=json), publisher pages.
UA = {"User-Agent": "PolyScout-peer-scan/1.0 (mailto:research-ops@example.org)",
      "Accept": "application/json"}

def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

OA = "https://api.openalex.org/works/doi:{}"
PMSEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=1&retmode=json&term={}"
PM = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}&rettype=abstract&retmode=text"

with open(r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/recid_v4_metadata.json", encoding="utf-8") as f:
    meta = json.load(f)

def deinvert(inv):
    if not inv: return None
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))

need = [k for k, v in meta.items() if not v.get("crossref_abstract") and not v.get("pubmed_abstract")]
print("Need abstract:", need)

oa_fail = 0
for k in list(need):
    doi = meta[k].get("crossref_doi")
    if not doi: continue
    try:
        d = get_json(OA.format(doi))
        ab = deinvert(d.get("abstract_inverted_index"))
        if ab:
            meta[k]["openalex_abstract"] = ab
            meta[k]["openalex_oa_url"] = d.get("open_access", {}).get("oa_url")
            print(f"  OA {k}: OK len={len(ab)}")
        else:
            print(f"  OA {k}: no abstract in OpenAlex")
    except Exception as e:
        oa_fail += 1
        print(f"  OA {k}: FAIL {e}")
        if "429" in str(e) and oa_fail >= 2:
            print("!! OpenAlex hard-429 pattern — backing off 30s and continuing with pause")
            time.sleep(30)
    time.sleep(1.2)

# PubMed pass (now with retmode=json)
need2 = [k for k in meta if not meta[k].get("crossref_abstract") and not meta[k].get("openalex_abstract")]
print("Still need abstract:", need2)
for k in need2:
    title = meta[k].get("crossref_title", "")
    if not title: continue
    try:
        s = get_json(PMSEARCH.format(urllib.parse.quote(title[:120])))
        pmid = (s.get("esearchresult", {}).get("idlist") or [None])[0]
        if pmid:
            r2 = urllib.request.Request(PM.format(pmid), headers=UA)
            body = urllib.request.urlopen(r2, timeout=30).read().decode("utf-8", "ignore")
            # sanity: title should overlap with crossref title
            ovl = set(w.lower() for w in title.split()[:6]) & set(w.lower() for w in body.split()[:200])
            meta[k]["pubmed_abstract"] = body
            meta[k]["pmid"] = pmid
            meta[k]["pm_overlap_tokens"] = len(ovl)
            print(f"  PM {k}: OK pmid={pmid} overlap_tok={len(ovl)} len={len(body)}")
        else:
            print(f"  PM {k}: no PubMed hit")
    except Exception as e:
        print(f"  PM {k}: FAIL {e}")
    time.sleep(0.8)

with open(r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/recid_v4_metadata.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=1)

# Final status
print("\nFINAL STATUS:")
for k, v in meta.items():
    has = bool(v.get("crossref_abstract") or v.get("openalex_abstract") or (v.get("pubmed_abstract") and v.get("pm_overlap_tokens", 0) >= 3))
    print(f"  {k}: {'ABSTRACT-LOADED' if has else 'MISSING'}")
