#!/usr/bin/env python3
# pull_lou_jax_v1.py — THE FRESH PULL for the pre-registered civic call (Louisville KY selected).
# Routes, all keyless, verified this session:
#   [A] FBI CDE summarizer LATEST/summarized/agency/ORI/HOM  -> monthly offense RATES + counts class
#       (both Louisville KY0500300 and Jacksonville FL0160000 answer HTTP 200)
#   [B] Louisville ArcGIS Hub search API (data.louisvilleky.gov) -> dataset discovery (budget class)
#   NOTE the rate series is the CDE "United States Offenses" per-100k MONTHLY rate vector; counts come
#   from the same payload under offenses.counts (verify keys), populations block carries vintage.
import json, urllib.request, socket, statistics
socket.setdefaulttimeout(30)

def get(url, n=3000000):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read(n).decode("utf-8", "replace"))

out = {"built": "2026-11-25", "law": "fresh pull, route-labeled; no fabrication; direction-class only"}
# ---- [A] Louisville monthly HOM series, 2023-2025 ----
j = get("https://cde.ucr.cjis.gov/LATEST/summarized/agency/KY0500300/HOM?from=01-2023&to=12-2025")
off = j["offenses"]
out["keys_in_offenses"] = list(off.keys())
# find the counts block
for k, v in off.items():
    if isinstance(v, dict):
        sub = list(v.keys())[:6]
        out.setdefault("offenses_structure", {})[k] = sub
with open("_pull_cde_lou_raw.json", "w", encoding="utf-8") as f:
    json.dump(j, f)
print("offenses keys:", out["keys_in_offenses"])
print("structure:", json.dumps(out["offenses_structure"], indent=1))
# tooltips + populations
out["populations_head"] = {k: j["populations"][k] for k in list(j["populations"])[:3]} if "populations" in j else None
# extract Louisville city-level monthly rates per year
rates = off.get("rates", {})
city_keys = sorted(rates.keys())
out["rate_series_names"] = city_keys
with open("_pull_cde_lou_summary.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
for name in city_keys[:8]:
    vec = rates[name]
    yrs = {}
    for kk in sorted(vec):
        if "2024" in kk or "2025" in kk or "2023" in kk:
            y = kk.split("-")[1]
            yrs.setdefault(y, []).append(vec[kk])
    print(name, {y: round(sum(v), 2) for y, v in sorted(yrs.items())})
