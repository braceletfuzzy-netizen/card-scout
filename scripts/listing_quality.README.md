# listing_quality.py — V2 Grade-Tiered Listing Filter

## Status
**V2 — implemented but not user-facing.** Filter is wired into `discord_alert_bot_v3.py`
but the bot doesn't currently use eBay active listings (sportscardspro provides
the primary signal). Filter will activate when bot is re-wired to use eBay
active listings, OR when Jim wants V2 quality filtering on sportscardspro data.

## What it does

Scores each eBay listing 0-100 quality. Below threshold = drop from alert.
Above = include as deal candidate.

Heuristics:
- **+positive signals**: watchers ≥ 3, sold_count ≥ 5, reasonable price
- **-negative signals**: bulk lots, suspiciously low price ($1 BIN), zero watchers

## Thin market handling

If `card.market_thin == True`:
- Filter is **skipped entirely** (every listing is signal)
- All listings pass with score 100

Per spec: *"a thin-market card with $1 BIN is still a real signal even if it's 'junk' because there's no other data."*

## Score thresholds

| Score | Action |
|---|---|
| 100 | Always alert (thin market) |
| 80-99 | High confidence deal |
| 60-79 | Default threshold — include |
| 40-59 | Low quality — drop |
| 0-39 | Junk — drop |

Default threshold: 60.

## Inputs available from eBay actor

- `price_usd` (raw price)
- `listing_type`: 'sold' | 'active'
- `watchers_count` (people watching)
- `sold_count` (prior sales)
- `title` (raw text)

## Inputs NOT available (would need actor update)

- `timeLeft` (for auction ending soon)
- `shipping cost`
- BIN vs auction distinction

These are the V3 spec items per `For You/Plans/v2-grade-tiered-listing-filter-2026-09-14.md`.

## Self-test

Run `python scripts/listing_quality.py` to see the 5 test cases (real deal, junk BIN, bulk lot, PSA 10, thin market).

## Integration

In `discord_alert_bot_v3.py` (line ~620), after `filter_matching_items()`:

```python
from listing_quality import filter_listings_by_quality
quality_result = filter_listings_by_quality(
    matching,
    grade_tier=card.alert_type or 'raw',
    thin_market=bool(getattr(card, 'market_thin', 0)),
)
matching = quality_result['kept']
```

If filter fails for any reason, bot continues with all listings (graceful degradation).

## Why V2 not V1

Per spec: *"V1 ticker ships a working 'deal detection' today (sometimes with junk in it). Better filtering is a quality-of-life upgrade, not core feature. Don't ship complexity without proving core value first."*

Built now so it's ready when Jim asks for cleaner deal signals.
