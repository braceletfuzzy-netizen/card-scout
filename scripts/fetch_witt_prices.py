"""Fetch Bobby Witt Jr. PSA 10 rookie card price history from Card Hedge API.

Card: Topps Update 2022, card_id: 1667744987045x937707180623517000
Grade: PSA 10

Pulls overlapping 366-day windows to build the full timeline:
  1. ~Jan 2025 → today (most recent ~12 months)
  2. ~Jan 2024 → Jan 2025 (pre-30-30 through post-30-30 plateau)
  3. ~Jan 2023 → Jan 2024 (full rookie-year context, optional)

Uses CardHedgerClient from cardhedger_client.py.
"""

import sys
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))

from cardhedger_client import CardHedgerClient, CardHedgerError

CARD_ID = '1667744987045x937707180623517000'
GRADE = 'PSA 10'

OUT_DIR = Path(r'C:\Users\J\Documents\LLM\cardscout-2.0\For You\Research\event_case_studies')
RAW_OUT = OUT_DIR / 'witt_price_raw.json'
MERGED_OUT = OUT_DIR / 'witt_price_merged.json'
API_KEY_PATH = Path(r'C:\Users\J\.secrets\card-scout\card-hedger-api-key.txt')


def load_api_key():
    if API_KEY_PATH.exists():
        return API_KEY_PATH.read_text().strip()
    return None


def fetch_window(client, card_id, grade, days, end_date=None, label=''):
    print(f'  Fetching {label}: days={days}, end_date={end_date} ...')
    try:
        result = client.get_price_history(card_id=card_id, grade=grade, days=days, end_date=end_date)
        prices = result.get('prices', [])
        print(f'    -> got {len(prices)} price points')
        return prices
    except CardHedgerError as e:
        print(f'    ✗ ERROR: {e}')
        if e.status_code:
            print(f'      status: {e.status_code}')
        if e.response_body:
            print(f'      body: {e.response_body}')
        return []


def main():
    api_key = load_api_key()
    if not api_key:
        print('ERROR: No API key found. Expected at:', API_KEY_PATH)
        sys.exit(1)

    print(f'Card: {CARD_ID}')
    print(f'Grade: {GRADE}')
    print(f'API key: {"set" if api_key else "MISSING"}')
    print()

    client = CardHedgerClient(api_key=api_key, timeout=60)
    all_prices = {}

    # Window 1: ~Sept 2025 → today
    w1 = fetch_window(client, CARD_ID, GRADE, days=366, end_date=None, label='Window 1: ~Sept 2025 → today')
    for p in w1:
        d = p.get('closing_date', '')
        price_str = p.get('price', '0')
        if d and price_str:
            date_key = d[:10]  # YYYY-MM-DD
            all_prices[date_key] = float(price_str)

    # Window 2: ~Jan 2024 → Jan 2025
    w2 = fetch_window(client, CARD_ID, GRADE, days=366, end_date='2025-01-31',
                      label='Window 2: ~Jan 2024 → Jan 2025')
    for p in w2:
        d = p.get('closing_date', '')
        price_str = p.get('price', '0')
        if d and price_str:
            date_key = d[:10]
            all_prices[date_key] = float(price_str)

    # Window 3: ~Jan 2023 → Jan 2024
    w3 = fetch_window(client, CARD_ID, GRADE, days=366, end_date='2024-01-31',
                      label='Window 3: ~Jan 2023 → Jan 2024')
    for p in w3:
        d = p.get('closing_date', '')
        price_str = p.get('price', '0')
        if d and price_str:
            date_key = d[:10]
            all_prices[date_key] = float(price_str)

    sorted_prices = sorted(all_prices.items())
    print(f'\nTotal unique price points: {len(sorted_prices)}')

    if not sorted_prices:
        print('NO DATA RECEIVED. Cannot proceed.')
        sys.exit(1)

    print(f'Date range: {sorted_prices[0][0]} → {sorted_prices[-1][0]}')
    print()

    print('=== RAW PRICE DATA (chronological) ===')
    for date, price in sorted_prices:
        print(f'{date}  ${price:,.2f}')

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw_data = {
        'card_id': CARD_ID,
        'grade': GRADE,
        'card_name': 'Bobby Witt Jr. PSA 10 Rookie Card (Topps Update 2022)',
        'total_points': len(sorted_prices),
        'date_range': f'{sorted_prices[0][0]} to {sorted_prices[-1][0]}',
        'prices': [{'date': d, 'price': p} for d, p in sorted_prices],
    }
    RAW_OUT.write_text(json.dumps(raw_data, indent=2))
    print(f'\nRaw data saved to: {RAW_OUT}')

    merged_data = {
        'card_id': CARD_ID,
        'grade': GRADE,
        'card_name': 'Bobby Witt Jr. PSA 10 Rookie Card (Topps Update 2022)',
        'total_points': len(sorted_prices),
        'date_range': f'{sorted_prices[0][0]} to {sorted_prices[-1][0]}',
        'prices': [{'date': d, 'price': p} for d, p in sorted_prices],
    }
    MERGED_OUT.write_text(json.dumps(merged_data, indent=2))
    print(f'Merged data saved to: {MERGED_OUT}')

    # Key stats
    print('\n=== KEY STATS ===')
    prices_only = [p for _, p in sorted_prices]
    print(f'Min price: ${min(prices_only):,.2f}')
    print(f'Max price: ${max(prices_only):,.2f}')
    print(f'First price ({sorted_prices[0][0]}): ${sorted_prices[0][1]:,.2f}')
    print(f'Last price ({sorted_prices[-1][0]}): ${sorted_prices[-1][1]:,.2f}')

    # Key date references
    key_dates = [
        '2024-05-01', '2024-06-01', '2024-07-01', '2024-08-01',
        '2024-09-01', '2024-10-01', '2024-11-01', '2024-12-01', '2025-01-01'
    ]
    print('\n=== PRICES AROUND KEY DATES ===')
    for kd in key_dates:
        best = None
        for d, p in sorted_prices:
            if d <= kd:
                best = (d, p)
            else:
                break
        if best:
            print(f'{best[0]}  ${best[1]:,.2f}  (closest to {kd})')


if __name__ == '__main__':
    main()
