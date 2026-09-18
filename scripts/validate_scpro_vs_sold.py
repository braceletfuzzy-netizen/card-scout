"""Validate SCPro grading against eBay sold data (clean data #4).

Sept 18 clean-data #4: Fetch active + sold listings from SCPro for the same
card. Compare median prices by grade tier to check if SCPro's listings match
eBay sold reality.

Usage:
    python scripts/validate_scpro_vs_sold.py [--cards N]

Outputs:
    Per-card comparison of active vs sold prices by grade tier
    Where the data agrees (SCPro is accurate)
    Where the data diverges (SCPro might be biased or noisy)
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv('.env')

from db_models import Card, get_session
from discord_alert_bot_v3 import run_apify_search, classify_grade


def fetch_and_classify(card, include_sold=True, max_items=30):
    """Fetch listings and group by classified grade."""
    result = run_apify_search(card.search_query, preset='cards-sports', include_sold=include_sold, max_listings=max_items)
    items = result.get('items', []) if isinstance(result, dict) else result

    by_grade = defaultdict(list)
    for item in items:
        title = item.get('title', '')
        price = item.get('price_usd') or item.get('price')
        sold = item.get('sold') or item.get('sold_count', 0) > 0
        grade = classify_grade({'title': title})
        by_grade[grade].append({'price': price, 'sold': sold, 'title': title})

    return by_grade


def median(values):
    """Compute median of a list."""
    clean = [v for v in values if v is not None]
    if not clean:
        return None
    sorted_v = sorted(clean)
    n = len(sorted_v)
    return sorted_v[n // 2] if n % 2 else (sorted_v[n // 2 - 1] + sorted_v[n // 2]) / 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cards', type=int, default=3, help='Number of cards to validate')
    args = parser.parse_args()

    print(f'Validating SCPro data against eBay sold for {args.cards} cards...')
    print()

    session = get_session()
    cards = session.query(Card).filter_by(enabled=True).limit(args.cards).all()
    print('Cards being tested:')
    for c in cards:
        print(f'  - {c.search_query}')
    print()

    for card in cards:
        print(f'=== {card.search_query} ===')
        by_grade = fetch_and_classify(card, include_sold=True)

        # Print by grade tier
        print(f'  Got {sum(len(v) for v in by_grade.values())} total listings')
        print()
        print(f'  {"Grade":15} {"#Listings":>10} {"Median price":>14} {"Sold median":>14} {"Ratio":>8}')
        print(f'  {"-"*15} {"-"*10} {"-"*14} {"-"*14} {"-"*8}')

        for grade in sorted(by_grade.keys()):
            items = by_grade[grade]
            active = [i['price'] for i in items if not i.get('sold') and i['price']]
            sold = [i['price'] for i in items if i.get('sold') and i['price']]

            active_med = median(active)
            sold_med = median(sold)
            ratio = (active_med / sold_med) if (active_med and sold_med and sold_med > 0) else None
            ratio_str = f'{ratio:.2f}x' if ratio else 'N/A'

            print(f'  {grade:15} {len(items):>10} {"$"+f"{active_med:.2f}" if active_med else "N/A":>14} '
                  f'{"$"+f"{sold_med:.2f}" if sold_med else "N/A":>14} {ratio_str:>8}')

        print()

    session.close()

    print()
    print('=' * 70)
    print('INTERPRETATION')
    print('=' * 70)
    print()
    print('Expected pattern:')
    print('  - Active listings median >= sold median (active is asking, sold is what people paid)')
    print('  - Ratio usually 0.85-1.0x (asking is 0-15% above actual sale)')
    print('  - If ratio > 1.5x: SCPro listings are inflated (overpriced)')
    print('  - If ratio < 0.7x: SCPro listings are below sold (real deals!)')
    print()
    print('Notes:')
    print('  - SCPro sold data is sparse (only some listings have sold_count)')
    print('  - High-value cards (PSA 10 vintage) often have no eBay sold comps')
    print('  - If sold count = 0 for a grade tier, skip it')
    print()
    print('Action items:')
    print('  - Where active >> sold (ratio > 1.5x): Grade classifier might be wrong,')
    print('    OR SCPro is showing premium listings that dont sell at asking.')
    print('  - Where active << sold (ratio < 0.7x): Real opportunity - alert customer!')


if __name__ == '__main__':
    main()
