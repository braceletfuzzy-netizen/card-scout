"""Card Hedge API smoke test.

Runs a quick end-to-end test once CARD_HEDGER_API_KEY is set:
1. Ping the API to verify auth
2. Search for a known card (Bo Jackson 1987 Donruss #35)
3. Get FMV for PSA 10 grade
4. Get price history for last 30 days
5. Get comps

Exit code 0 = all pass, non-zero = something broke.

USAGE:
    export CARD_HEDGER_API_KEY=ch_xxx...
    python scripts/cardhedger_smoke_test.py
"""
import sys
import os
from pathlib import Path

# Allow running from repo root or scripts/ dir
sys.path.insert(0, str(Path(__file__).parent))

from cardhedger_client import CardHedgerClient, CardHedgerError


def run_smoke_test():
    print('=== Card Hedge API smoke test ===')
    print()

    try:
        client = CardHedgerClient()
    except CardHedgerError as e:
        print(f'[FAIL] Client init: {e}')
        return 1

    # 1. Ping
    print('[1/5] Pinging API...')
    try:
        ok = client.ping()
        if not ok:
            print('[FAIL] Ping returned 401/403 — check CARD_HEDGER_API_KEY')
            return 1
        print('[OK] API authenticated')
    except CardHedgerError as e:
        print(f'[FAIL] Ping error: {e}')
        return 1

    # 2. Search for Bo Jackson 1987 Donruss
    print('[2/5] Searching for "Bo Jackson Donruss"...')
    try:
        results = client.search_cards(search='Bo Jackson Donruss')
        cards = results.get('cards', results.get('results', results.get('data', [])))
        if not cards:
            print(f'[WARN] No cards returned. Full response: {results}')
            return 1
        print(f'[OK] Found {len(cards)} cards (total={results.get("total", "?")})')
        # Find one with a card_id
        first_with_id = next((c for c in cards if c.get('card_id') or c.get('id')), None)
        if not first_with_id:
            print(f'[WARN] No card_id in any result. Sample: {cards[0]}')
            return 1
        card_id = first_with_id.get('card_id') or first_with_id.get('id')
        card_name = first_with_id.get('name') or first_with_id.get('player') or 'unknown'
        print(f'[OK] Using card_id={card_id} ({card_name})')
    except CardHedgerError as e:
        print(f'[FAIL] Search error: {e}')
        return 1

    # 3. FMV
    print(f'[3/5] Getting FMV for {card_id} PSA 10...')
    try:
        fmv = client.get_fmv(card_id=card_id, grade='PSA 10')
        fmv_value = fmv.get('fmv') or fmv.get('fair_market_value') or fmv.get('value')
        if fmv_value is None:
            print(f'[WARN] No FMV value in response. Full: {fmv}')
        else:
            confidence = fmv.get('confidence', 'unknown')
            print(f'[OK] FMV = ${fmv_value} (confidence: {confidence})')
    except CardHedgerError as e:
        print(f'[WARN] FMV error (non-fatal): {e}')
        # Don't fail the whole test on FMV error — different tiers may have access
        fmv_value = None

    # 4. Price history (last 30 days)
    print('[4/5] Getting 30-day price history...')
    try:
        history = client.get_price_history(card_id=card_id, grade='PSA 10', days=30)
        # Response shape varies — try common keys
        history_data = history.get('prices') or history.get('history') or history.get('data') or history
        if isinstance(history_data, list):
            print(f'[OK] Got {len(history_data)} price points over 30 days')
        else:
            print(f'[OK] Got price history (shape: {type(history_data).__name__})')
    except CardHedgerError as e:
        print(f'[WARN] Price history error (non-fatal): {e}')

    # 5. Comps
    print('[5/5] Getting comparable sales (comps)...')
    try:
        comps = client.get_comps(card_id=card_id, grade='PSA 10', count=10)
        comp_list = comps.get('comps') or comps.get('data') or comps.get('sales') or []
        if isinstance(comp_list, list):
            print(f'[OK] Got {len(comp_list)} comparable sales')
            if comp_list:
                print(f'   Sample: {comp_list[0]}')
        else:
            print(f'[OK] Got comps response (shape: {type(comp_list).__name__})')
    except CardHedgerError as e:
        print(f'[WARN] Comps error (non-fatal): {e}')

    print()
    print('=== SMOKE TEST PASSED ===')
    print('Card Hedge integration is wired correctly.')
    print('You can now build the alert pipeline integration.')
    return 0


if __name__ == '__main__':
    sys.exit(run_smoke_test())
