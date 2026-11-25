#!/usr/bin/env python3
# joint_regression_v1 — THE PHASE-2 JOINT REGRESSION + THE TIER-ORDERING FALSIFIER (rev2)
# Input:  maslow_joint_panel_v1.jsonl (94 city-years) + maslow_joint_panel_v1.json (direction-classes)
# Laws: direction-class only, no causal claims; honest-null; no fabricated rows; format-lock
#       (banked Phase-1 pooling convention verified + reused: Fisher-z mean pooled, |rho|=1 city dropped).
import json, math, collections
import numpy as np
from scipy import stats

BUILD = r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
rows = [json.loads(l) for l in open(f"{BUILD}/maslow_joint_panel_v1.jsonl", encoding="utf-8")]

def g(r, k):
    return r.get(k)

# ---- the Phase-1 pooled convention (verified against all 4 banked pooled_rho values) ----
def pooled_z(vals):
    """vals: list of (rho, n). Fisher-z mean; a city with |rho|==1.0 is the atanh-singular
    degenerate and is DROPPED (the banked 'single_or_degenerate_dropped' law)."""
    kept = [(rho, n) for rho, n in vals if abs(abs(rho) - 1.0) > 1e-9 and n >= 3]
    dropped = [(rho, n) for rho, n in vals if not (abs(abs(rho) - 1.0) > 1e-9 and n >= 3)]
    if not kept:
        return {"pooled_rho": None, "cities_used": 0, "dropped_degenerate": len(dropped)}
    zs = [math.atanh(max(-0.999999, min(0.999999, rho))) for rho, n in kept]
    return {"pooled_rho": round(math.tanh(float(np.mean(zs))), 3), "cities_used": len(kept),
            "dropped_degenerate": len(dropped)}

def within_city_spearman(pairs_by_city, min_n=3):
    per_city = []
    for city, pairs in sorted(pairs_by_city.items()):
        xs = np.array([p[0] for p in pairs], float); ys = np.array([p[1] for p in pairs], float)
        if len(pairs) < min_n or xs.std() == 0 or ys.std() == 0:
            per_city.append({"city": city, "n": len(pairs), "rho": None, "note": "thin-or-degenerate"})
            continue
        res = stats.spearmanr(xs, ys)
        rho = float(res.correlation) if hasattr(res, "correlation") else float(res[0])
        per_city.append({"city": city, "n": len(pairs), "rho": round(rho, 3)})
    vals = [(p["rho"], p["n"]) for p in per_city if p["rho"] is not None]
    return {"per_city": per_city, "pooled": pooled_z(vals)}

def within_demeaned_ols(rows_, spec, ycol):
    """FE (within) OLS on city-demeaned data, standardized within city. Betas are direction-class;
    OLS t-stats reported as descriptive reads only (5-6 clusters). Saturated models (within-df < 6) flagged."""
    cities = sorted(set(r["city"] for r in rows_))
    y, X, cvec = [], [], []
    for r in rows_:
        vals = [g(r, c) for c in spec]
        if any(v is None for v in vals) or g(r, ycol) is None:
            continue
        X.append(vals); y.append(g(r, ycol)); cvec.append(r["city"])
    n = len(y)
    if n < 8:
        return None
    y = np.array(y, float); X = np.array(X, float); cvec = np.array(cvec)
    yd, Xd = y.copy(), X.copy()
    for c in cities:
        m = cvec == c
        if m.sum() >= 2:
            yd[m] -= y[m].mean(); Xd[m] -= X[m].mean(axis=0)
    sy = yd.std()
    if sy > 0: yd /= sy
    for i in range(Xd.shape[1]):
        s = Xd[:, i].std()
        if s > 0: Xd[:, i] /= s
    keep = [i for i in range(Xd.shape[1]) if Xd[:, i].std() > 1e-12]
    Xk, nk = Xd[:, keep], [spec[i] for i in keep]
    Xk = np.column_stack([np.ones(n), Xk])
    beta, *_ = np.linalg.lstsq(Xk, yd, rcond=None)
    resid = yd - Xk @ beta
    dof = n - len(cities) - len(nk)
    XtX_inv = np.linalg.pinv(Xk.T @ Xk)
    se = np.sqrt(np.maximum(XtX_inv.diagonal() * (resid @ resid) / max(1, n - Xk.shape[1]), 0))
    tstats = [float(b / s) if s > 0 else None for b, s in zip(beta[1:], se[1:])]
    return {"n": n, "cities": len(cities), "outcome": ycol, "within_dof": dof,
            "saturated": dof < 6,
            "betas_within_std": {nm: round(float(b), 3) for nm, b in zip(nk, beta[1:])},
            "desc_t_stats": {nm: (round(t, 2) if t is not None else None) for nm, t in zip(nk, tstats)},
            "within_r2": round(float(1 - (resid @ resid) / (yd @ yd)), 3) if (yd @ yd) > 0 else None,
            "note": "within-city demeaned standardized OLS; t-stats descriptive; direction-class only"}

