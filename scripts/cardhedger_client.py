"""Card Hedge API client for Card Scout.

USAGE:
    from cardhedger_client import CardHedgerClient
    client = CardHedgerClient()  # reads CARD_HEDGER_API_KEY from env

    # Search for cards
    results = client.search_cards(search='Bo Jackson', category='Baseball')
    # Returns list of card dicts with 'card_id', 'name', 'set_name', etc.

    # Get FMV (Fair Market Value) for a specific card
    fmv = client.get_fmv(card_id='abc123', grade='PSA 10')
    # Returns dict with 'fmv', 'confidence', etc.

ENV:
    CARD_HEDGER_API_KEY: API key from https://ai.cardhedger.com/api-services
    Optional: CARD_HEDGER_BASE_URL (default: https://api.cardhedger.com)

SUBSCRIPTION:
    Card Hedger subscription $14.99/mo or $49/mo (per pricing Sept 17).
    Sign up at https://ai.cardhedger.com, then enable API access in dashboard.

DESIGN NOTES (Sept 17):
    - Thin wrapper around REST endpoints we actually use, NOT a full client
    - Methods return parsed JSON or raise CardHedgerError
    - Auth: X-API-Key header (Card Hedge convention)
    - Endpoints implemented:
        search_cards         POST /v1/cards/card-search
        card_details         POST /v1/cards/card-details
        get_fmv              POST /v1/cards/card-fmv
        get_price_history    POST /v1/cards/prices-by-card
        get_comps            POST /v1/cards/comps
        details_by_certs     POST /v1/cards/details-by-certs
        price_history_by_cert POST /v1/cards/prices-by-cert
        fmv_by_cert          POST /v1/cards/fmv-by-cert
        total_sales_by_player POST /v1/cards/total-sales-by-player
        top_movers           GET  /v1/cards/top-movers
    - Endpoints NOT implemented (can add later if needed):
        population-by-* (GemRate contract required — not available)
        image-match, image-search (we have URLs, not images)
        set-search, player-search (not needed for current use case)

RETRY POLICY:
    - 3 retries on 5xx and connection errors (exponential backoff 1s, 2s, 4s)
    - No retry on 4xx (client error, fix the request)
    - Rate limit (429) → 60s wait then 1 retry
"""
import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

import requests

# Load .env if python-dotenv available
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass

logger = logging.getLogger(__name__)

BASE_URL = os.getenv('CARD_HEDGER_BASE_URL', 'https://api.cardhedger.com').rstrip('/')


class CardHedgerError(Exception):
    """Raised when Card Hedge API returns an error or unexpected response."""
    def __init__(self, message, status_code=None, response_body=None, endpoint=None):
        self.status_code = status_code
        self.response_body = response_body
        self.endpoint = endpoint
        super().__init__(message)


