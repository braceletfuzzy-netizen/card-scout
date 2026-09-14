# grade_range_calculator.py

**Purpose**: Builds the per-grade market value table from sportscardspro actor output, with statistical 90% confidence intervals.

## What it does

Given a sportscardspro actor response, builds a row per grade tier (PSA 10, 9.5, 9, 8, 7, Raw) with:
- Current typical price
- 30-day price delta
- 90% confidence interval (mean ± 1.645 × SD)
- Volume / frequency of sales
- 30-day sold count

## API

```python
from grade_range_calculator import (
    compute_range,
    build_per_grade_table,
    TIER_KEY_MAP,
    TIER_TO_BOT_BUCKET,
)

# Statistical range calculation
range_data = compute_range([100, 110, 90, 95, 105], z_score=1.645)
# {'count': 5, 'mean': 100, 'sd': 7.9, 'low': 87.0, 'high': 113.0, 'ci_pct': 90.0}

# Per-grade table from sportscardspro
table = build_per_grade_table(sc_data)
# Returns 6 rows: psa_10, psa_9.5, psa_9, psa_8, psa_7, ungraded
```

## Input Schema (sportscardspro actor output)

```python
{
    "prices_by_tier": {
        "ungraded": {"price_usd": 1.50, "delta_30d_usd": 0, "volume": "1 sale per day"},
        "psa_7":    {"price_usd": 12.75, ...},
        "psa_8":    {"price_usd": 13.18, ...},
        "psa_9":    {"price_usd": 18.36, ...},
        "psa_9_5":  {"price_usd": 25.0, ...},
        "psa_10":   {"price_usd": 107.50, ...},
    },
    "sold_counts_by_grade": {
        "ungraded": 30, "psa_10": 30, ...
    },
    "sales": [
        {"title": "...", "price_usd": 2.75, "date": "2026-09-13"},
        ...
    ]
}
```

## Output Schema (per-grade row)

```python
{
    'tier_key': 'psa_10',
    'tier': 'psa_10',           # bot bucket
    'grade': 10.0,
    'label': 'PSA 10 / BGS 10',
    'price': 107.50,
    'delta_30d_usd': 1.99,
    'volume': '1 sale per week',
    'sold_count_30d': 30,
    'range': {
        'count': 2,            # number of sales used for SD
        'mean': 105.0,
        'sd': 7.07,
        'low': 93.37,          # 90% CI low
        'high': 116.63,        # 90% CI high
        'ci_pct': 90.0,
    }
}
```

## Math

**90% Confidence Interval** (one-tailed): `mean ± 1.645 × SD`

For grades with **enough sales** (≥2 in the dataset):
- Use real mean and SD from sportscardspro's sales list
- Lower bound: `max(0, mean - 1.645 × SD)`
- Upper bound: `mean + 1.645 × SD`

For grades **without enough sales data**:
- Use heuristic ±30% range around the published price
- This is conservative (covers wider variability)

## Tier Mapping (sportscardspro keys → bot buckets)

| sportscardspro key | Bot bucket | Numeric grade | Display label |
|---|---|---|---|
| `ungraded` | `raw` | None | Raw (Ungraded) |
| `psa_7` | `psa_lower` | 7.0 | PSA 7 |
| `psa_8` | `psa_8` | 8.0 | PSA 8 |
| `psa_9` | `psa_9` | 9.0 | PSA 9 |
| `psa_9_5` | `psa_9` | 9.5 | PSA 9.5 / BGS 9.5 |
| `psa_10` | `psa_10` | 10.0 | PSA 10 / BGS 10 |

## Self-Test

```bash
python grade_range_calculator.py
```

## Known Limitations

- Only 6 grades covered (PSA 10/9.5/9/8/7 + Raw). No PSA 6, 5, 4 etc. — those grades have minimal eBay data.
- Sportscardspro returns a single price per grade, not a timeseries. SD is computed only when individual sales are available.
- For cards with <2 individual sales of a specific grade, we use the heuristic ±30% range.

## Gotcha: Schema Mismatch (Cost Me 2 Hours)

When I first built the per-grade ticker (commit `6b1d454`), I assumed the sportscardspro actor returned:
- `prices[]` list (WRONG — actual key is `prices_by_tier`)
- `sold_counts[]` list (WRONG — actual key is `sold_counts_by_grade`)

The actual schema is **dicts**, not lists. See "Input Schema" above. **If you're debugging "all grades show —", check that the keys match.**

## CRITICAL: `_raw_data` Stashing

`sportscardspro_lookup.extract_sold_summary()` returns a small dict with only the top-level fields (`psa_10_price`, `psa_10_volume`, etc.). It does NOT include `prices_by_tier`, `sold_counts_by_grade`, or `sales`.

**The bot must stash the raw actor response so the ticker formatter has full data:**

```python
sc_data = lookup_sportscardspro(url, max_sales=10, max_wait_sec=60)
sold_data = extract_sold_summary(sc_data)
sold_data['_raw_data'] = sc_data  # ← THIS LINE IS REQUIRED
format_deal_alert(..., sold_data=sold_data)
```

If you skip `_raw_data`, the ticker section will show "—" for all grades. No errors — just empty output. (This happened to me on first test.)

---

## Used By

- `ticker_formatter.py` → consumes the table for Discord embed rendering
- `discord_alert_bot_v3.py` → calls `build_per_grade_table()` then passes to formatter
