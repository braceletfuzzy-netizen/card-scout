"""
Deal detection logic (Sept 16 beta feedback).

Founder's insight: 'If the market for 10's doesn't have the pricing
spread, the price is the price. But where there is spread, there is a
deal definition.'

Algorithm (per-grade):
1. Get pricing band for a grade (low, high, volume)
2. If spread (high - low) is 0 or very small → no deals possible
3. If spread > $X% threshold → compute lower-third line:
   lower_third = low + (high - low) / 3
4. Flag listings priced below lower_third as deals

Why per-grade: PSA 10 often has $0 spread (single market rate).
PSA 9, 8, 7 often have real spread (condition varies).
Each grade shows deals only if spread exists.

Confidence: high spread + high volume = more confident deals.
Low spread + low volume = fewer/no deals.

Output: deals per grade, sorted by discount %.
"""

from typing import Dict, List, Optional


def compute_lower_third_threshold(low: float, high: float) -> float:
    """
    Compute the lower-third threshold for deal detection.

    Founder's definition:
    '[x1___/_*_/___x2], where * represents the mathematical avg between
    x1 and x2 and we split the range into thirds. Then anything below
    this threshold [lower third line] should show up.'

    Mathematically: lower_third = low + (high - low) / 3

    Example: low=$50, high=$200
      - Mid: $125
      - Lower third: $50 + ($200-$50)/3 = $100
      - Anything < $100 is a deal
    """
    if high <= low:
        return low
    spread = high - low
    return low + spread / 3


def grade_has_spread(low: Optional[float], high: Optional[float],
                     min_spread_dollars: float = 1.0,
                     min_spread_pct: float = 5.0) -> bool:
    """
    Decide if a grade has enough spread to define deals.

    Requirements:
    - Spread >= $1 (filters out noise)
    - Spread >= 5% of high (filters out narrow markets)

    Why both: a $0.50 spread on a $1000 card is real noise.
              A $50 spread on a $100 card is meaningful.
    """
    if low is None or high is None:
        return False
    spread = high - low
    if spread < min_spread_dollars:
        return False
    if high > 0 and (spread / high * 100) < min_spread_pct:
        return False
    return True


def detect_deals_for_grade(
    grade_label: str,
    low: float,
    high: float,
    listings: List[Dict],
    min_volume: int = 3,
    max_deals: int = 3
) -> Optional[Dict]:
    """
    Detect deals in listings for a specific grade.

    Args:
        grade_label: 'PSA 10', 'PSA 9', etc.
        low: lowest price in pricing band
        high: highest price in pricing band
        listings: raw listings for this grade [{price_usd, url, title, ...}]
        min_volume: minimum volume to consider deals
        max_deals: max deals to return (Discord limit)

    Returns: {
        'grade': str,
        'spread': float,
        'spread_pct': float,
        'threshold': float,
        'volume': int,
        'deals': [{price, discount_pct, url, title}],
        'no_deals_reason': str  # why no deals (if applicable)
    }
    """
    result = {
        'grade': grade_label,
        'spread': round(high - low, 2),
        'spread_pct': round((high - low) / high * 100, 1) if high > 0 else 0,
        'threshold': None,
        'volume': len(listings),
        'deals': [],
        'no_deals_reason': None
    }

    # Check 1: Is there enough spread?
    if not grade_has_spread(low, high):
        result['no_deals_reason'] = (
            f'No spread (low=${low:.2f}, high=${high:.2f}) — '
            f'market has single price'
        )
        return result

    # Check 2: Enough volume?
    if len(listings) < min_volume:
        result['no_deals_reason'] = (
            f'Only {len(listings)} listings — '
            f'need {min_volume} minimum for deals'
        )
        return result

    # Compute threshold
    threshold = compute_lower_third_threshold(low, high)
    result['threshold'] = round(threshold, 2)

    # Find listings below threshold
    deals = []
    for listing in listings:
        price = listing.get('price_usd', 0)
        if price > 0 and price < threshold:
            discount_pct = (threshold - price) / threshold * 100
            deals.append({
                'price': price,
                'discount_pct': round(discount_pct, 1),
                'url': listing.get('url', ''),
                'title': listing.get('title', '')[:80],
                'grade_label': grade_label
            })

    # Sort by discount (biggest discount first)
    deals.sort(key=lambda d: -d['discount_pct'])
    result['deals'] = deals[:max_deals]
    result['total_deals_found'] = len(deals)

    return result


