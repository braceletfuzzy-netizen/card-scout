# V2 Rollout: Stripe Sandbox Simulation Strategy

## Status
**DRAFTED Sept 15, 2026.** Jim's directive for when V2 (Stripe automation) is ready to roll out.

## What Jim said (verbatim)

> "I am going to send Beta #2 the form. When we roll V2 out I will let the
> guys know, we will reset and keep stripe in sandbox to simulate a payment
> -> so the system assigns customer ID and lets us know when a trial has
> been created, so we can check the customer flow etc."

## Interpretation

When V2 (webhook-driven tier automation) is shipped, Jim wants to:
1. Notify beta testers that V2 is live
2. **RESET** (clear out test data, start fresh)
3. Keep Stripe in **SANDBOX** mode (no real money)
4. Simulate payments through Stripe sandbox (still uses real Payment Link flow)
5. The system should automatically:
   - Assign customer ID when Stripe webhook fires
   - Detect when a trial has been created
   - Let us monitor the customer flow end-to-end

## What this means for V2 design

### Required capabilities (when V2 ships):

1. **Customer linking via webhook**:
   - When customer.subscription.created webhook fires
   - System matches to our customer (need matching strategy)
   - Saves `stripe_customer_id`, `stripe_subscription_id` to our DB

2. **Trial detection**:
   - System reads `subscription.status` from webhook payload
   - Sets `tier='trial'`, `trial_end_at=...`, `subscription_status='trialing'`

3. **Conversion detection**:
   - When customer.subscription.updated webhook fires with status='active'
   - System updates `tier='paid'`, `max_cards=12`

4. **Reset capability**:
   - One command to wipe all beta customer data
   - Reset Stripe sandbox state (only Jim can do this in Stripe dashboard)
   - Re-run V2 from scratch

5. **Monitoring dashboard** (lightweight):
   - View all customers + their tier + Stripe status
   - See webhook events processed
   - Identify failures (unmatched events, errors)

### What V2 needs to build

| Component | Effort | When |
|---|---|---|
| Webhook endpoint `/webhook/stripe` | 2 hours | V2 start |
| Signature verification | 30 min | V2 start |
| Customer matching strategy | 1 hour | V2 start |
| DB columns (stripe_customer_id, etc.) | 30 min | V2 start |
| DB migration script | 30 min | V2 start |
| Tier update logic | 2 hours | V2 mid |
| Monitoring endpoint or view | 1 hour | V2 end |
| Reset command | 30 min | V2 end |
| Beta tester announcement template | 15 min | V2 ship |

**Total V2 effort: ~8 hours** (was 6 in earlier estimate, +2 for monitoring + reset)

## Customer matching strategy (decision needed for V2)

How does our webhook handler find the right customer when Stripe fires an event?

| Strategy | How it works | Pros | Cons |
|---|---|---|---|
| **By email** | Customer email in Stripe matches email in our DB | Simple, works | Need to add email field to form |
| **By metadata** | We set `client_reference_id` or `metadata.customer_id` when creating Checkout session | Most reliable | Need to use Checkout Sessions, not raw Payment Links |
| **By webhook secret + manual link** | Customer manually connects their webhook to their customer record | Maximum control | Awkward UX, high friction |

**Recommendation**: By email. Requires V4 work to add email to the form, but it's the simplest and most robust.

For now (V2 with existing form), we can use the **by webhook lookup** approach as a fallback — match by the Discord webhook URL the customer used to sign up (if they put the same email when paying in Stripe, we match). If no match, queue the event for manual review.

## Reset command (V2 needs this)

When Jim wants to start fresh:

```bash
# 1. Wipe our DB customer data (keep schema)
python scripts/reset_beta_state.py

# 2. Manually clear Stripe sandbox (Jim does this in dashboard):
#    - Go to https://dashboard.stripe.com/test/customers
#    - Delete each test customer (or bulk delete via API)
#    - Go to https://dashboard.stripe.com/test/subscriptions
#    - Cancel/delete each test subscription

# 3. Reset Google Sheet "Imported?" column (manually or via script)

# 4. Re-run V2 from clean state
```

## Beta tester announcement (V2 ship template)

```
Hey [name],

Big update for Card Scout — V2 is live!

What changed:
- Stripe payments are now automated (still in test mode)
- Trial periods are auto-detected
- When you subscribe, your account auto-upgrades to Pro
- No more waiting for manual upgrades

How to test:
1. Use the existing form to sign up (if you haven't already)
2. Click the Stripe link we sent
3. Use test card 4242 4242 4242 4242
4. You should see your trial activated immediately
5. Try adding more than 3 cards — should work in trial mode

When you're done testing, please share:
- What worked
- What was confusing
- What you'd change

Thanks for being a beta tester!

[Jim]
```

## When V2 ships

1. ✅ Build V2 components (8 hours total)
2. ✅ Reset beta state (script + manual Stripe cleanup)
3. ✅ Send beta tester announcement
4. ✅ Monitor webhook events in Stripe dashboard
5. ✅ Verify customer flow end-to-end:
   - Form submit → trial tier
   - Stripe link click → webhook fires
   - Customer ID assigned
   - Trial detected
   - 14 days pass (or simulated via Stripe clock)
   - Trial converts → paid tier
6. ✅ Collect feedback from beta testers
7. ✅ Iterate based on feedback

## Open questions for V2 design

1. **Email field on form**: Add now (V4 work) or wait?
2. **Customer matching**: Which strategy?
3. **Monitoring UI**: New dashboard page or just SQL queries?
4. **Reset frequency**: On-demand only or scheduled?
5. **Real money**: When to switch to Stripe Live mode?
   - Recommended: After 5+ successful beta conversions in sandbox
   - NOT before

## Related docs

- `For You/Plans/stripe-setup-guide-2026-09-15.md` - Stripe API research
- `For You/Plans/v3-stripe-integration-2026-09-15.md` - V3 roadmap (current)
- `For You/Plans/stripe-manual-testing-playbook-2026-09-15.md` - Manual testing playbook
- `For You/Plans/stripe-sandbox-simulation-2026-09-15.md` - This file
