# Sports Card URL Updates — 2026-09-14

## What changed

Updated `sportscardspro_url` for 6 cards in card_scout.db based on URLs from Jim.

| Card | Old URL | New URL | Status |
|------|---------|---------|--------|
| #1 Donruss 87 Bo Jackson | (none) | https://www.sportscardspro.com/game/baseball-cards-1987-donruss-rookies/bo-jackson-14 | ✅ Verified, returns full price data |
| #2 Frank Thomas Topps Draft #1 Pick | (none) | https://www.sportscardspro.com/game/baseball-cards-1990-topps/frank-thomas-414 | ✅ Verified match (1990 Topps #414 = Frank Thomas Rookie) |
| #3 Michael Jordan 1991 Upper Deck Baseball | (none) | https://www.sportscardspro.com/game/baseball-cards-1991-upper-deck/michael-jordan-sp1 | ✅ Verified (Jordan White Sox SP1) |
| #4 Derek Jeter Topps Future Star | (already had 1995 Topps #199 URL) | (no change) | ✅ Already correct |
| #5 Henry Aaron Topps 1969 Autograph | (none) | https://www.sportscardspro.com/game/baseball-cards-1970-topps-super/henry-aaron-24 | ⚠️ Year mismatch — alert says 1969, URL is 1970 |
| #6 Alex Rodriguez Circa Mariners SS | (none) | (no URL from Jim) | ❌ Still missing |
| #7 Yancy Thigpen Air Force One 1996 Collectors Edge | (none) | https://www.sportscardspro.com/game/football-cards-1996-collector%27s-edge-president%27s-reserve-air-force-one/yancey-thigpen-30?q=yancy+thigpen+air+force+one | ✅ URL works, but card has no recorded prices (rare insert) |
| #8 Barry Sanders Stadium Club Super Chrome 1997 | (none) | https://www.sportscardspro.com/game/football-cards-1998-stadium-club/barry-sanders-first-day-issue-1 | ⚠️ Year mismatch — alert says 1997 Super Chrome, URL is 1998 Stadium Club First Day Issue |

## Outstanding items (need Jim's confirmation)

### 1. Card #5 Henry Aaron — year mismatch
- Alert name says: "Topps 1969 Autograph"
- URL provided: 1970 Topps Super #24
- These are different cards. Either:
  - (a) Update alert name to "1970 Topps Super" (URL is what Jim wants)
  - (b) Ask Jim for the actual 1969 Topps card URL
- Bot will work either way, but data + alert name should match.

### 2. Card #6 Alex Rodriguez — no URL provided
- Not in the batch Jim sent.
- Alert will continue running with eBay data only (no per-grade ticker).
- Need from Jim: search sportscardspro.com for "Alex Rodriguez 1996 Circa Mariners" → paste URL.

### 3. Card #8 Barry Sanders — year mismatch
- Alert name says: "Stadium Club Super Chrome 1997"
- URL provided: 1998 Stadium Club First Day Issue #1
- These are different products. The URL is a 1998 First Day Issue card (limited to /200).
- Either:
  - (a) Update alert name to "1998 Stadium Club First Day Issue" (URL is what Jim wants)
  - (b) Ask Jim for the actual 1997 Stadium Club Super Chrome URL

## Verification

Tested the actor on 2 cards:
- **#1 Bo Jackson**: Returns full price data including 6 tiers (ungraded, psa_7, psa_8, psa_9, psa_9_5, psa_10). 10 sales rows + 19 sold counts. ✅
- **#7 Yancy Thigpen**: URL works (correct title returned), but 0 prices/sales (rare insert card, no recorded sales on sportscardspro). Alert will still run with eBay data only. ✅
