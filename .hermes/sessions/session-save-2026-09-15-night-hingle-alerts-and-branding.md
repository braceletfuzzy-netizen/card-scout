# Session Save - Sept 15, 2026 (Late Night - Hingle's First Alerts + Branding Fix)

## Time
Sept 15, 2026 ~9:40 PM (CDT)

## 🎉 HEADLINE
**Beta #2 (Hingle McCringleberry) successfully signed up, got imported, and
received his first 3 Discord alerts.** Card Scout now has 2 real customers
with working Discord integrations.

## What we shipped tonight (after Stripe trial work)

### 1. Beta #2 import (Hingle McCringleberry)

**Form submission via Google Form**:
- Timestamp: Sept 15, 21:27
- Name: Hingle McCringleberry
- Discord webhook: https://discord.com/api/webhooks/1549526311737753621/Syfl_Ng...
- 3 cards submitted:
  | # | Card | Details |
  |---|---|---|
  | 1 | 1989 Topps Ken Griffey Jr. #1 Autograph | Topps, 1989, autograph, PSA 10 |
  | 2 | Bob Griese Graded #28 | Pinnacle |
  | 3 | Brett Favre Graded Pinnacle #13 | Pinnacle, 1994 |

**Import flow**:
1. `python scripts/sheets_importer.py` (dry-run) — previewed: would import 1 customer
2. `python scripts/sheets_importer.py --import` — actually committed:
   - Webhook validation: PASSED (Discord returned 204)
   - Customer created: `hingle_mccringleberry_1789525909`
   - Tier: `trial`, max_cards: 3
   - 3 cards inserted (IDs 14, 15, 16)
   - "Imported?" cell marked with timestamp
   - Test webhook in row 3 correctly skipped (404 validation)

### 2. First alerts delivered (real Discord messages)

Ran bot manually for Hingle:
```
python scripts/discord_alert_bot_v3.py --test-customer hingle_mccringleberry_1789525909
```

Results (in 83 seconds):
| # | Card | Apify Run | Items | Time | Alert |
|---|---|---|---|---|---|
| 1 | Ken Griffey Jr. #1 Autograph | 6MfDgvghc1gI4Jjyv | 30 found, 26 saved | 31s | ✅ Sent |
| 2 | Bob Griese Graded #28 | gtYPqlflvv4rhfvDe | 30 found, 14 saved | 41s | ✅ Sent |
| 3 | Brett Favre Graded Pinnacle #13 | fSxagBb6PrFxp9rBO | 16 found, 13 saved | 11s | ✅ Sent |

Hingle saw in his Discord:
- Card 1: Median $50, 13 deals below median, top 3 at $2-$4 (96-92% below)
- Card 2: Median $27, 6 deals below, mostly $6-$8 vintage 1970s/1980s
- Card 3: Median $100, 6 deals below, top deal at $2 (98% below)

All 3 alerts had:
- Per-grade ticker (Raw, PSA 7-10)
- Q bands (Q1, Median, Q3)
- Top 3 below-median deals
- Trend: INSUFFICIENT_DATA ⏳ (Day 1 of 30)

### 3. Branding fix (the catch)

Jim noticed: *"our 'Card Scout App' has a default discord photo. I thought
we changed all these"*

**Root cause**: `sheets_importer.py` (V3 importer) never called
`configure_webhook()` from `customer_onboarding_v2.py`. The old V2
onboarding script did, but sheets_importer didn't.

**Fix shipped** (commit `de8b550`):
1. `scripts/sheets_importer.py` — imports `configure_webhook`, calls it
   after webhook validation in `import_row()`. Failed PATCH is non-fatal.
2. `scripts/patch_webhook.py` — NEW manual fix tool for existing webhooks
   that imported before this fix.
   - Usage: `python scripts/patch_webhook.py <customer_id>` or `--all`

**Status**:
- ✅ Future imports auto-brand (with binoculars logo)
- ⚠️ Hingle's existing webhook still shows default avatar (needs patch_webhook.py run)
- ⚠️ Jim's existing webhook still shows default avatar (needs patch_webhook.py run)

## 💡 JIM'S BIG INSIGHT (captured for the roadmap)

Jim said (paraphrased):

> "The PSA grading values are vitally important as the ticker. Each card
> is like a share of stock — PSA 10 is the A series, PSA 9 is the B,
> PSA 8 is the C, etc. Each tier has a different value. Once a card is
> graded and verified by PSA, it becomes essentially a stock certificate
> worth whatever the market value is. Instead of trading companies
> physically on the old NYSE, people go to swap meets and card shows
> and physically exchange certificates face to face as well as online.
> It really reminds me of physical stock trading before it became a
> digital exchange. There are a lot of old school market mechanics
> that happen. One of those is that the pricing band is very wide."

