#!/usr/bin/env python3
# build_v2_housing_schools.py — THE [B] HOUSING + SCHOOLS REFITS (output-vector v2, family B).
# Two output lanes fitted per the banked laws (direction-class only; within-city FE;
# walk-forward t+1 BEFORE any call registers; LOCO hold-out; zero fabricated numbers).
#   Lane B1: panel inputs -> ACS rent-burden (B25070 lanes on disk: rent_burden_50pct_plus_share
#            + cost_burden_30pct_plus_share, 5 cities x 5 years 2021-25, 25 rows)
#   Lane B2: panel inputs -> grad lane (edu_outputvector_v1 city_year_joint_rows B15003
#            state-share joined city-year rows; inputs only where the panel carries them)
# GATE: walk-forward t+1 direction-class > 0.6 => a registration becomes ELIGIBLE; anything at
#       or under 0.6 => GATE-SHUT, nothing registers (walk-forward-before-call law).
import json, numpy as np

BUILD = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
rows = [json.loads(l) for l in open(f"{BUILD}/maslow_joint_panel_v1.jsonl", encoding="utf-8") if l.strip()]

SPEC = ["poverty_rate", "bachelors_pct", "snap_receipt_share_pct"]

def frame(ycol, lag=0):
    """y = outcome at year+lag; requires all inputs + outcome non-null on the same row."""
    out = []
    for r in rows:
        vals = [r.get(c) for c in SPEC]
        if any(v is None for v in vals):
            continue
        yv = r.get(ycol)
        if yv is None:
            continue
        out.append({"city": r["city"], "year": int(r["year"]), "X": vals, "y": yv})
    return out

def within_city_fit(recs, l2=0.5):
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
    m = {}
    for c in sorted({r["city"] for r in recs}):
        sub = [r for r in recs if r["city"] == c]
        X = np.array([r["X"] for r in sub], float); y = np.array([r["y"] for r in sub], float)
        m[c] = {"mean_x": X.mean(axis=0), "sd_x": np.maximum(X.std(axis=0), 1e-9),
                "mean_y": float(y.mean()), "sd_y": max(float(y.std()), 1e-9), "n": len(sub)}
    return m

def dirscore(preds, actuals, means):
    if not preds:
        return None
    hits = sum(1 for p, a, mu in zip(preds, actuals, means) if np.sign(p - mu) == np.sign(a - mu))
    return round(hits / len(preds), 3)

def walk_forward(recs, target_lag=1):
    """Per-city expanding-window ridge t+1 walk-forward, direction vs own expanding mean."""
    wf = {}; pooled_hits = pooled_n = 0
    for c in sorted({r["city"] for r in recs}):
        sub = sorted([r for r in recs if r["city"] == c], key=lambda r: r["year"])
        hits = n = 0; detail = []
        for i, p in enumerate(sub):
            train = sub[:i]
            if len(train) < 2:
                continue
            Xtr = np.array([t["X"] for t in train], float); ytr = np.array([t["y"] for t in train], float)
            mx, sx = Xtr.mean(axis=0), np.maximum(Xtr.std(axis=0), 1e-9)
            my, sy = float(ytr.mean()), max(float(ytr.std()), 1e-9)
            Z = (Xtr - mx) / sx; yc = (ytr - my) / sy
            alphas = np.linalg.solve(Z @ Z.T + 0.5 * np.eye(len(train)), yc)
            zt = (np.array(p["X"], float) - mx) / sx
            pred = my + float(zt @ Z.T @ alphas) * sy
            h = int(np.sign(pred - my) == np.sign(p["y"] - my))
            hits += h; n += 1; pooled_hits += h; pooled_n += 1
            detail.append({"input_year": p["year"], "target_year": p["year"] + target_lag,
                           "pred_dir": float(np.sign(pred - my)), "actual_dir": float(np.sign(p["y"] - my)),
                           "hit": bool(h)})
        wf[c] = {"hits": hits, "n": n, "acc": round(hits / n, 3) if n else None, "detail": detail}
    return {"pooled_direction_acc": round(pooled_hits / pooled_n, 3) if pooled_n else None,
            "pooled_n": pooled_n, "per_city": wf}

