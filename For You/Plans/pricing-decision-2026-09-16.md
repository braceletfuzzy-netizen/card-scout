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


---

## Sept 17 evening — Pro tier "Coming Soon" decision

**Founder guidance (verbatim)**: *"I don't feel comfortable offering a $150
dealer tier without being able to point to Population data though, so we
should change that to a coming soon option on the website. I want to have
it available once we can sustain it."*

**Context**: After verifying GemRate pricing ($200/mo developer tier), the
Pro tier at $150/mo loses its main differentiator (population context).
Without GemRate subscription, we can't deliver:
- Population context (PSA/BGS/SGC/CGC)
- Cert # lookup & vault tracking (Vault = PL-007)
- Player-level trend aggregation (PL-006)
- Bulk catalog CSV for inline search (PL-008)

**Decision**: Mark Pro tier as **"Coming Soon"** on cardscout.pro/pricing.
Keep the $150 price point. List features explicitly so customers see what's
coming. Add FAQ entry explaining the honest reason (data subscription
dependency, not "we ran out of time to build it").

**Changes shipped** (commit a283825):
- Pro tier card: dashed border, 65% opacity, "Coming Soon" badge
- Three Pro-tier features annotated with ○ icon and italic styling
- New FAQ: "Why is Pro tier marked Coming Soon?"
- Pricing page meta + subtitle updated

**Trigger to launch Pro**:
- 7+ paying customers (math supports $200/mo GemRate subscription)
- OR inline search UX becomes priority (needs gemrate_id canonical IDs)
- Same as PL-009 (GemRate integration) decision criteria

**What this means for the original Sept 16 pricing structure**:
- Casual $15, Standard $30, Dealer $75 — unchanged, all live
- Pro $150 — now visibly marked Coming Soon (was a "we built it but don't
  advertise it yet" tier, now openly honest about scope)
- Margin projections in this doc still valid for 3-tier case
- Add 4th row when Pro launches: $150/30 refreshes with population data

**Strategic intent**: This is **honesty > marketing**. Founder's words:
*"I have enough money to subsidize the operational bloat until we have
enough paying subscribers if we are smart and keep our overhead recurring
costs low until we have the need to inflate it."*

Per `Sessions/2026-09-17-cost-breakdown-vs-card-hedger.md`, Tier 2 (GemRate)
triggers at 7+ customers. Until then, Pro tier stays Coming Soon.

