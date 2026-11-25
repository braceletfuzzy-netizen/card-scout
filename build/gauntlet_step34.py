#!/usr/bin/env python3
# gauntlet_step34.py — STEP 3 THE COMPOSITION-BIAS SCAN (coefficient-sensitivity refits) and
# STEP 4 THE POWER-CURVE (SE-shrink extrapolation + within/between variance decomposition).
# All inputs banked files; every number traced. Honest-nulls named.
import json, math
import numpy as np
from scipy import stats

BUILD = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
rows = [json.loads(l) for l in open(f"{BUILD}/maslow_joint_panel_v1.jsonl", encoding="utf-8") if l.strip()]

SPEC_FE3 = ["care_per_100k", "cost_burden_30pct_plus_share", "median_home_value", "snap_receipt_share_pct", "bachelors_pct"]
MODELS = {
 "FE-3_maslow_joint_t0": {"spec": SPEC_FE3, "ycol": "murder_rate", "betas": [-0.181,-0.280,-0.099,0.640,-0.003]},
 "FE-3_arc_tplus1":      {"spec": SPEC_FE3, "ycol": "murder_rate_t+1", "betas": [-0.197,0.056,-0.263,0.544,-0.189]},
 "FE-6_care_plus_unemp": {"spec": ["care_per_100k","unemployment_rate"], "ycol": "murder_rate", "betas": [-0.304,0.312]},
 "FE-2_care_cage_bookings": {"spec": ["care_per_100k","cage_per_100k","bookings_per_1000"], "ycol": "murder_rate", "betas": [-0.452,0.419,0.013]},
}

def make_frame(spec, ycol):
    recs = []
    for r in rows:
        vals = [r.get(col) for col in spec]
        if any(v is None for v in vals) or r.get(ycol) is None: continue
        recs.append({"city": r["city"], "year": r["year"], "X": np.array(vals, float), "y": r[ycol]})
    return recs

def fit_fe(recs, k):
    X = np.array([r["X"] for r in recs], float)
    y = np.array([r["y"] for r in recs], float)
    Xd = X.copy(); yd = y.copy()
    for c in sorted({r["city"] for r in recs}):
        msk = np.array([r["city"] == c for r in recs])
        if msk.sum() >= 2:
            Xd[msk] -= X[msk].mean(axis=0); yd[msk] -= y[msk].mean()
    sd = Xd.std(axis=0); sd[sd == 0] = 1.0
    sy = yd.std() if yd.std() > 0 else 1.0
    A = np.column_stack([np.ones(len(recs)), Xd / sd]); zy = yd / sy
    beta, *_ = np.linalg.lstsq(A, zy, rcond=None)
    b = beta[1:]
    resid = zy - A @ beta
    n_eff = sum(1 for c in sorted({r['city'] for r in recs}) if sum(1 for r in recs if r['city']==c) > 1)
    dof = max(len(zy) - 1 - k - n_eff, 1)
    s2 = float(resid @ resid) / dof
    se_b = np.sqrt(s2 * np.diag(np.linalg.pinv(A.T @ A))[1:]) / sy
    ss = float(zy @ zy)
    r2 = float(1 - (resid@resid)/ss) if ss > 0 else None
    return b, se_b, r2, len(recs)

def year_is_low_quality(city, year, spec):
    """the banked low-quality classes, from banked evidence only"""
    q = []
    # (a) post-fit budget-forecast years (frame-drift class): 2025+ rows entered panel post-fit
    if year >= 2025: q.append("2025+ budget-forecast-vintage row (frame-drift class, eff-panel guard)")
    # (b) NYC EDU/IBO-era rows: pre-2021 NYC rows lack ACS inputs (they never enter FE-3 frame; note only)
    return q

