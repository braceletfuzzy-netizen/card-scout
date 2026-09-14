# TCG Data Sources — Research Notes (Sept 14, 2026)

**Source:** URL dump from Jon during Card Scout V2 planning session.

## TL;DR
Do NOT adopt any of these for V1. Bookmark for V2 only when specific use case emerges.

## What we have today (V1)
- **Sportscardspro + PriceCharting actor** (`PGRtI1ZjuqUELHCGr`) for per-grade ticker data
- **PSA actor** (`DgLihiFRCa1Qf781s`) for population depth
- **eBay actor** for listings (the buy side)
- Cost: ~$7/mo for all 3 of our own actors
- Coverage: Sports cards + TCGs (Black Lotus, Charizard Base Set, etc.)

## The 4 options Jon researched

### 1. TCGplayer Official API
- **Status:** No new API keys granted. Public docs offline for new signups.
- **Verdict:** Dead end. Skip.

### 2. TCGCSV
- **Status:** Public daily CSV dump of TCGplayer data, no auth required.
- **Cost:** Free.
- **Pros:** No platform dependency, daily refresh, community-driven.
- **Cons:** No real-time; no per-grade tier data; daily lag.
- **Verdict:** Skip. We have PriceCharting (real-time, per-grade) already.

### 3. TCGtracking.com/tcgapi
- **Status:** Free REST API mirroring TCGplayer data with edge cache.
- **Coverage:** 62 games, 7M+ SKUs, 51ms response time.
- **Special features:** SKU-level pricing (condition × variant × language), CardTrader integration, **POST /scan for image-to-product matching**.
- **Verdict:** **Bookmark for V2 photo app.** Free + edge-cached + has the /scan endpoint we need for raw card photo identification.

### 4. TCGapi.dev
- **Status:** Paid SaaS starting at $9.99/mo.
- **Pros:** Cleanest API, 54 games, daily refresh, per-condition pricing.
- **Cons:** Per-condition pricing is redundant (we have per-grade via PriceCharting); subscription adds platform risk.
- **Verdict:** Skip for V1. Re-evaluate if we add non-TCG verticals and need one API for many game types.

### 5. Apify TCGplayer Scraper (3rd party)
- **Status:** Paid per-use at $2/1k results.
- **Pros:** Real-time listings, sales history, seller data.
- **Cons:** 3rd-party actor means platform dependency (this is what we built OWN actors to avoid).
- **Verdict:** Skip. We built own eBay + PSA + PriceCharting actors precisely so we don't depend on 3rd parties.

## Decision Matrix

| Source | Add to V1? | Why not |
|---|---|---|
| TCGplayer Official API | ❌ | No new keys |
| TCGCSV | ❌ | Real-time coverage already via PriceCharting |
| TCGtracking.com/tcgapi | ❌ for V1 / **YES for V2 photo app** | Only useful for image → card ID match |
| TCGapi.dev | ❌ | Redundant with our setup; subscription overhead |
| Apify TCGplayer Scraper | ❌ | 3rd-party platform risk |

## When this could change
- **V2 photo app** (Jim's idea from Sept 14): use TCGtracking's `POST /scan` endpoint
- **10+ customers using TCGs**: maybe revisit TCGapi.dev for portfolio tracking at scale
- **Multi-vertical expansion** (coins/comics): check if TCGapi.dev covers non-TCG verticals before subscribing

## URL Reference
- https://tcgtracking.com/tcgapi/  — bookmarked for V2
- https://docs.tcgplayer.com/docs/getting-started  — official, no new keys
- https://www.reddit.com/r/mtgfinance/comments/irico0/using_the_tcgplayer_api_with_python_to_track/  — context only, not actionable
- https://apify.com/devcake/tcgplayer-data-scraper  — 3rd-party, skip
- https://tcgcsv.com/  — free CSV dump, useful for non-realtime reference data
- https://tcgapi.dev/  — paid SaaS, skip until needed
