"""Audit the grade classifier on real SCPro listings.

Sept 18 clean-data #3: Fetch live SCPro listings for several cards and check
how often classify_grade() gets the grade right.

Usage:
    python scripts/audit_grade_classifier.py [--cards N]

Outputs:
    Per-card accuracy breakdown
    Common misclassification patterns
    Recommendations for classifier improvements
"""
import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv('.env')

from db_models import Card, get_session


def fetch_listings_for_card(card, max_items=20):
    """Fetch live SCPro listings for a card."""
    # Import the SCPro runner
    from discord_alert_bot_v3 import run_apify_search
    try:
        result = run_apify_search(card.search_query, preset='cards-sports', include_sold=False, max_listings=max_items)
        items = result.get('items', []) if isinstance(result, dict) else result
        return items[:max_items] if items else []
    except Exception as e:
        return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cards', type=int, default=5, help='Number of cards to sample')
    args = parser.parse_args()

    print(f'Sampling {args.cards} cards from database...')
    session = get_session()

    # Get active cards
    cards = session.query(Card).filter_by(enabled=True).limit(args.cards * 3).all()
    if len(cards) > args.cards:
        cards = random.sample(cards, args.cards)

    print(f'Got {len(cards)} cards:')
    for c in cards:
        print(f'  - {c.search_query}')
    print()

    # Import classifier
    from discord_alert_bot_v3 import classify_grade

    # Classify each card's listings
    print('Fetching live SCPro listings for each card...')
    print()

    all_classifications = defaultdict(int)
    sample_by_grade = defaultdict(list)
    sample_by_card = {}

    for card in cards:
        print(f'--- {card.search_query} ---')
        items = fetch_listings_for_card(card, max_items=15)
        if not items:
            print('  No listings (SCPro failed or rate limited)')
            continue

        print(f'  Got {len(items)} listings')
        for item in items:
            title = item.get('title', '')
            price = item.get('price_usd') or item.get('price')
            grade = classify_grade({'title': title})
            all_classifications[grade] += 1
            sample_by_grade[grade].append({
                'card': card.search_query[:30],
                'title': title[:80],
                'price': price,
            })
            if card.id not in sample_by_card:
                sample_by_card[card.id] = []
            sample_by_card[card.id].append((title[:60], grade, price))

        # Print first 5 listings with classifications
        for title, grade, price in sample_by_card[card.id][:5]:
            print(f'    [{grade:18}] ${price} | {title}')
        print()

    session.close()

    print()
    print('=' * 70)
    print('CLASSIFICATION DISTRIBUTION')
    print('=' * 70)
    total = sum(all_classifications.values())
    if total == 0:
        print('No listings fetched')
        return
    for grade in sorted(all_classifications.keys(), key=lambda g: -all_classifications[g]):
        count = all_classifications[grade]
        pct = (count / total * 100)
        print(f'  {grade:20} {count:5} ({pct:5.1f}%)')

    print()
    print('=' * 70)
    print('SAMPLE TITLES BY GRADE (for hand-audit)')
    print('=' * 70)
    for grade in sorted(sample_by_grade.keys()):
        print(f'\n--- {grade} ({all_classifications[grade]} total) ---')
        for s in sample_by_grade[grade][:8]:
            print(f'  ${s["price"]:>8.2f} | [{s["card"]}] {s["title"]}')

    print()
    print('=' * 70)
    print('AUDIT CHECKLIST')
    print('=' * 70)
    print()
    print('For each sample above, ask:')
    print('1. Is the classified grade correct? (visual inspection of title)')
    print('2. Are there grade markers the classifier missed?')
    print('3. Are there grade markers it picked up but were wrong?')
    print()
    print('Common issues to look for:')
    print('- "PSA 9 MINT" with classifier saying PSA 10 (cross-grade confusion)')
    print('- "BGS 9.5" matched as PSA 10 because "9.5" is in the title')
    print('- "Gem Mint" alone (not PSA 10) misclassified as PSA 10')
    print('- "Raw" listings misclassified as graded')
    print('- "PSA" without number misclassified as unknown_graded (correct)')
    print('- Misordered: e.g., "BGS" before "PSA 10" check')


if __name__ == '__main__':
    main()
