# PSA Grades-as-Stock Ticker Design

## Time
Sept 16, 2026 (morning)

## Status
**DRAFTED.** Founder's big insight captured. Ready to implement.

## The insight (founder's words)

> "PSA 10 is the A series, PSA 9 is the B series, PSA 8 is the C series,
> etc. Each card is like a share of stock. Once a card is graded and
> verified by PSA, it becomes essentially a stock certificate worth whatever
> the market value is. People go to swap meets and card shows and physically
> exchange certificates face to face as well as online. It really reminds
> me of physical stock trading before it became a digital exchange. There
> are a lot of old school market mechanics that happen. One of those is
> that the pricing band is very wide."

## What this means for Card Scout

We are NOT just showing prices. We are building the **Bloomberg terminal
for graded cards**. Each card = a stock. Each grade = a class of shares.
The PSA population report = the issuer's outstanding share count.

## Stock-ticker analogy mapping

| Stock market concept | Card market equivalent | Card Scout data |
|---|---|---|
| Ticker symbol | Card identifier (search_query) | cards.search_query |
| Outstanding shares | Total PSA population | cards.psa_total_pop (NEW) |
| A-class shares (most valuable) | PSA 10 population | cards.psa_10_pop |
| B-class shares | PSA 9 population | cards.psa_9_pop |
| C-class shares | PSA 8 population | cards.psa_8_pop |
| Last traded price | Recent sale price | sportscardspro per-grade |
| 52-week high/low | 30-day range | pricing_bands |
| Volume traded | Sales per grade per period | sportscardspro sold_count |
| Market cap | Population × typical price | computed |
| Bid-ask spread | Price band width | pricing_bands low-high |
| Stock chart | Price history per grade | NEW: trend over time |

## New ticker display format (V3)

### Current (V2)
```
📊 Per-Grade Ticker
  Raw: $1.50
  PSA 7: $12.75 (typical $8.92-$16.57)
  PSA 8: $13.18
  PSA 9: $18.36
  PSA 10: $107.50 (typical $93.37-$116.63)
```

### Proposed (V3 - stock-style)
```
📊 Per-Grade Ticker (1996 Topps Chrome #80 Derek Jeter)

🎖️ Stock-class hierarchy:
  A (PSA 10): $107.50 [23 sold/30d] ⭐ RARE — only 399 exist (5% of pop)
  B (PSA 9):  $18.36   [12 sold/30d]  📊 COMMON — 715 exist (43%)
  C (PSA 8):  $13.18   [8 sold/30d]   📊 COMMON — 387 exist (23%)
  D (PSA 7):  $12.75   [0 sold/30d]   📊 COMMON — 230 exist (14%)

🏷️ Total outstanding: 1,731 graded
📈 Market depth: 33 sales/30d across all grades
💎 Premium: PSA 10 trades 6× the PSA 9 price (rare asset premium)
```

### Key additions

1. **Stock-class label** (A/B/C/D) next to grade
2. **Rarity indicator** — PSA 10 pop as % of total
3. **Market depth** — total sales across all grades
4. **Premium calculation** — price ratio between grades
5. **"RARE"/"COMMON"/"SCARCE"** tag based on rarity

## Data needs

### Currently have
- ✅ Per-grade prices (sportscardspro)
- ✅ Per-grade sales volume (sportscardspro)
- ✅ 30-day price bands (pricing_bands)
- ✅ Card metadata (cards)

### Need to add
- ❌ PSA population data persisted to DB
- ❌ Rarity % calculation
- ❌ Market depth calculation
- ❌ Premium calculation

### Schema change (migration needed)

Add 4 columns to `cards` table:

```sql
ALTER TABLE cards ADD COLUMN psa_total_pop INTEGER;      -- total PSA-graded count
ALTER TABLE cards ADD COLUMN psa_10_pop INTEGER;          -- PSA 10 count
ALTER TABLE cards ADD COLUMN psa_9_pop INTEGER;           -- PSA 9 count
ALTER TABLE cards ADD COLUMN psa_pop_fetched_at TIMESTAMP; -- when last fetched
```