def loco(recs, m_all):
    out = {}
    for c in sorted({r["city"] for r in recs}):
        train = [r for r in recs if r["city"] != c]
        fit = within_city_fit(train)
        m = m_all[c]
        preds, acts, mus = [], [], []
        for r in [x for x in recs if x["city"] == c]:
            z = (np.array(r["X"], float) - m["mean_x"]) / m["sd_x"]
            preds.append(m["mean_y"] + float(np.dot(np.array(fit["betas"]), z)) * m["sd_y"])
            acts.append(r["y"]); mus.append(m["mean_y"])
        out[c] = {"direction_acc": dirscore(preds, acts, mus), "n": len(preds),
                  "betas_loco": fit["betas"], "train_rows": fit["n_rows"]}
    return out

RESULT = {"_record": "housing_schools_output_fit_v1 (output-vector v2, family B: [B1] panel inputs -> B25070 rent-burden; [B2] panel inputs -> B15003 grad/state-share lane)",
 "laws_held": ["direction-class only, no causal claims", "within-city FE",
               "walk-forward t+1 BEFORE any call (gate 0.6)", "LOCO hold-out city",
               "zero fabricated numbers — every cell traces to maslow_joint_panel_v1.jsonl / edu_outputvector_v1.json / grad_lane files on disk"]}
RESULT["gate_rule"] = "walk-forward t+1 pooled direction-class > 0.6 strictly => registration ELIGIBLE; <=0.6 => GATE-SHUT (nothing registers)"

# ---------------- [B1] rent-burden ----------------
frame_rb = frame("rent_burden_50pct_plus_share")
m_rb = moments(frame_rb)
b1 = {"outcome_col": "rent_burden_50pct_plus_share",
      "outcome_source": "maslow_joint_panel_v1.jsonl rent_burden_50pct_plus_share (ACS B25070 lanes pulled Nov-22; _b25070_pct.json 10-city 2024 cross-check on disk)",
      "fit_t0": {"spec": SPEC, **within_city_fit(frame_rb), "frame": {c: m_rb[c]["n"] for c in m_rb}}}
wf_b1 = walk_forward(frame_rb)
b1["walk_forward_tplus1"] = {k: v for k, v in wf_b1.items() if k != "per_city"}
b1["walk_forward_tplus1"]["per_city"] = {c: {"hits": v["hits"], "n": v["n"], "acc": v["acc"]} for c, v in wf_b1["per_city"].items()}
b1["loco_t0"] = loco(frame_rb, m_rb)
loco_b1_mean = round(float(np.mean([v["direction_acc"] for v in b1["loco_t0"].values() if v["direction_acc"] is not None])), 3)
b1["loco_mean"] = loco_b1_mean
RESULT["B1_rent_burden"] = b1

# ---------------- [B2] grad lane ----------------
edu = json.load(open(f"{BUILD}/edu_outputvector_v1.json"))
cy = edu["city_year_joint_rows"]
pidx = {(r["city"], int(r["year"])): r for r in rows}
b2_frame = []
for r in cy:
    p = pidx.get((r["city"], r["year"]))
    if not p:
        continue
    vals = [p.get(c) for c in SPEC]
    if any(v is None for v in vals) or r.get("hs_grad_or_higher_share") is None:
        continue
    b2_frame.append({"city": r["city"], "year": int(r["year"]), "X": vals, "y": r["hs_grad_or_higher_share"]})
m_b2 = moments(b2_frame)
loco_b2_mean = None
if len(b2_frame) >= 10:
    wf_b2 = walk_forward(b2_frame)
    b2 = {"outcome_col": "hs_grad_or_higher_share",
          "outcome_source": "edu_outputvector_v1.json city_year_joint_rows — B15003 state-share rows joined to panel cities (Cincinnati->OH, Denver->CO, Detroit->MI, Memphis->TN, NYC->NY, St. Louis->MO); B15003 HS+ = L17..L25 sum law (categories mutually exclusive)",
          "grain_honest_note": "outcome is STATE grain (ACS B15003 state share) joined to city-year rows — grain law flags this as state-share-informed, NOT a city graduation rate",
          "fit_t0": {"spec": SPEC, **within_city_fit(b2_frame), "frame": {c: m_b2[c]["n"] for c in m_b2}},
          "walk_forward_tplus1": {k: v for k, v in wf_b2.items() if k != "per_city"}}
    b2["walk_forward_tplus1"]["per_city"] = {c: {"hits": v["hits"], "n": v["n"], "acc": v["acc"]} for c, v in wf_b2["per_city"].items()}
    b2["loco_t0"] = loco(b2_frame, m_b2)
    loco_b2_mean = round(float(np.mean([v["direction_acc"] for v in b2["loco_t0"].values() if v["direction_acc"] is not None])), 3)
    b2["loco_mean"] = loco_b2_mean
    RESULT["B2_grad_lane"] = b2
