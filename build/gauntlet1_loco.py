#!/usr/bin/env python3
# gauntlet1_loco.py v3 — THE HOLD-OUT TEST (LOCO), the banked scorer replicated LINE-FOR-LINE first,
# then re-fit per held-out city. Two forms, both scored with the banked convention
# (hit iff sign(pred - mean_y) == sign(actual(t+k) - mean_y), mean_y = the city's ycol-frame mean):
#   DRIFT-CHECK: fixed banked betas + current on-disk files -> quantifies the frame drift vs banked 0.938.
#   FORM-A "practical-within": betas re-derived on remaining cities; held-out city keeps its OWN
#           descriptive moments (mean_x/sd_x from its complete input rows; mean_y/sd_y from its ycol rows).
#           This is the same information class the banked scorer used (public descriptive stats, not fitted).
#   FORM-B "strict-blind": held-out city contributes NOTHING (train-only pooled moments) — the level-
#           transfer read. Known one-sidedness in actual; labeled.
import json
import numpy as np
from scipy import stats

BUILD = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
rows = [json.loads(l) for l in open(f"{BUILD}/maslow_joint_panel_v1.jsonl", encoding="utf-8") if l.strip()]
outcome = json.load(open(f"{BUILD}/_backwards_outcome_series_v1.json", encoding="utf-8"))
O = {(k.split("|")[0], int(k.split("|")[1])): v for k, v in outcome.items()}

SPEC_FE3 = ["care_per_100k", "cost_burden_30pct_plus_share", "median_home_value", "snap_receipt_share_pct", "bachelors_pct"]
MODELS = {
 "FE-3_maslow_joint_t0": {"spec": SPEC_FE3, "ycol": "murder_rate", "betas": [-0.181,-0.280,-0.099,0.640,-0.003]},
 "FE-3_arc_tplus1":      {"spec": SPEC_FE3, "ycol": "murder_rate_t+1", "betas": [-0.197,0.056,-0.263,0.544,-0.189]},
 "FE-6_care_plus_unemp": {"spec": ["care_per_100k","unemployment_rate"], "ycol": "murder_rate", "betas": [-0.304,0.312]},
 "FE-2_care_cage_bookings": {"spec": ["care_per_100k","cage_per_100k","bookings_per_1000"], "ycol": "murder_rate", "betas": [-0.452,0.419,0.013]},
}
PARTIAL_OUTCOME_YEARS = {2026}

# ---------- banked scorer replica (verbatim from backwards_test v1 script) ----------
def cstats_of(spec):
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

def make_frame(spec, ycol, exclude_city=None):
    recs = []
    for r in rows:
        c = r["city"]
        if exclude_city and c == exclude_city: continue
        vals = [r.get(col) for col in spec]
        if any(v is None for v in vals) or r.get(ycol) is None: continue
        recs.append({"city": c, "year": r["year"], "X": np.array(vals, float), "y": r[ycol]})
    return recs

def city_y_stats(recs):
    out = {}
    for r in recs:
        out.setdefault(r["city"], []).append(r["y"])
    return {c: {"mean_y": float(np.mean(v)), "sd_y": float(np.std(v))} for c, v in out.items()}

def score_banked(name, betas, cstats, mystats, exclude_city=None):
    m = MODELS[name]
    recs = []
    for r in rows:
        c, y = r["city"], r["year"]
        if exclude_city and c == exclude_city: continue
        if c not in cstats or c not in mystats: continue
        X = np.array([r.get(col) for col in m["spec"]], float)
        if np.isnan(X).any(): continue
        cs, ys = cstats[c], mystats[c]
        if any(s <= 0 for s in cs["sd_x"]): continue
        z = (X - cs["mean_x"]) / cs["sd_x"]
        pred = ys["mean_y"] + float(np.dot(betas, z)) * ys["sd_y"]
        for k in (1, 2, 3):
            yt = y + k
            if yt in PARTIAL_OUTCOME_YEARS: continue
            o = O.get((c, yt))
            if not o or o.get("rate") is None: continue
            actual = o["rate"]
            recs.append({"city": c, "t": y, "lag": k, "pred": pred, "actual": actual,
                         "hit": (pred > ys["mean_y"]) == (actual > ys["mean_y"])})
    return recs

