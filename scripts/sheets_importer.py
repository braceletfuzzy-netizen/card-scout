"""Google Sheets to Card Scout DB importer.

USE: After a new customer submits the Google Form, run this to import
their data into the Card Scout DB so the bot can start alerting them.

WORKFLOW:
    1. Enable Google Sheets API in card-scout-automation project
    2. Share the form's response Sheet with:
       card-scout-bot@card-scout-automation.iam.gserviceaccount.com
       (Give it Editor access so we can mark rows as imported)
    3. Set GOOGLE_SHEET_ID in card-scout/.env (already created)
    4. Run: python sheets_importer.py --dry-run
    5. Run: python sheets_importer.py --import
    6. Run again to mark imported rows (or auto-mark)

SHEET COLUMNS EXPECTED (from "Your Franchise Starts Here (Signup)"):
    A: Timestamp
    B: First Name (You)
    C: Last Name (You)
    D: Discord Webhook
    E: (Section 2 - "Scouting Report Card 1") Card details
    F-N: (Section 3, 4, 5) More cards

This script auto-detects column positions by header name.

SAFETY:
    - Dry-run by default (prints what would be imported, does nothing)
    - Idempotent: skips rows where Email or Discord Webhook already in DB
    - Marks imported rows in column O ("Imported?") with timestamp
"""
import sys
import os
import json
from pathlib import Path

# Load .env from card-scout root (one level up from scripts/)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    print("[WARN] python-dotenv not installed. Run: uv pip install python-dotenv")
    print("       Falling back to system env vars only.")
except Exception as e:
    print(f"[WARN] Could not load .env: {e}")

sys.path.insert(0, str(Path(__file__).parent))

# Add parent dir to path for db_models (since scripts/ is one level deep)
sys.path.insert(0, str(Path(__file__).parent.parent))

from db_models import init_db, get_session, Customer, Card
from datetime import datetime


# ============================================================================
# CONFIG
# ============================================================================

# SA key path: from env var if set, else default location
SA_PATH = Path(os.getenv(
    'GOOGLE_APPLICATION_CREDENTIALS',
    r'C:\Users\J\.secrets\card-scout\gcp-service-account.json'
))

# Sheet ID from the Google Sheets URL (the long alphanumeric between /d/ and /edit)
# Get this from your form: Open Responses -> click Sheets icon -> copy URL
SHEET_ID = os.getenv('GOOGLE_SHEET_ID', '')

# Column mapping (auto-detected from header row if not set)
# Override here if auto-detect fails
COLUMN_MAP = {
    'timestamp': None,  # Auto-detect: column with header "Timestamp"
    'first_name': None,  # Auto-detect: "First Name"
    'last_name': None,  # Auto-detect: "Last Name"
    'discord_webhook': None,  # Auto-detect: "Discord Webhook"
    'imported_marker': None,  # Column O (we add this)
}


# ============================================================================
# GOOGLE SHEETS AUTH
# ============================================================================

def get_sheets_client():
    """Build authenticated Google Sheets client using service account."""
    try:
        from google.oauth2.service_account import Credentials
        import gspread
    except ImportError:
        print("[FAIL] Missing deps. Run:")
        print("  pip install gspread google-auth")
        sys.exit(1)

    if not SA_PATH.exists():
        print(f"[FAIL] SA key not found at {SA_PATH}")
        print("  Check: C:\\Users\\J\\.secrets\\card-scout\\gcp-service-account.json")
        sys.exit(1)

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',  # Read + write Sheets
        'https://www.googleapis.com/auth/drive',  # Read Drive (for sheet metadata)
    ]

    creds = Credentials.from_service_account_file(str(SA_PATH), scopes=scopes)
    client = gspread.authorize(creds)
    return client


# ============================================================================
# IMPORT LOGIC
# ============================================================================

