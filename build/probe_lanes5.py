#!/usr/bin/env python3
# probe_lanes5.py — pull the Louisville homicide/CCR dataset item details (names, service URLs)
# + the FBI CDE summarized HOM monthly series for Louisville (KY0500300) 2024+2025,
# and check for a Jacksonville (FL0160000) series on the same CDE summarizer.
import json, urllib.request, socket, datetime
socket.setdefaulttimeout(30)

def get(url, n=2000000):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return r.status, r.read(n).decode("utf-8", "replace")

out = {}
# 1) name-resolution for the hub ids found (search items carry ids; fetch item via opendata api)
ids = ["4a0789c91e7b40d69a19cd1ee3f7ace7","44b6c06b060147448046f956a311da69","c31f9eaebdf3451a868815ac7f0175f8",
       "7abaa5c6b3844aa991b8b4d49ffe19f4","2225de04ba43422eb0e0a48fa05f6ce5"]
for i in ids:
    try:
        s, b = get(f"https://data.louisvilleky.gov/api/search/v1/datasets/{i}")
        j = json.loads(b)
        p = j.get("properties", {})
        out.setdefault("hub_items", []).append({"id": i, "name": p.get("name"), "type": p.get("type"),
            "service": p.get("serviceItemId") or p.get("url"), "snippet": (p.get("snippet") or "")[:150]})
    except Exception as e:
        out.setdefault("hub_items", []).append({"id": i, "err": str(e)[:150]})
# 2) CDE summarized HOM for Louisville 2023-2025 (monthly rates shown; want counts too)
for variant in ["HOM", "OFFENSES"]:
    url = f"https://cde.ucr.cjis.gov/LATEST/summarized/agency/KY0500300/{variant}?from=01-2023&to=12-2025"
    try:
        s, b = get(url, 200000)
        out.setdefault("cde_lou", {})[variant] = {"status": s, "body_head": b[:600]}
        j = json.loads(b)
        out.setdefault("cde_lou", {})[variant+"_keys"] = list(j.keys())[:10]
    except Exception as e:
        out.setdefault("cde_lou", {})[variant] = {"err": str(e)[:150]}
# Jacksonville same route
for ori in ["FL0160000"]:
    url = f"https://cde.ucr.cjis.gov/LATEST/summarized/agency/{ori}/HOM?from=01-2023&to=12-2025"
    try:
        s, b = get(url, 200000)
        out.setdefault("cde_jax", {})[ori] = {"status": s, "body_head": b[:600]}
    except Exception as e:
        out.setdefault("cde_jax", {})[ori] = {"err": str(e)[:150]}
with open("probe_lanes5_v1.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in out.items() if k != "hub_items"}, indent=1)[:2500])
print()
for h in out.get("hub_items", []):
    print(h)
