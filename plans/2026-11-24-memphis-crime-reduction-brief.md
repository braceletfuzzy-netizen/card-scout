# THE MEMPHIS POLICY BRIEF — Three Levers, Ranked, Each With a Falsifier

**Built:** 2026-11-24
**Status:** DESIGN ARTIFACT — examine-first, not advocate-first (the policy-queue law, same as the yard-crew sibling brief)
**Sibling doc:** `2026-11-23-memphis-yard-crew-brief.md` (same falsifier discipline, same zero-fabricated-dollars law)

**The laws this brief holds, in writing, up front:**
1. **Zero fabricated dollars** — no projected dollar value appears anywhere in this brief unless it was published by a source file. The yard-crew brief's placeholder-for-quotes pattern is the template; the lever magnitudes here are percentage/effect classes, not dollar projections.
2. **Every magnitude carries its source file** — every number traces to a file in `For You/PolyScout/build/` named inline. No outside speculation.
3. **Direction-class honesty** — where the panel is thin (n small, degrees-of-freedom low), the read is flagged DESCRIPTIVE. Nothing here is a causal Memphis estimate.
4. **Honest nulls are named** — cells that don't exist (eviction judgment rates 2019–2023, PIT counts 2013/2016) are printed as absent, never backfilled.
5. **Plain English first** — the next paragraph is the whole brief in one breath, before any mechanism.

---

## 1. THE ONE-PARAGRAPH VERSION (plain English)

Memphis recorded 188 murders in 2025. A 5–10% reduction in that number is **9–19 fewer deaths in one year** — 9–19 families that keep a son, a father, a daughter. At the 2023 peak of ~350, the same 5–10% band is **17–35 fewer deaths**. The founder's question — "can we get 5–10%?" — is not a moonshot ask. It sits inside the effect classes this work has now measured three independent ways: the city's own budget-and-blight panel (the care/cage file), the strongest published field experiments on the exact interventions Memphis controls (the lit bank), and the wage-structure read of why Memphis carries a high murder margin at all (the ladder file). This brief ranks the three levers by how fast they work and who owns them, names exactly what would falsify each one, and specifies the ledger that will catch a failed lever early. Nothing here promises a number; each lever carries the band it measured and the pre-registered test that will kill it if it deserves to die. [Certain — the frame and the laws; each magnitude below carries its file]

