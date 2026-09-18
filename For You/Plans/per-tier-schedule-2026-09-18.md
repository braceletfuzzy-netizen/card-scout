# Per-Tier Schedule Config (Sept 18)

## Founder's tier-value framing (Sept 18 evening)

> "At the lower tier the value proposition becomes time saved, having a helper.
> At the dealer level, it's finding the deals to make you more profitable.
> As long as we can satisfy both I am ok with the costs because we are a data
> aggregation service at one level and a data interpretation service at another
> level up. Unless we can get free access the costs are the costs and we need
> to make a profit."

**This is the entire pricing strategy in one paragraph:**

### Two products in one

| Tier | What we sell | What customer gets |
|---|---|---|
| Casual / Standard | **Data aggregation service** | "I don't have to watch eBay every day. Someone watches for me." |
| Dealer / Pro | **Data interpretation service** | "I make more money because someone finds me profitable deals I would've missed." |

### Why this justifies the cost difference

- Casual: 1×/wk scan = $3.53/mo cost = essentially free for us
- Pro: 3×/day scan = $52.95/mo cost at max = 65% margin still

The **value** to the customer scales faster than the cost:
- A casual collector saves 30 min/wk of manual eBay search = $X of time
- A dealer makes $Y from one good deal = many multiples of their subscription

**Both tiers are profitable if priced correctly.** No tier needs to "subsidize"
the other. Path A (throttling) maintains margin across the spectrum.

### Cost reality (Sept 18 founder directive)

> "Unless we can get free access the costs are the costs and we need to
> make a profit."

Card Hedger $49/mo is essentially "free" (we use it for all tiers).
Apify eBay $0.0353/run is the only meaningful variable cost.
GEMRATE $200/mo only kicks in when we have 7+ paying Pro customers.

### Architecturally

- Lower tiers = automated aggregation pipeline, raw signals out
- Higher tiers = interpretation layer (per-grade FMV math, sell-window
  detection, trend signals)
- The aggregation pipeline pays for itself; the interpretation is the
  premium product

## Founder's intent (18 Sep 2026 desktop notes)

Verbatim from `18 Sep 2026 Notes.txt`:
> "We can have the valuation Calc/ ticker pull on its schedule
> (valuation to customer cost)"
> "We can have the deals pull 12 hour intervals for base tier
> (deals to customer cost 'eBay')"
> "if the cost is low enough/nil we can have the deal push set to scan
> hourly etc."

Two distinct cost levers:
1. **Valuation pulls** (Card Hedger FMV) — bundled with $49/mo subscription, no per-call cost
2. **Deals pulls** (eBay/Apify) — $0.0353/run, **this is the variable cost lever**

## Three pull types in our system

| Pull type | Source | Cost/run | Used for |
|---|---|---|---|
| CH FMV | Card Hedger API | $0 (subscription) | `below_fmv` alerts, `sell_window` alerts, Vault values |
| eBay active | Apify eBay+Etsy actor | $0.0353 | `below_median` alerts, `below_fmv` listings comparison |
| SCPro sold | Apify SCPro actor | $0.0033 | `sell_window` median calculation, sold comps |

## Tier schedule (recommended — with throttling)

**KEY INSIGHT (Sept 18 recalc):** Apify eBay+SCPro cost is $0.0353+$0.0033 per
run per card. At max-cards per tier, several tiers BREAK EVEN or LOSE money.
**Solution: throttle cadence based on portfolio size.**

### Cadence by tier × card count

| Tier | Price | max_cards | ≤25 cards | 26-100 cards | >100 cards |
|---|---|---|---|---|---|
| **Casual** | $15 | 25 | 1/week | n/a (max 25) | n/a |
| **Standard** | $30 | 75 | 3/week (MWF) | 1/week | 1/week |
| **Dealer** | $75 | 250 | 1/day (6am) | 3/week | 1/week |
| **Pro** | $150 | unlimited | 3/day (6am/2pm/10pm) | 1/day | 3/week |

### Margin check at each tier's MAX card count

| Tier | Max cards | Cadence | Monthly eBay cost | Margin at max |
|---|---|---|---|---|
| Casual | 25 | 1/wk (4 runs/mo) | $3.53 | 76% |
| Standard | 75 | 1/wk (4 runs/mo, throttled) | $10.59 | 65% |
| Dealer | 250 | 1/wk (4 runs/mo, throttled) | $35.30 | 53% |
| Pro | 100 | 1/day (30 runs/mo) | $105.90 | 29% |

**Pro tier economics:** At 100 cards with 1/day cadence, margin is 29%. That's
still positive but thin. Solutions:
- (a) Require `>= 50 cards` to get Pro (force higher-value customers)
- (b) Throttle Pro cadence to 1/day only above 100 cards (already in plan)
- (c) Raise Pro price to $200/mo (matches GemRate cost)

**Recommended: option (b) — already in the table above.**

### Why throttling works

Customers with small portfolios WANT frequent updates (they're watching each
card closely). Customers with large portfolios can tolerate less frequent
updates (each card matters less). Throttling is win-win: small customers get
their frequent alerts, big customers get reasonable cost structure.

### Cost ceiling problem (originally raised)

Original plan: Pro tier at 50 cards + 3×/day = $164/mo cost, -9% margin.
Fixed: throttling kicks in beyond 25 cards, dropping Pro cadence from 3/day
to 1/day. Now: Pro at 50 cards = $26.47/mo cost = **82% margin**.

## Why these specific cadences

### Casual (1/week)
- "I'm casually watching this card" — don't need minute-by-minute updates
- 1/week = ~4 runs/mo = ~$0.04/mo cost (essentially free)
- Matches founder's framing: "monthly digest-style" for casual

