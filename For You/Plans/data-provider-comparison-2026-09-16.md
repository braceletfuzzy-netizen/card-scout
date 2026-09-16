# Data Provider Comparison (Sept 16, 2026)

## Time
Sept 16, 2026 (evening)

## Status
**DRAFTED.** Founder asked: "Look over alternatives to Card Ladder".

## Decision
**Layered stack: Card Ladder ($20) + SportsCardsPro API ($6) + eBay Browse (free)
= $26/mo full data stack for 50-500 customers**

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

## Layered stack (founder insight Sept 16)

| Source | Cost | What it gives |
|---|---|---|
| **eBay Browse API** | FREE | Listing data — spread from multiple active listings |
| **Pricecharting API** | $6/mo | Baseline single price per grade |
| **Card Ladder** | $20/mo | Sold data + pop data + sales history |
| **TOTAL** | **$26/mo** | Full data stack |

## Why this works

1. **eBay Browse** = spread source (multiple active listings = lower-third detection works)
2. **Pricecharting** = cheap fallback when eBay doesn't have the card
3. **Card Ladder** = sold prices (what people actually paid) for trend signals
4. **Card Ladder has pop data** → PSA actor drops out entirely

## Implementation sequence

### October (now)
- Wait for eBay Developer verification
- Build eBay Browse API integration
- Replace Apify eBay actor

### November
- Subscribe to Pricecharting Collector ($6/mo)
- Build PC API integration
- Replace Apify SCPRO actor

### December (or when 50+ customers)
- Subscribe to Card Ladder ($20/mo)
- Build Card Ladder integration
- Drop PSA actor entirely
- Stage 3 fully activated

## Decisions captured

### CONFIRMED
- **Card Ladder**: $20/mo subscription (next month or when 50+ customers)
- **SportsCardsPro API**: $6/mo added as fallback/baseline (when 25+ customers)
- **eBay Browse API**: free, biggest immediate win

### DEFERRED
- **Card Hedge**: still ON HOLD (x402 + sales call friction)
- **Ximilar**: wrong stage (V2.5+ feature)
- **SCN**: wrong category (dealer tool, not data API)

## Files

| File | Status |
|---|---|
| `For You/Plans/cost-cutting-roadmap-2026-09-16.md` | UPDATED — Stage 2/3 now reflect layered approach |
| `For You/Plans/data-provider-comparison-2026-09-16.md` | NEW (this doc) |

## Open fires

1. Wait for eBay Developer verification (~1 day)
2. Build eBay Browse API integration (~2-4 hours)
3. Subscribe to PC API (when 25+ customers)
4. Subscribe to Card Ladder (next month or when 50+ customers)