This allows the bot to:
1. Fetch PSA pop once per card (or daily)
2. Save to DB
3. Compute rarity % on every alert
4. Display stock-class labels

## Implementation plan (~3 hours)

### Phase 1: Persist PSA pop data (1 hour)

- Add 4 columns to cards table (migration script)
- Update `psa_pop_lookup.py` to write results to DB
- Add `fetch_psa_pop_for_card(card_id)` helper
- Wire into bot: when processing a card, fetch PSA pop if stale (>24h)

### Phase 2: Rarity calculator (30 min)

- Add `compute_rarity(psa_total_pop, psa_10_pop)` helper
- Returns: `{label: 'RARE'|'SCARCE'|'COMMON'|'PLENTIFUL', pct: float}`
- Thresholds:
  - PSA 10 < 1% of total = RARE
  - PSA 10 < 5% of total = SCARCE
  - PSA 10 < 15% of total = COMMON
  - PSA 10 > 15% of total = PLENTIFUL

### Phase 3: Stock-class label (30 min)

- Add `format_stock_class(tier, psa_pop, psa_total_pop)` helper
- Returns: `{label: 'A'|'B'|'C'|'D', description: 'most valuable'|'...' }`
- Mapping:
  - PSA 10 = A (highest value)
  - PSA 9 = B
  - PSA 8 = C
  - PSA 7 = D
  - Raw = unlisted

### Phase 4: New ticker formatter (1 hour)

- Update `ticker_formatter.py` to render the new format
- Add section for "Stock-class hierarchy"
- Show rarity %
- Compute market depth (total sales across grades)
- Compute premium (PSA 10 / PSA 9 ratio)

### Phase 5: Test on real data (30 min)

- Run bot for Bo Jackson (Jim has data)
- Verify PSA pop fetched and saved
- Verify new ticker format renders correctly
- Check Discord output looks like a stock ticker

## Decisions to make

1. **How often to refresh PSA pop?**
   - Daily? Weekly? On-demand only?
   - Recommendation: weekly (saves API cost)
   - Cache invalidation: >7 days old

2. **What if PSA pop fetch fails?**
   - Skip the stock-class section, show normal ticker
   - Show "(pop unavailable)" hint
   - Recommendation: skip gracefully

3. **Display rarity as %, label, or both?**
   - Both — label for quick scan, % for precision
   - Color-coded: red for RARE, yellow for SCARCE, gray for COMMON

4. **Include premium in ticker?**
   - "PSA 10 trades 6× PSA 9" is informative
   - Recommendation: yes, only when ratio > 2×

## Why this is the right next feature

This isn't just a cosmetic upgrade. It transforms Card Scout from
"price tracker" to "graded card intelligence platform":

1. **Differentiator** — no other tool shows PSA pop alongside price
2. **Educates users** — explains the rarity premium
3. **Frames cards as investments** — aligns with how collectors think
4. **Sets up future features** — historical pop trends, pop velocity (rare card getting more rare)

## Validation

After implementation:
- Run bot for Bo Jackson → should fetch PSA pop, save to DB
- Alert should include rarity section
- Send to Discord → verify visual

## Estimated value

- Customer-facing: HIGH (turns price tracker into investment tool)
- Cost: $0 (just code changes)
- Time: 3 hours
- Unblocks: V3 product positioning, future V4 features (historical pop, pop velocity)

## Related docs

- `For You/Plans/architecture-decision-record-storage-vs-pull-2026-09-14.md` — store-vs-pull principle
- `For You/Plans/v2-grade-tiered-listing-filter-2026-09-14.md` — V2 filter spec
- `scripts/psa_pop_lookup.py` — existing PSA pop fetcher
- `scripts/db_models.py` — Card model
