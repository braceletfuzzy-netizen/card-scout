import json, time, urllib.request, urllib.parse, html, re

# Phase 3: Pull DOI metadata for 17 candidate papers across Crossref + PubMed + open pages.
UA = {"User-Agent": "PolyScout-peer-scan/1.0 (mailto:research-ops@example.org)"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

CR = "https://api.crossref.org/works/"
PM = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}&rettype=abstract&retmode=text"
PMSEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=1&term={}"

cands = {
 "Bozick2018": "10.1007/s11292-018-9334-6",
 "Landenberger_Lipsey2005": "10.1007/s11292-005-3541-7",
 "Lipsey2007_Campbell": "10.4073/csr.2007.6",
 "Davis2013_RR266": "10.7249/rr266",
 "Duwe2011_mcorp": "10.1080/07418825.2011.555414",
 "Skardhamar_Telle2012": "10.1007/s10940-012-9166-x",
 "Visher_Travis2003": "10.1146/annurev.soc.29.010202.095931",
 "PrisonJ2014": "10.1177/0032885514548009",
 "Kim2026_jsocsci": "10.65150/ep-jsshrs/v2e7/2026-29",
 "Wilson2000_econ": "10.1016/s0047-2352(01)00123-4",
 "Davis2013_rb9728": "10.7249/rb9728",
 "Duwe2013_cjs": "10.1080/1478601x.2013.850081",
 "Berger-Gross2022_ss": "10.2139/ssrn.4083166",
 "Mancino2023_ss_1": "10.2139/ssrn.4509303",
 "Kovandzic2002": "10.1016/j.ijlcj.2025.100800",
 "Aos2000_wa": "10.1037/e455022008-001",
 "HarperChitty2005": "10.1037/e455022008-001",
 "Uggen1998_jclc": "10.2307/1144260",
 "Laub_sampson1990": "10.2307/2095859",
 "Bhuller2016_wp": "10.3386/w22648",
}

out = {}
for key, doi in cands.items():
    rec = {}
    try:
        d = get(urllib.parse.quote(CR + doi, safe="") + "/transforms" if False else CR + doi)
        m = d["message"]
        rec["crossref_doi"] = doi
        rec["crossref_title"] = (m.get("title") or [""])[0]
        rec["crossref_year"] = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
        rec["crossref_venue"] = (m.get("container-title") or [""])[0]
        rec["crossref_abstract"] = m.get("abstract")
        rec["crossref_cites"] = m.get("is-referenced-by-count")
        print(f"  CR  {key}: OK title={(rec['crossref_title'] or '')[:60]}")
    except Exception as e:
        rec["crossref_error"] = str(e)
        print(f"  CR  {key}: FAIL {e}")

    # PubMed search
    try:
        s = get(PMSEARCH.format(urllib.parse.quote(rec.get("crossref_title", "") or key)))
        pmid = (s.get("esearchresult", {}).get("idlist") or [None])[0]
        rec["pmid"] = pmid
        if pmid:
            r2 = urllib.request.Request(PM.format(pmid), headers=UA)
            rec["pubmed_abstract"] = urllib.request.urlopen(r2, timeout=30).read().decode("utf-8", "ignore")
            print(f"  PM  {key}: OK pmid={pmid} len={len(rec['pubmed_abstract'])}")
        else:
            rec["pubmed_abstract"] = None
            print(f"  PM  {key}: no-hit")
    except Exception as e:
        rec["pubmed_error"] = str(e)
        print(f"  PM  {key}: FAIL {e}")
    time.sleep(0.6)
    out[key] = rec

with open(r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/recid_v4_metadata.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
print("SAVED metadata")
