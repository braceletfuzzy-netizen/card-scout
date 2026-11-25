#!/usr/bin/env python3
# probe_lanes3.py — Louisville hub catalog search (homicide + budget) + FBI CDE via the keyless
# open route the wide-lane used (cde.ucr.cjis.gov LATEST summarizer, no API key).
import json, urllib.request, socket
socket.setdefaulttimeout(20)
UA = {"User-Agent": "Mozilla/5.0"}
def get(url, n=100000):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req) as r:
        return r.status, r.read(n).decode("utf-8", "replace")

out = {}
# Louisville hub search API (ArcGIS Hub v3 search endpoint)
for q in ["homicide", "murder", "budget", "crime"]:
    try:
        s, b = get(f"https://data.louisvilleky.gov/api/search/v1/collections/dataset/items?q={q}&limit=10")
        out.setdefault("lou_search", {q: {"status": s, "body": b[:4000]}})
    except Exception as e:
        out.setdefault("lou_search", {})[q] = {"err": str(e)[:150]}
# alternative hub domain
try:
    s, b = get("https://louisville-metro-opendata-lojic.hub.arcgis.com/api/search/v1/collections/dataset/items?q=homicide&limit=10")
    out["lojic_search"] = {"status": s, "body": b[:4000]}
except Exception as e:
    out["lojic_search"] = {"err": str(e)[:150]}
# FBI CDE keyless summarizer (the banked wide-lane route; no API key needed there)
for ori, name in [("KY0500300", "Louisville Metro PD"), ("KYLOJIC00", "Louisville LOJIC")]:
    url = f"https://cde.ucr.cjis.gov/LATEST/summarized/agency/{ori}/HOM?from=01-2024&to=12-2025"
    try:
        s, b = get(url, 8000)
        out.setdefault("cde_summarizer", {})[name] = {"url": url, "status": s, "body": b[:2000]}
    except Exception as e:
        out.setdefault("cde_summarizer", {})[name] = {"url": url, "err": str(e)[:150]}
with open("probe_lanes3_v1.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
for k, v in out.items():
    print("==", k)
    if isinstance(v, dict):
        for q, r in v.items():
            print("  ", q, "->", r.get("status"), (r.get("body") or r.get("err"))[:200] if isinstance(r, dict) else str(r)[:200])
    else:
        print(str(v)[:400])
