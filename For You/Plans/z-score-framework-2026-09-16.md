# The Z-Score Framework (Sept 16, 2026)

## Time
Sept 16, 2026 (evening, founder shower-thought level insight)

## Founder's insight (verbatim)
> "What we are doing is essentially a game of finding -z score
> left tail distributions"

## Status
**DRAFTED.** This is the mathematical framework under everything we've built.

## The mental model

Card prices for a specific grade follow a distribution (usually right-skewed):

```
Card market price distribution
         ▲
         │
    ████████  ← peak (median, mode)
   ██████████
  ████████████
 ──────────────  ← mean (μ)
███████████████
███████████████
        ▒▒▒
       ▒▒▒
      ▒▒▒  ← LEFT TAIL (deals — statistically rare)
     ▒▒
    ▒
──────────────────────────────────────►
z = -2   -1    0    +1    +2
```

**Every alert we send asks**: "is this listing in the -z tail?"

## Z-score thresholds

| z-score | Percentile | Meaning |
|---|---|---|
| z < -0.43 | Lower 1/3 | Founder's deal rule |
| z < -1.0 | Bottom 16% | Strong deal |
| z < -1.645 | Bottom 5% | Very strong (90% CI boundary) |
| z < -2.326 | Bottom 1% | Extreme outlier |

## Implications

### 1. The math is universal across verticals
- Cards, coins, watches, sneakers, vintage toys — all have price distributions
- Multi-vertical framework thesis validated mathematically
- Card Scout V1 → Coin Scout V2 → Watch Scout V3 all use the same model

### 2. CI bands become z-scores
- 90% CI = μ ± 1.645σ (catches central 90%)
- 70% CI = μ ± 1.04σ (catches central 70%)
- Lower-third line ≈ μ - 0.43σ

### 3. Noise filtering is outlier rejection
- "We are only as useful as we are accurate" = z-score threshold
- Outlier rejection is the philosophical answer, mathematically stated

### 4. Deal detector needs σ (not just low/high)
- pricing_bands today: σ = 0 (single price per grade)
- Stage 3 (Card Ladder): σ becomes computable from sold history
- Stage 3 unlocks proper deal detection

## Pricing tier feature gating (NEW INSIGHT)

| Tier | z-threshold | Signal quality |
|---|---|---|
| Casual ($15) | z < -0.43 | Lots of noise (lower third) |
| Standard ($30) | z < -1.0 | Filtered |
| Dealer ($75) | z < -1.645 | Curated (90% CI boundary) |
| Pro ($150) | z < -2.326 | Extreme outliers only |

**This is the quantified value stack the founder kept asking about.**

## Sales pitch (NEW FRAMING)

> "We find the bottom 5% of card prices, before everyone else.
> Every alert is a z-score below -1.645."

No competitor talks in z-scores. Mathematical rigor = differentiation.

## Multi-vertical scaling

| Vertical | σ behavior |
|---|---|
| Sports cards | Wide σ (liquidity varies by player/popularity) |
| TCG | Narrow σ (popular cards trade frequently) |
| Coins | Moderate σ (grade-dependent) |
| Watches | Wide σ (model/condition-dependent) |
| Sneakers | Moderate σ (release-driven) |

Same math framework, different distribution shapes per vertical.

## What unlocks proper z-score computation

| Data | Today | Stage 3 (Card Ladder) |
|---|---|---|
| Mean (μ) | ✅ Have | ✅ Have |
| Median | ✅ Have | ✅ Have |
| Std dev (σ) | ❌ Missing | ✅ Sold history gives σ |
| z-score | ❌ Undefined | ✅ Computable |
| CI bands | ❌ Q-bands only | ✅ Proper CI |

**Stage 3 = deal detector becomes mathematically rigorous.**

## ML features (future)

- z-score as primary deal signal
- Volume-weighted z-scores (more listings = higher confidence)
- Time-series z-scores (today's z vs 7-day z = acceleration)
- Cross-card z-scores (card-relative vs market-relative)

## Files to update (next iteration)

1. `scripts/deal_detector.py` — add z-score computation when σ available
2. `For You/Plans/pricing-decision-2026-09-16.md` — add z-score tier framing
3. Sales pitch deck — lead with z-score framing
4. Dashboard UI — show z-score alongside price

## Decisions captured

### CONFIRMED
- z-score is the underlying mathematical framework
- Stage 3 (Card Ladder) unlocks proper z-score computation
- Pricing tiers can be feature-gated by z-score threshold

### DEFERRED
- ML features (z-score acceleration, etc.) — Stage 4+
- z-score UI in dashboard — Stage 3+
- Sales pitch update — when z-score deal detection ships

## Memory note

This is the **mathematical thesis** under the business. Save this insight.
