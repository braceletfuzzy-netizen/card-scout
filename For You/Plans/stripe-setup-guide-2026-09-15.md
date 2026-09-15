# Stripe Setup Guide (Sept 15, 2026)

## Status
**Documented from research + Jim's manual test.** Stripe account exists in sandbox mode.
One product ($50/mo) exists. ONE problem to fix: no trial period on existing Payment Link.

## What Stripe account we have

- **Account ID**: `acct_1UEWcAFA55fKZHW6`
- **Business**: Fuzzy Bracelet (sandbox)
- **Email**: jonathangeorge13@gmail.com
- **Mode**: Test (sandbox)
- **Existing product**: "Fuzzy Bracelet Card Alert Service" - $50/mo recurring
- **Existing Payment Link**: `https://buy.stripe.com/test_8x25kD0ul7aJcGx91o9Zm00`

## What we just observed (Jim's manual test, Sept 15 7:08-7:09 PM)

Jim subscribed to the Payment Link with the test card `4242 4242 4242 4242`.

Events fired (in order):
1. `payment_intent.created`
2. `charge.succeeded` - **$50 charged immediately, no trial**
3. `payment_method.attached`
4. `payment_intent.succeeded`
5. `invoice.created` → `finalized` → `paid` → `payment_succeeded`
6. `customer.subscription.created` - status=`active` (not `trialing`)
7. `checkout.session.completed`

**Problem confirmed**: No trial period on current Payment Link. Customer was charged immediately.

---

## Question 1: How do we add a 14-day trial?

### Per Stripe docs (Sept 15, 2026):
> "Trial offers are only supported when creating subscriptions directly using the Subscriptions API. The following UI integrations don't support trial offers: Checkout, **Payment Links**, Elements with Checkout Sessions."

> BUT legacy `subscription_data.trial_period_days` parameter DOES work with Payment Links via API.

### Two options:

#### Option A: Recreate the Payment Link via API (RECOMMENDED)

Use the Stripe API (not the dashboard) to create a NEW Payment Link with `subscription_data.trial_period_days=14`.

```bash
curl https://api.stripe.com/v1/payment_links \
  -u "sk_test_...": \
  -d "line_items[0][price]=price_1UEWrhFA55fKZHW6HZTiwKbI" \
  -d "line_items[0][quantity]=1" \
  -d "subscription_data[trial_period_days]=14"
```

This gives a new Payment Link with the trial. **Doesn't touch the existing link** (so the existing subscription stays as-is).

#### Option B: Edit existing Payment Link in Dashboard

I cannot confirm if the dashboard UI lets you add `trial_period_days` to an existing Payment Link after creation. **Most likely no** - dashboard's Payment Link editor doesn't show this field.

But the Subscription Editor (Dashboard > Subscriptions > click one > Update) DOES let you add a trial to an existing subscription, but that's per-subscription, not per-link.

### Conclusion: Use Option A (recreate via API)

This is cleaner because:
- The old link stays for Jim's existing $50 customer (don't break what works)
- New link gets the trial built in
- Anyone subscribing via new link gets 14 days free

#### Step-by-step implementation

1. **Get the Stripe secret key** (sk_test_...) from the dashboard
2. **Run the curl command above** with the API key
3. **Get the new Payment Link URL** from the response
4. **Update STRIPE_PAYMENT_LINK in .env** to the new URL
5. **Test** with the test card
6. **Verify** `subscription.status === 'trialing'` in events

We can also automate this from Python using the `stripe` Python library (already installed):

```python
import stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Get the existing price
price = stripe.Price.retrieve('price_1UEWrhFA55fKZHW6HZTiwKbI')

# Create a new Payment Link with trial
payment_link = stripe.PaymentLink.create(
    line_items=[{'price': price.id, 'quantity': 1}],
    subscription_data={'trial_period_days': 14},
)
print(f"New Payment Link: {payment_link.url}")
```

---

## Question 2: How do we set up the recurring subscription?

We already have this. The existing price `$50/mo recurring` IS the recurring subscription setup.

When customer subscribes via Payment Link:
- Stripe creates a Subscription object
- Stripe generates an invoice monthly
- Stripe auto-charges the customer's saved card
- Stripe fires webhooks on every event (payment succeeded, failed, etc.)

**We don't need to change anything for the recurring side.** It's already set up correctly.

### Future: 3 tiers

You said we need 3 tiers. The Stripe model is:

**Option 1: 3 separate Products** (recommended for V1)
- "Card Scout Hobby" - $25/mo
- "Card Scout Pro" - $50/mo
- "Card Scout Elite" - $150/mo

Each is its own Product in Stripe Dashboard with its own Price. Customer chooses via different Payment Links (or a pricing table on your website).

**Option 2: Single Product with multiple Prices**
- One "Card Scout" product
- 3 Prices (Hobby, Pro, Elite)
- Customer picks via Checkout dropdown

**Option 3: Tiered pricing on single price** (volume discount)
- Not what you want - this is for "more cards = lower per-card cost"

### Recommended: Option 1 (3 separate products)

Why:
- Cleanest model
- Each tier has its own features clearly mapped
- Each tier can have its own trial (or not)
- Easy to add/remove tiers later
- Stripe handles the rest

### Setup steps for 3 tiers (when ready)

