# Card Hedger FMV as "Opinion, Not Fact" — Sept 18

## Jonathan's clarification (Sept 18)

> "CH FMV is an average or smoothing of data points. It is a cheat sheet as in
> they do the math for us. I would like to eventually derive our own FMV and
> for now we are going with ranges if that makes sense. Their FMV should be
> treated like an opinion rather than a stated fact."

## What this means

### Card Hedger FMV is **derived** (not raw)

Card Hedger takes:
- Recent sold listings
- Applies smoothing (winsorized median over 7-day window per their docs)
- Outputs a single number they call "FMV"

That single number is **one company's opinion** of what the card is worth.
Not a market consensus. Not a hard truth.

### We will eventually derive our own FMV

For now: **use Card Hedger's FMV as an opinion, not a fact.**
Display ranges instead of single numbers when possible.

### Practical implications

1. **Show ranges, not points** — instead of "PSA 10: $1,515", show
   "PSA 10: $1,200-$1,800 (CH A grade)". The range gives the customer
   more context than a single smoothed number.

2. **Card Hedger FMV is one input, not THE answer** — Cross-reference with:
   - SCPro median of active listings (live market signal)
   - SCPro sold comps (when working) (actual transaction prices)
   - Our own derived FMV (future) — winsorized median of all data sources

3. **De-emphasize CH confidence grade letter (A/B/C/D)** — it's Card Hedger's
   internal smoothing quality. We shouldn't treat it as gospel. Their D-grade
   cards might still have valid FMV if the underlying data is sound.

4. **Show the range, not the FMV** — this is the design change for the alerts.
   Current display: "PSA 10: $1,515 (CH A)".
   Future display: "PSA 10: $1,200-$1,800 range (CH opinion)".

### Future: derive our own FMV

When we have:
- Multiple sold comps from Card Hedger
- SCPro sold comps (when working)
- Direct eBay Browse API sold data

We can compute our own FMV using a transparent winsorized median or trimmed mean.
The formula would be in our code, not a vendor's. That gives us:
- Reproducible (anyone can verify the math)
- Open to inspection (we know what goes in and how it's smoothed)
- Adjustable (we can tune the smoothing window)

## Implementation (when ready)

### Now: ranges instead of points

Update `format_deal_alert` to show price_low - price_high range when available
(Card Hedger already returns these fields; we're just not displaying them).

### Soon: tag CH FMV as "opinion"

In Discord alerts, add a small disclaimer or tag indicating that the FMV
is a vendor's smoothed opinion, not a market consensus.

### Later: own FMV derivation

When we have sold comp data from multiple sources, write our own
`derive_fmv()` function in `scripts/`:

```python
def derive_fmv(sold_comps: list, smoothing_days: int = 7) -> dict:
    """Our own FMV from multiple data sources."""
    # 1. Filter to last N days
    # 2. Winsorize (drop top/bottom 5%)
    # 3. Compute median
    # 4. Return: { 'fmv': ..., 'low': ..., 'high': ..., 'sample_size': ... }
```

This becomes the canonical FMV. Card Hedger's becomes one of several inputs.

## Why this is the right call

- **Vendor lock-in risk** — if Card Hedger changes their formula or goes
  down, our alerts would either break or drift
- **Transparency** — customers want to know "how did you calculate this?"
- **Accuracy** — single-source FMV is opinion; multi-source FMV is consensus
- **Margin** — when we have our own FMV, we can offer it as a Pro feature

## Current alert format (Sept 18)

```
💎 Card Hedger per-grade FMV
  PSA 10: $1,515.00 (CH A)
  PSA 9: $177.33 (CH A)
  BGS 9.5: $425.00 (CH A)
  CGC 10: $537.79 (CH A)
```

**Future alert format (when ranges shipped)**

```
💎 Per-grade price range (Card Hedger opinion + our data)
  PSA 10: $1,400-$1,800 (CH: $1,515, n=12 sales, 7d window)
  PSA 9: $150-$220 (CH: $177, n=8 sales, 7d window)
  BGS 9.5: $380-$480 (CH: $425, n=4 sales, 30d window)
  CGC 10: $480-$620 (CH: $538, n=3 sales, 30d window)
```

This shows:
- The actual range (low-high from sales)
- CH's smoothed point estimate
- Sample size (how confident we should be)
- Time window (recent vs stale)

## Status: parking lot

Captured: Sept 18, 2026
Owner: Jonathan (you)
Related to: PSA-premium association model (also deferred until clean data)
Trigger: Sold comps available from multiple sources (CH + eBay Browse API + SCPro)

## Immediate action (small, do now)

Update the Discord alert to show price ranges where Card Hedger provides
price_low and price_high. This is already in our data — we just need to
display it.

```
PSA 10: $1,400-$1,800 (CH opinion, A grade)
```

Cost: ~30 min dev, 0 vendor cost.