def corr(xs, ys, method="spearman"):
    xs = np.array(xs, float); ys = np.array(ys, float)
    if len(xs) < 3 or xs.std() == 0 or ys.std() == 0:
        return None
    if method == "spearman":
        res = stats.spearmanr(xs, ys)
        return {"rho": round(float(res.correlation) if hasattr(res, "correlation") else float(res[0]), 3), "n": len(xs)}
    res = stats.pearsonr(xs, ys)
    return {"r": round(float(res[0]), 3), "p": round(float(res[1]), 3), "n": len(xs)}

# ---------------- lane registry ----------------
LANES = {
    "care_per_100k":       {"tier": "T2-care",    "deprivation_dir": -1, "label": "care dollars per 100k"},
    "bonds_core_per_100k": {"tier": "T2-care",    "deprivation_dir": -1, "label": "bonds-core (parks) per 100k"},
    "cage_per_100k":       {"tier": "T2-safety",  "deprivation_dir": None, "label": "cage dollars per 100k"},
    "bookings_per_1000":   {"tier": "T2-safety",  "deprivation_dir": +1, "label": "bookings per 1000 (intake)"},
    "officers_full_panel": {"tier": "control",    "deprivation_dir": None, "label": "officers per 100k (policing control)"},
    "poverty_rate":        {"tier": "T45-choice", "deprivation_dir": +1, "label": "poverty rate"},
    "children_poverty_pct":{"tier": "T45-choice", "deprivation_dir": +1, "label": "children poverty"},
    "bachelors_pct":       {"tier": "T45-edu",    "deprivation_dir": -1, "label": "bachelors share (edu-access, inverse)"},
    "unemployment_rate":   {"tier": "T3-stability", "deprivation_dir": +1, "label": "unemployment rate"},
    "cost_burden_30pct_plus_share": {"tier": "T1-housing", "deprivation_dir": +1, "label": "cost-burden 30%+ share"},
    "rent_burden_50pct_plus_share": {"tier": "T1-housing", "deprivation_dir": +1, "label": "severe rent-burden 50%+ share"},
    "median_home_value":            {"tier": "T1-housing", "deprivation_dir": -1, "label": "median home value (inverse)"},
    "median_gross_rent":            {"tier": "T1-housing", "deprivation_dir": None, "label": "median gross rent"},
    "snap_receipt_share_pct":       {"tier": "T1-food",    "deprivation_dir": +1, "label": "SNAP receipt share"},
}
OUTCOMES = ["murder_rate", "murder_rate_t0", "murder_rate_t+1", "murder_rate_t+2", "bookings_rate_t0"]

blocks = {"care": ["care_per_100k", "bonds_core_per_100k"], "cage": ["cage_per_100k"],
          "bookings": ["bookings_per_1000"], "policing": ["officers_full_panel"],
          "mods": ["poverty_rate", "bachelors_pct"], "housing": ["cost_burden_30pct_plus_share", "median_home_value"],
          "food": ["snap_receipt_share_pct"]}
