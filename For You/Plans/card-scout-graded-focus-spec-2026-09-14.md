# Card Scout — Grading Economics Spec (UPDATED)

> **⚠️  SUPERSEDED — Sept 14, 2026**
>
> This spec was written by Cosmo earlier in the day. The product has since been re-framed as a **Bloomberg-style Ticker** (no profit calc, no grading recommendations, no probability math).
>
> **Current master spec**: `card-scout-ticker-system-spec-2026-09-14.md` (279 lines)
>
> **Status of the items below**: OUT OF SCOPE for V1. The 4 open questions about PSA grading cost, BGS/CGC priority, etc. are NO LONGER BLOCKING because the V1 ticker doesn't need them.
>
> This doc is kept for historical reference only — do not implement from it. See the ticker spec for the current product vision.

---

# Card Scout — Grading Economics Spec (UPDATED)

> **⚠️  SUPERSEDED — Sept 14, 2026**
>
> This spec was written by Cosmo earlier in the day. The product has since been re-framed as a **Bloomberg-style Ticker** (no profit calc, no grading recommendations, no probability math).
>
> **Current master spec**: `card-scout-ticker-system-spec-2026-09-14.md` (279 lines)
>
> **Status of the items below**: OUT OF SCOPE for V1. The 4 open questions about PSA grading cost, BGS/CGC priority, etc. are NO LONGER BLOCKING because the V1 ticker doesn't need them.
>
> This doc is kept for historical reference only — do not implement from it. See the ticker spec for the current product vision.

---

# Card Scout — Grading Economics Spec (UPDATED)

## Source Documents

1. **Fuzzy's Google Docs** (Sept 14, 2026) — Card Grading Authority Pricing
   - Grading tier math (PSA 1-10 + half-points)
   - Authority pricing (PSA/BGS/CGC)
   - Hidden costs (shipping, supplies, value upcharges)
   - Economy of scale (1 / 10 / 25 cards)
   - Selling service options (consignment vs DIY)

2. **Fuzzy's design principle**: Graded cards = primary, raw = secondary context

## The Key Insight From The Doc

**Raw card pricing is fuzzy. Graded card pricing is precise.**

A raw $20 Bo Jackson could be a future $200 PSA 9 OR a $20 PSA 2 with a crease. **The grade reveals the truth.**

So when we say "deal at $20 raw" we mean one of:
- 30% chance of PSA 9 ($200) → expected $60
- 70% chance of PSA 4 or worse ($30) → expected $21
- **Net expected: ~$32** vs $20 listing = $12 "expected value deal"

But grading costs $20+ and takes 15-100 days. **Risk-adjusted return matters.**

## Updated Deal-Finder Math

For each raw card listed below market average:

```
Expected Profit = (
  (Prob_grade_9 × Market_PSA9)
  + (Prob_grade_10 × Market_PSA10)
  + (Prob_grade_8 × Market_PSA8)
  + (Prob_lower × Market_floor)
) - Grading_Cost - Listing_Price
```

For each graded card listed below market average for its grade:

```
Clean Profit = Market_Avg_for_Grade - Listing_Price
```

## Customer-Facing Output

### For Buyers (Clean Profit)

```
🎯 Grade 9 Bo Jackson — Found 3 below market
Grade 9 avg: $120 | Clean profit on top 3:
  $80  → +$40 (33% off)
  $85  → +$35 (29% off)
  $90  → +$30 (25% off)
```

### For Dealers (Raw → Grade Spread)

```
🎯 Raw Bo Jackson RC — Potential grading play
Listed: $20 | Raw avg: $20 | After-grading scenarios:
  PSA 9 (40% prob):  $200 - $20 grading = **$160 profit**
  PSA 8 (30% prob):  $80  - $20 grading = **$40 profit**
  PSA 6 (20% prob):  $30  - $20 grading = **-$10 loss**
  PSA 4 (10% prob):  $15  - $20 grading = **-$25 loss**

  Expected value: **$61 profit per card**
  Bulk play (25 cards): ~$475 grading × 25 = $11,875 / $1,525 = 7.8x ROI
```

### For Investors (Top Tier Only)

```
🎯 PSA 10 Bo Jackson RC — Found 1 below market
PSA 10 avg: $550 | Listed:
  $400 → +$150 (27% off, expected to flip in <30 days)
```

## Authority Pricing In The Math

| Use Case | Cheapest Authority | Why |
|---|---|---|
| 1 card | CGC ($48-58) | Flat $20 economy tier, no membership |
| 10 cards | BGS ($19.55/card) | Reopens $14.95 base at 10+ cards |
| 25 cards | BGS ($17.45/card) | Same + amortization |

**Best path for typical Card Scout user (1-10 cards)**: CGC economy.

## What's Harder Than It Looks

### 1. Probability Estimation
We don't know the prob distribution for raw cards. We'd need:
- Historical data on similar cards
- Or accept that we're estimating with rough numbers

**Workaround**: Show a range. "30-50% PSA 9, 50-70% PSA 8 or lower."

### 2. Grading Delay
PSA Standard = 90-100 days. CGC = 15 days. This affects "spread urgency."

### 3. Hidden Costs
- Outbound shipping $5-10
- Return shipping $15-25
- Memberships ($149 PSA)
- Upcharges for high-value cards

**Workaround**: Include shipping in the grading cost constant per authority.

## What Hugo Needs To Build

### 1. Grade Detection From Title
- Regex: `PSA\s*10`, `PSA\s*9`, `BGS\s*9\.5`, etc.
- Bucket listings into: `grade_10`, `grade_9`, `grade_8`, `grade_lower`, `raw`

### 2. Per-Grade Average (For Graded Listings)
- Already have Sportscardspro URLs
- Pull grade-specific averages from there
- Filter eBay listings to that grade bucket
- Compute avg per bucket

### 3. Raw Probability Model (For Raw Listings)
- Default probability table per card era
- Manual override in form (customer estimates)
- Show range, not single number

### 4. Grading Cost Configuration
- Customer picks default authority (PSA/BGS/CGC)
- System shows net profit using that cost
- Customer can switch to see other options

## Out Of Scope

- Live grade prediction from card images (would need ML model)
- Cross-card arbitrage (lot buying opportunities)
- Real-time grading backlog estimates
- Authority-specific UI (each authority is just a cost config)

## Open Questions

1. **Default authority per customer?** Or per signup? Or auto-detect?
2. **Show expected value as a range?** Or single number?
3. **Include consignment fees in flip math?** (5-20% on sell side)
4. **How to handle grading risk?** (ignore? show range? require probability input?)

## Implementation Estimate (Hugo)

- Grade detection regex: ~30 min
- Per-grade average from Sportscardspro: ~1 hr
- Output formatter with raw + graded sections: ~2 hrs
- Grading cost config in DB + UI: ~1 hr
- Expected value math: ~1 hr
- Testing + edge cases: ~1 hr
- **Total: ~6.5 hrs**

## Roles Recap

**Cosmo**: spec docs, customer flow, DB queries, light config, bug discovery + handoff docs

**Hugo**: actor code, parser updates, grade detection logic, output formatter, all heavy lifting

## Status

- ✅ This spec captures grading economics
- ✅ Roles defined
- ⏳ Hugo to implement
- ⏳ Fuzzy to answer 4 open questions when ready
