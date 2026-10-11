#!/usr/bin/env python3
import sys, json
sys.path.insert(0, 'scripts')
from cardhedger_client import CardHedgerClient

client = CardHedgerClient()

# Check price history for Griffey
history = client.get_price_history(card_id='1657991196721x285092702996430800', grade='PSA 10', days=365)
print("Price history keys:", list(history.keys()) if history else "None")
if history:
    prices = history.get('prices', [])
    print(f"Number of price points: {len(prices)}")
    if prices:
        print("\nFirst 5 price points:")
        for p in prices[:5]:
            print(f"  {p}")
        print("\nLast 5 price points:")
        for p in prices[-5:]:
            print(f"  {p}")

# Check what our FMV cache has for price history fields
print("\n--- Our FMV cache fields ---")
import polars as pl
df = pl.read_parquet('data_lake/gold/card_hedge_cache/fmv_cache_20260924.parquet')
print(f"Columns: {df.columns}")
print(f"\nSample row (Jose Ramirez):")
row = df.filter(pl.col('name') == 'Jose Ramirez').head(1)
print(f"  price_mean: {row['price_mean'][0]:.2f}")
print(f"  price_std: {row['price_std'][0]:.2f}")
print(f"  price_min: {row['price_min'][0]:.2f}")
print(f"  price_max: {row['price_max'][0]:.2f}")
print(f"  price_latest: {row['price_latest'][0]:.2f}")
print(f"  price_n_points: {row['price_n_points'][0]}")