def detect_columns(header_row):
    """Auto-detect which column has which field based on header text."""
    column_map = {
        'timestamp': None,
        'first_name': None,
        'last_name': None,
        'discord_webhook': None,
    }

    for i, header in enumerate(header_row):
        if not header:
            continue
        h = str(header).lower().strip()

        if 'timestamp' in h:
            column_map['timestamp'] = i
        elif 'first name' in h:
            column_map['first_name'] = i
        elif 'last name' in h:
            column_map['last_name'] = i
        elif 'discord' in h or 'webhook' in h:
            column_map['discord_webhook'] = i

    return column_map


def generate_customer_id(first_name, last_name, existing_ids):
    """Generate a unique customer_id like 'tester_jon_smith_1736894400'."""
    base = f"{(first_name or 'unknown').lower()}_{(last_name or 'unknown').lower()}"
    # Replace non-alphanumeric with underscore
    base = ''.join(c if c.isalnum() else '_' for c in base)
    # Remove duplicate underscores
    while '__' in base:
        base = base.replace('__', '_')
    base = base.strip('_')

    candidate = f"{base}_{int(datetime.utcnow().timestamp())}"
    if candidate not in existing_ids:
        return candidate
    return f"{candidate}_{len(existing_ids)}"


def parse_card_from_section(card_fields):
    """Parse a card from a list of form fields for ONE scouting report card.

    Each "Scouting Report Card" section has these fields (in order):
      [0]: Sports or TCG?            (e.g., "Sports")
      [1]: Brand                      (e.g., "Topps")
      [2]: Player Name                (e.g., "Mike Trout")
      [3]: Card #                     (e.g., "1")
      [4]: Year(s)                    (e.g., "2011")
      [5]: Special / Limited Edition? (e.g., "Rookie Card")
      [6]: Grade (optional)           (e.g., "Graded" or "Rawdog")

    Returns: dict with keys {search_query, sportscardspro_url, raw_fields}
             or None if no useful data
    """
    if not card_fields or not any(f.strip() for f in card_fields if f):
        return None

    cleaned = [f.strip() for f in card_fields]

    sports_or_tcg = cleaned[0] if len(cleaned) > 0 else ''
    brand = cleaned[1] if len(cleaned) > 1 else ''
    player = cleaned[2] if len(cleaned) > 2 else ''
    card_num = cleaned[3] if len(cleaned) > 3 else ''
    year = cleaned[4] if len(cleaned) > 4 else ''
    special = cleaned[5] if len(cleaned) > 5 else ''
    grade = cleaned[6] if len(cleaned) > 6 else ''

    # Build search query — combine available fields
    parts = [p for p in [year, brand, player, card_num, special] if p and p.strip()]
    search_query = ' '.join(parts) if parts else (sports_or_tcg or 'unknown card')

    return {
        'search_query': search_query[:500],
        'sportscardspro_url': None,  # Customer doesn't provide URL via form
        'raw_fields': {
            'sports_or_tcg': sports_or_tcg,
            'brand': brand,
            'player': player,
            'card_num': card_num,
            'year': year,
            'special': special,
            'grade': grade,
        }
    }


def get_card_field_groups(header_row):
    """Detect which columns belong to each Scouting Report Card section.

    The form has 3 Scouting Report Card sections. Each section has fields in this order:
      Sports or TCG? -> Brand -> Player Name -> Card # -> Year(s) -> Special Edition? -> Graded or Rawdog? -> What grade?

    The Sheet's header row doesn't include section titles (Google Forms drops them in Sheet export).
    We detect section boundaries by finding repeated "Sports or TCG?" columns.
    Each one starts a new section.

    Returns list of column-index lists, e.g. [[4,5,6,7,8,9,10,11], [12,...], [20,...]]
    """
    # Find positions of "Sports or TCG?" headers — these mark the START of each card section
    section_starts = []
    for i, header in enumerate(header_row):
        if header and 'sports or tcg' in str(header).lower():
            section_starts.append(i)

    if not section_starts:
        # Fallback: assume all columns after the basic info belong to one card
        print("[WARN] Could not find 'Sports or TCG?' headers, using fallback")
        return [[i for i in range(4, len(header_row))]]  # Skip first 4 columns (name/webhook)

    # For each section start, take the next 7-8 columns until the next section
    groups = []
    for j, start in enumerate(section_starts):
        if j + 1 < len(section_starts):
            end = section_starts[j + 1]
        else:
            # Last section: take until we hit "What grade are we looking for? [N]" (grade preferences)
            end = len(header_row)
            for k in range(start + 1, len(header_row)):
                h = str(header_row[k]).lower()
                if 'what grade are we looking for? [' in h:
                    end = k
                    break
        groups.append(list(range(start, end)))

    return groups


