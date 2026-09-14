# grade_detector.py

**Purpose**: Parses eBay listing titles for grade markers and routes them to the right tier bucket.

## What it does

Given an eBay listing title like `"1996 Topps Chrome #80 Derek Jeter BGS 9.5 GEM MINT"`, returns:

```python
{
    'authority': 'BGS',   # or None if raw
    'grade': 9.5,          # numeric grade
    'tier': 'psa_9',       # bot's 6-bucket system
    'is_graded': True
}
```

For raw listings like `"1995 Topps Derek Jeter Future Star #199"`, returns:

```python
{
    'authority': None,
    'grade': None,
    'tier': 'raw',
    'is_graded': False
}
```

## API

```python
from grade_detector import detect_grade, bucket_listings

# Single title
result = detect_grade("PSA 10 GEM MINT Jeter")
# {'authority': 'PSA', 'grade': 10.0, 'tier': 'psa_10', 'is_graded': True}

# Bucket a list of items
buckets = bucket_listings(items)
# Returns dict with keys: 'psa_10', 'psa_9', 'psa_8', 'psa_lower', 'raw', 'other_graders'
```

## Supported Patterns

| Pattern | Authority | Grade |
|---|---|---|
| `BGS 9.5`, `BGS 9.5 GEM MINT` | BGS | 9.5 |
| `BGS 10 BLACK LABEL`, `BGS 10 PRIME` | BGS | 10 |
| `BGS 10`, `BGS 9` | BGS | 10 / 9 |
| `CGC 10`, `CGC 9.5` | CGC | 10 / 9.5 |
| `SGC 10`, `SGC 9` | SGC | 10 / 9 |
| `PSA GEM MINT 10`, `PSA 10 GM` | PSA | 10 |
| `PSA MT 9` (= PSA 9 Mint) | PSA | 9 |
| `PSA 9 MINT` | PSA | 9 |
| `PSA 10`, `PSA 9` | PSA | 10 / 9 |

## Tier Mapping (per bot's 6-bucket system)

| Authority | Grade | Tier |
|---|---|---|
| PSA / BGS / CGC / SGC | 10 | `psa_10` |
| PSA / BGS / CGC / SGC | 9 | `psa_9` |
| PSA / BGS / CGC / SGC | 8 | `psa_8` |
| PSA / BGS / CGC / SGC | <8 | `psa_lower` |
| (no grade marker) | - | `raw` |

All graders (PSA, BGS, CGC, SGC) get bucketed by numeric grade — we don't differentiate authority at the tier level because the bot's `track_psa_X` filter is about grade, not company.

## Edge Cases Handled

- **`PSA MT 9`** → grade 9 (MT = Mint = PSA 9)
- **`BGS 9.5 GEM MINT`** → grade 9.5, tier `psa_9`
- **`BGS 10 BLACK LABEL`** → grade 10, tier `psa_10`
- **`PSA GEM MINT 10`** → grade 10
- **`Raw`** (no grade marker) → tier `raw`
- Multiple grades (rare) → first one wins

## Self-Test

```bash
python grade_detector.py
```

Runs 9 sample titles through the parser, prints results.

## Used By

- `ticker_formatter.py` → identifies which grade tier each eBay listing belongs to
- `grade_range_calculator.py` → groups sales-by-tier for SD/mean calculation
- `discord_alert_bot_v3.py` → (potential future use for grade filtering)

## Caveats

- Regex-based, not ML-based. Unusual title formats may be missed.
- BGS 9.5 has 7 unique sub-grades (BGS 9.5 Gold, Black Label, etc.) — we treat them all as 9.5 numeric.
- "Mint" alone (without PSA/BGS) is treated as raw, not graded.
