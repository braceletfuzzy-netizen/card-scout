#!/usr/bin/env python3
# pull_lou_v4.py — Louisville Metro Police (KY0568000) HOM monthly actuals 2013-2025 + Jacksonville
# (FL0160000) 2023-2025 refresh. Same route/format as the banked wide-lane caches. Then annual arcs.
import json, urllib.request, socket, time
socket.setdefaulttimeout(60)
def getjson(url, tries=3):
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(url).read())
        except Exception as e:
            if i == tries-1:
                print("FAIL", url[:90], str(e)[:120]); return None
            time.sleep(3)

cities = {"Louisville (LMPD)": "KY0568000", "Jacksonville (JSO)": "FL0160000"}
arc = {}
for city, ori in cities.items():
    yrs = {}
    y_lo, y_hi = (2013, 2025) if "Louisville" in city else (2023, 2025)
    for y in range(y_lo, y_hi + 1):
        d = getjson(f"https://cde.ucr.cjis.gov/LATEST/summarized/agency/{ori}/HOM?from=01-{y}&to=12-{y}")
        if not d: continue
        off = d.get("offenses", {})
        act = off.get("actuals") or {}
        rat = off.get("rates") or {}
        cov = (d.get("tooltips", {}).get("Percent of Population Coverage") or {})
        # months of data coverage this year (from coverage pct) + agency actual counts
        ag_keys = [k for k in act if "Sheriff" in k or "Metro" in k or "Louisville Metro" in k]
        ag_counts = {}
        for k in act:
            if city.startswith("Louisville") and "Louisville Metro" not in k: continue
            if city.startswith("Jacksonville") and "Sheriff" not in k: continue
            for kk, v in act[k].items():
                mo = int(kk.split("-")[0]); yy = int(kk.split("-")[1])
                if yy != y: continue
                ag_counts[kk] = ag_counts.get(kk, 0) + (v or 0)
        total = int(sum(ag_counts.values())) if ag_counts else None
        n_months = len(ag_counts)
        yrs[y] = {"ori": ori, "counts_by_month": ag_counts, "annual_total": total, "n_months_nonzero_or_reported": n_months}
        time.sleep(0.2)
    arc[city] = {y: v for y, v in yrs.items()}

# annual summary with coverage flags (months where the agency reported)
def annual_row(city, y):
    v = arc[city].get(y)
    if not v: return {"year": y, "status": "no-payload"}
    cnt = v["counts_by_month"]
    # a month counts as reported if its key exists (zero allowed only with coverage)
    return {"year": y, "annual_total": v["annual_total"], "months_keys": len(cnt)}

summary = {}
for city in arc:
    summary[city] = {y: annual_row(city, y) for y in sorted(arc[city])}
out = {"built": "2026-11-25", "routes": {c: f"cde.ucr.cjis.gov/LATEST/summarized/agency/{cities[c].split(' ')[-1] if False else O}/HOM?from=01-Y&to=12-Y" for c, O in [(k, v) for k, v in cities.items()]},
       "annual": arc, "summary": summary}
with open("civic_call_inputs_v1.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
for city, s in summary.items():
    print("==", city)
    for y, r in s.items():
        print(f"  {y}: total={r.get('annual_total')} months_keys={r.get('months_keys')}")
