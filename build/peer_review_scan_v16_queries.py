import json, time, urllib.parse, urllib.request, re
import os

OUT = r"C:\Users\J\peer_review_scan_v16_raw.jsonl"
KEY = "peer_review_scan_v16_queries.json"
os.chdir(r"C:\Users\J")

QUERIES = {
  "T1_food_housing": [
    "food insecurity child academic achievement effect",
    "school breakfast program academic outcomes effect",
    "SNAP participation child outcomes education effect",
    "housing vouchers children outcomes criminal conviction MTO",
    "housing instability children school mobility achievement",
    "eviction children outcomes effect",
    "crowded housing children outcomes effect",
  ],
  "T2_safety_care": [
    "psychiatric beds violent crime effect",
    "deinstitutionalization crime homicides effect",
    "violence intervention program effect size",
    "hospital-based violence intervention program outcomes",
    "Cure Violence community violence reduction effect",
    "focused deterrence crime effect size meta-analysis",
    "childhood lead exposure crime IQ effect",
  ],
  "T3_belonging": [
    "social capital crime effect",
    "collective efficacy violence neighborhood effect",
    "Big Brothers Big Sisters mentee outcomes effect",
    "youth mentoring meta-analysis effect size",
    "community organizations crime reduction effect",
    "summer job program youth violence effect",
    "religious congregation crime neighborhood effect",
  ],
  "T4_edu_transport": [
    "school spending increases adult outcomes Jackson",
    "school finance reform adult earnings poverty effect",
    "teacher value-added adult outcomes effect",
    "class size reduction long-term outcomes",
    "transit access employment outcomes effect",
    "school bus transportation attendance achievement effect",
    "public transit poor job access effect",
  ],
  "T5_choice_set": [
    "Opportunity Insights Chetty neighborhood effects children",
    "Opportunity Atlas intergenerational mobility children moving",
    "moving to opportunity children adult outcomes",
    "children savings accounts asset effects welfare",
    "SEED Oklahoma 529 savings outcomes",
    "housing mobility children future earnings",
  ],
}

try:
    done = {json.loads(l)["query"] for l in open(OUT, encoding="utf-8") if l.strip()}
except FileNotFoundError:
    done = {}

def xref(q):
    url = "https://api.crossref.org/works?query=" + urllib.parse.quote(q) + \
          "&rows=6&select=title,container-title,issued,is-referenced-by-count,DOI,type"
    req = urllib.request.Request(url, headers={"User-Agent": "research-scan/1.0 (mailto:scan@example.org)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except Exception as e:
        return {"error": str(e)}

with open(OUT, "a", encoding="utf-8") as f:
    for tier, qs in QUERIES.items():
        for q in qs:
            if q in done:
                print("skip (done):", q)
                continue
            d = xref(q)
            if "error" in d:
                rec = {"tier": tier, "query": q, "error": d["error"]}
            else:
                rec = {"tier": tier, "query": q, "hits": []}
                for it in d.get("message", {}).get("items", []):
                    t = (it.get("title") or [""])[0]
                    rec["hits"].append({
                        "title": t,
                        "venue": (it.get("container-title") or [""])[0],
                        "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
                        "cites": it.get("is-referenced-by-count", 0),
                        "doi": it.get("DOI", ""),
                        "type": it.get("type", ""),
                    })
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            print(f"{tier}: {q} -> {len(rec.get('hits', []))} hits")
            time.sleep(1.2)

print("ALL QUERIES DONE")
