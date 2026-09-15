# `sheets_importer.py` — Google Form Responses → Card Scout DB

## What it does
Reads Google Form responses (via the linked Google Sheet) and creates new customers + cards in the Card Scout DB. Lets your new testers self-onboard through the form without you manually typing their data.

## Current scope (Option B — fast ship)
- Reads Sheet rows
- Creates customer with Discord webhook
- Creates card entries from form sections (raw text for now)
- Marks imported rows so they're not re-processed
- Dry-run by default (safe to test)

## Long-term scope (Option A — dashboard)
- Build a customer-facing web page that bypasses Google Forms
- Replace this script with a direct DB write from the dashboard
- This script becomes the **fallback** for people who use the form anyway

## One-time setup (~10 min)

### 1. Enable Google Sheets API
In `card-scout-automation` GCP project:
- Go to APIs & Services → Library
- Search "Google Sheets API" → Enable
- Confirm `card-scout-bot@card-scout-automation.iam.gserviceaccount.com` already has access (it does — same project)

### 2. Get your Sheet ID
After creating the Google Form, click the Responses tab → click the Sheets icon → "Create a new spreadsheet".
URL looks like: `https://docs.google.com/spreadsheets/d/1AbC...XyZ/edit`
**Sheet ID is the part between `/d/` and `/edit`**: `1AbC...XyZ`

### 3. Share Sheet with the service account
In the Google Sheet:
- Click "Share" (top right)
- Add: `card-scout-bot@card-scout-automation.iam.gserviceaccount.com`
- Permission: **Editor** (so we can mark imported rows)
- Send

### 4. Set Sheet ID in env
Add to `card-scout/.env` (already gitignored):
```
GOOGLE_SHEET_ID=1AbC...XyZ
```

## Usage

### Test (dry run, no changes)
```bash
python scripts/sheets_importer.py --dry-run
```

### Actually import
```bash
python scripts/sheets_importer.py --import
```

### Override Sheet ID for one run
```bash
python scripts/sheets_importer.py --import --sheet-id 1AbC...XyZ
```

## What it does to your form

| Form field | DB field | Notes |
|---|---|---|
| Timestamp | (audit only) | Used to detect new rows |
| First Name (You) | (notes field) | Not stored separately yet |
| Last Name (You) | (notes field) | Same |
| Discord Webhook | customers.discord_webhook | Required, validated |
| Scouting Report Card 1, 2, 3 sections | cards.search_query | Raw text for now; structured parsing in V2 |

## Customer tier default
- New signups → `tier='trial'`, `subscription_status='trial'`, `max_cards=3`
- Change manually after import if customer is paying

## Safety features
- **Dry-run by default** — prints what would be imported, does nothing
- **Idempotent** — skips rows where Discord webhook is already in DB
- **Marks imported rows** — won't double-import
- **Webhook validation** — skips rows with malformed URLs

## What needs work for V2
- Parse structured fields from "Scouting Report Card" sections (currently raw text)
- Auto-detect tier from form response (multiple choice question)
- Map sportscardspro URL if customer provides it
- Email notification on import (so you know tester #2 is in)

## When tester #2 submits the form
1. They fill the form, submit
2. Row appears in the linked Google Sheet
3. Run: `python scripts/sheets_importer.py --import`
4. Bot can start alerting them on the next cycle

**Total time from form submit to first alert**: ~1 minute (just import + next bot run)
