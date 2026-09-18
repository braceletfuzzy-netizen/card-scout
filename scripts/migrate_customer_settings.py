"""Sept 18 — customer_settings table migration.

Adds per-customer schedule config:
- alert_cron: how often to run alerts (overrides default by tier)
- tier overrides: max_cards, vault_max_cards (from PL-007)
"""
import sqlite3

conn = sqlite3.connect('card_scout.db')
cur = conn.cursor()

# Idempotent: check if table exists
existing = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
if 'customer_settings' in existing:
    print('customer_settings already exists, skipping')
else:
    cur.execute('''
        CREATE TABLE customer_settings (
            customer_id INTEGER PRIMARY KEY,
            tier TEXT NOT NULL,
            alert_cron TEXT,                    -- cron expression (NULL = use tier default)
            alert_runs_per_month INTEGER,       -- effective runs/mo (computed)
            max_cards INTEGER,                  -- overrides customer.max_cards
            vault_max_cards INTEGER,            -- PL-007 max
            allow_sell_window BOOLEAN DEFAULT 0, -- Pro tier only
            allow_active_alerts BOOLEAN DEFAULT 1,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')
    print('Created customer_settings table')

conn.commit()

# Verify schema
print('\n=== customer_settings schema ===')
for r in cur.execute("PRAGMA table_info(customer_settings)"):
    print(f'  {r[1]}: {r[2]}')

# Insert default settings for existing customers based on tier
print('\n=== Inserting default settings for existing customers ===')

# Tier defaults from Sept 18 founder decision (Path A: throttling)
TIER_DEFAULTS = {
    'casual':     {'max_cards': 25,  'vault_max_cards': 25,  'allow_sell_window': 0, 'alert_runs_per_month': 4},
    'standard':   {'max_cards': 75,  'vault_max_cards': 75,  'allow_sell_window': 0, 'alert_runs_per_month': 12},
    'dealer':     {'max_cards': 250, 'vault_max_cards': 250, 'allow_sell_window': 0, 'alert_runs_per_month': 30},
    'pro':        {'max_cards': 999, 'vault_max_cards': 999, 'allow_sell_window': 1, 'alert_runs_per_month': 90},
    'beta_power': {'max_cards': 25,  'vault_max_cards': 25,  'allow_sell_window': 1, 'alert_runs_per_month': 12},  # Jim gets sell-side
    'trial':      {'max_cards': 25,  'vault_max_cards': 25,  'allow_sell_window': 0, 'alert_runs_per_month': 12},
}

for cust_row in cur.execute("SELECT id, tier FROM customers"):
    cust_id, tier = cust_row
    defaults = TIER_DEFAULTS.get(tier, TIER_DEFAULTS['trial'])
    cur.execute('''
        INSERT INTO customer_settings (customer_id, tier, max_cards, vault_max_cards, allow_sell_window, alert_runs_per_month)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (cust_id, tier, defaults['max_cards'], defaults['vault_max_cards'],
          defaults['allow_sell_window'], defaults['alert_runs_per_month']))
    print(f'  Customer {cust_id} (tier={tier}): max_cards={defaults["max_cards"]}, vault_max={defaults["vault_max_cards"]}, sell_window={defaults["allow_sell_window"]}, runs/mo={defaults["alert_runs_per_month"]}')

conn.commit()

# Verify
print('\n=== Final customer_settings rows ===')
for r in cur.execute("""
    SELECT cs.customer_id, c.customer_id as slug, cs.tier, cs.max_cards,
           cs.vault_max_cards, cs.allow_sell_window, cs.alert_runs_per_month
    FROM customer_settings cs
    JOIN customers c ON cs.customer_id = c.id
    ORDER BY cs.customer_id
"""):
    print(f'  id={r[0]} {r[1]:<30} tier={r[2]:<10} max_cards={r[3]:<4} vault={r[4]:<4} sell={r[5]} runs/mo={r[6]}')

conn.close()
print('\nDone.')
