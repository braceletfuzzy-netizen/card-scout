# Stripe Manual Testing Playbook (Stage 1)

## Purpose
Send beta testers through the Stripe Payment Link flow manually so we can
observe what data Stripe sends us, what events fire, what edge cases appear.

This is the OBSERVATION phase before we automate webhooks.

## What's the same as production

- Same Stripe Payment Link
- Same $50/mo product
- Same trial/cancellation flow

## What's different from production

- Test mode (no real money)
- We don't have webhook endpoint listening (events show up in Stripe dashboard)
- No automated tier upgrade (Jim does it manually in DB)

## When to use this

- Beta tester #2 wants to play with Card Scout
- Want to verify the Stripe flow works end-to-end
- Want to capture webhook payloads for V3 design
- Want to see what Stripe's customer portal looks like

## Step-by-step: sending a tester through

### 1. Tester fills the Google Form first (existing flow)

They go through the standard onboarding:
- Name + Discord webhook + cards
- Submit
- They get imported with tier=trial, 3 cards max
- Bot starts alerting them immediately

### 2. You send them the Stripe payment link

Email/message template:

```
Hey [name],

Card Scout is ready for you. You'll get 3 cards alerted for free.

Want full access (12 cards)? Card Scout Pro is $50/month with a 14-day
free trial. No charge until day 15.

To start your trial: [PASTE STRIPE PAYMENT LINK]

Use this test card info:
  Card: 4242 4242 4242 4242
  Exp: any future date (e.g. 12/30)
  CVC: any 3 digits
  ZIP: any 5 digits

After 14 days, your card gets charged $50/month. Cancel anytime.

Questions? Just ask.

[Jim's name]
```

### 3. Tester goes through Stripe Checkout

They see Stripe's hosted checkout page:
- Enter test card
- Confirm subscription
- See "Trial: 14 days" message

### 4. Stripe fires webhook events (you watch these)

Go to: https://dashboard.stripe.com/test/events

You'll see events like:
- `checkout.session.completed` (when they submit the form)
- `customer.subscription.created` (when subscription is created)
- `customer.subscription.trial_will_end` (3 days before trial ends)
- `invoice.created` (when trial ends, generates first invoice)
- `invoice.payment_succeeded` (when card is charged successfully)

For each event, capture:
- Full payload (JSON)
- When it fired
- What changed

### 5. After 14 days, Stripe auto-charges

The test card `4242 4242 4242 4242` will be charged $50.

**For Stage 1**: nothing happens in our DB. Jim watches the Stripe dashboard
to see the charge succeed.

If you want to test the post-trial flow, Jim can manually upgrade the
customer in DB:
```sql
UPDATE customers SET tier='paid', max_cards=12 WHERE customer_id='tester_jon_xxx';
```

### 6. (Optional) Test cancellation

Stripe has a customer portal where the tester can cancel:
- Customer goes to Stripe's portal
- Clicks "Cancel subscription"
- Stripe fires `customer.subscription.updated` with status=canceled

Watch the event in Stripe dashboard.

## What to capture for V3 design

For each webhook event you see, note:

| Field | Value |
|---|---|
| Event type | `customer.subscription.created` |
| When | 2026-09-15 14:32:01 UTC |
| Customer ID | `cus_xxxxx` |
| Subscription ID | `sub_xxxxx` |
| Status | `trialing` |
| Trial end | 2026-09-29 14:32:01 UTC |
| Metadata | (any custom fields you set) |
| Default payment method | `pm_xxxxx` |

Save these as you observe them. When Stage 2 starts, this is what we'll
automate.

## Failure modes to test

1. **Declined card** — use `4000 0000 0000 0002`
2. **Insufficient funds** — use `4000 0000 0000 9995`
3. **3D Secure required** — use `4000 0027 6000 3184`
4. **Expired card** — use any past date

Test each to see what events fire and how to handle them.

## Stripe dashboard links

- Sandbox events: https://dashboard.stripe.com/test/events
- Sandbox customers: https://dashboard.stripe.com/test/customers
- Sandbox subscriptions: https://dashboard.stripe.com/test/subscriptions
- Sandbox product: https://dashboard.stripe.com/test/products
- API keys: https://dashboard.stripe.com/test/apikeys

## Current Payment Links

| Link | Purpose | Trial | URL |
|---|---|---|---|
| OLD (no trial) | Reference / first Jim test | ❌ None | `https://buy.stripe.com/test_8x25kD0ul7aJcGx91o9Zm00` |
| **NEW (with trial)** | **Use this for beta testers** | ✅ **14 days** | **`https://buy.stripe.com/test_aFabJ1cd30MlfSJa5s9Zm01`** |

Created Sept 15, 2026 via Stripe API with `subscription_data.trial_period_days=14`.

## Time estimate

- Setup: 5 minutes (you have the link already)
- Each tester through the flow: 3 minutes
- Each webhook event observation: 1 minute
- Total Stage 1 work: ~2 hours of observation over 2-3 weeks

## When Stage 1 is "done"

You've observed enough to know:
- What webhook events fire and when
- What data each event contains
- What edge cases exist
- What the customer experience feels like

Then you start Stage 2 (automation).
