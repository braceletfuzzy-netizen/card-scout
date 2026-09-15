# Session Save - Sept 15, 2026 (Night - Dashboard + V2 Filter)

## Time
Sept 15, 2026 ~7:00 PM (CDT)

## What we shipped

1. Customer dashboard (Option A) — 4 files, 370 lines:
   - dashboard/app.py — Flask app, 6 routes, auth via webhook lookup
   - dashboard/requirements.txt
   - dashboard/README.md
   - dashboard/DEPLOY.md (3 hosting options: Render, Hetzner, HF Spaces)

2. Dashboard V2 enhancements:
   - Added PSA set URL + sportscardspro URL fields to add-card form
   - Added Edit feature (inline form pops out below each card)
   - Shows PSA + SC link status per card ('no URL' red text if missing)
   - Helper text explains URL formats

3. V2 grade-tiered listing filter:
   - scripts/listing_quality.py — scores listings 0-100
   - Heuristics: +positive (watchers, sold count, reasonable price), -negative (bulk, low price)
   - Thin markets bypass filter entirely (per spec)
   - Default threshold: 60
   - Wired into discord_alert_bot_v3.py after filter_matching_items
   - Test results: 5 test cases all score correctly

## Commits tonight
- 52e8dfc  dashboard — add PSA set URL + SC URL fields, edit feature
- (commit)   V2 grade-tiered listing filter — quality scorer + bot integration
- 37efc32  customer dashboard (Option A) — Flask, webhook auth, add/remove cards

## Decisions made

- Render.com deployment DEFERRED (user: funds tight, more money at end of month)
- Hetzner VPS still the right answer when 50+ customers
- Dashboard runs on localhost for development until then
- Edit feature added to dashboard (not just add/remove) — saves support time
- V2 filter built but not user-facing yet — bot uses sportscardspro primary, not eBay active

## Files Added/Modified Tonight

NEW:
- dashboard/app.py (450 lines after enhancements)
- dashboard/requirements.txt
- dashboard/README.md
- dashboard/DEPLOY.md
- scripts/listing_quality.py (220 lines)
- scripts/listing_quality.README.md

MODIFIED:
- scripts/discord_alert_bot_v3.py (added quality filter call site)

## Current State

### Dashboard (local only)
- 6 routes working
- Add/edit/remove cards via web UI
- Auth via Discord webhook lookup
- Edit feature lets customer fix URLs without support
- Run locally: `python dashboard/app.py` → http://localhost:5000

### V2 Listing Filter
- Built + tested + wired
- Won't activate until bot uses eBay active listings
- Or if Jim asks for cleaner signal on sportscardspro data

## Outstanding Items

- Onboard tester #2 (waiting on form submission)
- Decide on Mike Trout test row (delete or import)
- 2 alert/URL year mismatches (cosmetic)
- Charizard ex PSA URL bug (waiting on Jim)
- Dashboard deploy (deferred - save money)

## Next Time

1. Run dashboard locally — verify it works for you
2. Decide if tester #2 should use dashboard (skip Google Forms entirely)
3. If yes: deploy dashboard when funds available
4. Continue collecting pricing_bands data (trends become meaningful at 7+ days)
5. V3 features (per spec gaps): timeLeft, shipping cost, BIN/auction distinction
