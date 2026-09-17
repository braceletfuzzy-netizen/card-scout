# Data Provider Comparison (Sept 16, 2026)

## Time
Sept 16, 2026 (evening)

## Status
**CORRECTED Sept 17, 2026.** Major docs discovery: Card Ladder has NO public API; Pricecharting API is on Legendary tier (not Collector). Plan adjusted.

**MAJOR UPDATE Sept 17 evening:** GemRate discovered. Card Ladder's Population Reports are powered by GemRate. GemRate is a real partner API with public docs, x-api-key auth, and structured endpoints. This likely obsoletes Phase 1 PSA actor build (PL-004). Contact form sent via `/partner`. Pricing unknown until response.

## ⚠️ Critical corrections from Sept 17 doc review

### Card Ladder — NO PUBLIC API (confirmed via 3 sources)
- Their own `/api` and `/developers` URLs return 404
- parse.bot (third-party API aggregator) confirms: *"Card Ladder does not publish a public developer API"*
- YouTube ("The Memorabilia Zone"): *"Card Ladder does not publicly offer an application programming interface for direct data access"*
- Pro subscription gives: web dashboard, Sales History, CL Value, Population Reports, Watchlist emails — NOT API access
- **Implication**: original "Card Ladder integration ~1-2 weeks" line in cost-cutting-roadmap is WRONG. There is nothing to integrate. Pro = market research + personal use only.
- **Trial started Sept 17, 2026**: 7-day free trial running, Day-6 cancel reminder set (job `509a458e7bfd`, fires Sept 23 9:00 AM CDT)

### Pricecharting — API is LEGENDARY tier (not Collector $6/mo)
- Their pricing matrix shows: **Free = No API, Collector ($6/mo) = No API, Legendary = Full API**
- Support thread (1 year old): *"The full API and CSV data is only available on the Legendary tier. The Collector tier includes loose prices only."*
- API gives **current prices only**, no historic data (per JJ's 2021 comment)
- Single price per item per condition (no spread) — same data shape as existing SCPRO actor
- **Implication**: $6/mo Collector = waste (web dashboard only). Legendary = same data shape as SCPRO, marginal improvement. Need Legendary pricing before any decision.
- **Action deferred**: look up Legendary tier price before subscribing

### Revised Stage 3 unlocker
- **eBay Browse API (FREE, verification pending)** is the real Stage 3 unlocker — gives listing SPREAD (multiple active listings per card), which is what `deal_detector.py` actually needs
- Card Ladder Pro = research + personal use (decision Day 7, Sept 23)
- Pricecharting Legendary = optional backfill if CSV bulk downloads prove useful (pricing pending lookup)

### GemRate discovery (Sept 17) — pricing received

**Card Ladder's Population Reports are powered by GemRate** (per Card Ladder's own Zendesk article).

**Pricing response received Sept 17 evening** (from Ryan Stuczynski, GemRate founder):

| Item | Cost | Notes |
|---|---|---|
| **Developer tier** | **$200/mo** | Prototyping, testing, smaller-scale integrations |
| **Daily request quota** | **5,000 req/day** | Across all endpoints |
| **Endpoints included** | All except: historical data, cert images, change feed | Add-ons available |
| **Commercial use** | ✅ Permitted at this tier | Caching + storage allowed while subscription active |
| **Attribution** | ✅ Required when displaying data or derived metrics | |
| **Catalogs (separate)** | $1,000/mo for Pokemon | "Thousands per month" for sports catalog |
| **Free trial** | 7 days, credit card required | Sign up at dashboard.gemrate.com/sign-up |

**Without the historical data add-on**, we get current pop snapshots but NOT
30-day pop history. Need to ask Ryan about add-on pricing.

**Subscription math**:
- Today: 16 cards × ~1 pop lookup/day = ~16 req/day (312x under cap)
- 200 customers × 12 cards × 1 daily pull = 2,400 req/day (still OK)
- 500 customers × 12 cards × 1 daily pull = 6,000 req/day (OVER cap)

