# ticker_formatter.py

**Purpose**: Formats the per-grade market ticker output for Discord embeds per the ticker spec (Bloomberg-style).

## What it does

Three formatters:

1. `format_per_grade_ticker(grade_table)` — renders the **Per-Grade Market Values** block
2. `format_below_market_deals(items, grade_table)` — finds listings priced **below typical range for their grade**
3. **NEW (Sept 15, ADR-001):** `get_30day_average()` + `format_trend_indicator()` — adds "vs 30d avg" trend comparison per grade tier

## Output 1: Per-Grade Market Values

```python
from ticker_formatter import format_per_grade_ticker

ticker_text = format_per_grade_ticker(grade_table)
# Returns string ready for Discord embed field
```

### Example Output

```
PSA 10 / BGS 10: $107.50  (typical $93.37–$116.63) (5 sold/30d)
PSA 9.5 / BGS 9.5: $25.00 (6 sold/30d)
PSA 9: $18.36  (typical $16.67–$21.33) (12 sold/30d)
PSA 8: $13.18 (8 sold/30d)
PSA 7: $12.75
Raw (Ungraded): $1.50  (typical $0.25–$3.74) (30 sold/30d)
```

When range data is available (≥2 sales), shows the 90% CI. When only point price is known, shows just the price.

## Output 2: Below-Market Deals

```python
from ticker_formatter import format_below_market_deals

result = format_below_market_deals(items, grade_table, max_items=5)
# Returns:
# {
#   'deals': [
#     {title, url, price_usd, grade_label, tier, typical_low, typical_high, discount_pct},
#     ...
#   ],
#   'total_found': N
# }
# OR None if no below-market items found
```

### Discount Rule

A listing is flagged "below market" when:
- Its price < `typical_low` for its detected grade tier
- E.g., a PSA 10 listing at $50 when typical PSA 10 range is $93-$117 → flagged

### Example Output

```
3 below-market deals found:
$0.5 raw | typical $2.00-$2.00 | 75% off
$50.0 PSA 10.0 | typical $93.37-$116.63 | 46% off
$5.0 PSA 7.0 | typical $8.92-$16.57 | 44% off
```

## Used By

`discord_alert_bot_v3.py → format_deal_alert()` calls both to render:
- "📊 Per-Grade Market Values (ticker)" Discord embed field
- "🎯 Below-Market Deals" Discord embed field

## Self-Test

```bash
python ticker_formatter.py
```

## Design Decisions

- **Show, don't recommend**. Per the ticker spec, we don't say "buy this!" or calculate profit. We just show the market data and highlight anomalies.
- **No dollar amounts in deal descriptions**. We show percentage off + a price comparison link, not "you'd save $X" — that's profit math.
- **Sort deals by discount %**. Biggest discount first, so the most compelling anomalies surface.
- **Max 5 deals shown**. Keeps Discord embed readable.

## Limitations

- Tier detection depends on `grade_detector.py` regex. Unusual title formats may be misclassified.
- "Below market" comparison uses 90% CI low, which can be conservative for grades with little sales data. May miss some deals or flag false positives for high-volatility grades.
