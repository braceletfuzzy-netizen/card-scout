# Card Hedger vs SCPro Comparison — Sept 17-18, 2026

## TL;DR

**Keep BOTH vendors.** They measure different things, and the comparison reveals
a richer pricing story than either alone.

- **Card Hedger** = Fair Market Value (FMV), what a card actually sold for recently at PSA 10
- **SCPro (Apify actor)** = Median of active eBay listings (often raw + various grades)
- **Both together** = real-time active listings + reliable FMV reference

The "huge differences" we saw (+5000% etc.) are NOT data quality issues — they're
**measurement artifacts** from comparing two different pricing concepts.

## Methodology

**Setup (Sept 17 evening)**: Added `scripts/cardhedger_alert_integration.py`
that runs Card Hedger FMV lookup in parallel with the existing SCPro search
for every customer card. Both prices logged to `/data/card_hedger_vs_scpro.log`.

**Window**: Sept 17 15:54 → Sept 18 08:41 (~17 hours)
**Entries**: 20 log entries, 18 unique cards
**Customers**: Jim (15 cards) + Alan (3 cards) — Hingle merged into Jim mid-window

**Per-card metrics logged**:
- Card Hedger price (PSA 10 FMV)
- Card Hedger confidence (0-1 numeric)
- Card Hedger grade (A/B/C/D letter)
- Card Hedger source method (card_id direct vs search fallback)
- SCPro median listing price
- SCPro total listings count
- % difference between CH and SC

## The Data (18 unique cards, latest run each)

### Grade A (high confidence, 7 cards)

| Card | CH $ | SC $ | % diff | CH conf |
|---|---:|---:|---:|---:|
| Michael Jordan 1991 Upper Deck | $1,515 | $22.50 | +6,021% | 0.99 |
| Mewtwo Pokemon 151 #150 | $185 | $6 | +2,983% | 1.00 |
| Charizard ex Pokemon 151 #199 | $1,400 | $100 | +1,300% | 1.00 |
| 1989 Topps Ken Griffey Jr. 1 Auto | $287.50 | $64 | +349% | 0.99 |
| Brett Favre Graded Pinnacle 13 | $117.50 | $100 | +18% | 0.99 |
| Mookie Betts Raw 10 Topps US26 | $120 | $165 | -27% | 0.98 |
| 2018 Topps Upton/Ohtani/Trout US158 | $147.50 | $412.50 | -64% | 0.99 |

### Grade B (medium confidence, 2 cards)

| Card | CH $ | SC $ | % diff | CH conf |
|---|---:|---:|---:|---:|
| Pokemon Base Set Charizard Holo | $1,888 | $120 | +1,473% | 0.25 |
| Frank Thomas Topps Draft #1 Pick | $54 | $6 | +479% | 0.38 |

### Grade C (low confidence, 5 cards)

