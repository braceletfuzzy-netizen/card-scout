# OUTPUT VECTOR V2 — THE ALL-FOUR-COLUMNS VERDICT SHEET

**Built:** 2026-11-25 · **Parent:** deleg_58fa077b (hit its iteration cap mid-build; this pass finalizes) · **Siblings:** _econ_fit_v1.json, _housing_schools_fit_v1.json, _infra_lane_v1.json (accuracy-patched rerun), _acfr/*, output_vector_v2.json

**Laws held throughout:** zero-fabricated (every number traces to the banked file named with it) · honest-nulls carry routes · walk-forward-before-call (a gate-failing family registers NOTHING) · direction-class at small n · the [A] economy gate-shut stands unless ITS refit is run.

---

## THE FIVE FAMILY-VERDICTS, ONE LINE EACH

| # | Family | Verdict | The one thing to remember |
|---|--------|---------|---------------------------|
| 1 | **CRIME** | **FIT — the anchor** | t+1 arc direction 0.938 (reproduces exactly), LOCO arc mean 0.812; carries the ONE live registered call (Louisville 2026 DOWN, cron 790da3db5eeb untouched) |
| 2 | **ECONOMY** | **GATE-SHUT** | walk-forward t+1 0.50 = coin, LOCO 0.56, care$ beta 0.0; no instrument is real; nothing registered |
| 3 | **HOUSING + SCHOOLS** | **GATE-SHUT (both lanes, this pass's refits)** | rent-burden WF 0.533 below gate; grad lane WF 0.600 = AT the gate, not above it; nothing registers |
| 4 | **FISCAL** | **EXTRACT (no fit)** | CAFR/book line-grain banked STL/NYC/DET/MEM; the MATA subsidy spike caught at line grain = the archetype test; Cincy/Denver JS-walled = v2 |
| 5 | **INFRASTRUCTURE** | **NULL + DESCRIPTIVE** | SDWA output-fit honest-null (route banked); NBI 2025 bridges = real cross-section variance, no fit per law; 311 lane banked |

---

## 1. CRIME = FIT (THE ANCHOR)

What exists: a within-city-FE prediction instrument on the Maslow joint panel whose t+1-arc
direction read survives its own blindfolds.

- **Drift-check first:** banked fixed betas + current on-disk files reproduce the banked
  **0.938 (FE-3_arc_tplus1 lag-1, n=16) EXACTLY** — the number is live from current files, not stale.
  (Pooling all lags 1-3 gives 0.694 across the 2021-25 decline arc — a harder test, carried alongside.)
- **LOCO (leave-one-city-out, refit betas):** per-city lag-1 direction
  Cincinnati 0.75 / Detroit 1.00 / Memphis 0.75 / St. Louis 0.75 — **arc-class mean 0.812**. GATE-OPEN.
- **Residual-stick: STICKS (WEAK)** — pooled lag-1 r 0.459 > 0.3 threshold; arcs carry the signal,
  single next-year reads do not (founder-literal 2022->2023: 1/4 sign-holds).
- **Composition: HOLD, BOUNDED** — the founder-carrying signs (care−, snap+, FE-6 pair) never flip
  across 17 drop-refits; the flips that exist are home/cage/bookings and they are non-headline columns.
- **Power-curve: DEEPEN** — kink near n=150, flat by 250; between-city share 53-87% is absorbed by
  city FE; expand in the t+1 arc class (47% within-share).
- **Panel churn: 0.832 carry** — 116/663 window city-years are drop events; survivorship is
  publication-class, not outcome-selection.

**The one registered call (lives here, nowhere else):**

- **Louisville KY, 2026: DOWN** vs its own 2021-25 mean rate **30.69** per-100k.
- Registered 2026-11-25T07:20:00-06:00 with a falsifier: **falsified iff the 2026 rate finishes
  at-or-above 30.69** (LMPD full-year 2026 count via the keyless FBI CDE summarizer or the LMPD
  year-end report; non-reporting-class recurrence = void, not scored).
- Magnitude full-read (−32.5 rate-pts) explicitly VOIDED as out-of-support (Louisville's inputs sit
  18-21 SD off the 5-city panel frame); the DIRECTION agrees across the out-of-support full read and
  the in-support channel read (2025 already 36% below own mean).
- Cron: `civic_call_recheck_v1.py`, the 10am class (**790da3db5eeb — untouched this pass**).

Sources: `pre_expansion_gauntlet_v1.json` (six_verdicts_summary, step1_holdout_test),
`joint_regression_v2.json` (the_output_vector), `pre_registered_civic_call_v1.json`.

---

## 2. ECONOMY = GATE-SHUT (the honest refusal)

What was attempted: the banked Maslow ACS strata (bachelors %, poverty %, SNAP share) -> LAUS annual
unemployment rate 1990-2025 (FRED, keyless), within-city FE, LOCO + walk-forward t+1.

- **Walk-forward t+1 pooled direction: 0.500 (n=10) = coin.**
  Per-city: Cincinnati 0.0 / Detroit 1.0 / Memphis 1.0 / NYC 0.0 / St. Louis 0.5.
- **LOCO direction mean: 0.56** (Cincinnati 0.2 / Detroit 0.4 / Memphis 0.8 / NYC 0.6 / St. Louis 0.8).
- **The care$ channel does not price:** adding care_per_100k (fit B) moves within-R2 0.175 -> 0.292
  but the care beta lands at **−0.0** — the channel the founder's model leans on is not carrying this output.
- **THE VERDICT: GATE-SHUT. No call, no registration, no cron.** The instrument is NOT real yet.
  The gate-shut stands **unless ITS refit is run**: more years deep-first via the ACS 2021-2024 .dat
  route already banked (`_edu_raw/acs1y_b*.dat` lanes). A coin instrument is never force-registered.

**The aliased-pull defect (caught + hardened into law):** the first 6-city LAUS pull came back with
all six series IDENTICAL — an aliasing defect, caught in-session before any fit ran, refetched
per-city with an **identity gate** (asserted distinct 2010/2023/2025 values per city: 2010 = 9.7/9.5/
15.7/9.9/8.7/11.3). Cross-check vs the banked panel unemployment column: **7/7 within 1.0pt**.
The identity gate is now a standing law for any multi-series pull.

**Honest-nulls (with routes):**
- BFS city/county applications: `api.census.gov/data/timeseries/econ/bfs` requires a key →
  STATE-grain series banked (FRED BABATOTALNSA*, 2004-2026); no city-year fit attempted per grain law.
- BEA county GDP: BEA API requires a key → state annual NGSP banked (FRED {ST}NGSP, 1997-2025).

Sources: `_econ_fit_v1.json`, `_econ_pulls_v1.json` (+ its `_validation` block).

---

## 3. HOUSING + SCHOOLS = GATE-SHUT (this pass's refits — the unstarted family, now started and gate-checked)

Both output lanes fitted per the laws (within-city FE, direction-class, walk-forward t+1, LOCO),
gated at **strictly > 0.6** walk-forward direction. **Both failed. Nothing registers.**

### [B1] Panel inputs -> B25070 severe rent-burden (rent_burden_50pct_plus_share)

- Frame: 5 cities × 2021-25 (Cincinnati, Detroit, Memphis, NYC, St. Louis), n=25; outcome from the
  banked ACS B25070 lanes (10-city 2024 cross-check on disk in `_b25070_pct.json`).
- Fit t0 (within-city demeaned ridge): betas poverty +0.545 / bachelors −0.200 / snap −0.174;
  within-R2 0.255.
- **Walk-forward t+1 pooled direction: 0.533 (n=15) — BELOW the gate.**
  Per-city: Cincinnati 0.333 / Detroit 0.333 / Memphis 0.667 / NYC 0.333 / St. Louis 1.0.
- LOCO mean 0.68 (0.8/0.6/0.6/0.8/0.6) — within-sample descriptive only; **LOCO does not open a gate
  the temporal test shut.**

### [B2] Panel inputs -> grad lane (B15003 HS+ share, state grain joined city-year)

- Frame: n=20 joint city-year rows (Cincinnati/Detroit/Memphis/NYC/St. Louis × 2021-24 where the
  panel carries inputs); outcome = the banked B15003 state-share rows
  (`edu_outputvector_v1.json city_year_joint_rows`; HS+ = sum L17..L25, categories mutually
  exclusive — the banked first-pass mistake stays fixed).
- **Grain-honest note (law): the outcome is STATE grain (ACS B15003 state share) joined to
  city-year rows — a state-share-informed read, NOT a city graduation rate.** Labeled as such in the JSON.
- Fit t0: betas poverty +0.014 / bachelors −0.047 / snap −0.076; within-R2 0.398.
- **Walk-forward t+1 pooled direction: 0.600 (n=10) — EXACTLY AT the gate, and the gate is strict
  (> 0.6). At-the-gate = not a pass.** Per-city: Cincinnati 1.0 / Detroit 1.0 / Memphis 0.0 /
  NYC 1.0 / St. Louis 0.0 — city-heterogeneous coin, which is what 0.6 at n=10 is.
- LOCO mean 0.80 (1.0/1.0/0.5/0.75/0.75) — descriptive, same reasoning as B1.

**Law note:** walk-forward-before-call holds verbatim — both B lanes are at/below coin-level at
this n. No call, no cron, no pre-registration was created. Deepening route for v3: ACS .dat
year-expansion (the same deep-first route the economy refit would use — the .dat pipeline is
already proven in `_edu_raw`).

**Descriptive companion (no fit):** NAEP main-NAEP state scale lanes banked
(`edu_outputvector_v1.json`, 192 rows, g4/g8 math+reading, 2013-2024, param contract learned from
API 400 error text); g8-math × state-HS-share rho 0.173 (n=48) carried as descriptive.

Sources: `_housing_schools_fit_v1.json` (written this pass), `edu_outputvector_v1.json`,
`maslow_joint_panel_v1.jsonl`, `_b25070_pct.json`.

---

## 4. FISCAL = EXTRACT (no fit — extraction without a city-year panel does not fit; fit is v2/v3)

Line-grain CAFR/budget-book extracts banked per city. The extraction test the family had to pass —
catch an agency-level pattern at line grain that the summary grain hides — **passed, in Memphis.**

- **St. Louis** (`_acfr/stlouis_fy2025_extract_v1.json`, FY2025 signed final, 290pp):
  General Fund unassigned balance **$443.9M** (+$26.9M/5.4% this yr, −$24.1M/4.9% prior);
  Police Retirement System funded-ratio series (recent-first) **79.45 / 70.97 / 69.4** (+ERS and
  Firemen's series banked alongside).
- **NYC** (`_acfr/nyc_fy25_extract_v1.json`): General Fund unassigned **−$7.61B NEGATIVE**
  (prior year −$6.16B) from the FS Unassigned row; gross debt outstanding **$121.031B** =
  **$12,134/capita 2025** (10-yr arc 514 in 2016 → 12,134 in 2025); government-wide total net
  position **−$195.02B deficit**.
- **Detroit** (`_acfr/detroit_fy22_extract_v1.json`, FY22 ACFR; FY24 = the v2 task):
  GF balance **$1.04B** (+$182M yoy), unassigned surplus **$229.6M** (+$50.5M);
  GRS/PFRS Component I & II funded-ratio series banked at component grain (p155-158).
- **Memphis** (`_acfr/memphis_fiscal_pattern_v1.json` + `memphis_books_scan_v1.json`) — **the
  archetype catch:** the MATA city subsidy read at line grain runs
  **$22.99M (FY15) → $23.42M (16) → $25.92M (17) → $14.65M (18) → $6.7M (22) → $7.79M (23) →
  $30.67M (FY24-25)** — a quiet collapse-and-spike invisible at the summary grain. Honest-null:
  FY19-21 books absent from disk (never backfilled); memphistn.gov direct = 403 (urllib AND curl).
- **Cincinnati / Denver: HONEST-NULL (JS-walled budget portals)** = v2 route task; raws landing on
  disk (`_board2b/` cincy FY22-27 pdf set) but nothing invented.
- **Fit status:** no city-year fiscal panel assembled ⇒ no fit attempted ⇒
  walk-forward-before-call trivially holds.

---

## 5. INFRASTRUCTURE = NULL (SDWA fit) + DESCRIPTIVE (bridges) + BANKED (311)

### 5a. EPA SDWA municipal water systems — HONEST-NULL on the output-fit

Six municipal PWS systems pulled live (keyless EPA Envirofacts, Nov-25): Cincinnati OH3102612,
Denver CO0116001, Detroit MI0001800, Memphis TN0000450 (MLGW), New York NY7003493,
St. Louis MO6010715.

- Violation totals in the file window: **Cincinnati 0 / Detroit 1 / Memphis 1 / NYC 10 /
  St. Louis 18 / Denver 128**.
- Denver's 128 = **ALL "MR" monitoring/reporting class** (rule codes 320/122/340), not health-based.
- **Exactly ONE health-based-ind violation across all six systems:** NYC 2017, TT
  treatment-technique, contaminant 0800.
- **Read:** near-zero signal at the municipal grain — no city-year panel can be fit at this size ⇒
  the SDWA output-fit ships as an honest-null. **Route banked:**
  `data.epa.gov/efservice/Violation/PWSID/{pwsid}/JSON` (re-runnable).

### 5b. FHWA NBI 2025 bridges — DESCRIPTIVE CROSS-SECTION, no fit per law

City lat/lon-box counts (BL05/BL06 in bounds), 2025 JSON per state (keyless FHWA route):

| City | Bridges in box | Poor | Poor share |
|------|---------------|------|-----------|
| New York | 1200 | 113 | **9.4%** |
| Memphis | 535 | 44 | **8.2%** |
| St. Louis | 280 | 23 | **8.2%** |
| Detroit | 379 | 28 | **7.4%** |
| Denver | 618 | 36 | **5.8%** |
| **Cincinnati** | 308 | 7 | **2.3% (best)** |

**Real variance across cities (0.023-0.094) at one cross-section (n=6) — fit NOT attempted**
(direction-class needs a city-year panel). The 2020-2024 NBI archives exist at
`fhwa.dot.gov/bridge/nbi/ascii.cfm` — banked as the v2/v3 arc route. Grain caveat banked: city-box
counts mix owner agencies inside the boxes (e.g. NYSDOT 84000-class codes in NYC).

*Accuracy note (patched this pass):* the v1 `sdwa_read` phrasing said "four of six systems carry
0-1 violations" while the same file's own counts read five-of-six < 20 (St. Louis 18); the rerun
corrects the phrasing to match the data exactly. The substance (thin signal ⇒ honest-null) is unchanged.

### 5c. 311 service calls (the backlog signal) — LANE BANKED

Banked gray-safety panel (97 city-years, 6 cities); paired care$ rows n=37; within-city
Spearman care$ → calls-per-1k: **Cincinnati 0.636 (n=12) / Detroit 0.257 (n=6) / Memphis 0.771
(n=6) / NYC 0.829 (n=6) / St. Louis 0.821 (n=7)**. Explanatory read only (n tiny per city); the
lane is direction-fit-ready at n=97 when the input side is deepened (only 18 of 97 call-years have
care$ banked — honest-null on the fit for now).

---

## THE REGISTERED-CALL LEDGER (everything that exists, and the nulls)

| Instrument | Status | Where |
|-----------|--------|-------|
| Louisville 2026 DOWN (crime) | **REGISTERED** — timestamped, falsifiable, cron live | `pre_registered_civic_call_v1.json`, cron 790da3db5eeb |
| Economy -> LAUS unemployment | **GATE-SHUT — registers NOTHING** | `_econ_fit_v1.json` |
| Rent-burden (B1) | **GATE-SHUT — registers NOTHING** | `_housing_schools_fit_v1.json` |
| Grad lane (B2) | **GATE-SHUT — registers NOTHING** (WF 0.600 = at, not above) | `_housing_schools_fit_v1.json` |
| Fiscal panel fit | not attempted (no city-year panel) | — |
| SDWA fit | honest-null, route banked | `_infra_lane_v1.json` |
| Bridges fit | not attempted (cross-section only), archive route banked | `_infra_lane_v1.json` |

**No cron jobs were touched in this pass** (Louisville watcher 790da3db5eeb untouched).

---

## FILES WRITTEN THIS PASS

- `build/_housing_schools_fit_v1.json` — the [B] fits (family B verdicts)
- `build/build_v2_housing_schools.py` — re-runnable [B] fit script
- `build/_infra_lane_v1.json` — accuracy-patched infrastructure lane rerun
- `build/build_v2_infra.py` — accuracy-patched (`sdwa_read` now matches its own counts)
- `build/build_v2_economy.py` — accuracy-patched (dead-code defect removed); `_econ_fit_v1.json` unchanged
- `build/assemble_output_vector_v2.py` + `build/output_vector_v2.json` + this file
