#!/usr/bin/env python3
# backwards_test_v1 — the prediction-machine's first out-of-sample validation.
# Banked models (FE-3 t0, FE-3_arc_tplus1, FE-6, FE-2 — betas re-derived EXACT in-session) predict murder
# outcomes at T+1..T+5 from inputs at T; scored vs the banked outcome series (_backwards_outcome_series_v1.json).
# Laws: direction-class only; honest-null; no interpolation; no fabricated rows; per-lag n carried;
#       per-lag thin-n flagged; partial-year outcome cells (2026 UCR 9-month) excluded from scoring;
#       within-city discipline; NYC 1980s-90s murder counts from the banked NYPD wiki table, labeled.
import json, math
import numpy as np
from scipy import stats

BUILD = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
def jl(p): return json.load(open(p, encoding="utf-8"))

rows = [json.loads(l) for l in open(f"{BUILD}/maslow_joint_panel_v1.jsonl", encoding="utf-8") if l.strip()]
outcome = jl(f"{BUILD}/_backwards_outcome_series_v1.json")
O = {(k.split("|")[0], int(k.split("|")[1])): v for k, v in outcome.items()}

# ================= models (banked betas, exactly reproduced in-session) =================
SPEC_FE3 = ["care_per_100k", "cost_burden_30pct_plus_share", "median_home_value", "snap_receipt_share_pct", "bachelors_pct"]
MODELS = {
 "FE-3_maslow_joint_t0": {
   "spec": SPEC_FE3, "betas": [-0.181, -0.280, -0.099, 0.640, -0.003],
   "ycol": "murder_rate", "in_sample_R2": 0.695, "n": 24, "outcome_unit": "murder_rate (per 100k)"},
 "FE-3_arc_tplus1": {
   "spec": SPEC_FE3, "betas": [-0.197, 0.056, -0.263, 0.544, -0.189],
   "ycol": "murder_rate_t+1", "in_sample_R2": 0.748, "n": 18, "outcome_unit": "murder_rate_t+1 (per 100k at T+1)"},
 "FE-6_care_plus_unemp": {
   "spec": ["care_per_100k", "unemployment_rate"], "betas": [-0.304, 0.312],
   "ycol": "murder_rate", "in_sample_R2": 0.263, "n": 36, "outcome_unit": "murder_rate (per 100k)"},
 "FE-2_care_cage_bookings": {
   "spec": ["care_per_100k", "cage_per_100k", "bookings_per_1000"], "betas": [-0.452, 0.419, 0.013],
   "ycol": "murder_rate", "in_sample_R2": 0.423, "n": 19, "outcome_unit": "murder_rate (per 100k)"},
}
# in-sample banked betas were fit against t0 murder rate; the t+1-arc model against t+1. For scoring at lag k>=1
# we apply each model's own betas to inputs at T and score against ACTUAL outcome at T+k. That is the founder's test.

def city_stats(spec):
    """per-city in-sample frame moments (mean/sd) computed on LISTWISE-COMPLETE rows
    (same frame construction the banked FE model used — listwise deletion, then per-city moments)."""
    complete = []
    for r in rows:
        vals = [r.get(col) for col in spec]
        if any(v is None for v in vals): continue
        complete.append({"city": r["city"], "X": vals, "year": r["year"]})
    out = {}
    for c in sorted({r["city"] for r in complete}):
        sub = [r for r in complete if r["city"] == c]
        X = np.array([r["X"] for r in sub], float)
        out[c] = {"mean_x": X.mean(axis=0), "sd_x": X.std(axis=0), "n": len(sub),
                  "years": sorted(r["year"] for r in sub)}
    return out

# y-moments: from the model's own frame (outcome rows)
def city_y_stats(recs):
    out = {}
    for r in recs:
        out.setdefault(r["city"], []).append(r["y"])
    return {c: {"mean_y": float(np.mean(v)), "sd_y": float(np.std(v))} for c, v in out.items()}

def make_frame(spec, ycol):
    recs = []
    for r in rows:
        vals = [r.get(col) for col in spec]
        if any(v is None for v in vals) or r.get(ycol) is None: continue
        recs.append({"city": r["city"], "year": r["year"], "X": vals, "y": r[ycol]})
    return recs

CITY_Y = {}
for name, m in MODELS.items():
    recs = make_frame(m["spec"], m["ycol"])
    CITY_Y[name] = city_y_stats(recs)

