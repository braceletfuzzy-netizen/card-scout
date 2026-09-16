# Session Save - Sept 16, 2026 (Afternoon - PSA Block + Card Hedge Discovery)

## Time
Sept 16, 2026 (afternoon)

## 🎯 HEADLINE
**PSA.com is blocked for our founder.** Card Hedge API discovered but
gated on pricing. Decision: Path B — ship with 2/12 pop data, defer
pop expansion to Phase 1 (October) or pricing discussion.

## What happened this morning/afternoon

### 1. PSA URL hunt — paused
Started manual PSA.com browse for 7 missing Jim cards. Founder's
PSA.com password reset was accepted but login was blocked. Likely
IP-level or account-level ban from automated lookups.

### 2. Card Hedge API discovered
Founder sent link during workflow: https://api.cardhedger.com/docs

Research findings:
- Real company, OpenAPI 3.1 spec, 99.9% uptime
- 3.5M+ cards analyzed, 40M+ weekly sales
- 42+ categories (sports, Pokemon, MTG, One Piece, Lorcana)
- Pricing: pay-per-call via x402 (USDC on Base, settled via Stripe)
- Agent endpoints from $0.01/call
- `set-search` endpoint is FREE and returns PSA `set_url` directly
- Population endpoint returns full PSA pop breakdown per grade

### 3. Card Hedge has 2 API surfaces
- `api.cardhedger.com` — Agent API, x402 USDC payment (works)
- `cardhedge-api.com` — Traditional Bearer auth (DOES NOT RESOLVE — dead)
- Only the agent API works

### 4. PSA Public API researched
- Endpoint: https://api.psacard.com/publicapi/
- Auth: OAuth 2 password grant
- Methods: Cert Verification only (GetByCertNumber)
- Pop reports / spec_id discovery NOT available
- Cost NOT published
- **Verdict**: Doesn't solve our spec_id blocker

### 5. Pricing discussion triggered
Founder's offline math raised cost/card/month concerns:
- Card Hedge HYBRID: $0.16/card/month
- Current Apify-only: $0.05/card/month
- Founder paused Card Hedge integration pending pricing review

### 6. Decision: Path B
Ship with current state (2/12 Jim cards have pop data). Don't integrate
Card Hedge until pricing is settled. Phase 1 PSA search actor remains
the long-term solution (October).

## Cost model (captured for pricing review)

### Per-card/month costs
| Path | Cost | Notes |
|---|---|---|
| Apify-only (today) | $0.05 | PSA + Sportscardspro actors, weekly refresh |
| Card Hedge HYBRID | $0.16 | Card Hedge for spec_id discovery + weekly refresh |
| Card Hedge AGGRESSIVE | $0.68 | Card Hedge for everything, daily refresh |

### Per-customer margin (Pro tier, 12 cards, $50/mo)
| Path | Cost | Margin | Margin % |
|---|---|---|---|
| Apify-only | $0.48 | $49.52 | 99% |
| Card Hedge HYBRID | $1.92 | $48.08 | 96% |

### At scale (100 customers, 12 cards each)
| Path | Monthly cost |
|---|---|
| Apify-only | $48 |
| Card Hedge HYBRID | $193 |

## Current state

### Database

| Customer | Cards | Pop data | Status |
|---|---|---|---|
| buddy_test_001 (Jim) | 12 | 2/12 | Bo Jackson synthetic + Hank Aaron real |
| cs_CZYAJYA00001 | 1 | 0 | test |
| hingle_mccringleberry (Hingle) | 3 | 0 | trial, beta #2 |

### Dashboard
- Live at localhost:5000 (user can restart anytime)
- Auto-fetches pop on PSA URL change (Sept 16 morning feature)
- Pop stats display in card meta-row

### Files
- `For You/Plans/card-hedge-api-discovery-2026-09-16.md` — Card Hedge API research
- `For You/Plans/card-hedge-pricing-concern-2026-09-16.md` — pricing concern + Path B decision
- `For You/Plans/psa-pop-discovery-current-state-2026-09-16.md` — current state + decision
- `For You/Plans/psa-pop-data-long-term-2026-09-16.md` — long-term plan (Phase 1 in Oct)

## Decisions captured

1. **PSA.com blocked** — manual URL hunt paused, Apify actor likely also broken
2. **Card Hedge** — discovered, researched, integration PAUSED pending pricing
3. **Card Hedge pricing concern** — founder's offline math raised questions
4. **Path B** — ship with 2/12 pop data, no vendor commitment
5. **Phase 1 PSA search actor** — still planned for October (own build)
6. **Cost/card/month** — confirmed as right unit metric by founder

## What's next

### Immediate (when ready)

Pick any single thing. Founder said "one fire at a time":
- Run bot for Jim — verify alerts work despite PSA block (sportscardspro prices unaffected)
- Volume-by-grade ticker section (V3 enhancement)
- Cron job for auto-alerts
- Email field on Google Form
- Pricing discussion (when founder has done the math)

### Deferred (waiting on triggers)

- Card Hedge integration — pricing discussion
- Phase 1 PSA search actor — October
- 3-tier pricing — first paying customer
- Render deploy — end of month
- V2 Stripe webhook — when ready (~8 hours)

## Memory note for next session

When conversation resumes:
- PSA.com blocked for founder → Apify PSA actor likely broken too
- Card Hedge discovered, integration paused pending pricing review
- Path B: ship with 2/12 pop data, no vendor commitment
- Phase 1 PSA search actor (October) is long-term solution
- Cost/card/month is the right unit metric (founder stated)
- Memory: founder's name is NOT Jim — Jim is the beta tester

## Open questions for founder

1. When is the pricing discussion happening? (cost/card/month vs offline math)
2. Is PSA block testable from different IP/account?
3. What's the next "single fire" to address?

## Reference

- Pricing discussion thread (morning): see session-save-2026-09-16-morning-part2
- Cost model table: see card-hedge-api-discovery-2026-09-16.md
- Phase 1 plan: see psa-pop-data-long-term-2026-09-16.md
