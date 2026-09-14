# Session Save - Sept 14, 2026 (Evening Session)

## Time
Sept 14, 2026 ~21:50 CDT (UTC-5)

## What we did this session

### 1. Card URL mass-update from Jim
Jim sent 7 sportscardspro URLs from his Discord for sports cards.
Updated DB for cards 1, 2, 3, 5, 6, 7, 8 (A-Rod URL arrived last).

3 follow-ups still open (not blockers):
- Card #5 Henry Aaron: URL is 1970 Topps Super, alert says "1969 Autograph"
- Card #8 Barry Sanders: URL is 1998 Stadium Club First Day Issue, alert says "1997 Super Chrome"
- Card #6 A-Rod URL provided later (1997 Circa #100) - already updated + flagged market_thin

### 2. market_thin flag (Jim's thin market framing)
Jim's insight (verbatim from session):
"When Jim has the only graded card in existence, he charges $300.
He has the only one in the graded space. Population/grade counting is so important.
All cards start raw. Photo app. Card Scout = ticker for graded market + raw average.
Keeps liability off us."

Implementation:
- Added `cards.market_thin` column (INTEGER, default 0)
- Added field to Card model
- format_deal_alert() takes market_thin parameter
- Card #7 Thigpen flagged market_thin=1
- Card #6 A-Rod Circa flagged market_thin=1 (got URL last)
- Thin-market alert: shows raw listings (no % claim) + 90% CI ticker + disclaimer

### 3. SECURITY INCIDENT (caught, fixed)
Commit 1f3e87a accidentally committed config/gcp-service-account.json
with a GCP service account private key.

**Caught in ~30 seconds** before any push to a remote:
- Soft-reset the bad commit (c1d215f)
- Moved SA to C:\Users\J\.secrets\card-scout\gcp-service-account.json
- Added explicit .gitignore (config/gcp-service-account.json)
- Updated customer_onboarding_v2.py to use safe path with env var override
- Doc: card-scout/For You/Plans/security-incident-gcp-sa-leaked-2026-09-14.md
- **User must rotate key in Cloud Console (recommended, 3-min task)**

### 4. Sportscardspro Snipe tool reviewed
Jim pointed us to https://www.sportscardspro.com/snipe?category=baseball-cards
- Validates market exists for our product
- Not a direct competitor (different scope: generic vs Jim-specific)
- Useful V2 borrowing: midnight-10am ET timing, savings thresholds

### 5. V2 specs parked (not implementing now)
Per Jon + Jim Sept 14 discussion:
**grade-tiered listing filter**:
- eBay returns $1 junk listings (bulk lots, $1 BIN with $50 shipping)
- For grade 7-8: only show auctions <1-2h remaining OR BIN that "represents opportunity"
- SKIP for V1. Implement in V2 after proving core value.
- Doc: card-scout/For You/Plans/v2-grade-tiered-listing-filter-2026-09-14.md

### 6. TCG data sources research (parked)
Jon sent URL list of 4 TCG data sources. Review findings:
- TCGplayer Official API: dead end (no new keys)
- TCGCSV: redundant with PriceCharting
- TCGtracking.com/tcgapi: **BOOKMARK for V2 photo app** (POST /scan endpoint!)
- TCGapi.dev: paid subscription, redundant
- Apify TCGplayer Scraper: 3rd-party, skip per our avoidance policy
- Doc: card-scout/For You/Research/tcg-data-sources-research-2026-09-14.md

## Card Scout git state today
Commits (chronological today):
1. 868377f - Initial commit (Card Scout migrated from vostok-tools)
2. 757e134 - Self-host migration plan
3. 3a1f7a9 - HARD POLICY (Card Scout actors NEVER published)
4. 70fa20c - Multi-vertical framework strategy
5. 026aee2 - Master strategy captured
6. e069d30 - Session-save for Sept 14 night
7. 0a85de6 - Apify billing dispute prep
8. 51d32fb - Update dispute path per Apify support response
9. 38f77f9 - Sportscardspro URLs for 6 sports cards
10. c1d215f - market_thin feature (REVERTED — leaked GCP)
11. a6e9a90 - market_thin recommitted cleanly
12. 58526df - customer_onboarding_v2 path fix + security incident doc
13. b0e495d - A-Rod URL + market_thin flag
14. 3f7cd0f - V2 spec for grade-tiered listing filter
15. 423c1c8 - TCG data sources research

## DB state
- 12 cards: 8 sports, 4 TCG
- All 8 sports cards now have sportscardspro_url
- 2 cards flagged market_thin: #6 (A-Rod), #7 (Thigpen)
- All include_sold=0 (after Sept 14 DB fix in earlier session)

## Memory entries updated
- "PROJECTS + SECURITY (Sept 14)" - merged existing entries
- "JIM'S PRODUCT FRAMING (Sept 14, thin markets)" - new

## What NOT to do at session start next time
- **GCP key rotation**: user must rotate in Cloud Console (recommended)
- **Skip year mismatches for now**: Henry Aaron + Barry Sanders alerts work, just slight name mismatch with URL
- **Don't pursue TCG data subscriptions**: keep own-actor architecture

## Standing items (waiting for user)
1. Rotate GCP SA key (HIGH priority, 3 min)
2. Customer #2 onboarding (whenever ready)
3. Apify compensation response (2-3 business days)
4. V2 photo app discussion (separate session when ready)
5. V2 grade-tiered listing filter (separate session)

## Final state
- 2 repos: card-scout/ (own git), vostok-tools/ (watch-only)
- 3 actor builds: PSA, sportscardspro, eBay (all owned by us, NEVER publish)
- 7 V2 specs/docs parked in `For You/Plans/` + `For You/Research/`
- Master strategy: card-scout/For You/Plans/MASTER-STRATEGY-collectibles-asymmetry-framework-2026-09-14.md