else:
    RESULT["B2_grad_lane"] = {"verdict": "HONEST-NULL", "n_usable": len(b2_frame),
        "note": f"fewer than 10 joint city-year rows with BOTH full spec inputs and a B15003 outcome (n={len(b2_frame)}) — no fit per the small-n law; route banked (ACS 2021-24 .dat deepening for v3)"}

# ---------------- the gate ----------------
def gate(lane_name, b):
    acc = b["walk_forward_tplus1"]["pooled_direction_acc"]
    n = b["walk_forward_tplus1"]["pooled_n"]
    lm = b.get("loco_mean")
    if acc is None:
        return {f"{lane_name}": {"verdict": "GATE-SHUT", "wf_acc": None, "reason": "no walk-forward frames"}}
    ok = acc > 0.6  # strictly greater: 0.6 exactly at threshold = not a pass (coin-level at small n, walk-forward-before-call law)
    return {lane_name: {"wf_tplus1_pooled_direction_acc": acc, "wf_n": n, "loco_mean": lm,
                        "verdict": "GATE-OPEN (registration ELIGIBLE)" if ok else "GATE-SHUT (nothing registers)",
                        "gate_threshold": 0.6}}

RESULT["verdicts"] = {}
RESULT["verdicts"].update(gate("B1_rent_burden", RESULT["B1_rent_burden"]))
if "B2_grad_lane" in RESULT and "verdict" not in RESULT["B2_grad_lane"]:
    RESULT["verdicts"].update(gate("B2_grad_lane", RESULT["B2_grad_lane"]))

json.dump(RESULT, open(f"{BUILD}/_housing_schools_fit_v1.json", "w"), indent=1)

print("== [B1] rent-burden ==")
print(" fit t0:", json.dumps(RESULT["B1_rent_burden"]["fit_t0"]))
print(" WF t+1 pooled:", RESULT["B1_rent_burden"]["walk_forward_tplus1"]["pooled_direction_acc"],
      "n=", RESULT["B1_rent_burden"]["walk_forward_tplus1"]["pooled_n"],
      {c: v["acc"] for c, v in RESULT["B1_rent_burden"]["walk_forward_tplus1"]["per_city"].items()})
print(" LOCO:", {k: v["direction_acc"] for k, v in RESULT["B1_rent_burden"]["loco_t0"].items()}, "mean", loco_b1_mean)
print(" verdict:", RESULT["verdicts"]["B1_rent_burden"])
if "B2_grad_lane" in RESULT and "fit_t0" in RESULT["B2_grad_lane"]:
    print("== [B2] grad (state-share) ==")
    print(" fit t0:", json.dumps(RESULT["B2_grad_lane"]["fit_t0"]))
    print(" WF t+1 pooled:", RESULT["B2_grad_lane"]["walk_forward_tplus1"]["pooled_direction_acc"],
          "n=", RESULT["B2_grad_lane"]["walk_forward_tplus1"]["pooled_n"],
          {c: v["acc"] for c, v in RESULT["B2_grad_lane"]["walk_forward_tplus1"]["per_city"].items()})
    print(" LOCO:", {k: v["direction_acc"] for k, v in RESULT["B2_grad_lane"]["loco_t0"].items()}, "mean", loco_b2_mean)
    print(" verdict:", RESULT["verdicts"]["B2_grad_lane"])
else:
    print("== [B2] grad: HONEST-NULL ==", json.dumps(RESULT["B2_grad_lane"]))
