import json, time, urllib.request, urllib.parse, re, html

# Phase 5: direct Springer/JSTOR page pulls for remaining 4 abstracts
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")

def extract_abstract(htmltext):
    # Springer meta citation abstract
    m = re.search(r'<meta name="dc.description" content="(.{100,6000}?)"\s*/?>', htmltext, re.S)
    if m:
        return html.unescape(m.group(1))
    m = re.search(r'<meta name="description" content="(.{100,6000}?)"\s*/?>', htmltext, re.S)
    if m:
        return html.unescape(m.group(1))
    # Og description
    m = re.search(r'property="og:description" content="(.{50,6000}?)"\s*/?>', htmltext, re.S)
    if m:
        return html.unescape(m.group(1))
    # JSTOR abstract div
    m = re.search(r'<div[^>]*class="[^"]*abstract[^"]*"[^>]*>(.{80,6000}?)</div>', htmltext, re.S | re.I)
    if m:
        return re.sub(r"<[^>]+>", " ", html.unescape(m.group(1)))
    return None

targets = {
 "Bozick2018": "https://link.springer.com/article/10.1007/s11292-018-9334-6",
 "Landenberger_Lipsey2005": "https://link.springer.com/article/10.1007/s11292-005-3541-7",
 "Skardhamar_Telle2012": "https://link.springer.com/article/10.1007/s10940-012-9166-x",
 "Uggen1998_jclc": "https://www.jstor.org/stable/1144260",
}

with open(r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/recid_v4_metadata.json", encoding="utf-8") as f:
    meta = json.load(f)

for k, url in targets.items():
    try:
        t = fetch(url)
        ab = extract_abstract(t)
        if ab and len(ab) > 100:
            meta[k]["page_abstract"] = ab
            meta[k]["page_url"] = url
            print(f"  {k}: OK len={len(ab)} :: {ab[:180]}")
        else:
            print(f"  {k}: fetched {len(t)} bytes but no abstract pattern matched")
    except Exception as e:
        print(f"  {k}: FAIL {e}")
    time.sleep(1.5)

with open(r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/recid_v4_metadata.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=1)

print("\nFINAL:")
for k, v in meta.items():
    has = bool(v.get("crossref_abstract") or v.get("openalex_abstract") or (v.get("pubmed_abstract") and v.get("pm_overlap_tokens", 0) >= 3) or v.get("page_abstract"))
    print(f"  {k}: {'ABSTRACT-LOADED' if has else 'MISSING — drop'}")
