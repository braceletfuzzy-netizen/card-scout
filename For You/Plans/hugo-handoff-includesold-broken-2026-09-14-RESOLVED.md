# Hugo Handoff: includeSold=True Bug — RESOLVED (Sept 14)

**Status**: ✅ DONE (commit `6b1d454`)
**Decision**: Option B (per Cosmo's recommendation + ticker spec reframe)

## What was the bug

The eBay+Etsy actor's `includeSold=True` mode returns empty placeholder (1 item, $0).
- Manual reproduction: `includeSold=False` → 60 items in ~60s ✅
- Same query with `includeSold=True` → 1 empty item in 198s ❌
- Actor log shows: `[SKIP] Derek Jeter Topps Future Star returned empty/short (0 bytes)`
- Root cause: BD returning 0-byte responses for LH_Sold=1 endpoint (rate-limited/blocked)

## Resolution

**Per ticker spec reframe** (commit b4c2cec → f0654da):
- Card Scout = Bloomberg Terminal, SHOW prices, don't recommend
- Sold data already comes from sportscardspro+pricecharting actor (PGRtI1ZjuqUELHCGr)
- eBay sold scraping was for legacy "buy/sell spread" math — REMOVED from V1 scope

**What I changed**:
1. Dropped the conditional eBay sold search block in `discord_alert_bot_v3.py` (lines 561-577)
2. Bot still gets sold data via `lookup_sportscardspro()` which uses sportscardspro+pricecharting actor
3. Saved ~200s latency per card (no more waiting for broken BD response)
4. Sold section in alert still renders from sportscardspro's per-grade prices

**Why this is correct per the spec**:
- The spec says "Customer asks 'what's a deal?' → ticker shows current prices per grade → customer decides"
- Per-grade prices from sportscardspro are MORE accurate than eBay's sold listings (aggregator vs marketplace)
- Removing eBay's sold parsing eliminates a maintenance burden (no more eBay HTML drift)
- Sportscardspro includes historical sales → already gives us trend signal

## Verified

End-to-end test on card #4 (Jeter) and #12 (Base Set Charizard):
- eBay active search: 30 items in 31s ✅ (clean and fast)
- Sportscardspro: real per-grade ticker data
- Alert renders: PSA 10 / BGS 10, PSA 9, ..., Raw (Ungraded) per-grade table
- 90% CI shown for grades with enough sold data
- No more "includeSold broken" issue

## V1 alert output (per ticker spec)

For example, Charizard #4:
```
🎯 Deal Alert: Pokemon Base Set Charizard Holo
Found 13 listings below median ($5)

📊 Market Shape (Q Bands)
Q1 $1 → Median $5 → Q3 $290 | Range $1-$525

📊 Per-Grade Market Values (ticker)
PSA 10 / BGS 10: $12,062.20 (30 sold/30d)
PSA 9.5 / BGS 9.5: $7,264.29
PSA 9: $2,850.00
PSA 8: $1,350.26
PSA 7: $737.37
Raw (Ungraded): $374.60 (typical $226.76-$628.54) (59 sold/30d)

🎯 Below-Market Deals (13 found)
**$1** raw vs typical $227-$629 (100% off) [link]

💰 $1 (80% below median)
[Charizard Charmander...](https://ebay.com/itm/156780094465)
```

Customer sees the market state and decides — no profit math, no "should I buy".

## Files changed

- `scripts/discord_alert_bot_v3.py` — removed broken eBay sold search
- (No actor changes needed — bug persists but we don't use that code path)

## Future work (out of V1 scope)

If user wants eBay sold eventually:
- Could re-enable by fixing actor parser
- Or use a different actor (not blocking V1)
