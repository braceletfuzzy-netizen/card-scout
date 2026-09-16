# Card Scout Cost-Cutting Roadmap (Sept 16, 2026)

## Time
Sept 16, 2026

## Purpose
Founder's directive: roadmap for cost-cutting strategy with markers
at customer base levels. User-count goals = triggers.

## Customer Count Triggers

| Trigger | Today | New Stack | Monthly savings |
|---|---|---|---|
| **10 customers** | $6.96/mo (Apify usage) | $2.64/mo (eBay API free) | $4.32/mo (62% reduction) |
| **25 customers** | $17.40/mo | $11.40/mo (eBay API + PC API $6) | $6.00/mo (34% reduction) |
| **50 customers** | $34.80/mo | $13.20/mo (eBay API only) | $21.60/mo (62% reduction) |
| **100 customers** | $69.60/mo | $20.00/mo (Card Ladder all-in-one) | $49.60/mo (71% reduction) |
| **500 customers** | $348.00/mo | $24.00/mo (Card Ladder + DIY scraping) | $324/mo (93% reduction) |
| **1000 customers** | $696.00/mo | ~$50/mo (DIY everything) | $646/mo (93% reduction) |

## Stage 0: BASELINE (0-10 customers)

**When**: Now → 10 paying customers
**Stack**: Apify actors (eBay $0.018, SCPRO $0.001, PSA $0.010)
**Monthly cost**: $2-7/mo Apify usage
**Rationale**: No dev cost, current setup works at low scale

### Triggers to move to Stage 1
- 10+ paying customers
- OR >600 runs/month
- OR dev time available (~2-4 hours)

### What to build (when triggered)
1. Sign up for eBay Developer Account (5 min, free)
2. Get eBay Buy API credentials (app_id + cert_id)
3. Build eBay Buy API integration (~2-4 hours)
4. Test with 12 Jim cards
5. Replace Apify eBay actor call with direct API call
6. **Savings**: $4.32/mo at 10 customers, scales linearly

## Stage 1: eBay Buy API (10-25 customers)

**When**: 10+ customers
**Stack**: eBay Buy API (free) + Apify SCPRO/PSA actors
**Monthly cost**: $2.64/mo (eBay free) + $2.40/mo (SCPRO) + $24/mo (PSA broken, retry)
- Actual: ~$30/mo
**Savings vs Stage 0**: $4.32/mo at 10 customers

### What changes
- eBay data: Apify actor → direct eBay Buy API call
- SCPRO: stays on Apify (still cheap)
- PSA: stays on Apify (still broken, paying for retries)

### Triggers to move to Stage 2
- 25+ paying customers
- OR >600 SCPRO runs/month
- OR $6/mo for PC API becomes cheaper than Apify SCPRO

### What to build (when triggered)
1. Subscribe to Pricecharting Collector tier ($6/mo)
2. Get API token
3. Build Pricecharting API integration (~2-4 hours)
4. Replace Apify SCPRO actor call with direct PC API
5. **Savings**: ~$0-5/mo depending on call volume

## Stage 2: Pricecharting API (25-50 customers)

**When**: 25+ customers
**Stack**: eBay Buy API + Pricecharting API + Apify PSA actor
**Monthly cost**: ~$36/mo ($0 eBay + $6 PC + ~$30 PSA retries)
**Savings vs Stage 1**: ~$0-5/mo (small, mainly future-proofing)

### What changes
- SCPRO data: Apify actor → direct Pricecharting API ($6/mo unlimited)
- eBay: stays on free eBay Buy API
- PSA: stays on Apify (still broken)

### Value layers (founder insight Sept 16)
- **eBay Browse API** = listing data (asking prices — spread comes from here)
- **Pricecharting API** = baseline single-price per grade (fallback)
- **Card Ladder** = sold data (what people actually paid)

Combined: $6/mo PC + $20/mo Card Ladder = $26/mo for full data stack
- eBay Browse gives spread (multiple active listings)
- Pricecharting gives fallback single price
- Card Ladder gives sold history

**Note**: Sold data may require Card Ladder — eBay Browse only gives active listings, not sold prices.

### Triggers to move to Stage 3
- 50+ paying customers
- OR need PSA pop data reliably
- OR Card Ladder's all-in-one makes sense

### What to build (when triggered)
1. Subscribe to Card Ladder Pro ($20/mo)
2. Get API access
3. Build Card Ladder integration (~1-2 weeks)
4. Replace eBay + SCPRO + PSA with Card Ladder single API
5. **Savings**: $49.60/mo at 100 customers (71% reduction)

## Stage 3: Card Ladder + PC + eBay (50-500 customers)

**When**: 50-100+ customers
**Stack**: Card Ladder API ($20/mo) + Pricecharting API ($6/mo) + eBay Buy API (free)
**Monthly cost**: ~$26/mo flat ($20 Card Ladder + $6 Pricecharting)
**Savings vs Stage 2**: $10+/mo at 50 customers, $43.60/mo at 100 customers

### What changes (LAYERED APPROACH — founder insight Sept 16)
- **eBay Buy API (free)**: listing data — spread comes from multiple active listings
- **Pricecharting API ($6/mo)**: baseline single price per grade
- **Card Ladder ($20/mo)**: sold data, pop data, sales history
- **PSA actor**: drops out (Card Ladder has pop data)

### Triggers to move to Stage 4
- 500+ paying customers
- OR Card Ladder becomes too expensive at scale
- OR we need auction house data (Heritage/Goldin)
- OR dev time for Phase 1 PSA actor (~2-3 weeks)

### What to build (when triggered)
1. Phase 1: Build own PSA search actor (~3 weeks dev)
2. Phase 2: Direct BD scraping for eBay/sportscardspro (~2 weeks)
3. Phase 3: Add 130point for auction house data (~1 week)
4. **Savings**: $300+/mo at 500 customers

