"""Targeted test of sell-side second-pass logic."""
import sys
sys.path.insert(0, 'scripts')
from dotenv import load_dotenv
load_dotenv('.env')

# Build test data
matching = [
    {
        'title': '1990 Topps Frank Thomas #414 RC',
        'price_usd': 25.00,  # 10x typical
        'url': 'https://ebay.com/itm/123',
        'was_sold': False,
        'sold_count': 5,
    },
    {
        'title': '1990 Topps Frank Thomas #414',
        'price_usd': 1.25,  # below typical - buy signal, not sell
        'url': 'https://ebay.com/itm/456',
        'was_sold': False,
        'sold_count': 2,
    },
]

sold_data = {
    'title': 'Frank Thomas 1990 Topps #414 RC',
    'source_url': 'https://sportscardspro.com/test',
    'psa_10_price': 157.50,
    'psa_10_sold_30d': 30,
    'psa_9_price': 19.41,
    'psa_9_sold_30d': 30,
    'psa_8_price': 10.98,
    'ungraded_price': 1.99,
    'ungraded_sold_30d': 30,
    'recent_sales': [
        {'date': '2026-09-15', 'price_usd': 2.00},
        {'date': '2026-09-14', 'price_usd': 1.25},
        {'date': '2026-09-13', 'price_usd': 1.25},
        {'date': '2026-09-12', 'price_usd': 2.99},
        {'date': '2026-09-05', 'price_usd': 2.99},
        {'date': '2026-09-04', 'price_usd': 2.99},
        {'date': '2026-08-25', 'price_usd': 1.99},
        {'date': '2026-08-15', 'price_usd': 1.99},
        {'date': '2026-07-20', 'price_usd': 3.50},
    ]
}

# Test find_sell_window
from sell_side_alerts import find_sell_window, format_sell_alert

print('=== Test 1: find_sell_window ===')
sells = find_sell_window(matching, sold_data)
print(f'Found {len(sells)} sell candidates:')
for s in sells:
    print(f'  ${s.get("price_usd"):.2f} → ratio={s.get("_ratio"):.1f}x → tier={s.get("_tier")}')

print('\n=== Test 2: format_sell_alert ===')
msgs = format_sell_alert('1990 Topps Frank Thomas Rookie', sells, sold_data, max_items=2)
print(f'Generated {len(msgs)} Discord messages:')
for m in msgs:
    print(f'\n--- Message {msgs.index(m)+1} ---')
    print(f'Title: {m["title"]}')
    print(f'Description:')
    for line in m['description'].split('\n'):
        print(f'  {line}')

print('\n=== Test 3: customer_settings lookup ===')
import sqlite3
conn = sqlite3.connect('card_scout.db')
conn.row_factory = sqlite3.Row
for r in conn.execute('SELECT customer_id, tier, allow_sell_window FROM customer_settings WHERE customer_id IN (1, 3)'):
    print(f'  cust_id={r["customer_id"]} tier={r["tier"]} allow_sell={r["allow_sell_window"]}')
conn.close()