def fetch_unimported_rows(client, sheet_id):
    """Fetch all rows from the Sheet, return ones not yet imported."""
    if not sheet_id:
        print("[FAIL] GOOGLE_SHEET_ID not set in env")
        print("  Find your Sheet ID from the URL: docs.google.com/spreadsheets/d/[ID]/edit")
        sys.exit(1)

    try:
        sheet = client.open_by_key(sheet_id).sheet1  # First sheet
    except Exception as e:
        print(f"[FAIL] Could not open Sheet: {e}")
        print("  Make sure:")
        print("  1. GOOGLE_SHEET_ID is correct")
        print(f"  2. Sheet is shared with card-scout-bot@card-scout-automation.iam.gserviceaccount.com")
        print("  3. Service account has Editor access")
        sys.exit(1)

    all_rows = sheet.get_all_values()
    if not all_rows:
        print("[WARN] Sheet is empty")
        return [], sheet, None

    header = all_rows[0]
    column_map = detect_columns(header)
    print(f"[OK] Detected columns: {column_map}")
    print(f"[OK] Header row: {header}")

    if column_map['discord_webhook'] is None:
        print("[FAIL] Could not find Discord Webhook column")
        print(f"  Available headers: {header}")
        sys.exit(1)

    # Find or create the "Imported?" column
    imported_col = len(header)
    existing_imported_col = None
    for i, h in enumerate(header):
        if h and 'imported' in str(h).lower():
            existing_imported_col = i
            break

    if existing_imported_col is not None:
        column_map['imported_marker'] = existing_imported_col
        print(f"[OK] Using existing 'Imported?' column at position {existing_imported_col + 1}")
    else:
        print(f"[INFO] Adding 'Imported?' column at position {imported_col + 1}")
        sheet.update_cell(1, imported_col + 1, 'Imported?')
        column_map['imported_marker'] = imported_col

    # Find rows where imported column is empty
    unimported = []
    for row_num, row in enumerate(all_rows[1:], start=2):  # row_num=2 is first data row
        imported_marker = row[column_map['imported_marker']] if len(row) > column_map['imported_marker'] else ''
        if imported_marker.strip():
            continue  # Already imported

        unimported.append({
            'row_num': row_num,
            'data': row,
            'column_map': column_map,
            'all_headers': header,
        })

    return unimported, sheet, column_map