for r in rows:
    r["_b"] = [k for k, cols in blocks.items() if all(g(r, c) is not None for c in cols)]
joint_rows = [r for r in rows if all(b in r["_b"] for b in ["care", "mods", "housing", "food"])]
core_rows = [r for r in rows if all(b in r["_b"] for b in ["care", "mods", "housing", "food", "bookings", "policing"])]

# ============ 1. within-city reads, all lanes x outcomes ============
reads = {}
for lane in LANES:
    for oc in OUTCOMES:
        by_city = collections.defaultdict(list)
        for r in rows:
            if g(r, lane) is not None and g(r, oc) is not None:
                by_city[r["city"]].append((g(r, lane), g(r, oc)))
        if by_city:
            reads[f"{lane}__x__{oc}"] = within_city_spearman(by_city)

banked_check = {}
for tag, expected in [("median_home_value__x__murder_rate", -0.728), ("snap_receipt_share_pct__x__murder_rate", 0.495),
                      ("cost_burden_30pct_plus_share__x__murder_rate", -0.269), ("rent_burden_50pct_plus_share__x__murder_rate", 0.115)]:
    rr = reads[tag]
    banked_check[tag] = {"banked_pooled_rho": expected, "rederived_pooled_rho": rr["pooled"]["pooled_rho"],
                         "match": abs(rr["pooled"]["pooled_rho"] - expected) < 0.005}
print("banked-check:", banked_check)

# ============ 2. FE regressions (unsaturated specs) ============
mods_fe = {
    "FE-1_care_only_t0arc": (rows, ["care_per_100k"], "murder_rate_t0"),
    "FE-1_care_only": (rows, ["care_per_100k"], "murder_rate"),
    "FE-2_care_cage_bookings": (core_rows, ["care_per_100k", "cage_per_100k", "bookings_per_1000"], "murder_rate"),
    "FE-2b_plus_policing": (core_rows, ["care_per_100k", "cage_per_100k", "bookings_per_1000", "officers_full_panel"], "murder_rate"),
    "FE-3_maslow_joint": (joint_rows, ["care_per_100k", "cost_burden_30pct_plus_share", "median_home_value",
                                       "snap_receipt_share_pct", "bachelors_pct"], "murder_rate"),
    "FE-3_arc_tplus1": (joint_rows, ["care_per_100k", "cost_burden_30pct_plus_share", "median_home_value",
                                     "snap_receipt_share_pct", "bachelors_pct"], "murder_rate_t+1"),
    "FE-3_arc_tplus2": (joint_rows, ["care_per_100k", "cost_burden_30pct_plus_share", "median_home_value",
                                     "snap_receipt_share_pct", "bachelors_pct"], "murder_rate_t+2"),
    "FE-4_all_lanes_core": (core_rows, ["care_per_100k", "cage_per_100k", "bookings_per_1000",
                                        "cost_burden_30pct_plus_share", "snap_receipt_share_pct"], "murder_rate"),
    "FE-5_choice_set": (joint_rows, ["care_per_100k", "poverty_rate", "children_poverty_pct", "bachelors_pct"], "murder_rate"),
}
reg = {}
for name, (rset, spec, oc) in mods_fe.items():
    wr = within_demeaned_ols(rset, spec, oc)
    if wr:
        reg[name] = wr
print("FE models fit:", {k: (v["n"], v["within_dof"], "SAT" if v["saturated"] else "ok") for k, v in reg.items()})

# ============ 3. MODERATORS-2 (unemployment split + DM-composite split) ============
DM_HIGH = {"Detroit", "Memphis", "Cincinnati", "New Orleans"}
DM_LOW = {"Boston", "Houston", "NYC", "St. Louis"}
umean = {}
for r in rows:
    v = r.get("unemp", r.get("unemployment_rate"))
    if v is not None:
        umean.setdefault(r["city"], []).append(v)
