#!/usr/bin/env python3
# audit trail for backwards_test_v1: every scored (model, city, t, lag) pair with predicted vs actual
import json
import numpy as np

BUILD = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
rows = [json.loads(l) for l in open(f"{BUILD}/maslow_joint_panel_v1.jsonl", encoding="utf-8") if l.strip()]
O = {}
for k, v in json.load(open(f"{BUILD}/_backwards_outcome_series_v1.json", encoding="utf-8")).items():
    O[(k.split("|")[0], int(k.split("|")[1]))] = v
PARTIAL = {2026}
SPEC = {
 "FE-3_maslow_joint_t0": (["care_per_100k", "cost_burden_30pct_plus_share", "median_home_value", "snap_receipt_share_pct", "bachelors_pct"], [-0.181, -0.280, -0.099, 0.640, -0.003], "murder_rate"),
 "FE-3_arc_tplus1": (["care_per_100k", "cost_burden_30pct_plus_share", "median_home_value", "snap_receipt_share_pct", "bachelors_pct"], [-0.197, 0.056, -0.263, 0.544, -0.189], "murder_rate_t+1"),
 "FE-6_care_plus_unemp": (["care_per_100k", "unemployment_rate"], [-0.304, 0.312], "murder_rate"),
 "FE-2_care_cage_bookings": (["care_per_100k", "cage_per_100k", "bookings_per_1000"], [-0.452, 0.419, 0.013], "murder_rate"),
}
allrecs = []
for name, (spec, betas, ycol) in SPEC.items():
    complete = []
    for r in rows:
        vals = [r.get(col) for col in spec]
        if any(v is None for v in vals) or r.get(ycol) is None:
            continue
        complete.append({"city": r["city"], "year": r["year"], "X": vals, "y": r[ycol]})
    cm = {}
    for c in sorted({r["city"] for r in complete}):
        sub = [r for r in complete if r["city"] == c]
        X = np.array([r["X"] for r in sub], float)
        ys = np.array([r["y"] for r in sub], float)
        cm[c] = (X.mean(axis=0), X.std(axis=0), float(ys.mean()), float(ys.std()), len(sub), sorted(r["year"] for r in sub))
    for r in rows:
        c, y = r["city"], r["year"]
        if c not in cm:
            continue
        mean_x, sd_x, mean_y, sd_y, nrows, yyears = cm[c]
        vals = [r.get(col) for col in spec]
        if any(v is None for v in vals):
            continue
        if any(s <= 0 for s in sd_x) or sd_y <= 0:
            continue  # degenerate city frame: skip honestly
        z = (np.array(vals) - mean_x) / sd_x
        pred = mean_y + float(np.dot(betas, z)) * sd_y
        for k in range(1, 6):
            if y + k in PARTIAL:
                continue
            o = O.get((c, y + k))
            if not o or o.get("rate") is None:
                continue
            hit = (pred > mean_y) == (o["rate"] > mean_y)
            allrecs.append({
                "model": name, "city": c, "t": y, "lag": k, "year_scored": y + k,
                "pred": round(pred, 2), "pred_delta_from_mean": round(pred - mean_y, 2),
                "actual": o["rate"], "actual_delta_from_mean": round(o["rate"] - mean_y, 2),
                "direction_hit": hit, "abs_err": round(abs(pred - o["rate"]), 2),
                "outcome_src": o.get("rate_src"),
                "city_frame": {"n": nrows, "years": [min(yyears), max(yyears)]},
            })
json.dump(allrecs, open(f"{BUILD}/backwards_test_v1_scored_records.json", "w", encoding="utf-8"), indent=1)
print("records:", len(allrecs))
from collections import Counter
print(Counter((r["model"], r["lag"]) for r in allrecs))
