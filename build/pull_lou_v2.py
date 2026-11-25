#!/usr/bin/env python3
# pull_lou_v2.py — extract Louisville (KY0500300) ACTUAL counts by month-year + any agency-level
# series, and get the full CDE payload structure. Then compute the murder-rate arc 2023->2025.
import json, urllib.request, socket
socket.setdefaulttimeout(30)
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

j = json.load(open("_pull_cde_lou_raw.json", encoding="utf-8"))
off = j["offenses"]
print("offenses keys:", list(off.keys()))
act = off.get("actuals", {})
print("actuals series names:", sorted(act.keys()))
res = {}
for name, vec in act.items():
    yrs = {}
    for kk in sorted(vec):
        y = kk.split("-")[1]
        yrs.setdefault(y, 0)
        yrs[y] += vec[kk]
    res[name] = {y: int(v) for y, v in sorted(yrs.items()) if y in ("2023", "2024", "2025")}
print(json.dumps(res, indent=1))
# rates per year too
rates = off.get("rates", {})
rres = {}
for name, vec in rates.items():
    yrs = {}
    for kk in sorted(vec):
        y = kk.split("-")[1]
        if y in ("2023", "2024", "2025"):
            yrs.setdefault(y, 0.0)
            yrs[y] += vec[kk]
    rres[name] = {y: round(v, 2) for y, v in sorted(yrs.items())}
print(json.dumps(rres, indent=1))
# populations block — what vintages does CDE carry?
pops = j.get("populations", {})
print("populations keys:", list(pops.keys())[:12])
print(json.dumps(pops, indent=0)[:1500])
json.dump({"actuals_by_year": res, "rates_by_year": rres, "populations_head": {k: pops[k] for k in list(pops)[:4]}},
          open("_pull_cde_lou_arc.json", "w", encoding="utf-8"), indent=1)
