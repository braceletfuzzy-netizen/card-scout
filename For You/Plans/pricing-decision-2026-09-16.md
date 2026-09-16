# Card Scout — Pricing Decision (Sept 16, 2026)

## Time
Sept 16, 2026 (afternoon)

## Status
**DRAFTED.** Founder's offline math concerns addressed.

## Founder's offline math concerns (verbatim)

> "The offline math was having the price higher than I wanted it to be,
> which meant a restructuring of how many times we pull a week for the
> entry level. So like one update a week vs 3 for dealers, so we can
> still deliver value at a reasonable cost to the market."

> "I would like the entry price to be around the 15-30 dollar mark,
> but If it has to just cover cost then I am fine with that. I want
> the entry to lead to market adaptation, while the revenue comes from
> the dealer level."

## Key insight

**Pull frequency is the right lever** — not card count.
- Entry tier = monthly refresh (digest-style)
- Standard tier = weekly refresh
- Dealer tier = 3x/week
- Pro tier = daily refresh

This lets us hit $15-30 entry price while keeping margins sustainable.

## Proposed pricing structure (4 tiers)

| Tier | Price | Cards | Pulls/mo | Target | Margin @ 100 cust |
|---|---|---|---|---|---|
| **Casual** | $15 | 3 | 1 | Hobbyists / casual collectors | 91% |
| **Standard** | $30 | 6 | 4 | Active collectors (weekly) | 93% |
| **Dealer** | $75 | 20 | 12 | Power users (3x/week) | 90% |
| **Pro** | $150 | 50 | 30 | Dealers / shops (daily) | 77% |

## Cost basis (per card/month)

- Apify-only (today, PSA blocked): $0.020/run
- Monthly refresh (1/mo): $0.02/card
- Weekly refresh (4/mo): $0.08/card
- 3x/week (12/mo): $0.24/card
- Daily (30/mo): $0.60/card

## Why this works for your goals

1. **Entry at $15**: matches your $15-30 target
2. **Cost coverage**: positive margin even at 3 customers (Standard tier)
3. **Dealer capture**: $75-150 tiers where real revenue lives
4. **Pull frequency is the variable cost lever** — customers pay for what they need

## Revenue projections (60% Casual / 30% Standard / 10% Dealer mix)

| Customers | Revenue | Profit | Margin |
|---|---|---|---|
| 10 | $330 | $252 | 76% |
| 50 | $1,650 | $1,495 | 91% |
| 100 | $3,300 | $3,049 | 92% |
| 500 | $16,500 | $15,482 | 94% |

## Tradeoffs

### What we give up
- Casual tier (1 refresh/month) is restrictive — customers may want more
- Per-card cost stays low but revenue per customer is low too
- Stripe fees are 4-5% at low price points

### What we gain
- Low entry point → market adoption
- Clear upgrade path → dealer revenue
- Sustainable margins at all scales
- Pull frequency aligns with customer value (more updates = more value)

## Decision points for founder

1. Is $15 entry OK? (vs $20 or $25?)
2. Is 1 refresh/month enough for Casual? (vs 2 or 4)
3. Should Dealer tier be at 3x/week or daily?
4. Should we skip Pro ($150) for now?

## Next steps

1. Confirm tier structure
2. Update Stripe products with new prices
3. Update tiers in DB (tier=trial/hobby/standard/dealer/pro)
4. Update customer onboarding form
5. Document in customer-facing pricing page (future)
