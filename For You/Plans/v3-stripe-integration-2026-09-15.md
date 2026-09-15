# V3 Roadmap: Stripe Integration

## Status
**STAGE 1 — PAUSED for manual sandbox testing** (Sept 15, 2026 evening)

Jim's directive: *"beta guys implement the sandbox process so we can see
how everything flows into us so we can make the appropriate changes needed
and set up our process... but I don't want the stripe card slowing down
them playing with Card Scout."*

**No code changes for now.** Beta testers will use the existing Stripe
Payment Link manually so we can OBSERVE the flow before automating.

## The Correct Flow (Decided Sept 15, 2026)

### Customer journey (V3, post-stage-2)

```
1. Customer fills Google Form
   ↓
2. Bot immediately starts alerting (tier=trial, 3 cards max)
   ↓
3. Customer separately clicks Stripe Payment Link (no card upfront)
   ↓
4. Stripe Checkout: collect card info
   ↓
5. Stripe creates subscription in 'trialing' state (14-day free trial)
   ↓
6. Bot receives webhook → tier=trial (already is), track subscription
   ↓
7. 14 days pass...
   ↓
8. Stripe auto-charges card
   ↓
9. Subscription status: 'trialing' → 'active'
   ↓
10. Webhook fires: customer.subscription.updated
   ↓
11. Bot updates tier=paid, max_cards=12
```

### Why this flow is right

- **Friction-free for testers**: no card needed to try Card Scout
- **Stripe handles the billing**: we don't manage card data
- **Webhook-driven**: no manual tier upgrades needed
- **Standard SaaS pattern**: matches industry best practice
- **Trial period is natural**: customer gets 14 days to evaluate

### What we DON'T do

