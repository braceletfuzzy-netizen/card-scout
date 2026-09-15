# Session Save - Sept 15, 2026 (Morning - Sheets Importer + Pricing Bands)

## Time
Sept 15, 2026 ~10:00 CDT (UTC-5)

## What we did this session

### 1. ADR-001: storage vs pull decision
Jon raised a foundational architecture question: when to store/lookup vs always pull?
His concern: future-ready without over-engineering. Worried about 'explode' scenario requiring rewrite.

Decision locked: **Store what we ask more than once. Pull what changes daily.**
Documented migration triggers for SQLite -> PostgreSQL -> ClickHouse -> Meilisearch.
Cost trajectory: always sub-5% of revenue at every scale.

### 2. pricing_bands table (commit 132ea59)
Built the table Jon approved:
- 24 columns: card_id, band_date, per-grade low/high/volume for 6 tiers
- TTL=30 days, auto-cleanup on bot startup
- 5/5 verification tests pass

Storage: 12 cards x 30 days = ~360 rows = ~55KB (trivial)
Hooked into discord_alert_bot_v3.py - every SCPRO lookup captures a band.

### 3. Pre-filled Google Form URL generator (commit 3cba8b0)
Jon wanted per-customer pre-filled URLs for onboarding form.
Built scripts/generate_onboarding_url.py:
- One-time --setup config (paste 'Get pre-filled link' URL)
- Per-customer URL generation with customer_id, tier, card IDs, webhook

BUT — discovered Jon's actual form is much more complex than expected:
- 5 sections (multi-page form)
- Customer-driven card selection (sections 2-4)
- Fields like 'Sports or TCG?', 'Graded or Rawdog?'

CONCLUSION: Pre-filled URL approach DOESN'T FIT this form. Customer-driven
card selection means pre-filling with Jim's data doesn't help new testers
(picking different cards).

### 4. Option B: Google Sheets importer (commit [latest])
Jon's decision: B for now (form + importer), A (dashboard) later long-term.

Built scripts/sheets_importer.py:
- Reads Sheet rows via gspread
- Validates Discord webhook URL
- Creates customer (trial tier, 3 cards max)
- Creates cards from form sections (raw text for now)
- Marks imported rows in 'Imported?' column
- Dry-run by default, idempotent
- gspread 6.2.1 installed

Setup needed (one-time):
1. Enable Google Sheets API in card-scout-automation GCP project
2. Share Sheet with card-scout-bot@card-scout-automation.iam.gserviceaccount.com (Editor)
3. Set GOOGLE_SHEET_ID in .env

Time from form submit to first alert: ~1 minute.

## Today's commits
- 132ea59: pricing_bands table
- 4aa0c38: ADR-001 storage vs pull decision
- ee4f214: session save (Sept 14)
- 3cba8b0: pre-filled URL generator (kept for future 'Update Roster' form)
- [latest]: sheets_importer.py + README

## Standing items
- GCP key rotation (3 min, security) — STILL PENDING from Sept 14
- Enable Google Sheets API + share Sheet with SA (10 min) — NEW, blocker for importer
- Get GOOGLE_SHEET_ID from form responses Sheet

## Open question
- Long-term: build customer dashboard page (~6 hrs, $5/mo Hetzner, branded)
- Replaces both form + importer eventually
