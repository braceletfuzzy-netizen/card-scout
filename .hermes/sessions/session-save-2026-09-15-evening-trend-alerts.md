# Session Save - Sept 15, 2026 (Evening - Trend-Aware Alerts Live)

## Time
Sept 15, 2026 ~6:30 PM (CDT)

## What we shipped

1. Populated pricing_bands with today's real data (10/12 cards captured):
   - 2 cards failed (Thigpen #7, Mewtwo #11 - known intermittent issues)
   - Real PSA 10 prices: Bo Jackson \$655, Jordan \$1,541, Black Lotus \$91,017, etc.
   - DB now has actual price history starting today

2. Fixed bug in capture_pricing_band_from_sc:
   - Old code expected tier keys 'used_price'/'complete_price' (legacy)
   - Real actor returns 'ungraded'/'psa_7'/... (verified Sept 15)
   - Added both key sets for backward compat

3. Added trend indicator (ADR-001 trend-aware alerts):
   - get_30day_average(session, card_id, tier) → avg from pricing_bands
   - format_trend_indicator(current, avg_30d) → '↑13% vs 30d avg \$578'
   - format_per_grade_ticker now takes optional session+card_id for trend
   - Bot wired up to pass these args

4. Tested trend math:
   - Simulated +31% scenario → showed '↑13% vs 30d avg' (math correct)
   - Unit tests for trend indicator (none/small/medium/large/Negative)
   - 'flat' threshold: within 2% = no arrow

## Commits today
- 9e50d97  trend-aware alerts (ADR-001) — populate pricing_bands, add vs 30d avg
- 7c85b71  session-save-2026-09-15 architecture + onboarding + key rotation
- 2090d3d  README update for sheets_importer
- fb7ca2d  sheets_importer bug fixes

## Current State

### pricing_bands table
- 10 rows for today (Sept 15, 2026)
- DB size: 92 KB (was 3 MB - check if correct)
- Cards covered: #1, #2, #3, #4, #5, #6, #8, #9, #10, #12
- Cards NOT covered today: #7 (Thigpen), #11 (Mewtwo) - intermittent failures

### Trend alerts
- Today: shows 'vs 30d avg \$X, flat' (no history yet)
- Tomorrow (1 day of data): still 'flat' (need 2+ days)
- After 7 days: real trend indicators start appearing
- After 30 days: full 30-day window for comparison

### Bot
- Wired to call format_per_grade_ticker with session + card.id
- Falls back gracefully if pricing_bands lookup fails
- Per-grade ticker now shows current price + 30d avg + arrow

## Next Time

1. Run bot tomorrow → second row in pricing_bands → first real trend comparison
2. Continue daily for 7 days → meaningful trends
3. After 30 days → full window
4. Onboard tester #2 (just run --import when they submit form)
5. Build V2 features (photo app, dashboard, etc.)

## Outstanding Items

- Tester #2 form submission (waiting on them)
- Mike Trout test row in Sheet (delete or import)
- 2 alert/URL year mismatches (cosmetic, waiting on Jim)
- Charizard ex PSA URL bug (waiting on Jim)
- GCP SA key rotation (DONE)

## Architecture Wins (Sept 14-15)

- ADR-001 storage vs pull decision framework
- pricing_bands table (10 lines SQL, \$0 cost)
- Trend-aware formatting
- Future-ready schema (UUID-ready, JSON-ready)
- Migration plan documented for 5K/50K/500K customer scale
