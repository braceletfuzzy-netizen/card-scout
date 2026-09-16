# Cheaper Aggregation Paths — Research (Sept 16, 2026)

## Time
Sept 16, 2026 (afternoon)

## Status
**DRAFTED.** Founder asked: "Is there a cheaper way to aggregate data at
certain thresholds via other methods: a) API b) Strategic agreements
c) undiscovered etc?"

## Today's cost breakdown

At 100 customers × 6 cards × 4 weekly refreshes = 2,400 runs/month:

| Source | Per run | Monthly (2,400 runs) |
|---|---|---|
| eBay (Apify) | $0.018 | $43.20 |
| Sportscardspro (Apify) | $0.001 | $2.40 |
| PSA (Apify, broken) | $0.010 (with retry) | $24.00 |
| **TOTAL** | **$0.029** | **$69.60/mo** |

## Option A: OFFICIAL APIs (FREE TIER) — biggest finding

### 1. eBay Buy API — FREE
- **Cost**: $0/call (5,000 calls/day free)
- **Limit**: 5,000/day default (raise available)
- **Setup**: eBay Developer Account (free, ~5 min signup)
- **Data**: Same as our Apify eBay actor
- **Switch cost**: 2-4 hours dev (replace actor with direct API)
- **SAVINGS at 100 customers**: $43.20/mo (75% reduction on eBay cost!)

### 2. Pricecharting/Sportscardspro API — $6/mo
- **Cost**: $6/mo subscription (or $59/yr) — UNLIMITED calls
- **Same data** as our SCPRO Apify actor
- **Setup**: Subscribe to "Collector" tier
- **Switch cost**: 2-4 hours dev
- **SAVINGS at 100 customers**: $2.40/mo → $6/mo flat (small savings, but unlimited)
- **Breakeven**: Above 600 calls/mo (~25 customers)

## Option B: VENDOR AGGREGATORS

### 1. 130point API (parse.bot)
- **Coverage**: 6 marketplaces (eBay, Goldin, Heritage, Pristine, MySlabs, Fanatics)
- **Returns**: Up to 1,000 sale records per call
- **Pricing**: Unknown — likely subscription or pay-per-call
- **ADVANTAGE**: Auction house data (Heritage/Goldin = premium)
- **Status**: Need to verify pricing

### 2. Card Ladder Pro API — $20/mo
- **Cost**: $20/mo ($200/yr)
- **Coverage**: All-in-one (price + pop + sales history)
- **Features**: CL value, market value, 1-month/year summaries
- **Includes PSA pop counts!**
- **SAVINGS at 100 customers**: $20 vs $69.60 = **$49.60/mo saved (71%)**
- **Risk**: Vendor lock-in

### 3. Card Hedge API (already evaluated)
- **Cost**: $0.01-0.02/call (free set-search)
- **Coverage**: 3.5M+ cards, 42+ categories
- **Most complete data**: price + pop + comps + image match
- **At 100 customers**: $24/mo (was $69.60)
- **SAVINGS**: $45.60/mo (65%)
- **Risk**: x402 USDC wallet required

## Option C: STRATEGIC AGREEMENTS

### 1. eBay Partner Network (EPN)
- **NOT a data API** — affiliate commissions only
- Use eBay Browse/Buy API for data (already free)

### 2. Pricecharting Partnership
- "Legendary" tier (price unknown, likely $30-50/mo)
- Includes CSV downloads of ALL sets at once
- Worth negotiating bulk pricing at 1000+ customers

### 3. Direct with Heritage/Goldin/PWCC
- Auction houses offer data feeds to platforms
- Likely $1000+/mo + revenue share
- Only viable at 1000+ customers

### 4. PSA Official API
- Public API: only cert lookup, no pop
- "GemRate" enterprise: $$$$, not viable

## Option D: UNDISCOVERED — build our own

### 1. Phase 1 PSA Search Actor (October)
- **Cost**: ~$0.001/run (4-5x cheaper than current)
- Single call = spec_id + pop
- **SAVINGS at 100 customers**: $21.60/mo (PSA only)

### 2. Direct BD scraping (skip Apify)
- Use BD web_unlocker1 + regex
- Skip Apify per-result fees
- **SAVINGS at 100 customers**: $40.80/mo (eBay only)

### 3. Caching layer
- Cache 24h = 4x reduction
- Marginal savings

## TIER COMPARISON (per month)

| Customers | Runs/mo | Today | eBay API | PC API | Card Ladder | Card Hedge | DIY |
|---|---|---|---|---|---|---|---|
| 3 | 72 | $2.09 | $0.79 | $8.02 | $20.00 | $0.72 | $0.14 |
| 10 | 240 | $6.96 | $2.64 | $12.72 | $20.00 | $2.40 | $0.48 |
| 50 | 1200 | $34.80 | $13.20 | $39.60 | $20.00 | $12.00 | $2.40 |
| 100 | 2400 | $69.60 | $26.40 | $73.20 | $20.00 | $24.00 | $4.80 |
| 500 | 12000 | $348.00 | $132.00 | $342.00 | $20.00 | $120.00 | $24.00 |

## WHEN TO SWITCH (recommendation)

| Customer count | Best option | Why |
|---|---|---|
| 0-10 | Today (Apify) | No dev cost, current setup works |
| 10-50 | **eBay Buy API (free)** | 75% savings on eBay cost, free tier |
| 50-100 | eBay API + Pricecharting API | $6/mo for unlimited SCPRO |
| 100-500 | + Card Ladder ($20/mo) | All-in-one, includes pop |
| 500+ | + DIY Phase 1 PSA actor | Own infrastructure, scale savings |

## RECOMMENDATIONS

### Quick wins (do NOW)
1. **Switch eBay data to eBay Buy API** (free) — saves $43/mo at 100 customers
2. **Subscribe to Pricecharting API ($6/mo)** — once at 25+ customers

### Strategic moves (do at scale)
3. **Card Ladder integration** — at 50+ customers if we want all-in-one
4. **Phase 1 PSA actor** — at 100+ customers when dev cost amortizes
5. **Strategic partnerships** — at 1000+ customers

### Risk matrix
- eBay API: Low risk (it's their official free tier)
- Pricecharting: Low risk (subscription, easy to cancel)
- Card Ladder: Medium risk (vendor lock-in)
- Card Hedge: Medium risk (USDC wallet setup)
- DIY: Low risk (we own it)

## NEXT STEPS

1. Sign up for eBay Developer Account (5 min, free)
2. Get eBay Buy API credentials (app_id + cert_id)
3. Build eBay Buy API integration (~2-4 hours)
4. Test with current 12 cards
5. Replace Apify eBay actor call with direct API call
6. Save cost: $43/mo at 100 customers
