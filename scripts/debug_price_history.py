#!/usr/bin/env python3
import sys, json
sys.path.insert(0, 'scripts')
from cardhedger_client import CardHedgerClient

client = CardHedgerClient()

# Get price history for a player with good data
history = client.get_price_history(
    card_id='1720368706347x778313243362590700',  # Jose Ramirez
    grade='PSA 10',
    days=365
)

print("Price history response keys:", list(history.keys()))
prices = history.get('prices', [])
print(f"Number of price points: {len(prices)}")

if prices:
    print("\nFirst 3 price points:")
    for p in prices[:3]:
        print(f"  {json.dumps(p, default=str)}")
    print("\nLast 3 price points:")
    for p in prices[-3:]:
        print(f"  {json.dumps(p, default=str)}")

# Get comps with raw prices
print("\n--- Comps with raw prices ---")
comps = client.get_comps(
    card_id='1720368706347x778313243362590700',
    grade='PSA 10',
    count=5,
    include_raw_prices=True
)
print(json.dumps(comps, indent=2, default=str)[:2000])
