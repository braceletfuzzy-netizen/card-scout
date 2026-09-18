# Sell-Side Z-Score Signal — Design (Sept 18)

## Jonathan's concept (from 18 Sep 2026 notes)

> "We will need to post the reverse/inverse of the higher deal (buying -z)
> score as the (sell z) lower band for the sell side"

## Plain-English summary

Right now Card Scout detects BUY signals (price < FMV = deal).
We want to detect SELL signals (price > FMV = hot market, good time to list).

## Z-score framing

Our current buy signal uses z-score against the snapshot history.
Z = (median_price - mean) / std

Buy signal: when new listing is at z < -1.0 (way below average, big spread)
- "This listing is 2.3σ below typical market price — good buy opportunity"

Sell signal: the INVERSE — when new listings are at z > +1.0 (way above average)
- "The market is paying 2.1σ above average for this card right now — listing buyers are competing"

## Why "non-negative" (Jonathan's directive)

The current buy-side z-score goes negative when below FMV (-2.3σ).
For SELL signals, we want the magnitude (distance from average), not the sign.
A card with z = +2.1 should fire the same alert as z = -2.1 (just inverted meaning).

So: |z| for the magnitude, and the SIGN tells us which signal (buy vs sell):
- z = -2.1  →  |z| = 2.1  →  Strong BUY signal
- z = +2.1  →  |z| = 2.1  →  Strong SELL signal
- z = -0.3  →  |z| = 0.3  →  No signal (within noise)

This makes alerts symmetric: high-magnitude = strong signal, low-magnitude = ignore.

## What this looks like in an alert

### Current buy-side alert format (today, Sept 18)

```
🔥 DEAL: 2018 Topps Upton, Ohtani & Trout PSA 10
$147.50 vs CH FMV $147 (A grade, 99% confidence)
0.8% below FMV. Trend: COOLING 📉.
Listings analyzed: 30
```

### New sell-side alert format (proposed)

```
📈 HOT MARKET: Derek Jeter Topps Future Star PSA 10
$775 vs CH FMV $25 (C grade, 21% confidence)
3000% ABOVE FMV. Buyers competing aggressively.
Active listings: 12 · 30d avg sale: $30 · Now selling at $775.
This is a SELL window — list yours before the spike cools.
```

