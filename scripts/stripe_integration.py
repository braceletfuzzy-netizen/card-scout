"""
Stripe integration for Card Scout — Stage 1 stub (sandbox testing).

WHAT THIS IS (Sept 15, 2026, current state):
- Module exists but NOT YET WIRED INTO BOT FLOW
- Has `validate_confirmation()` for manual "paste your receipt #" flow
- Has `get_payment_url()` returning the static Stripe Payment Link
- NOT what we'll actually use in production

WHAT WE ACTUALLY NEED (decided Sept 15 evening):

The "paste confirmation #" approach is the WRONG flow for our use case. What
we really want:

1. Customer fills Google Form → customer record created with tier='trial'
2. Bot immediately starts alerting them (3 cards max, trial tier)
3. Customer separately clicks Stripe Payment Link → 14-day free trial
4. After 14 days, Stripe auto-charges their card
5. Stripe webhook fires to our endpoint → we update customer.tier='paid'
6. Customer now gets full alerts (12 cards max)

Why this is right:
- Friction-free for testers (no card needed to try)
- Stripe handles the actual billing (we don't manage cards)
- Webhook auto-updates tier (no manual reconciliation)
- Standard SaaS trial pattern

WHAT WE STILL NEED (Stage 2):
- Add Stripe Customer column to Customer model: stripe_customer_id,
  stripe_subscription_id, subscription_status, trial_end_at
- Build Stripe webhook handler: /webhook/stripe endpoint in dashboard
- Subscribe to events: customer.subscription.created,
  customer.subscription.updated, customer.subscription.deleted,
  invoice.payment_succeeded, invoice.payment_failed
- Update sheets_importer to NOT touch Stripe (handled by webhook)
- Add Stripe price ID to env: STRIPE_PRICE_ID=price_xxx
- Add webhook signing secret: STRIPE_WEBHOOK_SECRET=whsec_xxx

WHY WE PAUSED (Jim's input, Sept 15):
"beta guys implement the sandbox process so we can see how everything flows
into us so we can make the appropriate changes needed and set up our process"

Translation: don't automate yet. Let your beta testers go through the
manual Stripe Checkout flow with test cards so we can OBSERVE what data
Stripe sends, what events fire, what edge cases appear. THEN we automate
based on what we learned.

This stub is here so we can later add validation helpers when needed.

REFERENCE: For You/Plans/v3-stripe-integration-2026-09-15.md
"""

import os
import re
from typing import Optional, Tuple

# Load .env for STRIPE_* keys
try:
    from dotenv import load_dotenv
    from pathlib import Path
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass


STRIPE_PAYMENT_LINK = os.getenv('STRIPE_PAYMENT_LINK', 'https://buy.stripe.com/test_8x25kD0ul7aJcGx91o9Zm00')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', None)


def get_payment_url() -> str:
    """Return the payment link to send to a customer.

    For Stage 1 (manual testing), this is the static payment link.
    For Stage 2 (V3 automation), this will generate per-customer Checkout
    sessions with metadata.

    Returns:
        URL string (e.g. 'https://buy.stripe.com/test_...')
    """
    if not STRIPE_PAYMENT_LINK:
        raise ValueError(
            "STRIPE_PAYMENT_LINK not set in .env. "
            "Add STRIPE_PAYMENT_LINK=https://buy.stripe.com/test_... to card-scout/.env"
        )
    return STRIPE_PAYMENT_LINK


def _extract_charge_or_session_id(confirmation: str) -> Optional[str]:
    """Extract a charge ID or session ID from a Stripe receipt/confirmation #.

    Helper for manual validation flow (Stage 1 testing only).
    """
    if not confirmation:
        return None

    s = confirmation.strip()

    if 'stripe.com' in s:
        s = s.rstrip('/').split('/')[-1]

    s = re.sub(r'^[A-Za-z]+:\s*', '', s)

    m = re.match(r'^(ch|cs|pi|in|seti)(?:_test)?_[A-Za-z0-9_]+$', s)
    if m:
        return s

    return None


def validate_confirmation(confirmation: str) -> Tuple[bool, str]:
    """Validate a Stripe confirmation # (Stage 1 manual testing only).

    NOT IN USE — kept as helper for when beta testers manually paste
    confirmation #s during sandbox testing.

    Returns:
        (valid: bool, reason: str)
    """
    if not confirmation:
        return False, "Empty confirmation #"

    stripe_id = _extract_charge_or_session_id(confirmation)
    if not stripe_id:
        return False, f"Doesn't look like a Stripe ID: '{confirmation[:60]}'"

    if not STRIPE_SECRET_KEY:
        return True, "Format OK (no STRIPE_SECRET_KEY, skipping API validation)"

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY

        try:
            if stripe_id.startswith('ch_'):
                obj = stripe.Charge.retrieve(stripe_id)
                if not obj.paid:
                    return False, f"Charge {stripe_id} exists but not paid"
                amount_usd = obj.amount / 100
            elif stripe_id.startswith('cs_'):
                obj = stripe.checkout.Session.retrieve(stripe_id)
                if obj.payment_status != 'paid':
                    return False, f"Session {stripe_id} not paid"
                amount_usd = obj.amount_total / 100
            elif stripe_id.startswith('pi_'):
                obj = stripe.PaymentIntent.retrieve(stripe_id)
                if obj.status != 'succeeded':
                    return False, f"PaymentIntent {stripe_id} not succeeded"
                amount_usd = obj.amount / 100
            else:
                return False, f"Unhandled Stripe ID type: {stripe_id[:3]}"
        except Exception as e:
            return False, f"Stripe API error: {type(e).__name__}: {str(e)[:80]}"

        if amount_usd < 50:
            return False, f"Charge amount ${amount_usd:.2f} below $50 threshold"

        return True, f"Validated: {stripe_id} for ${amount_usd:.2f}"

    except ImportError:
        return True, "Format OK (stripe package not installed)"


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Stripe Integration — self-test (no API key, format-only)")
    print("=" * 70)

    # Test 1: get_payment_url
    print("\n1. get_payment_url():")
    try:
        url = get_payment_url()
        print(f"   [OK] Payment URL: {url}")
    except ValueError as e:
        print(f"   [FAIL] {e}")

    # Test 2: format extraction
    print("\n2. _extract_charge_or_session_id():")
    test_inputs = [
        'ch_3MwkLx2eZvKYlo2C1aBCDEFG',
        'cs_test_a1b2c3d4e5f6g7h8i9j0',
        'pi_1ABC2defGHI3jkl4MNO5pqr6',
        'https://dashboard.stripe.com/test/payments/ch_3MwkLx2eZvKYlo2C1aBCDEFG',
        'Confirmation: ch_3MwkLx2eZvKYlo2C1aBCDEFG',
        'junk-string',
        '',
    ]
    for inp in test_inputs:
        result = _extract_charge_or_session_id(inp)
        print(f"   '{inp[:50]}' → '{result}'")

    # Test 3: validate_confirmation (format only, no API key)
    print("\n3. validate_confirmation() (no API key, format-only):")
    test_confirmations = [
        ('ch_3MwkLx2eZvKYlo2C1aBCDEFG', 'valid format'),
        ('junk-string', 'should fail format check'),
        ('', 'should fail empty check'),
    ]
    for conf, expected in test_confirmations:
        valid, reason = validate_confirmation(conf)
        print(f"   '{conf[:40]}' → valid={valid}, reason='{reason}' ({expected})")

    print("\n" + "=" * 70)
    print("Note: With STRIPE_SECRET_KEY in .env, also verifies against Stripe API")
    print("=" * 70)
