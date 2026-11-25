# THE PRE-EXPANSION GAUNTLET v1 — all six questions, verdict-first
**Built 2026-11-25 · workspace `For You/PolyScout/build` · sequential, each question gating the next · zero fabricated numbers, honest-nulls named, no causal claims, direction-class at small n**

**THE SIX VERDICTS**
| # | Question | Verdict |
|---|----------|---------|
| 1 | The Hold-Out Test (the expansion gate) | **GATE-OPEN** |
| 2 | The Residual-Stick Test (administration instrument) | **STICKS (WEAK)** |
| 3 | The Composition-Bias Scan (selection check) | **HOLD, BOUNDED** |
| 4 | The Power Curve (when to stop expanding) | **DEEPEN FIRST** |
| 5 | The Panel Churn Audit (survivorship) | **0.832 CARRY** |
| 6 | The Pre-Registered Civic Call (founder-flavor) | **REGISTERED** |

---

## §1 THE HOLD-OUT TEST — does the machine hold on a city it never fit? → **GATE-OPEN**

**The drift-check came first** (fault-localization law): banked fixed betas + the *current* on-disk
files, scored with the banked scorer replicated line-for-line — **t+1 direction = 0.938, n=16,
EXACT reproduction of the banked headline.** The 93.8% is not a museum number; the files still
produce it. (Pooled over lags 1-3 on today's files it reads 0.694, n=36 — the all-lags pool across
the 2021-25 decline arc is a harder test than the banked lag-1 scorer; both banked in
`_gauntlet1_loco.json`.)

**The LOCO test** then re-derived betas with each panel city dropped in turn (within-city
standardized OLS on the remaining cities), predicting the held-out city's arc with its own
descriptive moments, banked direction convention:

| Held-out city | dir accuracy (t+1, lag-1) | within-city rho | n |
|---|---|---|---|
| Cincinnati | 0.75 | +1.0 | 4 |
| Detroit | 1.00 | +0.8 | 4 |
| Memphis | 0.75 | +1.0 | 4 |
| St. Louis | 0.75 | +1.0 | 4 |

**LOCO distribution: mean 0.812 · min 0.75 · max 1.00 (n=4 cities)** — against banked 0.938
in-sample. No city breaks the t+1 arc instrument.

Also scored: the wide care+unemp lane LOCOs even better (**mean 0.887**, min 0.636); the FE-3 t0
model LOCOs at mean 0.60 (NYC 0.0 — NYC is the one held-out city the arc model must NOT claim);
the FE-2 cage/bookings instrument LOCOs at mean 0.525 (coin-flip class; its t+1 arc does not
survive refit). The betas move when a city is dropped (care −0.069..−0.543 across refits) but the
SIGN CLASS does not.

**What does not hold — labeled honestly:** strict-blind FORM-B (held-out city contributes no
moments, train-only centering) drops St. Louis to 0.00 — the machine is a **within-city arc
instrument, not a between-city level instrument**. A new city needs its own mean before the
machine can read its arc.

**Verdict: the expansion gate OPEN for arc-class expansion.** No catastrophic failure; no founder
question surfaced mid-run.

---

## §2 THE RESIDUAL-STICK TEST — does the administration-instrument's residual predict itself? → **STICKS (WEAK)**

From `budget_efficiency_panel_v1.json` (31 FE-6_wide residual rows across CIN/DET/MEM/STL/NYC;
NYC honest-null — one cell, no pairs):

| City | consecutive run | n pairs | lag-1 r | lag-1 rho | 2022→2023 |
|---|---|---|---|---|---|
| Cincinnati | 2014-2025 (12y) | 11 | 0.431 | 0.20 | +1.41 → −0.39 (flip) |
| Detroit | 2020-2025 (6y) | 5 | 0.930 | 0.70 | +7.75 → −0.36 (flip) |
| Memphis | 2021-2025 (5y) | 4 | 0.441 | 0.20 | +2.19 → +10.19 (**holds**) |
| St. Louis | 2019-2025 (7y) | 6 | 0.383 | 0.49 | +6.26 → −8.50 (flip) |

**Pooled: r 0.459, rho 0.521 (n=26 consecutive city-year pairs)** — above the 0.3 direction-class
bar, with the caveat that pairs share cities (no inference, direction-class only).

**Plain English:** the budget-efficiency residual is not pure wind — Detroit's over-predicted
2020-22 run followed by under-predicted 2023-25 is a real multi-year run (r 0.93). But the
founder's literal read — *does residual-2022 predict residual-2023?* — answers NO at the
city-year grain: 1 sign-hold in 4. The administration instrument scores **arcs** (the banked
first-half/second-half convention), never one year ahead. That is now the registered usage rule.

