# GemRate vs Card Hedger — Subscriber-Tier Decision Framework

**Date**: Sept 17, 2026
**Purpose**: At what customer count does each vendor become the right choice?
**Status**: DRAFT (depends on GemRate pricing response expected 1-3 business days)

---

## TL;DR

**Card Hedger is the right choice NOW (0-25 customers).**
**GemRate becomes the right choice at 25-100 customers IF pricing ≤ $300/mo.**
**Beyond 100 customers, GemRate Enterprise or self-hosted data wins.**

---

## Quick Vendor Comparison

| | GemRate | Card Hedger |
|---|---|---|
| **Founded by** | Ryan Stuczynski (since 2021) | (relatively new — OpenAPI spec, MCP, agent-native) |
| **Data scope** | Pop data for PSA/BGS/SGC/CGC + grading trends | Pricing + sales + pop + image ID + 42 categories |
| **Sales data** | ❌ No (just pop + grading trends) | ✅ 40M+ weekly sales, comps, FMV |
| **eBay equivalent** | ❌ No | ✅ (via card-search, card-fmv, comps) |
| **Pricing model** | Enterprise B2B (hundreds-$1000s/mo) or indie ($100-300/mo CSV) | Pay-per-call from $0.01 + subscription tiers |
| **API quality** | Partner API (form-required, B2B) | OpenAPI 3.1, MCP, x402 for agents, self-serve |
| **Auth** | x-api-key (after partner approval) | x-api-key (instant) or x402 USDC |
| **Customer acquisition friction** | High (form, manual review, B2B sales call) | Low (self-serve ai.cardhedger.com) |
| **Use case fit** | Per-grade pop data ONLY | Full data pipeline (replaces Sportscardspro, PSA actor, eBay actor) |

## 💡 Strategic Insight

**GemRate is a POP DATA SPECIALIST.** Just pop counts + grading trends.
**Card Hedger is an ALL-IN-ONE.** Pop + sales + pricing + image ID + 42 categories.

For Card Scout's deal-detection system, we need:
- ✅ Active listings (eBay Browse API = FREE)
- ✅ Historical sales (Card Hedger = ✅)
- ✅ Comparable pricing (Card Hedger = ✅)
- ⚠️ Pop data (GemRate OR Card Hedger)
- ⚠️ Per-grade price breakdown (Card Hedger = ✅)

**Card Hedger covers 4 of these. GemRate covers 1.**

---

## Subscriber-Tier Decision Framework

### Stage 0: 0-10 customers (Today → ~1 month)
**Use**: Card Hedger pay-per-call + eBay Browse API (FREE)

| Item | Cost | Why |
|---|---|---|
| eBay Browse API | $0 | Listing spread for deal detection |
| Sportscardspro Apify actor | $0.001/run | Asking-price baseline (works today) |
| Card Hedger (spec_id discovery only) | ~$0.10/customer one-time | Pop data lookup, saves manual PSA URL hunting |
| **Total** | **~$0.10 + Apify usage** | **~ $2-7/mo total** |

**Reasoning**: At this scale, pay-per-call is cheapest. We don't need volume pricing. We're testing what data we actually use.

**Skip GemRate**: Too expensive ($100+/mo minimum) for sub-10-customer scale.

### Stage 1: 10-25 customers (~1-3 months out)
**Use**: Card Hedger subscription tier (volume pricing kicks in)

| Item | Cost | Why |
|---|---|---|
| eBay Browse API | $0 | Same |
| Card Hedger Subscription | $50-100/mo est. | Need quote — likely tiers at 10k+ calls/mo |
| **Total** | **~$50-100/mo + Apify STARTER $29** | **~$80-130/mo** |

**Reasoning**: At 10-25 customers, volume pricing from Card Hedger is cheaper than pay-per-call.

**Math**: 25 customers × 12 cards × 8 API calls/day = 2,400 calls/day = 72,000 calls/mo. At $0.01/call = $720/mo. At subscription tier (estimate $0.001/call) = $72/mo. **Subscription tier saves ~$650/mo**.

**Still skip GemRate**: With Card Hedger providing pop data via `/v1/cards/population-by-gemrate-id` endpoint, we don't need GemRate direct subscription.

### Stage 2: 25-100 customers (~3-12 months out)
**Use**: This is where GemRate pricing MATTERS

**Scenario A: GemRate Indie $100-300/mo + Card Hedger subscription**

| Item | Cost | Why |
|---|---|---|
| eBay Browse API | $0 | Same |
| Card Hedger Subscription | $150-300/mo est. | Volume pricing for sales/comps |
| GemRate Indie tier | $100-300/mo est. | Direct pop API, faster than Card Hedger proxy |
| **Total** | **~$250-600/mo + Apify STARTER $29** | **~$280-630/mo** |

