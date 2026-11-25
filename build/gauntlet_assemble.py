#!/usr/bin/env python3
# gauntlet_assemble.py — assemble pre_expansion_gauntlet_v1.json from the four step outputs + step 5/6 inputs.
import json, datetime

BUILD = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
def jl(p): return json.load(open(f"{BUILD}/{p}", encoding="utf-8"))

loco = jl("_gauntlet1_loco.json")
stick = jl("_gauntlet2_residual_stick.json")
scan = jl("_gauntlet34_scan_power.json")
wide = jl("_gauntlet3b_wide_holdouts.json")
churn = jl("_gauntlet5_churn_audit.json")
prereg = jl("pre_registered_civic_call_v1.json")

now = "2026-11-25"
out = {
 "_record": "pre_expansion_gauntlet_v1 — THE PRE-EXPANSION GAUNTLET: all six pre-expansion questions, verdict-first, sequentially gated",
 "built": now,
 "parent_artifacts": ["maslow_joint_panel_v1.jsonl", "joint_regression_v2.json (banked betas)",
   "_backwards_outcome_series_v1.json (584 cells)", "build_backwards_test_v1.py (the proven builder)",
   "budget_efficiency_panel_v1.json (31 residual rows)", "backwards_test_v1.json (the banked 93.8% t+1 anchor)"],
 "laws_held": [
   "zero fabricated numbers — every figure traces to a banked file or is a route-labeled fresh pull",
   "honest-nulls named wherever a lane cannot be priced",
   "no causal claims — direction-class at small n only",
   "each question's verdict EXPLICIT: hold/break/wind/gate-open/gate-shut",
   "sequential gating: step 1 (the expansion gate) had to open before the founder-flavor call was registered",
 ],
 "step1_holdout_test": {
   "question": "Does the banked prediction machine hold on a city NOT in the fit? (LOCO validation vs the banked 93.8% t+1 direction result)",
   "verdict": "GATE-OPEN",
   "drift_check_first": {
     "what": "before any refit: banked fixed betas + CURRENT on-disk files, banked scorer replicated line-for-line",
     "result": "FE-3_arc_tplus1 lag-1 dir = 0.938, n=16 — EXACT replication of the banked 0.938; the banked number is REPRODUCIBLE from the current files, not stale",
     "note": "scoring the full drift-check pool (lags 1-3, n=36) gives 0.694 — all-lags pooling across the 2021-25 decline arc is a different (harder) test than the banked lag-1 headline; both carried",
   },
   "loco_refit_results": {
     "convention": "betas re-derived on remaining cities (within-city standardized OLS); held-out city keeps its OWN descriptive moments; scored at lag-1 with the banked direction convention",
     "per_city_dir_lag1": loco["FE-3_arc_tplus1"]["loco_form_A_lag1_distribution"]["cities"],
     "distribution": loco["FE-3_arc_tplus1"]["loco_form_A_lag1_distribution"],
     "refit_stability": {c: {"betas_refit": v["betas_refit"], "within_r2": v["within_r2"]} for c, v in loco["FE-3_arc_tplus1"]["refits"].items()},
     "other_models": {m: loco[m]["loco_form_A_lag1_distribution"] for m in
                      ["FE-3_maslow_joint_t0", "FE-6_care_plus_unemp", "FE-2_care_cage_bookings"]},
   },
   "plain_english": ("The t+1 MURDER-ARC direction survives being blotted out of its own training set: every one of the four "
     "held-out scores ran 0.75-1.00 (mean 0.812, min 0.75, all within-city rho +0.8 to +1.0), against banked 0.938 "
     "in-sample. The wide care+unemp lane scores even better out-of-fit (mean 0.887). The model's knowledge is not "
     "one city's memorized arc. What does NOT hold: (a) LEVEL transfer — feeding the held-out city with no own "
     "moments (strict-blind) drops St. Louis to 0.00 (its level sits ~30 rate-pts above the training pool); the "
     "machine is a within-city arc instrument, not a between-city level instrument; (b) the FE-2 cage/bookings "
     "instrument (mean 0.525 — coin-flip class). The expansion gate opens for ARC-class expansion.",
   ),
   "honest_laws": ["form-B strict-blind reads are labeled as level-transfer reads, not failures of the arc instrument",
     "Cincinnati/Detroit/Memphis/St.Louis have the complete FE-3 frame; NYC not in the FE-3_arc frame (honest frame note)",
     "every refit n, beta and SE banked in _gauntlet1_loco.json"],
 },
 "step2_residual_stick": {
   "question": "Does the administration-lane residual predict itself next year? (does residual-2022 predict residual-2023?)",
   "verdict": "STICKS (WEAK) — above the 0.3 direction-class threshold POOLED, at the threshold per-city; sign-holds on 1 of 4 city-year 2022->2023 tests",
   "lane": "FE-6_wide efficiency residuals (banked budget_efficiency_panel_v1.json, 31 rows)",
   "per_city": stick["per_city"],
   "pooled": stick["pooled"],
   "founder_literal_2022_2023": stick["founder_literal_2022_2023"],
   "plain_english": ("Pooled lag-1 r = 0.459 (rho 0.521, n=26 consecutive city-year pairs) — above the 0.3 bar: the budget-efficiency "
     "residual is NOT pure wind. But the split is honest: Cincinnati (12 consecutive years, r 0.431) and Detroit (r 0.930) "
     "carry the stickiness; the 2022->2023 literal sign-holds only in Memphis (+2.2 -> +10.2); Cincinnati (+1.4 -> -0.4), "
     "Detroit (+7.8 -> -0.4) and St. Louis (+6.3 -> -8.5) all flip. The instrument measures something durable over a "
     "multi-year arc (Detroit's over-predicted 2020-22 followed by under-predicted 2023-25 is a real run, not noise) "
     "but a single next-year read is coin-toss class. Use the administration instrument on FIRST-HALF/SECOND-HALF "
     "arcs (already the banked convention), never one-year-ahead."),
 },
 "step3_composition_bias": {
   "question": "Would adding poorly-publishing cities plausibly flip any banked coefficient sign?",
   "verdict": "HOLD (with named fragile columns) — the FOUNDER-CARRYING coefficients (care negative, snap positive, FE-6 pair) never flip under any drop-class; the fragile columns are the ones the model's verdict does not lean on",
   "sign_scan": scan["step3_composition_bias"]["sign_stability"],
   "widest_lane_read": {m: scan["step3_composition_bias"]["models"][m] for m in ["FE-6_care_plus_unemp", "FE-3_arc_tplus1"]},
   "wide_lane_holdout_probe": wide,
   "honest_null_cities": scan["step3_composition_bias"]["honest_null_cities"],
   "plain_english": ("Who would the poor publishers be? The banked classes: Jacksonville (ten straight 0/12 non-reporting years), "
     "Raleigh (5/12-months 2014, four-year silence after), Omaha/Fresno/Baltimore/Long Beach/Sacramento/Tucson/San "
     "Francisco/Phoenix/Pittsburgh (single-year month-guards), and 34 cities whose outcome cells exist but whose city "
     "budget-books were never pulled (selection is by INPUT availability, not outcome). When every low-quality row class "
     "is dropped (2025+ forecast-vintage rows; each city in turn), the care beta never flips sign in ANY of the 4 models' "
     "17 variant refits; snap never flips; the FE-6 care+unemp pair never flips. Three columns CAN flip: median_home_value "
     "(Detroit drop), cage (St. Louis drop), bookings (St. Louis drop) — the banked verdict never leans on those three. "
     "Selection bias is BOUNDED, not eliminated: the panel's fragile columns are its non-headline columns."),
 },
 "step4_power_curve": {
   "question": "When should expansion stop — more rows, or deeper rows?",
   "verdict": "DEEPEN FIRST — the SE-shrink curve kinks near n≈150 (SE ~0.35-0.49x today's) and flattens by n≈250 (~0.27-0.38x); n=400 buys only another ~0.06-0.09x — expansion past ~150 city-years stops materially moving t-stats; DEEPENING (more years per existing city + more lanes per city) buys the same sqrt(n) without new fixed-effect intercepts AND without a new honest-null surface",
   "se_shrink_projection": {m: scan["step4_power_curve"][m]["se_shrink_projection"] for m in scan["step4_power_curve"]},
   "within_between_decomposition": {m: {"within_share": scan["step4_power_curve"][m]["new_city_year_within_info_share"],
                                         "between_share": scan["step4_power_curve"][m]["between_city_year_info_share"]} for m in scan["step4_power_curve"]},
   "se_current_per_input": {m: scan["step4_power_curve"][m]["se_current_per_input"] for m in scan["step4_power_curve"]},
   "plain_english": ("The between-city share of murder variance is 53%-87% depending on frame — and fixed effects ABSORB that share "
     "without explaining it. Every new city adds an intercept (dof cost) and a new honest-null surface, while the "
     "between-city variance it contributes is eaten, not used. The t+1 arc frame (the banked headline instrument) is "
     "the exception: it has a 47% within share, so new cities DO add learning there. Recommendation registered: deepen "
     "to ~150 city-years (the sqrt-knee), expand ONLY in the t+1 arc class where the 47% within-share says new cities teach, "
     "and expand one NEW-LANE per city (education/bookings arcs) rather than more cities at the same lanes."),
 },
 "step5_panel_churn": {
   "question": "How much history exists only because a city kept publishing?",
   "verdict": "0.832 CARRY — 116 of 663 banked-window city-years are drop events; the panel exists on a 83% retention base, and the five longest surviving runs (NYC 46, STL 28, CIN 12, DET 14-span, MEM 6) are 100% retained while BOSTON/NOLA/HOUSTON carry 33-63% drops",
   "headline": churn["headline"],
   "per_city_sweep": churn["per_city_sweep"],
   "drop_events_named": churn["banked_drop_events_named"],
   "months_guard_events": churn["months_guard_events"],
   "partials_class": churn["partials_2026_class"],
   "plain_english": ("Every banked window implies history that a publication gap erased: Boston lost 33 of 46 interior "
     "years (crack-era silence), New Orleans 22 of 35 (including the 0/12-months 2025 pass-through year), Houston 13 "
     "of 22, St. Louis 7 straight (2003-2009), Detroit 3, Raleigh 4 after its 5/12-months year. Jacksonville's "
     "bookings lane is defined by the ten-year 0/12 hole. The survivorship law: the panel's 100%-retained runs (NYC "
     "46-year, St. Louis 28-year, Cincinnati 12-year) are runs of CITIES THAT KEPT PUBLISHING — the survivorship is "
     "real but it is CITY-LEVEL publication, not outcome-selection: no panel city's murder arc was dropped for being "
     "high or low; drops are publication-class or format-class only. The models' history exists only because those "
     "six cities' ledgers never went dark in their window."),
 },
 "step6_preregistered_civic_call": {
   "question": "Founder-flavor: one outside-panel city, timestamped falsifiable prediction",
   "verdict": "REGISTERED — Louisville KY (better keyless lanes verified live: FBI CDE summarizer returns full LMPD monthly actuals + agency-pop; Jacksonville hub API gate 401s, Jax CDE 2024-25 pulled only as cross-check)",
   "preregistration": prereg,
   "cron_recheck": {"job_id": "790da3db5eeb", "name": "louisville_civic_call_recheck_10am", "schedule": "0 10 * * *",
                    "script": "~/.hermes/scripts/civic_call_recheck_v1.py (copy banked at build/civic_call_recheck_v1.py)",
                    "exit_codes": "0 pending (partials) | 1 HIT | 2 MISS | 3 route-failure (no claim)",
                    "next_run": "2026-11-25T10:00:00-06:00"},
   "city_choice_reasoning": "Jacksonville carries the banked ten-year 0/12 non-reporting run (the no-2024-bookings class) — its murders lane is exactly the failure class this gauntlet audits; Louisville publishes full monthly actuals + population through the same keyless route with zero gaps 2013-2025",
   "plain_english": ("Louisville was picked because BOTH its lanes answered without a key: the FBG CDE summarizer returns "
     "LMPD's full monthly actuals (2013-2025, zero gaps — against Jacksonville's ten-year silence) and its agency "
     "population block; the ACS strata came through the same keyless www2 route the panel is built on. The call: "
     "Louisville's 2026 rate finishes BELOW its own 2021-25 mean of 30.69. The honest full-read magnitude is out-of-support"
     " (Louisville's strata sit 18-21 SD off the 5-city panel frame) so the magnitude is VOIDED and only the direction "
     "is registered — with the falsifier, the timestamp, and a daily 10am re-check wired to the cron."),
 },
 "six_verdicts_summary": [
   "1 HOLD-OUT: GATE-OPEN — t+1 arc LOCO 0.75-1.00 (mean 0.812); drift-check reproduces the banked 0.938 exactly; arc instrument survives its own blindfolds, level-transfer and FE-2 book no such claims",
   "2 RESIDUAL-STICK: STICKS (WEAK) — pooled lag-1 r 0.459 > 0.3 threshold; arcs carry the signal, single next-year reads do not (1/4 sign-holds 2022->2023)",
   "3 COMPOSITION-BIAS: HOLD, BOUNDED — founder-carrying signs (care-, snap+, FE-6 pair) never flip across 17 drop-refits; home/cage/bookings flips named and they are non-headline columns",
   "4 POWER-CURVE: DEEPEN — kink near n=150, flat by 250; between-city share (53-87%) is absorbed by FE, deepening buys sqrt(n) without new intercepts; expand only in the t+1 arc class (47% within share)",
   "5 PANEL-CHURN: 0.832 CARRY — 116/663 window city-years are drop events; retained runs = cities that never went dark; survivorship is publication-class, not outcome-selection",
   "6 CIVIC CALL: REGISTERED — Louisville DOWN vs own 2021-25 mean 30.69; magnitude voided (out-of-support); falsifier + timestamp + 10am cron live",
 ],
 "gate_for_expansion_intent": "the step-1 gate OPENED (arc-class transfer holds); no catastrophic step-1 failure — no founder question surfaced mid-run",
}
with open(f"{BUILD}/pre_expansion_gauntlet_v1.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print("SHIPPED pre_expansion_gauntlet_v1.json", len(json.dumps(out))//1024, "KB")
for v in out["six_verdicts_summary"]:
    print(" *", v[:150])
