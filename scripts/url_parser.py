"""
URL Parser for Card Scout (Sept 16, 2026).

Founder insight: 'the more pricing points the better, as long as we can
get our URL search figured out'

Purpose: Extract structured IDs from marketplace URLs so we can do
direct lookups instead of fuzzy searches. Each URL gives us 1+ pricing
data points.

Supported URL formats:
- PSA: https://www.psacard.com/pop/{category}/{year}/{set}/{spec_id}
- eBay: https://www.ebay.com/itm/{item_id} or search URL
- Sportscardspro: https://www.sportscardspro.com/product/{product_id}
- Pricecharting: https://www.pricecharting.com/console/{slug}

Each parser returns a dict with:
- type: 'psa' | 'ebay' | 'scpro' | 'pricecharting' | None
- id: extracted ID
- raw_url: original URL
- extras: any additional data (e.g., category, year, set)
- valid: bool (whether the URL is usable)

Usage:
    from url_parser import parse_url

    result = parse_url("https://www.psacard.com/pop/baseball-cards/1969/topps-stamps/51060")
    # result = {
    #     'type': 'psa',
    #     'id': '51060',
    #     'raw_url': '...',
    #     'extras': {'category': 'baseball-cards', 'year': '1969', 'set': 'topps-stamps'},
    #     'valid': True
    # }
"""

import re
from typing import Optional, Dict


# PSA URL patterns
# Format: https://www.psacard.com/pop/{category}/{year}/{set-name}/{spec_id}
PSA_PATTERN = re.compile(
    r'psacard\.com/pop/([^/]+)/(\d{4})/([^/]+)/(\d+)',
    re.IGNORECASE
)

# eBay item URL: https://www.ebay.com/itm/{item_id}
EBAY_ITEM_PATTERN = re.compile(
    r'ebay\.com/itm/(?:[^/]+/)?(\d+)',
    re.IGNORECASE
)

# eBay search URL: https://www.ebay.com/sch/i.html?_nkw={query}
EBAY_SEARCH_PATTERN = re.compile(
    r'ebay\.com/sch/i\.html\?_nkw=([^&]+)',
    re.IGNORECASE
)

# Sportscardspro URL: https://www.sportscardspro.com/product/{id}-{slug}
# Product ID is the numeric portion before the slug
SCPRO_PATTERN = re.compile(
    r'sportscardspro\.com/product/(\d+)',
    re.IGNORECASE
)

# Pricecharting URL: https://www.pricecharting.com/console/{slug}
# The slug includes a number at the end which is the product ID
# Example: https://www.pricecharting.com/console/game-name-12345
PRICECHARTING_PATTERN = re.compile(
    r'pricecharting\.com/console/([\w-]+?)(?:-(\d+))?/?$',
    re.IGNORECASE
)


def parse_psa_url(url: str) -> Optional[Dict]:
    """
    Extract PSA spec_id from a PSA URL.

    Example:
        https://www.psacard.com/pop/baseball-cards/1969/topps-stamps/51060
        -> {
            'type': 'psa',
            'id': '51060',
            'raw_url': url,
            'extras': {
                'category': 'baseball-cards',
                'year': '1969',
                'set_slug': 'topps-stamps'
            },
            'valid': True
        }
    """
    m = PSA_PATTERN.search(url)
    if not m:
        return None

    category, year, set_slug, spec_id = m.groups()
    return {
        'type': 'psa',
        'id': spec_id,
        'raw_url': url,
        'extras': {
            'category': category,
            'year': year,
            'set_slug': set_slug,
        },
        'valid': True,
    }


def parse_ebay_url(url: str) -> Optional[Dict]:
    """
    Extract eBay item ID from a URL.

    Examples:
        https://www.ebay.com/itm/123456789
        -> {'type': 'ebay', 'id': '123456789', 'raw_url': url, 'extras': {}, 'valid': True}

        https://www.ebay.com/itm/Some-Title/123456789
        -> same as above

        https://www.ebay.com/sch/i.html?_nkw=bo+jackson+psa+10
        -> {'type': 'ebay', 'id': None, 'raw_url': url,
            'extras': {'search_query': 'bo jackson psa 10'}, 'valid': False}
    """
    # Try item URL first
    m = EBAY_ITEM_PATTERN.search(url)
    if m:
        return {
            'type': 'ebay',
            'id': m.group(1),
            'raw_url': url,
            'extras': {'kind': 'item'},
            'valid': True,
        }

    # Try search URL (gives us a query but no item_id)
    m = EBAY_SEARCH_PATTERN.search(url)
    if m:
        query = m.group(1).replace('+', ' ').replace('%20', ' ')
        return {
            'type': 'ebay',
            'id': None,
            'raw_url': url,
            'extras': {'kind': 'search', 'search_query': query},
            'valid': False,
        }

    return None


