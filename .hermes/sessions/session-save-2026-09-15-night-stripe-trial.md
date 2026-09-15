# Session Save - Sept 15, 2026 (Evening - Stripe 14-Day Trial LIVE)

## Time
Sept 15, 2026 ~7:15 PM (CDT)

## 🎉 HEADLINE WIN
**Card Scout now has a working Stripe 14-day free trial flow.** Joe Bob
(joebobemail@yahoo.com) successfully subscribed via the new Payment Link
and is in `trialing` status with trial ending **2026-09-29** (14 days).

## What we shipped tonight

### Stripe Phase 1 (sandbox trial flow)

1. **Researched Stripe docs** for trial + recurring + 3-tier setup:
   - Trial offers (new API) NOT supported on Payment Links
   - Legacy `subscription_data.trial_period_days` IS supported
   - 3-tier pricing = either 3 separate Products OR 1 Product + 3 Prices

2. **Jim's manual test (first)** with old Payment Link:
   - $50 charged immediately, no trial (link had no trial config)
   - 9 webhook events fired in 2 minutes (charge.succeeded, etc.)
   - All events captured for V3 design

3. **Built `scripts/stripe_integration.py`** (216 lines, STUB):
   - `get_payment_url()` - returns existing Payment Link
   - `validate_confirmation()` - validates Stripe IDs (ch/cs/pi/in/seti)
   - 7-test self-test passing
   - **Kept for reference only** - NOT in active flow

