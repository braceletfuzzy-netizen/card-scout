# THE PREDICTION-MACHINE v1 — RUN-LOG (BOARD-A, the what-if calculator)
*BUILT 2026-11-24 · the founder-approved build · the color-blind-law held (machine-picked label colors; every label carries text + value; color = redundancy only)*

## THE DELIVERABLE
`prediction_machine_v1.html` — self-contained (no CDN, no network), dark-theme, 4 tabs:

| Tab | The what-if lane | The models multiply |
|---|---|---|
| 1 | THE MASLOW JOINT — 5 input sliders (care / cost-burden / home-value / SNAP / bachelor's+) → the 4-card output vector (crime · grad · NAEP · employment) | FE-3 t0 (n=24, R² 0.695) + FE-3_arc_tplus1 (n=18, R² 0.748), banked betas verbatim |
| 2 | THE FLOOR + THE CAGE — care × unemp line (FE-6, n=36) + care × cage × bookings (FE-2, n=19) + the OEWS floor snapshot | FE-6 care −0.304 / unemp +0.312; FE-2 care −0.452 / cage +0.419 / bookings +0.013 |
| 3 | THE BETWEEN-CITY T-HEAD — the 10-metro OEWS-2025 strata snapshot + the rank-rho ladder + the ceiling-band/flight block | Spearman n=8: p10 −0.452 · median −0.667 · p90 −0.857 · p90/p10 −0.714 · mean −0.81 |
| 4 | THE SOURCES — every model, its banked file, frame, grain, and the carried read | — |

## THE SLIDERS → OUTPUT-VECTOR CONTRACT
- Each slider = deviation in WITHIN-CITY STANDARDIZED UNITS (±3 SD, step 0.1). The machine computes murder-delta = (Σ βᵢ·Δzᵢ) × within-SD(outcome) and prints: the delta value, ▲/▼/— arrow, the baseline (banked panel row, city + year labeled), and a plain-English readout sentence.
- Baselines = the latest FE-frame row per city from `maslow_joint_panel_v1.jsonl`: Cincinnati 2025 (21.9), Detroit 2025 (25.4), Memphis 2025 (30.2), NYC 2024 (4.2), St. Louis 2025 (50.7) — each labeled with its year on the card.
- Color-blind-law legend on every tab: CARE green #7ee787 · CAGE red #ff7b72 · HOUSING purple #d2a8ff · FOOD/SNAP gold #e3b341 · FLOOR blue #79c0ff · EDU orange #f0883e · UNEMP cyan #3fbcd6 — every swatch paired with the name AND the beta, never color-alone.

## THE VERIFICATION (verify-before-build, all re-derived at build time)
- **FE-3 t0 re-run from the 24-row frame: β = −0.181 / −0.280 / −0.099 / +0.640 / −0.003, within-R² 0.695 — EXACT match to banked.**
- **FE-3 arc t+1: −0.197 / +0.056 / −0.263 / +0.544 / −0.189, R² 0.748 — EXACT.**
- **FE-6: −0.304 / +0.312, R² 0.263 — EXACT. FE-2: −0.452 / +0.419 / +0.013, R² 0.423 — EXACT.**
- **Edu rhos: pooled Spearman NAEP-g8-math × HS+ = 0.172, × BA+ = 0.373 (n=48) — EXACT re-derivation.**
- **T-head: the −0.452/−0.667/−0.857/−0.714 are SPEARMAN (verified by re-run); the FE betas are OLS-on-z — the two grains are labeled separately per law 3.**
- Node runtime-audit: syntax-check OK; DOM-stub init + slider exercise OK (t0 care+1SD → −1.31 murder; snap+1SD → +4.62; FE-6 unemp+1SD → +2.36; FE-2 cage+1SD → +2.92 — all exactly β×SD). ID-audit: all 42 element references resolve.

## THE WITHIN-CITY SD CONVERSIONS (the slider scales, computed from the frames)
- FE-3 t0 SDs: care $13.74M/100k · burden 1.50pp · home $25,263 · snap 1.81pp · bach 0.88pp · murder 7.22 rate-pts/SD
- FE-3 t+1 murder SD 9.78 · FE-6: care $16.76M · unemp 1.84pp · murder 7.62 · FE-2: care $10.90M · cage $15.29M · bookings 799.8/1k · murder 6.97

## THE LAWS HELD
1. Direction-class only — the machine multiplies banked betas and shows the model's answer; the readout sentences say "the banked model reads", never "causes". No causal claim anywhere.
2. Honest-null — NYC unemp-2024 absent from FE-6 frame (labeled in the baseline card); OKC/Pittsburgh murder unjoined in the T-head (honest-null in the table, excluded from rhos); St. Louis unemp-2025 unjoined; no wage-floor within-city arc (snapshot lane labeled "2025 only").
3. Within-city vs between-city grain separation — tabs 1–2 carry within-city standardized models; tab 3 is the BETWEEN-city head, tagged as such.
4. Color-blind law — label-colors machine-picked per the house convention; name + value always printed.

## THE FILES
- `prediction_machine_v1.html` — the tool (37.8 KB, self-contained)
- `_pm_data_slice_v1.json`, `_pm_model_spec_v1.json` — the verified banked slices the tool was generated from (build-time artifacts, kept for re-audit)
- `_pm_math_test.js`, `_pm_drive.js` — the verification scripts (node run, exit-0)

## THE KNOWN-LIMITS (honest, printed on the board)
- The NAEP and GRAD gauges are lane-carried direction-class translations (via the banked +0.373/+0.172 rank rhos) — there is no banked causal model from the Maslow sliders to the edu outputs.
- The employment gauge on tab 1 hands off to FE-6/tab 2 (the pooled +0.104 is a rank read, n=33 diff-pairs carry 0.006 — the weakest lane, Grogger clause).
- FE-6 and FE-2 are different frames — their output cards never sum.
- Chrome debug-permission wall blocked the in-browser screenshot pass (founder-clicks-permission-walls law); verification ran through node syntax + DOM-stub + math-asserts instead.


---

# THE ELASTICITY-REFRAME ADDENDUM (v1.1, built 2026-11-24 · the founder's correction: CHANGES not levels)

## THE DELIVERABLE
`elasticities_v1.json` + `prediction_machine_v1.html` v1.1 (new tab 3: "x% → y% THE ELASTICITY CONVERTER"; sources moved to tab 4).

## THE THREE LAWS, SHIPPED
1. **THE DELTA-ELASTICITY** — dln(murder) ~ dln(care) within-city, contiguous-year pairs only, n=31 (Cin 11 / STL 6 / Det 5 / Mem 5 / NYC 4): raw b = **−1.55 rate-pts per +100% care** (i.e. −0.016 per +1%), t = −0.22, within-R² 0.003 — NOISY, direction-class only. Per-city Δρ: Cin −0.72 · STL +0.54 · Det −0.20 · Mem −0.30 · NYC −0.40. AR-1 care persistence: ρ = **−0.104** (n=58, t −0.7): year-to-year care changes do NOT persist — budgets are annual votes, not stocks. The compounding-correct machine multiplies the WHOLE window's Δln-care ONCE, never extrapolates.
2. **THE COMPOUNDING-CORRECT RE-READ** — cumulative Δln-care over each scored window, n=145 of the 258 pairs (lags ≤3; t+4/t+5 thin cells left in the banked bank): t+2 direction cells LIFT — FE-3_t0 dir 0.333 → **0.909** (n=11) · FE-2 0.375 → **0.667** (n=12) · FE-6 0.538 → **0.812** (n=16) — while FE-3_arc_tplus1 stays level-anchored (0.938 → 0.60). Compounding vs persistence_decay variants score IDENTICALLY on sign (positive coefficient sums; the AR-1 −0.10 sign flips no direction read at these horizons — honest). Founder-literal carries: NYC 1990→92 care +15.1% read murder-DOWN, actual fell — t+2 hit.
3. **THE CONVERTER** — every banked standardized beta now carries percent-space rows (Δmurder = β·SD_y-pool / SD_x-within × 0.01·mean_x-pool; % of the 27.7 geo-mean rate): FE-6 care −0.180 rate-pts/1% · FE-2 −0.226 · FE-3_t0 −0.148 · FE-3_arc −0.089; unemp +0.183 · cage +0.294 · snap +1.549 (t0 level-form) etc. The HTML tab takes typed x% and prints all four models' y rows.

## THE VERIFICATION
- All four converter rows re-derived to exact match from the banked frames (listwise-complete listwise construction identical to build_backwards_test_v1/joint_regression_v2).
- Node DOM-stub re-run: SCRIPT-OK / drawConv-OK / draw0+draw6+draw0b-OK / MATH-ASSERT-OK (−0.2264 exact). CAUGHT-AND-FIXED: the converter's first draft redeclared `fmt` (collision with the page's existing `const fmt`) — renamed `efmt`; the stub harness caught it before ship.
- Chrome debug-permission wall again blocked the in-browser pass (the v1 wall, unchanged) — node syntax + DOM-stub + math-asserts path per the established fallback.

## THE FILES
- `elasticities_v1.json` — A (Δln regressions) + A1 (per-city Δρ) + B (beta→percent converter table) + C (compounding-correct re-read, 145 pair rows) + D (worked examples) + verdict.
- `_elasticity_reframe_v1.py` — the build script (re-runnable, exit-0).
- `prediction_machine_v1.html` — v1.1, 5 tabs, self-contained.
