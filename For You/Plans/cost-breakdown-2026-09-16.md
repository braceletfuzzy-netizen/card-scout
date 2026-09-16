# Card Scout — Cost Breakdown (Sept 16, 2026)

## Time
Sept 16, 2026 (afternoon)

## Status
**DRAFTED.** Founder question answered.

## Founder's question

> "Where are the costs? Is it just the aggregation of the market?
> Is it in sourcing the deals? Etc."

## Answer

**YES — ~95% of variable cost is buying market data.**

Three sources, three layers of cost:

### Layer 1: AGGREGATION (80% of cost, ~$0.019/card/run)
- **eBay actor (Apify)**: $0.018/run (75% of per-card cost)
  - Search eBay for matching card listings
  - Returns 30 listings per query
  - Cost: $0.0006 per listing × 30
- **Sportscardspro actor**: $0.001/run (4% of per-card cost)
  - Get per-grade pricing + sold comps
  - Single request per card

### Layer 2: ENRICHMENT (20% of cost when working, ~$0.005/card/run)
- **PSA actor (Apify)**: $0.005/run (21%)
  - Get PSA population data (graded counts per grade)
  - Returns "how rare is this card"
  - **Currently broken** (PSA blocked our account)
  - When broken: retries add $0.005 (cost doubles to $0.010)

### Layer 3: PROCESSING (essentially $0)
- Bot runs on founder's local machine
- SQLite database (local file)
- Discord webhook (free)
- Stripe fees: 2.9% + $0.30 per charge
- Apify STARTER plan: $29/month (fixed)

## Total per-card-per-run

- **PSA works**: $0.024/card/run
- **PSA blocked (today's reality)**: $0.029/card/run (34% wasted on retries)

## At 100 customers × 6 cards avg × 4 weekly refreshes

Total monthly runs: **2,400 runs/month**

| Component | Monthly cost | % of total |
|---|---|---|
| Stripe fees (3% of $3,500 revenue) | $131.50 | 57% |
| eBay (listings) | $43.20 | 19% |
| Apify STARTER plan | $29.00 | 13% |
| PSA (working) | $12.00 | 5% |
| PSA retries (blocked) | $12.00 | 5% |
| Sportscardspro (comps) | $2.40 | 1% |
| Apify start fees | $0.20 | 0.1% |
| **TOTAL** | **$230.30** | 100% |

## Key insights

### Where the money goes
- **57% to Stripe** (revenue proportional)
- **25% to Apify usage** (eBay + PSA + SCPRO)
- **13% to Apify fixed plan** ($29/mo)
- **5% to PSA retries** (wasted due to block)

### What's actually expensive
- **eBay** is the biggest single cost ($43/mo at 100 customers)
  - But: provides listing URLs (where customers click to buy)
  - Essential for the deal alert flow
- **PSA retries** are pure waste ($12/mo at 100 customers)
  - Fix: PSA search actor (October Phase 1) → eliminate retries

### What's essentially free
- Bot compute (founder's PC)
- Database (SQLite)
- Discord delivery
- Bright Data proxy (free tier 5K/mo)

## Why this matches your offline math

Your insight: "price higher than I wanted... restructured to weekly vs 3x for dealers"

This maps directly to the cost structure:
- Pull frequency IS the variable cost lever
- More pulls = more cost (linearly)
- Card count adds linearly too

So the pricing model correctly tracks:
- Casual (1 pull/mo): $0.02/card → $0.06/customer/mo variable
- Standard (4 pull/mo): $0.08/card → $0.48/customer/mo
- Dealer (12 pull/mo): $0.24/card → $4.80/customer/mo
- Pro (30 pull/mo): $0.60/card → $30/customer/mo

## Optimization opportunities

1. **Build our own PSA actor (October)**
   - Estimated: $0.001/run (4-5x cheaper)
   - Savings: $9.60/mo at 100 customers
   - Risk: still depends on PSA data source

2. **Card Hedge hybrid (alternative)**
   - $0.01 per card lookup (vs $0.005-0.010 with retries)
   - Slightly more expensive but RELIABLE
   - No retry waste

3. **Cache sportscardspro longer**
   - Weekly refresh is already standard
   - Already in our model

4. **Skip eBay when sportscardspro has data**
   - Saves $43/mo at 100 customers
   - But: lose listing URLs (deal click-through)
   - Marginal — not recommended

## What this means for pricing

The 4-tier structure (Casual $15, Standard $30, Dealer $75, Pro $150) is sustainable because:

1. **Variable cost is 1-2% of revenue** at all tiers
2. **Stripe fees are 4-5% at low tiers, 2-3% at high tiers**
3. **Apify fixed cost is the biggest issue at low customer counts**
4. **Once at 50+ customers, fixed cost is <5% of revenue**

The risk is **<50 customers** where fixed costs dominate. That's why your entry tier ($15) is critical — it needs volume to work.
