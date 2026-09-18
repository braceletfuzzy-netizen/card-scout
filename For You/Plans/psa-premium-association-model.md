# Sept 18 Math Model — PSA-Premium Association Logic

## Jonathan's insight (Sept 18, mid-conversation)

> "Down the road we will figure out the math model: (psa10-premium) = psa 9.
> There will be an association logic as a discount to premium function that
> will tell us a really good idea of what that price 'should' be around.
> We just aren't there yet."

## What this means

**Each grade tier has a known relationship to its neighbors.** PSA 10 commands a
premium over PSA 9, PSA 9 over PSA 8, etc. Across the card market, the ratio
between grade tiers follows patterns:

- Modern base cards: PSA 10 ≈ 2-4x PSA 9 (sharp premium for gem mint)
- Vintage base cards: PSA 10 ≈ 8-15x PSA 9 (harder to grade, scarcer at top)
- Rookie cards: PSA 10 ≈ 4-8x PSA 9
- Junk-era cards (1986-1993 Donruss/Fleer/Topps): variable

## The "discount to premium function"

Jonathan's idea: for any card, if we know the PSA 10 price, we can derive a
likely PSA 9 price (or PSA 8, BGS 9.5, etc.) using a learned function.

```
psa9_price = f(psa10_price, card_category, era, scarcity_signal)
```

Where `f` is a learned association function — could be:
- A simple lookup table by era + card category
- A regression model trained on comp data
- A Bayesian prior updated by individual card sales

## Why this matters

1. **Cross-validation of FMV data**: When we see CH FMV at PSA 10 = $1,500 and
   PSA 9 = $200, the ratio is 7.5x. Is that realistic for this card category?
   If not, one of the FMVs is suspect.

2. **Imputation when FMV is missing**: Low-confidence cards often have FMV at
   only one grade. We can derive others from the known one.

3. **Better alerts**: A PSA 9 listing at "below PSA 10 FMV" might still be
   overpriced if the card's category typically shows 5x premium (PSA 9 should
   be ~$300, not $1,500). The function gives us a sanity check.

4. **Population-aware pricing**: Combine with PSA pop counts — if PSA 10 is
   rare (Top 1% pop) AND the ratio is unusual, the card is a strong candidate
   for the function to flag.

## Current data we have (Sept 18)

The comparison log captures per-grade FMVs for every Card Hedger fetch. This
is the training data for the function.

### Observed ratios (Sept 18 data, n=4 cards)

| Card | PSA 10 | PSA 9 | Ratio (10/9) | BGS 9.5 | CGC 10 |
|---|---:|---:|---:|---:|---:|
| Donruss 87 Bo Jackson | $13 | $5 | 2.6x | $7 | $19 |
| Frank Thomas Draft | $54 | $15 | 3.6x | $20 | $18 |
| Michael Jordan 1991 UD | $1,515 | $177 | 8.6x | $425 | $538 |
| Mookie Betts | $120 | $41 | 2.9x | $74 | $75 |
| Upton/Ohtani/Trout | $148 | $45 | 3.3x | $98 | $68 |
| Henry Aaron 1969 Auto | $1,697 | $557 | 3.0x | $761 | $803 |
| Portgas D. Ace | $193 | $2 | 96.5x (anomaly!) | $26 | $23 |
| Derek Jeter Future Star | $25 | $775 | 0.03x (anomaly!) | $9 | $13 |

**Anomalies detected**:
- Portgas D. Ace PSA 9 = $2 → likely misclassification (very low confidence grade C)
- Derek Jeter PSA 9 = $775 while PSA 10 = $25 → looks like the PSA 9 and PSA 10
  are mapped to different cards. Card Hedger search fallback can pick wrong cards.

### Patterns emerging

- **Modern base cards** (Frank Thomas, Mookie Betts, Upton/Ohtani/Trout): 2.6-3.6x premium
- **Vintage/high-value** (Michael Jordan 1991 UD): 8.6x premium (high because gem-mint is rare)
- **Vintage key** (Henry Aaron 1969 Auto): 3.0x premium

## What's needed to build the function

1. **More data** — 1 week of dual-source logs will give us 50+ data points
2. **Card categorization** — modern vs vintage, base vs rookie, sport vs TCG
3. **Era tagging** — 1980s, 1990s, 2000s, 2010s, 2020s
4. **Card Hedger high-confidence-only** — filter out D-grade FMVs (anomalies)

## Implementation (when ready)

```
def estimate_psa9_price(psa10_price, card_category, era):
    """Estimate PSA 9 price from PSA 10 price using learned association."""
    base_ratio = CATEGORY_RATIOS[card_category][era]
    confidence_interval = RATIO_STD[card_category][era]
    return psa10_price / base_ratio
```

This becomes a second opinion on the FMV — when CH PSA 9 FMV is far from
the function's estimate, we know something is off (low confidence, wrong card,
anomaly in CH data).

## NOT YET BUILT — this is a future fire

This is on the parking lot. The per-grade alert logic works without it. The
math model would make the alerts smarter, but it's not required.

## Why this is hard

1. **Sports vs TCG have different ratios** — Pokemon cards grade differently than sports
2. **Era matters** — modern cards (2010+) have more PSA 10s, different premium
3. **Rookie vs base** — rookie premiums are different
4. **Subset/parallels** — gold refractor / auto / patch variants have different ratios
5. **Population context** — if PSA 10 pop is 5 vs 5000, the premium ratio is very different

A robust model needs Card Hedger's per-card `category` and `era` fields, plus
GemRate's population data for the population-aware component.

## Trigger conditions

Build the math model when:
- [ ] We have 100+ per-grade data points (currently ~10)
- [ ] Card Hedger per-card metadata (era, category) is mapped in our DB
- [ ] Or: we want to publish "expected ratio" tables for premium tiers
- [ ] Or: a customer asks "what should a PSA 9 of this card cost?"

## Related fires

- **Population data** (GemRate, deferred to 7+ customers): required for the
  population-aware component of the model
- **Per-tier schedule config**: not directly related, separate concern
- **Sell-side z-score**: also depends on cross-grade price relationships

---

Status: **Parking lot item, future fire**
Captured: Sept 18, 2026
Owner: Jonathan (you)