**Strategic implication**: Card Ladder has no data moat. Our moat is in our
deal-detection algorithm (z-score lower-third) + Discord delivery UX + tiered
pricing. GemRate is the right vendor at the right price for our pop data needs.

**Status (Sept 17 evening)**: Pricing received. **7-day free trial available.**
Recommendation: subscribe during trial, validate data quality, build integration
in October if quality is good.

Full research in `Sessions/2026-09-17-gemrate-discovery.md`. Draft message in
`Sessions/2026-09-17-gemrate-inquiry-draft.md`.

### Combined data stack (revised Sept 17)
| Source | Cost | What it gives |
|---|---|---|
| **eBay Browse API** | FREE (pending) | Listing data — spread from multiple active listings |
| **GemRate** | **$200/mo** (developer tier) | Pop data PSA+BGS+SGC+CGC, cert lookup, universal card IDs (no history without add-on) |
| **SCPro (existing Apify actor)** | $0.001/run | Asking-price baseline — CANDIDATE for retirement (Card Hedger covers better) |
| **TOTAL** | **$29 Apify + $200 GemRate** | Full data stack |

### Card Hedger re-evaluation (Sept 17 evening — Cosmo + Hugo verification)

**Trigger**: Cosmo (parallel Hermes agent) wrote `For You/Plans/gemrate-vs-cardhedger-subscriber-tier-2026-09-17.md`
proposing Card Hedger as a competitor to GemRate. Founder asked for verification
before trusting the framework.

**Verified from live docs (Sept 17 evening):**

| Claim from Cosmo | Reality | Status |
|---|---|---|
| Self-serve signup at `ai.cardhedger.com` | Confirmed — 7-day free trial, from $14.99/mo, API plans from $49/mo | ✅ Correct |
| Pay-per-call from $0.01 | Confirmed via x402 on `api.cardhedger.com/v1/agent/*` | ✅ Correct |
| MCP server | **YES** — `https://api.cardhedger.com/mcp` for API-key auth, `/mcp/agent/` for x402 pay-per-call | ✅ Correct, more than expected |
| OpenAPI 3.1 spec | Plausible from doc structure; not 100% verified | ⚠️ Unverified |
| 42 categories | Not verified | ⚠️ Unverified |
| `/v1/cards/population-by-gemrate-id` endpoint | **DOES NOT EXIST in docs** | ❌ Incorrect |
| Card Hedger proxies GemRate pop data | **Not supported by docs** — Card Hedger has its own price/sales data, not pop | ❌ Incorrect |

**What Card Hedger DOES have (verified from MCP docs):**
- `match_card` (AI card matching), `search_cards` (3.5M+ cards)
- `get_prices_by_cert`, `get_details_by_certs` (batch)
- `get_price_history`, `get_all_prices` (latest across grades)
- `get_comps` (with anomaly filtering), `get_card_fmv` (FMV with confidence)
- `get_top_movers`, `get_total_sales_by_player`
- 40M+ weekly sales tracked, 2,500+ customer base

**What Card Hedger does NOT have (per docs):**
- Population data per grade (PSA 10 count, etc.)
- Cert # lookup with grader metadata (their cert lookup returns prices, not pop)
- Anything resembling GemRate's `/population` endpoint

**Conclusion**: Card Hedger is a **PRICE + SALES + COMPS** specialist.
GemRate is a **POP + CERT LOOKUP** specialist. **They don't overlap; they
complement each other.** Cosmo's claim that "Card Hedger covers 4 of our
needs, GemRate covers 1" was wrong about the pop data — but the
**complementary stack** insight is correct.

**Updated data stack (Sept 17 evening):**

| Source | Cost | What it gives |
|---|---|---|
| **eBay Browse API** | FREE (pending) | Listing data — spread from multiple active listings |
| **GemRate** | TBD (~$?/mo) | Pop data PSA+BGS+SGC+CGC, cert lookup, universal card IDs, history |
| **Card Hedger** | $14.99/mo (subscription) or pay-per-call | Price + sales + comps + FMV; MCP server for agent-native integration |
| **SCPro (existing Apify actor)** | $0.001/run | Asking-price baseline (existing actor, may retire if Card Hedger covers it) |
| **TOTAL** | **$29 Apify + $49 Card Hedger + TBD GemRate** | Full data stack |

