import json, time, urllib.request, urllib.parse

# Phase 1: search Crossref across the BOB-THIRD recidivism threads, list candidates
UA = {"User-Agent": "PolyScout-peer-scan/1.0 (mailto:research-ops@example.org)"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

threads = {
  "education_rct": "correctional education recidivism meta-analysis",
  "education_rand": "Davis correctional education meta-analysis RAND recidivism",
  "vocational": "vocational training prison recidivism employment",
  "jobs_null": "employment intervention post-release crime causal effect",
  "community_social_capital": "social capital community reentry recidivism",
  "mentoring": "mentoring program reentry recidivism evaluation",
  "cbt": "cognitive behavioral therapy offender recidivism meta-analysis",
  "housing": "housing first prisoner reentry recidivism",
  "sca": "Second Chance Act evaluation recidivism",
  "family": "family support prisoner reentry recidivism",
  "education2": "education while incarcerated recidivism reduction",
}

results = {}
for key, q in threads.items():
    url = ("https://api.crossref.org/works?query.bibliographic=" +
           urllib.parse.quote(q) + "&rows=8&select=DOI,title,author,issued,container-title,abstract,is-referenced-by-count,type&sort=relevance")
    try:
        d = get(url)
        items = d.get("message", {}).get("items", [])
        results[key] = [{"doi": it.get("DOI"), "title": (it.get("title") or [""])[0][:120],
                         "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
                         "venue": (it.get("container-title") or [""])[0][:60],
                         "cites": it.get("is-referenced-by-count"), "type": it.get("type"),
                         "has_abstract": bool(it.get("abstract"))} for it in items]
        print(f"### {key} OK ({len(items)} items)")
    except Exception as e:
        results[key] = [{"error": str(e)}]
        print(f"### {key} FAIL {e}")
    time.sleep(1.0)

with open(r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/recid_v4_crossref_candidates.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=1)
print("SAVED candidates")
