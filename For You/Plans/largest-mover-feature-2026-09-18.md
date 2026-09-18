# Largest Mover / X Feature — Design (Sept 18)

## Jonathan's vision

"Weekly hot 10 list" — show what's moving up/down by category. From Sept 18 notes:
- "trending up and down, like a hot 10 list"
- "hosted on the site"

## What Card Hedger already gives us

Two relevant endpoints:

### `/v1/cards/top-movers?count=20&category=Baseball`
Returns the top weekly gainers. Test results (Sept 18):
- Baseball top 5: Pete Crow-Armstrong 2026 Bowman, Edgardo Henriquez 2025 Topps Chrome Auto,
  James Wood 2022 Bowman Chrome Prospects, Yoshinobu Yamamoto 2026 Topps,
  Frank Thomas 1999 Skybox Premium
- Pokemon top 5: Purrloin 2014 XY, Dialga 2009 Platinum, Manaphy 2016 XY Promo, etc.
- Gain values around 1.9-2.0% (these are the BEST gainers)

### `/v1/cards/total-sales-by-player`
Returns total sales count for a player over a window.
- Mike Trout 7 days: 3,512 sales
- Shohei Ohtani 7 days: 20,180 sales (big difference — Trout vs Ohtani trading volume)

## What this feature could be

### Option A: Card Hedger's `top-movers` (passive)
- Use their pre-computed weekly gainers
- Filter by category (Baseball, Basketball, Football, Pokemon, MTG, etc.)
- Show top 10 with thumbnail + % gain + 7d/30d sales count
- **Effort**: ~3 hours. Just a wrapper + UI.

### Option B: Our own movers (active, derived)
- Run our alert bot for a curated list of cards
- Compare 7d median vs 30d median
- Calculate our own % delta
- **Effort**: ~6 hours. Need to track history.

### Option C: Combine both (recommended)
- Show Card Hedger's top-movers (industry-wide signal)
- ALSO show top movers among cards our customers track
- Personal signal + market signal side by side
- **Effort**: ~4 hours. Wrapper + UI + customer cards aggregation.

## UI design (Option C, recommended)

**Hosted on cardscout.pro** as a public page (`/trending`).

Two sections:

### Section 1: Market-wide top movers
By category tabs: All | Baseball | Basketball | Football | Pokemon | MTG | One Piece
Each tab shows top 10 with:
- Card thumbnail
- Description + player + set
- % gain (7d)
- 7d sales count
- Link to add to customer's watchlist

### Section 2: Trending among tracked cards (your customers)
Show top 10 movers from cards that ANY of our customers are tracking.
- More relevant signal for our users (what THEY care about is moving)
- Good differentiator vs raw Card Hedger data
- Also helps retention (customers see value even when not getting personal alerts)

## Backend

### New endpoint: `GET /dashboard/trending?category=Baseball&limit=10`

```python
@app.route('/dashboard/trending')
def trending():
    category = request.args.get('category', 'All')
    limit = int(request.args.get('limit', 10))
    
    # Card Hedger top movers
    client = CardHedgerClient()
    movers = client.top_movers(count=limit, category=category)
    
    # Customer-tracked cards: pull from DB, calculate delta
    tracked = get_tracked_cards_with_delta(category)
    
    return render_template('trending.html',
        market_movers=movers['cards'],
        tracked_movers=tracked,
        category=category,
    )
```

### Customer-tracked movers calculation

```python
def get_tracked_cards_with_delta(category):
    """For all enabled customer cards, compute 7d delta from snapshots."""
    cards = session.query(Card).filter_by(enabled=True).all()
    results = []
    for card in cards:
        if card.category != category and category != 'All':
            continue
        snaps_7d = get_snapshots(card.id, days=7)
        if len(snaps_7d) < 2:
            continue
        old_price = snaps_7d[0].median_price
        new_price = snaps_7d[-1].median_price
        delta_pct = (new_price - old_price) / old_price * 100
        results.append({
            'card': card,
            'delta_pct': delta_pct,
            'old_price': old_price,
            'new_price': new_price,
        })
    return sorted(results, key=lambda x: x['delta_pct'], reverse=True)[:10]
```

## Data sources

| Source | Used for | Cost |
|---|---|---|
| Card Hedger `top-movers` | Market-wide signal | Free (already in plan) |
| Our snapshot history | Customer-tracked signal | Already have data |
| `Pop data` (GemRate) | Future: "hot AND rare" | Deferred to 7+ customers |

## Hosting decision

**Hosted on cardscout.pro as `/trending`**:
- Free marketing for new visitors (SEO)
- Public page → customers can share links
- "Coming soon" widget on dashboard cards that show "this card is in our top 10 movers"

## Implementation effort (Option C)

| Component | Effort | Notes |
|---|---|---|
| Backend `/dashboard/trending` route | 1 hr | Simple wrapper around CH |
| Customer-tracked movers aggregation | 2 hrs | Need snapshot history query |
| Public `/trending` page with category tabs | 2 hrs | Bootstrap + cards |
| "Add to watchlist" button on each card | 1 hr | Reuse add-card form |
| Daily refresh (cron) | 1 hr | Cache movers to avoid rate limits |

**Total**: ~6-7 hours

## Validation questions for Jonathan

1. **Hosted publicly** on cardscout.pro/trending, or **dashboard-only** behind login?
2. **Two sections** (market + your tracked) or **just one** (your tracked)?
3. **Categories to support**: All / Baseball / Basketball / Football / Pokemon / MTG / One Piece — or start with just Baseball + Pokemon?
4. **Update cadence**: Hourly / Daily / Weekly? (Daily is probably right)
5. **Pro tier gate?** Pro tier $150/mo might be the only tier that sees trending. Free/Casual just see own watchlist.

## Related Sept 18 ideas

- "Sell-side z-score" uses snapshot history too — same infrastructure
- "Vault / Portfolio Tracker" tracks owned cards — could show as third tab
- All three features share "snapshot history" as the data foundation