class CardHedgerClient:
    """Thin Python client for the Card Hedge REST API.

    Read auth key from CARD_HEDGER_API_KEY env var by default. Pass explicitly
    via api_key= for testing.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        self.api_key = api_key or os.getenv('CARD_HEDGER_API_KEY')
        if not self.api_key:
            raise CardHedgerError(
                'CARD_HEDGER_API_KEY not set. Sign up at https://ai.cardhedger.com '
                'and set the env var in .env'
            )
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'CardScout/1.0 (+https://cardscout.pro)',
        })

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST to Card Hedge with retry on 5xx."""
        url = f'{BASE_URL}{path}'
        last_err = None
        for attempt in range(4):
            try:
                resp = self.session.post(url, json=payload, timeout=self.timeout)
                if resp.status_code == 429:
                    # Rate limit
                    wait = 60
                    logger.warning(f'Rate limited on {path}, waiting {wait}s')
                    time.sleep(wait)
                    last_err = CardHedgerError(f'Rate limited on {path}', 429, resp.text, path)
                    continue
                if 500 <= resp.status_code < 600:
                    # Server error, retry
                    wait = 2 ** attempt
                    logger.warning(f'Server error {resp.status_code} on {path}, retry in {wait}s (attempt {attempt+1}/4)')
                    time.sleep(wait)
                    last_err = CardHedgerError(f'HTTP {resp.status_code}', resp.status_code, resp.text, path)
                    continue
                if resp.status_code >= 400:
                    # Client error, don't retry
                    try:
                        body = resp.json()
                    except Exception:
                        body = resp.text
                    raise CardHedgerError(
                        f'HTTP {resp.status_code} from {path}: {body}',
                        resp.status_code, body, path
                    )
                # Success
                return resp.json()
            except requests.exceptions.RequestException as e:
                last_err = CardHedgerError(f'Request failed: {e}', endpoint=path)
                wait = 2 ** attempt
                logger.warning(f'Request error on {path}: {e}, retry in {wait}s')
                time.sleep(wait)
        raise last_err

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET to Card Hedge with retry on 5xx."""
        url = f'{BASE_URL}{path}'
        last_err = None
        for attempt in range(4):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                if resp.status_code == 429:
                    wait = 60
                    logger.warning(f'Rate limited on {path}, waiting {wait}s')
                    time.sleep(wait)
                    last_err = CardHedgerError(f'Rate limited on {path}', 429, resp.text, path)
                    continue
                if 500 <= resp.status_code < 600:
                    wait = 2 ** attempt
                    logger.warning(f'Server error {resp.status_code} on {path}, retry in {wait}s')
                    time.sleep(wait)
                    last_err = CardHedgerError(f'HTTP {resp.status_code}', resp.status_code, resp.text, path)
                    continue
                if resp.status_code >= 400:
                    try:
                        body = resp.json()
                    except Exception:
                        body = resp.text
                    raise CardHedgerError(
                        f'HTTP {resp.status_code} from {path}: {body}',
                        resp.status_code, body, path
                    )
                return resp.json()
            except requests.exceptions.RequestException as e:
                last_err = CardHedgerError(f'Request failed: {e}', endpoint=path)
                wait = 2 ** attempt
                time.sleep(wait)
        raise last_err

    # ========================================================================
    # SEARCH & DISCOVERY
    # ========================================================================

    def search_cards(self,
                     search: Optional[str] = None,
                     set_name: Optional[str] = None,
                     category: Optional[str] = None,
                     player: Optional[str] = None,
                     number: Optional[str] = None,
                     subset: Optional[str] = None,
                     rookie: Optional[str] = None,
                     page: int = 1) -> Dict[str, Any]:
        """Search Card Hedge's catalog.

        Returns the raw API response (includes 'cards' list, 'total', 'page').

        Examples:
            results = client.search_cards(search='Bo Jackson', category='Baseball')
            results = client.search_cards(player='Michael Jordan', subset='Base Set')
        """
        payload = {k: v for k, v in {
            'search': search,
            'set': set_name,
            'category': category,
            'player': player,
            'number': number,
            'subset': subset,
            'rookie': rookie,
            'page': page,
        }.items() if v is not None}
        return self._post('/v1/cards/card-search', payload)



    def search_cards_wsort(
        self,
        search: Optional[str] = None,
        set_name: Optional[str] = None,
        category: Optional[str] = None,
        player: Optional[str] = None,
        number: Optional[str] = None,
        subset: Optional[str] = None,
        rookie: Optional[str] = None,
        sort_by: str = 'relevance',  # relevance | price | sales | recent
        sort_order: str = 'desc',
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """Search cards with structured params + sorting.

        Used by inline search UX (PL-008): customer picks player/year/set
        instead of typing free-form queries.

        Args:
            search: free-text query (combined with structured filters)
            set_name: e.g., "Topps", "Bowman Chrome"
            category: e.g., "Baseball", "Basketball", "Pokemon"
            player: e.g., "Mike Trout", "Michael Jordan"
            number: card number (e.g., "1", "US26")
            subset: subset/parallels (e.g., "Chrome", "Refractor")
            rookie: "true" to filter rookies only
            sort_by: relevance (default), price, sales, recent
            sort_order: desc (default) | asc
            page: 1-indexed page number
            page_size: results per page (default 20, max 100)

        Returns:
            dict with cards[], pages, count
        """
        params = {
            'page': page,
            'pageSize': page_size,
            'sortBy': sort_by,
            'sortOrder': sort_order,
        }
        if search:
            params['search'] = search
        if set_name:
            params['set'] = set_name
        if category:
            params['category'] = category
        if player:
            params['player'] = player
        if number:
            params['number'] = number
        if subset:
            params['subset'] = subset
        if rookie:
            params['rookie'] = rookie

        return self._post('/v1/cards/search-cards-wsort', payload=params)

    def card_details(self, card_id: str) -> Dict[str, Any]:
        """Get full details for a single card by Card Hedge card_id."""
        return self._post('/v1/cards/card-details', {'card_id': card_id})

    def details_by_certs(self, certs: List[str], grader: str = 'PSA') -> Dict[str, Any]:
        """Batch cert lookup (max 100 certs)."""
        if len(certs) > 100:
            raise CardHedgerError(f'Max 100 certs per batch (got {len(certs)})')
        return self._post('/v1/cards/details-by-certs', {
            'certs': certs,
            'grader': grader,
        })

    # ========================================================================
    # PRICING & VALUATION
    # ========================================================================

    def get_fmv(self, card_id: str, grade: str) -> Dict[str, Any]:
        """Get Fair Market Value (FMV) with confidence grade.

        grade format: 'PSA 10', 'BGS 9.5', 'CGC 10', 'SGC 10', etc.
        Returns: {fmv, confidence, explanation, last_updated, ...}
        """
        return self._post('/v1/cards/card-fmv', {
            'card_id': card_id,
            'grade': grade,
        })

    def get_price_history(self,
                          card_id: str,
                          grade: str,
                          days: int = 30,
                          end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get price history for a card+grade.

        days: 1-366 (default 30)
        end_date: optional YYYY-MM-DD, defaults to today
        """
        payload = {'card_id': card_id, 'grade': grade, 'days': days}
        if end_date:
            payload['end_date'] = end_date
        return self._post('/v1/cards/prices-by-card', payload)

    def get_comps(self,
                  card_id: str,
                  grade: str,
                  count: int = 20,
                  time_weighted: bool = False,
                  include_raw_prices: bool = False) -> Dict[str, Any]:
        """Get comparable sales (comps) for a card.

        count: 1-100 comps
        time_weighted: weight recent sales more (WMA algorithm)
        """
        return self._post('/v1/cards/comps', {
            'card_id': card_id,
            'grade': grade,
            'count': count,
            'time_weighted': time_weighted,
            'include_raw_prices': include_raw_prices,
        })

    def price_history_by_cert(self, cert: str, grader: str = 'PSA', days: int = 180) -> Dict[str, Any]:
        """Get price history by cert number (uses GemRate cache when available)."""
        return self._post('/v1/cards/prices-by-cert', {
            'cert': cert,
            'grader': grader,
            'days': days,
        })

    def fmv_by_cert(self, cert: str, grader: str = 'PSA') -> Dict[str, Any]:
        """Get FMV by cert number (convenience wrapper)."""
        return self._post('/v1/cards/fmv-by-cert', {
            'cert': cert,
            'grader': grader,
        })

    # ========================================================================
    # ANALYTICS
    # ========================================================================

    def total_sales_by_player(self, player: str, days: int = 30) -> Dict[str, Any]:
        """Total sales count for a player over a time window."""
        return self._post('/v1/cards/total-sales-by-player', {
            'player': player,
            'days': days,
        })

    def top_movers(self, count: int = 20, category: Optional[str] = None) -> Dict[str, Any]:
        """Get top movers (weekly price gainers)."""
        params = {'count': count}
        if category:
            params['category'] = category
        return self._get('/v1/cards/top-movers', params=params)

    # ========================================================================
    # HEALTH CHECK
    # ========================================================================

    def ping(self) -> bool:
        """Verify API key is valid by hitting a cheap endpoint."""
        try:
            # top-movers is unauth-friendly and cheap
            self.top_movers(count=1)
            return True
        except CardHedgerError as e:
            if e.status_code in (401, 403):
                return False
            raise


