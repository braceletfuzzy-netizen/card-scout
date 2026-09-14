# Card Scout — Ticker System Spec

> **🎯 MASTER SPEC — V1 Bloomberg Ticker (Active Sept 14, 2026)**
> This is the active spec for Card Scout V1. The previous "grading-economics" version is SUPERSEDED (see `card-scout-graded-focus-spec-2026-09-14.md`).
> Status: ACTIVE — Hugo is implementing per this doc.

## Business Model

**Card Scout = Bloomberg Terminal for the trading card market.**

### Product Tiers (Future)

| Tier | Price | What You Get | Audience |
|---|---|---|---|
| **Ticker (Core)** | $X/mo | Market values, anomalies, trends, scarcity | Buyers, collectors, casual users |
| **Ticker Pro** | $XX/mo | Multi-card tracking, alerts, API access, historical data | Active collectors, investors |
| **Mega Deluxe (Future)** | $XXX/mo | Advisor mode, arbitrage calculator, grading optimization, full analytics suite | Dealers, high-volume flippers |

**The Mega Deluxe features include:**
- Advisory mode ("should I buy this?")
- Arbitrage calculator (grading cost + sell fees + profit)
- Bulk grading optimization (25-card batches)
- Authority recommendations (when to use PSA vs BGS vs CGC)
- "Best grade to submit" predictions
- Consignment house comparisons
- ROI forecasting

**These are FUTURE features, not core.** Today's customer is buying the Bloomberg ticker, not the advisor.

## Core Identity

**Card Scout is a Bloomberg Terminal for trading cards.**

