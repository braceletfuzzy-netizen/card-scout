# Vault / Portfolio Tracker (PL-007) — Design & Build Plan

## What is the Vault?

A **portfolio tracker for customer-owned cards**. Lets each customer see:
- Cards they own
- Cost (what they paid) — manual entry
- Current value (live from CH FMV)
- Total portfolio value
- ROI per card and total

## Why now (Sept 18, dealer crowd pivot)

Jim's "Bull Pen" framing (from 18 Sep 2026 Notes.txt):
- "date added, not date acquired if we are figuring ROI. Or have the user input cost/price"
- "per card value now, total per value now"

What we already have (Sept 18):
- ✅ Per-grade FMV from Card Hedger (range, with confidence)
- ✅ Era/category/sport metadata on every card
- ✅ Path C attribution (no vendor names in customer copy)
- ✅ sell_window alert for high-price listings
- ✅ /tracked page with 90-day sparklines per card

What Vault needs:
- Cost basis entry per card (user input)
- Current value (computed from CH FMV)
- ROI per card + portfolio total
- Display in dashboard

## Scope decisions

### In scope for v1

| Feature | Why |
|---|---|
| Add `cost_basis` column to cards | User's purchase price |
| Per-card ROI calc | `(current_fmv - cost) / cost × 100` |
| Portfolio total | Sum of all per-card values |
| `/dashboard/<id>/vault` route | New page |
| Vault UI: list of cards + value + ROI | Foundation for everything else |

### Out of scope for v1

| Feature | Why not |
|---|---|
| Sell-side alerts from Vault | sell_side_alerts already exists; will be linked from Vault |
| Cert # lookup | Was tied to GemRate; not subscribed yet |
| Multi-condition tracking (raw + graded) | Start simple, one cost_basis per card |
| Auto-detect cost from purchase history | User inputs; reliable vs guessed |
| Currency conversion | US only for now |

## Data model changes

```sql
ALTER TABLE cards ADD COLUMN cost_basis_usd REAL;  -- What they paid (NULL = unknown)
ALTER TABLE cards ADD COLUMN cost_basis_set_date DATE;  -- When they got it (NULL = use added_date)
ALTER TABLE cards ADD COLUMN notes TEXT;  -- User notes about the card
```

### Why `cost_basis_usd` vs alternatives

- `cost_basis_usd` = simple, user knows it, no math needed
- `acquisition_price_usd` = same thing, just naming
- We go with `cost_basis_usd` because Jim said "cost/price" and accountant-speak is "cost basis"

## Vault UI design

### Layout

```
┌─ Vault — Jim's portfolio ───────────────────────────────────────────┐
│  Total cost:    $847.50                                              │
│  Current value: $1,247.30                                           │
│  All-time gain: +$399.80 (+47.2%)                                    │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Card                        │ Acquired │ Cost   │ Now     │ ROI    │
│  ─────────────────────────  │ ──────── │ ────── │ ──────  │ ────── │
│  Michael Jordan 1991 UD     │ Sep 2026 │ $750   │ $1,515  │ +102% │
│  Derek Jeter Future Star    │ Sep 2026 │ $40    │ $25     │ -37%  │
│  ...                                                                 │
│                                                                      │
│  [+ Add cost basis]  [Edit costs]  [Sell window alerts →]            │
└──────────────────────────────────────────────────────────────────────┘
```

### Key principles (from Secret Sauce Stance)

- No "Market opinion: $1,515 (A grade)" in user copy
- Show: "Now: $1,515" with hover tooltip "High confidence"
- ROI colored: green for +, red for -
- Total at top, drill-down on rows

## Implementation steps

### Phase 1: Schema + model (1 hr)

- ALTER TABLE add cost_basis_usd, cost_basis_set_date, notes
- Update `scripts/db_models.py` with new columns
- Migration script (works on both local + Render)

### Phase 2: Cost-basis entry UI (2 hrs)

- `/dashboard/<id>/vault` route
- Form to add/edit cost_basis per card
- Inline edit on cards list (no separate page needed)

### Phase 3: Value calc + display (1 hr)

- For each card, pull CH FMV (PSA 10 by default)
- If no CH FMV, fall back to SCPro psa_10_price
- Compute ROI per card + portfolio total

### Phase 4: Polish + button placement (1 hr)

- Add "📊 Vault" nav link to dashboard
- Link from `/dashboard/<id>` overview
- Link from sell_window alerts ("Track this in Vault")

### Phase 5: Test + sync (30 min)

- Run Jim + Alan, populate test cost_basis values
- Verify ROI math
- Sync to Render

**Total: ~6 hours**

## Open questions for Jonathan

1. **Default grade for "current value"** — PSA 10 (highest), or user-selected?
   - Recommended: PSA 10 by default, dropdown to change (PSA 9 / BGS 9.5 / raw)

2. **For cards with no CH FMV** (like Bo Jackson — search fallback rejects)?
   - Recommended: show "—" with hover "No market data yet"

3. **Portfolio total formula** — sum of individual card values, or weighted by liquidity?
   - Recommended: simple sum; liquidity weighting is Pro tier

4. **Negative ROI** — red text or just sign?
   - Recommended: green +, red -, neutral when cost_basis unknown

5. **Should Vault be Pro-tier only?**
   - Recommended: free for beta, Pro feature when we launch paid tier
   - Sells the Pro tier while not blocking beta users
