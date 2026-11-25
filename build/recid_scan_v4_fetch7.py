import json, urllib.request, urllib.parse, re, html, time

# Phase 7: fix author metadata + final targeted search for mentoring/family-support RCT rows
UA = {"User-Agent": "PolyScout-peer-scan/1.0 (mailto:research-ops@example.org)"}

def cr(doi_or_query, bibliographic=False):
    if bibliographic:
        url = "https://api.crossref.org/works?query.bibliographic=" + urllib.parse.quote(doi_or_query) + "&rows=5&select=DOI,title,author,issued,container-title,abstract,is-referenced-by-count"
    else:
        url = f"https://api.crossref.org/works/{doi_or_query}"
    req = urllib.request.Request(url, headers=UA)
    d = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return d["message" if not bibliographic else "items"]

for doi in ["10.1007/s10940-012-9166-x", "10.2139/ssrn.4083166"]:
    m = cr(doi)
    au = ", ".join(f"{a.get('given','')} {a.get('family','')}".strip() for a in (m.get("author") or []))
    print(f"{doi} -> {au}")

# targeted searches
for key, q in {
    "duwe_mentoring": "Duwe Wraparound case management mentoring recidivism randomized",
    "faith_based": "faith-based prison program recidivism evaluation InnerChange",
    "restorative": "Bonta restorative justice reentry recidivism experiment",
    "job_retention": "Cook employment retention prisoner reentry randomized evaluation recidivism",
    "family_visit": "Bales family visitation recidivism prison visitation",
}.items():
    items = cr(q, bibliographic=True)
    print(f"=== {key} ===")
    for it in items:
        doi2 = it.get("DOI", "")
        t = (it.get("title") or [""])[0]
        au = ", ".join(a.get("family", "") for a in (it.get("author") or [])[:3])
        yr = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        ab = it.get("abstract")
        print(f"  {doi2} | {yr} | {au} | {t[:90]} | abst={'Y' if ab else 'n'}")
    time.sleep(0.8)
