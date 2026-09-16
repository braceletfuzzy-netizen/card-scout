# Session Save - Sept 16, 2026 (Afternoon - Beta Feedback + Deal Detector)

## Time
Sept 16, 2026 (afternoon)

## What we shipped

### Bot run for all 3 customers
- Jim: 12 alerts sent ✅
- Hingle: 3 alerts sent ✅
- cs_CZYAJYA00001 (test): 0 (dead webhook)
- Total: 15/16 successful (94% delivery)

### Deal detector (commit `8ebe702`)

Founder's insight from beta notes:
> "If the market for 10's doesn't have the pricing spread, the price
> is the price. But where there is spread, there is a deal definition."

Algorithm: per-grade lower-third threshold
- threshold = low + (high - low) / 3
- Filter grades where spread < $1 or < 5%
- Flag listings below threshold as deals
- Sort by discount % (biggest first)

Why per-grade:
- PSA 10: often $0 spread (single market rate)
- PSA 9, 8, 7: real spread (condition varies)

### Pricing band data check
- Bo Jackson PSA 10: low=$655.34, high=$655.34 (no spread)
- All current Jim cards have $0 spread (sportscardspro returns 1 price per grade)
- This means: PSA 10 deals will be rare with current data
- Need richer data capture for PSA 9/8/7 deals (where spread exists)

## Founder's beta notes (Jim)

### Spacing + Font
- "results are hard to read, need more spacing in between data groupings"
- "we might have to go a little larger (2-4 maybe)"
- "Jim likes the trending part"

### Layout (founder's proposal)
1. **Trend** (top — keep current)
2. **Per-grade Market Values** (move from bottom to top, under trend)
3. **Market Shape** (under per-grade values)
4. **NEW SECTION**: User-defined search parameter (ex Bo Jackson ... PSA 9) + 90% CI + 70% CI
5. **Deals** (use new deal_detector, per-grade lower-third)

### Deal definition (founder's logic)
- "anything below the lower third line of the CI band"
- `[x1___/_*_/___x2]` — split range into thirds
- * = mathematical avg between x1 and x2
- Top 3 in Discord with links
- Top X (5, 10) on website (founder undecided)

### Business insight (founder)
- "driving traffic to our website will eventually open the door for ad revenue"
- "we are only as useful as we are accurate. Everything else will fall into place"

## Decisions captured

1. **Deal detection**: per-grade (per founder's "spread determines deals" insight)
2. **Threshold formula**: `low + (high - low) / 3` (founder's lower-third)
3. **Min spread**: $1 OR 5% (filters noise)
4. **Min volume**: 3 listings (need enough data to define deals)
5. **Top 3 deals in Discord** (founder's choice)
6. **Top X (5-10) on website** (founder undecided — needs decision)

## What's pending

### From Jim's notes
- Font size 2-4pt larger
- Spacing between sections
- Reorder alert layout

### From founder's notes
- Add 90% CI + 70% CI section
- Wire deal_detector into bot
- Build website view (top 5-10 deals) — drives ad revenue potential

### Other open fires
- URL ownership pattern (shower insight)
- Pricing discussion (cost/card/month)
- PSA unblock testing
- Cron job for bot

## Files

| File | Status |
|---|---|
| `scripts/deal_detector.py` | NEW (267 lines, 12 self-tests pass) |
| `For You/Plans/card-hedge-api-discovery-2026-09-16.md` | NEW (research) |
| `card_scout.db` | updated (12 pricing bands captured today) |

## Memory note for next session

When conversation resumes:
- Bot runs all customers successfully (Jim + Hingle, cs test dead)
- Deal detector committed (`8ebe702`)
- PSA all-pop lookups fail (expected with PSA block)
- Sportscardspro still works for all prices
- Pricing_bands have flat low/high/volume (no CI captured)
- Jim + founder notes both pending layout rework

## When founder returns

Likely next:
1. Wire deal_detector into bot (replaces current below-market logic)
2. Reorder alert layout per founder's spec
3. Increase font size + spacing
4. Build website view for deals (ad revenue potential)
5. URL ownership pattern (shower insight)
