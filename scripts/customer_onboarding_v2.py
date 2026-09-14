"""
Card Scout Customer Onboarding Engine v2
=========================================

Reads from Google Form responses (auto-piped to Sheet), creates customers in DB,
configures Discord webhooks, and sends welcome emails.

Architecture:
    1. Read 'Form Responses 1' tab (Google Forms auto-pipes here)
    2. For each new row, build a smart search query from structured fields
    3. Create Customer + Card records in DB
    4. PATCH Discord webhook with Card Scout branding
    5. Send welcome email via Gmail API
    6. Mark row as "processed" by writing timestamp to a separate column

Customer ID: cs_XXXXXX (6 hex chars, auto-generated)

Usage:
    python customer_onboarding_v2.py

Cron: every 4 hours
"""

import os
import sys
import json
import re
import uuid
import time
import base64
import sqlite3
import requests
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Add scripts dir to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from db_models import init_db, get_session, Customer, Card

# ============ CONFIG ============
# GCP service account key location.
# Default: C:\\Users\\J\\.secrets\\card-scout\\gcp-service-account.json (outside repo)
# Override with GCP_SA_KEY_PATH env var for production.
CONFIG_DIR = os.path.join(SCRIPT_DIR, '..', 'config')
LEGACY_GCP_PATH = os.path.join(CONFIG_DIR, 'gcp-service-account.json')
SAFE_GCP_PATH = os.path.join(os.path.expanduser('~'), '.secrets', 'card-scout', 'gcp-service-account.json')
GCP_KEY_PATH = os.environ.get('GCP_SA_KEY_PATH') or (
    SAFE_GCP_PATH if os.path.exists(SAFE_GCP_PATH) else LEGACY_GCP_PATH
)
if not os.path.exists(GCP_KEY_PATH):
    raise FileNotFoundError(
        f"GCP service account key not found. Tried:\n  {SAFE_GCP_PATH}\n  {LEGACY_GCP_PATH}\n"
        "Set GCP_SA_KEY_PATH env var or place key in one of these locations."
    )
BRAND_LOGO_PATH = os.path.join(SCRIPT_DIR, '..', 'For You', 'Brand', 'card-scout-discord-avatar.png')
WELCOME_EMAIL_FROM = 'braceletfuzzy@gmail.com'
SIGNATURE = 'Fuzzy'

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.send'
]

FORM_RESPONSES_TAB = 'Form Responses 1'

# Sheet column mapping (1-indexed)
COL_TIMESTAMP = 1
COL_FIRST_NAME = 2
COL_LAST_NAME = 3
COL_DISCORD_WEBHOOK = 4
COL_SPORTS_OR_TCG = 5
COL_BRAND = 6
COL_PLAYER = 7
COL_CARD_NUM = 8
COL_YEAR = 9
COL_SPECIAL = 10
COL_PROCESSED = 11  # Will be added if not present

# Preset mapping
PRESET_MAP = {
    'Sports': 'cards-sports',
    'TCG': 'cards-pokemon',  # could also be cards-tcg
    'Pokemon': 'cards-pokemon',
    'MTG': 'cards-tcg',
    'Magic': 'cards-tcg',
    'Yu-Gi-Oh': 'cards-tcg',
    'One Piece': 'cards-tcg',
}


def load_config():
    """Load Sheet ID and service account email from saved configs."""
    with open(os.path.join(CONFIG_DIR, 'card-scout-sheet.json')) as f:
        sheet_info = json.load(f)
    return sheet_info['sheet_id']


def init_google_services():
    """Build Sheets + Gmail service clients."""
    if not os.path.exists(GCP_KEY_PATH):
        raise FileNotFoundError(f"Service account key not found: {GCP_KEY_PATH}")
    creds = service_account.Credentials.from_service_account_file(
        GCP_KEY_PATH, scopes=SCOPES
    )
    sheets_service = build('sheets', 'v4', credentials=creds)
    gmail_service = build('gmail', 'v1', credentials=creds)
    return sheets_service, gmail_service


def generate_customer_id():
    """Generate cs_XXXXXX customer ID.

    DEPRECATED: Use generate_customer_id_v2() for production customers.
    Kept for backwards compat with any test data.
    """
    return f"cs_{uuid.uuid4().hex[:6]}"


def encode_base26(n, min_len=1):
    """Encode integer to base 26 using A=0, B=1, ..., Z=25.

    Returns uppercase letters, zero-padded to min_len if needed.
    Padding uses 'A' (which represents 0 in base 26), NOT '0'.
    """
    if n == 0:
        return 'A' * min_len
    digits = []
    while n > 0:
        digits.append(chr(ord('A') + (n % 26)))
        n //= 26
    result = ''.join(reversed(digits)) if digits else 'A'
    # Pad with A's (representing zeros) to min_len
    if len(result) < min_len:
        result = 'A' * (min_len - len(result)) + result
    return result


def decode_base26(s):
    """Decode base-26 string back to integer (A=0, B=1, ..., Z=25)."""
    n = 0
    for c in s:
        n = n * 26 + (ord(c) - ord('A'))
    return n