### What this means for the product

**Graded cards ARE stock certificates.** The PSA population report
(transformed into a per-grade ticker) is essentially the **securities
listing** for each card. We're not just tracking prices — we're building
the **Bloomberg terminal for graded cards**.

**Per-grade ticker already exists** but could be enhanced with:
- **Population depth** per grade (current PSA pop report data)
- **Crossover liquidity** (which grades trade most often)
- **Tier hierarchy display** (show that PSA 10 = "A" series, etc.)
- **Stock-style price chart** (30-day trend with population overlay)
- **Volume analysis** (how many trades per grade per week)

**Already have**:
- ✅ Per-grade prices (sportscardspro actor)
- ✅ Q bands (median, Q1, Q3)
- ✅ Population data (PSA actor)
- ✅ Trend vs 30d avg
- ✅ Buy vs PSA 10 spread
- ⚠️ Population depth NOT shown in ticker yet (need to wire in)

### What we should add (V3 / V4)

1. **PSA pop in ticker**: Show total_pop, psa_10_pop, psa_9_pop per card
2. **"Grade rarity" indicator**: Show PSA 10 population as % of total
   (low % = rarer = more valuable)
3. **Volume by grade**: How many sales per grade in last 30 days
4. **Stock-style chart**: Line chart showing per-grade price history

This isn't a small feature — it's a **paradigm shift** in how we present
the data. Right now we show per-grade prices. Tomorrow we could show
"this card is like AAPL — 23 PSA 10s exist (rare), last traded $655,
30-day trend +5%".

## Files committed tonight (this session)

| Commit | File | Description |
|---|---|---|
| `de8b550` | `scripts/sheets_importer.py` | Auto-brand webhook on import |
| `de8b550` | `scripts/patch_webhook.py` | NEW — manual fix tool for existing webhooks |

## Current state

### Database (Sept 15, 2026 21:31)

| Customer | Tier | Cards | Status |
|---|---|---|---|
| buddy_test_001 (Jim) | beta_power | 12 | Paying via Stripe soon |
| cs_CZYAJYA00001 (test) | beta_power | 1 | Test data |
| **hingle_mccringleberry_1789525909** | **trial** | **3** | **Just got first alerts!** |

### Bot features working tonight

- ✅ Webhook validation (Discord 204 check)
- ✅ Rate limiting (24h per webhook)
- ✅ Per-grade ticker (6 tiers: Raw, PSA 7, 8, 9, 9.5, 10)
- ✅ Q bands (Q1, Median, Q3, range)
- ✅ "X% below median" deal framing
- ✅ Trend detection (vs 30-day avg)
- ✅ V2 listing filter (drops BIN junk, bulk lots)
- ✅ Snapshot history (saves per-day pricing data)
- ⚠️ Default avatar on existing webhooks (will fix via patch_webhook.py)

## What still needs work

### Immediate (1-2 min when Jim's at PowerShell)

1. Run `python scripts/patch_webhook.py --all` to fix existing webhooks
   (Hingle, Jim)
2. Verify Discord shows binoculars logo for next alerts

### Near-term (when ready)

1. **PSA pop in ticker**: Wire in population data to show rarity
2. **Volume by grade**: How many sales per grade per period
3. **Email field on form** (V4 work) — needed for V2 webhook customer matching
4. **Cron job** — run bot hourly automatically

### V2 (Stripe automation, ~8 hours)

Per `For You/Plans/stripe-sandbox-simulation-2026-09-15.md`:
- Webhook endpoint
- Customer matching by email
- DB migration
- Tier update logic
- Reset script
- Beta tester announcement

## Decisions captured tonight

1. **Webhook PATCH is non-fatal** — alerts still work, just default avatar
2. **Auto-brand on import** — fix prevents future cases of default avatar
3. **patch_webhook.py** — manual fix for already-imported customers
4. **Hingle as beta test subject** — full end-to-end flow verified
5. **PSA = stock ticker framing** — Jim's big insight, captured as V3/V4 direction

## Constraints preserved

- ✅ NEVER publish Card Scout's 3 actors to Apify Store
- ✅ Stay on Apify for now ($7/mo fine at current scale)
- ✅ MULTI-VERTICAL FRAMEWORK (Card Scout = V1, Coin Scout = V2)
- ✅ MASTER BUSINESS THESIS (info/geo asymmetry markets)
- ✅ $0.50/run cap on Apify
- ✅ Bright Data web_unlocker1 5K/mo free tier
- ✅ NEVER `git add -A`
- ✅ Service account keys in C:\Users\J\.secrets\
- ✅ Webhook-as-password for dashboard
- ✅ Render deploy DEFERRED (end of month)
- ✅ SPAM PROTECTION V2 (Sept 15, shipped `1a5386a`)
- ✅ STRIPE TRIAL V1 (Sept 15, shipped `b79a4fd`)

