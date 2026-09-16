"""
URL Resolver (Sept 16, 2026).

Founder insight: 'the more pricing points the better, as long as we
can get our URL search figured out'

Problem: Set-level URLs (e.g., /game/baseball-cards-1987-donruss-rookies/)
give us set pages with hundreds of cards. We need to find specific card
URLs (e.g., /game/baseball-cards-1987-donruss-rookies/bo-jackson-14).

Solution: For each card, drill into the set page and find the specific
card's product URL. This gives us a product ID that can be used for
direct API lookups.

Strategy:
1. Fetch the set page (e.g., SCPRO /game/{slug})
2. Parse the page for individual card listings
3. Match our card (player/year/set/number) to one of those listings
4. Return the specific card's URL

This module provides the framework; the actual scraping logic will be
implemented per-source in subsequent steps.

Usage:
    from url_resolver import resolve_card_urls

    resolved = resolve_card_urls(
        card_name='Bo Jackson',
        year='1987',
        set_name='Donruss',
        card_number='14',
        scpro_url='https://www.sportscardspro.com/game/baseball-cards-1987-donruss-rookies/bo-jackson-14',
    )
"""

import re
from typing import Optional, Dict, List
from url_parser import parse_url


def build_card_slug(card_name: str) -> str:
    """
    Convert a card name into a URL slug.

    Examples:
        'Bo Jackson' -> 'bo-jackson'
        'Michael Jordan' -> 'michael-jordan'
        "Yancey Thigpen" -> 'yancey-thigpen'
    """
    # Lowercase, replace spaces with hyphens, remove special chars
    slug = card_name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return slug


def build_scpro_card_url(set_slug: str, card_slug: str, card_number: Optional[str] = None) -> str:
    """
    Build a specific card URL on Sportscardspro.

    Format: https://www.sportscardspro.com/game/{set-slug}/{card-slug}-{card-number}

    Example:
        build_scpro_card_url('baseball-cards-1987-donruss-rookies', 'bo-jackson', '14')
        -> 'https://www.sportscardspro.com/game/baseball-cards-1987-donruss-rookies/bo-jackson-14'
    """
    parts = ['https://www.sportscardspro.com/game', set_slug]
    if card_number:
        parts.append(f'{card_slug}-{card_number}')
    else:
        parts.append(card_slug)
    return '/'.join(parts)


def build_psa_card_url(category: str, year: str, set_slug: str, spec_id: str) -> str:
    """
    Build a specific card URL on PSA.

    Format: https://www.psacard.com/pop/{category}/{year}/{set-slug}/{spec_id}

    Example:
        build_psa_card_url('baseball-cards', '1987', 'donruss', '110001')
        -> 'https://www.psacard.com/pop/baseball-cards/1987/donruss/110001'
    """
    return f'https://www.psacard.com/pop/{category}/{year}/{set_slug}/{spec_id}'


def extract_card_name_from_query(card_search_query: str) -> str:
    """
    Extract the card name (player name) from search query.

    Examples:
        'Donruss 87 Bo Jackson' -> 'Bo Jackson'
        'Frank Thomas Topps Draft #1 Pick' -> 'Frank Thomas'
        'Michael Jordan 1991 Upper Deck Baseball' -> 'Michael Jordan'
        'Bo Jackson #14' -> 'Bo Jackson'
        'Derek Jeter Topps Future Star' -> 'Derek Jeter'
    """
    # Remove card numbers like #14 or SP1
    cleaned = re.sub(r'#\s*[a-zA-Z0-9]+', '', card_search_query)
    cleaned = re.sub(r'\b(SP|RC|SSP|AP)\s*\d+', '', cleaned, flags=re.IGNORECASE)

    # Remove years (4-digit numbers AND 2-digit years like "'87" or "87")
    cleaned = re.sub(r"\b(19|20)\d{2}\b", '', cleaned)
    cleaned = re.sub(r"\b'\d{2}\b", '', cleaned)
    cleaned = re.sub(r"\b\d{2,3}\b", '', cleaned)  # 2-3 digit numbers (years + card numbers like 151)

    # Remove common brand/set words
    SET_WORDS = {
        'topps', 'donruss', 'upper', 'deck', 'fleer', 'bowman', 'score',
        'stadium', 'club', 'chrome', 'pinnacle', 'select', 'prizm',
        'mosaic', 'optic', 'panini', 'hoops', 'circa', 'sp',
        'authentics', 'premier', 'draft', 'pick', 'future', 'star',
        'mariners', 'ss', 'super', 'refractor', 'autograph', 'base',
        'insert', 'parallel', 'pokemon', 'tcg', 'mtg', 'magic',
        'lorcana', 'flesh', 'blood', 'alpha', 'beta', 'unlimited',
        '1st', 'edition', 'shadowless', 'black', 'lotus', 'mox',
        'time', 'walk', 'ancestral', 'set', 'holo', 'holographic',
        'collectors', 'collector', 'edge', 'reserve', 'force', 'one',
        'air', 'chrome', 'baseball', 'football', 'basketball',
        'hockey', 'soccer', 'ultra', 'spectra', 'momentum', 'zenith',
        'revolution', 'absolute', 'contenders', 'phoenix',
    }
    words = cleaned.split()
    name_words = [w for w in words if w.lower() not in SET_WORDS]
    return ' '.join(name_words).strip()