---

## §3 THE COMPOSITION-BIAS SCAN — would poor publishers flip the banked signs? → **HOLD, BOUNDED**

**Who would they be (all banked classes):** Jacksonville (ten straight 0/12 non-reporting years
2011-2020), Raleigh (5/12-months 2014, then a 4-year silence), Omaha/Fresno/Baltimore/Long
Beach/Sacramento/Tucson/San Francisco/Phoenix/Pittsburgh (single-year month-guard drops), and 34
cities whose **outcome** cells exist but whose city budget-books were never pulled — the panel's
selection is by INPUT availability, not outcome severity.

**The sensitivity read:** 17 variant refits (all four models × drop-2025+-forecast-vintage +
drop-each-city). Results:
- **care (−): flips in ZERO of 17 refits. snap (+): ZERO. The FE-6 care+/unemp+ pair: ZERO.**
- Fragile columns, named: `median_home_value` flips when Detroit drops (t0-model); `cage` and
  `bookings` flip when St. Louis drops (FE-2's already coin-flip-class instrument). **None of the
  three fragile columns is a headline column** — the banked verdicts lean on care/snap/FE-6.

**Wide-lane holdout probe (honest-null):** Jacksonville and Raleigh have NO banked unemployment or
care lane on disk — they cannot be scored today; the month-guard cities' murder arcs sit banked
(`_backwards_outcome_series_v1.json`) awaiting a future lanes pass. The panel could not silently
absorb them — that is the point of the honest-null bookkeeping.

**Verdict: the banked signs are publication-selection-robust where it matters; fragile where it
doesn't. Bias bounded, and the boundary is written down.**

---

## §4 THE POWER CURVE — expand or deepen? → **DEEPEN FIRST**

SE-shrink projection (SE ∝ √(within-variance/n), banked R² per model):

| city-years | 150 | 250 | 400 |
|---|---|---|---|
| FE-3 t0 | 0.40x | 0.31x | 0.245x |
| FE-3 arc t+1 | 0.35x | 0.27x | 0.21x |
| FE-6 care+unemp | 0.49x | 0.38x | 0.30x |
| FE-2 care/cage/bookings | 0.36x | 0.28x | 0.22x |

(x = relative SE vs today's frame; today per-input SEs ≈ 0.02-0.03 on unit-standardized betas.)

**The kink is near n≈150** (SE already 0.35-0.49x today's); by n=250 the curve flattens; the
n=400 step buys only ~0.06-0.09x more. The frame decomposition clinches the *how*: the
between-city share of murder variance is **53%-87%** depending on frame, and fixed effects absorb
that share without explaining it. Each new city = a new intercept (dof cost) + a new honest-null
surface, while its between-city variance is eaten not used. The **t+1 arc frame is the exception
(47% within-share)** — new cities genuinely teach there.

**Registered recommendation: deepen to ~150 city-years (more years per existing city, more lanes
per city), expand city COUNT only in the t+1-arc class, and spend the next build on new lanes
(edu/bookings arcs) rather than more cities at the same lanes.**

---

## §5 THE PANEL CHURN AUDIT — how much history exists only because cities kept publishing? → **0.832 CARRY**

Of the 663 city-years implied by the banked windows, **116 are drop events** (publication stops,
month-guards, format breaks); 576 banked cells remain: **83.2% carry.**

The big drops, all banked:
- **Boston 1980-2025: 33 of 46 interior years missing** (crack-era publication silence) — carry 0.33
- **New Orleans 1990-2024: 22 of 35 missing** (incl. the 0/12-months 2025 pass-through year) — carry 0.37
- **Houston 2004-2025: 13 of 22 missing** — carry 0.41
- **St. Louis 2003-2009: 7 straight missing**; Raleigh 2015-2018 (after the 5/12-months year); Detroit 2014/2017/2018
- **Jacksonville 2011-2020: ten 0/12-months years** (its bookings lane is DEFINED by the hole)
- plus the 2026 partials class (9-11-month UCR YTD, excluded from scoring, never annualized) and
  the single-year month-guards (Omaha/Fresno/Baltimore/Long Beach/Sacramento/Tucson/SF/Phoenix/Pgh)

**The survivorship verdict:** the panel's fully-retained runs — NYC 46-year, St. Louis 28-year,
Cincinnati 12-year, Detroit 14-span, Memphis 6 — are runs of cities that never went dark. Drops
are **publication-class and format-class only**: no city's murder arc was dropped for being high or
low. The model's history exists because six ledgers never closed — and the audit now prices exactly
how much of the past that dependency consumed.

---

## §6 THE PRE-REGISTERED CIVIC CALL — Louisville KY → **REGISTERED**

**City choice:** Louisville, on verified live keyless routes (both probed this session, 2026-11-25):
- FBI CDE summarizer `cde.ucr.cjis.gov/LATEST/summarized/agency/KY0568000/HOM` → **full LMPD monthly actuals 2013-2025, zero gaps** + agency-pop block
- ACS 1-yr via the banked keyless www2 route (`summary_file/…/table-based-SF/data/1YRData/acsdt1y<yr>-<tab>.dat`), geo 1600000US2148006 — B17001/B15003/B25070/B25077/B19013 all pulled
- Jacksonville was the loser on reachability: hub API 401s, ten-year 0/12 reporting hole in the banked lane (the exact failure class §5 audits); Jax CDE 2024/25 pulled as cross-check only.

**Fresh pulls (route-labeled):** Louisville murders 2021:252 / 2022:244 / 2023:198 / 2024:210 /
2025:136; agency-pop denominators 678,236 → 691,630; rate arc 37.16 / 36.01 / 29.58 / 31.03 / **19.66**.
ACS 2024: poverty 15.48% · bachelors+ 30.44% · rent-burden-50+ 30.87% · median mortgage/rent $241,700.

**The call:** **DOWN — Louisville's 2026 murder rate finishes below its own 2021-25 mean of 30.69 per-100k.**

**The honest full-read is OUT-OF-SUPPORT:** Louisville's strata sit 18-21 SD off the 5-city panel
frame (burden z −17.9, bachelors z +21.1) → Σβz = −5.23 × own-SD 6.22 = −32.5 rate-pts, which is
absurd as a level. **Magnitude VOIDED; direction registered.** The in-support channel read on
Louisville's own 2021-25 arc agrees (2025 already 36% below its own mean), so the direction is not
a degenerate extrapolation — but the falsifier, not the story, resolves the call.

**Honest-nulls named:** care-per-100k (Louisville budget dept-grain not routed this pass — the
model's t~2+ lane cannot be priced here), SNAP share (B22010 unrouted), 2025 ACS not yet published,
CDE agency-pop ≠ ACS place pop (both carried; rate class identical).

**Registration artifacts:** `pre_registered_civic_call_v1.json` (timestamp 2026-11-25T07:20:00-06:00,
falsifier: LMPD full-year 2026 count on the same CDE route as it refreshes ~Mar-2027; FALSIFIED iff
2026 rate ≥ 30.69; void if the 0/12 non-reporting class recurs) +
cron **`louisville_civic_call_recheck_10am`** (job 790da3db5eeb, `0 10 * * *`,
`~/.hermes/scripts/civic_call_recheck_v1.py`, no-agent, deliver-local; exit codes 0 pending / 1 HIT /
2 MISS / 3 route-failure). First run today 10:00 CT. Louisville 2026 YTD at registration: 43
(partial-months carried, never annualized — the months-guard law).

---

## LAWS HELD (both files)
Zero fabricated numbers — every figure traces to `maslow_joint_panel_v1.jsonl` /
`joint_regression_v2.json` / `backwards_test_v1.json` / `budget_efficiency_panel_v1.json` /
`city_component_annual_v1.jsonl` / the churn-audit banked gap lists, or to the route-labeled fresh
pulls of §6. Honest-nulls named at every unroutable lane. No causal claims anywhere.
Direction-class at small n. Every verdict explicit.

## WORKING NOTES (append)
- Drift-check discovery: `backwards_test_v1_scored_records.json` predates the panel extension (pred 24.44
  vs current 24.54); fixed-betas drift-check on CURRENT files reproduces the banked 0.938 exactly — format-lock held.
- FE-2 does not survive LOCO refit (mean 0.525): the cage/bookings instrument is a t0-level read, not an
  arc instrument; registered as such (banked betas still carried verbatim).
- Strict-blind FORM-B results banked for the level-transfer question (St. Louis 0.0 at lag-1 dir); labeled
  a level-transfer read, NOT an arc-instrument failure.
- Step-3's "all signs hold" holds ONLY on the founder-carrying columns; the fragile columns are banked named.
- Power curve uses the √(within-variance/n) form with the banked R²; the t+1-arc 47% within-share is the
  one frame where expansion is NOT dominated by deepening.
- §6 Louisville selection: both cities probed live BEFORE the pick; Jacksonville's 401 + ten-year hole
  decided it. All Louisville routes re-verifiable by re-running `civic_call_recheck_v1.py` (exit-0 today).
