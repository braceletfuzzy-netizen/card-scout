# Tracked Cards — 90-day Graph Feature (Sept 18, simple version)

## User intent

Jonathan (Sept 18): "Start with simple and we build out from there. Make your
notes where you need to, to help the future you."

This is the SIMPLE pivot table: customer picks category dropdown, sees their
tracked cards with 90-day price history as a sparkline, sortable by 7d delta.

## Why Option 1 (simpler pivot table)

Three options considered:
- Option 1 (chosen): 90-day graph per tracked card, ~3hr
- Option 2: Sales stats by player pivot table, ~4hr
- Option 3: Full hybrid pivot table, ~8hr

We chose Option 1 because:
- Maps directly to Jonathan's mental model: "drop down + snapshot data"
- Smallest API surface (1 endpoint: prices-by-card)
- Fastest ship → get feedback before building more
- Naturally extends to Option 2/3 later without rewrite

## User experience flow

1. Customer visits `/tracked` (or `/dashboard/<id>/tracked`)
2. Sees category dropdown pre-selected to their most-tracked category
3. Sees ranked list of their tracked cards in that category
4. Each row has:
   - Card name + description
   - 90-day sparkline (SVG, no chart library needed)
   - 7d delta vs 90d average (% change)
   - Total listings (liquidity signal)
   - Trend emoji (🔥 / 📉 / ➡️ / ❓)
5. Click sparkline → expand to full-size 90-day chart
6. Future: sort by delta, by 7d sales, by category, by era

## Available endpoints (Sept 18)

### Primary: POST /v1/cards/prices-by-card
Price history for a specific card and grade.

Request body:
```json
{
  "card_id": "1594912932081x453440041273786400",
  "grade": "PSA 10",
  "days": 90
}
```

Response shape (need to verify, but likely):
```json
{
  "card_id": "...",
  "grade": "PSA 10",
  "days": 90,
  "history": [
    {"date": "2026-01-01", "median": 15.0},
    {"date": "2026-01-08", "median": 15.5},
    ...
  ]
}
```

NOTE: Sep 18 we haven't yet tested this endpoint's actual response.
Need to call it on Jim's Donruss Bo Jackson card_id first.

### Card ID lookup flow

Most of our customer cards don't yet have card_id (Jim's 5 cards all NULL).
Need to use either:
- search-cards (text fallback, validated as risky in clean data #2)
- inline matcher (card-match endpoint, cleaner)

RECOMMENDATION: Run inline matcher on all customer cards FIRST.
Then this feature works smoothly.

## Data we have vs need

| Need | Have | Gap |
|---|---|---|
| Customer-tracked cards | Yes (cards table) | None |
| Card ID for each | 5/19 cards have it | Run inline matcher |
| 90-day price history | No (need CH API) | Fetch per card per view |
| Snapshot history | Yes (~3 days) | Use for "freshness" signal |
| Era / category metadata | Yes (clean data #5) | None |

## Implementation plan

### Phase 1: API integration (~1hr)
1. Add `prices_by_card(card_id, grade, days)` method to cardhedger_client.py
2. Test on Jim's Bo Jackson to confirm response shape
3. Add caching (file-based, TTL 6 hours per card_id+grade)

### Phase 2: Card matcher prep (~1hr)
1. Run inline matcher on all customer cards (currently 14/19 without card_id)
2. Store card_id in cards table
3. Sync to Render

### Phase 3: UI route (~1.5hr)
1. Add `/tracked` route to public_site.py (or /dashboard/<id>/tracked if behind login)
2. Category dropdown queries our cards table
3. Render ranked list with sparkline + delta

### Phase 4: Sparkline rendering (~30min)
- Pure SVG (no chart library)
- 90 data points → 90px wide
- Min/max normalize, accent for current vs past
- Hover shows date+price

### Phase 5: Cron (~30min)
- Daily refresh of cached prices (run once per day at 5am)
- 19 cards × 1 grade (top grade per card) = 19 API calls/day = safe

## Total effort: ~4.5 hours

## Open questions

### Q1: Public or dashboard-only?
/tracked on cardscout.pro/tracked → public
OR /dashboard/<id>/tracked → logged-in only

PRO public: shows new visitors what we do, SEO wins
PRO dashboard: only logged-in customers see their own cards (no anon browsing)

DECISION NEEDED — recommend DASHBOARD because:
- Tracked cards are personal data
- Sparklines look better in dashboard context
- Trending page (/trending) is already the public surface

### Q2: How many grades per card?
Each card has grades: PSA 10, PSA 9, BGS 9.5, CGC 10.
1 chart per card (track top grade) OR 4 charts per card (one per grade)?

PRO 1 chart: simpler, faster, fewer API calls
PRO 4 charts: more useful, matches the per-grade alert logic we shipped

DECISION: 1 chart per card for v1, show grade in label.
Add 4-chart mode as v2 if customers ask.

### Q3: Where does it live?
Two routes, two tabs:
- /trending → public market movers (already shipped)
- /tracked → customer's tracked cards (new)
- /trending/{category} → filtered view of public movers
- /dashboard/<id>/tracked → same as /tracked but auto-logs-in

RECOMMENDATION: /tracked as public-but-personal.
If no customer in session, show empty state with "log in to see your cards"
If logged in, show their cards.

### Q4: Sparkline rendering
Options:
a) Inline SVG (no library, lightweight)
b) Chart.js (heavyweight, has 90d chart)
c) d3.js (overkill for sparklines)
d) Server-side PNG (Render every page load = expensive)

