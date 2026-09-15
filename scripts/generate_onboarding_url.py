"""Generate pre-filled Google Form URLs for customer onboarding.

WHY: Google Forms doesn't natively support per-customer prefilled URLs,
but does support pre-filled URLs (just URL params like ?entry.X=value).
We programmatically build these URLs from the DB so each customer
gets a unique link with their current data already filled.

USAGE (after setup):
    python generate_onboarding_url.py jim
    python generate_onboarding_url.py --list-customers
    python generate_onboarding_url.py --setup  # one-time form config

ONE-TIME SETUP:
    1. Open the Google Form in edit mode
    2. Click 3-dot menu > "Get pre-filled link"
    3. Type sample values into each field
    4. Click "Get link" - Google gives you a URL with entry.X=VALUE params
    5. Copy that URL and paste it into form_config.json (created by --setup)

OUTPUT:
    https://docs.google.com/forms/d/e/FORM_ID/viewform?usp=pp_url
        &entry.123456=jim
        &entry.234567=standard
        &entry.345678=Card%201%2CCard%203
        &entry.456789=https%3A%2F%2Fdiscord.com%2Fapi%2Fwebhooks%2F...

Send this URL to your customer via email/Discord. When they click it,
the form opens with everything pre-filled. They review, adjust, submit.
"""
import sys
import json
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from db_models import init_db, get_session, Customer, Card


# ============================================================================
# FORM CONFIG — edit this once after setup, OR run --setup
# ============================================================================

CONFIG_FILE = Path(__file__).parent / "form_config.json"

# Default config template — user fills in after running --setup
DEFAULT_CONFIG = {
    "form_url": "https://docs.google.com/forms/d/e/YOUR_FORM_ID_HERE/viewform",
    "field_mappings": {
        "customer_id": "entry.123456",
        "customer_name": "entry.234567",
        "tier": "entry.345678",
        "tracked_card_ids": "entry.456789",
        "discord_webhook": "entry.567890",
        # Add more as needed
    },
}


def load_config():
    """Load form config from form_config.json, or use defaults."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return DEFAULT_CONFIG


def save_config(config):
    """Save form config to form_config.json."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def setup_config_interactive():
    """One-time setup: walk user through pasting form info."""
    print("=" * 70)
    print("CARD SCOUT FORM SETUP (one-time)")
    print("=" * 70)
    print()
    print("INSTRUCTIONS:")
    print()
    print("1. Open the Google Form in edit mode (you need to be logged in)")
    print("2. Click the 3-dot menu in the upper right")
    print("3. Click 'Get pre-filled link'")
    print("4. Type sample values into each field you want to pre-fill")
    print("5. Click 'Get link' button at bottom")
    print("6. Copy the URL it gives you (it'll have ?entry.XXXXXX=VALUE params)")
    print()
    print("Paste that URL below.")
    print()

    url = input("Form URL: ").strip()

    if not url or "docs.google.com" not in url:
        print("[FAIL] URL must be a docs.google.com URL")
        return False

    # Extract entry IDs from URL
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)

    print(f"\nFound {len(query)} entry field(s):")
    entry_fields = {}
    for k, v in query.items():
        if k.startswith("entry."):
            entry_fields[k] = v[0] if v else ""
            print(f"  {k} = {v[0] if v else ''}")

    print()
    print("Map each field to a customer attribute. (Press Enter to skip.)")
    print()

    field_mappings = {}

    for entry_id, sample_value in entry_fields.items():
        print(f"  Field {entry_id} had sample value: '{sample_value}'")
        print("  What should this represent?")
        print("    Options: customer_id, customer_name, tier,")
        print("             tracked_card_ids, discord_webhook, or your own label")
        label = input("    > ").strip()
        if label:
            field_mappings[label] = entry_id
        print()

    # Save
    base_form_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    config = {
        "form_url": base_form_url,
        "field_mappings": field_mappings,
    }
    save_config(config)

    print(f"[OK] Config saved to {CONFIG_FILE}")
    print()
    print("Next steps:")
    print("  python generate_onboarding_url.py --list-customers")
    print("  python generate_onboarding_url.py <customer_id>")
    return True


def generate_url(customer_id):
    """Generate a pre-filled URL for a specific customer."""
    config = load_config()
    if not config.get("field_mappings"):
        print("[FAIL] No field mappings configured. Run: python generate_onboarding_url.py --setup")
        return None

    session = get_session()
    try:
        customer = session.query(Customer).filter_by(customer_id=customer_id).first()
        if not customer:
            print(f"[FAIL] Customer '{customer_id}' not found")
            return None

        cards = session.query(Card).filter_by(customer_id=customer.id, enabled=True).all()

        # Build URL params
        base_url = config["form_url"]
        params = {}

        field_map = config["field_mappings"]

        if "customer_id" in field_map:
            params[field_map["customer_id"]] = customer.customer_id
        if "customer_name" in field_map:
            params[field_map["customer_name"]] = ""
        if "tier" in field_map:
            params[field_map["tier"]] = customer.tier or "trial"
        if "tracked_card_ids" in field_map:
            card_ids = ",".join(str(c.id) for c in cards)
            params[field_map["tracked_card_ids"]] = card_ids
        if "discord_webhook" in field_map:
            params[field_map["discord_webhook"]] = customer.discord_webhook or ""

        # Build full URL
        if params:
            query = urllib.parse.urlencode(params)
            full_url = f"{base_url}?{query}"
        else:
            full_url = base_url

        return full_url, customer, cards
    finally:
        session.close()


def list_customers():
    """List all customers in the DB."""
    session = get_session()
    try:
        customers = session.query(Customer).all()
        print("=" * 70)
        print("CARD SCOUT CUSTOMERS")
        print("=" * 70)
        print()
        for c in customers:
            card_count = sum(1 for card in c.cards if card.enabled)
            print(f"  {c.customer_id:20} tier={c.tier:10} cards={card_count}")
        print()
    finally:
        session.close()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python generate_onboarding_url.py --setup")
        print("  python generate_onboarding_url.py --list-customers")
        print("  python generate_onboarding_url.py <customer_id>")
        return 1

    arg = sys.argv[1]

    if arg == "--setup":
        success = setup_config_interactive()
        return 0 if success else 1

    if arg == "--list-customers":
        list_customers()
        return 0

    # Treat as customer_id
    result = generate_url(arg)
    if result is None:
        return 1

    url, customer, cards = result

    print("=" * 70)
    print(f"PRE-FILLED FORM URL FOR: {customer.customer_id}")
    print("=" * 70)
    print()
    print(f"Tier: {customer.tier}")
    print(f"Active cards: {len(cards)}")
    print()
    print("URL:")
    print(url)
    print()
    print("=" * 70)
    print()
    print("Send this URL to your customer. When they open it,")
    print("the form will have their data pre-filled.")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