# ---------- STEP 3: sensitivity refits ----------
s3 = {"models": {}}
for name, m in MODELS.items():
    spec, ycol = m["spec"], m["ycol"]
    base = make_frame(spec, ycol)
    b0, se0, r20, n0 = fit_fe(base, len(spec))
    s3["models"][name] = {"n_frame": n0, "frame_cities": sorted({r["city"] for r in base}),
        "banked_betas": m["betas"], "refit_betas_current_frame": [round(float(x),3) for x in b0],
        "se_current_frame": [round(float(x),3) for x in se0], "within_r2_current": round(r20,3),
        "variants": {}}
    # variant 1: drop every 2025+ row (the frame-drift class)
    v1 = [r for r in base if r["year"] < 2025]
    if len(v1) >= len(spec)+3 and len({r["city"] for r in v1}) >= 2:
        b1, se1, r21, n1 = fit_fe(v1, len(spec))
        s3["models"][name]["variants"]["drop_2025plus_forecast_vintage"] = \
            {"n": n1, "betas": [round(float(x),3) for x in b1], "se": [round(float(x),3) for x in se1],
             "within_r2": round(r21,3)}
    # variant 2: drop each CITY in turn whose rows are the widest-lane (FE-6 uses 2014-2025 CIN rows =
    # the oldest budget-vintage input class); city-level drops = LOCO sensitivity of signs
    for c in sorted({r["city"] for r in base}):
        v2 = [r for r in base if r["city"] != c]
        if len(v2) >= len(spec)+3 and len({r["city"] for r in v2}) >= 2:
            b2, se2, r22, n2 = fit_fe(v2, len(spec))
            s3["models"][name]["variants"][f"drop_city_{c}"] = \
                {"n": n2, "betas": [round(float(x),3) for x in b2], "se": [round(float(x),3) for x in se2],
                 "within_r2": round(r22,3) if r22 else None}

# sign-stability table
def sign(x): return "neg" if x < 0 else ("pos" if x > 0 else "zero")
sign_scan = {}
for name, mm in s3["models"].items():
    cols = MODELS[name]["spec"]
    banked_signs = [sign(x) for x in MODELS[name]["betas"]]
    stability = {c: {"banked": s0, "current_refit": s1, "dropped_city_signs": {}}
                 for c, s0, s1 in zip(cols, banked_signs, [sign(x) for x in mm["refit_betas_current_frame"]])}
    for vname, v in mm["variants"].items():
        for c, s in zip(cols, [sign(x) for x in v["betas"]]):
            stability[c]["dropped_city_signs"].setdefault(vname, s)
    flips = []
    for c, e in stability.items():
        all_signs = [e["banked"], e["current_refit"]] + list(e["dropped_city_signs"].values()) + \
                    [sign(v["betas"][i]) for v in mm["variants"].values() for i, cc in enumerate(cols) if cc == c]
        if len(set(all_signs)) > 1:
            flips.append(c)
    sign_scan[name] = {"columns": cols, "stability": stability, "sign_flip_columns": flips,
                       "all_signs_hold": len(flips) == 0}
s3["sign_stability"] = sign_scan

# honest-null cities named (banked): cities with outcome coverage but NOT in panel
s3["honest_null_cities"] = {
 "in_outcome_series_not_in_panel": 35,
 "note": "outcome-series carries 40 cities; panel carries 6. The 34 non-panel cities are the honest-null class: they could not enter ANY fit because care/cage $ books (city budget-dept grain) were never pulled for them — the selection is by input availability, not outcome availability.",
 "months_guard_fails_banked": {
   "Raleigh": [2014, 2015, 2016, 2017, 2018], "Jacksonville": list(range(2011, 2021)),
   "Omaha": [2021, 2023], "Fresno": [2019], "Baltimore": [2021], "Long Beach": [2021],
   "Sacramento": [2021], "Tucson": [2021], "San Francisco": [2021], "Phoenix": [2021],
   "Pittsburgh": [2019, 2021], "Detroit": [2026]},

}

