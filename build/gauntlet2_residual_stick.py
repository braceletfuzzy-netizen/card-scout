#!/usr/bin/env python3
# gauntlet_step2.py — THE RESIDUAL-STICK TEST: year-over-year autocorrelation of the city-budget-
# efficiency residuals (FE-6_wide lane, 31 rows) per city. Question: does residual-2022 predict residual-2023?
import json
import numpy as np
from scipy import stats

BUILD = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
src = json.load(open(f"{BUILD}/budget_efficiency_panel_v1.json", encoding="utf-8"))
panel = src["panel"]
MODEL = "FE-6_wide"

res = {}
for r in panel:
    v = r.get("residual", {}).get(MODEL)
    if v is None: continue
    res.setdefault(r["city"], {})[r["year"]] = v

out = {"model_lane": MODEL, "per_city": {}, "pooled": {}}
pairs_all = []
for c in sorted(res):
    yrs = sorted(res[c])
    # longest consecutive run
    runs, run = [], [yrs[0]]
    for y in yrs[1:]:
        if y == run[-1] + 1: run.append(y)
        else: runs.append(run); run = [y]
    runs.append(run)
    best = max(runs, key=len)
    r2 = {k: res[c][k] for k in [x for x in res[c] if x != yrs[0] and f"{x-1}" in map(str, [])] }  # placeholder
    # consecutive pairs anywhere in the city's series
    for y in yrs:
        if y - 1 in res[c]:
            pairs_all.append((y - 1, res[c][y - 1], y, res[c][y]))
    pairs = [(y - 1, res[c][y - 1], y, res[c][y]) for y in yrs if y - 1 in res[c]]
    a = np.array([p[1] for p in pairs]); b = np.array([p[3] for p in pairs])
    entry = {
        "years": yrs, "n_consecutive_runs": {f"{r2n[0]}-{r2n[-1]}": len(r2n) for r2n in runs},
        "longest_consecutive_run": f"{best[0]}-{best[-1]} (n={len(best)})",
        "n_pairs": len(pairs), "pairs": [[p[0], round(p[1],2), p[2], round(p[3],2)] for p in pairs],
        "honest_null": len(pairs) < 3,
    }
    if len(pairs) >= 3 and a.std() > 0 and b.std() > 0:
        entry["lag1_pearson_r"] = round(float(stats.pearsonr(a, b).statistic), 3)
        entry["lag1_spearman_rho"] = round(float(stats.spearmanr(a, b).statistic), 3)
        # 2022 -> 2023 cell specifically
        e22 = next((p for p in pairs if p[0] == 2022), None)
        entry["residual_2022"] = round(e22[1], 2) if e22 else None
        entry["residual_2023"] = round(e22[3], 2) if e22 else None
    out["per_city"][c] = entry

# pooled across cities (each pair is one city-year; pairs share cities -> direction-class read)
if len(pairs_all) >= 5:
    a = np.array([p[1] for p in pairs_all]); b = np.array([p[3] for p in pairs_all])
    out["pooled"] = {"n_pairs": len(pairs_all),
                     "lag1_pearson_r": round(float(stats.pearsonr(a, b).statistic), 3),
                     "lag1_spearman_rho": round(float(stats.spearmanr(a, b).statistic), 3),
                     "note": "pairs are not independent (4-5 cities; a city-year enters twice) — no inference, direction-class read only"}

# the founder's literal: does residual-2022 predict residual-2023?
lit = {}
for c, e in out["per_city"].items():
    if e.get("residual_2022") is not None and e.get("residual_2023") is not None:
        lit[c] = {"residual_2022": e["residual_2022"], "residual_2023": e["residual_2023"],
                  "sign_holds": (e["residual_2022"] > 0) == (e["residual_2023"] > 0)}
out["founder_literal_2022_2023"] = lit

with open(f"{BUILD}/_gauntlet2_residual_stick.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)

for c, e in out["per_city"].items():
    print(c, "|", e["longest_consecutive_run"], "| pairs", e["n_pairs"],
          "| r", e.get("lag1_pearson_r"), "| rho", e.get("lag1_spearman_rho"),
          "| 2022->2023", e.get("residual_2022"), "->", e.get("residual_2023"))
print("pooled:", out["pooled"])
print("founder literal:", lit)