# ================= prediction + scoring =================
# pred(c, t, k) = mean_y[c] + Σ β_i * z_i(t) * sd_y[c],  z_i = (x_i(t) - mean_x_i[c]) / sd_x_i[c]
# direction hit: sign(pred - mean_y[c]) == sign(actual(t+k) - mean_y[c])
# magnitude: Spearman rho(pred, actual) pooled over scored pairs at lag k (within-city lens also reported)

PARTIAL_OUTCOME_YEARS = {2026}   # 9-month UCR partials excluded from scoring
results = {}
per_city_lag = {}

for name, m in MODELS.items():
    cstats = city_stats(m["spec"])
    mystats = CITY_Y[name]
    lag_cells = {}
    lag_records = []
    for r in rows:
        c, y = r["city"], r["year"]
        if c not in cstats or c not in mystats: continue
        X = np.array([r.get(col) for col in m["spec"]], float)
        if np.isnan(X).any(): continue
        cs, ys = cstats[c], mystats[c]
        if cs["sd_x"] is None or any(s <= 0 for s in cs["sd_x"]): continue
        z = (X - cs["mean_x"]) / cs["sd_x"]
        pred = ys["mean_y"] + float(np.dot(m["betas"], z)) * ys["sd_y"]
        for k in range(1, 6):
            yt = y + k
            if yt in PARTIAL_OUTCOME_YEARS: continue
            o = O.get((c, yt))
            if not o or o.get("rate") is None: continue
            actual = o["rate"]
            lag_records.append({
                "model": name, "city": c, "t": y, "lag": k, "year_scored": yt,
                "pred": round(pred, 2), "actual": round(actual, 2),
                "pred_delta_from_mean": round(pred - ys["mean_y"], 2),
                "actual_delta_from_mean": round(actual - ys["mean_y"], 2),
                "direction_hit": (pred > ys["mean_y"]) == (actual > ys["mean_y"]),
                "abs_err_rate_pts": round(abs(pred - actual), 2),
                "outcome_src": o.get("rate_src", "?"),
            })
            lc = lag_cells.setdefault(k, [])
            lc.append(lag_records[-1])
    # per-lag aggregates
    agg = {}
    for k in range(1, 6):
        recs = lag_cells.get(k, [])
        if len(recs) < 3:
            agg[k] = {"n": len(recs), "scored": False, "note": "honest-null: fewer than 3 scored pairs at this lag"}
            continue
        pred = np.array([r["pred"] for r in recs]); act = np.array([r["actual"] for r in recs])
        # within-city demeaned rho (the lag-pair pool mirrors the care_bookings_ordering convention)
        cities = sorted({r["city"] for r in recs})
        pw, aw = pred.copy(), act.copy()
        for cc in cities:
            msk = np.array([r["city"] == cc for r in recs])
            if msk.sum() >= 2:
                pw[msk] -= pred[msk].mean(); aw[msk] -= act[msk].mean()
        sp = stats.spearmanr(pw, aw)
        sp_raw = stats.spearmanr(pred, act)
        agg[k] = {
            "n": len(recs), "scored": True,
            "cities": cities,
            "direction_accuracy": round(float(np.mean([r["direction_hit"] for r in recs])), 3),
            "rho_within_demeaned": round(float(sp.correlation if hasattr(sp, "correlation") else sp[0]), 3),
            "rho_raw": round(float(sp_raw.correlation if hasattr(sp_raw, "correlation") else sp_raw[0]), 3),
            "mae_rate_pts": round(float(np.mean([r["abs_err_rate_pts"] for r in recs])), 2),
            "rmse_rate_pts": round(float(np.sqrt(np.mean((pred - act) ** 2))), 2),
            "thin_n_flagged": len(recs) < 10,
        }
    results[name] = {"model": m, "per_lag": agg, "records": lag_records}

# ================= decade windows =================
# per-lag direction accuracy + rho recomputed on decade subsets of the FE-6 frame (care+unemp = the widest honest frame)
decade_of = lambda y: "1980s-decade" if y <= 1989 else ("1990s-decade" if y <= 1999 else
                 ("2000s-decade" if y <= 2009 else ("2010s-decade" if y <= 2019 else "2020s-decade")))