| Card | CH $ | SC $ | % diff | CH conf |
|---|---:|---:|---:|---:|
| Ken Griffey Auto (Hingle's import) | $18,009 | $507.50 | +3,449% | 0.13 |
| Henry Aaron Topps 1969 Auto | $1,697 | $210 | +708% | 0.18 |
| Donruss 87 Bo Jackson | $12.53 | $5 | +151% | 0.19 |
| Portgas D. Ace One Piece OP13-119 | $193 | $135 | +43% | 0.11 |
| Derek Jeter Topps Future Star | $25 | $35 | -29% | 0.19 |

### Grade D (very low confidence, 3 cards)

| Card | CH $ | SC $ | % diff | CH conf |
|---|---:|---:|---:|---:|
| Yancy Thigpen Air Force One | $74.63 | $5 | +1,393% | 0.07 |
| MTG Black Lotus Alpha | $467,071 | $42,000 | +1,012% | 0.04 |
| Bob Griese Graded 28 | $316 | $25.50 | +1,139% | 0.05 |

## Pattern Analysis

### Direction: CH > SC in 14/18 cards (78%)

This is the expected pattern. PSA 10 FMV (CH) is typically much higher than
the median of active listings (SC) because active listings include:
- Raw cards (no grading premium)
- Lower grades (PSA 8, 9, BGS 8.5, etc.)
- Damaged/miscarded examples
- Bulk lots
- "Make offer" listings with inflated BIN

So CH > SC ≠ "CH is wrong". It means CH is showing the **graded premium**
that active listings don't capture.

### The 3 cards where CH < SC (outliers worth investigating)

1. **2018 Topps Upton/Ohtani/Trout US158**: CH $147, SC $412 (CH -64%)
   - SC has a multi-card lot or premium graded example skewing the median up
   - CH shows realistic FMV for a 2018 Topps Update parallel card
   - **Likely SC outlier**, not CH error

2. **Mookie Betts Raw 10 Topps US26**: CH $120, SC $165 (CH -27%)
   - SC median higher than CH FMV — unusual for raw card
   - Possibly the "Raw 10" in the search query is pulling a graded example
   - **Worth manual inspection**

3. **Derek Jeter Topps Future Star**: CH $25, SC $35 (CH -29%)
   - Both low-confidence; SC may be inflated by a BIN listing
   - Small dollar amounts, low signal

### Confidence matters

- **7 cards** with high confidence (≥0.9): reliable FMV
- **11 cards** with low confidence (<0.5): FMV is a guess based on sparse market
  - These are rare cards where recent sale data is limited
  - For low-confidence cards, the SCPro listing median is arguably MORE useful
    (shows what's actually being asked)

## Sept 24 Decision Framework

**Original question**: "Should we keep Card Hedger or SCPro?"

**Answer based on data**: **Keep BOTH**.

Reasoning:
1. **Different measurement** — FMV vs active listings measure different things
2. **Different strengths**:
   - Card Hedger: reliable PSA 10 reference price (when confidence high)
   - SCPro: real-time buy-side opportunity (is this listing a deal?)
3. **Together = better alerts** — when SCPro listing price is significantly below
   CH FMV, that's the actual "deal" signal

**What this changes for the alert pipeline**:
- Current: alert fires on "listing below median" (SCPro only)
- Improved: alert fires on "listing significantly below FMV" (uses both)

**Cost-benefit analysis**:
- Card Hedger: $49/mo Starter ($299/yr annual) — 5,000 req/day, covers us
- SCPro: $0.0033/run × ~150 runs/wk × 4 weeks = ~$2/mo
- Total data cost: $51/mo for **both** = better signal quality

**Recommendation**: **Keep Card Hedger, keep SCPro, use BOTH in alert logic.**

## Implementation Notes for Sept 24+

### Improved alert logic (proposed)

```
For each card, fetch:
  ch_fmv = CardHedger.get_fmv(card_id, grade='PSA 10')  # reliable if confidence >0.7
  sc_listings = SCPro.search(search_query)  # active eBay listings

Compute "deal score":
  if ch_fmv and ch_confidence > 0.7:
    deal_threshold = ch_fmv * 0.85  # 15% below FMV is a deal
    listings_below_threshold = [l for l in sc_listings if l['price'] < deal_threshold]
  else:
    # Low CH confidence - fall back to SCPro relative comparison
    deal_threshold = median(sc_listings) * 0.7  # 30% below median
    listings_below_threshold = [l for l in sc_listings if l['price'] < deal_threshold]

Alert if: listings_below_threshold.length > 0
```

This combines both data sources intelligently based on confidence.

### What we still need

- [ ] Population data (GemRate, deferred to 7+ paying customers)
- [ ] More Card Hedger data to validate Sept 24 decision
- [ ] Better SCPro filtering (drop low-quality listings before median calc)
- [ ] "Sold comps" data — currently broken in SCPro, need eBay Browse API fallback

## Conclusion

**Don't retire either source.** They serve complementary purposes. The dual-source
comparison data is **validating both** rather than showing one is wrong.

Card Hedger's confidence grade (A/B/C/D) is the key signal: high confidence cards
give us reliable FMV, low confidence cards we should trust SCPro's median more.

**Card Hedger is worth $49/mo IF we use both data sources in the alert logic.**
Without the comparison, Card Hedger's data is reference-grade only; combined with
SCPro, it powers the actual "is this a deal?" signal.