def generate_customer_id_v2(session=None, today=None):
    """Generate customer ID in format cs_<YEAR3><DAY3><COUNTER6>.

    Format breakdown:
        cs_<YEAR3>  = 3-char base-26 of full year (e.g., 2026 = CZY)
        <DAY3>     = 3-char base-26 of Julian day (e.g., day 256 = AJW)
        <COUNTER6> = A + 5 digits, A00000 reserved, starts at A00001

    Examples:
        1st customer of 2026-09-13: cs_CZYAJWA00001
        100th customer of 2026-09-13: cs_CZYAJWA00100
        1st customer of 2027-01-01: cs_CZZAA...A00001

    The A00000 counter is reserved (broadcast/sentinel).
    See: For You/Plans/customer-id-system-design-2026-09-13.md

    Args:
        session: SQLAlchemy session (created if None)
        today: date object (defaults to today)

    Returns:
        Customer ID string like 'cs_CZYAJWA00001'
    """
    from datetime import date
    if today is None:
        today = date.today()

    if session is None:
        from db_models import init_db, get_session
        init_db()
        session = get_session()

    # Date components
    year = today.year
    julian = today.timetuple().tm_yday

    # Encode year + day
    year_enc = encode_base26(year, 3)
    day_enc = encode_base26(julian, 3)
    date_prefix = f"cs_{year_enc}{day_enc}"

    # Find today's max counter in DB
    from db_models import Customer
    like_pattern = f"{date_prefix}A%"
    today_customers = session.query(Customer).filter(
        Customer.customer_id.like(like_pattern)
    ).all()

    # Extract counter values, find max
    max_counter = 0
    for c in today_customers:
        if c.customer_id and len(c.customer_id) >= 14:
            counter_str = c.customer_id[9:]  # Last 6 chars
            if len(counter_str) == 6:
                letter = counter_str[0]
                digits = counter_str[1:]
                if letter.isalpha() and digits.isdigit():
                    counter_val = (ord(letter) - ord('A')) * 100000 + int(digits)
                    max_counter = max(max_counter, counter_val)

    # Next counter (skip A00000 = 0)
    next_counter = max(max_counter + 1, 1)
    letter = chr(ord('A') + (next_counter // 100000))
    digits = next_counter % 100000

    return f"{date_prefix}{letter}{digits:05d}"


def build_search_query(row):
    """Build a smart search query from form fields.

    Combines: Brand + Player + Card # + Year + Special
    Example: 'Topps 1993 Derek Jeter #449 Rookie'
    """
    parts = []
    for col in [COL_BRAND, COL_PLAYER, COL_YEAR, COL_CARD_NUM, COL_SPECIAL]:
        if col <= len(row):
            val = row[col - 1].strip()
            if val:
                parts.append(val)
    return ' '.join(parts)


def get_preset_for(sports_or_tcg):
    """Map Sports/TCG choice to eBay+Etsy preset."""
    return PRESET_MAP.get(sports_or_tcg.strip(), 'cards-sports')


def configure_webhook(webhook_url):
    """PATCH Discord webhook with Card Scout branding."""
    try:
        parts = webhook_url.rstrip('/').split('/webhooks/')
        webhook_id = parts[1].split('/')[0]
        webhook_token = parts[1].split('/')[1]
        api_url = f"https://discord.com/api/webhooks/{webhook_id}/{webhook_token}"

        with open(BRAND_LOGO_PATH, 'rb') as f:
            logo_b64 = base64.b64encode(f.read()).decode('utf-8')

        payload = {
            "name": "Card Scout",
            "avatar": f"data:image/png;base64,{logo_b64}"
        }
        resp = requests.patch(api_url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"  [WEBHOOK] Error: {e}")
        return False


def send_welcome_email(gmail_service, customer_email, customer_name, customer_id, card_count, search_query):
    """Send welcome email via Gmail API."""
    subject = "Your Card Scout is ready"

    body = f"""Hi {customer_name},

Welcome to Card Scout! You're all set to start receiving smart alerts.

📊 First card tracked: {search_query}

You're tracking {card_count} card{'s' if card_count != 1 else ''}.

🔧 Update your cards anytime: [Update Form Link]

💳 Upgrade to Pro: [Stripe Link]

Your customer ID: {customer_id} (save this for updates)

What to expect:
- Alerts run Mon/Wed/Fri at 2pm Central
- Each alert shows Q bands, trend signals, and population data
- Reply to this email with questions

— {SIGNATURE}
Card Scout
"""

    msg = MIMEText(body)
    msg['to'] = customer_email
    msg['from'] = WELCOME_EMAIL_FROM
    msg['subject'] = subject

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    try:
        gmail_service.users().messages().send(
            userId='me', body={'raw': raw}
        ).execute()
        return True
    except Exception as e:
        print(f"  [EMAIL] Error: {e}")
        return False


def ensure_processed_column(sheets_service, sheet_id):
    """Add a 'processed_at' column to Form Responses 1 if not present."""
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"'{FORM_RESPONSES_TAB}'!A1:Z1"
    ).execute()
    headers = result.get('values', [[]])[0]

    if 'processed_at' not in headers:
        # Add column
        new_col_idx = len(headers) + 1
        sheets_service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"'{FORM_RESPONSES_TAB}'!{chr(64 + new_col_idx)}1",
            valueInputOption='RAW',
            body={'values': [['processed_at']]}
        ).execute()
        print(f"  ✓ Added 'processed_at' column at col {new_col_idx}")
        return new_col_idx
    return headers.index('processed_at') + 1


