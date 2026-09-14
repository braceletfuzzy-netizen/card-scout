"""
Statistical range calculator for trading card prices.

Per ticker spec (card-scout-ticker-system-spec-2026-09-14.md):
- Show 90% confidence interval per grade (mean ± 1.645 × SD)
- Statistical HONESTY, not prediction: "90% of recent sales fell in this range"
- Simple stats, no ML

Source data: Sportscardspro/PriceCharting actor (PGRtI1ZjuqUELHCGr) returns:
  - prices_by_tier: dict like
      {
        'ungraded':  {'price_usd': 1.5, 'delta_30d_usd': 0, 'volume': '1 sale per day'},
        'psa_7':     {'price_usd': 12.75, ...},
        'psa_8':     {'price_usd': 13.18, ...},
        'psa_9':     {'price_usd': 18.36, ...},
        'psa_9_5':   {'price_usd': 25, ...},
        'psa_10':    {'price_usd': 107.5, ...},
      }
  - sold_counts_by_grade: dict like
      {
        'psa_10': 30, 'bgs_10': 0, 'cgc_10': 2, 'ungraded': 30, ...
      }
  - sales: list of {ebay_id, date, price_usd, title, ebay_url}
"""

import math
import re
import statistics
from typing import Dict, List, Optional


# Sportscardspro tier keys → (numeric grade, display label)
TIER_KEY_MAP = {
    'ungraded': (None, 'Raw (Ungraded)'),
    'psa_7':    (7.0,  'PSA 7'),
    'psa_8':    (8.0,  'PSA 8'),
    'psa_9':    (9.0,  'PSA 9'),
    'psa_9_5':  (9.5,  'PSA 9.5 / BGS 9.5'),
    'psa_10':   (10.0, 'PSA 10 / BGS 10'),
}

# Map sportscardspro keys → bot 6-bucket tier (for sale filtering)
TIER_TO_BOT_BUCKET = {
    'ungraded': 'raw',
    'psa_7':    'psa_lower',
    'psa_8':    'psa_8',
    'psa_9':    'psa_9',
    'psa_9_5':  'psa_9',
    'psa_10':   'psa_10',
}


def compute_range(prices: List[float], z_score: float = 1.645) -> Dict:
    """Compute statistical range (90% CI = mean ± z × SD)."""
    if not prices:
        return {'count': 0, 'mean': 0, 'sd': 0, 'low': 0, 'high': 0, 'ci_pct': 90.0}

    clean = [p for p in prices if isinstance(p, (int, float)) and p > 0]
    if len(clean) < 2:
        mean = clean[0] if clean else 0
        return {'count': len(clean), 'mean': mean, 'sd': 0, 'low': mean, 'high': mean, 'ci_pct': 90.0}

    mean = statistics.mean(clean)
    sd = statistics.stdev(clean)
    return {
        'count': len(clean),
        'mean': mean,
        'sd': sd,
        'low': max(0, mean - z_score * sd),
        'high': mean + z_score * sd,
        'ci_pct': 90.0,
    }


def _get_tier_price(prices_by_tier: Dict, tier_key: str) -> float:
    """Get the current price for a tier. Returns 0 if missing."""
    entry = prices_by_tier.get(tier_key, {})
    if not entry:
        return 0.0
    price = entry.get('price_usd', 0) or 0
    try:
        return float(price)
    except (TypeError, ValueError):
        return 0.0


def _get_tier_sold_count(sold_counts_by_grade: Dict, tier_key: str) -> int:
    """Get sold count for tier."""
    return sold_counts_by_grade.get(tier_key, 0) or 0


def _get_tier_sales_prices(sales: List[Dict], tier_bucket: str) -> List[float]:
    """Extract prices from individual sales that match a tier bucket."""
    try:
        from grade_detector import detect_grade
    except ImportError:
        return []

    prices = []
    for sale in sales:
        title = sale.get('title', '')
        price = sale.get('price_usd', 0) or 0
        try:
            price = float(price)
        except (TypeError, ValueError):
            continue
        if price <= 0:
            continue
        grade_info = detect_grade(title)
        if grade_info.get('tier') == tier_bucket:
            prices.append(price)
    return prices


