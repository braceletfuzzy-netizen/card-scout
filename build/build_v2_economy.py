#!/usr/bin/env python3
# build_v2_economy.py — THE ECONOMY-OUTPUT FIT (output-vector v2, family A) v2.
# Inputs (banked Maslow panel ACS strata + care$) -> LAUS unemployment-rate output (pulled this session).
# Laws: direction-class only; within-city FE; walk-forward t+1 BEFORE any call registers; LOCO hold-out;
#       zero fabricated numbers — every cell traces to _econ_pulls_v1.json or maslow_joint_panel_v1.jsonl;
#       honest-null with route named (BFS county grain: api.census.gov/bfs requires key -> honest-null, state-grain series banked).
import json, numpy as np
from scipy import stats

BUILD = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
rows = [json.loads(l) for l in open(f"{BUILD}/maslow_joint_panel_v1.jsonl", encoding="utf-8") if l.strip()]
econ = json.load(open(f"{BUILD}/_econ_pulls_v1.json"))
LAUS = {c: {int(y): v for y, v in s.items()} for c, s in econ["laus_unemployment_rate"].items()}
CITY_MAP = {"NYC": "New York"}

def laus_val(city, year):
    s = LAUS.get(CITY_MAP.get(city, city))
    return s.get(int(year)) if s else None

def frame(spec, want):
    """want: 't0' -> y=laus(t); 't1' -> y=laus(t+1). Inputs all non-null required."""
    out = []
    for r in rows:
        vals = [r.get(c) for c in spec]
        if any(v is None for v in vals):
            continue
        y = int(r["year"])
        if want == "t0":
            yv = laus_val(r["city"], y)
        else:
            yv = laus_val(r["city"], y + 1)
        if yv is None:
            continue
        out.append({"city": r["city"], "year": y, "X": vals, "y": yv})
    return out

def within_city_fit(recs, l2=0.5):
    """Per-city demeaned (within-city FE) ridge. Returns betas + within R2."""
    dm = []
    for c in sorted({r["city"] for r in recs}):
        sub = [r for r in recs if r["city"] == c]
        if len(sub) < 4:
            continue
        X = np.array([r["X"] for r in sub], float); y = np.array([r["y"] for r in sub], float)
        dm.append((X - X.mean(axis=0), y - y.mean()))
    if not dm:
        return {"betas": None, "n_rows": 0, "n_cities": 0, "within_R2": None}
    Xall = np.vstack([x for x, _ in dm]); yall = np.concatenate([y for _, y in dm])
    A = Xall.T @ Xall + l2 * np.eye(Xall.shape[1])
    b = np.linalg.solve(A, Xall.T @ yall)
    resid = yall - Xall @ b
    ss_t = float(((yall - yall.mean()) ** 2).sum())
    r2 = round(1 - float((resid ** 2).sum()) / ss_t, 3) if ss_t > 0 else None
    return {"betas": [round(float(v), 3) for v in b], "n_rows": len(yall),
            "n_cities": len(dm), "within_R2": r2}

def moments(recs):
    out = {}
    for c in sorted({r["city"] for r in recs}):
        sub = [r for r in recs if r["city"] == c]
        X = np.array([r["X"] for r in sub], float); y = np.array([r["y"] for r in sub], float)
        out[c] = {"mean_x": X.mean(axis=0), "sd_x": np.maximum(X.std(axis=0), 1e-9),
                  "mean_y": float(y.mean()), "sd_y": max(float(y.std()), 1e-9), "n": len(sub)}
    return out

def zpred(betas, m, X_row):
    z = (np.array(X_row, float) - m["mean_x"]) / m["sd_x"]
    return m["mean_y"] + float(np.dot(betas, z)) * m["sd_y"]

def dirscore(preds, actuals, means):
    hits = sum(1 for p, a, mu in zip(preds, actuals, means)
               if np.sign(p - mu) == np.sign(a - mu))
    return round(hits / len(preds), 3) if preds else None

SPEC_A = ["bachelors_pct", "poverty_rate", "snap_receipt_share_pct"]
SPEC_B = SPEC_A + ["care_per_100k"]
RESULT = {"_record": "economy_output_fit_v1 (output-vector v2, family A: panel inputs -> LAUS annual unemployment rate, direction-class)",
 "outcome_source": "_econ_pulls_v1.json laus_unemployment_rate - FRED fredgraph.csv LAUCN/LAUSA {fips}000000003A annual 1990-2025 keyless; initial 6-city pull ALIASED (identical series) and was refetched with an identity gate (distinct 2010/2023/2025 values per city recorded in _validation); banked panel unemployment_rate col cross-checked 7/7 within 1pt",
 "honest_nulls": [
   "BFS city/county applications: route api.census.gov/data/timeseries/econ/bfs requires key - honest-null, STATE-grain series banked (FRED BABATOTALNSA*, 2004-2026) and no city-year fit attempted per grain law",
   "BEA county-quad GDP: BEA API requires key - state annual NGSP banked (FRED {ST}NGSP / NGSP{ST}, 1997-2025); city-fit not attempted per grain law"]}

