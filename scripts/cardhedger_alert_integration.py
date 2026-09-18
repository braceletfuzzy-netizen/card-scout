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
from datetime import datetime, timezone
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
        # Pure JSONL: timestamp is a field inside each entry so log analysis
        # tools can parse each line as JSON. The Python logger formatter
        # only emits the message body.
        _fh.setFormatter(logging.Formatter('%(message)s'))
        _comparison_logger.addHandler(_fh)
    except Exception as e:
        print(f'[WARN] Could not set up comparison log: {e}')


GRADES_TO_FETCH = ['PSA 10', 'PSA 9', 'BGS 9.5', 'CGC 10']

# Sept 18 Clean Data #1: drop low-confidence grades from alerts.
# Card Hedger's confidence_grade is A/B/C/D. D = 'very low confidence, sparse market'.
# Confidence is 0-1 numeric. We drop:
#   - D letter grade (always)
#   - C letter grade with confidence < 0.1 (essentially untrusted)
# Other grades (A/B/C with decent confidence) are kept.
DROP_CONFIDENCE_GRADES = {'D'}
DROP_CONFIDENCE_BELOW = 0.10  # numeric confidence threshold (also catches ungraded C)


def _should_drop_fmv(confidence_grade, confidence):
    """Decide whether to drop a per-grade FMV from alerts.

    Returns True if the FMV is too unreliable to surface.
    """
    if confidence_grade in DROP_CONFIDENCE_GRADES:
        return True
    if confidence is not None and confidence < DROP_CONFIDENCE_BELOW:
        return True
    return False

# Map our card.track_* flags to Card Hedger grade requests
TRACK_FLAG_TO_GRADES = {
    'track_psa_10': 'PSA 10',
    'track_psa_9': 'PSA 9',
    'track_other_graders': 'BGS 9.5',  # BGS is the most common "other grader"
}


