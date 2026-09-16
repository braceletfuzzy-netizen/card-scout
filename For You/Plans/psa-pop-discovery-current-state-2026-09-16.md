# PSA Pop Discovery — Current State (Sept 16 PM)

## Time
Sept 16, 2026 (afternoon)

## Status
**DRAFTED.** PSA blocked + Card Hedge gated. Path B (skip Card Hedge).

## What happened

1. **PSA blocked** — Founder can't log into PSA.com (password reset
   accepted but login blocked). Likely IP/account-level block from
   automated lookups. Our PSA Apify actor uses the same credentials.

2. **Card Hedge discovered** — Real company, OpenAPI 3.1, 3.5M+ cards,
   40M+ weekly sales, $0.01/call pricing. Looks legitimate.

3. **Card Hedge has 2 surfaces**:
   - `api.cardhedger.com` — Agent API, x402 USDC payment
   - `cardhedge-api.com` — Traditional, Bearer auth (DOES NOT EXIST —
     DNS doesn't resolve)
   - Only the agent API works

4. **Pricing concern paused** Card Hedge integration earlier — founder's
   offline math showed cost/card/month issues

5. **Founder's directive**: "We will do B for now. PSAcards has an API
   but I don't know what it costs or what it returns"

## PSA Public API research

| Detail | Value |
|---|---|
| Endpoint | `https://api.psacard.com/publicapi/` |
| Auth | OAuth 2 password grant (PSA login) |
| Cost | NOT published — contact collectors-apis@collectors.com |
| Methods | Cert Verification only (GetByCertNumber) |
| Pop reports | NOT available |
| Set search | NOT available |
| Spec_id discovery | NOT available |

**Verdict**: PSA Public API doesn't solve our spec_id blocker. Only
useful if customers provided cert numbers (they don't — they submit
search_query text).

## Decision: Path B (skip Card Hedge, ship with 2/12 pop)

We will:
- Accept 2/12 Jim cards have pop data (Bo Jackson synthetic + Hank Aaron real)
- Stock-class ticker shows for cards with `psa_total_pop` set
- Cards without pop get just the price ticker (no rarity, no outstanding shares)
- Customers can add cards via dashboard, paste PSA URL if they have one
- Dashboard auto-fetches pop when URL is provided (current implementation)

## What this means for the stock-class ticker

| Card | Pop data | Stock-class section shows? |
|---|---|---|
| Bo Jackson (#1) | Yes (synthetic) | ✅ YES |
| Hank Aaron (#5) | Yes (real) | ✅ YES |
| Derek Jeter (#4) | No | ❌ No (price ticker only) |
| Frank Thomas (#2) | No | ❌ |
| Michael Jordan (#3) | No | ❌ |
| A-Rod (#6) | No | ❌ |
| Yancy Thigpen (#7) | No | ❌ |
| Barry Sanders (#8) | No | ❌ |
| Charizard ex (#9) | No | ❌ |
| Black Lotus (#10) | No | ❌ |
| Mewtwo (#11) | No | ❌ |
| Charizard Base Set (#12) | No | ❌ |

## Long-term options (when founder wants to revisit)

| Option | Cost | Effort | When |
|---|---|---|---|
| Card Hedge x402 | $0.07 one-time | 30 min (USDC wallet setup) | When pricing is settled |
| PSA Public API | Unknown | Hours (OAuth flow) | Doesn't help our problem |
| Phase 1 PSA search actor (own) | $0 | 20 hours | October per plan |
| Manual PSA URL hunt | $0 | 30 min/user | This morning, paused |
| Skip pop, ship without | $0 | 0 | **CURRENT DECISION** |

## Files to update

- `For You/Plans/card-hedge-pricing-concern-2026-09-16.md` — update decision to B
- `For You/Plans/psa-pop-data-long-term-2026-09-16.md` — note PSA blocked
- `For You/Plans/psa-grades-as-stock-ticker-2026-09-16.md` — note 2/12 cards only

## Memory note for next session

When conversation resumes:
- PSA.com is blocked (founder's account)
- Card Hedge hybrid path is on hold (pricing concern)
- We shipped with 2/12 Jim cards having pop data
- Stock-class ticker works for cards with `psa_total_pop`
- Long-term: Phase 1 PSA search actor in October (own build)
- Phase 1 solves the blocker regardless of PSA/Card Hedge status

## When founder wants to revisit

If/when:
- PSA unblock happens (test from different IP/account)
- Card Hedge pricing discussion happens
- Time to build Phase 1 (October)

Just pick up from here.
