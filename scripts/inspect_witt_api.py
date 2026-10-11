"""Quick test: inspect the raw API response structure for the Witt card."""

import sys
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))

from cardhedger_client import CardHedgerClient, CardHedgerError

CARD_ID = '1667744987045x937707180623517000'
GRADE = 'PSA 10'
API_KEY_PATH = Path(r'C:\Users\J\.secrets\card-scout\card-hedger-api-key.txt')

api_key = API_KEY_PATH.read_text().strip()
client = CardHedgerClient(api_key=api_key, timeout=60)

# Fetch a small window first
result = client.get_price_history(card_id=CARD_ID, grade=GRADE, days=10, end_date='2025-01-31')
print('=== FULL RESPONSE (first 10 days) ===')
print(json.dumps(result, indent=2)[:3000])
print()

# Also check what keys are at top level
print('=== TOP-LEVEL KEYS ===')
print(list(result.keys()))
print()

if 'prices' in result:
    print('=== FIRST PRICE ENTRY ===')
    prices = result['prices']
    print(f'Count: {len(prices)}')
    print(f'First entry: {json.dumps(prices[0], indent=2)}')
    print(f'Last entry: {json.dumps(prices[-1], indent=2)}')