def parse_scpro_url(url: str) -> Optional[Dict]:
    """
    Extract Sportscardspro product ID from a URL.

    Example:
        https://www.sportscardspro.com/product/72584-michael-jordan-1986-fleer
        -> {
            'type': 'scpro',
            'id': '72584',
            'raw_url': url,
            'extras': {},
            'valid': True
        }
    """
    m = SCPRO_PATTERN.search(url)
    if not m:
        return None

    return {
        'type': 'scpro',
        'id': m.group(1),
        'raw_url': url,
        'extras': {},
        'valid': True,
    }


def parse_pricecharting_url(url: str) -> Optional[Dict]:
    """
    Extract Pricecharting slug/ID from a URL.

    Example:
        https://www.pricecharting.com/console/basketball-cards-1986-fleer-michael-jordan-72584
        -> {
            'type': 'pricecharting',
            'id': '72584',
            'raw_url': url,
            'extras': {'slug': 'basketball-cards-1986-fleer-michael-jordan-72584'},
            'valid': True
        }
    """
    m = PRICECHARTING_PATTERN.search(url)
    if not m:
        return None

    full_slug = m.group(1)
    product_id = m.group(2)  # May be None if no trailing ID

    return {
        'type': 'pricecharting',
        'id': product_id,
        'raw_url': url,
        'extras': {'slug': full_slug},
        'valid': product_id is not None,
    }


def parse_url(url: str) -> Dict:
    """
    Auto-detect URL type and extract structured data.

    Returns a dict with at minimum:
        {'type': None | 'psa' | 'ebay' | 'scpro' | 'pricecharting',
         'id': str | None,
         'raw_url': str,
         'extras': dict,
         'valid': bool}

    If no pattern matches, returns:
        {'type': None, 'id': None, 'raw_url': url, 'extras': {}, 'valid': False}
    """
    if not url or not isinstance(url, str):
        return {'type': None, 'id': None, 'raw_url': str(url), 'extras': {}, 'valid': False}

    parsers = [
        parse_psa_url,
        parse_ebay_url,
        parse_scpro_url,
        parse_pricecharting_url,
    ]

    for parser in parsers:
        result = parser(url)
        if result:
            return result

    return {'type': None, 'id': None, 'raw_url': url, 'extras': {}, 'valid': False}


def parse_urls(urls) -> list:
    """
    Parse multiple URLs at once.

    Args:
        urls: list of URL strings (may include None or empty)

    Returns:
        list of parse result dicts (one per input URL)
    """
    if not urls:
        return []
    return [parse_url(u) if u else {'type': None, 'id': None, 'raw_url': '', 'extras': {}, 'valid': False} for u in urls]


# ============================================================================
# Self-tests
# ============================================================================

def _self_test():
    test_cases = [
        # (URL, expected_type, expected_valid, expected_id)
        ("https://www.psacard.com/pop/baseball-cards/1969/topps-stamps/51060", 'psa', True, '51060'),
        ("https://www.psacard.com/pop/tcg-cards/2024/pokemon-surging-sparks/59164", 'psa', True, '59164'),
        ("https://www.ebay.com/itm/123456789", 'ebay', True, '123456789'),
        ("https://www.ebay.com/itm/Some-Card-Title/987654321", 'ebay', True, '987654321'),
        ("https://www.ebay.com/sch/i.html?_nkw=bo+jackson", 'ebay', False, None),
        ("https://www.sportscardspro.com/product/72584-michael-jordan", 'scpro', True, '72584'),
        ("https://www.pricecharting.com/console/basketball-cards-1986-fleer-72584", 'pricecharting', True, '72584'),
        ("https://example.com/random", None, False, None),
        ("", None, False, None),
        (None, None, False, None),
    ]

    passed = 0
    failed = 0

    for url, exp_type, exp_valid, exp_id in test_cases:
        result = parse_url(url)
        if (result['type'] == exp_type and
            result['valid'] == exp_valid and
            result['id'] == exp_id):
            passed += 1
            print(f"  [OK] {url or '(None)':60} -> {result['type']}/{result['id']}")
        else:
            failed += 1
            print(f"  [FAIL] {url or '(None)':60}")
            print(f"         expected: type={exp_type}, valid={exp_valid}, id={exp_id}")
            print(f"         got:      type={result['type']}, valid={result['valid']}, id={result['id']}")

    print()
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)}")
    return failed == 0


if __name__ == '__main__':
    import sys
    success = _self_test()
    sys.exit(0 if success else 1)