# ============================================================================
# CLI for quick testing
# ============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Test Card Hedge API client')
    parser.add_argument('--search', help='Search query (e.g. "Bo Jackson")')
    parser.add_argument('--player', help='Player name filter')
    parser.add_argument('--fmv', help='Get FMV for card_id (use with --grade)')
    parser.add_argument('--grade', default='PSA 10', help='Grade label (default: PSA 10)')
    parser.add_argument('--ping', action='store_true', help='Just ping the API')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    try:
        client = CardHedgerClient()
    except CardHedgerError as e:
        print(f'[ERROR] {e}', file=sys.stderr)
        sys.exit(1)

    try:
        if args.ping:
            ok = client.ping()
            print(f'Ping: {"OK" if ok else "FAILED (401/403)"}')
        elif args.search or args.player:
            results = client.search_cards(search=args.search, player=args.player)
            indent = 2 if args.pretty else None
            print(json.dumps(results, indent=indent))
        elif args.fmv:
            result = client.get_fmv(card_id=args.fmv, grade=args.grade)
            indent = 2 if args.pretty else None
            print(json.dumps(result, indent=indent))
        else:
            parser.print_help()
            sys.exit(1)
    except CardHedgerError as e:
        print(f'[ERROR] {e}', file=sys.stderr)
        if e.status_code:
            print(f'Status: {e.status_code}', file=sys.stderr)
        if e.response_body:
            print(f'Body: {e.response_body}', file=sys.stderr)
        sys.exit(2)
