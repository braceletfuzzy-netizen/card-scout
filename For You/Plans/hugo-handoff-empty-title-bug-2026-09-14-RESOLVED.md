# RESOLVED — Sept 14, 2026

**Status**: ✅ DONE (see commit `cc0f38c`)
**Severity**: P0 (was blocking all alerts)

## What Cosmo Reported

> "Bot runs Jeter card, Apify run completes in 200+ seconds, but bot reports 'Found 1 items' with empty title. Bot's filter rejects with 'No items match Derek Jeter Topps Future Star'. 0 alerts sent."

## What I Found (3 actual bugs)

The "1 item with empty title" was the `_summary` object the eBay actor pushes at end-of-run (it has `title=None`). That's expected — `filter_matching_items` correctly rejects it (empty title fails keyword check). **The empty title was a red herring.**

The REAL bugs blocking alerts:

### Bug #1: Card model missing `sportscardspro_url` column
**File**: `scripts/db_models.py` line 82
**Symptom**: Bot's sold-data lookup silently skipped for all 5 cards with sportscardspro URLs
**Fix**: Added `sportscardspro_url = Column(String(500), nullable=True)` to Card class
**Why this matters**: Without this, `card.sportscardspro_url` raised AttributeError, and the bot's `getattr(card, 'sportscardspro_url', None)` silently returned None. The alert had no "Market Reference" section.

### Bug #2: `extract_pop_summary` returns first match instead of best match
**File**: `scripts/psa_pop_lookup.py` line 126
**Symptom**: Pop data returned wrong card ("Derek Parks" instead of "Derek Jeter" when filtering by "Derek")
**Fix**: Replaced `match = candidates[0]` with priority logic:
  1. Exact name match
  2. Starts-with match
  3. Longest name containing subject_filter
  4. First candidate (fallback)
**Note**: This function is only used in our test scripts — the bot has its own pop_data building logic (which uses `all(kw in name for kw in keywords)`) that's correct.

### Bug #3: PSA login flake not handled in bot wrapper
**File**: `scripts/psa_pop_lookup.py` line 91
**Symptom**: ~20% of PSA runs returned only diagnostic items (no data) due to brand-selection redirect on login. Bot silently got 0 cards.
**Fix**: Added retry logic — if first run returns no usable data, wait 2s and retry once. Prints "[POP] Run returned no usable data (login flake). Retrying..." then "[POP] ✓ Retry succeeded".
**Cost impact**: Doubles cost on flaky runs only (~20% of the time). Still well within $0.005-0.013/run budget.

## Verified Working End-to-End (after fixes)

Tested Jeter card full flow:

```
[APIFY] Searching: Derek Jeter Topps Future Star
[APIFY] Run started: 3hr2i9ChafehR3M93
[APIFY] Found 21 items (42s)

Matching: 19, Deals: 9
Sold: PSA 10 = $107.50
Trend: ACCELERATING_UP

=== ALERT MESSAGE ===
🎯 Deal Alert: Derek Jeter Topps Future Star
Found 9 listings below median ($20)
🔥 Trend: ACCELERATING UP
📊 Market Shape: Q1 $2 → Median $20 → Q3 $100
💵 Market Reference: PSA 10 $107.50 (+1.99 30d), 30 sold/30d
💹 Buy vs PSA 10 Spread: Buy $1 → $107.50 = 99% upside
💰 3 deal cards with eBay URLs
🔥 Trend Signal: 7d +900%, 30d +263.6%
```

All sections render correctly. PSA pop section would also render if PSA actor returns data (sometimes login flake prevents this run, but alert works without it — gracefully degrades).

## What Was NOT the Bug

- **Empty title in items**: This is the `_summary` object the actor pushes at end-of-run. The filter correctly excludes it (no keyword match). It's not "empty data" — it's intentional metadata.
- **Preset hang (200s)**: This was previously fixed in v4.274 (preset expansion removed). Each card now does a single explicit query, runs in ~40s.

## Files Changed

| File | Lines Changed | Fix |
|---|---|---|
| `scripts/db_models.py` | +1 | Added `sportscardspro_url` column |
| `scripts/psa_pop_lookup.py` | +30 | extract_pop_summary best-match + PSA retry on empty |

## Next Steps

1. **Run the bot** on `buddy_test_001` — all 12 cards should now get alerts.
2. **If PSA pop is still missing**: the retry should handle it. If not, the actor's brand-selection fix is needed (separate P0 from earlier handoff).
3. **Add `sportscardspro_url` to new cards**: any new card added via DB should already have this column (it's in the model now).


## Build Deployment (added Sept 14)

**Status**: ✅ Build 0.4.10 PUSHED to Apify (commit `eff2bf0`)

What I forgot to do initially:
- The bot code fixes were in commits `cc0f38c`, `bb5c764`, `718ad2a`
- BUT the eBay actor at `AtQq66Qn8FB7aLq2l` hadn't been re-pushed to Apify since build 0.4.9
- So all live test runs were still using the OLD code

**What I pushed now** (commit `eff2bf0`):
- `apify push --force` → build 0.4.10 with all main.js changes
- Updated actor metadata: tagged `latest`, set default build to 0.4.10, fixed title to "eBay + Etsy Watch Scraper (Monetized)"

**Performance improvement**:
- Old: smartSearch + customSearchTerms = 2 BD queries × ~50s = 100s per card
- New: empty smartSearch + customSearchTerms = 1 BD query × ~28s = 28s per card
- **3.5x faster** (12 cards × 28s = 5.6 min vs 20 min)

**Verified**:
- Build 0.4.10 SUCCEEDED
- 15 listings returned with valid titles
- 0 empty-title items (just the `_summary` metadata, expected)