def detect_all_deals(
    pricing_bands: Dict[str, Dict],
    listings_by_grade: Dict[str, List[Dict]]
) -> List[Dict]:
    """
    Detect deals across all grades for a card.

    Args:
        pricing_bands: {'psa_10': {'low': x, 'high': y, 'volume': z}, ...}
        listings_by_grade: {'psa_10': [listings], 'psa_9': [listings], ...}

    Returns: list of per-grade results (one entry per grade that has spread)
    """
    grade_label_map = {
        'psa_10': 'PSA 10',
        'psa_9_5': 'PSA 9.5',
        'psa_9': 'PSA 9',
        'psa_8': 'PSA 8',
        'psa_7': 'PSA 7',
        'raw': 'Ungraded'
    }

    results = []
    for tier_key, band in pricing_bands.items():
        if not band:
            continue
        low = band.get('low')
        high = band.get('high')
        listings = listings_by_grade.get(tier_key, [])

        result = detect_deals_for_grade(
            grade_label=grade_label_map.get(tier_key, tier_key),
            low=low,
            high=high,
            listings=listings
        )
        if result:
            results.append(result)

    return results


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("DEAL DETECTION — SELF-TEST")
    print("=" * 70)

    # Test 1: compute_lower_third_threshold
    print("\n[Test 1] compute_lower_third_threshold")
    cases = [
        ((50, 200), 100.0),      # Founder's example
        ((100, 100), 100.0),     # No spread → returns low
        ((10, 50), 23.33),       # Smaller case
        ((0, 100), 33.33),       # low=0 edge case
    ]
    for (low, high), expected in cases:
        result = compute_lower_third_threshold(low, high)
        ok = "[OK]" if abs(result - expected) < 0.1 else "[FAIL]"
        print(f"  {ok} low=${low}, high=${high} → threshold=${result:.2f} (expected ${expected:.2f})")

    # Test 2: grade_has_spread
    print("\n[Test 2] grade_has_spread")
    cases = [
        ((50, 200), True),       # Real spread ($150)
        ((100, 100), False),     # No spread
        ((99, 100), False),      # Tiny spread (< 5%)
        ((95, 105), True),       # 9.5% spread ($10)
        ((None, 100), False),    # Missing low
        ((99.5, 100), False),    # $0.50 spread (< $1)
    ]
    for (low, high), expected in cases:
        result = grade_has_spread(low, high)
        ok = "[OK]" if result == expected else "[FAIL]"
        print(f"  {ok} low={low}, high={high} → has_spread={result} (expected {expected})")

    # Test 3: detect_deals_for_grade with Bo Jackson-like data
    print("\n[Test 3] detect_deals_for_grade (Bo Jackson PSA 10 — no spread)")
    bo_jackson_p10 = [
        {'price_usd': 655.34, 'url': 'https://example.com/1', 'title': 'Bo Jackson Donruss PSA 10'},
        {'price_usd': 700.00, 'url': 'https://example.com/2', 'title': 'Bo Jackson PSA 10'},
    ]
    result = detect_deals_for_grade('PSA 10', low=655.34, high=655.34, listings=bo_jackson_p10)
    print(f"  Spread: ${result['spread']} ({result['spread_pct']}%)")
    print(f"  Reason: {result['no_deals_reason']}")
    assert result['deals'] == []
    assert result['no_deals_reason'] is not None

    # Test 4: detect_deals_for_grade with spread (hypothetical card)
    print("\n[Test 4] detect_deals_for_grade (hypothetical card with spread)")
    listings = [
        {'price_usd': 30, 'url': 'url1', 'title': 'Cheap one'},
        {'price_usd': 50, 'url': 'url2', 'title': 'Below median'},
        {'price_usd': 80, 'url': 'url3', 'title': 'Above median'},
        {'price_usd': 120, 'url': 'url4', 'title': 'Above threshold'},
        {'price_usd': 200, 'url': 'url5', 'title': 'Top of range'},
    ]
    result = detect_deals_for_grade('PSA 9', low=30, high=200, listings=listings, max_deals=3)
    print(f"  Spread: ${result['spread']} ({result['spread_pct']}%)")
    print(f"  Threshold: ${result['threshold']}")
    print(f"  Total deals found: {result['total_deals_found']}")
    print(f"  Top deals:")
    for d in result['deals']:
        print(f"    ${d['price']} ({d['discount_pct']}% below threshold)")
    # Expected: threshold=30 + (200-30)/3 = 86.67
    # Deals below $86.67: $30, $50, $80 (3 deals — 80 is below threshold)
    assert abs(result['threshold'] - 86.67) < 0.1
    assert len(result['deals']) == 3

    print("\n" + "=" * 70)
    print("Self-test complete.")
