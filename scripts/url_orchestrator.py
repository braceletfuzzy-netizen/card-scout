"""
URL-Based Lookup Orchestrator (Sept 16, 2026).

Founder insight: 'the more pricing points the better, as long as we can
get our URL search figured out'

This module coordinates lookups across multiple marketplaces using
URL-derived IDs. The goal is to maximize pricing data points per card
without relying on fuzzy text search.

Strategy:
1. Parse URLs to extract IDs (PSA spec_id, SCPRO product_id, eBay item_id)
2. Call appropriate API/actor with the ID
3. Aggregate all pricing points per card
4. Fall back to fuzzy search only if URL lookup fails

Pricing point sources (in priority order):
1. eBay Browse API (free, listing data, spread source)
2. Card Ladder (sold data, pop, sales history)
3. Pricecharting API (single price per grade, fallback)
4. Sportscardspro API (single price per grade, fallback)
5. PSA actor (pop data, currently broken)
6. Fuzzy search (last resort)

Usage:
    from url_orchestrator import lookup_card_pricing

    result = lookup_card_pricing(
        card_id=123,
        search_query='Bo Jackson 1990 Topps PSA 10',
        psa_url='https://www.psacard.com/pop/baseball-cards/1990/topps/110001',
        sportscardspro_url=None,
        ebay_url=None,
        pricecharting_url=None,
    )
"""

from typing import Optional, Dict, List
from url_parser import parse_url


def extract_pricing_sources(
    psa_url: Optional[str] = None,
    sportscardspro_url: Optional[str] = None,
    ebay_url: Optional[str] = None,
    pricecharting_url: Optional[str] = None,
) -> Dict:
    """
    Extract all available pricing sources from URLs.

    Returns a dict mapping source name -> parsed URL data.
    Sources without valid URLs are excluded.

    Example:
        {
            'psa': {'type': 'psa', 'id': '51060', 'valid': True, ...},
            'ebay': {'type': 'ebay', 'id': '123456789', 'valid': True, ...},
            'scpro': None,  # no URL provided
            'pricecharting': None,  # no URL provided
        }
    """
    return {
        'psa': parse_url(psa_url) if psa_url else None,
        'scpro': parse_url(sportscardspro_url) if sportscardspro_url else None,
        'ebay': parse_url(ebay_url) if ebay_url else None,
        'pricecharting': parse_url(pricecharting_url) if pricecharting_url else None,
    }


def count_pricing_points(sources: Dict) -> int:
    """
    Count how many pricing data points we can get from the URLs.

    Returns:
        int: number of pricing sources available
    """
    count = 0
    for source_name, source_data in sources.items():
        if source_data and source_data.get('valid'):
            count += 1
    return count


def get_lookup_strategy(sources: Dict) -> Dict:
    """
    Determine lookup strategy based on available URLs.

    Returns:
        dict with:
            - mode: 'url_first' | 'search_fallback' | 'search_only'
            - primary_id: dict of source -> id for direct lookups
            - search_query: str to use as fallback
            - reason: str explaining the choice
    """
    valid_sources = {k: v for k, v in sources.items() if v and v.get('valid')}

    if not valid_sources:
        return {
            'mode': 'search_only',
            'primary_id': None,
            'search_query': None,
            'reason': 'No valid URLs provided — must use fuzzy search',
        }

    # URL-first mode: we have at least one valid URL
    primary_id = {k: v['id'] for k, v in valid_sources.items()}

    return {
        'mode': 'url_first',
        'primary_id': primary_id,
        'search_query': None,
        'reason': f"URL-first mode using {len(valid_sources)} sources: {', '.join(valid_sources.keys())}",
    }


def lookup_card_pricing(
    card_id: int,
    search_query: str,
    psa_url: Optional[str] = None,
    sportscardspro_url: Optional[str] = None,
    ebay_url: Optional[str] = None,
    pricecharting_url: Optional[str] = None,
) -> Dict:
    """
    Main entry point: lookup pricing data for a card using URLs.

    Args:
        card_id: DB card ID (for logging)
        search_query: Fallback search term if URL lookup fails
        psa_url: Optional PSA URL
        sportscardspro_url: Optional Sportscardspro URL
        ebay_url: Optional eBay URL (item URL)
        pricecharting_url: Optional Pricecharting URL

    Returns:
        dict with:
            - strategy: lookup strategy used
            - sources: parsed URL data for each source
            - pricing_points: count of available pricing points
            - data: dict of source -> actual pricing data (placeholder for now)
    """
    sources = extract_pricing_sources(
        psa_url=psa_url,
        sportscardspro_url=sportscardspro_url,
        ebay_url=ebay_url,
        pricecharting_url=pricecharting_url,
    )

    strategy = get_lookup_strategy(sources)
    pricing_points = count_pricing_points(sources)

    return {
        'card_id': card_id,
        'strategy': strategy,
        'sources': sources,
        'pricing_points': pricing_points,
        'fallback_query': search_query,
        # Placeholder for actual API calls — will be filled in by integration
        'data': {},
    }


# ============================================================================
# Self-tests
# ============================================================================

def _self_test():
    test_cases = [
        # (description, args, expected_mode, expected_pricing_points)
        (
            "PSA URL only",
            dict(
                card_id=1,
                search_query='Hank Aaron 1969 Topps',
                psa_url='https://www.psacard.com/pop/baseball-cards/1969/topps-stamps/51060',
            ),
            'url_first',
            1,
        ),
        (
            "All 4 URLs",
            dict(
                card_id=2,
                search_query='Michael Jordan Fleer',
                psa_url='https://www.psacard.com/pop/baseball-cards/1986/fleer/72584',
                sportscardspro_url='https://www.sportscardspro.com/product/72584-michael-jordan',
                ebay_url='https://www.ebay.com/itm/123456789',
                pricecharting_url='https://www.pricecharting.com/console/1986-fleer-mj-72584',
            ),
            'url_first',
            4,
        ),
        (
            "No URLs (search only)",
            dict(
                card_id=3,
                search_query='Bo Jackson',
            ),
            'search_only',
            0,
        ),
        (
            "Bad URL (invalid format)",
            dict(
                card_id=4,
                search_query='Frank Thomas',
                psa_url='https://example.com/random',
            ),
            'search_only',
            0,
        ),
        (
            "eBay item URL only",
            dict(
                card_id=5,
                search_query='Charizard Base',
                ebay_url='https://www.ebay.com/itm/987654321',
            ),
            'url_first',
            1,
        ),
    ]

    passed = 0
    failed = 0

    for description, kwargs, expected_mode, expected_points in test_cases:
        result = lookup_card_pricing(**kwargs)
        actual_mode = result['strategy']['mode']
        actual_points = result['pricing_points']

        if actual_mode == expected_mode and actual_points == expected_points:
            passed += 1
            print(f"  [OK] {description:30} | mode={actual_mode}, points={actual_points}")
        else:
            failed += 1
            print(f"  [FAIL] {description}")
            print(f"         expected: mode={expected_mode}, points={expected_points}")
            print(f"         got:      mode={actual_mode}, points={actual_points}")
            print(f"         strategy: {result['strategy']['reason']}")

    print()
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)}")
    return failed == 0


if __name__ == '__main__':
    import sys
    success = _self_test()
    sys.exit(0 if success else 1)