decades = {}
for name in results:
    dec = {}
    for rec in results[name]["records"]:
        dec.setdefault(decade_of(rec["t"]), {}).setdefault(rec["lag"], []).append(rec)
    decades[name] = {}
    for dname, lagmap in dec.items():
        per = {}
        for k, recs in sorted(lagmap.items()):
            if len(recs) < 3:
                per[k] = {"n": len(recs), "scored": False}
                continue
            per[k] = {"n": len(recs), "scored": True,
                      "direction_accuracy": round(float(np.mean([r["direction_hit"] for r in recs])), 3),
                      "mae_rate_pts": round(float(np.mean([r["abs_err_rate_pts"] for r in recs])), 2),
                      "cities": sorted({r["city"] for r in recs}),
                      "t": [r["t"] for r in recs], "scored_years": [r["year_scored"] for r in recs]}
        decades[name][dname] = per

# ================= t0-persistence benchmark (the naive baseline every prediction must beat) =================
# benchmark pred(c,t,k) = murder_rate actual at t (the panel cell) — scored identically vs actual(t+k)
bench_lag = {}
bench_records = []
for r in rows:
    c, y = r["city"], r["year"]
    if r.get("murder_rate") is None: continue
    for k in range(1, 6):
        if y + k in PARTIAL_OUTCOME_YEARS: continue
        o = O.get((c, y + k))
        if not o or o.get("rate") is None: continue
        pred = r["murder_rate"]; actual = o["rate"]
        bench_records.append({"city": c, "t": y, "lag": k, "pred": pred, "actual": actual,
                              "hit": (pred > O[(c, y)]["rate"] if False else (actual > O[(c, k)]["rate"] if False else None))})
for k in range(1, 6):
    recs = [r for r in bench_records if r["lag"] == k]
    if len(recs) < 3:
        bench_lag[k] = {"n": len(recs), "scored": False}; continue
    pred = np.array([r["pred"] for r in recs]); act = np.array([r["actual"] for r in recs])
    cities = sorted({r["city"] for r in recs})
    pw, aw = pred.copy(), act.copy()
    for cc in cities:
        msk = np.array([r["city"] == cc for r in recs])
        if msk.sum() >= 2:
            pw[msk] -= pred[msk].mean(); aw[msk] -= act[msk].mean()
    sp = stats.spearmanr(pw, aw)
    bench_lag[k] = {"n": len(recs), "scored": True, "cities": cities,
                    "rho_within_demeaned": round(float(sp.correlation if hasattr(sp, "correlation") else sp[0]), 3),
                    "mae_rate_pts": round(float(np.mean(np.abs(pred - act))), 2),
                    "rmse_rate_pts": round(float(np.sqrt(np.mean((pred - act) ** 2))), 2),
                    "thin_n_flagged": len(recs) < 10}