### Standard (3/week = MWF)
- "I want to know about deals but not be spammed"
- Matches our CURRENT cron schedule (`0 8 * * 1,3,5`)
- 12 runs/mo × $0.0353 = $0.42/mo (cheap)

### Dealer (1/day)
- Active dealer needs daily alerts to compete
- Daily at 6am = "morning report" style
- 30 runs/mo × $0.0353 = $1.06/mo (manageable)

### Pro (3/day)
- High-velocity dealer / shop — needs real-time alerts
- 6am, 2pm, 10pm — covers business hours + close-of-day
- 90 runs/mo × $0.0353 = $3.18/mo (high but proportional)

## Implementation

### 1. Tier-aware cron schedule

Add `tier` column-aware scheduling. Each customer tier gets a cron that runs
ONLY their cards. We have 4 options:

**Option A**: 4 separate crons (one per tier)
- `card-scout-casual-alerts` runs Sundays at 6am
- `card-scout-standard-alerts` runs MWF at 8am (current)
- `card-scout-dealer-alerts` runs daily at 6am
- `card-scout-pro-alerts` runs 3× daily (6am, 2pm, 10pm)
- Pro: Each cron is tier-specific, easy to reason about
- Con: 4× the cron count

**Option B**: One cron, in-loop check tier
- `card-scout-alerts` runs every 2 hours
- Script checks each customer's tier, skips if not their tier's window
- Pro: One cron to manage
- Con: Wastes CPU checking each customer, more complex logic

**Option C**: Per-customer cron (advanced)
- When a customer upgrades, create a new cron
- Pro: Most efficient
- Con: Cron management complexity (cron counts grow with customers)

**Recommended: Option A** — simple, clear, matches our current pattern.

### 2. Settings table

```sql
CREATE TABLE customer_settings (
    customer_id INTEGER PRIMARY KEY,
    tier TEXT NOT NULL,
    schedule_ch_fmv TEXT,  -- cron expression
    schedule_ebay_active TEXT,
    schedule_scpro_sold TEXT,
    max_cards INTEGER DEFAULT 25,
    vault_max_cards INTEGER,  -- from PL-007 tier policy
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

Default schedules by tier:

```python
DEFAULT_SCHEDULES = {
    'casual':    {'ch_fmv': '0 6 * * 0',     'ebay_active': '0 6 * * 0',     'scpro_sold': '0 6 * * 0'},
    'standard':  {'ch_fmv': '0 8 * * 1,3,5', 'ebay_active': '0 8 * * 1,3,5', 'scpro_sold': '0 6 * * 0'},
    'dealer':    {'ch_fmv': '0 6 * * *',     'ebay_active': '0 6 * * *',     'scpro_sold': '0 6 * * *'},
    'pro':       {'ch_fmv': '0 6,14,22 * * *', 'ebay_active': '0 6,14,22 * * *', 'scpro_sold': '0 6 * * *'},
    'beta_power': {'ch_fmv': '0 8 * * 1,3,5', 'ebay_active': '0 8 * * 1,3,5', 'scpro_sold': '0 6 * * 0'},
    'trial':     {'ch_fmv': '0 8 * * 1,3,5', 'ebay_active': '0 8 * * 1,3,5', 'scpro_sold': '0 6 * * 0'},
}
```

### 3. Per-tier cron scripts

Replace the current single cron `2fb20f7ad396` with tier-aware versions:

```bash
# Current: runs Jim + Alan (mixed tiers, all get same schedule)
# New: 4 separate crons

# Casual/Standard/Trial/Beta — current schedule, but tier-aware
0 8 * * 1,3,5  python run_alerts.py --tiers casual,standard,beta_power,trial

# Dealer — daily
0 6 * * *     python run_alerts.py --tiers dealer

# Pro — 3× daily
0 6,14,22 * * *  python run_alerts.py --tiers pro
```

When a customer upgrades, they get a different effective schedule automatically.

## Why this matters for Pro tier ($150/mo)

Currently: Pro tier is "Coming Soon" because we can't deliver:
- Population context (PSA/BGS/SGC/CGC)
- Cert # lookup & vault tracking (Vault = PL-007 ✅ just shipped)
- Player-level trend aggregation (PL-006)
- Bulk catalog CSV (PL-008 ✅ just shipped)

With tier schedule config, Pro can also have:
- **3× daily alerts** = always up-to-date
- **Pro-tier sell_window alerts on Vault items** (per Sept 18 PL-007 decision)
- **Hourly deal push** during business hours (per founder's note "if cost is low enough/nil")

## Open questions for Jonathan

1. **Casual tier: weekly OR monthly?**
   - Weekly (4 runs/mo, $0.04): more competitive vs other tools
   - Monthly (1 run/mo, $0.01): matches Sept 16 "monthly digest" framing
   - Recommendation: weekly for casual ($15 is not enough for daily)

2. **Pro tier: 3× daily OR 1× daily?**
   - 3× daily ($3.18/mo/customer at 12 cards) is what I sketched
   - 1× daily halts cost to $1.06/mo but is less of a "real-time" feel
   - Recommendation: 3× daily for Pro — they've paid $150, they want urgency

3. **Same schedule for all 3 pulls, or different?**
   - Same: simpler, all data fresh at same time
   - Different: eBay active can run hourly if CH stays cached
   - Recommendation: same schedule per tier (simpler)

4. **Should we make schedules customer-overridable?**
   - E.g., a Dealer paying $75 can opt for daily at no extra cost
   - Risk: customers game the system
   - Recommendation: NO overrides — keeps tier differentiation clear

## Build effort estimate

- Settings table: 30 min
- 3 new tier-aware crons: 1 hr
- run_alerts.py with --tiers flag: 2 hrs
- Schedule config UI in dashboard: 2 hrs (optional)
- **Total: ~3 hrs core, +2 hrs UI**
