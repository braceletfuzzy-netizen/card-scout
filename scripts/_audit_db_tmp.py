"""One-off DB audit: dump customers + cards."""
import sqlite3

conn = sqlite3.connect('card_scout.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
print("=== CUSTOMERS ===")
for r in cur.execute("SELECT id, customer_id, email, discord_webhook, subscription_status FROM customers"):
    print(dict(r))
print("\n=== CARDS per customer ===")
for r in cur.execute("SELECT c.customer_id, ca.id, ca.search_query, ca.enabled FROM cards ca JOIN customers c ON ca.customer_id=c.id"):
    print(dict(r))
conn.close()