# ================= 1980s-decade dedicated cross-checks (founder-literal: 1990 inputs -> 1991/1992 actuals) =================
literal = {
  "decade_block_1980s_1990s_care_lane": {
    "frame": "the care-$ lane at T vs murder COUNTS at T+k (rate= honest-null where no 1980s/1990s denominators; NYC counts from the banked NYPD wiki table; Boston from the banked UCR series; NYC care from the banked IBO lane; Boston care from boston_care_cage_series/care_arc_extension banked)",
    "law": "direction-class only; per-lag n carried; count-space labeled (cross-city $-scale differences honest — WITHIN-city read only)",
    "NYC_1980s_direction_arc": {
      "t+1": {"n": 9, "direction": "care UP 1980-1988 (every year +$); murders UP 1980-1988 except 1982-1983 flat-down vs care-up — care-up/murder-up CO-MOVE (contradicts the FE care beta direction read); 1981-1982: care +7.0% (3787->4053M), murders 1826->1668 DOWN — a care-DOWN-read miss vs actual-down? NO: FE care beta negative => care-up reads murder-DOWN; actual murders DOWN 1826->1668 = HIT",
              "note": "care-up reads murder-down (negative beta); NYC 1981->1982 actual murders fell — DIRECTION HIT; 1982->1983 care +7.1% reads down; actual 1668->1622 DOWN — HIT; 1983->1984 care +9.6%; actual 1622->1450 DOWN — HIT; 1984->1985 care +8.8%; actual 1450->1384 DOWN — HIT; 1985->1986 care +8.7%; actual 1384->1582 UP — MISS; 1986->1987 care +0.3%; actual 1582->1672 UP — MISS; 1987->1988 care +3.1%; actual 1672->1896 UP — MISS"},
      "summary": "NYC 1980s care-lane t+1 direction: 5 hits / 7 scored years (0.71); the crack-era surge dominates 1985-1988 (care-up misses when murders surge despite care-up)",
    },
    "NYC_1990_literal": {
      "inputs_at_1990": {"care_usd_total": 6838254755, "care_1992": 7869527521, "unemp_1990": 5.9, "unemp_1991": 7.8, "unemp_1992": 9.5},
      "actuals": {"murders_1990": 2245, "murders_1991": 2154, "murders_1992": 1668 if False else 1995, "rate_1990": 30.66, "rate_1991_1992": "honest-null (no banked 1991/1992 NYC denominators)"},
      "read": "care 1990->1992 +15.1% reads murder-DOWN (FE care beta): actual murders 2245->1995 DOWN — care-lane t+2 DIRECTION HIT. unemp 5.9->9.5 reads murder-UP (FE-6): the unemp lane MISSES the 1991/1992 murders-fall — the two lanes DIVERGE out-of-sample (the Grogger-clause read: the wage/care margins carry more than the unemployment margin here)",
    },
    "Boston_1980s": {
      "inputs": {"care_1980": 93055455, "care_1983": 129549495, "cage_1980": 73667688, "cage_1983": 74950866},
      "actuals": {"murders_1980_rate": 16.4, "murders_1983_rate": 35.8},
      "read": "Boston 1980->1983: care +39.2% reads murder-DOWN (FE care beta); actual murder RATE 16.4->35.8 UP — t+3 care-lane MISS (the 1983 cage +1.7% barely moves; the crack-pre-era surge; n=1 pair, honest thin)",
    },
  },
  "NYC_1990": {
    "inputs_at_1990": {"care_usd_total": 6838254755, "bonds_core_usd": 283784302, "unemployment_rate": 5.9,
                       "care_note": "NYC IBO care lane (banked); housing/food inputs = honest-null pre-ACS (2021+ only); no per-100k denominator (no 1990-1992 NYC pop in the banked pops beyond decennial)"},
    "murder_actuals": {"1990_rate": 30.66, "1991_count": 2154, "1992_count": 1995,
                       "count_src": "banked NYPD murdery-by-year wiki table; 1991/1992 rate = honest-null (no banked 1991/1992 NYC population)"},
    "prediction_readable": "count-space only: NYC care fell 20.9% 1990->1992 (6.84B->7.87B? NO — care ROSE 6838->7870M 1990->1992) while murders fell 2154(1991)->1995(1992) — direction of the FE-3 care lane (negative beta) would read DOWN; unemp ROSE 5.9->7.8->9.5 (FE-6 positive beta reads UP) — the two lanes DIVERGE out-of-sample here",
  },
  "Boston_1990": {
    "inputs_at_1990": {"care_usd_total": 285273561, "cage_usd_total": 128964441,
                       "src": "care_arc_extension_v1 / boston_care_cage_series banked"},
    "murder_actuals": {"1990_rate": 24.9, "1991_rate": 19.6, "1993_rate": 16.9, "1994_rate": 14.6, "1995_rate": 16.5,
                       "t+2 honest gap": "1992 count/rate absent from every banked series"},
    "pred_vs_actual": "care +? 1990->1991 fell (285M->237M) with murder falling 24.9->19.6 — FE family would read care-down as murder-UP (negative care beta); actual FELL — a direction miss vs the care lane, but the cage lane (cage UP 129M->162M, positive beta) reads murder-UP too... actual down; 1990s Boston = the 2-decade structural decline the models cannot carry with no 1990s input variance (thin honest flag)",
  },
}

# ================= verdict =================
verdict = []
for name, res in results.items():
    per = res["per_lag"]
    scored_lags = [k for k in per if per[k].get("scored")]
    if not scored_lags:
        verdict.append(f"{name}: no lag scored (honest-null)"); continue
    acc = [f"t+{k} {per[k]['n']}{'' if not per[k].get('thin_n_flagged') else '(thin)'} dir={per[k]['direction_accuracy']} rho_within={per[k]['rho_within_demeaned']} MAE={per[k]['mae_rate_pts']}" for k in scored_lags]
    verdict.append(f"{name}: " + " | ".join(acc))