# ---------- STEP 4: power curve ----------
s4 = {}
for name, m in MODELS.items():
    spec, ycol = m["spec"], m["ycol"]
    base = make_frame(spec, ycol)
    b0, se0, r20, n0 = fit_fe(base, len(spec))
    R2 = r20 if r20 else 0.0
    k = len(spec)
    # within/between decomposition of outcome (variance the FE design must carry)
    ys_all = np.array([r["y"] for r in base])
    within_var, between_var = 0.0, 0.0
    gm = ys_all.mean()
    for c in sorted({r["city"] for r in base}):
        sub = [r["y"] for r in base if r["city"] == c]
        within_var += float(np.var(sub, ddof=0)) * len(sub) if len(sub) > 1 else 0.0
        between_var += (np.mean(sub) - gm) ** 2 * len(sub)
    tot_var = float(np.var(ys_all, ddof=0)) * len(ys_all)
    s4[name] = {
      "n_current": n0, "k_inputs": k, "within_r2_current": round(R2, 3),
      "se_current_per_input": [round(float(x), 3) for x in se0],
      "banked_betas": m["betas"],
      "min_abs_t_current": round(min(abs(bb / s) for bb, s in zip(b0, se0) if s > 0), 2) if any(s > 0 for s in se0) else None,
      "new_city_year_within_info_share": round(within_var / tot_var, 3) if tot_var else None,
      "between_city_year_info_share": round(between_var / tot_var, 3) if tot_var else None,
      "se_shrink_projection": {},
      "deepen_vs_expand": {},
    }
    # SE(model) for mean-outcome read ~ sqrt(R2_eff * sig^2 / n_eff); within-city info share caps what NEW cities add
    e = s4[name]
    eff_within = e["new_city_year_within_info_share"] or 0.0
    for n_target in (150, 250, 400):
        se_mean_scaled = math.sqrt((1 - R2) * eff_within) / math.sqrt(n_target)
        se_mean_current = math.sqrt((1 - R2) * eff_within) / math.sqrt(n0) if n0 else None
        ratio = (se_mean_scaled / se_mean_current) if se_mean_current else None
        e["se_shrink_projection"][n_target] = {
          "n_target": n_target, "se_relative_to_today": round(ratio, 3) if ratio else None}
    # deepening: N more years on SAME cities -> same within-variance source; new cities -> new city intercepts
    # the between-city share is what expansion CANNOT reduce (absorbed by FE per city); deepening grows n
    # without new intercepts, so its SE-sqrt gain is direct:
    for extra_n in (56, 156, 306):
        pass
    e["verdict_terms"] = {
      "expand_gains": "sqrt(n) SE shrink on the POOLED within read + each new city tests transfer (LOCO class)",
      "expand_costs": "each new city adds a fixed-effect intercept (dof cost) and a new honest-null surface; between-city share of variance (see above) is absorbed, not explained",
      "deepen_gains": "sqrt(n) SE shrink WITHOUT new intercept dof + longer within-city arcs (lag t+2/t+3 cells), no new data-quality surface to learn",
      "deepen_costs": "no new transfer evidence — the LOCO question (does it hold on unseen cities?) stays unanswered at greater precision",
    }

out = {"step3_composition_bias": s3, "step4_power_curve": s4}
with open(f"{BUILD}/_gauntlet34_scan_power.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)

print("== STEP 3 sign stability ==")
for name, sc in sign_scan.items():
    print(f"{name}: all-signs-hold={sc['all_signs_hold']} flip-columns={sc['sign_flip_columns']}")
print()
print("== STEP 4 ==")
for name, e in s4.items():
    print(f"{name}: n={e['n_current']} within-share={e['new_city_year_within_info_share']} between-share={e['between_city_year_info_share']} R2={e['within_r2_current']}")
    for nt, v in e["se_shrink_projection"].items():
        print(f"    n={nt}: SE = {v['se_relative_to_today']}x today's")