**Card Hedger decision criteria:**
- ✅ Subscribe immediately: replaces SCPro actor for most use cases, adds comps/FMV
  data we don't have today
- ✅ MCP server = agent-native integration (Claude Code, Codex can use directly)
- ✅ Self-serve signup = no sales-call friction
- ⚠️ Wait for verification: 7-day free trial first; if data quality is good,
  subscribe at $14.99/mo (or $49/mo for API plan if we need higher call volume)

**What this changes in the plan:**
- PL-002 (Card Hedger ON HOLD) is now RESOLVED — vendor has evolved, friction is
  gone
- SCPro Apify actor is now a candidate for retirement (Card Hedger covers it
  better with better data + MCP integration)
- Subscriber-tier math from Cosmo's doc remains valid (we still need GemRate
  for pop at 25+ customers if pricing works)

### Card Ladder as competitor (revised)
Card Ladder *uses* GemRate. We will use GemRate. Same data layer.
What Card Ladder doesn't do that we do:
- Lower-third z-score deal detection (Card Ladder shows % deltas, not deal alerts)
- Discord delivery (Card Ladder has email; collectors live in Discord)
- Tiered pricing by refresh frequency (Card Ladder is flat $20/mo)
- Self-serve card management with inline search (Card Ladder has watchlist only)

## Card Ladder trial — market observations (Sept 17, 2026)

### Sales History data shape (confirmed from live UI)
Each sale row contains:
| Field | Example | Value to Card Scout |
|---|---|---|
| `card_title` | "Bo Jackson 1987 Leaf Donruss Rated Rookie Auto #35" | Card matching |
| `marketplace` | "eBay" | Source attribution (hidden from customers per Sept 16 strip) |
| `seller_name` + `feedback` | "steelcitycollectibles1" 165,131 | Deal-validity filter (low-feedback = noise) |
| `sold_price` | $299.95 | Sold data — what `deal_detector.py` actually wants |
| `sold_date` | Sep 16, 2026 | Time-series for trend/σ calc |
| `listing_type` | Fixed Price / Best Offer / Auction | Auction-vs-asking distinction |
| `verified` | ✅ green check | Quality flag |

### Multi-source confirmed
Sales History filters include: eBay, PWCC, plus others (Goldin, Heritage per pricing page).
- **5,105 results** for "bo jackson donruss rookie card" — confirms search quality
- URL pattern with `saleId=` parameter (e.g. `saleId=ebay-237067678912`) means each sale has a stable internal ID — important for any future B2B partnership negotiation

### Player index data shape (`/players/<name>` page)
27 graded cards per player, each with 6 fields:

| Field | Example | Value to Card Scout |
|---|---|---|
| `card_name` | "1988 Topps Bo Jackson #327 Super Rookie" | Card identity |
| `grade` | "PSA 10" | Grading company + numeric grade |
| `pop` | "598" | Population count for that grade |
| `1M % Change` | "+43.25%" | Rolling 1-month % delta — **THIS is the "ladder score"** |
| `Last Sold` | "$4,124.00" | Most recent sale |
| Index contribution | (aggregates into 25,275 player score) | Player-level trend indicator |

**Side window on individual card click** shows time series chart + eBay BIN listings. URL pattern: `?cardId=DjzqjOlFlay5Ez4642rD` (stable identifier).

### Filters available
Min/Max price, Min/Max date, Platform(s), Listing Type, Seller ID, Verified Status.
Search supports: synonyms, typos (toggleable), "!" prefix for exact match, cert # deep-link.

### Open questions (look at during trial)
1. **CL Value vs Sales History median** — does Card Ladder's pricing algorithm match the median sold price, or does it apply player-index weighting + outlier trim? Look at a Bo Jackson Donruss rookie detail page and compare. (5 min)
2. **Population Report quality** — how does CL's pop data compare to what our broken PSA actor returns? (5 min)
3. **Watchlist alert email** — what does a price-drop alert look like? Useful as manual backup deal-feed if our bot misses something. (5 min)