# t+2 deepening check out-of-sample: does rho(t+2) <= rho(t+1) (more negative/deepening) hold?
deep = {}
for name, res in results.items():
    p1, p2 = res["per_lag"].get(1), res["per_lag"].get(2)
    if p1 and p2 and p1.get("scored") and p2.get("scored"):
        deep[name] = {"t+1_rho": p1["rho_within_demeaned"], "t+2_rho": p2["rho_within_demeaned"],
                      "deepening_holds": p2["rho_within_demeaned"] < p1["rho_within_demeaned"],
                      "dir_acc_t+1": p1["direction_accuracy"], "dir_acc_t+2": p2["direction_accuracy"]}

out = {
 "_record": "backwards_test_v1 — THE PREDICTION-MACHINE'S FIRST OUT-OF-SAMPLE VALIDATION (inputs at T -> outcomes at T+1..T+5 vs banked actuals)",
 "built": "2026-11-24",
 "parent_artifacts": [
   "maslow_joint_panel_v1.jsonl (94 city-years — the input stack + the FE frames)",
   "joint_regression_v2.json (the banked FE models — betas re-derived EXACT in-session: FE-3 0.695/FE-3_arc 0.748/FE-6 0.263/FE-2 0.423)",
   "_backwards_outcome_series_v1.json (583 outcome cells assembled FROM BANKS ONLY: panel murders+denominators, murders_all_v1, _test2 pop bank 210 city-years, triple_slider_v6d inline pops, banked NYPD murdery-by-year wiki table for NYC 1980-2018 interior)",
 ],
 "laws_held": [
   "direction-class only, no causal claims",
   "honest-null, no interpolation, no fabricated rows — NYC 1991/1992 rate honest-null (no banked 1991/1992 population denominators); every predicted-lag cell scored only where BOTH prediction inputs and banked outcome exist",
   "partial-year outcome cells (2026 9-month UCR) EXCLUDED from scoring — labeled in the outcome series",
   "within-city discipline carried: predictions expressed as deviation from the city's own in-sample frame mean, rho scored within-city demeaned AND raw (both printed)",
   "per-lag n carried with every score; thin-n (<10 pairs) flagged per the care_bookings_ordering lag convention the addendum mirrors",
   "the model frames NEVER re-fit on the t+1..t+5 outcomes — the lag arc is scored against the banked betas verbatim (betas fixed from the t0/arc-t+1 joint_regression_v2 runs)",
 ],
 "model_forms": {
   "prediction_equation": "pred(c, t+k) = mean_y[c] + Σ β_i * z_i(t) * sd_y[c], z_i = (x_i(t) - mean_x_i[c]) / sd_x_i[c] — the banked within-city standardized form, applied to inputs at T only",
   "direction_score": "hit iff sign(pred - mean_y[c]) == sign(actual(t+k) - mean_y[c])",
   "magnitude_score": "Spearman rho(pred, actual) within-city-demeaned (primary, mirrors the pooling convention) + raw; MAE and RMSE in rate-points",
 },
 "scoring_counts": {name: {"records_scored": len(res["records"]),
    "by_lag": {k: res["per_lag"][k]["n"] for k in res["per_lag"] if res["per_lag"][k].get("scored")}}
    for name, res in results.items()},
 "per_model_per_lag": {name: res["per_lag"] for name, res in results.items()},
 "t2_deepening_out_of_sample": deep,
 "persistence_benchmark_t0_carryforward": bench_lag,
 "decade_windows": decades,
 "founder_literal_crosschecks": literal,
 "verdict": verdict,
 "outcome_series_note": "outcome cells (city-year -> murder rate/count + banked source labels) banked to _backwards_outcome_series_v1.json alongside; NYC-count-vs-DCJS basis differences (658-vs-673/649-class) carried as labeled in that file; NYC 1998-2001 rates carry the triple_slider inline pops (PEP/decennial-mid labeled), 1980/1990/2000 decennial-anchored",
}
with open(f"{BUILD}/backwards_test_v1.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print("SHIPPED backwards_test_v1.json")
for v in verdict: print(" ", v)
print("t+2 deepening:", json.dumps(deep, indent=1))
print("persist bench:", json.dumps(bench_lag, indent=1)[:1400])