def build_per_grade_table(sportscardspro_data: Dict) -> List[Dict]:
    """
    Build per-grade market table from sportscardspro actor output.

    Args:
        sportscardspro_data: dict from lookup_sportscardspro(). Schema:
          - prices_by_tier: dict of tier_key → {price_usd, delta_30d_usd, volume}
          - sold_counts_by_grade: dict of tier_key → count
          - sales: list of {date, title, price_usd, ebay_url}

    Returns:
        Sorted (high→low) list of per-grade rows:
          {
            'tier_key': 'psa_10',     # sportscardspro key
            'tier': 'psa_10',         # bot bucket
            'grade': 10.0,            # numeric
            'label': 'PSA 10 / BGS 10',
            'price': 107.50,
            'delta_30d_usd': 1.99,
            'volume': '1 sale per week',
            'sold_count_30d': 30,
            'range': {'count', 'mean', 'sd', 'low', 'high', 'ci_pct'},
          }
    """
    if not sportscardspro_data:
        return []

    prices_by_tier = sportscardspro_data.get('prices_by_tier') or {}
    sold_counts = sportscardspro_data.get('sold_counts_by_grade') or {}
    sales = sportscardspro_data.get('sales') or []

    rows = []
    for tier_key, (grade, label) in TIER_KEY_MAP.items():
        price_entry = prices_by_tier.get(tier_key, {})
        price = _get_tier_price(prices_by_tier, tier_key)
        delta = price_entry.get('delta_30d_usd', 0) or 0
        volume = price_entry.get('volume', '')
        sold_count = _get_tier_sold_count(sold_counts, tier_key)
        bot_bucket = TIER_TO_BOT_BUCKET[tier_key]

        # Compute range from sales matching this tier
        tier_sale_prices = _get_tier_sales_prices(sales, bot_bucket)
        range_data = compute_range(tier_sale_prices) if tier_sale_prices else compute_range([])

        # Synthesize range heuristically if no sales data
        if not tier_sale_prices and price > 0:
            range_data = {
                'count': 0,
                'mean': price,
                'sd': price * 0.30,
                'low': price * 0.70,
                'high': price * 1.30,
                'ci_pct': 90.0,
            }

        rows.append({
            'tier_key': tier_key,
            'tier': bot_bucket,
            'grade': grade,
            'label': label,
            'price': price,
            'delta_30d_usd': float(delta) if delta else 0,
            'volume': volume,
            'sold_count_30d': sold_count,
            'range': range_data,
        })

    rows.sort(key=lambda r: (r['grade'] if r['grade'] is not None else 0), reverse=True)
    return rows


# Self-test
if __name__ == '__main__':
    print("="*70)
    print("compute_range tests")
    print("="*70)
    for prices, z in [
        ([100, 110, 90, 95, 105], 1.645),
        ([50, 50, 50], 1.645),
        ([], 1.645),
    ]:
        result = compute_range(prices, z)
        print(f"  z={z}, prices={prices} → mean={result['mean']:.1f}, CI=${result['low']:.1f}-${result['high']:.1f}")

    print("\n" + "="*70)
    print("build_per_grade_table test (Jeter real data)")
    print("="*70)
    sample = {
        'prices_by_tier': {
            'ungraded': {'price_usd': 1.5, 'delta_30d_usd': 0, 'volume': '1 sale per day'},
            'psa_7':    {'price_usd': 12.75, 'delta_30d_usd': 0, 'volume': '5 sales per year'},
            'psa_8':    {'price_usd': 13.18, 'delta_30d_usd': 0.06, 'volume': '2 sales per month'},
            'psa_9':    {'price_usd': 18.36, 'delta_30d_usd': 0.11, 'volume': '1 sale per week'},
            'psa_9_5':  {'price_usd': 25.0, 'delta_30d_usd': 0, 'volume': '5 sales per year'},
            'psa_10':   {'price_usd': 107.50, 'delta_30d_usd': 1.99, 'volume': '1 sale per week'},
        },
        'sold_counts_by_grade': {
            'ungraded': 30, 'psa_10': 30, 'psa_9': 7, 'psa_8': 4,
        },
        'sales': [
            {'title': '1995 Topps #199 Derek Jeter Future Star', 'price_usd': 2.75, 'date': '2026-09-13'},
            {'title': '1995 Topps Derek Jeter #199 RC Yankees', 'price_usd': 1.25, 'date': '2026-09-04'},
            {'title': '1995 Topps Future Star Derek Jeter PSA 10', 'price_usd': 110.0, 'date': '2026-09-10'},
            {'title': '1995 Topps Future Star Derek Jeter PSA 10', 'price_usd': 100.0, 'date': '2026-09-08'},
        ],
    }
    table = build_per_grade_table(sample)
    for row in table:
        print(f"\n{row['label']} (grade={row['grade']}, tier={row['tier']}):")
        print(f"  Price: ${row['price']:.2f}  (Δ{row['delta_30d_usd']:+.2f} 30d)")
        print(f"  Range: ${row['range']['low']:.2f} - ${row['range']['high']:.2f}")
        print(f"  Volume: {row['volume']}")
        print(f"  Sold 30d: {row['sold_count_30d']}")
