# Card Hedge API — Discovery + Decision

## Time
Sept 16, 2026 ~7:40 AM (CDT)

## Status
**DRAFTED.** Discovered during manual PSA URL workflow. NOT integrated yet.

## What founder found

URL: https://api.cardhedger.com/docs

Founder's framing: "I found this while you were doing your thing. check
this out while I start the task you gave me"

## What it is

A real trading card data API company. NOT like the Reddit-promoted
lulzasaur9192 API (skipped Sept 16 morning — see psa-pop-data-long-term
plan).

### Specs

- **Catalog**: 3.5M+ cards
- **Sales data**: 40M+ weekly sales
- **Categories**: 42+ (sports, Pokemon, MTG, One Piece, Lorcana, etc.)
- **Uptime**: 99.9% (claimed)
- **Pricing model**: Pay-per-call via x402 (USDC on Base, settled via Stripe)
  - Agent endpoints: from $0.01/call
  - Or traditional API key subscription (via ai.cardhedger.com/api-services)
- **OpenAPI 3.1 spec**: yes
- **MCP support**: yes (`/mcp-docs`, `/mcp/agent/`)
- **AI agent ready**: yes (`llms.txt` discovery index)

## Endpoints relevant to Card Scout

| Endpoint | What it does | Replaces |
|---|---|---|
| `POST /v1/cards/card-search` | Search cards by text/player/set | (new — for onboarding form) |
| `POST /v1/cards/card-match` | AI match text → card (with confidence) | (new — for form "what card is this?") |
| `POST /v1/cards/card-details` | Get one card by Card Hedge ID | (new — for dashboard card view) |
| `POST /v1/cards/comps` | Recent sales + comp avg | Sportscardspro (partial) |
| `POST /v1/cards/comps-by-cert` | Sales from slab cert# | (new — for cert verification) |
| `POST /v1/cards/card-fmv` | Fair market valuation | (new — for FMV ticker) |
| `POST /v1/cards/prices-by-card` | Daily price time series | pricing_bands table (storage-vs-pull) |
| `POST /v1/cards/all-prices-by-card` | Current prices at every grade | sportscardspro per-grade |
| `population` endpoint | PSA/BGS/SGC/CGC breakdown per grade | PSA spec_id blocker (solved) |
| `GET /v1/cards/top-movers` | Weekly gainers | (new — for market intel alerts) |

## How it solves our biggest problem (PSA spec_id blocker)

Card Hedge's `population` endpoint returns:
```json
{
  "graders": [
    {
      "grader": "PSA",
      "specid": "378808",  ← Internal PSA spec_id (the thing we couldn't find)
      "set_url": "https://www.psacard.com/pop/baseball-cards/1999/bowman-chrome/34101",
      "total_population": 1730,
      "gems": 641,
      "gem_rate": 0.3705,
      "grades": [
        {"grade": "PSA 10", "count": 641, "non_auto": 636, "auto": 5, "qualifiers": 0},
        {"grade": "PSA 9", "count": 963, "non_auto": 951, "auto": 12, "qualifiers": 4}
      ]
    }
  ]
}
```

This is **the entire PSA pop data we need** with no URL hunting.

## Why this is different from Reddit's lulzasaur9192

| Signal | Reddit (lulzasaur9192) | Card Hedge |
|---|---|---|
| Company legitimacy | One-purpose account | Real co, OpenAPI spec, 99.9% uptime |
| Catalog size | PSA pop only | 3.5M+ cards, all graders |
| Pricing model | Subscription $9.99/mo (50 req free) | Pay-per-call from $0.01 |
| Sales data | None | 40M+ weekly sales |
| Categories | PSA only | 42+ categories |
| Spec_id discovery | No | YES (this is the win) |
| MCP/agent support | No | Yes |
| Production-ready | Likely dead | Yes |

## Decision matrix

### Path A: Integrate Card Hedge
**Pros**:
- Solves PSA spec_id blocker (no manual browsing)
- One API for many needs (search, match, prices, pop, comps)
- Pay-per-call fits our trial model
- 42 categories = reusable for coin/graded-comics future

**Cons**:
- Cost per lookup (was ~free with our own scraper)
- Vendor dependency (vendor can change pricing, die, get acquired)
- x402 USDC payment = need crypto wallet setup for agents
- We lose competitive moat of owning the data layer

**Estimated cost**:
- 12 cards × daily refresh × 5 endpoints × $0.01 = $0.60/day per customer
- 100 customers × $0.60/day = $60/day = $1800/mo
- Could be cheaper with subscription tier (need to check ai.cardhedger.com)

### Path B: Stay on our own stack
**Pros**:
- $0 vendor cost (just Apify + BD)
- Own the data layer (competitive moat)
- No vendor lock-in
- We can build PSA search actor in October (per Phase 1 plan)

**Cons**:
- Manual PSA URL hunting (current blocker)
- Limited pop data (only what we can find URLs for)
- No image-match, no comp-by-cert, no FMV out of the box
- 1 of 12 Jim cards has real pop today

### Path C: Hybrid (use Card Hedge for spec_id discovery, keep our own stack)
**Pros**:
- Use Card Hedge ONCE per card to find spec_id
- After that, our own actors fetch pop for free
- Best of both worlds

**Cons**:
- Need to integrate Card Hedge (still vendor dependency)
- Spec_id may change over time (need re-discovery)
- Adds another API surface to maintain

## Recommended path: C (hybrid)

1. Integrate Card Hedge for one purpose only: spec_id discovery
2. After we have the spec_id, save it to our DB (forever)
3. Our existing Apify PSA actor fetches pop using that spec_id
4. Long-term: Phase 1 PSA search actor replaces Card Hedge for spec_id discovery

This gets the cards moving TODAY without full vendor commitment.

## What's needed before integration

1. **API key** — need to check ai.cardhedger.com/api-services
2. **Pricing tier** — pay-per-call ($0.01) vs subscription (need quote)
3. **Card Scout budget impact** — founder needs to approve the cost
4. **Test plan** — verify on a single card before rolling out

## Files to create (when ready)

- `scripts/card_hedge_client.py` — minimal client for spec_id discovery
- `scripts/migrate_add_card_hedge_ids.py` — column for cached spec_ids
- `tests/test_card_hedge.py` — verify against one known card

## Decision: HOLD

Not integrating now. The founder said "check this out while I start
the task you gave me" — they're driving the PSA URL hunt manually.

When founder returns to this:
1. Review this doc
2. Decide: A, B, or C
3. If A or C: get API key, run test, build integration
4. If B: keep this doc as reference for Phase 1 PSA search actor design

## Memory note

For future sessions:
- Card Hedge API is a viable alternative to our own PSA spec_id search
- Pay-per-call model ($0.01+) fits our trial/small-customer model
- x402 USDC payment path = interesting but complex for agent autonomy
- Hybrid path (use Card Hedge only for spec_id discovery) is the safest
- Founder discovered this during manual PSA workflow