### Critical constraints (do NOT violate)
- **No documented public API** — confirmed across 3 independent sources
- **No scraping the internal API** even though `saleId=` URLs suggest one exists:
  1. Internal APIs log query patterns; bot detection is trivial
  2. Scraping kills the future B2B partnership path when we need it at 50+ customers
  3. CFAA gray area; we don't need legal exposure for a $20/mo service
- **Use the trial as research + personal-use evaluation, not as a data source**

### Decision criteria for Day 7 (Sept 23)
- **Keep $20/mo if**: you personally use the dashboard weekly for your own cards, and the Sales History/Pop data is materially better than what we have access to today
- **Cancel if**: you only logged in once, the CL Value doesn't match what you'd call fair market, or you'd rather wait for a B2B conversation at scale
- **Either way**: this doc gets updated with the decision and reasoning, so future-you has the full trail

## Founder insight captured
> "I still like card Ladder but we could add SCPRO api at $6/month, eBay will give
> us the spread with the listing data. Getting eBay sold data might be something
> we have to rely on card ladder for."

## The 4 alternatives evaluated

### 1. Card Hedge API (`api.cardhedger.com`)
- **Verdict**: Already evaluated Sept 16 (ON HOLD)
- **Strength**: 4.1M cards, image recognition, sold + listing data
- **Weakness**: x402 USDC payment = crypto wallet friction; gated contact-sales for full pricing
- **Card Scout fit**: Overkill for V1 (we have URLs, not photos); wrong stage

### 2. SportsCardsPro API (`pricecharting.com/api`)
- **Verdict**: ✅ **APPROVED** ($6/mo)
- **Strength**: Cheap ($6/mo unlimited), JSON + CSV, simple auth
- **Weakness**: Returns single price per grade (no spread)
- **Card Scout fit**: 1:1 replacement for our existing Apify SCPRO actor

### 3. Ximilar Collectibles API (`api.ximilar.com/collectibles/v2/`)
- **Verdict**: Wrong stage
- **Strength**: Image recognition + price search combined
- **Weakness**: Image-first API (we have URLs); enterprise pricing (custom quote)
- **Card Scout fit**: V2.5+ (if we ever build mobile scan feature)

### 4. Sports Card Network (SCN) Business Plan (`sportscardnetwork.ai`)
- **Verdict**: Wrong category
- **Strength**: Full dealer inventory management
- **Weakness**: Built for dealers selling cards (we alert buyers)
- **Card Scout fit**: None. Uses CardHedger as data source, which is what we're considering

## Why Card Ladder wins (founder-direct)

### 1. Only one with public pricing at our scale
| Provider | Pricing transparency |
|---|---|
| Card Ladder | ✅ Published $20/mo tier |
| Card Hedge | ❌ Sales call required |
| SCPRO API | ✅ $6/mo |
| Ximilar | ❌ Custom quote |
| SCN | ✅ $60/mo |

### 2. Right data shape for our use case
| Need | Card Ladder |
|---|---|
| Multi-source price history | ✅ |
| PSA pop data | ✅ |
| Sales history (trend detection) | ✅ |
| REST API + Bearer token | ✅ |
| Card Ladder is a *data* company, not UI | ✅ |

### 3. Hidden costs of alternatives
| Alternative | Real cost beyond price |
|---|---|
| Card Hedge | Sales call + crypto wallet + x402 protocol = weeks of dev |
| SCPRO API | Doesn't solve deal detection blocker (single price) |
| Ximilar | Image-first = doesn't fit URL workflow |
| SCN | Dealer tool = wrong category for data API |

## Layered stack (founder insight Sept 16, REVISED Sept 17)

| Source | Cost | What it gives |
|---|---|---|
| **eBay Browse API** | FREE (pending) | Listing data — spread from multiple active listings |
| **GemRate** | TBD (~$?/mo) | Pop data PSA+BGS+SGC+CGC, cert lookup, universal card IDs, history |
| **Card Hedger** (NEW) | $14.99/mo subscription OR pay-per-call | Price + sales + comps + FMV + MCP server; replaces SCPro for most uses |
| **SCPro (Apify)** | $0.001/run | Asking-price baseline — CANDIDATE FOR RETIREMENT (Card Hedger covers better) |
| **TOTAL** | **$29 Apify + $14.99 Card Hedger + TBD GemRate** | Full data stack (~current price + better data) |

