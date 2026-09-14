# V2 Feature Spec: Grade-Tiered Listing Filter

## Source
Jon + Jim, Sept 14, 2026. Discussion after viewing sportscardspro.com/snipe tool.

## Problem
Current eBay scrape returns a lot of $1 items that aren't accurate signals:
- $1 BIN with crazy shipping ($50 shipping on a $1 card)
- $1 starting bid on 30-day auctions (will never sell)
- Bulk lot listings ($1 = "lot of 5 cards" not "1 card")
- Junk listings with no real seller intent

These pollute the "below median" signal. Today, a $1 Bo Jackson listing would show
"80% below median" — but it's a junk listing, not a deal.

## Proposed V2 Logic

### For grade 7-8 cards (mid-grade, where Jim spends most time):
- **Auctions**: only show if `<1-2 hours` remaining (sellers actually want to sell)
- **Buy-it-now**: only show if price "represents an opportunity"
  - What this means (TBD): probably exclude $1 BIN with shipping > $10
  - And exclude bulk lots

### Why V2, not V1
- V1 ticker ships a working "deal detection" today (sometimes with junk in it)
- Better filtering is a quality-of-life upgrade, not core feature
- Don't ship complexity without proving core value first

## What needs design work
1. **Listing-type filtering**: how to detect BIN vs auction vs lot in eBay data
2. **Time-left parsing**: how reliable is `timeLeft` field from Apify eBay actor
3. **Shipping cost**: sometimes $1 card + $50 shipping = $51 effective cost
4. **Grade-tier rules**: V2 adds filter per grade tier. Should PSA 10 also have rules? Probably yes (only show BIN < market, ignore $1 BIN).
5. **"Opportunity" definition**: mathematical or heuristic?

## Architecture decision
Should live in `filter_matching_items()` or a new `score_listing_quality()` step in
`discord_alert_bot_v3.py`. Outputs a `quality_score: 0-100` per listing.

Below threshold → drop from alert. Above → show as deal candidate.

## Linkage to other features
- **Thin market handling**: a thin-market card with $1 BIN is still a real signal even if it's "junk" because there's no other data. Filter should skip when `market_thin=True`.
- **Per-card customization**: customers can mark certain cards (e.g., their collection) as "show all" while others get strict filtering.

## Estimate
- ~3-4 hours dev time
- ~1 hour testing on existing 12 cards
- Zero additional cost (uses existing actor output)

## Status
**Parked for V2.** Do NOT implement in V1.
