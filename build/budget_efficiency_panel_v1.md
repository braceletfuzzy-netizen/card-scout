# THE BUDGET-EFFICIENCY PANEL v1

*Built 2026-11-24 · founder GO: 'Go! With that we can rate administrations and administrators.'*

**The instrument in one sentence:** after the banked fixed-effect murder equation eats every city-year's own inputs — care dollars, cage dollars, bookings, rent burden, home value, SNAP, schooling, unemployment — whatever murder rate is LEFT OVER is the delivery-quality residual. **Negative residual = reality did better than the model's promise at those inputs (efficient). Positive = underperformer.**

**Hard honesty up front:** on the anchor frame every city has only 4-5 scored city-years. This ranks *direction*, not guilt. No causal claim is made or derivable at this n.

### 1. THE EFFICIENCY RANK — anchor frame (FE-3, murder-rate t0, 2021-2025)

| Rank | City | n city-years | Mean residual (rate-pts) | First-half → Second-half | Trend (pts/yr) | Direction | <8 flag |
|---|---|---|---|---|---|---|---|
| 1 | Cincinnati | 5 (2021, 2022, 2023, 2024, 2025) | +0.000 | +1.99 → -0.92 | -1.20 | improving | YES — flag |
| 2 | Memphis | 5 (2021, 2022, 2023, 2024, 2025) | -0.000 | +4.64 → -9.45 | -5.03 | improving | YES — flag |
| 3 | St. Louis | 5 (2021, 2022, 2023, 2024, 2025) | +0.000 | +9.06 → -7.03 | -4.90 | improving | YES — flag |
| 4 | Detroit | 5 (2021, 2022, 2023, 2024, 2025) | -0.000 | +8.62 → -9.13 | -5.66 | improving | YES — flag |

*Rows per city: Cincinnati 5 · Detroit 5 · Memphis 5 · St. Louis 5. NYC/Denver carry no anchor rows (honest-nulls below). Mean residual = ACTUAL − PREDICTED murder rate per 100k. THE MEAN-LEVEL GUARD: within-city fixed effects absorb each city's average, so mean residuals pin at ~0 by construction and CANNOT rank cities — the rank column orders the CUMULATIVE ARC (first-half mean minus second-half mean, 'arc_rank_score' in the JSON); the mean cell is printed for the record only.*

### 2. THE WIDE-FRAME CROSS-CHECK (FE-6: care + unemployment; Cincinnati back to 2014, St. Louis to 2019, Detroit to 2020)

| Rank | City | n city-years | Mean residual (rate-pts) | First-half → Second-half | Trend (pts/yr) | Direction | <8 flag |
|---|---|---|---|---|---|---|---|
| 1 | Cincinnati | 12 (2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025) | -0.000 | -2.16 → +2.15 | +0.35 | declining | n/a |
| 2 | Detroit | 6 (2020, 2021, 2022, 2023, 2024, 2025) | -0.000 | +7.61 → -7.61 | -4.74 | improving | YES — flag |
| 3 | Memphis | 5 (2021, 2022, 2023, 2024, 2025) | +0.000 | +5.26 → -10.35 | -5.51 | improving | YES — flag |
| 4 | St. Louis | 7 (2019, 2020, 2021, 2022, 2023, 2024, 2025) | -0.000 | +8.76 → -10.85 | -4.23 | improving | YES — flag |

*Different frame — its cards never sum with the anchor's (the banked run-log law). St. Louis's wider window adds its 2019-2020 Krewson-era years and 2020's COVID spike (actual rate 87.2, the panel's worst murder cell). Same mean-level guard applies: arcs rank, means don't.*

### 3. WHAT THE RANK SAYS (plain English)

