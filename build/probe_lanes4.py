#!/usr/bin/env python3
# probe_lanes4.py — parse the Louisville hub dataset hits (homicide, budget) into ids+names,
# and test the FBI CDE summarizer without /LATEST and with alternate casing.
import json, urllib.request, socket
socket.setdefaulttimeout(25)
UA = {"User-Agent": "Mozilla/5.0"}
def get(url, n=200000):
    UA = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req) as r:
        return r.status, r.read(n).decode("utf-8", "replace")

out = {}
for q in ["homicide", "murder", "operating budget", "crime"]:
    try:
        s, b = get(f"https://data.louisvilleky.gov/api/search/v1/collections/dataset/items?q={q}&limit=12")
        j = json.loads(b)
        feats = j.get("features", [])
        hits = []
        for f in feats:
            p = f.get("properties", {})
            hits.append({"id": f.get("id"), "name": p.get("name"), "type": p.get("type"),
                         "updated": p.get("updatedAt") or p.get("modified"),
                         "snippet": (p.get("snippet") or "")[:120]})
        out[q] = {"status": s, "n_hits": len(hits), "hits": hits}
    except Exception as e:
        out[q] = {"err": str(e)[:200]}

# FBI CDE summarizer — variant routes
cde = [
 "https://cde.ucr.cjis.gov/LATEST/summarized/agency/KY0500300/HOM?from=01-2024&to=12-2025",
 "https://cde.ucr.cjis.gov/summarized/agency/KY0500300/HOM?from=01-2024&to=12-2025",
 "https://cde-api.ucr.cjis.gov/LATEST/summarized/agency/KY0500300/HOM?from=01-2024&to=12-2025",
]
out["cde_variants"] = []
for u in cde:
    try:
        s, b = get(u, 4000)
        out["cde_variants"].append({"url": u, "status": s, "body": b[:600]})
    except Exception as e:
        out["cde_variants"].append({"url": u, "err": str(e)[:150]})

with open("probe_lanes4_v1.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
for q in ["homicide", "murder", "operating budget", "crime"]:
    v = out.get(q, {})
    print("==", q, v.get("n_hits"), v.get("err", ""))
    for h in (v.get("hits") or [])[:12]:
        print("   -", h["id"], "|", h["name"], "|", h.get("type"), "|", h.get("updated"))
print()
for c in out["cde_variants"]:
    print("CDE:", c.get("status"), c.get("err", ""), (c.get("body") or "")[:120])
