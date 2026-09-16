# Session Save - Sept 16, 2026 (Morning Part 2 - Dashboard PSA Pop Integration)

## Time
Sept 16, 2026 ~7:30 AM (CDT)

## What we shipped this session

### 1. V3 Stock-Class Ticker (commit `e20cc14`)

Founder's big insight (PSA grades as stock classes) is now implemented:
- DB: 4 new columns (psa_total_pop, psa_10_pop, psa_9_pop, psa_pop_fetched_at)
- `scripts/psa_pop_persister.py`: fetch + persist + rarity + premium
- `scripts/ticker_formatter.py`: format_stock_class_section()
- `scripts/discord_alert_bot_v3.py`: wires section into alerts

### 2. PSA Pop for 2/12 Jim cards (commit `26800ad`)

Tried web search for all 12 cards' PSA URLs. Reality: web search is unreliable.
- 4 of 8 web-searched URLs pointed to wrong sets
- 1 (Charizard ex) returned data for Exeggcute instead of Charizard
- Only 1 real fetch succeeded: Hank Aaron (45 graded, 0 PSA 10, 5 PSA 9)
- Bo Jackson synthetic data for testing

### 3. Long-term PSA plan (commit `6f11447`)

Founder's directive: "We will eventually create our own since we have the
time and infrastructure to do this." In response to Reddit-promoted
third-party PSA pop API. Captured long-term plan:
- Phase 1: PSA search actor (~20 hours) — TARGET: October as V2.5-V3 project
- Phase 2: Pop history tracking (1 week)
- Phase 3: Public API (1 week)

### 4. Dashboard V3 integration (commit `e76dced`)

When a user saves a card with a new PSA URL, auto-fetch pop data.
Display pop stats in the card meta-row. Applied to BOTH sports and TCG
sections. Cleared URLs now clear pop data too.

## Current state

### Database

| Customer | Cards | Pop data | Notes |
|---|---|---|---|
| buddy_test_001 (Jim) | 12 | 2/12 | Bo Jackson synthetic + Hank Aaron real |
| cs_CZYAJYA00001 | 1 | 0 | test customer |
| hingle_mccringleberry (Hingle) | 3 | 0 | trial, beta #2 |

### Files

| File | Status |
|---|---|
| `scripts/db_models.py` | updated: 4 new PSA pop columns |
| `scripts/migrate_add_psa_pop.py` | NEW (migration) |
| `scripts/psa_pop_persister.py` | NEW (250 lines, 16 self-tests) |
| `scripts/ticker_formatter.py` | updated: stock-class section |
| `scripts/discord_alert_bot_v3.py` | updated: wires section into alerts |
| `dashboard/app.py` | updated: auto-fetch + display |
| `For You/Plans/psa-grades-as-stock-ticker-2026-09-16.md` | NEW (design) |
| `For You/Plans/psa-pop-data-long-term-2026-09-16.md` | NEW (long-term plan) |

## Decisions captured

1. **Build our own PSA pop API** — no third-party APIs
2. **Phase 1 PSA search actor: October** (V2.5-V3 project, ~20 hours)
3. **Manual PSA URL entry via dashboard** (short-term, current implementation)
4. **Auto-fetch pop on URL save** (Sept 16 dashboard enhancement)
5. **Stock-class section as core feature** (not cosmetic)
6. **Rarity thresholds**: ≤1/≤5/≤15/>15% (RARE/SCARCE/COMMON/PLENTIFUL)

## Today's grand total (Sept 16)

| Feature | Status | Commit |
|---|---|---|
| Webhook branding fix | ✅ | (yesterday `de8b550`) |
| V3 stock-class ticker | ✅ | `e20cc14` |
| PSA pop for 2/12 Jim cards | ✅ | `26800ad` |
| Long-term PSA plan | ✅ | `6f11447` |
| Dashboard auto-fetch pop | ✅ | `e76dced` |

**Total Sept 16 so far**: 5 features, ~3 hours of work, $0 spent.

## What's next

### Immediate (when ready)

1. **Refresh Bo Jackson with REAL data** — replace synthetic 1731/23/715 with real PSA pop
2. **Add more cards to dashboard** — founder browses PSA.com, finds URLs, pastes via dashboard
3. **Run bot** — verify alerts now show stock-class hierarchy for cards with pop

### Short-term (when convenient)

1. **Volume by grade in ticker** (V3 enhancement, 2 hours)
2. **Cron job for auto-alerts** (30 min)
3. **Email field on form** (V4, ~1 hour) — needed for V2 Stripe webhook

### Long-term

1. **Phase 1 PSA search actor** — October V2.5-V3 project (~20 hours)
2. **3-tier pricing** — after first paying customer
3. **Render deploy** — end of month
4. **V2 webhook handler** — when ready (~8 hours)

## Reference docs (all committed)

- `For You/Plans/psa-grades-as-stock-ticker-2026-09-16.md` — stock-class design
- `For You/Plans/psa-pop-data-long-term-2026-09-16.md` — long-term Phase 1-3
- `scripts/psa_pop_persister.py` — pop fetcher + rarity + premium helpers
- `scripts/migrate_add_psa_pop.py` — DB migration
- `scripts/ticker_formatter.py` — stock-class section
- `scripts/discord_alert_bot_v3.py` — alert integration
- `dashboard/app.py` — auto-fetch + display

## Memory note for next session

When conversation resumes:
- PSA pop is in DB schema (4 new columns)
- Dashboard auto-fetches pop on URL change
- Bo Jackson has synthetic data; Hank Aaron has real data
- 10/12 Jim cards still need PSA URLs (manual via PSA.com browse)
- Phase 1 PSA search actor: deferred to October
- Memory: founder's name is NOT Jim — Jim is the beta tester