- ❌ Require card upfront (loses testers)
- ❌ Customer pastes confirmation # into form (manual friction)
- ❌ We manually verify charges (operational burden)
- ❌ Direct API charges (loses Stripe's safety net)

## Stage 1: Manual Sandbox Testing (NOW, no code changes)

**The plan**: Send beta testers to the Stripe Payment Link directly.
Let them go through the flow with test cards. We OBSERVE what happens.

### What we observe

1. **Stripe sends receipt emails** — capture example receipts to see format
2. **Stripe sends webhook events** — even without our endpoint listening,
   they show up in Stripe dashboard's "Events" tab
3. **Subscription lifecycle** — when does status change from trialing → active?
4. **Failed payment handling** — what happens when test card expires?
5. **Customer portal** — what does Stripe's hosted portal look like?

### What we capture for each event

For each webhook event Stripe fires, we record:
- Event type (`customer.subscription.created`, etc.)
- Full payload (JSON)
- When it fired (timestamp)
- What changed in the subscription object

This data feeds our Stage 2 design.

### Test card to use

```
Card number: 4242 4242 4242 4242
Expiry: any future date (e.g. 12/30)
CVC: any 3 digits (e.g. 123)
ZIP: any 5 digits
```

### Stripe dashboard to watch

- https://dashboard.stripe.com/test/events (Sandbox mode)
- https://dashboard.stripe.com/test/customers
- https://dashboard.stripe.com/test/subscriptions

## Stage 2: Automation (WHEN ready, ~6 hours)

When we've observed enough flow from Stage 1 to know what we're automating.

### Schema changes

```sql
-- Add columns to customers table
ALTER TABLE customers ADD COLUMN stripe_customer_id TEXT;
ALTER TABLE customers ADD COLUMN stripe_subscription_id TEXT;
ALTER TABLE customers ADD COLUMN subscription_status TEXT;
ALTER TABLE customers ADD COLUMN trial_end_at TIMESTAMP;
ALTER TABLE customers ADD COLUMN subscription_period_end TIMESTAMP;

-- Create subscription_events table for audit trail
CREATE TABLE subscription_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    stripe_event_id TEXT UNIQUE NOT NULL,
    event_type TEXT NOT NULL,
    event_payload TEXT,  -- JSON blob
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

### Webhook handler

New file: `dashboard/stripe_webhook.py` (or part of `dashboard/app.py`)

```python
@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400

    # Idempotency: check if event_id already processed
    existing = session.query(SubscriptionEvent).filter_by(
        stripe_event_id=event.id
    ).first()
    if existing:
        return jsonify({'status': 'already processed'}), 200

    # Log the event
    log_subscription_event(event)

    # Handle by event type
    if event.type == 'customer.subscription.created':
        handle_subscription_created(event.data.object)
    elif event.type == 'customer.subscription.updated':
        handle_subscription_updated(event.data.object)
    elif event.type == 'customer.subscription.deleted':
        handle_subscription_deleted(event.data.object)
    elif event.type == 'invoice.payment_succeeded':
        handle_payment_succeeded(event.data.object)
    elif event.type == 'invoice.payment_failed':
        handle_payment_failed(event.data.object)

    return jsonify({'status': 'ok'}), 200


def handle_subscription_updated(subscription):
    """Called when subscription status changes (trial → active, etc.)"""
    stripe_customer_id = subscription.customer
    status = subscription.status  # 'active', 'past_due', 'canceled', etc.

    customer = session.query(Customer).filter_by(
        stripe_customer_id=stripe_customer_id
    ).first()
    if not customer:
        # New customer from Stripe, not yet in our DB
        # Wait for them to fill the form first
        return

    customer.subscription_status = status

    if status == 'active':
        customer.tier = 'paid'
        customer.max_cards = 12
    elif status in ('past_due', 'unpaid'):
        # Downgrade but don't kick out immediately (grace period)
        customer.tier = 'trial'
        customer.max_cards = 3
    elif status == 'canceled':
        customer.tier = 'canceled'
        customer.max_cards = 0
        customer.subscription_status = 'canceled'

    session.commit()
```

### Sheets importer changes

```python
def import_row(row_info, dry_run=True):
    # ... existing logic ...

    # DON'T touch Stripe here. Webhook handles it.
    # Customer created with tier='trial' immediately.

    tier = 'trial'
    subscription_status = 'pending'
    max_cards = 3

    customer = Customer(
        # ... existing fields ...
        tier=tier,
        subscription_status=subscription_status,
        max_cards=max_cards,
    )

    # Add stripe_customer_id later via webhook matching
    # Use email to match (but we don't collect email yet — V4 work)
```

### Env vars needed

```
STRIPE_SECRET_KEY=sk_test_...  # Sandbox
STRIPE_WEBHOOK_SECRET=whsec_...  # From webhook endpoint creation
STRIPE_PRICE_ID=price_...  # The $50/mo product
STRIPE_PAYMENT_LINK=https://buy.stripe.com/test_...  # Already have this
```

### Local webhook testing (before deploy)

```bash
# Forward Stripe events to local server
stripe listen --forward-to http://localhost:5000/webhook/stripe

# Trigger test events
stripe trigger customer.subscription.created
stripe trigger customer.subscription.updated
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed
```

## Stage 3: Production (after Stage 2 validated)

- Switch Stripe from test mode to live mode
- Update Price to actual $50/mo (or whatever final pricing)
- Update webhook endpoint URL to Hetzner-hosted dashboard
- Real customer payments start flowing
- Bot tiers auto-update from webhooks

## What's in the codebase NOW (Sept 15, 2026)

| File | Status | Purpose |
|---|---|---|
| `scripts/stripe_integration.py` | Stage 1 stub | `get_payment_url()` + `validate_confirmation()` — kept for reference, NOT used in flow |
| `scripts/sheets_importer.py` | V2 only | Imports customer with tier='trial' regardless of Stripe |
| Bot | Not changed | Alerts customer regardless of tier (uses max_cards from DB) |

## What beta testers do TODAY

1. Fill Google Form → get tier=trial, 3 cards max, alerts start
2. Click the Stripe Payment Link Jim sends them (separately)
3. Enter test card `4242 4242 4242 4242`
4. Get 14-day free trial
5. After 14 days, Stripe auto-charges
6. **For now: nothing happens in our DB** (we're observing, not automating)

Jim manually upgrades tier to 'paid' in DB if he wants to test the post-trial flow.

## Decisions captured

- **No card upfront** (14-day trial is the standard pattern)
- **Stripe handles billing** (we just observe webhook events)
- **Manual tier upgrade for now** (Jim runs SQL when he wants to test paid flow)
- **Observe first, automate later** (avoid premature automation)

## Reference

- Stripe trials: https://docs.stripe.com/payments/checkout/free-trials
- Subscription lifecycle: https://docs.stripe.com/billing/subscriptions/overview
- Webhook events: https://docs.stripe.com/api/events/types
- Trial-period conversion: https://operatoriq.io/blog/stripe-trial-periods

## Files to create (Stage 2)

- `dashboard/stripe_webhook.py` (or merge into app.py)
- `scripts/migrate_add_stripe_columns.py` (DB migration)
- `scripts/check_subscription_status.py` (manual verification)