## Stage 4: DIY Infrastructure (500+ customers)

**When**: 500+ customers
**Stack**: DIY actors + BD scraping + 130point for auctions
**Monthly cost**: ~$24/mo (just BD + 130point subscriptions)
**Savings vs Stage 3**: $300+/mo (93% reduction)

### What changes
- All data: own infrastructure
- BD proxy: $1.50/1K requests (replaces Apify fees)
- 130point: subscription for auction house data

## Stage 5: STRATEGIC PARTNERSHIPS (1000+ customers)

**When**: 1000+ customers
**Stack**: Everything above + direct partnerships with Heritage/Goldin/PWCC
**Monthly cost**: ~$50-100/mo (with partnership deals)
**Negotiate at scale**: bulk pricing, revenue share, white-label deals

### What to negotiate
- Pricecharting Legendary tier (CSV bulk dumps)
- Heritage Auctions data feed
- Goldin Auctions API
- PWCC Marketplace data
- PSA Enterprise tier (GemRate)

## Decision matrix

| Stage | Customer count | Dev cost | Monthly cost | Margin @ 100 cust |
|---|---|---|---|---|
| 0. Baseline | 0-10 | $0 | $7 | 91% |
| 1. eBay API | 10-25 | $0 (2-4 hrs) | $30 (w/ PSA retries) | 93% |
| 2. PC API | 25-50 | $0 (2-4 hrs) | $36 | 93% |
| 3. Card Ladder | 50-500 | $0 (1-2 wks) | $20 | 96% |
| 4. DIY | 500+ | $5-10K (2-3 months) | $24 | 96% |
| 5. Partnerships | 1000+ | $10K+ (months) | $50-100 | 95%+ |

## Watch for these signals

### Stage 1 trigger signals
- 10+ paying customers (you have repeat customers asking for more)
- eBay Apify bill > $10/mo
- You have 2-4 hours for dev work

### Stage 2 trigger signals
- 25+ paying customers
- SCPRO Apify bill > $2/mo (or approaching $6/mo)
- Customers asking about refresh frequency

### Stage 3 trigger signals
- 50+ paying customers
- Need PSA pop data working (currently broken)
- Customers asking for "premium" features
- Card Ladder cost (~$20/mo) is cheaper than current stack

### Stage 4 trigger signals
- 500+ paying customers
- Card Ladder bill becoming meaningful (relative to revenue)
- Need auction house data (Heritage/Goldin)
- Have dev resources (2-3 weeks sprint)

### Stage 5 trigger signals
- 1000+ paying customers
- $10K+/mo revenue
- Industry recognition (people asking about partnerships)
- Series A or funded (can afford $10K+ dev investment)

## Monthly cost projection by stage

| Stage | 10 cust | 50 cust | 100 cust | 500 cust | 1000 cust |
|---|---|---|---|---|---|
| 0. Baseline | $7 | $35 | $70 | $348 | $696 |
| 1. eBay API | $3 | $13 | $26 | $132 | $264 |
| 2. PC API | $9 | $39 | $73 | $342 | $660 |
| 3. Card Ladder | $20 | $20 | $20 | $20-40 | $40-80 |
| 4. DIY | $1 | $5 | $5 | $24 | $48 |
| 5. Partnerships | TBD | TBD | TBD | $50 | $50-100 |

## Key insight: Card Ladder's flat $20/mo is the sweet spot

At 100 customers, Card Ladder is the cheapest option ($20 vs $26 for eBay API alone).
At 500 customers, DIY becomes competitive ($24 vs $20).
Above 500 customers, DIY wins.

## IMMEDIATE NEXT STEPS

1. ~~Sign up for eBay Developer Account~~ ✅ **DONE Sept 16, 2026 (awaiting ~1 day verification)**
2. **Get eBay Buy API credentials** (10 min after verification)
   - Sign in at https://developer.ebay.com
   - Click "Application Keys" → "Create a keyset" under Production
   - Name it "Card Scout"
   - Copy App ID + Cert ID (Client Secret) — paste to Hugo
3. **Build eBay Buy API integration** (~2-4 hours dev)
4. **Test with current 12 Jim cards**
5. **Save $43/mo at 100 customers** (scaling linearly)

When 25+ customers: subscribe to Pricecharting API ($6/mo).
When 50+ customers: subscribe to Card Ladder ($20/mo).
When 500+ customers: invest in DIY infrastructure.
When 1000+ customers: negotiate strategic partnerships.

## Files

- `For You/Plans/cheaper-aggregation-paths-2026-09-16.md` — detailed research
- `For You/Plans/cost-breakdown-2026-09-16.md` — where money goes today
- `For You/Plans/pricing-decision-2026-09-16.md` — pricing tiers (Casual/Standard/Dealer/Pro)
- `scripts/discord_alert_bot_v3.py` — current bot
- `card_scout.db` — current data

## Notes for founder

- **Don't pre-optimize**: Stages 0-1 work fine for current scale
- **Card Ladder sweet spot**: $20/mo flat is unbeatable below 500 customers
- **DIY at 500+**: only if we have dev resources (2-3 week sprint)
- **Strategic partnerships at 1000+**: only if we're a recognized player
- **eBay Buy API is FREE**: sign up today, save $43/mo at 100 customers

## Risk mitigation

| Risk | Mitigation |
|---|---|
| eBay API changes ToS | Stay under 5,000/day limit, monitor |
| Pricecharting raises prices | Easy to switch back to Apify |
| Card Ladder becomes expensive | Cancel anytime (monthly subscription) |
| DIY actor bugs | Fallback to vendor APIs |
| Partnership negotiations fail | Continue with vendor APIs |
