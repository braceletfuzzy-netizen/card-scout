import json, time, urllib.request, urllib.parse

# Anchored pass: known anchor studies + author-anchored supplement (Phase 2)
UA = {"User-Agent": "PolyScout-peer-scan/1.0 (mailto:research-ops@example.org)"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

anchors = {
  "Davis2013_rand": "Davis Bozick Steele Correctional education in adult prisons meta-analysis",
  "Aos2011_wsjipp": "Aos Miller Drake Washington State Institute Public Policy adult corrections juvenile",
  "Landenberger_Lipsey2005": "Landenberger Lipsey positive effects treatment criminal offenders meta-analysis",
  "Lipsey2009": "Lipsey Landenberger Wilson effects cognitive behavioral programs offenders",
  "Visher_travis2003": "Visher Travis Transitions from prison to community",
  "Laub_sampson": "Laub Sampson Sharing in life of success maternal social bonds desistance",
  "Villetaz_king_2005": "Villetaz King Wheller meta-analysis vocational training employment offenders",
  "Visher2020_mentoring": "Visher La Vigne mentoring former prisoners recidivism evaluation",
  "Bouffard_2000": "Bouffard educational intervention incarceration recidivism",
  "Harper_chitty": "Harper Chitty impact of corrections on reoffending report",
  "Mears": "Mears Cochran prisoner reentry employment program meta-analysis",
  "Braga_cse": "Braga Davis The consequences of the Second Chance Act",
  "Duwe_housing": "Duwe Minnesota Comprehensive Offender Reentry Plan recidivism",
  "Duwe_2017": "Duwe individualized reentry wraparound services recidivism",
  "Nally_2014": "NallyLockwood Tafr post-release employment recidivism",
  "Severson_mentoring": "Severson Bruns Mentoring clients community corrections recidivism",
  "Cid_martins2009": "Cid Martins Recidivism and employment key issues",
  "Uggen1999": "Uggen work as turning point criminal desistance",
  "Bouffard2003": "Bouffard examining relationship between participation in prison education and recidivism",
}

out = {}
for key, q in anchors.items():
    url = ("https://api.crossref.org/works?query.bibliographic=" +
           urllib.parse.quote(q) + "&rows=5&select=DOI,title,author,issued,container-title,abstract,is-referenced-by-count,type&sort=relevance")
    try:
        d = get(url)
        items = d.get("message", {}).get("items", [])
        out[key] = items
        print(f"### {key} OK ({len(items)} items)")
    except Exception as e:
        out[key] = [{"error": str(e)}]
        print(f"### {key} FAIL {e}")
    time.sleep(1.0)

with open(r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/recid_v4_anchors.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
print("SAVED anchors raw")