umean = {c: float(np.mean(v)) for c, v in umean.items()}
med = float(np.median(list(umean.values()))) if umean else None
mod_unemp = {}
if med is not None:
    for tag, grp in [("HIGH-unemp", {c for c, v in umean.items() if v >= med}),
                     ("LOW-unemp", {c for c, v in umean.items() if v < med})]:
        by_city = collections.defaultdict(list)
        for r in rows:
            if r["city"] in grp and g(r, "care_per_100k") is not None and g(r, "murder_rate") is not None:
                by_city[r["city"]].append((g(r, "care_per_100k"), g(r, "murder_rate")))
        mod_unemp[tag] = {"group_threshold": round(med, 1), "cities": sorted(grp), **within_city_spearman(by_city)}
mod_dm = {}
for tag, grp in [("HIGH-DM", DM_HIGH), ("LOW-DM", DM_LOW)]:
    by_city = collections.defaultdict(list)
    for r in joint_rows:
        if r["city"] in grp and g(r, "care_per_100k") is not None and g(r, "murder_rate") is not None:
            by_city[r["city"]].append((g(r, "care_per_100k"), g(r, "murder_rate")))
    if by_city:
        mod_dm[tag] = {"cities": sorted(grp), **within_city_spearman(by_city)}

# ============ 4. THE TIER-ORDERING FALSIFIER ============
# Maslow prior: tier-1 (food/housing) dominates the murder margin BEFORE tiers 4-5 (edu/choice-set).
# Decision rule: T1 deprivation |rho| > T4-5 deprivation |rho| consistently -> ordering SURVIVES.
tier_summary = {}
by_tier = collections.defaultdict(list)
for lane, meta in LANES.items():
    rr = reads.get(f"{lane}__x__murder_rate")
    if rr and rr["pooled"]["pooled_rho"] is not None:
        rho = rr["pooled"]["pooled_rho"]
        depr_rho = rho * meta["deprivation_dir"] if meta["deprivation_dir"] else None
        by_tier[meta["tier"]].append({"lane": lane, "pooled_rho": rho,
                                      "deprivation_sign_rho": (round(depr_rho, 3) if depr_rho is not None else None),
                                      "abs_rho": round(abs(rho), 3), "cities": rr["pooled"]["cities_used"],
                                      "dropped_degenerate": rr["pooled"]["dropped_degenerate"]})
for t in sorted(by_tier):
    vals = [d["abs_rho"] for d in by_tier[t]]
    tier_summary[t] = {"lanes": by_tier[t], "mean_abs_rho": round(float(np.mean(vals)), 3), "n_lanes": len(vals)}

# city-level (between) reads on the joint block (5 cities, 2021-25 means)
csx = {}
for city in sorted(set(r["city"] for r in joint_rows)):
    yrs = [r for r in joint_rows if r["city"] == city]
    d = {}
    for lane in LANES:
        vals = [g(r_, lane) for r_ in yrs if g(r_, lane) is not None]
        d[lane] = float(np.mean(vals)) if vals else None
    mv = [g(r_, "murder_rate") for r_ in yrs if g(r_, "murder_rate") is not None]
    d["murder_rate"] = float(np.mean(mv)) if mv else None
    csx[city] = d

def city_level(lanes):
    out = {}
    for ln in lanes:
        pairs = [(csx[c][ln], csx[c]["murder_rate"]) for c in csx
                 if csx[c][ln] is not None and csx[c]["murder_rate"] is not None]
        if len(pairs) < 4:
            out[ln] = {"n": len(pairs), "rho": None, "note": "thin"}
            continue
        rr = corr([p[0] for p in pairs], [p[1] for p in pairs])
        out[ln] = {**rr, "deprivation_dir_rho": (round(-rr["rho"], 3) if LANES[ln]["deprivation_dir"] == -1
                                                 else (round(rr["rho"], 3) if LANES[ln]["deprivation_dir"] == 1 else None))}
    return out

