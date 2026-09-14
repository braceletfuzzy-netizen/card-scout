# Apify Compensation Request — Email Template

**Send to**: support@apify.com
**Or**: via in-app chat on Starter plan (https://console.apify.com)
**Send by**: 2026-09-21 (15-day window for Sep 6 charge)

---

## Subject

Compensation request — 2 zero-output runs from etsy-listings-scraper actor

---

## Body

Hi Apify Support,

I'm requesting compensation for two failed runs of a third-party Actor
(etsy-listings-scraper, Actor ID `2C8cXecL4Dcti0Xte`) that I rented through
the Apify Store. Both runs completed successfully according to Apify's status
indicator but produced **zero data items** — making them functionally useless
and leaving me with no way to recover the spent credits.

### Account

- Email: jonathangeorge13@gmail.com
- Username: fuzzy_bracelet
- Plan: Starter
- Account ID: mvlzb3QsgwQKEtOjl

### Runs in question

**Run 1**
- Run ID: `tdCrBLs8bLShMzi34`
- Started: 2026-08-30 12:56:22 UTC
- Cost: $5.58
- Status: SUCCEEDED
- Items returned: 0

**Run 2**
- Run ID: `BzHLebZaGRdyElb5F`
- Started: 2026-09-06 12:56:04 UTC
- Cost: $54.12
- Status: SUCCEEDED
- Items returned: 0

**Total disputed: $59.71**

### Why compensation is warranted

Per Section 7.9 of your General Terms, I am writing within the 15-day window
to dispute these charges. The runs are unambiguously non-functional:

1. Both runs returned 0 items to the dataset
2. The $54.12 run consumed substantial compute units without producing a single result
3. The actor's "SUCCEEDED" status indicates Apify charged me as if the job
   completed successfully — but the job produced no usable output
4. This is a clear failure of the pay-per-event model: I paid for events
   (results) and received none

I understand per Apify's compensation policy that compensation is issued as
credits rather than a monetary refund. I'm requesting credit compensation for
the full $59.71.

### What I've already done

- Verified the runs via the Apify API (both show SUCCEEDED status, both
  have datasetItemCount = 0)
- Stopped using the actor to prevent further charges
- Built my own replacement actors (no longer relying on third-party tooling)

### What I'd like

- Credit compensation for the full $59.71
- Confirmation that compensation was processed and visible in my account
- (Optional) feedback on whether this actor should remain in the Apify Store
  given the failure pattern

Thank you for your time. Let me know if you need any additional information.

Best regards,
[Jonathan]

---

## Notes for sending

- Replace `[Jonathan]` with your actual name
- Don't edit the run IDs or amounts — those are precise
- Send via in-app chat for faster response (if on Starter plan)
- File before 2026-09-21 to stay within Apify's 15-day window