For each tier:
1. Dashboard > Products > + Add product
2. Name: "Card Scout [Tier]"
3. Description: features
4. Add a price (recurring, monthly)
5. Set amount
6. (Optional) Add trial period (same as before)
7. Save
8. Create Payment Link for this product
9. Repeat for next tier

Then on your dashboard/pricing page, list all 3 Payment Links with "Subscribe" buttons.

---

## Question 3: What tier prices should we use?

This is a business decision, not technical. But here's a framework:

### Suggested tier structure (for Card Scout)

| Tier | Price | Cards | Features |
|---|---|---|---|
| **Hobby** | $25/mo | 3 | Basic alerts, sport/TCG |
| **Pro** | $50/mo | 12 | All cards, custom alerts, priority support |
| **Elite** | $150/mo | unlimited | All Pro features + API access + custom dashboard |

### Pricing considerations

- **Hobby** (~$25): Below $30 = no "I need to justify this" threshold. Easy yes.
- **Pro** (~$50): The sweet spot. Enough features to be valuable, not painful price.
- **Elite** (~$150): Power users. Only ~10% of customers, but 30% of revenue.

This is the **3-tier pricing ladder pattern** - common in SaaS (Linear, Vercel, etc.).

### When to implement 3 tiers

Trigger: when you have 5+ paying customers and at least 1 asks for more features. Currently:
- 1 customer (Jim, beta, free)
- No feature requests yet
- No paying customers

**Recommendation**: Don't build 3 tiers yet. Stick with single $50 tier until validated. You'll know when to add tiers when customers start asking.

---

## Implementation plan (when Jim is ready)

### Tonight (Stage 1.5 - if Jim wants to test trial):

1. Get Stripe secret key from dashboard
2. Add to .env: `STRIPE_SECRET_KEY=sk_test_...`
3. Run the Python script to create a new Payment Link with 14-day trial
4. Update STRIPE_PAYMENT_LINK in .env
5. Test with test card
6. Verify `trialing` status in Stripe dashboard

### Stage 2 (when ready to automate):

1. Add webhook endpoint to dashboard (`/webhook/stripe`)
2. Subscribe to events (6 events listed below)
3. Update sheets_importer to use `tier=trial` immediately, leave Stripe update to webhook
4. Add DB columns: stripe_customer_id, stripe_subscription_id, subscription_status, trial_end_at
5. Deploy dashboard (Hetzner) for production webhooks

### Events to subscribe to (V3 Stage 2):

| Event | When it fires | What we do |
|---|---|---|
| `customer.subscription.created` | Customer subscribes | Save stripe_customer_id, subscription_id |
| `customer.subscription.updated` | Status changes (trial → active) | Update tier: trial→paid, max_cards: 3→12 |
| `customer.subscription.deleted` | Customer cancels | Downgrade tier to canceled, max_cards=0 |
| `customer.subscription.trial_will_end` | 3 days before trial ends | (Optional) Send "trial ending" Discord DM |
| `invoice.payment_succeeded` | Recurring payment succeeded | Log payment, refresh period_end |
| `invoice.payment_failed` | Recurring payment failed | Downgrade tier to past_due, send Discord alert |

---

## Pricing tier business model (for future)

When you're ready to implement 3 tiers, here's a thought experiment:

### Tier 1: Hobby ($25/mo)
- 3 cards max (current trial tier)
- Basic alerts
- Sports + TCG

### Tier 2: Pro ($50/mo) ← CURRENT
- 12 cards max
- All alerts
- Custom webhook per card

### Tier 3: Elite ($150/mo)
- Unlimited cards
- API access
- White-label option
- Custom integrations

This gives clear upgrade path:
- Trial → Hobby (when paying starts)
- Hobby → Pro (when they want more cards)
- Pro → Elite (when they want API/white-label)

---

## Open questions for Jim

1. **Do you want to ship the trial NOW** (Stage 1.5, ~30 min)?
   - Pro: Beta testers get 14 days free
   - Con: Doesn't match "pause for observation" stance

2. **3 tiers: when to add?**
   - Now (parallel to trial setup)
   - Later (after first paying customer validates $50 tier)
   - Never (stick with single tier)

3. **Webhook handler: hosted where?**
   - Add to existing dashboard (Flask on localhost, deploy when ready)
   - Separate microservice
   - Use Stripe's native webhooks UI (no code, just config)

4. **Customer matching: how do we link Stripe customer to our DB customer?**
   - By email (collect in form)
   - By metadata (we set `customer_id` when creating Checkout session)
   - By Discord webhook (we match later)

My recommendation: **ship trial NOW** (test the flow), **3 tiers LATER** (after first paying customer), **webhook on dashboard** (reuse existing), **match by email** (add email field to form).

---

## Reference (docs consulted Sept 15, 2026)

- https://docs.stripe.com/billing/subscriptions/trials
- https://docs.stripe.com/payments/checkout/free-trials
- https://docs.stripe.com/products-prices/pricing-models
- https://docs.stripe.com/payment-links/create

## Test card (sandbox)

```
Card: 4242 4242 4242 4242
Exp: any future date
CVC: any 3 digits
ZIP: any 5 digits
```

## Other test cards (for failure modes)

| Card | Failure mode |
|---|---|
| `4000 0000 0000 0002` | Card declined |
| `4000 0000 0000 9995` | Insufficient funds |
| `4000 0027 6000 3184` | 3D Secure required |
