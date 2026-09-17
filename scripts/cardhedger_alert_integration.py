"""
Card Hedger dual-source integration for Card Scout alert pipeline.

Sept 17: Adds Card Hedger as a parallel price source to compare against
SCPro Apify for 1 week. Logs discrepancies to /data/card_hedger_vs_scpro.log.
At week mark, decide which source to keep based on data quality.

Usage:
  from cardhedger_alert_integration import fetch_card_hedger_data, log_comparison

  ch_data = fetch_card_hedger_data(card)
  scpro_stats = ... existing SCPro data ...
  log_comparison(card, ch_data, scpro_stats)
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent))
from cardhedger_client import CardHedgerClient

# Set up comparison logger
_log_dir = '/data' if os.path.isdir('/data') else '.'
_log_path = os.path.join(_log_dir, 'card_hedger_vs_scpro.log')

_comparison_logger = logging.getLogger('card_hedger_vs_scpro')
_comparison_logger.setLevel(logging.INFO)
if not _comparison_logger.handlers:
    try:
        _fh = logging.FileHandler(_log_path)
        _fh.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        _comparison_logger.addHandler(_fh)
    except Exception as e:
        print(f'[WARN] Could not set up comparison log: {e}')


def fetch_card_hedger_data(card):
    """Fetch price/sales data for a card from Card Hedger.

    Uses card.card_id if set (from the inline matcher), otherwise falls back
    to a search via card.search_query.

    Returns dict with keys matching SCPro snapshot stats shape:
      median_price, avg_price, min_price, max_price, total_listings,
      items_with_sold_count, total_sold_reported, hot_items_count, avg_sold_count

    Returns None if Card Hedger call fails (rate limit, no match, etc.).
    """
    client = CardHedgerClient()

    try:
        # Strategy 1: Use the matched card_id (preferred) — get FMV at PSA 10
        if card.card_id:
            fmv_data = client.get_fmv(card.card_id, grade='PSA 10')
            if fmv_data and (fmv_data.get('fmv') or fmv_data.get('price')):
                price = fmv_data.get('fmv') or fmv_data.get('price')
                return {
                    'source': 'cardhedger',
                    'method': 'card_id_fmv_psa10',
                    'median_price': price,
                    'avg_price': price,
                    'min_price': fmv_data.get('price_low'),
                    'max_price': fmv_data.get('price_high'),
                    'total_listings': 1,
                    'items_with_sold_count': 1,
                    'total_sold_reported': 1,
                    'hot_items_count': 0,
                    'avg_sold_count': 1.0,
                    'card_hedger_confidence': fmv_data.get('confidence'),
                    'card_hedger_grade': fmv_data.get('confidence_grade'),
                    'card_hedger_explanation': fmv_data.get('price_explanation') or fmv_data.get('explanation'),
                    'raw_response': fmv_data,
                }

        # Strategy 2: Fallback to search and use first card's FMV
        search_result = client.search_cards(search=card.search_query, page=1)
        cards_list = search_result.get('cards', []) if isinstance(search_result, dict) else []
        if not cards_list:
            return None

        # Take the first card (best match)
        first = cards_list[0]
        first_id = first.get('card_id') or first.get('id')
        if not first_id:
            return None

        fmv_data = client.get_fmv(first_id, grade='PSA 10')
        if fmv_data and (fmv_data.get('fmv') or fmv_data.get('price')):
            price = fmv_data.get('fmv') or fmv_data.get('price')
            return {
                'source': 'cardhedger',
                'method': 'search_fallback',
                'median_price': price,
                'avg_price': price,
                'min_price': fmv_data.get('price_low'),
                'max_price': fmv_data.get('price_high'),
                'total_listings': 1,
                'items_with_sold_count': 1,
                'total_sold_reported': 1,
                'hot_items_count': 0,
                'avg_sold_count': 1.0,
                'card_hedger_confidence': fmv_data.get('confidence'),
                'card_hedger_grade': fmv_data.get('confidence_grade'),
                'raw_response': fmv_data,
            }

        return None
    except Exception as e:
        _comparison_logger.warning(f'CARD_HEDGER_FETCH_FAILED card_id={card.id} query={card.search_query!r} error={type(e).__name__}: {e}')
        return None


def log_comparison(card, ch_data, scpro_stats):
    """Log a comparison of Card Hedger vs SCPro data for a card.

    Both inputs should have the standard snapshot stats shape.
    Logs to /data/card_hedger_vs_scpro.log for week-long comparison.
    """
    ch_price = (ch_data or {}).get('median_price')
    sc_price = (scpro_stats or {}).get('median_price')

    # Compute % difference
    pct_diff = None
    if ch_price and sc_price and sc_price > 0:
        pct_diff = (ch_price - sc_price) / sc_price * 100

    log_entry = {
        'card_id': card.id,
        'search_query': card.search_query,
        'card_hedger_price': ch_price,
        'scpro_price': sc_price,
        'pct_difference': pct_diff,
        'card_hedger_source': (ch_data or {}).get('method') if ch_data else 'NO_DATA',
        'card_hedger_confidence': (ch_data or {}).get('card_hedger_confidence'),
        'card_hedger_grade': (ch_data or {}).get('card_hedger_grade'),
        'scpro_total_listings': (scpro_stats or {}).get('total_listings'),
    }
    _comparison_logger.info(json.dumps(log_entry))

    return log_entry


def fetch_with_fallback(card):
    """Try Card Hedger first, fall back to SCPro if it fails.

    This is the function the alert pipeline should call. Returns:
      (stats_dict, source_label) where source_label is 'cardhedger' or 'scpro'
    """
    # Try Card Hedger
    ch_data = fetch_card_hedger_data(card)
    if ch_data and ch_data.get('median_price'):
        return ch_data, 'cardhedger'

    # Fall back to SCPro (caller handles this)
    return None, 'cardhedger_failed'
