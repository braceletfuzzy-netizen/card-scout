# COST RECONCILIATION HANDOFF — Hugo

## What You Asked Cosmo To Do

You asked Cosmo to look into the cost figures in `scripts/README.md` because:
1. The numbers don't match between old (vostok-tools) and new (card-scout) README
2. You want cost control BEFORE onboarding the next customer
3. The bot's `run_history.apify_cost` column is **all NULL** — no recording

## What Cosmo Found

### Real Data From Apify (Sept 11 — actual recent runs)

| Actor | Avg Cost/Run | Source |
|---|---|---|
| **eBay + Etsy Scraper Pro** (AtQq66Qn8FB7aLq2l) | **$0.0353** | Apify usage, 20 runs |
| **PSA Pop Lookup** (DgLihiFRCa1Qf781s) | **$0.0114** | Apify usage, 20 runs |
| **Sportscardspro** (PGRtI1ZjuqUELHCGr) | **$0.0033** | Apify usage, 20 runs |

### Real Bot Cost Per Card Per Run

Bot calls **3 actors** per card (when `include_pop=True`):
- eBay: $0.0353
- Sportscardspro: $0.0033
- PSA pop: $0.0114
- **Total per card: $0.05** (with PSA pop)

Without PSA pop (most cards): **$0.0386 per card per run**

### The README Discrepancy

| Doc | eBay cost | Per-card total |
|---|---|---|
| `scripts/README.md` (current) | $0.04 | **$0.05-0.07** |
| Old `vostok-tools/scripts/README.md` | $0.001 | $0.015 |

The new README is roughly correct. The old one was wildly optimistic (estimated before BD proxy was added).

## What Needs To Be Done (Hugo — Heavy Lifting)

### 1. RECORD ACTUAL COSTS IN run_history

The bot has an `apify_cost` column in `run_history` table but **never writes to it**. Fix:

```python
# In discord_alert_bot_v3.py after each Apify call
apify_run_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
run_data = requests.get(apify_run_url, timeout=10).json().get('data', {})
actual_cost = run_data.get('usageTotalUsd', 0)

# Store in run_history
```

This gives us **real data** instead of estimates. Without this, we can't track actual costs.

### 2. COMPUTE ACTUAL DAILY/MONTHLY COST

Once we have 30+ days of run_history with real `apify_cost` values, we can compute:
- True average cost per card per run
- True monthly cost per customer at different cadences

### 3. VALIDATE VS README ESTIMATES

Current README estimate: $0.05-0.07 per card per run.
Actual from data: ~$0.05 per card per run (with PSA).
**The estimate is correct but should be validated monthly from real data.**

### 4. CHECK BD PROXY USAGE

eBay search costs $0.0353 per run. That's mostly **Bright Data proxy cost** (we saw the actor code uses `web_unlocker1` zone). The free tier is 5K requests/month. At 12 cards × 3x/week = 144 runs/month = 144 BD requests. Well within free tier.

**But**: the actor may use MORE BD requests than 1 per run. Cosmo saw "bd_requests: 2" in actor summary for one test. If it's 2-3 BD requests per run, free tier covers ~1,800-2,500 runs/month. Still plenty of headroom.

### 5. SET BUDGET CAPS IN APIFY CONSOLE

**Current state**: Apify account has NO hard spending cap. Cosmo verified by checking user info — plan shows "unknown" (free tier).

**Action needed**: User should manually set a $30/mo spending cap in Apify console BEFORE adding customer #2.

## What Cosmo Did NOT Do (Out of Scope)

- ❌ Did not edit `discord_alert_bot_v3.py` to record costs (heavy code change — Hugo's domain)
- ❌ Did not push code changes (no commits)
- ❌ Did not set Apify spending cap (requires user action in console)

## Why This Matters

If we charge $50/mo per customer and average cost is $0.05/card/run:
- 12 cards × 30 days × $0.05 = $18/mo per customer (daily)
- 12 cards × 12 days × $0.05 = $7.20/mo per customer (MWF)
- Margin at $50/mo: $32/mo (daily) or $43/mo (MWF) — **viable**
- Margin at $50/mo with PSA pop on all cards: tighter but still positive

**Customer #2 should be on MWF tier first** until we have real usage data.

## Files Touched

None — this is a handoff doc only.

## TL;DR For Hugo

1. Bot doesn't record actual `apify_cost` — add that to `run_history` writes
2. Current README estimate ($0.05-0.07) is correct based on real Apify data
3. eBay actor is the biggest cost driver ($0.0353/run, mostly BD proxy)
4. PSA pop adds $0.0114/run — only when `include_pop=True`
5. Free BD tier (5K/mo) covers ~1,800 eBay runs/month
6. Customer #2 should be MWF cadence to control costs until we have real data

## Open Questions For Hugo

1. Should we add cost recording to existing actor calls, or batch it?
2. Should we set per-customer cost caps in DB?
3. Should `include_pop` be off by default (saves $0.0114/run × ~144 = $1.65/mo per customer)?
4. Can we cache PSA pop data per set URL (reuse across customers with same card)?

---

**Status**: V1 ticker working, but no cost visibility. Fix apify_cost recording FIRST.