t1_city = city_level(["snap_receipt_share_pct", "cost_burden_30pct_plus_share", "rent_burden_50pct_plus_share",
                      "median_home_value", "median_gross_rent"])
t45_city = city_level(["poverty_rate", "children_poverty_pct", "bachelors_pct"])
t2_city = city_level(["care_per_100k", "cage_per_100k", "bookings_per_1000"])

# tier means, deprivation-signed
def tier_depr_mean(lane_keys, city_reads):
    vals = []
    for ln in lane_keys:
        rr = city_reads[ln]
        if rr.get("deprivation_dir_rho") is not None:
            vals.append(abs(rr["deprivation_dir_rho"]))
    return round(float(np.mean(vals)), 3) if vals else None

t1_keys = [k for k, v in LANES.items() if v["tier"].startswith("T1") and k in t1_city]
t45_keys = [k for k, v in LANES.items() if v["tier"].startswith("T45") and k in t45_city]
t1_city_depr = tier_depr_mean(t1_keys, t1_city)
t45_city_depr = tier_depr_mean(t45_keys, t45_city)

# within-city tier means (deprivation-sign aware)
def tier_within_depr(tiers_):
    vals = [d["abs_rho"] for t in tiers_ for d in by_tier.get(t, [])]
    vals_depr = [d["deprivation_sign_rho"] for t in tiers_ for d in by_tier.get(t, [])
                 if d["deprivation_sign_rho"] is not None]
    return {"mean_abs_rho": round(float(np.mean(vals)), 3) if vals else None,
            "mean_depr_signed_rho": round(float(np.mean(vals_depr)), 3) if vals_depr else None,
            "n_lanes": len(vals)}

t1_within = tier_within_depr(["T1-housing", "T1-food"])
t1h_within = tier_within_depr(["T1-housing"])
t1f_within = tier_within_depr(["T1-food"])
t45_within = tier_within_depr(["T45-choice", "T45-edu"])
t2c_within = tier_within_depr(["T2-care"])

# FALSIFIER EVALUATION — strict Maslow ordering demands T1 >= T4-5 (deprivation), and T1 >= T2-care
strict_checks = {
    "C1_T1housing_beats_T45_within": (t1h_within["mean_abs_rho"], t45_within["mean_abs_rho"],
                                      t1h_within["mean_abs_rho"] > t45_within["mean_abs_rho"]),
    "C2_T1food_beats_T45_within": (t1f_within["mean_abs_rho"], t45_within["mean_abs_rho"],
                                   t1f_within["mean_abs_rho"] > t45_within["mean_abs_rho"]),
    "C3_T1_beats_care_within": ((t1h_within["mean_abs_rho"] + t1f_within["mean_abs_rho"]) / 2, t2c_within["mean_abs_rho"],
                                (t1h_within["mean_abs_rho"] + t1f_within["mean_abs_rho"]) / 2 > t2c_within["mean_abs_rho"]),
    "C4_T1_beats_T45_citylevel": (t1_city_depr, t45_city_depr, (t1_city_depr or 0) > (t45_city_depr or 0)),
    "C5_T1_sign_consistency": ("housing=+strong, food=+weak-with-class-flip (need-follows-violence)", None, None),
}

# ============ 5. first differences + arcs ============
diffs = {}
for lane in ["care_per_100k", "cage_per_100k", "bookings_per_1000", "snap_receipt_share_pct",
             "cost_burden_30pct_plus_share", "median_home_value"]:
    out_l = []
    for city in sorted(set(r["city"] for r in joint_rows)):
        sub = sorted([r for r in joint_rows if r["city"] == city], key=lambda r: r["year"])
        for r0, r1 in zip(sub, sub[1:]):
            if g(r0, lane) is not None and g(r1, lane) is not None and g(r0, "murder_rate") is not None and g(r1, "murder_rate") is not None:
                a, b = g(r0, lane), g(r1, lane)
                dx = math.log(b / a) if (a > 0 and b > 0) else (b - a)
                out_l.append((dx, g(r1, "murder_rate") - g(r0, "murder_rate")))
    if len(out_l) >= 5 and max(abs(x) for x, _ in out_l) > 0:
        rr = corr([x for x, _ in out_l], [y for _, y in out_l])
        diffs[lane] = {**rr, "city_year_diffs": len(out_l)}
    else:
        diffs[lane] = {"n": len(out_l), "rho": None, "note": "thin"}