4. **Jim found Stripe secret key**:
   - First two were `mk_...` (restricted keys, can't create Payment Links)
   - Third was `sk_test_...` (correct secret key)
   - Saved to `C:\Users\J\Documents\LLM\Stripe.txt` temporarily
   - Hugo copied to `card-scout/.env` and removed old placeholder

5. **Created NEW Payment Link via Stripe API** with 14-day trial:
   - Link ID: `plink_1UG2DEFA55fKZHW6O1tvcAOT`
   - URL: `https://buy.stripe.com/test_aFabJ1cd30MlfSJa5s9Zm01`
   - Trial: 14 days
   - After trial: $50/mo recurring
   - Active: True

6. **Verified via API call**:
   - `subscription_data.trial_period_days = 14` ✅
   - `trial_settings.end_behavior.missing_payment_method = create_invoice` ✅

7. **Joe Bob subscribed via new link**:
   - Customer: `cus_VGZOdFbMSylvYW` (joebobemail@yahoo.com)
   - Subscription: `sub_1UG2FqFA55fKZHW6SWuQt6xf`
   - **Status: `trialing`** ✅
   - Trial end: 2026-09-29 (14 days from Sept 15)
   - Payment method saved: `pm_1UG2FoFA55fKZHW6lcfE9Wv7`
   - No immediate charge (working as designed)

## Files committed tonight

| Commit | File | Description |
|---|---|---|
| `b79a4fd` | `For You/Plans/stripe-manual-testing-playbook-2026-09-15.md` | Updated with both Payment Links table |
| `3c073a2` | `For You/Plans/stripe-setup-guide-2026-09-15.md` | Full Stripe research findings |
| `720eb3b` | `For You/Plans/v3-stripe-integration-2026-09-15.md` | V3 roadmap (corrected: webhook-driven, not confirmation#) |
| `<in-place>` | `.env` | Added STRIPE_SECRET_KEY + updated STRIPE_PAYMENT_LINK |
| `scripts/stripe_integration.py` | NEW | 216 lines, validate_confirmation() + get_payment_url() |

## Current state

### Stripe sandbox state

- **Account**: `acct_1UEWcAFA55fKZHW6` (Fuzzy Bracelet)
- **Product**: "Fuzzy Bracelet Card Alert Service" - $50/mo recurring
- **Price ID**: `price_1UEWrhFA55fKZHW6HZTiwKbI`
- **Subscriptions** (4 total in sandbox):
  | # | Customer | Status | Trial end | Created |
  |---|---|---|---|---|
  | 1 | joebobemail@yahoo.com | **trialing** | 2026-09-29 | Sept 15 |
  | 2 | jonathangeorge13@gmail.com | active | (none) | Sept 15 |
  | 3 | test2@gmail.com | active | (none) | Sept 11 |
  | 4 | testemail@gmail.com | active | (none) | Sept 11 |

### .env state (Sept 15)

```bash
STRIPE_PAYMENT_LINK=https://buy.stripe.com/test_aFabJ1cd30MlfSJa5s9Zm01  # NEW (with trial)
STRIPE_SECRET_KEY=sk_test_...h8Iy  # NEW (107 chars)
# STRIPE_WEBHOOK_SECRET=whsec_...  # Still commented (Stage 2)
# STRIPE_PRICE_ID=price_...  # Still commented (Stage 2)
```

### Code state (Sept 15)

- `sheets_importer.py` - Reverted the wrong "paste confirmation #" approach
- `discord_alert_bot_v3.py` - **No Stripe integration yet** (waits for webhook in Stage 2)
- `scripts/stripe_integration.py` - Stub, useful for tests but NOT in production flow

## The correct V3 flow (designed tonight, NOT built)

```
Customer signs up via Google Form
   ↓
sheets_importer creates customer with tier=trial, max_cards=3
   ↓
Bot immediately starts alerting (free tier, 3 cards max)
   ↓
Customer separately clicks Stripe Payment Link
   ↓
Stripe Checkout collects card info
   ↓
Stripe creates subscription in 'trialing' state for 14 days
   ↓
14 days pass...
   ↓
Stripe auto-charges $50
   ↓
Subscription status: 'trialing' → 'active'
   ↓
(Stage 2) Webhook fires → bot updates tier=paid, max_cards=12
```

**Key insight from Jim**: Beta testers should use the manual Stripe flow
NOW so we can OBSERVE what data Stripe sends us before automating.
Stripe sandbox events are visible at https://dashboard.stripe.com/test/events
even without our webhook endpoint listening.

## Webhook events to subscribe to (Stage 2 design)

| Event | When it fires | What we do |
|---|---|---|
| `customer.subscription.created` | Customer subscribes | Save stripe_customer_id, subscription_id |
| `customer.subscription.updated` | Status changes (trial → active) | Update tier: trial→paid, max_cards: 3→12 |
| `customer.subscription.deleted` | Customer cancels | Downgrade tier to canceled, max_cards=0 |
| `customer.subscription.trial_will_end` | 3 days before trial ends | (Optional) Send "trial ending" Discord DM |
| `invoice.payment_succeeded` | Recurring payment succeeded | Log payment, refresh period_end |
| `invoice.payment_failed` | Recurring payment failed | Downgrade tier to past_due, send Discord alert |

## What's NOT built yet

- ❌ Webhook endpoint (Stage 2, ~6 hours)
- ❌ DB columns for stripe_customer_id, subscription_id, etc.
- ❌ Auto-upgrade tier when trial converts
- ❌ 3-tier pricing (Hobby/Pro/Elite) - recommended to defer
- ❌ Stripe Live mode (stay in sandbox for now)

## Decisions captured

- **No card upfront** (14-day trial is standard SaaS pattern)
- **Stripe handles billing** (we just observe webhook events)
- **Manual tier upgrade for now** (Jim runs SQL when he wants to test paid flow)
- **Observe first, automate later** (avoid premature automation)
- **Defer 3 tiers** until first paying customer validates $50 tier
- **Both old + new Payment Links kept**: old for Jim's existing $50 customer, new for beta testers

## Key constraints preserved (Sept 14-15)

- **NEVER publish Card Scout's 3 actors** (PSA, sportscardspro, eBay) to Apify Store
- **Stay on Apify for now** ($7/mo for own actors is fine)
- **MULTI-VERTICAL FRAMEWORK STRATEGY** (Card Scout = V1, Coin Scout = V2)
- **MASTER BUSINESS THESIS** (multi-vertical framework for info/geo asymmetry)
- **$0.50/run cap** on any Apify run
- **Bright Data web_unlocker1** 5K/mo free tier preferred
- **NEVER `git add -A`** (Sept 14 incident)
- **Service account keys** in `C:\Users\J\.secrets\`
- **Webhook-as-password auth** for dashboard (no separate password)
- **Render deploy DEFERRED** (Sept 15, end of month)

## Today's full timeline (Sept 15)

1. morning - sheets_importer bug fixes (commit `fb7ca2d`)
2. mid-day - GCP SA key rotation (incident closed)
3. afternoon - pricing_bands populated + trend-aware alerts (commit `9e50d97`)
4. evening - Flask customer dashboard + V2 listing filter (commit `37efc32` + `<dashboard v2>`)
5. night - Stripe 14-day trial LIVE (this session)

**5 sessions, 10+ features shipped, 1 security incident closed, 1 deployed (Render cancelled)**

## Next session priorities (when ready)

| Priority | Item | Time | Trigger |
|---|---|---|---|
| 1 | Joe Bob trial converts in sandbox (observe) | 0 min | Just wait, Sept 29 |
| 2 | Recurring subscription handling (Stage 2) | ~6 hours | When 1+ paying customer |
| 3 | 3-tier pricing | ~3 hours | When customers ask for tiers |
| 4 | Render deploy | ~30 min | End of month (cash flow) |
| 5 | Rec 2 invite codes | ~1 hour | This week (spam defense) |

## Open questions for Jim

1. **Do you want to ship the trial NOW?** (Stage 1.5 - DONE) ✅
2. **3 tiers: when to add?** (Defer until first paying customer)
3. **Webhook handler: hosted where?** (Add to dashboard, Hetzner when deployed)
4. **Customer matching: how do we link Stripe customer to our DB customer?**
   - Recommended: by email (need to add email field to form)

## Reference docs (committed)

- `For You/Plans/stripe-setup-guide-2026-09-15.md` (291 lines) - Full Stripe research
- `For You/Plans/v3-stripe-integration-2026-09-15.md` (240+ lines) - V3 roadmap (corrected)
- `For You/Plans/stripe-manual-testing-playbook-2026-09-15.md` (152+ lines) - Beta tester playbook
- `scripts/stripe_integration.py` (216 lines) - Stage 1 stub
- `scripts/stripe_integration.README.md` - Stage 1 stub docs

## Memory update (compact)

- V3 STRIPE INTEGRATION (Sept 15): webhook-driven, observe first, automate later
- 2-LAYER SPAM PROTECTION (Sept 15, shipped `1a5386a`)
- Pricing_bands (Sept 15) + Trend-aware alerts (Sept 15, commit `9e50d97`)