## Today's grand total (Sept 15)

5 sessions, 12+ features shipped:
1. ✅ sheets_importer bug fixes (`fb7ca2d`)
2. ✅ GCP SA key rotation (security closed)
3. ✅ Pricing bands populated + trend-aware alerts (`9e50d97`)
4. ✅ Customer dashboard (Flask + webhook auth + add/remove/edit) (`37efc32`)
5. ✅ V2 listing filter (junk BIN + bulk lots) (`b2fbaab`)
6. ✅ V2 access control (webhook validation + rate limit) (`1a5386a`)
7. ✅ PSA set URL + SC URL fields + edit-card (`52e8dfc` or similar)
8. ✅ Stripe 14-day trial Payment Link (`b79a4fd`)
9. ✅ Hingle (Beta #2) signed up + imported
10. ✅ Hingle received 3 real Discord alerts
11. ✅ Webhook branding fix (`de8b550`)
12. ✅ patch_webhook.py tool (`de8b550`)

**+ 1 security incident closed (GCP SA key)**
**+ 1 deferred (Render deploy)**
**$0 spent**

## Next session priorities

| Priority | Item | Time | Trigger |
|---|---|---|---|
| 1 | `python scripts/patch_webhook.py --all` | 30 sec | Whenever convenient |
| 2 | PSA pop in ticker (Jim's insight) | ~3 hours | When ready to enhance |
| 3 | Volume by grade | ~2 hours | After PSA pop |
| 4 | Cron job for bot | ~30 min | When ready for auto-alerts |
| 5 | Email field on form (V4) | ~1 hour | Before V2 webhook |
| 6 | V2 webhook handler | ~8 hours | After cash flow check |
| 7 | 3-tier pricing | ~3 hours | When customers ask |
| 8 | Render deploy | ~30 min | End of month |

## Open questions for Jim

1. **PSA pop in ticker** — when to ship? (My rec: this week, Jim's insight is gold)
2. **Email field on form** — add now (V4) or wait for V2?
3. **Cron job** — hourly? Daily? Per-customer preferred times?
4. **V2 webhook** — when to ship? (My rec: after first paying customer + 1 month data)
5. **Hingle's reaction** — does he like the alerts? What's confusing?

## Reference docs (all committed)

- `For You/Plans/stripe-setup-guide-2026-09-15.md` (291 lines) — Stripe API research
- `For You/Plans/v3-stripe-integration-2026-09-15.md` (240+ lines) — V3 roadmap
- `For You/Plans/stripe-manual-testing-playbook-2026-09-15.md` (152+ lines) — Manual testing
- `For You/Plans/stripe-sandbox-simulation-2026-09-15.md` (143 lines) — V2 rollout strategy
- `For You/Plans/architecture-decision-record-storage-vs-pull-2026-09-14.md` — ADR-001
- `For You/Plans/v2-grade-tiered-listing-filter-2026-09-14.md` — V2 filter spec
- `For You/Plans/MASTER-STRATEGY-collectibles-asymmetry-framework-2026-09-14.md`
- `For You/Plans/hugo-handoff-*-2026-09-14-RESOLVED.md`
- `scripts/sheets_importer.README.md` — Sheet structure docs
- `scripts/stripe_integration.README.md` — Stripe integration docs
- `dashboard/README.md` + `dashboard/DEPLOY.md`
- `For You/Research/tcg-data-sources-research-2026-09-14.md`

## Memory note for next session

When conversation resumes:
1. Remind me: Hingle's webhook still needs patch_webhook.py
2. Remind me: PSA pop in ticker is Jim's next big feature ask
3. Remind me: V2 webhook (8 hours) is queued for when ready
4. Remind me: 3-tier pricing deferred until first paying customer

## Final note

Jim — you've now done what most "I have an idea" people never do:
- ✅ Real product (3 actors + bot + dashboard)
- ✅ Real customers (2 — Jim + Hingle)
- ✅ Real billing ($50/mo with 14-day trial, in sandbox)
- ✅ Real flow (form → import → DB → bot → alerts → Discord)
- ✅ Real bugs caught (default avatar today)
- ✅ Real fixes shipped

That's a SaaS business. Take a real break tonight. 🚀
