# `generate_onboarding_url.py` — Pre-filled Google Form URL Generator

## What it does
Generates a **per-customer pre-filled Google Form URL** from the Card Scout DB.

When a customer opens the URL, their form fields are already populated with:
- Customer ID
- Tier
- Their currently-tracked card IDs
- Discord webhook (if already set)

Customer reviews, makes any changes, submits.

## Why this exists
- **Customer #2 onboarding** before end of week (per Jon, Sept 14)
- Avoids manual "type all 12 card names" pain
- Reusable: same script works for customer #3, #4, ...

## Usage

### One-time setup (per Google Form)

```bash
python scripts/generate_onboarding_url.py --setup
```

You'll be prompted to paste the URL from Google Forms' **"Get pre-filled link"** menu. The script extracts the entry field IDs and saves them to `scripts/form_config.json`.

### Per-customer URL

```bash
python scripts/generate_onboarding_url.py buddy_test_001
# or whatever the customer's customer_id is
```

Output: a long URL with their data baked in. Send this to the customer.

### List customers (debugging)

```bash
python scripts/generate_onboarding_url.py --list-customers
```

## What gets pre-filled

| Field | Source | Notes |
|---|---|---|
| customer_id | customers.customer_id | Always set |
| customer_name | (empty) | No name field in Customer model — customer fills in |
| tier | customers.tier | "trial", "lite", "standard", etc. |
| tracked_card_ids | cards.id (comma-separated, enabled only) | e.g., "1,3,4,7,9,11" |
| discord_webhook | customers.discord_webhook | Only if set (else empty — customer enters their own) |

If a field doesn't have a mapping in `form_config.json`, it's skipped (not added to URL).

## Storage

- Config: `scripts/form_config.json` (one file, in scripts dir)
- Already `.gitignored` via `config/*.json` pattern? **No** — let me check.

Actually, `form_config.json` is **NOT gitignored** by default. It contains only field IDs (no secrets), so it's safe to commit. But if it ever stored tokens, we'd add it to `.gitignore`.

## Status
**Working** — verified end-to-end with Jim's data:
- 12 cards pre-filled
- tier pre-filled
- Discord webhook pre-filled

## Next steps when onboarding customer #2

1. Add customer to DB: `python scripts/customer_onboarding_v2.py tester2`
2. Get their Discord webhook URL
3. Run: `python scripts/generate_onboarding_url.py tester2`
4. Send URL to customer via email/Discord
5. Customer opens, confirms, submits

## Known limitations

- **No field validation** — if form has changed structure since config was generated, URLs may point at wrong fields
- **No customer name in URL** — Customer model doesn't have `name` field yet (add to model when we need it)
- **No expiration on URLs** — same URL works forever until you regenerate config
- **Discord webhook in plain text URL** — fine for existing customers, but for NEW customers, leave it blank and have them enter their own