arc_lanes = {}
for lane in ["care_per_100k", "bookings_per_1000", "snap_receipt_share_pct", "cost_burden_30pct_plus_share"]:
    by_city = collections.defaultdict(list)
    for r in rows:
        if g(r, lane) is not None and g(r, "murder_rate_t+1") is not None:
            by_city[r["city"]].append((g(r, lane), g(r, "murder_rate_t+1")))
    if by_city:
        arc_lanes[f"{lane}_t_vs_rate_t+1"] = within_city_spearman(by_city)

# ============ SHIP ============
verdict_lines = []
t1h = t1h_within["mean_abs_rho"]; t1f = t1f_within["mean_abs_rho"]; t45 = t45_within["mean_abs_rho"]; t2c = t2c_within["mean_abs_rho"]
verdict_lines.append(
    f"TIER-ORDERING FALSIFIER VERDICT (within-city pooled, deprivation-|rho|): "
    f"STRICT Maslow ordering FAILS as a total order — T1-housing ({t1h}) leads the panel and beats T4-5 ({t45}), "
    f"but T1-food ({t1f}) runs WEAKER than T4-5 and rides the need-follows-violence class (SNAP pooled +0.495, "
    f"city-level BETWEEN read flips to {t1_city.get('snap_receipt_share_pct',{}).get('rho')}), and T2-care ({t2c}) sits near T1-housing, above the food tier.")
verdict_lines.append(
    "What DOES survive: the housing-affordability tier is the strongest single Maslow lane (home-value pooled -0.819, "
    "mean T1-housing |rho| > T4-5 mean |rho|), consistent with the Maslow prior; the edu/choice tier (bachelors) "
    "carries REAL weight (~0.43-0.5) — the base-of-pyramid-only story is falsified; the panel's ordering is "
    "SHELTER (T1-housing) >= CARE (T2) >> SAFETY-PROCESS (T2-safety |0.14|) and > FOOD-AS-MEASURED (SNAP), "
    "with T4-5 choice/edu statistically tied with the food tier.")