# ---------- re-fit on remaining cities (banked within-city standardized OLS) ----------
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
    A = np.column_stack([np.ones(len(Z := Xd / sd)), Z])
    zy = yd / sy
    beta, *_ = np.linalg.lstsq(A, zy, rcond=None)
    b = beta[1:]
    resid = zy - A @ beta
    n_cities_eff = sum(1 for c in sorted({r['city'] for r in recs}) if sum(1 for r in recs if r['city']==c) > 1)
    dof = max(len(zy) - 1 - k - n_cities_eff, 1)
    s2 = float(resid @ resid) / dof
    se_b = np.sqrt(s2 * np.diag(np.linalg.pinv(A.T @ A))[1:]) / sy
    ss = float(zy @ zy)
    r2 = float(1 - (resid @ resid) / ss) if ss > 0 else None
    return b, se_b, r2, len(recs)

RESULT = {}
for name, m in MODELS.items():
    spec, ycol = m["spec"], m["ycol"]

    # --- drift check: fixed betas, banked scorer, current files ---
    drift_recs = score_banked(name, np.array(m["betas"]), cstats_of(spec), city_y_stats(make_frame(spec, ycol)))
    drift = {"n": len(drift_recs),
             "dir_acc": round(float(np.mean([r["hit"] for r in drift_recs])), 3) if drift_recs else None,
             "dir_acc_lag1": (lambda r1: round(float(np.mean([r["hit"] for r in r1])), 3) if r1 else None)([r for r in drift_recs if r["lag"] == 1]),
             "misses": [f'{r["city"]}:{r["t"]}+{r["lag"]}' for r in drift_recs if not r["hit"]]}

    # --- LOCO FORM-A ---
    all_cities = sorted({r["city"] for r in make_frame(spec, ycol)})
    per_city, refits = {}, {}
    for hc in all_cities:
        train = make_frame(spec, ycol, exclude_city=hc)
        tr_cities = sorted({r["city"] for r in train})
        if len(tr_cities) < 2:
            per_city[hc] = {"status": "not_scored", "note": "dropping city leaves <2 cities"}
            continue
        b, se_b, r2, n_tr = fit_fe(train, len(spec))
        refits[hc] = {"n_train_rows": n_tr, "n_train_cities": len(tr_cities),
                      "betas_refit": [round(float(x), 3) for x in b],
                      "se_refit": [round(float(x), 3) for x in se_b],
                      "within_r2": round(r2, 3) if r2 is not None else None}
        # held-out city's own descriptive moments
        hm_y = city_y_stats(make_frame(spec, ycol)).get(hc, {})
        full = cstats_of(spec)
        hm = full.get(hc, {})
        recsA, recsB = [], []
        # FORM-B train-pooled moments
        Xg = np.array([v["mean_x"] for v in [ {"mean_x": np.mean([r["X"] for r in train if r["city"]] or [0], axis=0)} for c in tr_cities ]]) if False else None
        mean_x_g, sd_x_g, mean_y_g, sd_y_g = [], [], [], []
        for c in tr_cities:
            sub = [r for r in train if r["city"] == c]
            Xs = np.array([r["X"] for r in sub], float)
            mean_x_g.append(Xs.mean(axis=0)); sd_x_g.append(Xs.std(axis=0))
            mean_y_g.append(float(np.mean([r["y"] for r in sub]))); sd_y_g.append(float(np.std([r["y"] for r in sub])))
        mean_x_g = np.mean(mean_x_g, axis=0); sd_x_g = np.mean(sd_x_g, axis=0)
        mean_y_g = float(np.mean(mean_y_g)); sd_y_g = float(np.mean(sd_y_g))
        for r in rows:
            c, y = r["city"], r["year"]
            if c != hc: continue
            X = np.array([r.get(col) for col in spec], float)
            if np.isnan(X).any(): continue
            predA = predB = None
            if hm and hm_y and all(s > 0 for s in hm["sd_x"]):
                zA = (X - hm["mean_x"]) / hm["sd_x"]
                predA = hm_y["mean_y"] + float(np.dot(b, zA)) * hm_y["sd_y"]
            zB = (X - mean_x_g) / np.where(sd_x_g > 0, sd_x_g, 1.0)
            predB = mean_y_g + float(np.dot(b, zB)) * sd_y_g
            for k in (1, 2, 3):
                yt = y + k
                if yt in PARTIAL_OUTCOME_YEARS: continue
                o = O.get((hc, yt))
                if not o or o.get("rate") is None: continue
                actual = o["rate"]
                if predA is not None:
                    recsA.append({"t": y, "lag": k, "pred": predA, "actual": actual,
                                  "hit": (predA > hm_y["mean_y"]) == (actual > hm_y["mean_y"])})
                recsB.append({"t": y, "lag": k, "pred": predB, "actual": actual,
                              "hit": (predB > mean_y_g) == (actual > mean_y_g)})
        def summ(recs):
            if not recs: return {"status": "not_scored", "n_pairs": 0}
            l1 = [x for x in recs if x["lag"] == 1]
            rho = None
            if len(l1) >= 3:
                p = np.array([x["pred"] for x in l1]); a = np.array([x["actual"] for x in l1])
                if p.std() > 0 and a.std() > 0:
                    rho = round(float(stats.spearmanr(p, a).statistic), 3)
            return {"status": "scored", "n_pairs": len(recs), "n_pairs_lag1": len(l1),
                    "dir_acc": round(float(np.mean([x["hit"] for x in recs])), 3),
                    "dir_acc_lag1": round(float(np.mean([x["hit"] for x in l1])), 3) if l1 else None,
                    "within_city_rho_lag1": rho,
                    "years": sorted({x["t"] for x in recs})}
        per_city[hc] = {"form_A_practical_within": summ(recsA), "form_B_strict_blind": summ(recsB)}

    # aggregate
    agg = {"cities": {}}
    accs = []
    for hc, v in per_city.items():
        sA = v.get("form_A_practical_within", {})
        if sA.get("status") == "scored" and sA["n_pairs"] >= 3:
            agg["cities"][hc] = {"dir_acc_lag1": sA["dir_acc_lag1"], "n": sA["n_pairs_lag1"],
                                 "rho_lag1": sA["within_city_rho_lag1"]}
            accs.append(sA["dir_acc_lag1"])
    if accs:
        agg.update({"n_cities": len(accs), "mean": round(float(np.mean(accs)), 3),
                    "min": round(float(np.min(accs)), 3), "max": round(float(np.max(accs)), 3)})
    RESULT[name] = {"drift_check_fixed_betas": drift, "refits": refits, "per_city": per_city,
                    "loco_form_A_lag1_distribution": agg,
                    "banked_anchor": "backwards_test_v1.json FE-3_arc_tplus1 t+1 dir=0.938 n=16 (files-then)"}

with open(f"{BUILD}/_gauntlet1_loco.json", "w", encoding="utf-8") as f:
    json.dump(RESULT, f, indent=1, ensure_ascii=False)

for name, r in RESULT.items():
    d = r["loco_form_A_lag1_distribution"]
    print(f"\n== {name} == drift(fixed betas, current files): {r['drift_check_fixed_betas']}")
    print(f"   LOCO-A lag1 dir: n_cities {d.get('n_cities')} mean {d.get('mean')} min {d.get('min')} max {d.get('max')}")
    for c, v in sorted(d.get("cities", {}).items()):
        print(f"     {c:12s} dir {v['dir_acc_lag1']} rho {v['rho_lag1']} n {v['n']}")