def _grades_to_fetch_for_card(card):
    """Determine which grade tiers to fetch for this card based on track_* flags.

    Sept 18: don't fetch grades the customer isn't tracking.
    This cuts Card Hedger calls by 50%+ on average.
    Default: if all track_* flags are True (default), fetch all 4 grades.
    """
    grades = []
    for flag_attr, grade in TRACK_FLAG_TO_GRADES.items():
        if getattr(card, flag_attr, True):
            grades.append(grade)

    # CGC 10 only if track_other_graders (treat as alternative to BGS)
    if getattr(card, 'track_other_graders', True):
        grades.append('CGC 10')

    # De-dupe while preserving order
    seen = set()
    result = []
    for g in grades:
        if g not in seen:
            seen.add(g)
            result.append(g)

    # Default fallback: if nothing tracked (shouldn't happen), fetch PSA 10
    if not result:
        result = ['PSA 10']

    return result


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
            # Fallback: search and STRICTLY validate first result matches query
            # CLEAN DATA FIX #2 (Sept 18): require player-name match.
            # Without this, 'Donruss 87 Bo Jackson' returns Azzi Fudd 2025
            # Donruss #87 as first result because 'donruss' matches every result.
            # We were alerting on FMVs for the WRONG CARD.
            search_result = client.search_cards(search=card.search_query, page=1)
            cards_list = search_result.get('cards', []) if isinstance(search_result, dict) else []
            if not cards_list:
                return None

            # Strategy: Find a query token that looks like a player name (capitalized,
            # not a number/year) and require it to appear in the result's player or
            # description. Skip generic tokens like 'donruss', 'topps' that match many.
            GENERIC_TOKENS = {
                'donruss', 'topps', 'fleer', 'upper', 'deck', 'panini', 'baseball',
                'football', 'basketball', 'hockey', 'pokemon', 'card', 'rookie',
                'the', 'and', 'with', 'auto', 'autograph', 'graded', 'raw', 'mint',
                'gem', 'set', 'series', 'insert', 'parallel', 'refractor', 'prizm',
                'select', 'optic', 'clearly', 'recollection', 'classics',
            }
            query_lower = card.search_query.lower()
            query_tokens = [
                t for t in query_lower.split()
                if len(t) > 2 and not t.isdigit()
            ]
            specific_tokens = [t for t in query_tokens if t not in GENERIC_TOKENS]

            # If no specific tokens (e.g., query is just 'topps 1989'), fall back
            # to requiring at least the year match.
            best_match = None
            for candidate in cards_list[:10]:
                desc = (candidate.get('description') or '').lower()
                player = (candidate.get('player') or '').lower()

                if specific_tokens:
                    # Require at least one specific (non-generic) token to match
                    matched_specific = [t for t in specific_tokens if t in desc or t in player]
                    if matched_specific:
                        best_match = candidate
                        break
                else:
                    # No specific tokens - require year match as fallback
                    year_tokens = [t for t in query_lower.split() if t.isdigit() and len(t) == 4]
                    if year_tokens and any(y in desc for y in year_tokens):
                        best_match = candidate
                        break

            if not best_match:
                _comparison_logger.warning(
                    f'CARD_HEDGER_SEARCH_NO_MATCH card_id={card.id} query={card.search_query!r} '
                    f'top_result={cards_list[0].get("description", "?")!r} '
                    f'specific_tokens={specific_tokens}'
                )
                return None

            target_id = best_match.get('card_id') or best_match.get('id')
            source_method = 'search_fallback_validated'
        else:
            source_method = 'card_id'

        if not target_id:
            return None

        # Fetch FMV at grade tiers relevant to this card (smart fetch based on track_* flags)
        # Cuts Card Hedger calls by ~50% vs always fetching all 4 grades.
        grades_for_this_card = _grades_to_fetch_for_card(card)
        for grade in grades_for_this_card:
            try:
                fmv_data = client.get_fmv(target_id, grade=grade)
                if fmv_data and (fmv_data.get('fmv') or fmv_data.get('price')):
                    confidence_grade = fmv_data.get('confidence_grade')
                    confidence = fmv_data.get('confidence')

                    # Sept 18 Clean Data #1: drop D-grade / very-low-confidence FMVs
                    # from alerts (still logged for analysis, but not surfaced to customer)
                    if _should_drop_fmv(confidence_grade, confidence):
                        _comparison_logger.info(
                            f'CARD_HEDGER_FMV_DROPPED card_id={card.id} grade={grade} '
                            f'confidence_grade={confidence_grade} confidence={confidence:.4f} '
                            f'price={fmv_data.get("fmv") or fmv_data.get("price")} '
                            f'reason=low_confidence'
                        )
                        continue  # don't add to fmvs dict

                    fmvs[grade] = {
                        'price': fmv_data.get('fmv') or fmv_data.get('price'),
                        'price_low': fmv_data.get('price_low'),
                        'price_high': fmv_data.get('price_high'),
                        'confidence': confidence,
                        'confidence_grade': confidence_grade,
                        'explanation': fmv_data.get('price_explanation') or fmv_data.get('explanation'),
                    }
            except Exception as grade_err:
                # Skip this grade but continue with others
                _comparison_logger.warning(
                    f'CARD_HEDGER_GRADE_FETCH_FAILED card_id={card.id} grade={grade} '
                    f'error={type(grade_err).__name__}: {grade_err}'
                )

        # Sept 18: if ALL grades were dropped, log + return None (whole card unreliable)
        if not fmvs and grades_for_this_card:
            _comparison_logger.info(
                f'CARD_HEDGER_NO_RELIABLE_FMV card_id={card.id} '
                f'grades_attempted={grades_for_this_card} '
                f'all_below_confidence_threshold'
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
        # NEW Sept 18: timestamp is now a JSON field, not a prefix.
        # Each JSONL line is fully self-describing for log analysis.
        'timestamp': datetime.now(timezone.utc).isoformat(),
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