def extract_card_number(card_search_query: str) -> Optional[str]:
    """
    Extract card number from search query like 'Bo Jackson #14' or 'Michael Jordan SP1'.

    Returns the number/string after # or the variant code.
    """
    # Look for # followed by digits
    m = re.search(r'#\s*([a-zA-Z0-9]+)', card_search_query)
    if m:
        return m.group(1)

    # Look for SP, RC, etc. followed by digits
    m = re.search(r'\b(SP|RC|SSP|AP)\s*(\d+)', card_search_query, re.IGNORECASE)
    if m:
        return m.group(2)

    return None


def resolve_scpro_set_to_card(
    scpro_set_url: str,
    card_name: str,
    card_number: Optional[str] = None,
) -> Dict:
    """
    Given a set-level SCPRO URL, build a likely card-level URL.

    This is a heuristic — we guess the card URL based on naming conventions.
    The real verification requires scraping the set page and matching listings.

    Args:
        scpro_set_url: Set-level URL like /game/{slug}
        card_name: 'Bo Jackson'
        card_number: '14' (optional)

    Returns:
        dict with:
            - guessed_url: predicted card-level URL
            - confidence: 'high' if card_number present, 'low' otherwise
            - needs_verification: bool (should we scrape the set page?)
    """
    parsed = parse_url(scpro_set_url)
    if not parsed or parsed['type'] != 'scpro':
        return {
            'guessed_url': None,
            'confidence': 'none',
            'needs_verification': True,
            'reason': 'Invalid SCPRO URL',
        }

    slug = parsed['extras'].get('slug', '')
    if not slug:
        return {
            'guessed_url': None,
            'confidence': 'none',
            'needs_verification': True,
            'reason': 'No slug extracted',
        }

    card_slug = build_card_slug(card_name)
    guessed_url = build_scpro_card_url(slug, card_slug, card_number)

    confidence = 'high' if card_number else 'low'

    return {
        'guessed_url': guessed_url,
        'confidence': confidence,
        'needs_verification': confidence == 'low',
        'set_slug': slug,
        'card_slug': card_slug,
        'card_number': card_number,
        'reason': f'Guessed URL from set slug + card name' + (f' + #{card_number}' if card_number else ''),
    }


# ============================================================================
# Self-tests
# ============================================================================