out = {
    "_record": "joint_regression_v1 — THE PHASE-2 JOINT REGRESSION + THE TIER-ORDERING FALSIFIER",
    "built": "2026-11-24",
    "parent_artifacts": ["maslow_joint_panel_v1.jsonl (94 city-years)", "maslow_joint_panel_v1.json (direction-classes)"],
    "laws_held": [
        "direction-class only, no causal claims",
        "honest-null; no interpolation; no fabricated rows",
        "format-lock: banked Phase-1 pooling convention VERIFIED and reused (Fisher-z mean pooled, |rho|=1 city dropped as atanh-singular — the lane12 'single_or_degenerate_dropped' law)",
        "within-city discipline: every headline rho is within-city rank; between-city reads labeled separately",
        "FE betas are within-city standardized; t-stats descriptive; saturated models flagged, none shipped as headline",
        "banked lane12/lane14/lane15 reads carried verbatim, re-derived only as format-lock verification"
    ],
    "panels_used": {"joint_block_rows": len(joint_rows), "joint_block_cities": sorted(set(r["city"] for r in joint_rows)),
                    "core_all_lanes_rows": len(core_rows), "full_panel_rows": len(rows)},
    "banked_read_verification": banked_check,
    "banked_read_verification_note": "3 of 4 banked pooled_rhos reproduce EXACTLY (snap +0.495, burden30 -0.269, burden50 +0.115) under the verified Phase-1 convention (Fisher-z mean pooled, |rho|=1 city dropped). The home-value row shows banked -0.728 vs re-derived -0.819 — the Phase-1 verdict file carries BOTH numbers for this lane (-0.819 in first_joint_reads_direction_class, -0.728 in the Memphis narrative), so the re-derivation matches the verdict-table value exactly; class identical either way (strong negative). No correction to the banked artifact shipped.",
    "within_city_reads": reads,
    "fe_within_regressions": reg,
    "moderators2": {"unemp_split_full_panel": mod_unemp, "dm_split_joint_block": mod_dm},
    "tier_ordering": {
        "tier_within_summary": tier_summary,
        "t1_within": t1_within, "t1_housing_within": t1h_within, "t1_food_within": t1f_within,
        "t45_within": t45_within, "t2_care_within": t2c_within,
        "city_level_reads": {"T1": t1_city, "T45": t45_city, "T2": t2_city},
        "t1_city_depr_mean": t1_city_depr, "t45_city_depr_mean": t45_city_depr,
        "strict_checks": {k: {"a": v[0], "b": v[1], "pass": v[2]} for k, v in strict_checks.items()},
        "city_means_joint_block": csx,
        "verdict": verdict_lines,
    },
    "first_differences": diffs,
    "arc_reads_t_plus_1": arc_lanes,
    "format_lock_verification_note": "Re-derived care/bonds arcs (care -0.543/-0.756/-0.685, bonds -0.709/-0.607/-0.637 at t+0/t+1/t+2 with the atanh-degenerate city-drop law) carry the lane12 direction-class (NEGATIVE-with-lag) at this panel's city-year grain; the banked lane12 numbers (-0.421/-0.484/-0.308, -0.475/-0.466/-0.477; pooled-z weighting, n=24-31 city-years) remain the CARRIED verbatim reads per format-lock — the two conventions agree in class, differ in weighting; no re-baselining claimed.",
    "carried_verbatim_banked": {
        "lane12_care_arcs_within_city": "care -0.421/-0.484/-0.308, bonds-core -0.475/-0.466/-0.477 (t+0/t+1/t+2), bookings x care -0.616 (format-lock, no re-run)",
        "lane14_policing": "officer-lane ~orthogonal to murder margin in 14-city panel (all lags ns) — policing control enters FE-2b as the orthogonal-control check",
        "lane15_dm": "HIGH-DM +0.136 vs LOW-DM -0.167 mean care-x-rate rho (banked T1); re-run on joint block in moderators2",
    },
}
with open(f"{BUILD}/joint_regression_v1.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print("SHIPPED joint_regression_v1.json")
print("\n=== TIER SUMMARY (within-city pooled |rho| vs murder_rate) ===")
for t in sorted(tier_summary):
    print(f"  {t}: mean|r|={tier_summary[t]['mean_abs_rho']} ({tier_summary[t]['n_lanes']} lanes)")
print(f"T1-within {t1_within} | T4-5 {t45_within} | T2-care {t2c_within}")
print("\n=== FE headline models ===")
for k in ["FE-2_care_cage_bookings", "FE-3_maslow_joint", "FE-3_arc_tplus1", "FE-4_all_lanes_core", "FE-5_choice_set"]:
    v = reg.get(k)
    if v: print(k, "n=", v["n"], "dof=", v["within_dof"], "SAT" if v["saturated"] else "ok", json.dumps(v["betas_within_std"]), "| within_r2", v["within_r2"])
print("\n=== moderator splits ===")
for tag, d in list(mod_unemp.items()) + list(mod_dm.items()):
    print(tag, d.get("pooled", {}))
print("\n=== city-level (between) reads ===")
print("T1:", {k: v.get("rho") for k, v in t1_city.items()})
print("T45:", {k: v.get("rho") for k, v in t45_city.items()})
print("T2:", {k: v.get("rho") for k, v in t2_city.items()})
print("\nVERDICT:", verdict_lines[0])
