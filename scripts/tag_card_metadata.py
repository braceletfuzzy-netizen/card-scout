"""Tag cards with era + category metadata (clean data #5).

Sept 18 clean-data #5: Add era (decade) and category (sport/TCG) metadata
to cards table. Required for:
- Cross-card ratio analysis (math model)
- Filter alerts by category
- Era-aware deal scoring

Strategy:
1. For Jim's existing 5 cards: manually tag based on knowledge
2. For future cards: auto-derive from search query year + keywords
3. Optionally pull from Card Hedger search results (more reliable)

Usage:
    python scripts/tag_card_metadata.py [--auto] [--customer-id ID]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv('.env')

from db_models import Card, Customer, get_session


# Manual tag definitions for Jim's 5 cards + Alan's 3 cards + Hingle's cards
# Format: search_query_pattern -> {era, category, subcategory, is_rookie, is_key_card}
MANUAL_TAGS = {
    # Jim's 5 active cards
    'donruss 87 bo jackson': {'era': '1980s', 'category': 'Sports Cards', 'subcategory': 'Baseball', 'is_rookie': True, 'is_key_card': True},
    'frank thomas topps draft #1 pick': {'era': '1990s', 'category': 'Sports Cards', 'subcategory': 'Baseball', 'is_rookie': True, 'is_key_card': True},
    'michael jordan 1991 upper deck baseball': {'era': '1990s', 'category': 'Sports Cards', 'subcategory': 'Baseball', 'is_rookie': False, 'is_key_card': True},
    'derek jeter topps future star': {'era': '1990s', 'category': 'Sports Cards', 'subcategory': 'Baseball', 'is_rookie': True, 'is_key_card': False},
    'henry aaron topps 1969 autograph': {'era': '1960s', 'category': 'Sports Cards', 'subcategory': 'Baseball', 'is_rookie': False, 'is_key_card': True},
    # Jim's disabled cards (15 from before, including Hingle's)
    'alex rodriguez circa mariners ss': {'era': '1990s', 'category': 'Sports Cards', 'subcategory': 'Baseball', 'is_rookie': True, 'is_key_card': False},
    'yancy thigpen air force one 1996 collectors edge': {'era': '1990s', 'category': 'Sports Cards', 'subcategory': 'Football', 'is_rookie': True, 'is_key_card': False},
    'barry sanders stadium club super chrome 1997': {'era': '1990s', 'category': 'Sports Cards', 'subcategory': 'Football', 'is_rookie': False, 'is_key_card': True},
    'charizard ex pokemon 151 #199': {'era': '2020s', 'category': 'TCG', 'subcategory': 'Pokemon', 'is_rookie': False, 'is_key_card': True},
    'mtg black lotus alpha': {'era': '1990s', 'category': 'TCG', 'subcategory': 'MTG', 'is_rookie': False, 'is_key_card': True},
    'mewtwo pokemon 151 #150': {'era': '2020s', 'category': 'TCG', 'subcategory': 'Pokemon', 'is_rookie': False, 'is_key_card': True},
    'pokemon base set charizard holo': {'era': '1990s', 'category': 'TCG', 'subcategory': 'Pokemon', 'is_rookie': False, 'is_key_card': True},
    '1989 topps ken griffey jr. 1 autograph': {'era': '1980s', 'category': 'Sports Cards', 'subcategory': 'Baseball', 'is_rookie': True, 'is_key_card': True},
    'bob griese graded 28': {'era': '1970s', 'category': 'Sports Cards', 'subcategory': 'Football', 'is_rookie': False, 'is_key_card': False},
    'brett favre graded pinnacle 13': {'era': '1990s', 'category': 'Sports Cards', 'subcategory': 'Football', 'is_rookie': False, 'is_key_card': False},
    # Alan's cards
    '2018 topps upton, ohtani & trout us158 parallel': {'era': '2010s', 'category': 'Sports Cards', 'subcategory': 'Baseball', 'is_rookie': False, 'is_key_card': True},
    'mookie betts raw 10 topps us26': {'era': '2010s', 'category': 'Sports Cards', 'subcategory': 'Baseball', 'is_rookie': False, 'is_key_card': True},
    'portgas d. ace graded 10 one piece op13-119': {'era': '2020s', 'category': 'TCG', 'subcategory': 'One Piece', 'is_rookie': False, 'is_key_card': False},
}


def derive_era_from_query(query):
    """Extract era from year in search query. Returns decade string or None."""
    # Find 4-digit years
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', query)
    if not years:
        return None
    year = int(years[0])
    if year < 1970:
        return 'pre-1970s'
    decade = (year // 10) * 10
    return f'{decade}s'


def derive_category_from_query(query):
    """Extract category from keywords in query."""
    q = query.lower()
    if 'pokemon' in q or 'pikachu' in q or 'charizard' in q:
        return ('TCG', 'Pokemon')
    if 'mtg' in q or 'magic' in q or 'black lotus' in q:
        return ('TCG', 'MTG')
    if 'one piece' in q or 'luffy' in q or 'ace' in q:
        return ('TCG', 'One Piece')
    # Sports detection
    if any(w in q for w in ['baseball', 'mlb']):
        return ('Sports Cards', 'Baseball')
    if any(w in q for w in ['football', 'nfl', 'qb']):
        return ('Sports Cards', 'Football')
    if any(w in q for w in ['basketball', 'nba']):
        return ('Sports Cards', 'Basketball')
    if 'hockey' in q or 'nhl' in q:
        return ('Sports Cards', 'Hockey')
    return (None, None)


def auto_tag(card):
    """Auto-derive era + category from search_query."""
    era = derive_era_from_query(card.search_query)
    category, subcategory = derive_category_from_query(card.search_query)
    return {
        'era': era,
        'category': category,
        'subcategory': subcategory,
        'is_rookie': 'rookie' in card.search_query.lower() or 'rc' in card.search_query.lower(),
        'is_key_card': None,  # Hard to auto-detect
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help='Use auto-derivation instead of manual tags')
    parser.add_argument('--customer-id', type=int, help='Only tag cards for one customer')
    args = parser.parse_args()

    session = get_session()

    # Build query
    q = session.query(Card)
    if args.customer_id:
        q = q.filter_by(customer_id=args.customer_id)
    cards = q.all()

    print(f'Tagging {len(cards)} cards (mode: {"AUTO" if args.auto else "MANUAL"})')
    print()

    tagged = 0
    skipped = 0
    for card in cards:
        if args.auto:
            tags = auto_tag(card)
        else:
            key = card.search_query.lower().strip()
            tags = MANUAL_TAGS.get(key)

        if tags:
            card.era = tags.get('era')
            card.category = tags.get('category')
            card.subcategory = tags.get('subcategory')
            card.is_rookie = tags.get('is_rookie')
            card.is_key_card = tags.get('is_key_card')
            tagged += 1
            print(f'  [OK] {card.search_query[:50]:50} | era={card.era} cat={card.category}/{card.subcategory} rookie={card.is_rookie}')
        else:
            skipped += 1
            print(f'  [SKIP] {card.search_query[:50]:50} (no tag found)')

    session.commit()
    print()
    print(f'Tagged {tagged}, skipped {skipped}')

    # Summary
    from collections import Counter
    era_counts = Counter(c.era for c in cards if c.era)
    cat_counts = Counter((c.category, c.subcategory) for c in cards if c.category)

    print()
    print('Era distribution:')
    for era, count in era_counts.most_common():
        print(f'  {era}: {count}')

    print()
    print('Category distribution:')
    for (cat, sub), count in cat_counts.most_common():
        print(f'  {cat} / {sub}: {count}')

    session.close()


if __name__ == '__main__':
    main()
