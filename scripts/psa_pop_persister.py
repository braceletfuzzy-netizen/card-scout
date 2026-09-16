"""
PSA population fetcher with DB persistence (Sept 16, V3 stock-ticker feature).

Fetches PSA pop data via the Apify actor and persists to the cards table.
Enables the "stock ticker" framing where each card = a stock and PSA grades
= share classes.

Usage:
    from psa_pop_persister import fetch_and_persist_pop, compute_rarity, get_stock_class_label

    # Fetch + persist
    pop_data = fetch_and_persist_pop(session, card)
    if pop_data:
        print(f"PSA 10: {pop_data['psa_10_pop']} of {pop_data['total_pop']}")

    # Compute rarity
    rarity = compute_rarity(psa_10_pop=23, total_pop=1731)
    # Returns: {'label': 'RARE', 'pct': 1.3}

    # Stock class label
    label = get_stock_class_label('psa_10')
    # Returns: 'A'
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict

sys.path.insert(0, str(Path(__file__).parent))

from db_models import Card
from sqlalchemy.orm import Session


# ============================================================================
# RARITY COMPUTATION
# ============================================================================

def compute_rarity(psa_10_pop: Optional[int], total_pop: Optional[int]) -> Dict:
    """
    Compute rarity of PSA 10 within total PSA population.

    Founder's framing (Sept 16): "Each tier has a different value... PSA 10
    is the A series, 9 is the B, 8 is the C... Each card is like a share
    of stock."

    Returns: {
        'label': 'RARE'|'SCARCE'|'COMMON'|'PLENTIFUL'|'UNKNOWN',
        'pct': float|None,  # PSA 10 as % of total pop
        'description': str  # human-readable
    }

    Thresholds:
      - PSA 10 < 1% of total = RARE (e.g. 5/500)
      - PSA 10 < 5% of total = SCARCE
      - PSA 10 < 15% of total = COMMON
      - PSA 10 > 15% of total = PLENTIFUL
    """
    if not psa_10_pop or not total_pop or total_pop == 0:
        return {
            'label': 'UNKNOWN',
            'pct': None,
            'description': 'No population data'
        }

    pct = (psa_10_pop / total_pop) * 100

    # Boundary: 1% is RARE, 5% is SCARCE, 15% is COMMON
    # Use <= so 1.0% counts as RARE (not SCARCE)
    if pct <= 1:
        return {
            'label': 'RARE',
            'pct': pct,
            'description': f'Only {pct:.1f}% of total pop (highly sought-after)'
        }
    elif pct <= 5:
        return {
            'label': 'SCARCE',
            'pct': pct,
            'description': f'{pct:.1f}% of total pop (rare)'
        }
    elif pct <= 15:
        return {
            'label': 'COMMON',
            'pct': pct,
            'description': f'{pct:.1f}% of total pop (common)'
        }
    else:
        return {
            'label': 'PLENTIFUL',
            'pct': pct,
            'description': f'{pct:.1f}% of total pop (plentiful)'
        }


def get_stock_class_label(tier: str) -> str:
    """
    Map grade tier to stock-class label.

    Founder's insight (Sept 16): "PSA 10 is the A series, PSA 9 is the B
    series, PSA 8 is the C series, etc."

    Mapping:
      PSA 10 = A (highest value class)
      PSA 9.5 = A-
      PSA 9 = B
      PSA 8 = C
      PSA 7 = D
      Raw = unlisted (no PSA grade)
    """
    mapping = {
        'psa_10': 'A',
        'psa_9_5': 'A-',
        'psa_9': 'B',
        'psa_8': 'C',
        'psa_7': 'D',
        'raw': '—',  # unlisted (no PSA grade)
    }
    return mapping.get(tier, '?')


def compute_premium(psa_10_price: Optional[float], psa_9_price: Optional[float]) -> Optional[float]:
    """
    Compute the premium multiplier of PSA 10 vs PSA 9.

    E.g. if PSA 10 = $655 and PSA 9 = $107, premium = 6.1×
    meaning PSA 10 trades at 6.1× the PSA 9 price (rare-asset premium).

    Returns: float ratio, or None if either price is missing.
    """
    if not psa_10_price or not psa_9_price or psa_9_price <= 0:
        return None
    return round(psa_10_price / psa_9_price, 1)


# ============================================================================
# FETCH + PERSIST
# ============================================================================

# Cache TTL — don't re-fetch PSA pop more than once per week (founder's call)
PSA_POP_CACHE_DAYS = 7


def should_fetch_pop(card: Card) -> bool:
    """
    Decide whether to fetch PSA pop for this card.

    Returns True if:
      - Card has psa_set_url
      - Card.include_pop is True
      - No prior fetch OR fetch is older than PSA_POP_CACHE_DAYS
    """
    if not card.psa_set_url:
        return False
    if not card.include_pop:
        return False
    if not card.psa_pop_fetched_at:
        return True
    age = datetime.utcnow() - card.psa_pop_fetched_at
    return age > timedelta(days=PSA_POP_CACHE_DAYS)


def fetch_and_persist_pop(session: Session, card: Card) -> Optional[Dict]:
    """
    Fetch PSA population data for a card and persist to DB.

    Returns: dict with psa_total_pop, psa_10_pop, psa_9_pop, all_grades
             OR None if fetch failed or skipped.
    """
    if not should_fetch_pop(card):
        # Return cached data if available
        if card.psa_total_pop is not None:
            return {
                'psa_total_pop': card.psa_total_pop,
                'psa_10_pop': card.psa_10_pop,
                'psa_9_pop': card.psa_9_pop,
                'cached': True
            }
        return None

    # Lazy import (only when needed — avoids loading Apify code for non-pop flows)
    try:
        from psa_pop_lookup import lookup_psa_population, extract_pop_summary
    except ImportError as e:
        print(f"  [POP] Could not import psa_pop_lookup: {e}")
        return None

    # Extract subject from search_query (best-effort)
    subject = card.search_query.split()[-1] if card.search_query else None

    try:
        items = lookup_psa_population(card.psa_set_url, max_results=10)
        if not items:
            return None
        pop_summary = extract_pop_summary(items, subject_filter=subject)
        if not pop_summary:
            return None

        # Persist to DB
        card.psa_total_pop = pop_summary.get('total_pop')
        card.psa_10_pop = pop_summary.get('psa_10_pop')
        card.psa_9_pop = pop_summary.get('psa_9_pop')
        card.psa_pop_fetched_at = datetime.utcnow()
        session.commit()

        return {
            'psa_total_pop': pop_summary.get('total_pop'),
            'psa_10_pop': pop_summary.get('psa_10_pop'),
            'psa_9_pop': pop_summary.get('psa_9_pop'),
            'all_grades': pop_summary.get('all_grades'),
            'cached': False
        }
    except Exception as e:
        print(f"  [POP] Failed to fetch/persist for card {card.id}: {e}")
        return None


def get_card_pop_summary(card: Card) -> Dict:
    """
    Get a summary of the card's PSA population data (read-only, no fetch).

    Returns: {
        'rarity': {...},     # compute_rarity output
        'stock_class': 'A',  # for the highest grade tracked
        'premium': None,     # not computed here (needs prices)
        'has_data': bool,
        'fetched_at': datetime|None,
        'is_stale': bool
    }
    """
    if not card.psa_total_pop:
        return {
            'rarity': compute_rarity(None, None),
            'stock_class': '?',
            'has_data': False,
            'fetched_at': None,
            'is_stale': True
        }

    is_stale = (
        not card.psa_pop_fetched_at or
        datetime.utcnow() - card.psa_pop_fetched_at > timedelta(days=PSA_POP_CACHE_DAYS)
    )

    return {
        'rarity': compute_rarity(card.psa_10_pop, card.psa_total_pop),
        'stock_class': 'A',  # we always report PSA 10 as the top class
        'has_data': True,
        'fetched_at': card.psa_pop_fetched_at,
        'is_stale': is_stale
    }


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("PSA POP PERSISTER — SELF-TEST")
    print("=" * 70)

    print("\n[Test 1] compute_rarity()")
    cases = [
        (5, 500, 'RARE'),       # 1% boundary
        (10, 500, 'SCARCE'),    # 2%
        (50, 500, 'COMMON'),    # 10%
        (100, 500, 'PLENTIFUL'),  # 20%
        (None, 500, 'UNKNOWN'),  # missing
        (5, 0, 'UNKNOWN'),      # zero total
    ]
    for psa10, total, expected in cases:
        result = compute_rarity(psa10, total)
        ok = "[OK]" if result['label'] == expected else "[FAIL]"
        print(f"  {ok} psa_10={psa10}, total={total} → {result['label']} (expected {expected})")
        if result['pct'] is not None:
            print(f"        pct={result['pct']:.1f}%, desc='{result['description']}'")

    print("\n[Test 2] get_stock_class_label()")
    class_cases = [
        ('psa_10', 'A'),
        ('psa_9_5', 'A-'),
        ('psa_9', 'B'),
        ('psa_8', 'C'),
        ('psa_7', 'D'),
        ('raw', '—'),
        ('unknown_tier', '?'),
    ]
    for tier, expected in class_cases:
        result = get_stock_class_label(tier)
        ok = "[OK]" if result == expected else "[FAIL]"
        print(f"  {ok} {tier} → {result} (expected {expected})")

    print("\n[Test 3] compute_premium()")
    premium_cases = [
        (655.34, 107.50, 6.1),   # Bo Jackson
        (1500, 250, 6.0),
        (None, 100, None),
        (500, None, None),
        (500, 0, None),
    ]
    for p10, p9, expected in premium_cases:
        result = compute_premium(p10, p9)
        ok = "[OK]" if result == expected else "[FAIL]"
        print(f"  {ok} PSA 10=${p10}, PSA 9=${p9} → premium={result}× (expected {expected})")

    print("\n" + "=" * 70)
    print("Self-test complete.")
