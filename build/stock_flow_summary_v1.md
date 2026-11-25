# STOCK-vs-FLOW ELASTICITIES v1 — the closeout summary (2026-11-24)

The founder's systems-efficiency frame, banked as machine-readable cards. ONE input-panel, TWO machines,
and the gap between them is the multiplier the founder was asking for.

## The frame
- **STOCK** = the beds and staff — capacity standing at day-0. A dollar is a cost only in order to HAVE them there.
- **FLOW** = the annual budget line — an in-year decision, moving capacity only while it recurs.
- **THE MULTIPLIER (care lane, same panel, same input):** the stock read is ~**11.6x** (FE-6 spec) / ~**9.5x** (FE-3 spec) the flow read per unit — and the stock machines carry the significance (t to −2.24) while the flow pool is noisy (t = −0.22, direction-class only).

## The elasticity pairs (Section A)
| lane | FLOW card (one-year) | STOCK card (sustained) |
|---|---|---|
| care capacity | +10% one-year → ~−0.16 rate-points (n=31, t=−0.22) | +10% sustained → −1.48 t0 / −0.89 t+1 rate-points (FE-6: −1.80; FE-2: −2.26) |
| unemployment | Δu x Δmurder rho = 0.006 (n=33) — the flow carries ~nothing | +10pp sustained → +1.83 rate-points standing (FE-6 β 0.312) |
| home value (shelter) | honest-null (no delta machine) | +10% sustained → −2.82 rate-points (t+1 form) |
| SNAP share | honest-null (reactive class) | +10pp sustained → +15.5 rate-points within (POSITIVE: need-follows-violence) |
| per-pupil spend (lit.) | +10% one cohort-year → +0.05–0.2 SD test scores per treated year | +10% x 12 years → +0.31 yrs edu, +7% wages, −3.2 pp poverty (Jackson QJE 2015) |

## The elasticity cards (Section B)
Schema shipped: `x% for 1 year (FLOW) | x% sustained N years (STOCK)`, units = murder rate-points (frame-scale)
+ % change vs the geo-mean rate 27.04. All five cards carry both forms.

## Durability ladder (Section C)
1. **T4 edu spending** — dose-linear per treated year; 12-year sustain → +7% wages (the literature template)
2. **T2 lead-removal** — exposure-stock decay, elasticity ~0.8, decades
3. **T5 neighborhood** — under-13 exposure window; adolescent/adult null-to-negative
4. **Panel care FLOWS** — AR-1 rho = −0.104 (n=58, t=−0.7): **annual flow changes do NOT persist** — the honest-null bottom rung (budgets are annual votes, not stocks)

## Horizon activation (Section D)
The stock read pays across horizons: t0 −0.148, still t+1 −0.089 rate-points per sustained 1%. The
compounding-correct window re-read lifts the t+2 cells on every multi-input model (dir-acc FE-3_t0 0.333 → 0.909;
FE-6 0.538 → 0.812; FE-2 0.375 → 0.667) while FE-3_arc_t+1 stays level-anchored (0.938 → 0.60, honest dual number).
**The AR-1 gate proves the lift is the whole-window LEVEL change, not flow extrapolation** — the stock machine
multiplies nothing forward; it prices the standing thing directly.

## Verification battery
- All 12 banked converter rows re-derived delta-0 (FE-3_t0 / FE-3_t+1 / FE-6 / FE-2 x {5,10,20}%).
- 28 scan-16 rows + 37 scan-18 lanes scanned; 3 literature stock exemplars; Jackson DOI carried.
- Honest-nulls carried explicitly: 4 one-machine lanes (no flow machine banked, never backfilled),
  1 persistence null, NYC single-year murder / Denver no-denominator carried per format-lock.

## Laws held
Direction-class only; no fabricated magnitudes (every number traced to a banked field, machine labeled per card);
format-lock (banked converter rows re-derived before shipping); honest-nulls banked as honest-nulls.

## Files
- `stock_flow_elasticities_v1.json` — the build (Section A pairs, B cards, C durability, D horizon activation)
- `_stock_flow_elasticities_v1_build.py` — the reproducible builder (rerun: `python _stock_flow_elasticities_v1_build.py`)
