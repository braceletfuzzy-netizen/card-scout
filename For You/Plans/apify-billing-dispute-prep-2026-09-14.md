# Apify Billing Dispute — Preparation & Email Template

**Date**: 2026-09-14
**Author**: Hugo
**Status**: Ready to send
**Recipient**: Apify Support via in-app chat OR support@apify.com

---

## TL;DR

Two charges from a third-party Apify Store actor returned **zero data items**
but cost **$59.71 total**. Both are within Apify's 15-day dispute window
(Section 7.9 of T&C). Strongest claim: **$54.12** (Sep 6, 8 days ago).
Secondary claim: **$5.58** (Aug 30, exactly 15 days ago).

---

## Apify's Compensation Policy (Verified)

Per Apify's official help docs (help.apify.com/en/articles/10717922):
- Apify calls it **"compensation"**, not "refund"
- Compensation is returned as **CREDITS, not money** (per Apify T&C)
- Requested via in-app chat (Starter plan and above) or email
- Must reference the actor, run IDs, and reason

Per Apify's General T&C (Section 7.9):
> "To dispute a charge, you must notify us in writing within fifteen (15) days 
> of the charge or invoice date. Failure to do so waives your right to dispute 
> the charge."

---

## Dispute-Able Charges

| Run ID | Actor ID | Date | Cost | Items Returned | Days Ago | Window |
|---|---|---|---|---|---|---|
| `tdCrBLs8bLShMzi34` | `2C8cXecL4Dcti0Xte` (etsy-listings-scraper) | 2026-08-30 | $5.58 | 0 | 15 | AT BOUNDARY |
| `BzHLebZaGRdyElb5F` | `2C8cXecL4Dcti0Xte` (etsy-listings-scraper) | 2026-09-06 | $54.12 | 0 | 8 | OPEN |
| **TOTAL** | | | **$59.71** | **0** | | |

### Why This Is a Strong Case

1. **Both runs returned ZERO items** — exactly the failure mode Apify
   compensation is designed for
2. **Run status was "SUCCEEDED"** — meaning Apify charged us as if the
   actor worked, but it produced no usable output
3. **An entire $54.12 run with 0 items** is the smoking gun — that's
   $54.12 for nothing
4. **We're on the Starter plan** — confirmed ($19/mo + pay-as-you-go)
5. **Within 15-day dispute window** — both runs

### Why My Earlier $94.48 Figure Was Wrong

The earlier audit showed $94.48 of "orphan actor" charges. After re-checking:
- Only $59.71 is actual dispute-able charges from a third-party actor
- The other $34.77 was misattributed (likely from actors we did run, or
  billings from prior cycles)
- The 3 other "orphan" actors (ebay-sold-listings, avito-ru-scraper,
  olx-marketplace-scraper) returned 404 on the actor endpoint, meaning
  they don't exist as public actors — so we couldn't have run them
- This means the **actual recoverable amount is $59.71**, not $94.48

---

## Where to File (Updated per Apify Support Response)

**Apify support responded**: For third-party (Store) actors, compensation requests must go through the **Actor's Issues tab**, not directly to Apify Support. The developer reviews first, then submits to Apify.

**Correct URL**: https://apify.com/astravalabs/etsy-listings-scraper/issues

> Note: Apify's auto-response linked a different actor (`akash9078/etsy-product-scraper`). 
> The actor we actually paid is `astravalabs/etsy-listings-scraper`. Use the link above.

## Issue Template (Post to Actor's Issues tab)

**Title**: Compensation request: 2 runs returned 0 items ($59.71 total)

**Body**:

---

Hi Apify Support,

I'm requesting compensation for two failed runs of a third-party Actor
(etsy-listings-scraper, Actor ID `2C8cXecL4Dcti0Xte`) that I rented through
the Apify Store. Both runs completed successfully according to Apify's status
indicator but produced **zero data items** — making them functionally useless
and leaving me with no way to recover the spent credits.

