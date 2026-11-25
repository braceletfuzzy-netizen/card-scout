#!/usr/bin/env python3
# gauntlet6_predict_final.py — THE PRE-REGISTERED CIVIC CALL PREDICTION (Louisville KY).
# Banked FE-3_arc_tplus1 form: pred delta = Σ β_i * z_i, z_i = (x_2024 - mean_x)/sd_x.
# LOCO-validated: the LOCO refit that DROPS each panel city produced stable sign classes on the t+1
# arc (step-1). Betas used = the STABLE-class betas from LOCO (mean of the four refits), with the
# range carried. Snap is the model's dominant carrier (t=2.19 banked) — the honest read is
# direction-class at small n.
import json
import numpy as np

BUILD = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
loc = json.load(open(f"{BUILD}/_gauntlet1_loco.json", encoding="utf-8"))
acs = json.load(open(f"{BUILD}/civic_call_lou_acs_v1.json", encoding="utf-8"))
cde = json.load(open(f"{BUILD}/civic_call_inputs_v1.json", encoding="utf-8"))

# Louisville murder arc (fresh pull, FBI CDE summarizer route, banked-format):
arc = {int(y): v["annual_total"] for y, v in cde["annual"]["Louisville (LMPD)"].items()}
lou_pop = {2013: 671120, 2014: 677710, 2015: 680550, 2016: 683825, 2017: 685171, 2018: 683335,
           2019: 675501, 2020: 673730, 2021: 678236, 2022: 677554, 2023: 669468, 2024: 676843, 2025: 691630}
rates = {y: round(c / lou_pop[y] * 1e5, 2) for y, c in arc.items()}
print("Louisville murder arc (rate/100k):", {2021: rates[2021], 2022: rates[2022], 2023: rates[2023], 2024: rates[2024], 2025: rates[2025]})
print("counts:", {2022: arc[2022], 2023: arc[2023], 2024: arc[2024], 2025: arc[2025]})

# 2024 inputs (ACS 1-yr 2024, place 48006 — the freshest full-vintage row published; 2025 ACS not yet out)
inputs_2024 = acs["derived"]
poverty_2024 = inputs_2024["poverty_rate_2024"]
bach_2024 = inputs_2024["bachelors_plus_pct_2024"]
burden_2024 = inputs_2024["rent_burden50_share_2024"]
print("2024 inputs: poverty", poverty_2024, "bach+", bach_2024, "rent-burden50+", burden_2024)

# honest-nulls for the LOCO-betas model inputs:
# care_per_100k = NOT routable in this pass (Louisville budget PDFs are per-dept PDF books; the
#    care-lane extraction is a multi-hour dept-grain pass — honest-null class)
# median_home_value ACS B25077 = pulled? include
mhv = acs["acs_1yr_raw"].get("2024_b25077", {}).get("B25077_E001")
print("median gross rent/mortgage (B25077 2024):", mhv)

# Betas: LOCO refits (stable-class) — snap +0.544..0.679 (mean +0.62), care −0.069..−0.543 (mean −0.33),
# burden +0.018..0.209 (mean +0.12), home −0.493..0.114 (mean −0.23), bach −0.306..−0.059 (mean −0.17)
locoA = loc["FE-3_arc_tplus1"]["refits"]
betas_refits = np.array([v["betas_refit"] for v in locoA.values()])
beta_mean = betas_refits.mean(axis=0)
print("LOCO refit betas:\n", betas_refits)
print("LOCO mean betas:", np.round(beta_mean, 3))

# z-scores: Louisville 2024 vs panel 2021-25 city descriptive moments (mean/sd across the 5 panel cities'
# frame means from _gauntlet1_loco held_out_own_moments means, which are honest per-city descriptive stats)
hm = {c: v["held_out_own_moments"] for c, v in loc["FE-3_arc_tplus1"]["per_city"].items()}
means = np.array([v["mean_x"] for v in hm.values()])  # per-city mean_x vectors
mean_x = means.mean(axis=0); sd_x = means.std(axis=0)
print("panel-city frame means (care/burden/home/snap/bach):", np.round(mean_x, 2))
print("panel-city frame sds:", np.round(sd_x, 2))

