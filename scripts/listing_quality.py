"""
Listing quality scorer — V2 grade-tiered filter.

WHY: Per Sept 14 spec — eBay listings can be junk ($1 BIN with $50 shipping,
$1 starting bid on 30-day auctions, bulk lots). These pollute the "below median"
signal.

This module scores each listing 0-100 quality. Above threshold = show in alert.
Below = drop. Thin markets skip the filter entirely (every listing is signal).

Architecture:
- score_listing_quality(item, grade_context) -> {'score': int, 'reasons': [str]}
- filter_listings_by_quality(items, threshold, grade_context) -> filtered list

Where grade_context is from grade_detector (tier, grade, label).

Inputs we have from eBay actor:
- price_usd (raw price)
- listing_type: 'sold' | 'active'
- watchers_count: int (people watching this)
- sold_count: int (already sold N)
- title: str (raw text)

Inputs we don't have (would need actor update):
- timeLeft (for auction ending soon)
- shipping cost
- BIN vs auction distinction

For V2, we use heuristics:
- Auctions with no watchers + low price → likely junk (score < 50)
- BIN with high price + recent activity → likely real (score > 70)
- Bulk lots ("LOT OF" in title) → very low score
- "$0.99" or "$1.00" type BIN → low score unless thin market
"""

from typing import Dict, List, Optional


# Score thresholds
SCORE_THRESHOLD_DEFAULT = 60  # Above this = show in alert
SCORE_THRESHOLD_THIN_MARKET = 0  # Skip filter entirely for thin markets

# Heuristic weights
JUNK_KEYWORDS = [
    'lot of', 'bulk', 'mixed lot', 'wholesale',
    'parts', 'repair', 'broken', 'damaged',
    'no grade', 'ungraded', 'raw - ',
]


def score_listing_quality(
    item: Dict,
    grade_tier: Optional[str] = None,
    thin_market: bool = False,
) -> Dict:
    """Score a single listing 0-100 based on quality signals.

    Args:
        item: eBay listing dict with price_usd, title, listing_type, etc.
        grade_tier: detected grade tier (psa_10, psa_9, raw, etc.) or None
        thin_market: if True, skip quality filter (return 100)

    Returns:
        {
            'score': 0-100,
            'reasons': list of human-readable reasons for the score,
            'should_alert': bool (above threshold),
        }
    """
    if thin_market:
        return {
            'score': 100,
            'reasons': ['thin market — skipping quality filter'],
            'should_alert': True,
        }

    score = 70  # Start neutral
    reasons = []

    title = (item.get('title') or '').lower()
    price = item.get('price_usd') or 0
    listing_type = item.get('listing_type', 'active')
    watchers = item.get('watchers_count') or 0
    sold_count = item.get('sold_count') or 0

    # === NEGATIVE SIGNALS ===

    # Bulk lots / wholesale — almost never a real single-card deal
    for kw in JUNK_KEYWORDS:
        if kw in title:
            score -= 30
            reasons.append(f"title contains '{kw}' (bulk/junk signal)")
            break

    # Suspiciously low price (likely error or junk)
    if 0 < price < 2.00:
        score -= 20
        reasons.append(f"price ${price:.2f} is suspiciously low")

    # Zero watchers on active listing — possibly junk or unwanted item
    if listing_type == 'active' and watchers == 0 and sold_count == 0:
        score -= 10
        reasons.append("no watchers, no prior sales — possibly unwanted")

    # === POSITIVE SIGNALS ===

    # Has watchers — indicates interest
    if watchers >= 3:
        score += 10
        reasons.append(f"{watchers} watchers — real interest")

    # Has sold_count — seller is active
    if sold_count >= 5:
        score += 10
        reasons.append(f"{sold_count} prior sales — active seller")

    # Reasonable price (>$5 for raw, >$20 for graded)
    if grade_tier == 'raw' and price >= 5:
        score += 5
        reasons.append(f"raw price ${price:.2f} looks reasonable")
    elif grade_tier and grade_tier.startswith('psa_') and price >= 20:
        score += 5
        reasons.append(f"graded price ${price:.2f} looks reasonable")

    # Clamp to 0-100
    score = max(0, min(100, score))

    should_alert = score >= SCORE_THRESHOLD_DEFAULT

    return {
        'score': score,
        'reasons': reasons,
        'should_alert': should_alert,
    }


def filter_listings_by_quality(
    items: List[Dict],
    grade_tier: Optional[str] = None,
    thin_market: bool = False,
    threshold: int = SCORE_THRESHOLD_DEFAULT,
) -> Dict:
    """Filter a list of eBay listings by quality score.

    Args:
        items: list of eBay listing dicts
        grade_tier: detected grade tier or None
        thin_market: if True, return all listings unfiltered
        threshold: minimum score to include (default 60)

    Returns:
        {
            'kept': [...listings above threshold...],
            'dropped': [...listings below threshold...],
            'scores': [{listing, score, reasons}, ...]
        }
    """
    if thin_market:
        return {
            'kept': items,
            'dropped': [],
            'scores': [
                {'item': i, 'score': 100, 'reasons': ['thin market']}
                for i in items
            ],
        }

    kept = []
    dropped = []
    scores = []

    for item in items:
        result = score_listing_quality(item, grade_tier, thin_market=False)
        scores.append({'item': item, **result})

        # Use the threshold passed in (default 60)
        if result['score'] >= threshold:
            kept.append(item)
        else:
            dropped.append(item)

    return {
        'kept': kept,
        'dropped': dropped,
        'scores': scores,
    }


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Listing Quality Scorer — self-test")
    print("=" * 70)

    test_items = [
        {
            'name': 'Real deal (high watchers, reasonable price)',
            'item': {
                'title': '1987 Donruss Bo Jackson #14 Rookie RC',
                'price_usd': 15.00,
                'listing_type': 'active',
                'watchers_count': 12,
                'sold_count': 8,
            },
            'grade_tier': 'raw',
            'thin_market': False,
        },
        {
            'name': 'Junk $1 BIN (no watchers)',
            'item': {
                'title': 'Bo Jackson Card',
                'price_usd': 1.00,
                'listing_type': 'active',
                'watchers_count': 0,
                'sold_count': 0,
            },
            'grade_tier': 'raw',
            'thin_market': False,
        },
        {
            'name': 'Bulk lot',
            'item': {
                'title': 'LOT OF 50 Baseball Cards Bo Jackson Frank Thomas',
                'price_usd': 25.00,
                'listing_type': 'active',
                'watchers_count': 5,
                'sold_count': 3,
            },
            'grade_tier': None,
            'thin_market': False,
        },
        {
            'name': 'PSA 10 graded, real seller',
            'item': {
                'title': '1987 Donruss Bo Jackson #14 Rookie PSA 10 GEM MINT',
                'price_usd': 650.00,
                'listing_type': 'active',
                'watchers_count': 25,
                'sold_count': 50,
            },
            'grade_tier': 'psa_10',
            'thin_market': False,
        },
        {
            'name': 'Thin market A-Rod (any listing is signal)',
            'item': {
                'title': 'Alex Rodriguez 1997 Circa Rookie',
                'price_usd': 1.39,
                'listing_type': 'active',
                'watchers_count': 0,
                'sold_count': 0,
            },
            'grade_tier': 'psa_10',
            'thin_market': True,
        },
    ]

    for test in test_items:
        result = score_listing_quality(test['item'], test['grade_tier'], test['thin_market'])
        print(f"\n{test['name']}:")
        print(f"  Score: {result['score']}  (alert: {result['should_alert']})")
        for reason in result['reasons']:
            print(f"    - {reason}")