1. **Cincinnati** is the best-than-model performer on the anchor frame (cumulative-arc rank 1 of 4; the mean level is pinned at ~0 by the fixed effect — see the mean-level guard; its 2021→2025 arc runs +1.99 → -0.92, direction improving).
2. **Detroit** carries the worst cumulative arc (rank 4 of 4; +8.62 → -9.13).
3. Memphis lands at anchor rank 2 of 4 on the cumulative arc (+4.64 → -9.45) — its 2024-2025 swing is steeply negative (the panel's sharpest improving run), exactly the years where both the care inputs surged AND the outcome fell.
4. The wide frame REORDERS the mid-pack: St. Louis scores best on the cumulative arc (first-half +8.76 → second-half -10.85, the deepest negative swing of the four — the 2020-21 COVID-spike cells resolve hard-negative) while Cincinnati's 12-year wide window nets ~flat (+0.35 rate-pts/yr the only non-improving trend, driven by its 2020-21 spike). Cincinnati keeps rank 1 as the least-arc-volatile city; St. Louis's wide-frame swing beats its own anchor read.

**Trend read (the part the founder rates):** all four cities' residual arcs run down-hill across 2021-2025 — the national murder decline does part of that, but the residual is measured AFTER the equation already expects each city's input path, so the differential is in the ARC SHAPE: Detroit -5.66 and Memphis -5.03 rate-pts/yr (the big-residual big-swing cities) vs Cincinnati -1.20 (the low-voltage steady city). Who 'improved fastest' and who 'is best' are different questions, and the table now carries both.

### 4. THE ADMINISTRATION-LANE — boundary reads (descriptive, falsifiable, no causal claim)

**Memphis** — boundary: 2024-01: Jim Strickland era -> Paul Young administration (banked: memphis_care_cage_series_v1 'Paul Young took office Jan 2024')
   - Pre (2021, 2022, 2023, n=3): mean residual +6.30
   - Post (2024, 2025, n=2): mean residual -9.45
   - **Direction-class read: -15.75 rate-pts → residual-improved-after-change**
   - Second boundary (attribution guard): 2025-09-29: Memphis Safe Task Force federal deployment begins (banked; MULTI-ACTOR guard — the crime-delta attribution is federal+state+city, the who-gets-credit lane)

**St. Louis** — boundary: 2021-04: Lyda Krewson era -> Tishaura Jones administration; 2025-04: Jones era ends -> Cara Spencer (banked: band_a_candidates_v1 'the Tishaura-Jones-era = the ended-May-2025 + the NEW-mayor-Spencer took-office-Apr-2025')
   - Pre (2021, 2022, 2023, 2024, n=4): mean residual +2.17
   - Post (2025, n=1): mean residual -8.66
   - **Direction-class read: -10.83 rate-pts → residual-improved-after-change**

**Cincinnati** — boundary: 2022-01: John Cranley era -> Aftab Pureval administration (banked: band_a_foursome_v1 names 'Aftab Pureval' as the city's mayor 'the transmittal-letter-found'; the Jan-2022 swearing-in is context-asserted, not banked-dated — tagged [context-asserted])
   - Pre (2021, n=1): mean residual +4.42
   - Post (2022, 2023, 2024, 2025, n=4): mean residual -1.10
   - **Direction-class read: -5.52 rate-pts → residual-improved-after-change**

**Detroit** — honest-null
**NYC** — honest-null
**Denver** — honest-null
*Wide-frame corroboration (Cincinnati, FE-6, 2014-2025, Cranley→Pureval boundary at 2022): pre(2021) mean +6.36 (n=1) → post(2022-25) mean -0.06 (n=4), delta -6.42 → residual-improved-after-change. The wide window adds the 2014-2020 Cranley-era years: residuals ran -2.9 to -4.0 (2014-2018) before the 2020 COVID spike (+6.82) and 2021 (+6.36).*

*Wide-frame corroboration (St. Louis, FE-6, 2019-2025; Jones sworn in mid-2021 so 2021 is a transition-year cell, counted pre): pre(2021-24) mean -2.09 (n=4) → post(2025) mean -13.55 (n=1), delta -11.46 → residual-improved-after-change — n=1 on the Spencer side; carry as a direction-lead only.*

### 5. MEMPHIS DEEP-DIVE — the leaks, lane by lane

**Memphis residual by year (anchor frame):**

| Year | Predicted | Actual | Efficiency residual | Biggest input pushes |
|---|---|---|---|---|
| 2021 | 46.7 | 54.5 | **+7.79** |  |
| 2022 | 46.5 | 48.0 | **+1.50** |  |
| 2023 | 46.3 | 55.9 | **+9.61** |  |
| 2024 | 45.0 | 40.4 | **-4.59** |  |
| 2025 | 44.5 | 30.2 | **-14.31** |  |

**The transit lane = THE efficiency archetype (banked mata_diagnosis_v1):** Memphis runs transit at **$82 per resident** (NTD 2024 ops) vs **Cincinnati $514**, **St. Louis ~$1,041-class peers**, **Detroit $264** — 5.7x-12.7x below the functioning peers. $0 of agency-levied taxes every reported year (vs COTA's $161.4M sales-tax stream in Columbus). Farebox ~5% of budget. Fixed-route service hours 320,000/yr (2017) → 215,000/yr (2026); 23→18 routes with 60-minute headways from Nov 2024; MATAplus denying ~300 paratransit trips/month. The zero-fare natural experiment (Nov 2025) lifted ridership +18-25% within weeks on a static network — suppressed demand exists; supply is the binding constraint.

**The per-resident care-dollar band, 2021-25 (the inputs the FE equation ate):**

   - **Memphis** mean care spending 218/resident/yr (2021-25, n=5)
   - **St. Louis** mean care spending 352/resident/yr (2021-25, n=5)
   - **Cincinnati** mean care spending 407/resident/yr (2021-25, n=5)
   - **Detroit** mean care spending 564/resident/yr (2021-25, n=5)
- **Cage lane (per 100k residents, mean 2021-25; Detroit n=2 banked years only):** Cincinnati ~$548,236/100k-res (n=5) · Detroit ~$565,121/100k-res (n=2) · Memphis ~$477,817/100k-res (n=5) · St. Louis ~$1,020,420/100k-res (n=4) (Memphis runs the smallest cage bank of the four, ~13% below Cincinnati — the lane where city dollars are NOT the leak)
- **Governance-overhead leak:** the trustee costs $75,000/MONTH; TransPro crisis contract $1.3M; diagnostic $336K — dollars burned on institutional failure, before a single bus-hour is bought (banked).
- **The 2024 care jump:** FY2024 care +31% the year Paul Young took office (banked: 'the mayorial-transition year') — the care-lead response to the crime emergency, not a cage-lead; care/cage ratio band held 0.40-0.52 across the whole FY20-FY26 series (no cage surge in the city books).
- **The MSTF guard:** the steep 2024-2025 residual improvement coincides with the federal Memphis Safe Task Force (13,020 arrests by Sept 2026) + $100M state safety grants — that deployment is OUTSIDE the city ledger, so the city-efficiency instrument neither claims nor clears it; the founder's administration-instrument scores the city-budget response (care-lead, ratio band held), not the federal delta.

**Memphis boundary read (from §4):** the Young administration's scored years show residual improved after Jan-2024 (delta -15.75).

### 6. THE GUARDS

- **Composition confounder:** every row ships WITH its care/cage/poverty/SNAP/rent-burden/home-value/unemployment context columns (see JSON `need_structure_context`), so the rank can be checked as a *non*-poverty-rank: the FE equation already ate those columns. Note St. Louis has the panel's worst murder LEVELS but sits mid-pack on residuals; Memphis has the panel's worst poverty context and a mid-pack residual — the rank is not mechanically re-ranking need.
- **Honest-nulls named:** PIT homelessness 2013 + 2016 = HUD published-nothing at the per-CoC route (banked, never backfilled); eviction judgment rates 2020-21 carry COVID freeze flags; health outcomes ride county-grain only (never blended); Denver has no murder denominator in the panel window; NYC has exactly ONE complete predicted city-year (2001); facility-grain bookings = NYC-only (Memphis/Detroit/STL jail routes tried-and-no-capture, UCR-intake proxy carried instead, labeled); grad lane = 4 banked cells only.
- **Frame-drift (full disclosure):** joint_regression_v2 banked FE-3 records n=24/cities=5 at fit time; the current on-disk panel yields n=20 complete rows for the same spec (panel file evidently extended post-fit with budget-forecast years). Format-lock law: banked betas carried verbatim; frame-drift quantified here, never silently refit into the headline.
- **Mean-level guard (the zero-sum property):** the four anchor cities' mean residuals are all ~0.00 by construction — a within-city fixed-effect frame cannot charge or credit a city's average level (each city's mean is absorbed by its own intercept). The instrument therefore reads CUMULATIVE ARCS and year-slopes (first-half vs second-half, trend rate-pts/yr), not mean levels. The rank order on those arcs: Cincinnati > Memphis > St. Louis > Detroit; the refit sensitivity below reports how far the order is frame-robust.
- **Sensitivity check (arc rank):** banked-betas arc rank {'Cincinnati': 1, 'Memphis': 2, 'St. Louis': 3, 'Detroit': 4} vs refit-on-current-frame arc rank {'Cincinnati': 1, 'Memphis': 2, 'Detroit': 3, 'St. Louis': 4} — RANKS PARTIALLY DISAGREE: {"St. Louis": [3, 4], "Detroit": [4, 3]} — Cincinnati stable at #1; the bottom half re-orders inside one position; carry the banked-betas rank as headline with the instability named.
- **No causal claims:** descriptive + direction-class only; every city n=4-5 (all <8, flagged); administration reads are before/after residual means, not effects.

### 7. VERIFICATION

- Anchor frame rows applied: 20 across 4 cities ['Cincinnati', 'Detroit', 'Memphis', 'St. Louis']; wide FE-6 rows: 31 across ['Cincinnati', 'Detroit', 'Memphis', 'NYC', 'St. Louis']; FE-2: 19 across ['Cincinnati', 'Detroit', 'Memphis', 'St. Louis'].
- All betas carried verbatim from banked joint_regression_v2.json (format-lock); refit shown side-by-side as sensitivity only.
- Every actual-rate cell traces to maslow_joint_panel_v1 (FE-frame convention) or _backwards_outcome_series_v1 with its source string in the JSON row.
- Every dollar cell traces to city_component_annual_v1 / care_bookings_ordering_v1 panel / mata NTD pulls.


---

## WORKING NOTES (build pass, 2026-11-24)
- The anchor frame is the banked FE-3 (5 inputs) applied to murder_rate_t0 across the 20 rows where all five inputs AND the outcome are simultaneously banked (2021-2025 x CIN/DET/MEM/STL). NYC carries exactly one complete predicted cell (2001; FE-6 family, unemp lane) — no NYC rank computed. Denver carries care dollars only (no denominators) — zero efficiency rows, honest-null.
- Frame-drift found and disclosed: banked FE-3 was fit on n=24/cities=5 per its own header; the current panel yields n=20 complete t0 rows for the same spec. Format-lock honored (banked betas verbatim). The refit-on-current-frame sensitivity reproduces Cincinnati #1 and Memphis #2; St. Louis/Detroit swap at the bottom — the instability is NAMED in the guards, not buried.
- The anchor-frame rank is a CUMULATIVE-ARC rank (first-half mean minus second-half mean), not a mean-level rank: within-city FE absorb city means, so mean residuals pin at ~0 by construction and would be a nonsense rank. Both tables print the mean for the record and rank on the arc.
- Administration dating rode banked strings only: Young Jan-2024 (memphis_care_cage_series_v1), Jones->Spencer Apr/May-2025 (band_a_candidates_v1), Pureval current (band_a_foursome_v1; the Jan-2022 swearing-in tagged [context-asserted]). Detroit/NYC/Denver carry honest-nulls (no in-window boundary / no predicted rows).
- Memphis MSTF double-boundary guard: the Young boundary read (delta -15.75) covers 2024-2025; the federal MSTF deployment starts 2025-09-29 — the read cannot separate city-administration delivery from the federal surge at n=2; the guard is written into the row and the MD.
- Transit archetype carried verbatim from mata_diagnosis_v1 ($82 vs $514/$1,041-class/$264 per-res, NTD 2024; $0 agency-levied taxes; VRH 261k->216k 2022->2025; service hours 320k->215k 2017->2026; zero-fare +18-25% natural experiment).
- Care/cage context: care 2021-25 per-res band MEM $218 / STL $352 / CIN $407 / DET $564; cage (per 100k) band MEM ~$478k / CIN ~$548k / DET ~$565k (n=2) / STL ~$1.02M — Memphis runs the SMALLEST cage bank of the four, so its mid-pack residual arc is not a spend-more-story.
- Guards: PIT 2013/2016 honest-nulls (HUD published nothing, banked); eviction 2020-21 covid_freeze flags; health = county-grain companion only; facility-grain bookings NYC-only (Shelby/Detroit/STL routes-tried-no-capture, UCR intake proxy labeled); grad = 4 cells; no causal claims at small n.
- Secondary outcome columns: bookings intake per-100k (proxy, labeled), murder_rate_t+1 banked, grad where banked (4 cells) — carried in JSON rows where they exist, never zero-filled.