RECOMMENDATION: a) Inline SVG. Tiny, fast, looks good.

## Risks

### Rate limits
CH Starter: 10 req/min. 19 cards × 1 grade = 19 req per page refresh.
If we cache for 6 hours, only refreshers hit the limit.

If we display 4 grades per card = 76 req per page = too much.
SOLUTION: use 1 grade per card for v1, fetch only on cache miss.

### Cache invalidation
Cards move, prices change. A 6-hour cache might show stale prices.
SOLUTION: Add "as of HH:MM" timestamp to page header.
Customers know they're looking at cached data.

### Card ID availability
14/19 customer cards lack card_id. The feature literally won't work
for those cards without it.
SOLUTION: Run inline matcher first (Phase 2 above).

## Future extensions (not in v1)

### Extension A: Sales stats by player (Option 2)
Add `sales-stats-by-player` view per customer card. Sales count + mean price
bucketed by day/week/month. Adds sales activity dimension.

### Extension B: Hybrid pivot table (Option 3)
- Dimension selector: era / category / grade
- Multiple time buckets in columns
- Drill-down to specific cards

### Extension C: Alert on tracked delta
"Notify me when any of my tracked cards move >X% in 7 days"
This becomes a new alert type for Pro tier.

### Extension D: Side-by-side comparison
Show 2-3 cards' 90d charts next to each other for direct comparison.

## Files to create/modify

NEW:
- scripts/compute_tracked_movers.py (the data fetching + caching)
- dashboard/trending_cache/prices_<card_id>.json (one per card)

MODIFIED:
- scripts/cardhedger_client.py (add prices_by_card method)
- dashboard/public_site.py (add /tracked route)
- dashboard/dashboard_template.html (sparkline template, if separate)

TESTED:
- scripts/run_inline_matcher.py (need to create - runs matcher on all cards)

## Architecture decisions

1. **Same cache dir as trending**: dashboard/trending_cache/
   Pattern: trending_cache/{prices,fmv,movers}_<key>.json

2. **Single-grade focus for v1**: top tracked_grade per card
   Stored in card.tracked_grade field (need to add)
   Default: 'PSA 10'

3. **Pure server-side rendering**: flask + Jinja2 + inline SVG
   No React, no Vue, no client-side JS framework
   Single fetch on page load

4. **Daily cron refresh**: 5am Central
   Pre-warms cache before users start browsing

## Status

STARTED Sept 18. Phase 1 (API integration) next.