# ---------- t0 fit ----------
t0 = frame(SPEC_A, "t0")
fitA0 = within_city_fit(t0)
mA0 = moments(t0)
RESULT["fit_A_t0"] = {"spec": SPEC_A, **fitA0, "frame": {c: mA0[c]["n"] for c in mA0}}

# ---------- LOCO ----------
locoA = {}
for c_hold in sorted(mA0):
    train = [r for r in t0 if r["city"] != c_hold]
    fit = within_city_fit(train)
    m = mA0[c_hold]
    preds, acts, mus = [], [], []
    for r in [x for x in t0 if x["city"] == c_hold]:
        preds.append(zpred(np.array(fit["betas"]), m, r["X"])); acts.append(r["y"]); mus.append(m["mean_y"])
    locoA[c_hold] = {"direction_acc": dirscore(preds, acts, mus), "n": len(preds),
                     "betas_loco": fit["betas"], "train_rows": fit["n_rows"]}
RESULT["loco_A_t0"] = locoA
loco_mean = round(float(np.mean([v["direction_acc"] for v in locoA.values()])), 3)

# ---------- walk-forward t+1 (temporal; the gate BEFORE any call) ----------
t1 = frame(SPEC_A, "t1")
pairs = sorted(t1, key=lambda r: (r["city"], r["year"]))
wf = {}
pooled_hits = pooled_n = 0
for c in sorted({p["city"] for p in pairs}):
    sub = sorted([p for p in pairs if p["city"] == c], key=lambda p: p["year"])
    hits = n = 0
    detail = []
    for i, p in enumerate(sub):
        train = sub[:i]
        if len(train) < 2:
            continue
        Ztr = np.array([t["X"] for t in train], float); ytr = np.array([t["y"] for t in train], float)
        mx, sx = Ztr.mean(axis=0), np.maximum(Ztr.std(axis=0), 1e-9)
        my, sy = ytr.mean(), max(ytr.std(), 1e-9)
        b = np.linalg.solve(Ztr @ Ztr.T if False else (Ztr - mx) / sx @ ((Ztr - mx) / sx).T + 0.5*np.eye(len(train)),
                            ((ytr - my) / sy))
        # dual-form ridge on standardized train rows (n_train x n_train) — fine for these tiny frames
        Ztrain = (Ztr - mx) / sx
        yc = (ytr - my) / sy
        alphas = np.linalg.solve(Ztrain @ Ztrain.T + 0.5 * np.eye(len(train)), yc)
        zt = (np.array(p["X"], float) - mx) / sx
        pred = my + float(zt @ Ztrain.T @ alphas) * sy
        actual = p["y"]; mu = my
        h = int(np.sign(pred - mu) == np.sign(actual - mu))
        hits += h; n += 1; pooled_hits += h; pooled_n += 1
        detail.append({"input_year": p["year"], "target_year": p["year"] + 1,
                       "pred_dir": float(np.sign(pred - mu)), "actual_dir": float(np.sign(actual - mu)),
                       "hit": bool(h)})
    wf[c] = {"hits": hits, "n": n, "acc": round(hits / n, 3) if n else None, "detail": detail}
RESULT["walk_forward_tplus1"] = {"pooled_direction_acc": round(pooled_hits / pooled_n, 3) if pooled_n else None,
                                 "pooled_n": pooled_n, "per_city": wf, "spec": SPEC_A}

# ---------- secondary fit: +care$ channel ----------
t0b = frame(SPEC_B, "t0")
fitB = within_city_fit(t0b)
RESULT["fit_B_t0_with_care"] = {"spec": SPEC_B, **fitB}

# ---------- BFS descriptive (state grain, honest about it) ----------
bfs = econ["bfs_applications_state"]
RESULT["bfs_descriptive"] = {
  c: {"yoy_growth_2021_2025": {str(y): round(s[y]/s[y-1]-1, 4) for y in range(2021, 2026) if y in s and y-1 in s}}
  for c, s in bfs.items() if s}
RESULT["gdp_descriptive"] = {
  c: {"real? no — NGSP current$ millions; state GDP yoy": {str(y): round(s[y]/s[y-1]-1, 4) for y in range(2021, 2026) if y in s and y-1 in s}}
  for c, s in econ["state_gdp_millions"].items() if s}

json.dump(RESULT, open(f"{BUILD}/_econ_fit_v1.json", "w"), indent=1)
print("FIT t0:", json.dumps(fitA0))
print("LOCO:", {k: v["direction_acc"] for k, v in locoA.items()}, "mean", loco_mean)
print("WF t+1 pooled:", RESULT["walk_forward_tplus1"]["pooled_direction_acc"], "n=", pooled_n,
      {c: v["acc"] for c, v in wf.items()})
print("fitB:", json.dumps(fitB))
print("frame t0/t1:", len(t0), len(t1), {c: mA0[c]["n"] for c in mA0})
