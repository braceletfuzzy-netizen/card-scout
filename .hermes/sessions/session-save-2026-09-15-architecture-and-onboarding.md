# Session Save - Sept 15, 2026 (Morning + Afternoon - Architecture + Form Setup + Key Rotation)

## Time
Sept 15, 2026 ~10:00 AM - ~3:30 PM (Central Daylight Time)

## Big picture
- Completed architecture decision (ADR-001: pull vs store)
- Built pricing_bands table (30-day pricing history)
- Built pre-filled Google Form URL generator
- Built Google Sheets → DB importer for customer #2 onboarding
- Rotated GCP service account key (security incident closed)
- Verified all 3 flows end-to-end

## Completed Actions

1. ADR-001 written + committed:
   - Storage vs pull decision framework (when to store, when to pull)
   - Future-ready design pattern (SQLite → PostgreSQL → ClickHouse)
   - Migration triggers at 5K / 50K / 500K customers
   - Schema portability principles (UUID IDs, JSON cols, FK cleanliness)
   - File: For You/Plans/architecture-decision-record-storage-vs-pull-2026-09-14.md

2. pricing_bands table built (commit 132ea59):
   - 6 grade tiers × 3 fields (low/high/volume) per day per card
   - Bot auto-captures every sportscardspro lookup
   - Daily cleanup script (cleanup_old_pricing_bands.py)
   - Verification script (verify_pricing_bands.py) - 5/5 pass
   - README updated

3. generate_onboarding_url.py (commit 3cba8b0):
   - Pre-filled Google Form URL generator
   - --setup wizard walks through pasting "Get pre-filled link" URL
   - --list-customers shows Jim
   - Generates URLs with customer_id, tier, tracked_card_ids pre-filled
   - For status checks, not onboarding (form too complex for full pre-fill)

4. sheets_importer.py (commits fb7ca2d, 2090d3d):
   - Reads Google Form responses from linked Sheet
   - Imports new customers + cards into Card Scout DB
   - Card parsing: groups 7 fields per "Scouting Report Card" section
   - Bug fixes:
     * dry-run was actually committing (now rollback)
     * every cell parsed as own card (now groups fields)
     * duplicate "Imported?" columns on each run (now dedupes)
   - .env auto-loaded via python-dotenv
   - README updated
   - Cleaned up polluted test rows from earlier dry-runs

5. Security incident CLOSED:
   - New GCP SA key created (d89c984fd18ed5207095eecd3b1a8127a67f9d5)
   - Old key (d241a87c...) deleted from GCP
   - New JSON saved to C:\Users\J\.secrets\card-scout\gcp-service-account.json
   - Plaintext copy in Documents folder deleted
   - Script verified working with new key

## Key Decisions (today)

- ADR-001: Always pull when cost is low. Store ONLY when (a) needed for trend math,
  (b) expensive to re-pull, (c) referenced frequently. Schema portability > engine choice.

- Pricing bands table = 10 lines SQL, $0 cost, future-proof for trend charts.
  Don't over-engineer (no ClickHouse yet). Migration plan documented for 5K+ customers.

- Pre-filled URL approach parked - form is too complex (3 Scouting Report Card
  sections, customer picks their own cards). Use it for status updates later.

- Sheets importer = Option B (today). Customer dashboard (Option A) parked for V2.
  Form → Sheets → DB → bot alerts = 1 minute from form submit to first alert.

- GCP SA key rotation = hygiene, not damage control. Key only existed ~30 seconds
  in git before being soft-reset.

## Commits today (card-scout)

- 2090d3d  README update for sheets_importer
- fb7ca2d  sheets_importer bug fixes (dry-run, card parsing, dedupe)
- e5e7e9d-ish  generate_onboarding_url + sheets_importer initial
- 132ea59  pricing_bands table

## Current State

### Card Scout
- 12 cards in DB (Jim's roster, all working)
- pricing_bands table populated (synthetic + ready for real data)
- sheets_importer end-to-end working
- GCP SA key rotated
- 1 test row in Sheet (Mike Trout, will need to delete or import as trial customer)

### Pre-filled URL config
- script ready at scripts/generate_onboarding_url.py
- --setup command walks through pasting form's "Get pre-filled link" URL
- Currently not run yet (parked since form is too complex for full pre-fill)

### Blocked
- Charizard ex PSA URL bug (Surging Sparks vs Pokemon 151) - waiting on Jim
- 2 alert/URL year mismatches (Henry Aaron, Barry Sanders) - cosmetic
- 1 test row in Sheet from earlier (Mike Trout) - need to delete or import

### Queued
- Onboard customer #2 (tester waiting)
- V2 dashboard (Option A) - 6 hours, $5/mo hosting
- V2 grade-tiered listing filter (parked spec)
- TCG V2 data sources (parked - tcgtracking.com/tcgapi/v1/scan for photo app)

## Lessons Learned (today)

- PowerShell path quirk: cd "/c/Users/..." gets prefixed with C:\ → invalid path
  Fix: use Windows-style path in PowerShell, OR run from Git Bash
- browser_use clicks don't work on unfocused Chrome windows (background mode)
  Fix: user must click Add key in Chrome directly, file downloads to Downloads/Documents
- Google Forms "Get pre-filled link" works for checkboxes but form structure
  (3 Scouting Report Card sections) makes it impractical for first-time onboarding
- GCP SA keys: create new BEFORE deleting old, save JSON immediately,
  rotate regularly as hygiene
- Lazy-load SQLAlchemy bug: accessing relationship attrs after session.close()
  raises DetachedInstanceError - use try/finally pattern

## Next Steps (when back from break)

1. Decide what to do with Mike Trout test row in Sheet (delete or import)
2. When tester #2 submits form: run --import
3. Pre-fill URL: setup when ready (or skip if not needed)
4. V2 prep: dashboard, photo app research

## Files Created/Modified Today

NEW:
- For You/Plans/architecture-decision-record-storage-vs-pull-2026-09-14.md (109 lines)
- scripts/generate_onboarding_url.py (249 lines)
- scripts/generate_onboarding_url.README.md (83 lines)
- scripts/sheets_importer.README.md (94 lines)
- scripts/db_models.README.md (60 lines)
- scripts/cleanup_old_pricing_bands.py (37 lines)
- scripts/verify_pricing_bands.py (132 lines)
- card-scout/.env (47 lines, gitignored)
- .hermes/sessions/session-save-2026-09-15-architecture-and-onboarding.md (this file)

MODIFIED:
- scripts/db_models.py (added PricingBand model + helpers)
- scripts/discord_alert_bot_v3.py (auto-capture pricing_bands on each alert)

## Security Status
- ✅ GCP SA key rotated (old deleted, new active)
- ✅ New key ONLY in C:\Users\J\.secrets\card-scout\ (gitignored, outside repo)
- ✅ No plaintext secrets in any repo dir

## Standing Items
- [DONE] GCP key rotation
- [PENDING] Decide on Mike Trout test row (delete or import)
- [PENDING] Onboard tester #2 when they submit form
