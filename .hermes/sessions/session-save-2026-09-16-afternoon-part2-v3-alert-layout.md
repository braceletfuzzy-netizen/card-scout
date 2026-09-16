# Session Save - Sept 16, 2026 (Afternoon Part 2 - V3 Alert Layout)

## Time
Sept 16, 2026 (afternoon, ~3 hours of work)

## What we shipped

### 1. Bot run for Jim (12 alerts)
- 11/12 alerts sent successfully (A-Rod had no matching listings this run)
- All alerts with new V3 layout

### 2. deal_detector.py (commit `8ebe702`)
- Per-grade lower-third threshold
- 12 self-tests pass
- Wired into bot

### 3. V3 alert layout (commit `fa71896`)
- **Order: Trend → Per-grade → Market Shape → Per-Grade Deals → Top listings**
- **Trend at top** (dedicated field, not in description)
- **Per-grade values moved up** (under trend)
- **Market Shape moved down** (with CI thirds calc)
- **Per-grade deals** (uses deal_detector.py)
- **Removed duplicate Trend Signal** at bottom

### Bugs found and fixed
1. **Duplicate Trend Signal** — was appended twice (once at top, once at bottom)
2. **"none found" message** — was checking wrong data source (summary.grade_breakdown which doesn't exist)
3. **Fix**: Build grade_breakdown from deals (parse grade from title text)

## Jim's beta notes addressed
- Spacing: more blank lines between sections (\n\n separators)
- Font: bigger formatting with ** bold ** for key terms
- Reordered per founder's spec

## Founder's beta notes addressed
- Per-grade market values at top under trend ✅
- Market Shape under per-grade values ✅
- Per-grade deal detection (where spread exists) ✅
- "Where there's no spread, there's no deal" ✅

## What still needs work
- **CI bands (90% CI + 70% CI)** — need to capture actual confidence intervals
- **Top 3 vs Top X on website** — founder undecided
- **Per-grade volume** (sold count, listings count) — partially captured
- **Larger font size** — Discord embeds don't really support this (limitation)

## Open fires still pending
1. URL ownership pattern (shower insight)
2. Pricing discussion (cost/card/month)
3. PSA unblock testing (different IP)
4. Phase 1 PSA search actor (October)
5. Website view for top deals (ad revenue)
6. Cron job for bot
7. Email field on form

## Files

| File | Status |
|---|---|
| `scripts/discord_alert_bot_v3.py` | PATCHED (140 inserts, 45 deletes, commit `fa71896`) |
| `scripts/deal_detector.py` | NEW (commit `8ebe702`) |
| `For You/Plans/card-hedge-api-discovery-2026-09-16.md` | NEW |
| `card_scout.db` | updated (12 pricing bands + 11 new snapshots today) |

## Memory note for next session

When conversation resumes:
- V3 alert layout is shipped and tested
- 11/12 Jim alerts delivered today
- All 3 customers can be tested (Jim has webhook, Hingle has webhook, cs_test is dead)
- Deal detector uses lower-third threshold (founder's spec)
- Per-grade detection works where spread exists
- PSA pop still failing (PSA blocked)

## When founder returns

Likely next fires:
1. URL ownership pattern (shower insight — make URLs required)
2. Pricing discussion (cost/card/month)
3. Build website view for deals (ad revenue)
4. Cron job for bot (auto-alerts every hour)
5. PSA unblock testing