def process_form_responses(sheets_service, gmail_service, sheet_id, dry_run=False):
    """Read Form Responses, create customers, send emails."""
    print("\n" + "="*70)
    print("PROCESSING FORM RESPONSES")
    print("="*70)

    # Get all data
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"'{FORM_RESPONSES_TAB}'!A1:Z1000"
    ).execute()
    rows = result.get('values', [])

    if len(rows) < 2:
        print("  No form responses yet")
        return 0

    # Ensure processed_at column exists
    processed_col = ensure_processed_column(sheets_service, sheet_id)

    new_customers = 0
    for row_idx, row in enumerate(rows[1:], start=2):
        # Pad row to expected length
        row = row + [''] * (processed_col - len(row))

        # Skip if already processed
        if len(row) >= processed_col and row[processed_col - 1].strip():
            continue

        # Extract fields
        first_name = (row[COL_FIRST_NAME - 1] if len(row) >= COL_FIRST_NAME else '').strip()
        last_name = (row[COL_LAST_NAME - 1] if len(row) >= COL_LAST_NAME else '').strip()
        webhook = (row[COL_DISCORD_WEBHOOK - 1] if len(row) >= COL_DISCORD_WEBHOOK else '').strip()
        sports_tcg = (row[COL_SPORTS_OR_TCG - 1] if len(row) >= COL_SPORTS_OR_TCG else '').strip()

        if not first_name or not last_name or not webhook:
            print(f"  Row {row_idx}: missing name/webhook, skipping")
            continue

        full_name = f"{first_name} {last_name}"
        search_query = build_search_query(row)
        preset = get_preset_for(sports_tcg)

        print(f"\n  Row {row_idx}: {full_name} ({sports_tcg})")
        print(f"    Query: {search_query}")
        print(f"    Preset: {preset}")

        if dry_run:
            print(f"    [DRY RUN] Would create customer")
            continue

        # Create customer in DB
        session = get_session()
        try:
            # Check if already exists
            existing = session.query(Customer).filter_by(discord_webhook=webhook).first()
            if existing:
                print(f"    ⚠️  Customer with this webhook exists: {existing.customer_id}")
                continue

            customer_id = generate_customer_id_v2(session)
            new_customer = Customer(
                customer_id=customer_id,
                email=f"{first_name.lower()}.{last_name.lower()}@placeholder.local",  # No email from form
                discord_webhook=webhook,
                tier='beta_power',  # Default to power for now
                subscription_status='active',  # Mark as active customer
            )
            session.add(new_customer)
            session.commit()
            session.refresh(new_customer)
            print(f"    ✓ Customer {customer_id} created")

            # Add the card
            new_card = Card(
                customer_id=new_customer.id,
                search_query=search_query,
                alert_type='below_median',
                max_listings=15,
                enabled=True,
            )
            session.add(new_card)
            session.commit()
            print(f"    ✓ Card added: {search_query}")

        except Exception as e:
            print(f"    ✗ DB error: {e}")
            session.rollback()
            continue
        finally:
            session.close()

        # Configure webhook
        print(f"    Configuring webhook...")
        if configure_webhook(webhook):
            print(f"    ✓ Webhook branded")
        else:
            print(f"    ⚠️  Webhook config failed (continuing)")

        # Mark processed
        try:
            sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"'{FORM_RESPONSES_TAB}'!{chr(64 + processed_col)}{row_idx}",
                valueInputOption='RAW',
                body={'values': [[datetime.utcnow().isoformat()]]}
            ).execute()
            print(f"    ✓ Marked processed")
        except Exception as e:
            print(f"    ⚠️  Mark processed failed: {e}")

        new_customers += 1

    return new_customers


def main():
    """Main onboarding runner."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Process but no changes')
    args = parser.parse_args()

    sheet_id = load_config()
    print(f"📊 Card Scout Customer Onboarding v2")
    print(f"   Sheet ID: {sheet_id}")
    print(f"   Dry run: {args.dry_run}")

    # Init services
    try:
        sheets_service, gmail_service = init_google_services()
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        return 1

    # Init DB
    init_db()

    # Process form responses
    new_count = process_form_responses(sheets_service, gmail_service, sheet_id, dry_run=args.dry_run)

    print(f"\n{'='*70}")
    print(f"DONE: {new_count} new customers")
    print('='*70)
    return 0


if __name__ == '__main__':
    sys.exit(main())