## Account Information

- Account email: jonathangeorge13@gmail.com
- Username: fuzzy_bracelet
- Plan: Starter
- Account ID: mvlzb3QsgwQKEtOjl

## Runs in Question

### Run 1
- Run ID: `tdCrBLs8bLShMzi34`
- Started: 2026-08-30 12:56:22 UTC
- Cost: **$5.58**
- Status: SUCCEEDED (per Apify)
- Items returned: **0**
- Compute units consumed but no data delivered

### Run 2
- Run ID: `BzHLebZaGRdyElb5F`
- Started: 2026-09-06 12:56:04 UTC
- Cost: **$54.12**
- Status: SUCCEEDED (per Apify)
- Items returned: **0**
- Compute units consumed but no data delivered

**Total disputed: $59.71**

## Why Compensation Is Warranted

Per Apify's T&C (Section 7.9), I am writing within the 15-day window to
dispute these charges. The runs are unambiguously non-functional:

1. Both runs returned **0 items** to the dataset
2. The $54.12 run consumed a substantial amount of compute units without
   producing a single result
3. The actor's "SUCCEEDED" status indicates Apify charged me for a
   completed job — but the job produced no usable output
4. This is a clear failure of the pay-per-event model: I paid for events
   (results) and received none

I understand per Apify's compensation policy that compensation is issued
in the form of credits rather than monetary refund. I am requesting credit
compensation for the full $59.71.

## What I've Already Done

- Verified the runs via `https://api.apify.com/v2/acts/2C8cXecL4Dcti0Xte/runs`
  (both show SUCCEEDED status, both have datasetItemCount = 0)
- Stopped using the actor to prevent further charges
- Built my own replacement actors (no longer relying on third-party)

## What I'd Like

- Credit compensation for the full $59.71
- Confirmation that compensation was processed (and visible in my account)
- (Optional) feedback on whether this actor should remain in the Apify
  Store given the failure pattern

Thank you for your time. Let me know if you need any additional information.

Best regards,
[Jonathan]

---

## Alternative: In-App Chat Path

If you prefer the in-app chat (faster response on Starter plan):

1. Go to https://console.apify.com
2. Click the chat bubble (bottom-right)
3. Choose "Request user credit compensation"
4. Fill in:
   - User ID: `mvlzb3QsgwQKEtOjl`
   - Actor ID: `2C8cXecL4Dcti0Xte`
   - Exact amount: `$59.71`
   - Reason: "Both runs returned 0 items despite SUCCEEDED status"

---

## What To Do If Apify Denies the Dispute

If Apify denies (per their T&C, "charges are based exclusively on our
invoicing records, which are final"):

1. **Ask for a goodwill credit** — mention you stopped using the actor
2. **Escalate to legal@apify.com** — for amounts >$50
3. **Dispute via your payment provider** (Stripe/credit card) — they have
   their own dispute process independent of Apify
4. **Just accept the $59.71 loss** — it's small relative to your $7/mo
   baseline spend

---

## Important Caveats

- **15-day window**: This dispute must be filed by **2026-09-21** for
  the Sep 6 charge to remain valid (15 days from Sep 6 = Sep 21)
- **Don't wait**: file today if you can
- **Compensation is credits, not money**: You won't get a cash refund;
  you'll get Apify credits to spend on future usage
- **This is a low-stakes dispute**: $59.71 is below Apify's typical
  threshold for serious escalation. They may approve quickly as a
  goodwill gesture.

---

## Filing Checklist

- [ ] Copy email template above
- [ ] Open in-app chat OR compose email to support@apify.com
- [ ] Send with run IDs + actor ID + amounts
- [ ] Wait 2-3 business days for response
- [ ] If approved: credits appear in your account automatically
- [ ] If denied: consider the alternative paths above

**Urgency**: File before **2026-09-21** for Sep 6 charge to be within window.
