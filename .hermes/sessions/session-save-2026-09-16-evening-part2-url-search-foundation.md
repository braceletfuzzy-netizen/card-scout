# Session Save - Sept 16, 2026 (Evening Part 2 - URL Search Foundation)

## Time
Sept 16, 2026 (evening, founder "quick save" request)

## What we shipped this session

### URL Search Foundation (founder insight)
> "the more pricing points the better, as long as we can get
> our URL search figured out"

### 3 modules built (47 tests pass):
1. `scripts/url_parser.py` — Extract IDs from URLs (12 tests)
   - PSA: /pop/{category}/{year}/{set}/{spec_id}
   - eBay: /itm/{item_id}
   - Sportscardspro: /product/{id} AND /game/{slug}
   - Pricecharting: /console/{slug-id} AND /game/{slug}

2. `scripts/url_orchestrator.py` — Coordinate multi-source lookups (5 tests)
   - url_first mode when any valid URL exists
   - search_only mode as fallback
   - Counts pricing points per card (max 4)

3. `scripts/url_resolver.py` — Drill set URLs to specific cards (30 tests)
   - Card name extraction from search queries
   - Card number extraction
   - URL slug building
   - Fixed bug: rstrip("'s") was breaking "Topps" → "topp"

### Coverage Analysis (Jim's 12 cards)
| Source | Coverage |
|---|---|
| Direct PSA ID | 5/12 (42%) |
| Direct SCPRO URL | 4/12 (33%) |
| TCG product-level | 4/12 (33%) |
| Need fuzzy search | 7/12 (58%) |

## Files updated today (Sept 16 grand total)

### Code (10 files)
- `scripts/deal_detector.py` (NEW, 268 lines, 12 tests)
- `scripts/url_parser.py` (NEW, 286 lines, 12 tests)
- `scripts/url_orchestrator.py` (NEW, 245 lines, 5 tests)
- `scripts/url_resolver.py` (NEW, 358 lines, 30 tests)
- `scripts/discord_alert_bot_v3.py` (PATCHED — V3 alert layout)
- `dashboard/app.py` (PATCHED — auto-fetch pop on URL change)
- `scripts/psa_pop_persister.py` (NEW, 308 lines, 16 tests)
- `scripts/migrate_add_psa_pop.py` (NEW, 89 lines)
- `scripts/patch_webhook.py` (NEW, 83 lines)

### Plans (8 files)
- `For You/Plans/pricing-decision-2026-09-16.md` (NEW, 90 lines)
- `For You/Plans/cost-breakdown-2026-09-16.md` (NEW, 129 lines)
- `For You/Plans/cheaper-aggregation-paths-2026-09-16.md` (NEW, 146 lines)
- `For You/Plans/cost-cutting-roadmap-2026-09-16.md` (NEW, 236 lines)
- `For You/Plans/cost-cutting-roadmap-NOTEPAD-2026-09-16.txt` (NEW)
- `For You/Plans/data-provider-comparison-2026-09-16.md` (NEW, 155 lines)
- `For You/Plans/z-score-framework-2026-09-16.md` (NEW, 138 lines)
- `For You/Plans/psa-pop-data-long-term-2026-09-16.md` (NEW, 152 lines)
- `For You/Plans/card-hedge-api-discovery-2026-09-16.md` (NEW, 172 lines)
- `For You/Plans/card-hedge-pricing-concern-2026-09-16.md` (NEW, 105 lines)
- `For You/Plans/psa-pop-discovery-current-state-2026-09-16.md` (NEW, 106 lines)

### Session saves (3 files)
- `.hermes/sessions/session-save-2026-09-16-afternoon-part2-v3-alert-layout.md` (NEW)
- `.hermes/sessions/session-save-2026-09-16-afternoon-pricing-cost-optimization.md` (NEW)
- `.hermes/sessions/session-save-2026-09-16-evening-ebay-signup-done.md` (NEW)
- `.hermes/sessions/session-save-2026-09-16-evening-part2-url-search-foundation.md` (NEW, this file)

## Memory updated (Sept 16)

- Added z-score framework insight to memory (cross-session)
- Current memory: 52% — 2,632/5,000 chars

## Decisions captured today

### PRICING
- Casual $15 / Standard $30 / Dealer $75 / Pro $150
- Pull frequency is the lever
- Margins 71-95% across scales

### COST CUTTING ROADMAP
- Stage 0: 0-10 customers (Apify)
- Stage 1: 10+ customers (eBay Buy API FREE)
- Stage 2: 25+ customers (+ Pricecharting $6/mo)
- Stage 3: 50+ customers (+ Card Ladder $20/mo)
- Stage 4: 500+ customers (DIY)
- Stage 5: 1000+ customers (strategic partnerships)

### DATA STACK
- eBay Browse API (free) — listing data + spread
- Pricecharting API ($6/mo) — baseline single price
- Card Ladder ($20/mo) — sold data + pop + history
- Alternatives evaluated: Card Hedge (gated), Ximilar (wrong stage), SCN (wrong category)

### Z-SCORE FRAMEWORK (NEW)
- Card prices = distribution
- Deal = point in -z tail
- Pricing tiers feature-gated by z-threshold
- Multi-vertical thesis validated mathematically

### URL SEARCH (NEW)
- URL-first when valid URL exists
- Drill set URLs to specific cards
- Pricing points counter per card

## Open fires for next session

### IMMEDIATE (when founder returns)
1. **eBay Developer Account verification** — pasting App ID + Cert ID
2. **Build eBay Browse API integration** (~2-4 hours dev)
3. **Test with current 12 Jim cards**
4. **Save $43/mo at 100 customers**

### NEXT (when 25+ customers)
1. Subscribe to Pricecharting API ($6/mo)
2. Subscribe to Card Ladder ($20/mo)

### NEXT (this month or when ready)
1. Hosting ($5/mo, Render.com)

### OCTOBER TARGET
1. Phase 1 PSA search actor (own infrastructure)

### PENDING (lower priority)
1. Cron job for bot (auto-alerts)
2. Email field on form
3. 90% CI + 70% CI section
4. Top X deals on website (5 or 10?)
5. Build Stripe products for new tiers
6. Update DB tier values
7. Update Google Form with new tier options
8. URL set-page scraping to find specific card URLs (7 cards need this)

## Today's grand total

| Metric | Count |
|---|---|
| Features/docs delivered | 18 |
| Git commits today | ~15 |
| Tests passing | 75+ |
| Infrastructure spent | $0 |
| Time invested | ~6 hours |

## Memory note for next session

When conversation resumes:
- Pricing: Casual $15 / Standard $30 / Dealer $75 / Pro $150
- Cost-cutting roadmap: 5 stages with customer count triggers
- IMMEDIATE: Paste eBay credentials once verified
- Card Ladder = sweet spot at 50-500 customers ($20/mo flat)
- eBay Browse API = biggest immediate win (free)
- z-score framework is the mathematical thesis
- URL search infrastructure ready, needs eBay verification to fully activate
- PSA still blocked, using Apify with retries
- 11/12 Jim alerts delivered today with V3 layout

## When founder returns

Likely next:
1. Paste eBay credentials once verified
2. Build eBay Browse API integration
3. Continue with other pending fires
4. One fire at a time per founder's preference