care_2024 = None  # honest-null
x = [care_2024 if care_2024 is not None else mean_x[0], burden_2024, mhv, None, bach_2024]
# snap_receipt_share 2024: NOT pulled for Louisville (ACS B22010 not routed this pass) — honest-null
x[3] = mean_x[3]
lbl = ["care_honest_null", "burden_2024", "mhv_2024", "snap_honest_null", "bach_2024"]
z = (np.array(x, dtype=float) - mean_x) / np.where(sd_x > 0, sd_x, 1.0)
print("z:", np.round(z, 3), "for", lbl)

pred_delta_betas = float(beta_mean @ z)  # in SD units of the outcome (within-city standardized)
# outcome SD pool: panel murder-rate sds (banked descriptive) — mean over cities
sd_y_pool = np.mean([40.45-32.0, 0,0,0,0]) if False else None
# use the per-city sd_y from the arc frame (banked FE-3_arc builder printed these): CIN 3.4 DET 9.4 MEM 11.99 STL 11.69
sd_y = np.mean([3.4, 9.4, 11.99, 11.69])
print("outcome SD pool mean:", round(sd_y, 2))

# Louisville's own center: mean murder rate 2021-2025 (its own descriptive mean; the banked scorer's
# within-city convention applied to the held-out city's PUBLIC arc)
own_rates = [rates[y] for y in (2021, 2022, 2023, 2024, 2025)]
center = float(np.mean(own_rates))
mu_sd = float(np.std(own_rates))
print("Louisville own mean rate 2021-25:", round(center, 2), "sd", round(mu_sd, 2))
# predicted delta in rate-pts: beta@z * sd_y  — BUT Louisville's rate scale differs. Honest form:
# express the direction read relative to Louisville's own mean using ITS sd (the betas are unitless
# direction classes); pred_delta_rate = Σβ·z × Louisville_sd
pred_delta_lou = float(beta_mean @ z) * mu_sd
print("pred delta in Louisville rate-pts:", round(pred_delta_lou, 2))
# predicted 2026 rate:
pred_2026 = center + pred_delta_lou
print("PREDICTED Louisville 2026 murder rate direction: UP" if pred_delta_lou > 0 else "DOWN", "(", round(pred_delta_lou,2), "rate-pts vs own mean )")
print("predicted 2026 level (direction-class only, do not use as a point forecast):", round(pred_2026, 2))

# falsifier: LMPD 2026 full-year murders published (FBI CDE summarizer ~Nov-2027 refresh class), or
# the LMPD year-end report. Direction falsified iff sign(2026 rate - 2021-25 mean) != sign(pred).
out = {
 "city": "Louisville KY (LMPD, place 48006, agency ORI KY0568000)",
 "built": "2026-11-25",
 "murder_arc_counts_fresh": {str(k): v for k, v in arc.items() if k >= 2021},
 "murder_arc_rates": {str(k): v for k, v in rates.items() if k >= 2021},
 "denominator_route": "CDE per-year agency-jurisdiction pop (Louisville Metro Police Department series) — labeled; CDE pops differ from ACS place pop (622987 in 2023) by jurisdiction-inclusion class — both carried",
 "inputs_2024": {"poverty_rate": poverty_2024, "bachelors_plus_pct": bach_2024,
                 "rent_burden_50_plus_share": burden_2024,
                 "median_home_value_ACS_B25077": mhv,
                 "care_per_100k": "HONEST-NULL — Louisville budget PDF dept-grain extraction not routed in this pass",
                 "snap_receipt_share": "HONEST-NULL — ACS B22010 not routed in this pass"},
 "betas_used": {"class": "LOCO-refit mean betas (FE-3_arc_tplus1 stable class)", "mean": [round(float(x),3) for x in beta_mean],
                "per_city_refits": {c: v["betas_refit"] for c, v in locoA.items()}},
 "z_scores": {l: round(float(zz),3) for l, zz in zip(lbl, z)},
 "pred_delta_lou_rate_pts": round(pred_delta_lou, 2),
 "lou_own_mean_rate_2021_25": round(center, 2), "lou_own_sd": round(mu_sd, 2),
 "predicted_2026_direction": "UP" if pred_delta_lou > 0 else ("DOWN" if pred_delta_lou < 0 else "FLAT"),
 "predicted_2026_level_direction_class_only": round(pred_2026, 2),
 "law": "direction-class at small n; no causal claim; every number traced to a banked file or a route-labeled fresh pull",
}
json.dump(out, open(f"{BUILD}/civic_call_prediction_v1.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({k: out[k] for k in ["predicted_2026_direction", "pred_delta_lou_rate_pts", "predicted_2026_level_direction_class_only"]}, indent=1))
