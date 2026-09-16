# Card Hedge — Pricing Concern (Sept 16)

## Time
Sept 16, 2026 ~7:50 AM (CDT)

## Status
**DRAFTED.** Founder's pricing concern captured. Integration on HOLD.

## Founder's directive (verbatim)

> "I like A, but with integration our pricing targets were forced to
> move. I had been doing the math and those pricing points make more
> sense due to the cost/card/month issues that I was coming up with in
> offline calculations. We will need to also have a discussion on
> pricing and cost metrics once we solve this problem that we are
> currently working on"

## What this means

### Decision: HYBRID (Option A)
- Get Card Hedge API key
- Integrate spec_id discovery
- Solve PSA pop blocker for the 7 missing Jim cards

### BUT: pricing needs to change

The founder had been doing **offline math** that surfaced cost/card/month
issues. The previously-suggested tiers (Hobby $25/3, Pro $50/12, Elite
$150/unlimited) may no longer match the real economics.

## What changed (the math)

Previously (Apify-only, $0.05/card/month):
- Hobby 3 cards: $0.15 cost / $25 revenue = 99.4% margin
- Pro 12 cards: $0.60 cost / $50 revenue = 98.8% margin
- Elite 12 cards: $0.60 cost / $150 revenue = 99.6% margin

With Card Hedge hybrid ($0.16/card/month):
- Hobby 3 cards: $0.48 cost / $25 revenue = 98.1% margin
- Pro 12 cards: $1.92 cost / $50 revenue = 96.2% margin
- Elite 12 cards: $1.92 cost / $150 revenue = 98.7% margin

Margins still strong, but the founder's offline math revealed other
issues. Without seeing the full offline math, I can only capture
**that** it raised concerns, not **what** they are.

## Possible pricing implications

These are guesses based on common SaaS economics — founder needs to
confirm which apply:

1. **Floor price per card**: minimum $/card to maintain healthy margin
2. **Tier restructuring**: maybe Hobby/Pro/Elite should be replaced
3. **Volume discounts**: cheaper per-card at higher tiers (economies of scale)
4. **Setup fees**: cover one-time Card Hedge spec_id discovery cost
5. **Feature gating**: pop data behind higher tier

## Action items

### NOW (this morning)

- [x] Capture this concern in a doc (this file)
- [x] Hold Card Hedge integration until pricing discussed
- [ ] Continue manual PSA URL hunt (no vendor lock-in needed yet)
- [ ] Founder to share offline pricing math (or run the math here)

### LATER (after current task)

1. Founder shares pricing math
2. We reconcile it with the Card Hedge cost model
3. Decide if HYBRID is still right, or pivot to a different cost structure
4. Once pricing is settled, integrate Card Hedge

## Files

- This file: `For You/Plans/card-hedge-pricing-concern-2026-09-16.md`
- Cost model: `For You/Plans/card-hedge-api-discovery-2026-09-16.md`
- Long-term PSA plan: `For You/Plans/psa-pop-data-long-term-2026-09-16.md`

## Why we paused (not just delayed)

The risk: integrate Card Hedge at $0.16/card/month, build customer
expectations around that data quality, then realize pricing needs to
move to maintain margin → customer churn.

Better path: resolve pricing first (informed by Card Hedge costs),
then integrate. Avoids the churn scenario.

## Memory note for next session

When conversation resumes:
- HYBRID path is the right technical answer (cost table in card-hedge-api-discovery-2026-09-16.md)
- But founder's offline pricing math raised concerns
- Pricing discussion is needed BEFORE we integrate
- Manual PSA URL hunt continues in parallel
- Cost/card/month is the right unit metric (founder stated)

## Open question for founder

When you're ready to discuss pricing, please share:
1. What are the issues your offline math surfaced?
2. What's the floor price per card you're comfortable with?
3. Should we structure tiers differently than Hobby/Pro/Elite?
4. Is there a target margin floor (e.g. 80% minimum)?
