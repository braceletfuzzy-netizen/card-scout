# PSA Pop Data — Long-Term Plan

## Time
Sept 16, 2026 (morning)

## Status
**DRAFTED.** Founder's direction: build our own PSA pop API.

## Founder's directive (verbatim)

> "We will eventually create our own since we have the time and
> infrastructure to do this."

In response to a Reddit post about a third-party PSA pop API. Decision:
**don't depend on third-party APIs, build our own.**

## Current state

We have:
- ✅ Apify PSA actor (Hugo's own, `DgLihiFRCa1Qf781s`) — works but slow (~30-60s/run)
- ✅ 2/12 Jim cards have real pop data (Bo Jackson synthetic, Hank Aaron real)
- ✅ DB schema with 4 PSA pop columns
- ✅ Stock-class ticker renderer live

We don't have:
- ❌ Reliable way to find PSA spec_ids (the long blocker)
- ❌ Search-by-name capability (actor only supports setUrl or certNumber)
- ❌ Bulk historical pop data
- ❌ Pop velocity tracking (when did PSA 10 pop last grow?)

## Why we won't use third-party APIs

| Third-party API | Problem |
|---|---|
| Reddit-promoted API (lulzasaur9192) | 50 req/month free tier (useless), possibly dead, hostile marketing |
| PSA official API | "Recently dropped their free API" — paid plans expensive (per Reddit comment) |
| RapidAPI marketplace | No quality control, listings come and go |

## Long-term approach: build our own

### Phase 1: PSA Set Registry scraping (1-2 weeks)

**Approach**: Build our own actor that:
1. Searches PSA's set registry by player/year/brand
2. Extracts spec_id from search results
3. Navigates to the spec_id page
4. Extracts full pop data (PSA 1-10 + qualifiers)
5. Returns structured JSON

**Tech stack**:
- Puppeteer (we already use it for login)
- Bright Data web_unlocker1 (handles CF)
- Cloudflare workers for caching

**Cost estimate**:
- Dev: ~20 hours of build time
- Runtime: $0.005-0.013 per card lookup (BD proxy + compute)
- At 100 customers × 12 cards each = 1,200 lookups = ~$15 to populate

### Phase 2: Pop history tracking (1 week)

**Approach**: Track pop data over time per card.
- DB schema: `psa_pop_history(card_id, fetched_at, psa_10_pop, psa_9_pop, ...)`
- Daily cron to refresh top N cards
- Detect pop velocity (rate of new PSA 10s per month)

**Value**: Pop velocity = "are PSA 10s of this card getting rarer or more common?"
- Rarer = price tends to go UP
- More common = price tends to go DOWN

### Phase 3: API for ourselves (and customers?) (1 week)

**Approach**: Wrap our pop lookup into a clean REST API.
- `GET /v1/pop/{set_url}` → returns full pop breakdown
- `GET /v1/pop/search?q={query}` → returns matching sets

Could be:
- Internal only (use in our bot/dashboard)
- External (charge for API access — third revenue stream?)

## Short-term fixes (do now)

### 1. Manual PSA URL entry via dashboard (15 min)

Add a "PSA set URL" field to the dashboard's edit-card form. Founder pastes URL from PSA.com after browsing.

**Why first**: 
- 100% accurate (humans are source of truth)
- Zero engineering risk
- Sets up Phase 1 by collecting correct URLs as users add cards

### 2. Build a small web search helper (1 hour)

Even though our test showed it's unreliable, **some** searches do work. Build a helper that:
- Searches for the card
- Returns top 3 PSA URLs
- Founder reviews and picks correct one (or rejects all)

### 3. PSA Set Registry via Playwright (2-3 hours)

When Phase 1 is needed, build it incrementally:
- Start with the easiest cards (popular baseball, recent years)
- Verify accuracy
- Scale up

## Timeline

| Phase | Effort | When |
|---|---|---|
| Manual URL entry via dashboard | 15 min | This week |
| Web search helper | 1 hour | When convenient |
| Our own PSA search actor (Phase 1) | 20 hours | When 5+ customers + paid |
| Pop history tracking (Phase 2) | 1 week | After Phase 1 |
| Public API (Phase 3) | 1 week | After Phase 2 |

## Cost projections (Phase 1)

| Scale | Cards | Lookups/mo | Cost |
|---|---|---|---|
| 1 customer (Jim, current) | 12 | 12 | $0.16/mo |
| 10 customers | 120 | 120 | $1.56/mo |
| 50 customers | 600 | 600 | $7.80/mo |
| 100 customers | 1,200 | 1,200 | $15.60/mo |

Sustainable. Build when customer count justifies.

## Decisions captured

1. ✅ Build our own PSA pop data — no third-party APIs
2. ✅ Apify actor stays as fallback
3. ✅ Manual URL entry as short-term solution
4. ⏸️ Phase 1 PSA search actor: when 5+ customers
5. ⏸️ Phase 2 pop history: after Phase 1
6. ⏸️ Phase 3 public API: after Phase 2

## Why this matters

This isn't a coding decision — it's a **strategic decision** that affects:
- Cost structure (we control, not a vendor)
- Reliability (we own uptime)
- Data integrity (no third-party edits/deletes)
- Competitive moat (proprietary data source)

If Card Scout becomes a real business, owning our own PSA pop data layer is a **moat**. Vendors can change pricing, kill free tiers, go bankrupt. We can't be at that risk.

## References

- Apify PSA actor (current): `DgLihiFRCa1Qf781s` v1.0 — Hugo's own
- PSA URL structure: `/pop/{category}/{year}/{brand}/{spec_id}` (spec_id is internal)
- Reddit post (read but NOT followed): `/r/sportscards/comments/1rzctbx/...`
- Note from comment: "PSA recently dropped their free API"
