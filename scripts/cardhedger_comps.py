"""
Fetch Card Hedger comps (recent sold sales) per card.

Sept 18: Wiring CH comps into the alert pipeline so all customers
(not just Jim) get sold-data signals. Until eBay Browse API is approved,
this is our primary sold-data source.

Cost: 1 API call per card (PSA 10 comps only — other grades too expensive
given Starter tier 10 req/min limit).

Returns: dict with comp_price (median), high, low, count_used
"""
import json
from pathlib import Path

from cardhedger_client import CardHedgerClient

_comps_log_path = Path('/data/card_hedger_comps.log')
try:
    _comps_log_path.parent.mkdir(parents=True, exist_ok=True)
except Exception:
    _comps_log_path = Path('card_hedger_comps.log')  # local fallback

import logging
_comps_logger = logging.getLogger('card_hedger_comps')
if not _comps_logger.handlers:
    handler = logging.FileHandler(_comps_log_path)
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    _comps_logger.addHandler(handler)
    _comps_logger.setLevel(logging.INFO)


def fetch_card_hedger_comps(card, grade: str = 'PSA 10', count: int = 10):
    """Fetch recent sold comps from Card Hedger for a card.

    Sept 18: this is our sold-data source until eBay Browse API is approved.
    Returns REAL sale prices (not a vendor's smoothed opinion like FMV).

    Args:
        card: Card SQLAlchemy model with potentially card_id set
        grade: which grade tier to fetch comps for (default PSA 10 — most relevant)
        count: number of comps to fetch (1-100, default 10)

    Returns:
        dict with comp_price, high, low, count_used, source_method
        None if no comps available or fetch fails
    """
    client = CardHedgerClient()
    target_id = None

    try:
        # Reuse same card_id resolution as fetch_card_hedger_data
        if card.card_id:
            target_id = card.card_id
            source_method = 'card_id'
        else:
            # Search fallback (same pattern as FMV fetch)
            search_result = client.search_cards(search=card.search_query, page=1)
            cards_list = search_result.get('cards', []) if isinstance(search_result, dict) else []
            if not cards_list:
                return None
            target_id = cards_list[0].get('card_id') or cards_list[0].get('id')
            source_method = 'search_fallback'

        if not target_id:
            return None

        comps = client.get_comps(
            card_id=target_id,
            grade=grade,
            count=count,
            time_weighted=False,  # Equal-weight all sales in window
        )

        if not comps or not comps.get('count_used'):
            return None

        result = {
            'source': 'cardhedger_comps',
            'method': source_method,
            'grade': grade,
            'comp_price': comps.get('comp_price'),
            'high': comps.get('high'),
            'low': comps.get('low'),
            'count_used': comps.get('count_used'),
            'count_requested': comps.get('count_requested'),
            'raw_high': comps.get('raw_high'),
            'raw_low': comps.get('raw_low'),
        }

        _comps_logger.info(json.dumps({
            'card_id': card.id,
            'search_query': card.search_query,
            'grade': grade,
            'source_method': source_method,
            'comp_price': result['comp_price'],
            'high': result['high'],
            'low': result['low'],
            'count_used': result['count_used'],
        }))

        return result

    except Exception as e:
        _comps_logger.warning(
            f'CARD_HEDGER_COMPS_FAILED card_id={card.id} grade={grade} '
            f'error={type(e).__name__}: {e}'
        )
        return None