**The deaths arithmetic, tagged:**
- 5–10% of 188 = 9–19 fewer deaths. [Arithmetic on the founder's 2025 count; the bank holds Memphis 2025 = 184, `maslow_joint_panel_v1.jsonl` / `murders_all_v1.json` — the ~4-count gap is a bookkeeping-window difference and does not move the band: 5–10% of 184 = 9–18]
- 5–10% of ~350 = 17–35 fewer deaths. [Arithmetic on the founder's 2023 peak year; the bank holds 2023 = 344, same sources — the band moves by at most a fraction of a death]
- 2026 running count 147 with the system-change flag per the archive lane. [`murders_all_v1.json`]

---

## 2. THE THREE LEVERS, RANKED

### LEVER-1 — CODE-ENFORCEMENT REMEDIATION (fastest, city-ownable)

**What it is, one sentence:** Fix the visible built environment — vacant lots, abandoned buildings, overgrown yards, graffiti, illegal dumping — on a schedule, on targeted corridors, with the city's existing code-enforcement machinery.

**The measured magnitude (with source files):**
- The published causal anchor: abandoned-building remediation cut firearm violence **−39%** (95% CI −28 to −50); vacant-lot remediation **−4.6%** (CI −4.2 to −5.0); per-$1 of building remediation $5 taxpayer / $79 societal return; lot remediation $26 taxpayer / $333 societal. [Cite: Branas AJPH-2016, as stored in `gray_safety_lane_v1.json` lit_magnitude block]
- The citywide cluster-RCT replication: 541-lot greening reduced firearm shootings in below-poverty-median neighborhoods, with **NULL in the poorest neighborhoods** — the targeting law (Section 4). [Cite: Branas AJPH-2019, `peer_review_scan_v18.jsonl`]
- The citywide police-reported class the yard-crew sibling brief already banked: −13.3% police-reported crime, −29.1% gun violence from the lot-greening arm. [`peer_review_scan_v18.jsonl` (Branas PNAS-2018 arm) + yard-crew brief §3b]
- The durability read: at a 10-year follow-up, sustained greening still showed **−12% any-crime / −11% violent crime** (contamination-adjusted). [Cite: PNAS-2026, `gray_safety_lane_v1.json` lit_magnitude]
- The Memphis-side machinery, verified live: the city's 311 system carries **122,270 code-enforcement-class calls in 2026 (26.5% of all calls)** — overgrown yard/trash 40,002, vacant/overgrown property 9,788, illegal dumping 5,337, graffiti classes ~12,500 combined, structure-maintenance multi-tenant ~9,872. [Cite: `gray_safety_lane_v1.json`, Memphis exposure_side]
- The honest caveat on our own panel: city-year 311-call volume does NOT track same-year murder (r = +0.006, n=53) and the pooled forward arc (r = +0.344 t+1, +0.394 t+2) is city-heterogeneous (Memphis within-city r = −0.76, St. Louis +0.51) — so our lane is direction-class only; the causal freight rides on the published lot/building-grain experiments. [Cite: `gray_safety_lane_v1.json` + `gray_safety_lane_tests_v1.json`]

**Cost class:** Low. The intake lane exists (311/AGOL is keyless and already pulling — verified in the lane file); the intervention is mow-edge-plant-board-fence, the yard-crew brief's exact intervention family. NO dollar projection is quoted here; the yard-crew brief holds that law and this lever inherits it.

**Timeline:** Months. This is the only lever that can show corridor-level movement inside one budget year, which is why it is ranked first.

**The falsifier (pre-registered):** The **pre/post corridor differential**. Pick treated corridors and matched non-treated corridors BEFORE the first mow. If treated corridors do not improve relative to controls on service-request volume and incident counts after the treatment window (the panel's t+1 arc says the read window is next-year, not same-year), the lever's Memphis transfer fails and it is demoted honestly. Guard: the yard-crew lag-arc rule — a 3-month null is NOT the falsifier firing; the read is at 12 months, against a control set. [Method frame: `gray_safety_lane_v1.json` t0-vs-t+1 structure + yard-crew brief §7 falsifier pattern]

---

### LEVER-2 — THE LADDER: GROW THE SPECIALIZED BAND + FILL THE MIDDLE (durable, 2–4 years)

**What it is, one sentence:** Grow the share of Memphis jobs that are Computer/Math and Management ("CM+Mgmt") and the pay at the 90th-percentile ceiling — through anchor-employer deals with clawbacks, local-hire contracts on city money, and community-college tracks into the band — because the murder margin tracks the top of the wage structure, not the floor.

**The measured magnitude (with source files):**
- The ranked-relationships read (between-city, cross-sectional, n=8): p10 x murder-2020s-mean **−0.452**, median **−0.667**, p90 **−0.857**. The read steepens UP the wage structure — the ceiling is the strongest single input, not the floor. [Cite: `joint_regression_v2.json` between_reads; n=8 = direction-class only]
- The occupation-mix anatomy: Memphis holds **29.1% CM+Mgmt** inside its specialized band vs **Houston 44.6%** (Boston 49.7, NYC 42.8). The band shares of employment are similar everywhere (~23–28%) — the lever is WHAT IS IN THE BAND and WHAT IT PAYS (band weighted-mean x p90 **+0.98**, n=10), not the band's size. [Cite: `occupation_mix_v1.json` headline_read + band_share_x_p90_correlations]
- What Memphis's band actually holds: Registered Nurses 13,760 @ $87,370, Gen&Ops Managers 9,730 @ $132,440 — Houston's equivalent layer rests on 97,320 G&OMs + 65,910 RNs + 28,400 Software Developers-class mass, ~5x bigger. [Cite: `occupation_mix_v1.json` band_mass blocks]
- The wage-strata anchors: Memphis p10 $28,880 / median $46,890 / **p90 $100,640** vs Houston p90 $128,040. [Cite: `wage_stratified_v1.json` rows; verified BLS-verbatim in `occupation_mix_v1.json` verify_against_banked]
- The same-occupations-pay-different truth: Houston pays its OWN band members ~10–15% more in shared groups (Computer/Math $119,519 vs $103,044; Business/Financial $101,463 vs $85,157) — the gap is both mix and level, so the lever has two dials. [Cite: `occupation_mix_v1.json` headline_read]
- The access dial (the transport half): Memphis transit commute-share **0.47–0.78% across 2021–2024** — roughly **3–8x below the income-peer midwest set** (Cincinnati 3.9–6.6%, STL 4.9–7.9%, Detroit 3.9–5.6%). And the commute-TIME null: Memphis mean commute 21.4 min = flat mid-pack, no within-city movement across the panel — the service.absence, not the distance, is the deficit. [Cite: `worker_ladder_acs1yr_commute_v1.json` the_reads; the poverty-band anatomy (69.8% of below-poverty workers drive alone, only 3.1% reach work by transit) in `lane13_transport_lever_v1.json`]
- The commute↔band join: mean-commute-2024 x OEWS band weighted-mean **+0.963** / x p90 **+0.929** (n=6, between-city). [Cite: `worker_ladder_acs1yr_commute_v1.json` band_mean_join]
- The youth-jobs RCT class (the sharpest rung on the ladder): summer youth employment cut violent-crime arrests **−33–43%** during the treatment summer — the only randomized-proven violence lever in the scan. [Cite: Heller Science-2014, `peer_review_scan_v17.jsonl`]
- The moderation clause: employment-program effects concentrate when targeted; the READI high-bar test (18-month transitional jobs + CBT, N=2,456) returned null on its primary violent index. [Cite: READI QJE-2023 + CPP targeting framework, `peer_review_scan_v17.jsonl`]
- The neighborhood-mechanism clause: Sampson's collective efficacy mediates the disadvantage→violence channel — any facility or program on the ladder pays through neighborhood trust, which is why the youth-activities inventory matters (59 venue rows, Memphis's 28 with subsidy columns: 11 tax-subsidized-public / 11 nonprofit). [Cite: Sampson Science-1997, `peer_review_scan_v18.jsonl`; `youth_activities_inventory_v1.json` density_metrics_v1]

**Cost class:** Medium-high and multi-year — anchor-deal structures (clawbacks per job delivered), local-hire contract language, and community-college tracks. The clawback design means the city's cost exposure is conditional on employer performance. NO dollar projection is quoted.

**Timeline:** 2–4 years for the mix to move (the ceiling read `wage_stratified_v1.json` is a snapshot — its own grain note says no within-city wage arc exists, so the movement itself is a thing to measure going forward, not a banked fact).

**The falsifier (pre-registered):** Two-part. (a) **The band-mix falsifier:** if Memphis CM+Mgmt band-share and band weighted-mean wage have not moved off the 29.1%/$102,341 anchors after the clawback-deal cohort's first contracts conclude (the anchors are in `occupation_mix_v1.json` / `worker_ladder_acs1yr_commute_v1.json` band_mean_join), the lever's mix dial failed. (b) **The access falsifier (pre-registered in lane13 already):** if Memphis transit-access share does NOT clear out of the 0.47–0.78% band after the access investments land, the lane dies honestly — the pre-registered per one-pager #3 falsifier text in `lane13_transport_lever_v1.json`. The judge is the annual ACS 1-YR re-pull, the same keyless route already banked in `worker_ladder_acs1yr_commute_v1.json`.

---

### LEVER-3 — CARE, SUSTAINED (slower; needs 3–4 years)

**What it is, one sentence:** Hold and grow the city's care capacity — the treatment/housing/community-services dollar line ("care" as the panel defines it: care-per-100k) — not as a one-year boost but as a **standing capacity**, because the panel's own stock-vs-flow read says the standing thing is what carries the effect.

**The measured magnitude (with source files):**
- The flow card (one-year change): +10% care in one year = **−0.16 rate-points, n=31, t −0.22** — noisy, direction-class; the honest read of a one-year bump is approximately nothing measurable. [Cite: `elasticities_v1.json` A_DELTA_ELASTICITIES + verdict]
- The stock cards (the standing capacity read): +10% sustained = **−1.48 rate-pts (FE-3 t0) / −0.89 t+1**; **FE-6 −1.80**; **FE-2 −2.26**. [Cite: `elasticities_v1.json` B_STANDARDIZED_BETA_TO_ELASTICITY_CONVERT + `stock_flow_elasticities_v1.json` stock rows]
- **The multiply-once law:** the same panel read as a stock runs ~**11.6x** (spec FE-6) / ~**9.5x** (spec FE-3) the one-year-flow read — a flow dollar moves nothing until it stands as capacity; the level betas carry the co-movement of the standing thing. The rule this imposes: the effect is claimed ONCE for the stock, not compounding year over year. [Cite: `stock_flow_elasticities_v1.json` the_multiplier]
- The persistence honest-null: year-over-year care changes do not persist (AR1 rho **−0.104**, n=58, t −0.7) — budgets are annual votes, not stocks; the machine therefore does NOT extrapolate a care bump forward. [Cite: `elasticities_v1.json` care_persistence_AR1 + verdict honest-limits]
- The compounding-correct re-read: cumulative care change over the window lifts the t+2 direction-accuracy (FE-3_t0 0.333→0.909 at n=11; FE-6 0.538→0.812 n=16) — the sustained-window read is the one the machine confirms. [Cite: `elasticities_v1.json` C_COMPOUNDING_CORRECT_RE_READ]

**What this means for the 5–10% band (the honest arithmetic):** On the frame-mean-scale converter, FE-6's +10% sustained ≈ −1.8 rate-points on murder rate against a pooled frame mean near 35 — roughly a 5% class movement; FE-2's −2.26 is slightly stronger. A **sustained +15–35% care-stock build held 3–4 years is the class that spans the founder's 5–10% band** across the stock machines. This is a direction-class statement off small-n panel machines (n=18–36) — it is the strongest the bank can honestly say, and no stronger. [Cite: `elasticities_v1.json` D_CONVERTER_EXAMPLES + `stock_flow_elasticities_v1.json`; DESCRIPTIVE, not causal]

**Cost class:** Highest — this is the recurring budget line, which is exactly why the multiply-once law matters (a reallocated-dollar design beats a new-dollar ask, and the t+1 arc means the read window is year 2+, not the launch year).

**Timeline:** 3–4 years. The panel's t+2 cells are where the re-read lifts; a 1-year read of this lever is a measurement error, not a verdict.

**The falsifier (pre-registered):** The **stock-test falsifier**. Pre-commit the annual care-per-100k series (the panel's own countable). If the city holds the sustained build 3+ years and the murder-rate direction does not move against the within-city baseline the panel machine predicts, the stock read fails for Memphis and the lever is demoted to cost-neutral housekeeping. Additionally the one-year bump is ITSELF a falsified approach under the bank (the flow card is the honest null) — funding a 1-year spike and pointing at nothing is a prediction the bank already rejects.

---

## 3. WHAT NOT TO DO (the banked anti-patterns)

1. **The one-year care bump.** The flow card is the honest null: +10% in one year = −0.16 rate-points, t −0.22. It reverts; the AR1 persistence read (rho −0.104) says the next year carries nothing. A one-year funding announcement is NOT the lever. [`elasticities_v1.json`]

2. **Top-end-only incentives.** The ceiling read says the p90 wage is the strongest correlate — but the mix lever is CM+Mgmt DENSITY, not band SIZE (band-share-of-employment is ~flat across metros and even runs NEGATIVE vs p90, −0.469, while band weighted-mean runs +0.984). Sprawling the band with low-band-grade jobs leaks; growing the CM+Mgmt density inside it is the lever. [`occupation_mix_v1.json` band_share_x_p90_correlations]

3. **Untargeted remediation spending.** The targeting law: the lot-greening RCT fired in below-poverty-median neighborhoods and was NULL in the poorest; the employment-program clause says effects concentrate in mid-disadvantaged targeting and generic spending underperforms. Equal-by-square-mile distribution is the anti-design; mid-disadvantaged corridors (per the 2019 citywide cluster-RCT) are the design. [`peer_review_scan_v18.jsonl` Branas-2019; `peer_review_scan_v17.jsonl` CPP-targeting]

4. **One-year pilot reads judged as verdicts.** The lag-arc law from the sibling brief: the panel shows same-year nulls and forward arcs; killing a lever at 3 months is a measurement mistake. [Yard-crew brief §7 falsifier #6]

---

## 4. THE VERIFICATION APPARATUS

**The panel (what exists now):** The 94-city-year joint panel (`maslow_joint_panel_v1.jsonl`) is the standing machine — city x year rows carrying care-per-100k, murder counts/rates (t0/t+1/t+2 arcs), plus the lane files that extend it: the gray/311 panel (97 rows, `gray_safety_lane_panel_v1.json`), the worker-ladder commute column (24 city-years, 2021–2024), and the OEWS strata snapshot. Every read in this brief ran on this apparatus; nothing above it was used.

**The machine (the rules it runs under):** within-city demeaned (the banked FE convention), contiguous-year pairs only, honest-null cells never backfilled, direction-class with descriptive t-stats carried verbatim, and the two-machine structure — stock machines (levels, the durable read) and flow machines (changes, the honest-null read). Each lane's re-run route is a keyless re-pull of the same file it built from (`_lane13_gray_*.py` for 311, `worker_ladder_lane_build.py` for ACS/OEWS, the elasticity build for the panel) — every falsifier below can be re-run by re-executing the banked scripts. [`elasticities_v1.json` laws_held; per-file `laws_held` blocks]

**The pre-registered falsifiers, all in one place:**

| # | Watch | Falsifier fires when | Read window | Source file that re-runs it |
|---|-------|----------------------|-------------|------------------------------|
| F1 | Corridor differential (Lever-1) | Treated corridors show no pre/post improvement vs matched controls on 311-class volume + incident counts | 12 months (lag-arc guard: not a 3-month read) | `gray_safety_lane_v1.json` + panel re-pull |
| F2 | Care stock direction (Lever-3) | Sustained care build 3+ yrs with no murder-rate direction move vs within-city machine baseline | t+1 through t+2 | `elasticities_v1.json` + `maslow_joint_panel_v1.jsonl` |
| F3 | Band-mix anchors (Lever-2) | CM+Mgmt band-share stays 29.1% and band weighted-mean stays ~$102,341 after first clawback cohort concludes | 2–4 yrs | `occupation_mix_v1.json` (OEWS annual re-pull, keyless route banked) |
| F4 | Transit access (Lever-2) | Transit commute-share stays inside 0.47–0.78% after access investments land | annually | `worker_ladder_acs1yr_commute_v1.json` (ACS 1-YR re-pull, keyless route banked) |
| F5 | PIT homelessness series (outcome watch) | The January point-in-time stock moves in the WRONG direction while the levers run (or stands flat, honestly) | annually, one number | `pit_homelessness_lane_v1.json` (HUD per-CoC route banked) |
| F6 | Eviction judgment rates (outcome watch) | F5-parallel watch on the judgment-rate series — with the honest-null carried: standardized place-grain judgment rates DO NOT EXIST for 2019–2023 (Eviction Lab CTR suspension); filings-proxy only, 4 tracked cities | annually | `eviction_rate_lane_v1.json` |
| F7 | Health outcomes (outcome watch) | County life-expectancy and drug-poisoning companions move wrong vs the murder direction | annually (county grain, companion only) | `health_outcome_lane_v1.json` |

**The outcome watches (F5–F7) are the honest-context block:** the PIT lane is a static stock, read once a year, never as a flow (2013 and 2016 are verified-absent HUD gaps, 8/8 CoCs, 404 — banked nulls, never backfilled). The eviction lane carries its covid-freeze flag and its null years in plain sight. The health lane is county-grain only under the grain-law, never blended into the city-year panel. These watches are NOT lever verdicts — they are the canaries that tell us whether the neighborhood's whole condition is moving with the levers or against them. [Cite: the three `*_lane_v1.json` files' laws_held blocks]

**The direction-class discipline, restated once:** every regression row in the bank carries n, t-stats described as DESCRIPTIVE, and the within-city convention. The n-saturated cells (dof=5-class) are printed as descriptive-only throughout. This brief makes no causal city-year claim anywhere; the only double-digit causal percentages it carries are the published RCT/quasi-experimental magnitudes, named as such with their own sources. [`elasticities_v1.json` / `joint_regression_v2.json` / all lane files, laws_held]

---

## 5. SOURCES — the file map (every figure traced)

| Figure used in this brief | Value(s) | Source file |
|---------------------------|----------|-------------|
| Care flow card: +10% one-year = −0.16 rate-pts, n=31, t −0.22 | −0.16 / n31 / t−0.22 | `elasticities_v1.json` (A_DELTA_ELASTICITIES + verdict) |
| Care stock cards: +10% sustained = −1.48 (FE-3 t0) / −0.89 (t+1); FE-6 −1.80; FE-2 −2.26 | as stated | `elasticities_v1.json` (B/D blocks); `stock_flow_elasticities_v1.json` (stock rows) |
| Stock-over-flow multiplier 11.6x / 9.5x | 11.6 / 9.5 | `stock_flow_elasticities_v1.json` (the_multiplier) |
| Care persistence rho −0.104 (n=58, t −0.7) | −0.104 | `elasticities_v1.json` (care_persistence_AR1) |
| Compounding-correct re-read lifts (0.333→0.909 n=11; 0.538→0.812 n=16) | as stated | `elasticities_v1.json` (C_COMPOUNDING_CORRECT_RE_READ) |
| Gray-lane panel: t0 ~zero r+0.006 n=53; forward +0.344 t+1 (n=43), +0.394 t+2 (n=37); reverse ~zero r+0.027; per-city heterogeneous (MEM −0.76 …) | as stated | `gray_safety_lane_v1.json` + `gray_safety_lane_tests_v1.json` |
| Branas AJPH-2016: building remediation −39% firearm (CI −28 to −50); lot −4.6%; ROI $5/$79, $26/$333 | as stated | `gray_safety_lane_v1.json` (lit_magnitude) |
| Branas AJPH-2019 citywide cluster-RCT: below-poverty-median fires, poorest NULL — the targeting law | as stated | `peer_review_scan_v18.jsonl` |
| Kondo PLoS-ONE-2015 DiD: no spatial displacement | as stated | `gray_safety_lane_v1.json` (lit_magnitude) |
| PNAS-2026 10-yr durability: sustained greening −12% any-crime / −11% violent | as stated | `gray_safety_lane_v1.json` (lit_magnitude) |
| Memphis 311 code-enforcement class 2026: 122,270 calls, 26.5% of all; top classes enumerated | as stated | `gray_safety_lane_v1.json` (Memphis exposure_side) |
| Worker ladder: between-city commutes x band-wmean +0.963 / x p90 +0.929 (n=6); within-city null | as stated | `worker_ladder_acs1yr_commute_v1.json` (band_mean_join + honest_null_verdict) |
| Memphis transit-access 0.47/0.56/0.78/0.55% = 3–8x below income-peer mids | as stated | `worker_ladder_acs1yr_commute_v1.json` (the_reads) |
| Poverty-band anatomy: 69.8% below-poverty workers drive alone; 3.1% by transit | as stated | `lane13_transport_lever_v1.json` (the_finding) |
| Memphis CM+Mgmt 29.1% vs Houston 44.6% (Boston 49.7, NYC 42.8); band-wmean x p90 +0.98(4); band-share vs p90 −0.469 | as stated | `occupation_mix_v1.json` (headline_read + correlations) |
| Band mass anatomy: Memphis 13,760 RN + 9,730 G&OM vs Houston 97,320 G&OM + 65,910 RN + 22,940 SW-dev | as stated | `occupation_mix_v1.json` (band_mass + headline_read) |
| Same-occupations Houston premium ~10–15% (CM $119,519 vs $103,044 etc.) | as stated | `occupation_mix_v1.json` (headline_read) |
| Wage strata Memphis p10 $28,880 / median $46,890 / p90 $100,640; Houston p90 $128,040 | as stated | `wage_stratified_v1.json` rows; verified in `occupation_mix_v1.json` verify_against_banked |
| Between-city strata x murder: p10 −0.452 / median −0.667 / p90 −0.857 (n=8) | as stated | `joint_regression_v2.json` (between_reads + verdict) |
| Panel n=94 city-years; FE machines (FE-2 n19, FE-3 n24/n18, FE-6 n36) | as stated | `maslow_joint_panel_v1.jsonl`; `joint_regression_v2.json` (fe_within_regressions) |
| Memphis murder counts 2023=344, 2024=248, 2025=184, 2026=147 (rate 30.2) | as stated | `maslow_joint_panel_v1.jsonl`; `murders_all_v1.json` |
| Heller summer jobs −33–43% violent arrests (RCT) | as stated | `peer_review_scan_v17.jsonl` |
| READI QJE-2023: primary ~null (−65% shooting arrests p=.13, N=2,456) | as stated | `peer_review_scan_v17.jsonl` |
| Sampson collective-efficacy mediating (Science-1997) | as stated | `peer_review_scan_v18.jsonl` |
| Youth activities: 59 venue rows total; Memphis 28 by subsidy class (11 public/11 nonprofit) | as stated | `youth_activities_inventory_v1.json` (density_metrics_v1) |
| PIT homeless lane: 112 rows 2010–2025 x 8 cities; PIT 2013/2016 verified-absent honest-nulls; Memphis-2023 1,292 truth-check | as stated | `_bob19_outputs/pit_homelessness_lane_v1.json` |
| Eviction lane: 48 rows; judgment rates 2016–2018 only; 2019–2023 place-grain rates DO NOT EXIST | as stated | `_bob19_outputs/eviction_rate_lane_v1.json` |
| Health outcomes: 84 LE + 228 drug-poisoning county rows; county grain, companion only; LE x murder +1.32 (n=200) direction-class | as stated | `_bob19_outputs/health_outcome_lane_v1.json` |
| Raleigh Springs site read: post-2020 crime bbox series, $41.94M HCD-committed, pre-2016 honest-null | as stated | `raleigh_springs_site_v2.json` |
| Camp Washington skatepark (Cincinnati) third-site read: $950k class, 2026-08-27 open | as stated | `third_site_v1.json` |
| Kingsport lane: three-line site panel + county-substitute grain flags | as stated | `kingsport_three_line_v1.json` |
| The founder's 2025 count 188 / 2023 peak ~350 (framing; bank holds 184/344 — band moves by ≤ a fraction of a death) | as stated | parent-task framing; cross-checked to `murders_all_v1.json` / `maslow_joint_panel_v1.jsonl` |

**Honest-nulls named in one list (never backfilled, per the law):**
- Eviction Lab standardized place-grain judgment rates 2019–2023: DO NOT EXIST (CTR suspension). [`eviction_rate_lane_v1.json`]
- PIT per-CoC counts 2013 and 2016: HUD published nothing at the route for any CoC (404, 8/8 verified). [`pit_homelessness_lane_v1.json`]
- Memphis 311 pre-2024: system carries bulk volume 2024+ only (2020–23 rows are switch artifacts, flagged). [`gray_safety_lane_v1.json`]
- St. Louis 2015 311 year: official file byte-empty = missing, not zero. [`gray_safety_lane_v1.json`]
- ACS 1-YR commute pre-2020: 404-verified absent (5-yr companion covers older window); Kingsport below 1-YR cutoff = county-substitute grain. [`worker_ladder_acs1yr_commute_v1.json`]
- Within-city wage arc: does not exist (OEWS strata enter as snapshot). [`wage_stratified_v1.json` / `worker_ladder_acs1yr_commute_v1.json`]
- CDC WONDER: 403/WAF this pass; the CHR analytic CSVs + NCHS Socrata are the banked keyless routes. [`health_outcome_lane_v1.json`]
- Raleigh pre-2016 incident series: no public keyless route; the open dataset starts 2020. [`raleigh_springs_site_v2.json`]

---

## APPEND — WORKING NOTES (build-time, this pass)

- **Built:** 2026-11-24, capstone pass. Every number in Sections 1–4 was read directly from its named source file this session (the elasticity cards re-read in full incl. D_CONVERTER_EXAMPLES and the verdict block; the gray lane incl. lit_magnitude and honest_nulls_and_flags; the worker-ladder incl. band_mean_join and the_reads; occupation_mix incl. headline_read and per-metro band compositions; joint_regression_v2 incl. between_reads and fe_within_regressions; the three BOB-19 output lanes incl. verdicts/laws; the peer-review scans record-by-record for Heller/READI/Sampson/Branas-2019/targeting; the youth inventory density metrics; the site files' lanes).
- **The founder-counts reconciliation:** parent task carried 188 (2025) and ~350 (2023 peak); the bank holds 184 and 344 (annual-window definitions differ). The brief carries BOTH, tagged, and shows the band barely moves (9–19 vs 9–18; 17–35 vs 17–34). No fabricated reconciliation; the difference is named.
- **The one honest line the brief refuses to write:** no dollar projection of the levers' yields. The only dollars quoted are published-source figures (Branas ROI class, OEWS wages, HCD committed funds) — each tagged to its file. The yard-crew law (zero fabricated dollars) is held verbatim at brief scope.
- **Ranking logic:** Lever-1 first because it is the only city-ownable lever with a 12-month falsifier window; Lever-2 second because its read steepens up the wage structure and its RCT rung (youth jobs) is the only randomized-proven violence lever; Lever-3 third because the flow card is an honest null and the stock card needs 3–4 sustained years.
- **The multiply-once law restated:** the stock effect is claimed once for the standing capacity, never compounded across future years (the AR1 honest-null means the machine itself refuses to extrapolate).
- **Sitting-open items:** the corridor-control selection for F1 (needs the vacancy/311 overlay run — a PolyScout lane), the clawback-template drafting for F3 anchors, and the annual re-pull calendar cadence for F4–F7.