**Reasoning**: At 50-100 customers, dedicated data layer pays off. GemRate's Universal Pop Report (cross-grader) is unique data we can't get elsewhere.

**Scenario B: Card Hedger only (skip GemRate)**

| Item | Cost | Why |
|---|---|---|
| eBay Browse API | $0 | Same |
| Card Hedger Subscription | $400-800/mo est. | Need quote for 100k+ calls/mo |
| **Total** | **~$430-830/mo** | |

**Reasoning**: Card Hedger's `/v1/cards/population-by-gemrate-id` endpoint proxies GemRate data, so we get pop via Card Hedger without paying GemRate directly.

**Decision criteria**:
- Choose Scenario A if GemRate pricing ≤ $200/mo
- Choose Scenario B if GemRate pricing > $200/mo OR if Card Hedger pricing is significantly better than estimated

### Stage 3: 100-500 customers (Year 2)
**Use**: GemRate Enterprise (custom contract) OR self-hosting decision

**GemRate Enterprise**: $500-2000/mo (typical B2B data licensing)
- Pro: SLA, support, real-time data
- Con: High cost, vendor lock-in

**Self-host hybrid**:
- Self-host the Apify actors we own (free compute + BD proxy)
- Use Card Hedger for niche data (sales history, comp-by-cert)
- Use GemRate for cross-grader universal pop data (if pricing justifies)

**Decision**: At 100+ customers, revisit whether Card Hedger + GemRate combo or self-hosting is cheaper. Estimated break-even: ~$1K/mo total data spend.

### Stage 4: 500+ customers (Year 2-3)
**Use**: Self-host primary data layer + Card Hedger API for niche lookups

**Reasoning**: At this scale, the savings from self-hosting exceed dev/maintenance cost. Card Hedger stays as a fallback for data we don't have.

---

## Cost Per Customer At Each Stage

| Stage | Customers | Monthly Cost | Cost Per Customer | Margin At $30/mo Customer |
|---|---|---|---|---|
| 0 | 1-10 | ~$5 | $0.50-5 | 83-98% |
| 1 | 10-25 | ~$100 | $4-10 | 67-87% |
| 2A | 25-100 | ~$400 | $4-16 | 47-87% |
| 2B | 25-100 | ~$600 | $6-24 | 20-80% |
| 3 | 100-500 | ~$1,500 | $3-15 | 50-90% (with $150/mo customer avg) |
| 4 | 500+ | ~$3,000 (self-hosted) | $6 | 80% (with $30/mo avg) |

**Conclusion**: At Dealer tier ($75/mo) or higher, Card Hedger-only is profitable across all stages. At Casual tier ($15/mo), we need Stage 0 (Card Hedger pay-per-call) to be viable.

---

## What This Means For Decision Today

**Don't subscribe to GemRate yet.** Wait for pricing response.

**Do subscribe to Card Hedger.** Get API key, do a proof-of-concept with 1-2 cards.

**Track usage**: Once we have real call volume data (1-2 weeks), we can compute accurate cost per customer and confirm Stage 0/1 transition triggers.

---

## Risk Factors

| Risk | Mitigation |
|---|---|
| GemRate pricing much higher than estimate ($500+/mo) | Skip GemRate, use Card Hedger proxy |
| Card Hedger raises pay-per-call prices | Lock in subscription tier early |
| Card Hedger goes out of business | Self-host fallback (we own the actors) |
| Both vendors raise prices simultaneously | Self-host is always an escape hatch |
| eBay Browse API changes/degrades | Fallback to Apify actor |

---

## What To Do When GemRate Pricing Arrives

1. **If ≤ $100/mo**: Subscribe immediately. Indie tier fits 0-25 customers.
2. **If $100-300/mo**: Wait until 25+ customers. Subscribe then.
3. **If $300+/mo**: Skip entirely. Use Card Hedger proxy for pop data.
4. **If Enterprise-only ($500+/mo)**: Definitely skip until 100+ customers.

---

## Action Items

- [ ] Get Card Hedger API key (instant, ai.cardhedger.com)
- [ ] Build Card Hedger client (spec_id discovery use case)
- [ ] Wait for GemRate pricing response (1-3 business days from Sept 17)
- [ ] When GemRate responds: run decision criteria above
- [ ] At 10 customers: revisit Card Hedger subscription tier
- [ ] At 25 customers: revisit GemRate subscribe decision
- [ ] At 100 customers: self-host decision

---

## TL;DR (One More Time)

**0-25 customers**: Card Hedger pay-per-call. Don't even think about GemRate.
**25-100 customers**: Card Hedger subscription. Add GemRate only if ≤ $200/mo.
**100+ customers**: Self-host primary + Card Hedger for niche.
**Always**: eBay Browse API is free, use it everywhere.
