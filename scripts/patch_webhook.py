#!/usr/bin/env python
"""
Patch one or more webhooks with Card Scout branding.

Use this when:
- A customer signs up via Google Form but sheets_importer didn't PATCH the webhook
- A new customer needs the Card Scout logo on their alerts
- Discord shows default avatar instead of binoculars logo

Usage:
    python scripts/patch_webhook.py hingle_mccringleberry_1789525909
    python scripts/patch_webhook.py --all   # patch all webhooks in DB
    python scripts/patch_webhook.py --webhook "https://discord.com/api/webhooks/..."
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import base64
import argparse
import requests
from customer_onboarding_v2 import configure_webhook
from db_models import init_db, get_session, Customer


def main():
    parser = argparse.ArgumentParser(description='PATCH Discord webhooks with Card Scout branding')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('customer_id', nargs='?', help='Patch webhook for specific customer_id')
    group.add_argument('--all', action='store_true', help='Patch all customer webhooks in DB')
    group.add_argument('--webhook', help='Patch a specific webhook URL directly')

    args = parser.parse_args()

    init_db()
    session = get_session()

    webhooks_to_patch = []

    if args.all:
        customers = session.query(Customer).all()
        webhooks_to_patch = [(c.customer_id, c.discord_webhook) for c in customers if c.discord_webhook]
    elif args.webhook:
        webhooks_to_patch = [('(manual)', args.webhook)]
    else:
        customer = session.query(Customer).filter_by(customer_id=args.customer_id).first()
        if not customer:
            print(f"[FAIL] Customer not found: {args.customer_id}")
            session.close()
            return 1
        webhooks_to_patch = [(customer.customer_id, customer.discord_webhook)]

    session.close()

    if not webhooks_to_patch:
        print("[FAIL] No webhooks to patch")
        return 1

    print(f"Patching {len(webhooks_to_patch)} webhook(s)...\n")

    success = 0
    failed = 0
    for cust_id, webhook_url in webhooks_to_patch:
        if not webhook_url:
            print(f"  [SKIP] {cust_id}: no webhook")
            continue
        print(f"  [{cust_id}] {webhook_url[:60]}...")
        if configure_webhook(webhook_url):
            print(f"    [OK] Patched")
            success += 1
        else:
            print(f"    [FAIL] Could not PATCH")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Patched {success}, failed {failed}")
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
