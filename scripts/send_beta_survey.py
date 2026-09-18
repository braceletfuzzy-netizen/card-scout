"""
Beta user survey sender (Sept 18 framework).

Sends a Discord DM to every active beta customer with a Google Form link.

Re-runnable weekly. Each send captures:
- Who got the survey (just for tracking, not attribution)
- Timestamp
- Send success/failure per recipient

Results come back anonymously via Google Form responses (collected
in a separate Google Sheet, no per-user tracking).

Usage:
    python scripts/send_beta_survey.py [--form-url URL] [--dry-run]

Schedule:
    Cron every Friday at 10am (or weekly cadence)
    First run: ~Sept 25, 2026
"""
import argparse
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def get_active_beta_customers():
    """Return all active customers in beta tiers."""
    db_path = Path('card_scout.db')
    if not db_path.exists():
        print(f'DB not found: {db_path}')
        return []

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("""
        SELECT c.customer_id, c.discord_webhook, c.tier, c.email,
               COUNT(card.id) as card_count
        FROM customers c
        LEFT JOIN cards card ON card.customer_id = c.id AND card.enabled = 1
        WHERE c.tier LIKE 'beta_%' OR c.subscription_status = 'trial'
        GROUP BY c.id
        HAVING card_count > 0
    """)
    rows = cur.fetchall()
    conn.close()

    return [
        {'customer_id': r[0], 'discord_webhook': r[1], 'tier': r[2], 'email': r[3], 'card_count': r[4]}
        for r in rows
    ]


def send_survey_to_customer(customer, form_url, dry_run=False):
    """Send a Discord DM with the survey link via webhook.

    Note: webhooks only support channel posts, not DMs. So we post in
    the customer's existing alert channel (where they already see alerts).
    """
    if dry_run:
        return {'status': 'dry_run', 'customer_id': customer['customer_id']}

    webhook_url = customer.get('discord_webhook')
    if not webhook_url:
        return {'status': 'no_webhook', 'customer_id': customer['customer_id']}

    # Build the survey message
    message = {
        'content': (
            f'📊 **Quick feedback request** (3 min, anonymous)\n\n'
            f'You\'ve been using Card Scout for a few weeks now. '
            f'Could you take 3 minutes to share what\'s working and what isn\'t?\n\n'
            f'👉 **Survey link:** {form_url}\n\n'
            f'Your responses are anonymous and will help shape what we build next.'
        ),
        'username': 'Card Scout Survey',
    }

    # Use requests to POST to webhook
    try:
        import requests
        resp = requests.post(webhook_url, json=message, timeout=10)
        if resp.status_code in (200, 204):
            return {'status': 'sent', 'customer_id': customer['customer_id']}
        else:
            return {
                'status': 'failed',
                'customer_id': customer['customer_id'],
                'http_status': resp.status_code,
                'response': resp.text[:200],
            }
    except Exception as e:
        return {'status': 'error', 'customer_id': customer['customer_id'], 'error': str(e)}


def log_send(result):
    """Log the send result to a local file for audit."""
    log_path = Path('survey_send_log.jsonl')
    record = {
        'timestamp': datetime.utcnow().isoformat(),
        **result,
    }
    with open(log_path, 'a') as f:
        f.write(json.dumps(record) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--form-url', required=True, help='Google Form URL to send')
    parser.add_argument('--dry-run', action='store_true', help='Show who would receive, do not send')
    args = parser.parse_args()

    print(f'Sending beta user survey to all active beta customers')
    print(f'Form URL: {args.form_url}')
    print(f'Mode: {"DRY RUN" if args.dry_run else "LIVE"}')
    print()

    customers = get_active_beta_customers()
    print(f'Found {len(customers)} active beta customer(s):')
    for c in customers:
        print(f'  - {c["customer_id"]} (tier: {c["tier"]}, email: {c["email"] or "n/a"})')
    print()

    if not customers:
        print('No active beta customers to survey.')
        return

    if args.dry_run:
        print('--dry-run: not sending')
        return

    # Send to each
    sent = 0
    failed = 0
    for c in customers:
        result = send_survey_to_customer(c, args.form_url)
        log_send(result)
        status = result['status']
        if status == 'sent':
            sent += 1
            print(f'  [SENT] {c["customer_id"]}')
        else:
            failed += 1
            print(f'  [{status.upper()}] {c["customer_id"]}')

        # Rate limit to avoid Discord API throttling
        time.sleep(2)

    print()
    print(f'Results: {sent} sent, {failed} failed')
    print(f'Logged to: survey_send_log.jsonl')


if __name__ == '__main__':
    main()