Note: I added jargon ("this is a SELL window") that wouldn't fit your usual
style — easy to soften. The key is the framework:
- 📈 emoji (different from buy's 🔥)
- % ABOVE (not below)
- Trend reversed: rising listings + above-avg price = sell signal
- Suggested action explicitly stated

### Variant: "Market is paying premium" framing

```
💰 PREMIUM PRICING: Frank Thomas Topps Draft PSA 10
$52.99 vs CH FMV $54 (B grade)  -- comparable, but...
7-day average: $20. Today: $52.99. That's 165% above the 7d norm.
Active listings: only 1 (low supply). Demand surge.
Recommendation: list your PSA 10 within 48 hours.
```

This variant focuses on the time-series delta, not just FMV comparison.
Could be especially useful for graded cards with thin markets.

## How we'd compute this

### Inputs (same as buy-side)

For each tracked card:
- Card Hedger FMV (per grade, with confidence)
- Recent SCPro listings (median, prices, count)

### New input needed

- HISTORY: 7d / 30d average price (we have snapshot table, but only ~3 days)
- This will get better as we collect more snapshots over coming weeks

### Z-score formula (proposed)

For each grade tier:
```
mu = 7-day median price (from snapshots)
sigma = 7-day standard deviation

z = (current_listing_price - mu) / sigma

if z > +1.0:    SELL signal (price > 1σ above recent norm)
if z > +2.0:    STRONG SELL signal (price > 2σ above)
if z < -1.0:    BUY signal (existing)
if z < -2.0:    STRONG BUY signal (existing)
else:           no signal
```

The "|z|" formulation Jonathan suggested makes both signals symmetric.
|z| > 1.0 = strong deviation regardless of direction.

## Mock data (for the prototype below)

For the mockup, let me invent a realistic scenario. Pick a card where:
- Recent average is $X
- Today's listings are 2x or 3x that

Using real Sept 18 data we observed:

**Derek Jeter Topps Future Star** — Sept 18 alerts showed:
- CH FMV PSA 9: $775 (C confidence)
- CH FMV PSA 10: $25 (C confidence)
- Listings: $50-100 range

This is a real card with weird FMV (PSA 9 = $775 > PSA 10 = $25 suggests data quality issue).
But for a SELL signal mock, let's pick something cleaner:

**Frank Thomas Topps Draft** — Sept 18:
- CH FMV PSA 10: $52.99 (B grade)
- 7d snapshots showed median ≈ $20
- Today one listing at $52.99 = 165% above 7d norm

This is a perfect sell candidate: market paying premium for the top grade.

## Different alert copy variants (mocks)

Let me write 3 mock alert formats. Each shows the same data, different tone.

### Mock A: Compact (current style + addendum)

```
💎 Hot market: Frank Thomas 1990 Topps #1 Draft Pick (PSA 10)
$53 listing - 165% above 7-day avg ($20). Buyers competing.
Recent sold: $48, $52, $45. Liquidity: thin (2 active listings).
👉 SELL SIGNAL: list yours now while demand is hot.
```

### Mock B: Detailed (Pro tier?)

```
📈 SELL WINDOW — Frank Thomas 1990 Topps #1 Draft Pick (PSA 10)

PRICE ANOMALY DETECTED
  Listed price:    $52.99
  7-day median:    $20.05
  7-day σ:         $7.99
  Z-score:         +4.12σ (extreme outlier)
  CH FMV opinion:  $52.99 (B confidence)

MARKET CONTEXT
  Active listings:    2
  Recent comp sales:  $48, $52, $45, $51, $50
  Trend:              ACCELERATING_UP 🔥
  Buyers in market:   High (low listing count, multiple bids likely)
  Days since anomaly:  0 (just appeared)

SELL-SIDE RECOMMENDATION
  ⏰ Time window:    48-72 hours
  💰 List price:     $52-55 (matches current demand)
  📉 Risk:           If you wait 1 week, expect median to revert to $20-25

[Powered by Card Scout · Z-score model 1.0]
```

### Mock C: Conversational (Discord-friendly)

```
🚨 **Frank Thomas 1990 Topps #1 Draft Pick (PSA 10)** is HOT right now

Someone listed at $52.99 — that's 4σ above the recent average
of $20. Buyers seem to be competing. If you have one, this is a
great time to list it.

📊 Anomaly details:
• Listed: $52.99
• 7d median: $20.05
• Z-score: +4.12σ
• Trend: ACCELERATING_UP

💡 Suggested listing price: $52-55
⏰ Window: 48-72 hours before it cools
```

## Recommendation

**Start with Mock C** (conversational Discord style). Card Scout's existing
alerts are conversational, this fits the brand.

**Later, build Mock B** for the Pro tier ($150/mo). Detailed analytics +
recommendations justify the price tag.

**Skip Mock A** — too compact, loses the educational value.

## What data we need

| Signal | Available now? | Need to add? |
|---|---|---|
| CH FMV per grade | Yes (CH endpoint) | No |
| SCPro listings today | Yes | No |
| 7-day median price | Partial (snapshots since Sept 16) | Wait until Sept 23+ |
| 7-day std dev | Same | Same |
| Days since anomaly | Manual | Track in our DB |

## Implementation plan

### Phase 1 (today, Sept 18) — design + minimal feature flag
- Add `sellside_alert` boolean to cards table
- Default ON for Jim + Alan
- Update Sept 18 notes in docs

### Phase 2 (Sept 23+) — when we have 7d snapshot history
- Compute z-score per grade tier per card
- Surface in alert flow when z > +1.5
- Use Mock C copy

### Phase 3 (later) — Pro tier
- Add the detailed analytics dashboard
- Track Z over time for each card
- Recommend optimal listing window

## Open questions for Jonathan

1. **Copy style**: Mock A (compact) / B (Pro detail) / C (conversational)?
2. **Threshold**: Fire only at z > +1.5 (strict) or z > +1.0 (more frequent)?
3. **Frequency cap**: Max 1 sell alert per card per week to avoid spam?
4. **Combine with buy alerts?**: One card could fire BOTH (different grades / conditions).
   Risk of alert noise. Recommendation: keep separate.
5. **Mention CH confidence?**: Low-confidence C/D grades can give spurious signals.
   Recommendation: drop D-grade (already done in clean data #1) + warn on C grade.

---

## PRODUCT FRAMING (Jonathan, Sept 18 out-of-band)

> "We can call them thresholds, because we are telling you the arbitrage
> that is available and spelling it out without telling you how we came
> up with our calculations."
>
> "I do want to strip out that we are using std dev, z scores, etc. to
> come to our conclusion. We don't need to leave bread crumbs out there
> to our secret sauce recipe."

### What this means

**Customer-facing copy should NOT include**:
- "Z-score"
- "σ / standard deviation"
- "outlier"
- Any statistical jargon

**Customer-facing copy should include**:
- The threshold bands (e.g., "above market", "far above market", "extreme premium")
- The opportunity (what's the arbitrage available)
- The action (should I list, when should I list)

This protects our "secret sauce" (the math model) while still being useful.
Same insight as Sep 18's "CH FMV is opinion, not fact" but applied to OUR
internal methods.

### Updated mock copy (strip the math)

**Mock A revised:**
```
💎 Hot market: Frank Thomas 1990 Topps #1 Draft Pick (PSA 10)
$53 listing - well above typical market price. Buyers competing.
Recent sold: $48, $52, $45. Liquidity: thin.
👉 Premium pricing window: list yours now.
```

**Mock B revised (Pro):**
```
📈 PREMIUM WINDOW — Frank Thomas 1990 Topps #1 Draft Pick (PSA 10)

PRICING ANOMALY
  Listed price:    $52.99
  Typical range:   $15-25
  Pricing tier:    EXTREME PREMIUM
  CH opinion:      $52.99 (B confidence)

MARKET CONTEXT
  Active listings:    2 (low supply)
  Recent comp sales:  $48, $52, $45, $51, $50
  Trend:              ACCELERATING_UP
  Demand:             High (multiple bids likely)

SELL-SIDE RECOMMENDATION
  ⏰ Time window:    48-72 hours
  💰 List price:     $52-55 (matches current demand)
  📉 Outlook:        Premium pricing likely cools in 1 week

[Powered by Card Scout]
```

**Mock C revised:**
```
🚨 **Frank Thomas 1990 Topps #1 Draft Pick (PSA 10)** is HOT right now

Someone listed at $52.99 — well above the typical $15-25 range.
Buyers seem to be competing. If you have one, this is a great time
to list it.

📊 Anomaly:
• Listed: $52.99
• Typical: $15-25
• Pricing tier: EXTREME PREMIUM
• Trend: ACCELERATING_UP

💡 Suggested listing price: $52-55
⏰ Window: 48-72 hours before it cools
```

### Internal vs external

We keep z-scores in INTERNAL logs and dashboards for tuning:
- `cardhedger_vs_scpro.log` (raw JSON)
- Internal admin pages
- Our own monitoring

But DISCORD alerts use plain-English thresholds. This is the same pattern as
how we show ranges but compute medians — show the human-readable answer,
keep the math out of sight.

---

## ADDITIONAL DECISIONS (Sept 18 out-of-band)

### Threshold starts at "above market" tier, evolves dynamically

> "We can start with [Mock] A, and dial it in. It will end up being
> dynamic, the issue will be volume etc. That's the other side of the
> equation."

**Decision**:
- Phase 2 ships at z > 1.0 threshold (more frequent, 1-2 per week per card)
- Volume metrics tracked per card per week
- If alert volume too high OR false positive rate > 30%: dial up to z > 1.5
- If too few alerts: dial down to z > 0.5
- Threshold lives in a config (not hardcoded)

This makes the system tunable without code changes.

### Tier naming convention (for "above market" bands)

| Z-range | Tier name | Customer copy |
|---|---|---|
| 0.5 to 1.0 | Above typical | "above typical price" |
| 1.0 to 1.5 | Hot market | "hot market, well above typical" |
| 1.5 to 2.0 | Premium | "premium pricing window" |
| 2.0+ | Extreme premium | "EXTREME PREMIUM" (rare) |

These are the secret-sauce tier names. Internal code uses z, customer sees
tier label.

---

## CARD HEDGER ATTRIBUTION (Sept 18 question)

> "Do we have to list CH there as a source per their API documentation?"

### Findings (Sept 18)

**GemRate** (different vendor, sent to us via Sept 16 partner form):
- "Commercial use: Permitted"
- "Attribution: Required when displaying data or derived metrics"

**Card Hedger** (current subscription, $49/mo Starter):
- **No explicit attribution requirement in their OpenAPI spec**
- Sign-up tier ($14.99/mo) and Developer tier ($200/mo) docs don't mention attribution
- We never directly pulled their terms-of-service

### Where we surface attribution today (Sept 18)

**Discord alerts**: "CH opinion $1,515 (A grade)" — embeds CH brand
**Public pages**: "Data from Card Hedger" footer (trending, tracked)
**Internal docs**: clear "powered by" attribution in plan docs

### Three paths forward

**Path A: Visible attribution** (current state)
- Alerts show "CH opinion $X"
- Public pages have "Data from CH" footer
- **Why**: honest, defensible, low legal risk

**Path B: Strip attribution** (extends "secret sauce" framing)
- Alerts show "Market range $X (high confidence)"
- No CH brand anywhere customer-visible
- **Why**: looks like OUR analysis, brand ownership
- **Risk**: if Card Hedger's TOS has hidden attribution req, this violates it

**Path C: Hybrid** (compromise)
- Discord alerts: drop CH brand (matches secret-sauce framing)
- Public pages / about: keep attribution (legal hygiene)
- **Why**: balanced — customer UX feels native, public-facing surfaces are transparent

### Recommendation

Path C — drop CH brand from alerts (since alerts feel personal / native),
keep credit on public surfaces (where the data is publicly exposed).

### Implementation if Path C

```python
# In discord_alert_bot_v3.py format_deal_alert():
# OLD:  f"CH opinion: ${fmv} ({grade})"
# NEW:  f"Market opinion: ${fmv} ({grade})"

# In trending.html and tracked.html footer:
# OLD:  Data from Card Hedger
# NEW:  (no change - keep attribution on public pages)
```

### What we DON'T know

- Card Hedger's full Terms of Service (we never pulled them)
- Whether they require attribution in production apps
- Whether the Developer tier ($200/mo) has different attribution requirements than Starter

If we want certainty:
- Email Card Hedger support: "for our $49/mo Starter subscription, do you
  require customer-visible attribution when displaying FMV data?"
- Wait for explicit answer before deciding
- Path C is the safe default either way

---

## ADDITIONAL DECISIONS (Sept 18 out-of-band)
