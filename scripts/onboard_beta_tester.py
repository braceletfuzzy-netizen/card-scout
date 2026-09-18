"""Sept 18 — Onboard a beta tester.

Quick path for adding a new beta tester:
1. They create Discord webhook (channel settings → integrations → webhook)
2. They send you the URL
3. You run: python scripts/onboard_beta_tester.py <email> <webhook_url>
4. Script does the rest:
   - Generates customer_id
   - Inserts customer row
   - Inserts customer_settings row (max_cards=5, beta tier)
   - Creates 5 empty card slots (user adds cards via dashboard later)
   - Posts welcome message to their webhook
   - Returns their login URL
"""
import sys
import os
import json
import secrets
import string
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv
load_dotenv('.env')


def generate_customer_id():
    """Generate cs_<8-char base36> id (e.g. cs_a1b2c3d4)."""
    alphabet = string.ascii_lowercase + string.digits
    suffix = ''.join(secrets.choice(alphabet) for _ in range(8))
    return f'cs_{suffix}'


def onboard(email, webhook_url, max_cards=5, beta_days=14, name=None, notes=None):
    """Add a new beta tester to the system.

    Args:
        email: Their email address
        webhook_url: Discord webhook URL (their channel)
        max_cards: Cards allowed (default 5 for beta)
        beta_days: Days until beta expires (default 14)
        name: Optional name (we don't have a name field, so put in notes)
        notes: Optional notes (e.g. referral source)

    Returns:
        dict with customer_id, login_url, etc.
    """
    conn = sqlite3.connect('card_scout.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Validate webhook by sending a test message
    print(f'\n1. Validating webhook...')
    try:
        test_resp = requests.post(webhook_url, json={
            'content': '🧪 **Card Scout beta tester onboarding**\n\n'
                       'Webhook validated! You can ignore this message — '
                       'we\'ll send you real alerts starting on your first scheduled run.\n\n'
                       f'Onboarded at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        }, timeout=10)
        if test_resp.status_code >= 400:
            print(f'  ✗ Webhook returned {test_resp.status_code}: {test_resp.text[:200]}')
            print(f'  Aborting — please check the webhook URL with your tester.')
            return None
        print(f'  ✓ Webhook validated (HTTP {test_resp.status_code})')
    except Exception as e:
        print(f'  ✗ Webhook test failed: {e}')
        return None

    # Generate customer_id
    customer_id = generate_customer_id()
    print(f'\n2. Generated customer_id: {customer_id}')

    # Insert customer
    note_text = notes or ''
    if name:
        note_text = f'Name: {name}\n{notes or ""}'.strip()
    cur.execute('''
        INSERT INTO customers (
            customer_id, email, discord_webhook, tier,
            subscription_status, beta_end_date, max_cards, joined_date, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        customer_id, email, webhook_url,
        'beta_power',  # Beta testers get full power (matches Jim)
        'active',       # Beta = active, no trial countdown
        (datetime.now() + timedelta(days=beta_days)).isoformat(),
        max_cards,
        datetime.now().isoformat(),
        note_text or None,
    ))
    cust_pk = cur.lastrowid
    print(f'  ✓ Customer inserted (id={cust_pk})')

    # Insert customer_settings
    cur.execute('''
        INSERT INTO customer_settings (
            customer_id, tier, max_cards, vault_max_cards,
            allow_sell_window, allow_active_alerts, alert_runs_per_month
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        cust_pk, 'beta_power', max_cards, max_cards, 1, 1, 12  # beta_power = 12 runs/mo (MWF)
    ))
    print(f'  ✓ customer_settings inserted (max_cards={max_cards}, sell_window=1)')

    conn.commit()

    # Login URL
    login_url = f'https://card-scout-pr67.onrender.com/dashboard/{customer_id}'

    print(f'\n=== Onboarding complete ===')
    print(f'  customer_id: {customer_id}')
    print(f'  email:       {email}')
    print(f'  webhook:     {webhook_url[:60]}...')
    print(f'  max_cards:   {max_cards}')
    print(f'  beta ends:   {beta_days} days from now')
    print(f'  login URL:   {login_url}')
    print(f'\nSend them this URL. They can add up to {max_cards} cards via the dashboard.')

    return {
        'customer_pk': cust_pk,
        'customer_id': customer_id,
        'email': email,
        'webhook_url': webhook_url,
        'max_cards': max_cards,
        'beta_end_date': (datetime.now() + timedelta(days=beta_days)).isoformat(),
        'login_url': login_url,
    }


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python scripts/onboard_beta_tester.py <email> <webhook_url> [--max-cards 5] [--beta-days 14] [--name "Jane"]')
        print()
        print('Example:')
        print('  python scripts/onboard_beta_tester.py jane@example.com https://discord.com/api/webhooks/123/abc')
        print()
        print('How your tester creates a Discord webhook:')
        print('  1. Open Discord, go to the channel where they want alerts')
        print('  2. Channel settings (gear icon) → Integrations → Webhooks')
        print('  3. New Webhook → Name it "Card Scout" → Copy URL')
        print('  4. Send it to you')
        sys.exit(1)

    email = sys.argv[1]
    webhook_url = sys.argv[2]

    # Parse optional flags
    max_cards = 5
    beta_days = 14
    name = None
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--max-cards' and i+1 < len(sys.argv):
            max_cards = int(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '--beta-days' and i+1 < len(sys.argv):
            beta_days = int(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '--name' and i+1 < len(sys.argv):
            name = sys.argv[i+1]
            i += 2
        else:
            i += 1

    onboard(email, webhook_url, max_cards=max_cards, beta_days=beta_days, name=name)
