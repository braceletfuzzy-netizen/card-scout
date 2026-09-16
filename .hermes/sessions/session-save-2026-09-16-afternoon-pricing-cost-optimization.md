# Session Save - Sept 16, 2026 (Pricing + Cost Optimization)

## Time
Sept 16, 2026 (afternoon)

## What we shipped this session

### Pricing discussion (3 rounds)
1. First model: Card-count-based tiers (Hobby/Pro/Elite)
2. Founder's offline math concern surfaced: pull frequency is the right lever
3. Rebuilt model: Casual $15 / Standard $30 / Dealer $75 / Pro $150
4. Margin analysis: 90%+ at 100 customers, break-even at <5 customers

### Cost breakdown (founder question)
- 95% of variable cost is buying market data
- Layer 1: Aggregation (80%, $0.019/card/run)
- Layer 2: Enrichment (20%, $0.005/card/run, currently broken)
- Layer 3: Processing (~0%, local compute)

### Cheaper aggregation paths (founder question)
- eBay Buy API: FREE (5,000 calls/day)
- Pricecharting API: $6/mo unlimited
- Card Ladder API: $20/mo all-in-one (price + pop + sales)
- Card Hedge API: $0.01/call
- 130point API: auction houses
- DIY: own infrastructure (Phase 1 PSA actor)

### Cost-cutting roadmap
- 5-stage roadmap with customer count triggers
- Stage 0 (0-10): Baseline, Apify actors
- Stage 1 (10-25): eBay Buy API (FREE)
- Stage 2 (25-50): Pricecharting API ($6/mo)
- Stage 3 (50-500): Card Ladder ($20/mo) ← sweet spot
- Stage 4 (500+): DIY infrastructure
- Stage 5 (1000+): Strategic partnerships

## Key insights captured

1. **Pull frequency is the right lever** for pricing (founder's offline math)
2. **Variable cost = 1-2% of revenue** at all tiers (pricing is sustainable)
3. **Stripe fees matter at low price points** (4-5% at $25 tier)
4. **Card Ladder flat $20/mo** is unbeatable below 500 customers
5. **eBay Buy API is FREE** — biggest immediate win (save $43/mo at 100 customers)

## Decisions captured

### Pricing (Sept 16, approved)
- Casual: $15 (3 cards, 1 pull/mo)
- Standard: $30 (6 cards, 4 pulls/mo)
- Dealer: $75 (20 cards, 12 pulls/mo)
- Pro: $150 (50 cards, 30 pulls/mo)
- Margins: 71-95% across scales
- Entry covers cost (acceptable), Dealer = real revenue

### Cost optimization roadmap (Sept 16, drafted)
- User-count goals trigger stage transitions
- eBay Developer Account sign-up = immediate next step
- Card Ladder at $20/mo = sweet spot below 500 customers
- DIY at 500+ customers (requires dev investment)
- Partnerships at 1000+ customers

## Files created this session

| File | Status |
|---|---|
| `For You/Plans/pricing-decision-2026-09-16.md` | NEW (90 lines, commit `999ca0d`) |
| `For You/Plans/cost-breakdown-2026-09-16.md` | NEW (129 lines, commit `1aaadf0`) |
| `For You/Plans/cheaper-aggregation-paths-2026-09-16.md` | NEW (146 lines, commit `cfb2ce0`) |
| `For You/Plans/cost-cutting-roadmap-2026-09-16.md` | NEW (236 lines, commit `96e27e9`) |
| `For You/Plans/cost-cutting-roadmap-NOTEPAD-2026-09-16.txt` | NEW (plain-text version for notepad) |

## Open fires (one at a time)

### IMMEDIATE (when founder returns)
1. **Sign up for eBay Developer Account** (5 min, free) — biggest immediate win
2. **Get eBay Buy API credentials** (10 min)
3. **Build eBay Buy API integration** (~2-4 hours dev)
4. Test with current 12 Jim cards
5. Save $43/mo at 100 customers

### NEXT (when 25+ customers)
1. Subscribe to Pricecharting API ($6/mo)
2. Replace Apify SCPRO actor with direct API

### NEXT (when 50+ customers)
1. Subscribe to Card Ladder Pro ($20/mo)
2. Replace eBay + SCPRO + PSA with Card Ladder

### NEXT (when 500+ customers)
1. Phase 1: Build own PSA search actor (3 weeks dev)
2. Phase 2: Direct BD scraping for eBay/sportscardspro (2 weeks)
3. Phase 3: Add 130point for auction house data (1 week)

### NEXT (when 1000+ customers)
1. Strategic partnerships with Heritage/Goldin/PWCC
2. PSA Enterprise tier (GemRate)

## Other open fires (still pending from previous sessions)

1. URL ownership pattern (shower insight)
2. Phase 1 PSA search actor (October target)
3. PSA unblock testing (different IP)
4. Cron job for bot (auto-alerts)
5. Email field on form
6. 90% CI + 70% CI section (need to capture CIs)
7. Top X deals on website (5 or 10? — founder undecided)
8. Build Stripe products for new tiers (4 new prices, 4 new payment links)
9. Update DB tier values (trial → casual/standard/dealer/pro)
10. Update Google Form with new tier options

## Today's grand total (Sept 16)

| Feature | Status | Commit |
|---|---|---|
| Webhook branding | ✅ | `de8b550` |
| V3 stock-class ticker | ✅ | `e20cc14` |
| PSA pop for 2/12 Jim cards | ✅ | `26800ad` |
| Long-term PSA plan | ✅ | `6f11447` |
| Dashboard auto-fetch pop | ✅ | `e76dced` |
| Cost model for Card Hedge | ✅ | `add4528` |
| PSA block + Path B decision | ✅ | latest |
| Card Hedge pricing concern doc | ✅ | latest |
| Bot run for all customers | ✅ | (no commit) |
| deal_detector.py | ✅ | `8ebe702` |
| V3 alert layout (Jim + founder) | ✅ | `fa71896` |
| Pricing decision | ✅ | `999ca0d` |
| Cost breakdown | ✅ | `1aaadf0` |
| Cheaper aggregation paths | ✅ | `cfb2ce0` |
| Cost-cutting roadmap | ✅ | `96e27e9` |

**15 features/docs, $0 spent on infrastructure.**

## Memory note for next session

When conversation resumes:
- Pricing model: Casual $15 / Standard $30 / Dealer $75 / Pro $150
- Cost-cutting roadmap: 5 stages with customer count triggers
- IMMEDIATE: Sign up for eBay Developer Account (free, 5 min)
- Card Ladder = sweet spot at 50-500 customers ($20/mo flat)
- eBay Buy API = biggest immediate win (free)
- PSA still blocked, using Apify with retries
- 11/12 Jim alerts delivered today with V3 layout

## When founder returns

Likely next:
1. Sign up for eBay Developer Account
2. Build eBay Buy API integration
3. Or: continue with other open fires
4. One fire at a time per founder's preference