We are NOT:
- A marketplace (no buying/selling through us)
- A grading authority (we don't grade)
- An investment advisor (no "should you buy" recommendations)
- A consignment service (we don't take possession)

We ARE:
- A price ticker (current market value)
- A trend signal (price changes over time)
- A scarcity reporter (PSA population data)
- A deal finder (listings below market)
- An information broker

**Customer Value**: "Tell me what this card is worth RIGHT NOW and how that compares to historical prices."

## Future Evolution Path

```
V1 (Today): Ticker — Bloomberg for cards
   ↓
V2 (1-2 yrs): Ticker Pro — multi-card tracking, alerts, API
   ↓
V3 (2-3 yrs): Mega Deluxe — advisor mode + arbitrage + grading optimization
   ↓
V4 (Possibly): Market maker (consignment, grading integration)
```

**The Bloomberg model scales from $0 to $25K/seat.** Card Scout follows the same arc:
- Start with information (low friction, mass adoption)
- Add features that save time (collectors pay for convenience)
- Eventually offer advisor services (dealers pay for edge)

**Our core = information. Our future = optional advisory services.**

## The Usage Pattern (Information Asymmetry)

Card Scout exists because **information asymmetry creates opportunity**.

```
Information asymmetry (our service)
        ↓
User sees a pricing anomaly (PSA 9 listed $90, typical $110-$200)
        ↓
User does their own math (grading cost, time, sell channel)
        ↓
User profits because they SAW the deal first
        ↓
We never told them to buy — we showed them the price
```

**We don't enable arbitrage. We surface it through information.**

Users will naturally:
- See a raw Bo Jackson listed $5 when typical is $20 → "Hmm, might grade up"
- See PSA 9 Bo Jackson listed $90 when typical is $150 → "That's a deal, let me check"
- See PSA 10 trend up 12% last month → "Time to move inventory"

**All their own math. Our job: surface the anomaly clearly.**

## The Output Model

For each card in our system, we report:

### 1. Market Value Per Grade
The actual current price for each grade tier:

```
Bo Jackson RC 1987 Donruss
  PSA 10 (Gem Mint):     $1,200 (typical $1,050-$1,400)
  PSA 9 (Mint):          $150   (typical $110-$200)
  PSA 8 (NM-MT):         $45    (typical $30-$60)
  PSA 7 (NM):            $25    (typical $20-$35)
  Raw (ungraded):        $20    (typical $10-$30)
```

### 2. Below-Market Deals
Listings currently below the typical range for their grade:

```
🎯 Found 3 deals below market (Bo Jackson PSA 9):
  $90   (33% below typical $110-$200 range)
  $95   (35% below range)
  $105  (15% below range)
```

### 3. Trend Signals
How prices are moving over time:

```
📈 Bo Jackson PSA 9 — Last 30 days
  7d change:   +5.2% (accelerating)
  30d change:  +12.1% (steady up)
  Trend: 🔥 ACCELERATING_UP
```

### 4. Scarcity Context
How rare the card is in each grade:

```
🎯 PSA Population (Scarcity)
  PSA 10: 234 cards exist
  PSA 9:  1,847 cards exist
  PSA 8:  5,213 cards exist
  Rarity: PSA 10 = 0.6% of all graded copies
```

## What We Don't Calculate

❌ **Grading cost** — Customer's decision, not ours
❌ **Grading probability** — Customer's risk
❌ **Net profit** — Customer does their own math
❌ **Investment recommendations** — We report data, customer decides
❌ **Consignment fees** — Customer picks selling channel
❌ **Expected value with grading** — Out of scope
❌ **Whether to buy** — Customer's call

**We surface pricing anomalies. Users discover arbitrage opportunities through information.**

## Why This Is Cleaner

**V1 (Grading Economics Approach)**:
- Customer asks: "What's a deal?"
- We answer: "Expected value $61 profit, with $20 grading cost and 30% probability of PSA 9"
- Customer thinks: "Wait, that's complicated"
- Customer leaves

**V2 (Ticker Approach)**:
- Customer asks: "What's a deal?"
- We answer: "PSA 9 Bo Jackson lists at $90, typical range $110-$200, that's a deal"
- Customer thinks: "Cool, I'll buy it"
- Customer stays

**Simplicity wins.** Bloomberg doesn't tell you whether to buy Apple stock. They show you the price.

## Customer Segments (Updated)

| Persona | What They Want | What We Show |
|---|---|---|
| **Buyer** | Cheapest grade-X listings | "PSA 9 Bo Jackson deals: $90, $95, $105" |
| **Collector** | Mint condition cards | "PSA 10 deals this week" |
| **Dealer** | Buy/sell spread | "Buy PSA 9 at $90, market avg $150 = $60 spread" |
| **Investor** | High-grade trends | "PSA 10 trending up, +12% last 30d" |
| **Casual** | What's my card worth | "Your raw Bo Jackson: $20 typical, range $10-$30" |

## The Math We DO Use

### Statistical Range (For Each Grade)

From Sportscardspro data:
- Recent sales for each grade
- Compute mean + standard deviation
- 90% confidence interval = mean ± 1.645 × SD

```
PSA 9 Bo Jackson:
  Mean: $150
  SD: $30
  90% range: $101-$199 (~$150 ± $49)
```

This is **statistical honesty**, not prediction. We're saying "90% of recent sales fell in this range."

### Trend Calculation

```
7d change:  (today_price - 7d_ago_price) / 7d_ago_price
30d change: (today_price - 30d_ago_price) / 30d_ago_price
```

### Q Bands (Existing)

```
Q1 = 25th percentile of recent sales
Median = 50th percentile
Q3 = 75th percentile
```

## Customer-Selectable Authority — When?

**V1 (Now)**: Skip. Defaults to "report the market as-is."

**V2 (Later, 100+ customers)**: Could add as a setting:
- Default authority for their "grading expectations"
- Helps them see "what would PSA 10 Bo Jackson sell for" vs "what would CGC 10 sell for"
- But NOT for profit calculation

**Why V2**: Once we have volume, we can show authority-specific price trends. PSA vs CGC vs BGS pricing for the same card.

**Implementation cost when added**: 1 DB column + 1 form field + 1 lookup in alert code. ~30 min.

## EV Range — Statistical Math

**Implementation** (Hugo):
1. Pull recent sold prices for each grade tier from Sportscardspro
2. Compute mean + standard deviation
3. Show range: "$X typical ($Y - $Z range)"
4. Use Z=1.645 for 90% confidence (one-tailed) or 1.96 for 95%

**Simple stats, no ML needed.** Just numpy/pandas on a list of recent sales.

## Out Of Scope (Definitely)

❌ Grading cost calculator
❌ Grading probability model
❌ Net profit calculations
❌ Expected value formulas
❌ Consignment fee awareness
❌ "Best grade to submit" advice
❌ "Best authority for this card" advice

## Out Of Scope (Maybe Later)

- Customer-selectable authority preference (V2)
- Bulk deal optimization (25-card batches)
- Set completion tracking
- Watchlist alerts (per customer)

## In Scope (V1)

✅ Market value per grade
✅ 90% range per grade (statistical)
✅ Below-market deal alerts
✅ Trend signals (7d/30d)
✅ Q bands (existing)
✅ PSA population data
✅ Discord alerts (existing)
✅ Customer onboarding via form (existing)

## Roles Recap

**Cosmo**: spec docs, customer flow, DB queries, light config, bug discovery + handoff docs

**Hugo**: actor code, parser updates, statistical math, output formatter, all heavy lifting

## Implementation Estimate (Hugo)

- Grade detection regex: ~30 min
- Statistical range calculator: ~1 hr
- Per-grade market value table: ~2 hrs
- Update output formatter (drop profit calc): ~1 hr
- Testing: ~1 hr
- **Total: ~5.5 hrs**

## Status

- ✅ Reframe to ticker system
- ✅ Removed grading economics from model
- ✅ Statistical math for ranges (90% CI)
- ✅ Customer-selectable authority deferred to V2
- ✅ Hugo implemented V1 (Sept 14, 2026, commit 6b1d454) — see "V1 Implementation Status" section below
