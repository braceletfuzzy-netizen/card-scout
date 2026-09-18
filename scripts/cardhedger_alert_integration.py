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


GRADES_TO_FETCH = ['PSA 10', 'PSA 9', 'BGS 9.5', 'CGC 10']


def fetch_card_hedger_data(card):
    """Fetch FMV at MULTIPLE grade tiers from Card Hedger.

    Per Sept 18 insight: each grade tier is its own market. PSA 10 FMV
    is meaningless when comparing to a PSA 9 listing. So we fetch all
    major grade tiers for each card.

    Grades fetched: PSA 10, PSA 9, BGS 9.5, CGC 10 (4 grades)
    Cost: 4 Card Hedger calls per card per run (within Starter 10/min limit
    if we have <= 2 cards/min)

    Returns dict with keys:
      source, method, fmvs (dict of grade -> FMV data), confidence grades
      For backward compat: median_price = PSA 10 FMV if available, else BGS 9.5
    """
    client = CardHedgerClient()

    fmvs = {}  # grade -> fmv_data
    card_id_used = None

    try:
        # Use card_id if matched (preferred), else search
        target_id = card.card_id
        source_method = None

        if not target_id:
            # Fallback: search and use first result
            search_result = client.search_cards(search=card.search_query, page=1)
            cards_list = search_result.get('cards', []) if isinstance(search_result, dict) else []
            if not cards_list:
                return None
            target_id = cards_list[0].get('card_id') or cards_list[0].get('id')
            source_method = 'search_fallback'
        else:
            source_method = 'card_id'

        if not target_id:
            return None

        # Fetch FMV at all major grade tiers
        for grade in GRADES_TO_FETCH:
            try:
                fmv_data = client.get_fmv(target_id, grade=grade)
                if fmv_data and (fmv_data.get('fmv') or fmv_data.get('price')):
                    fmvs[grade] = {
                        'price': fmv_data.get('fmv') or fmv_data.get('price'),
                        'price_low': fmv_data.get('price_low'),
                        'price_high': fmv_data.get('price_high'),
                        'confidence': fmv_data.get('confidence'),
                        'confidence_grade': fmv_data.get('confidence_grade'),
                        'explanation': fmv_data.get('price_explanation') or fmv_data.get('explanation'),
                    }
            except Exception as grade_err:
                # Skip this grade but continue with others
                _comparison_logger.warning(
                    f'CARD_HEDGER_GRADE_FETCH_FAILED card_id={card.id} grade={grade} '
                    f'error={type(grade_err).__name__}: {grade_err}'
                )

        if not fmvs:
            return None

        # Backward compat: median_price = PSA 10 (or fallback to BGS 9.5)
        psa10 = fmvs.get('PSA 10', {})
        bgs95 = fmvs.get('BGS 9.5', {})

        median_price = psa10.get('price') or bgs95.get('price')
        avg_price = median_price
        min_price = min((f.get('price_low') for f in fmvs.values() if f.get('price_low')), default=None)
        max_price = max((f.get('price_high') for f in fmvs.values() if f.get('price_high')), default=None)

        # Overall confidence = best (highest) of the grades fetched
        best_grade = max(fmvs.items(), key=lambda kv: kv[1].get('confidence') or 0)
        overall_confidence = best_grade[1].get('confidence')
        overall_confidence_grade = best_grade[1].get('confidence_grade')

        return {
            'source': 'cardhedger',
            'method': source_method,
            'fmvs': fmvs,  # NEW: per-grade FMVs (Sept 18 insight)
            'median_price': median_price,  # PSA 10 for backward compat
            'avg_price': avg_price,
            'min_price': min_price,
            'max_price': max_price,
            'total_listings': 1,
            'items_with_sold_count': 1,
            'total_sold_reported': 1,
            'hot_items_count': 0,
            'avg_sold_count': 1.0,
            'card_hedger_confidence': overall_confidence,
            'card_hedger_grade': overall_confidence_grade,
            'card_hedger_explanation': best_grade[1].get('explanation'),
        }

    except Exception as e:
        _comparison_logger.warning(f'CARD_HEDGER_FETCH_FAILED card_id={card.id} query={card.search_query!r} error={type(e).__name__}: {e}')
        return None


def log_comparison(card, ch_data, scpro_stats):
    """Log a comparison of Card Hedger vs SCPro data for a card.

    Both inputs should have the standard snapshot stats shape.
    Logs to /data/card_hedger_vs_scpro.log for week-long comparison.

    Per Sept 18: now logs per-grade FMV (PSA 10, PSA 9, BGS 9.5, CGC 10)
    since each grade tier is its own market.
    """
    ch_price = (ch_data or {}).get('median_price')
    sc_price = (scpro_stats or {}).get('median_price')

    # Compute % difference (overall, uses median_price = PSA 10 for back compat)
    pct_diff = None
    if ch_price and sc_price and sc_price > 0:
        pct_diff = (ch_price - sc_price) / sc_price * 100

    # Per-grade breakdown
    per_grade_fmvs = (ch_data or {}).get('fmvs', {})
    per_grade_summary = {
        grade: {
            'ch_price': fmv.get('price'),
            'ch_confidence': fmv.get('confidence'),
            'ch_grade': fmv.get('confidence_grade'),
        }
        for grade, fmv in per_grade_fmvs.items()
    }

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
        # NEW per-grade (Sept 18)
        'card_hedger_fmvs': per_grade_summary,
        'grades_fetched': list(per_grade_fmvs.keys()),
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