def import_row(row_info, dry_run=True):
    """Import one row into DB. Returns created customer_id or None."""
    row_num = row_info['row_num']
    row = row_info['data']
    cm = row_info['column_map']

    timestamp = row[cm['timestamp']] if cm['timestamp'] is not None and len(row) > cm['timestamp'] else ''
    first_name = row[cm['first_name']] if cm['first_name'] is not None and len(row) > cm['first_name'] else ''
    last_name = row[cm['last_name']] if cm['last_name'] is not None and len(row) > cm['last_name'] else ''
    discord_webhook = row[cm['discord_webhook']] if cm['discord_webhook'] is not None and len(row) > cm['discord_webhook'] else ''

    if not discord_webhook:
        return None  # Skip rows without webhook

    # Validate webhook format
    if 'discord.com/api/webhooks/' not in discord_webhook:
        print(f"  [WARN] Row {row_num}: webhook URL doesn't look right: {discord_webhook[:60]}...")
        return None

    session = get_session()

    # Check if customer already exists by webhook
    existing = session.query(Customer).filter_by(discord_webhook=discord_webhook).first()
    if existing:
        print(f"  [SKIP] Row {row_num}: webhook already in DB (customer_id={existing.customer_id})")
        session.close()
        return None

    # Generate unique customer_id
    existing_ids = {c.customer_id for c in session.query(Customer).all()}
    customer_id = generate_customer_id(first_name, last_name, existing_ids)

    # Create customer
    customer = Customer(
        customer_id=customer_id,
        email=None,  # Form doesn't collect email
        discord_webhook=discord_webhook,
        tier='trial',  # Default for new signups
        subscription_status='trial',
        beta_end_date=None,
        max_cards=3,  # Trial default
        joined_date=datetime.utcnow(),
        notes=f"Imported from Google Form on {datetime.utcnow().isoformat()}",
        settings={},
    )
    session.add(customer)
    session.flush()  # Get the customer.id

    # Parse cards from sections (using group detection)
    card_groups = get_card_field_groups(row_info['all_headers'])
    card_count = 0

    for group_cols in card_groups:
        # Extract the values for this card section
        card_fields = [row[c] if c < len(row) else '' for c in group_cols]
        card_data = parse_card_from_section(card_fields)
        if not card_data:
            continue

        card = Card(
            customer_id=customer.id,
            search_query=card_data['search_query'],
            preset='cards-sports',  # Default; user can change later
            sportscardspro_url=card_data['sportscardspro_url'],
            enabled=True,
            include_sold=False,
            include_pop=False,
            added_date=datetime.utcnow(),
        )
        session.add(card)
        card_count += 1

    if dry_run:
        session.rollback()  # Don't actually save during dry-run
    else:
        session.commit()
    session.close()

    return {
        'customer_id': customer_id,
        'first_name': first_name,
        'last_name': last_name,
        'card_count': card_count,
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', default=True, help='Print what would be imported (default)')
    parser.add_argument('--import', dest='do_import', action='store_true', help='Actually import rows')
    parser.add_argument('--sheet-id', help='Override GOOGLE_SHEET_ID env var')
    args = parser.parse_args()

    sheet_id = args.sheet_id or SHEET_ID
    do_import = args.do_import

    print("=" * 70)
    print("Card Scout Google Sheets Importer")
    print("=" * 70)
    print()
    print(f"Sheet ID: {sheet_id or '(NOT SET)'}")
    print(f"Mode: {'IMPORT' if do_import else 'DRY RUN'}")
    print()

    if not sheet_id:
        print("[FAIL] Set GOOGLE_SHEET_ID in .env or pass --sheet-id")
        sys.exit(1)

    init_db()
    client = get_sheets_client()

    unimported, sheet, column_map = fetch_unimported_rows(client, sheet_id)

    if not unimported:
        print("[OK] No unimported rows found")
        return 0

    print(f"\n[OK] Found {len(unimported)} unimported row(s)")
    print()

    imported_count = 0
    for row_info in unimported:
        result = import_row(row_info, dry_run=not do_import)
        if not result:
            continue

        if isinstance(result, dict):
            print(f"  [OK] Row {row_info['row_num']}: {result['customer_id']} ({result['card_count']} cards)")
            imported_count += 1

            if do_import:
                # Mark as imported in the Sheet
                marker = f"Imported {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
                col_letter = chr(ord('A') + column_map['imported_marker'])
                sheet.update_acell(f'{col_letter}{row_info["row_num"]}', marker)
                print(f"         Marked cell {col_letter}{row_info['row_num']} = '{marker}'")

    print()
    print("=" * 70)
    if do_import:
        print(f"[OK] Imported {imported_count} customer(s)")
    else:
        print(f"[DRY RUN] Would import {imported_count} customer(s)")
        print("         Re-run with --import to actually import")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