def _self_test():
    test_cases = [
        # build_card_slug
        ('Bo Jackson', 'bo-jackson'),
        ('Michael Jordan', 'michael-jordan'),
        ('Alex Rodriguez', 'alex-rodriguez'),

        # build_scpro_card_url
        ('baseball-cards-1987-donruss-rookies', 'bo-jackson', '14',
         'https://www.sportscardspro.com/game/baseball-cards-1987-donruss-rookies/bo-jackson-14'),
        ('football-cards-1997-circa', 'alex-rodriguez', None,
         'https://www.sportscardspro.com/game/football-cards-1997-circa/alex-rodriguez'),

        # build_psa_card_url
        ('baseball-cards', '1987', 'donruss', '110001',
         'https://www.psacard.com/pop/baseball-cards/1987/donruss/110001'),

        # extract_card_number
        ('Bo Jackson #14', '14'),
        ('Michael Jordan SP1', '1'),
        ('No number here', None),
        ('Alex Rodriguez #100', '100'),
    ]

    passed = 0
    failed = 0

    # Test slug building
    for card_name, expected in test_cases[:3]:
        actual = build_card_slug(card_name)
        if actual == expected:
            passed += 1
            print(f"  [OK] build_card_slug({card_name!r}) = {actual!r}")
        else:
            failed += 1
            print(f"  [FAIL] build_card_slug({card_name!r})")
            print(f"         expected: {expected!r}")
            print(f"         got:      {actual!r}")

    # Test SCPRO URL building
    for set_slug, card_slug, num, expected in test_cases[3:5]:
        actual = build_scpro_card_url(set_slug, card_slug, num)
        if actual == expected:
            passed += 1
            print(f"  [OK] build_scpro_card_url({set_slug!r}, {card_slug!r}, {num!r})")
        else:
            failed += 1
            print(f"  [FAIL] build_scpro_card_url({set_slug!r}, {card_slug!r}, {num!r})")
            print(f"         expected: {expected!r}")
            print(f"         got:      {actual!r}")

    # Test PSA URL building
    category, year, set_slug, spec_id = test_cases[5][:4]
    expected_psa = test_cases[5][4]
    actual = build_psa_card_url(category, year, set_slug, spec_id)
    if actual == expected_psa:
        passed += 1
        print(f"  [OK] build_psa_card_url({category!r}, {year!r}, {set_slug!r}, {spec_id!r})")
    else:
        failed += 1
        print(f"  [FAIL] build_psa_card_url")
        print(f"         expected: {expected_psa!r}")
        print(f"         got:      {actual!r}")

    # Test card number extraction
    for query, expected in test_cases[6:]:
        actual = extract_card_number(query)
        if actual == expected:
            passed += 1
            print(f"  [OK] extract_card_number({query!r}) = {actual!r}")
        else:
            failed += 1
            print(f"  [FAIL] extract_card_number({query!r})")
            print(f"         expected: {expected!r}")
            print(f"         got:      {actual!r}")

    # Test resolve_scpro_set_to_card
    set_url = 'https://www.sportscardspro.com/game/baseball-cards-1987-donruss-rookies'
    result = resolve_scpro_set_to_card(set_url, 'Bo Jackson', '14')
    if result['guessed_url'] and 'bo-jackson-14' in result['guessed_url']:
        passed += 1
        print(f"  [OK] resolve_scpro_set_to_card('Bo Jackson', #14) -> {result['guessed_url']}")
    else:
        failed += 1
        print(f"  [FAIL] resolve_scpro_set_to_card result: {result}")

    # Test extract_card_name_from_query
    name_tests = [
        ('Donruss 87 Bo Jackson', 'Bo Jackson'),
        ('Frank Thomas Topps Draft #1 Pick', 'Frank Thomas'),
        ('Michael Jordan 1991 Upper Deck Baseball', 'Michael Jordan'),
        ('Bo Jackson #14', 'Bo Jackson'),
        ('Derek Jeter Topps Future Star', 'Derek Jeter'),
        ('Yancy Thigpen Air Force One 1996 Collectors Edge', 'Yancy Thigpen'),
        ('Charizard ex Pokemon 151 #199', 'Charizard ex'),
        ('MTG Black Lotus Alpha', ''),  # All words are set words — search by set
    ]

    for query, expected in name_tests:
        actual = extract_card_name_from_query(query)
        if actual == expected:
            passed += 1
            print(f"  [OK] extract_card_name_from_query({query!r}) = {actual!r}")
        else:
            failed += 1
            print(f"  [FAIL] extract_card_name_from_query({query!r})")
            print(f"         expected: {expected!r}")
            print(f"         got:      {actual!r}")

    print()
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
    return failed == 0


if __name__ == '__main__':
    import sys
    success = _self_test()
    sys.exit(0 if success else 1)