## Why this works (revised)
1. **eBay Browse** = spread source (multiple active listings = lower-third detection works)
2. **GemRate** = canonical card identity + population data + cert lookup (all 4 graders)
3. **SCPro** = cheap asking-price fallback when eBay doesn't have the card
4. **Card Ladder** = research/personal use only; not in the data pipeline

## Implementation sequence (revised)

### Now (Sept 17)
- Wait for eBay Developer verification (in progress)
- Send GemRate contact form (DONE)
- Continue Card Ladder trial research (in progress, free)

### October
- Subscribe to Card Hedger ($14.99/mo) — verified self-serve, MCP available
- Build Card Hedger integration (~2-4 hrs dev, MCP-native — much faster than REST adapter)
- Build eBay Browse API integration (~2-4 hrs dev) once verified
- Get GemRate pricing + subscribe if ≤ $50/mo
- Build GemRate integration (~1 day dev)
- Replace PSA actor with GemRate adapter (or keep Apify as fallback)
- Retire SCPro Apify actor once Card Hedger integration is validated### November
- Inline search UX (PL-008) — GemRate primary, SCPro price fallback
- Build cert # lookup entry point (vault preparation)

### December (or when 50+ customers)
- Decision: keep, upgrade, or replace GemRate based on usage patterns
- Player Index feature (PL-006) — uses GemRate history endpoint

## Decisions captured

### CONFIRMED
- **eBay Browse API**: free, biggest immediate win (listing spread for deal detection)
- **Card Hedger**: subscribe ($14.99/mo) — verified self-serve + MCP + better than SCPro for pricing data
- **GemRate**: $200/mo developer tier confirmed; **7-day free trial recommended**, decision after validating data quality
- **SCPro (Apify)**: candidate for retirement once Card Hedger integration lands

### DEFERRED
- **Card Ladder Pro**: trial ACTIVE, decision Day 7 (likely cancel — no API)
- **Pricecharting Legendary**: pricing unknown; deprioritized after GemRate discovery
- **Card Hedge**: still ON HOLD (x402 + sales call friction) — now lower priority
- **Ximilar**: wrong stage (V2.5+ feature)
- **SCN**: wrong category (dealer tool, not data API)
- **Phase 1 PSA actor build**: LIKELY OBSOLETE if GemRate pricing works

## Files

| File | Status |
|---|---|
| `For You/Plans/cost-cutting-roadmap-2026-09-16.md` | UPDATED — Stage 2/3 now reflect layered approach |
| `For You/Plans/data-provider-comparison-2026-09-16.md` | NEW (this doc) |

## Open fires (Sept 17 evening — GemRate pricing received)
1. **Subscribe to GemRate 7-day free trial** — $200/mo developer tier, no risk, validates data quality
2. **Subscribe to Card Hedger** ($14.99/mo) — verified self-serve, MCP available, replaces SCPro
3. Wait for eBay Developer verification (~1 day, started Sept 16) — listing spread for deal detection
4. Build eBay Browse API integration (~2-4 hours) once verified
5. **Build Card Hedger integration** (~2-4 hrs dev, MCP-native) after subscription
6. **Build GemRate integration** (~1 day dev) after trial validates data quality
7. **Retire SCPro Apify actor** once Card Hedger integration lands
8. **Ask Ryan at GemRate**: historical data add-on pricing, attribution format, rate limits per minute, ToS on deal-alerts
9. ~~Subscribe to Pricecharting Collector ($6/mo)~~ — DEFERRED, Collector has no API
10. ~~Subscribe to Card Ladder Pro ($20/mo)~~ — CANCELLED Sept 17
11. ~~Look up Pricecharting Legendary tier price~~ — DEFERRED indefinitely (Card Hedger covers price needs)
