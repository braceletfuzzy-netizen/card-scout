# Card Scout Architecture Decision Record (ADR-001)

## Subject
Storage vs. Pull decision for sports trading card pricing data

## Status
APPROVED (high-level direction); Pricing bands table pending Jon's sign-off

## Date
2026-09-14

## Context
Jon raised: "when do we store/lookup vs doing a pull, or do we always pull?"
He wants to be future-ready without over-engineering.

## Decision
**Store what we'd ask more than once. Pull what changes daily.**

## Practical Triage

| Data | Decision | Why |
|------|----------|-----|
| Card identity | Store | Same card forever |
| Customer accounts | Store | Of course |
| Snapshot history | Store | Already doing it (Snapshot table) |
| Pricing bands (new) | **Store (implement next)** | Needed for trend charts |
| Deal alert history (Runs table) | Store | Already doing it |
| eBay current listings | Pull | Fresh every alert, expires in hours |
| Sportscardspro prices | Pull (don't store forever) | Refreshing from source is fine |
| Sportscardspro historical chart | **Store (when implemented)** | That's what charts need |
| PSA population | Store, refresh weekly | Slow-changing, expensive to pull every time |
| Raw individual sales | Don't store | Too much data, expires fast |

## Why SQLAlchemy Matters

If we use SQLAlchemy ORM, the migration from SQLite to PostgreSQL to ClickHouse costs:
- SQLite → PostgreSQL: 2 hours, 0 downtime (change DB URL)
- PostgreSQL + add ClickHouse: 1 week planned, 0 downtime if gradual cutover
- Add Meilisearch: 2-3 weeks, 0 downtime

The "rewrite" Jon is worried about does NOT happen because ORM abstracts the engine.
What's actually needed is "data moves to a new engine" — not "code is rewritten."

## Migration Triggers (when to upgrade engine)

| Stage | Cards | Currently | Move to |
|-------|-------|-----------|---------|
| V1 (now) | 12 | SQLite | (stay) |
| 5K customers | 60K | SQLite slow | PostgreSQL |
| 50K customers | 600K | PostgreSQL slow on analytics | ClickHouse |
| 500K customers | 6M | ClickHouse slow on search | + Meilisearch |
| 5M customers | 60M | Same + read replicas | + Postgres read replicas |

## Implementation Plan

### Phase 1: pricing_bands table (RECOMMENDED NEXT)
1. Add schema migration: 10 lines of SQL
2. Add daily capture: 1 cron (or piggyback on alert run)
3. Add TTL cleanup: 1 cron (or piggyback)
4. Add trend chart on Dashboard (V2 work)

### Phase 2: PSA pop storage
1. New `psa_pop_history` table
2. Refresh weekly instead of monthly
3. Track deltas over time

### Phase 3: Sportscardspro chart pull
1. New `price_history` table (30 days)
2. Daily fetch via existing actor (extended to capture chart data)
3. Powers V2 chart panel

### Phase 4: Search index (only if customer demands it)
1. Add Meilisearch instance
2. Index cards by year/brand/player for typo-tolerant search
3. Bridge to existing alert system

## Cost Trajectory

| Scale | Infra cost | Why it's safe |
|-------|-----------|---------------|
| 1K customers | ~$7/mo (current) | Already operating at this |
| 5K customers | ~$80/mo | Adds PostgreSQL, still tiny vs revenue |
| 50K customers | ~$300-500/mo | ClickHouse + proxy tier |
| 500K customers | ~$1-2K/mo | Multi-node ClickHouse + Meilisearch |

At every scale, infra is sub-5% of revenue.

## Why I'm Saying This is "Future-Ready"

The pattern Jon needs:
1. **Pull-what-changes-daily** is the same at every scale (eBay API call is eBay API call)
2. **Store-everything-else** with TTL = 30 days is the same at every scale
3. **Engine choice** changes as scale demands, but ORM abstracts it
4. **Cost grows linearly, not exponentially** — because we always read from source for fresh data

What's NOT future-ready:
- ❌ Storing raw eBay listings forever
- ❌ ClickHouse for 12 cards (overkill)
- ❌ No TTL (unbounded growth)
- ❌ ORM-raw SQL hardcoded (rewrite needed)

## Open Questions
- Should pricing_bands table go in V1 (now) or V2?
- What's the smallest delta Jim needs to see for trend charts? (5%? 10%? 20%?)
- Do we need PSA pop history or just current?

## Recommendation
Build pricing_bands table NOW. It's the smallest step that creates a 30-day memory without over-engineering. ~3 hours of work, then we wait for organic demand to drive further infrastructure.
