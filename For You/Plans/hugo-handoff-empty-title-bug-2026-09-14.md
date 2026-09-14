# Hugo Handoff: eBay Actor Empty Title Bug

## ✅ RESOLVED 2026-09-14 by Hugo

**3-step fix** (commits `cc0f38c`, `eff2bf0`, `c7e964a`):

### Fix 1 (commit `cc0f38c`) — Code fixes
- Added `sportscardspro_url` to Card model
- Fixed `extract_pop_summary` best-match logic (was picking "Derek Parks" instead of "Derek Jeter")
- Added PSA retry on empty result (login flake)

### Fix 2 (commit `eff2bf0`) — Build deployment
- Pushed actor as build 0.4.10 (was sitting on 0.4.9 with the bug)
- Tagged `latest`, set as default build
- Title updated
- Optimization: skip smartSearch to halve query time

### Fix 3 (commit `c7e964a`) — Balanced approach
**THE REAL FIX** after reading the actor's README + main.js:
- Use `customSearchTerms=[search_query, preset_first_term]` instead of either:
  - Just customSearchTerms (works but limited to one query)
  - Full presets expansion (10 terms = hangs)
- Added `PRESET_FIRST_TERMS` mapping (top term from each preset's expanded list)
- 2 queries per card instead of 1 or 11

**Why this is the right answer**:
- Actor's `interpretQuery` returns single query for proper nouns (like "Derek Jeter") — no expansion benefit from smartSearch
- Full preset expansion (10 terms) takes 8+ minutes and times out
- Top preset term + exact search = best coverage in 30s

**Verification**:
- Jeter (#4, cards-sports): 30 items, 24 match, 12 deals in 31s
- Black Lotus (#10, cards-tcg): 16 items, 8 match, 4 deals in 21s
- Full 12-card run estimated ~10 minutes
- 0 empty-title items (actor returns `_summary` and "Shop on eBay" promos, both correctly filtered by `filter_matching_items`)

### Lesson Learned (added to memory)

**THE READ README PROTOCOL** (per my own checklist):
Before changing any actor/parser I didn't build, ALWAYS:
1. Read README.md + BUILD_STATUS.md + handoff doc
2. Read main.js header + top-of-file comments
3. Run single manual test with same inputs
4. Confirm bug exists in YOUR test before changing code

Cosmo got burned by not doing this. Won't happen again.

## TL;DR (original)


The eBay+Etsy actor (`fuzzy_bracelet/ebay-etsy-watch-scraper-monetized`) sometimes returns items with empty `title` fields. Bot v3 filters those out as "no match," resulting in 0 alerts being sent. Needs investigation.

## Symptoms

**When bot runs Jeter card** (live test 2026-09-14):
- Apify run starts: `K3NItv5A4eN1AqQhJ` (active) + `CN3BreidyurtU6ySl` (sold)
- Each run completes in 200+ seconds (preset hang was fixed)
- BUT bot reports "Found 1 items" with empty title
- Bot's filter rejects: "No items match 'Derek Jeter Topps Future Star'"
- 0 alerts sent

**When I run same actor directly** (manual test, 2026-09-14):
- Same params (smartSearch, no preset, 5 listings max)
- Completes in 40 seconds
- Returns 9 items, ALL with valid titles
- E.g., "1995 Topps - Future Star Derek Jeter #199", "1996 Topps Chrome #80 Derek Jeter BGS 9.5"

**Same code path. Same params. Different results.** This points to a race condition.

## What I Already Fixed (Today)

The bot was hanging for 11+ minutes per card. Root cause: preset expansion runs 8 separate Bright Data queries (one per preset term like "baseball card", "hockey card", etc.).

**Fix shipped (v4.274)** in `scripts/discord_alert_bot_v3.py`:

```python
# BEFORE (hanging):
"presets": [preset],
"customSearchTerms": [],

# AFTER (works in 40s):
"presets": [],
"customSearchTerms": [search_query],
```

This makes the bot use a single explicit query instead of expanding into 8.

## What Hugo Needs To Investigate

### Question 1: Why does the actor return empty titles in the bot's flow?

The actor's main.js has these key paths:
- Line 297: `if (title && listingId)` — saves item only if BOTH are present
- Line 259: `parseEbayListingsFromHtml(html, maxItems, soldOnlyFlag)` — the parser

When bot polls, it might be reading the dataset BEFORE the actor finishes writing items. So the first item might be a placeholder.

### Question 2: Does the actor's polling have a "wait for full dataset" step?

When Apify actor SUCCEEDS but dataset is still being populated, the items endpoint may return partial data.

Look at how `parseEbayListingsFromHtml` handles each `block` and where items get pushed.

### Question 3: Is there a dataset "completion" delay?

Some actors have a finalize step that runs after the main loop. If items are pushed to dataset before this step, early reads show partial data.

## Suggested Investigation Steps

1. Run the actor via Apify UI with same params as bot
2. Watch the dataset in real-time during the run
3. Check if items appear before SUCCEEDED status

OR

1. Read main.js to find the `pushData` calls
2. See if there's a finalize step after the main scraping loop
3. Add a delay or confirmation step before items are pushed

## Test That Reproduces

Run from terminal:
```bash
cd /c/Users/J/Documents/LLM/vostok-tools
python scripts/discord_alert_bot_v3.py --test-customer buddy_test_001
```

Wait for it to run. If you see "Found 1 items" with empty title, you've reproduced.

## Files Involved

| File | Lines | Purpose |
|---|---|---|
| `scripts/discord_alert_bot_v3.py` | 156-200 | `run_apify_search()` — polls until SUCCEEDED, then fetches items |
| `scripts/actors/ebay-etsy-watch-scraper-monetized/main.js` | 259-330 | `parseEbayListingsFromHtml()` — extracts items from HTML |
| `scripts/actors/ebay-etsy-watch-scraper-monetized/main.js` | 460-540 | Main scrape loop |

## Context

This is the only blocker for the live test on Jeter card. Other 11 cards in DB haven't been tested yet because this bug prevents the alert flow from completing for any card.

Once Hugo fixes the empty-title bug, all 12 cards will get alerts on the next MWF cron run.

## Working Knowledge

- Bot v3 is the production bot (replaces V2)
- Jim (`buddy_test_001`) gets alerts at 2pm Central on Mon/Wed/Fri
- Cron job ID: `2fb20f7ad396`
- Bot v3 + DB + grade filter + customer ID v2 all shipped
- The only P0 blocker is the empty-title bug

## How To Ping Hugo

If you're the user/operator, just say "Hugo" in chat and the next session will pick up from this doc + working notes.
