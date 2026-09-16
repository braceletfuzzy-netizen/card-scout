# Session Save - Sept 16, 2026 (Morning - V3 Stock-Class Ticker)

## Time
Sept 16, 2026 ~7:10 AM (CDT)

## 🎉 HEADLINE
**V3 stock-class ticker is LIVE.** Founder's big insight (PSA grades as
stock classes) is now implemented and rendering in Discord alerts.

The new section transforms Card Scout from "price tracker" into the
"Bloomberg terminal for graded cards."

## What we shipped this morning

### A. Webhook branding fix (already done)

`python scripts/patch_webhook.py --all` patched:
- ✅ buddy_test_001 (Jim's beta customer #1) — binoculars logo
- ✅ hingle_mccringleberry_1789525909 (Hingle, beta #2) — binoculars logo
- ⚠️ cs_CZYAJYA00001 (test) — failed (fake webhook, expected)

### B. V3 Stock-Class Ticker (the big one)

**Founder's insight (verbatim)**:
> "PSA 10 is the A series, PSA 9 is the B series, PSA 8 is the C series,
> etc. Each card is like a share of stock. Once a card is graded and
> verified by PSA, it becomes essentially a stock certificate worth
> whatever the market value is. There are a lot of old school market
> mechanics that happen. One of those is that the pricing band is very
> wide."

**What we built** (commit `e20cc14`):

1. **DB migration** (`scripts/migrate_add_psa_pop.py`):
   - Added 4 columns to `cards` table:
     - `psa_total_pop` — total PSA-graded count
     - `psa_10_pop` — PSA 10 count (A-class)
     - `psa_9_pop` — PSA 9 count (B-class)
     - `psa_pop_fetched_at` — TTL timestamp (7 days)

2. **`scripts/psa_pop_persister.py`** (NEW, 250 lines):
   - `fetch_and_persist_pop()` — fetches PSA pop via Apify actor + saves to DB
   - `compute_rarity()` — returns RARE/SCARCE/COMMON/PLENTIFUL
   - `get_stock_class_label()` — A/A-/B/C/D mapping
   - `compute_premium()` — PSA 10 / PSA 9 ratio
   - 16 self-tests pass

3. **`scripts/ticker_formatter.py`** (UPDATED):
   - New function `format_stock_class_section(card)`:
     - Rarity emoji (⭐ RARE / 💎 SCARCE / 📊 COMMON / 📈 PLENTIFUL)
     - Stock-class label
     - Rarity %
     - Total outstanding

4. **`scripts/discord_alert_bot_v3.py`** (UPDATED):
   - Wires stock-class section into Discord alerts
   - Only shows when `card.psa_total_pop` is set

5. **`For You/Plans/psa-grades-as-stock-ticker-2026-09-16.md`** (NEW, 165 lines):
   - Design doc with stock-market → card-market mapping
   - Implementation plan
   - Future features (historical pop, pop velocity)

## Real output (Bo Jackson with synthetic pop data)

```
🎖️ Stock-Class Hierarchy
  💎 **PSA 10** = **SCARCE** (1.3% of pop, only **23** exist)
  • PSA 9 = B-class (715 exist)

🏷️ Total outstanding: 1,731 graded

📊 Per-Grade Ticker
  PSA 10: $655.34 (23 sold/30d)
  PSA 9: $107.50 (30 sold/30d)

💎 Premium: PSA 10 trades at 6.1× the PSA 9 price (rare-asset premium)
```

## Stock-market → card-market mapping

| Stock concept | Card equivalent | Data source |
|---|---|---|
| Ticker symbol | Card ID | cards.search_query |
| Outstanding shares | Total PSA population | cards.psa_total_pop |
| A-class shares | PSA 10 population | cards.psa_10_pop |
| B-class shares | PSA 9 population | cards.psa_9_pop |
| Last traded price | Recent sale price | sportscardspro per-grade |
| Volume traded | Sales per grade per period | sportscardspro sold_count |
| Market cap | Population × typical price | computed |
| 52-week high/low | 30-day range | pricing_bands |
| Stock chart | Price history per grade | pricing_bands over time |

## Rarity thresholds

| Rarity label | PSA 10 % of total | Example |
|---|---|---|
| ⭐ RARE | ≤ 1% | 5/500 |
| 💎 SCARCE | 1-5% | 23/1731 (Bo Jackson) |
| 📊 COMMON | 5-15% | 100/1000 |
| 📈 PLENTIFUL | > 15% | 200/1000 |
| ❓ UNKNOWN | (no data) | — |

## Current state

### Database

- 3 customers (Jim, test, Hingle)
- 16 cards total
- **NEW**: psa_total_pop/psa_10_pop/psa_9_pop/psa_pop_fetched_at columns on cards
- Bo Jackson (card #1): manually populated with 1731/23/715 for testing

### Files committed

| Commit | Description |
|---|---|
| `e20cc14` | V3 stock-class ticker — PSA grades as stock classes |
| `0ce02f7` | session-save (yesterday, Hingle alerts) |

## Decisions captured

1. **Stock-class hierarchy as core feature** — not cosmetic
2. **Rarity thresholds**: 1/5/15% boundaries (RARE/SCARCE/COMMON/PLENTIFUL)
3. **PSA pop cache TTL: 7 days** — saves API cost, data doesn't change rapidly
4. **Stock-class section is optional** — skip if no pop data (non-fatal)
5. **PSA 10 = A class always** (highest value tier)

## What's next

### Immediate (when ready)

1. Fetch real PSA pop for Jim's other 11 cards (~5 min via PSA actor)
2. Run bot for Jim → verify all alerts show stock-class hierarchy
3. Add pricing_bands-style historical pop tracking (V4)

### V3 enhancements (when ready)

1. **Volume by grade** in ticker (sales count per grade per period)
2. **Premium context** (PSA 10 / PSA 9 ratio) inline
3. **Historical pop trends** (when did PSA 10 pop last grow?)
4. **Per-grade pop depth** (PSA 8, PSA 7 pop counts — currently only PSA 9 + PSA 10)

### V4 / deferred

1. **Email field on form** — needed for V2 Stripe webhook matching
2. **V2 webhook handler** — when ready (~8 hours)
3. **3-tier pricing** — after first paying customer
4. **Render deploy** — end of month

## Today's grand total (Sept 16)

| Feature | Status | Commit |
|---|---|---|
| Webhook branding fix (existing customers) | ✅ | (existing `de8b550`) |
| V3 stock-class ticker (NEW) | ✅ | `e20cc14` |

**Total Sept 16 so far**: 2 features, ~3 hours of work, $0 spent.

## Open questions

1. **Fetch real PSA pop for Jim's other 11 cards now?** (5 min, $0.05 cost)
2. **Add email field to form?** (V4 work, needed for V2 webhook)
3. **Volume by grade in ticker?** (2 hours, V3 enhancement)
4. **Cron job for bot?** (30 min, auto-alerts)

## Reference docs (all committed)

- `For You/Plans/psa-grades-as-stock-ticker-2026-09-16.md` (165 lines) — design
- `scripts/migrate_add_psa_pop.py` (85 lines) — DB migration
- `scripts/psa_pop_persister.py` (250 lines) — fetch + compute helpers
- `scripts/ticker_formatter.py` (UPDATED) — stock-class section
- `scripts/discord_alert_bot_v3.py` (UPDATED) — alert integration
- `For You/Plans/architecture-decision-record-storage-vs-pull-2026-09-14.md` — ADR-001 (store-vs-pull rule, motivated the persistence)

## Memory note for next session

When conversation resumes:
1. PSA pop persistence is live — DB has 4 new columns
2. Bo Jackson has synthetic pop data; needs real fetch to verify
3. 11 other cards need PSA pop populated
4. Stock-class section will render automatically when card.psa_total_pop is set
5. Memory note: founder's name is NOT Jim — Jim is the beta tester
