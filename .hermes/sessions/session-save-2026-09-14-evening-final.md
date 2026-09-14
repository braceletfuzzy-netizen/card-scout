# Session Save — Sept 14, 2026 (Evening)

## What We Did Today

### Major Discoveries (After Hugo's Restructure)

1. **Card Scout moved to its own repo**: `C:/Users/J/Documents/LLM/card-scout/`
   - All specs, handoff docs, module READMEs migrated there
   - Git history preserved at vostok-tools side
   - Hugo also fixed the DB include_sold bug at commit `1f3e87a` (8 sports cards: 1→0)

2. **Master Strategy doc exists** (NEW): `For You/Plans/MASTER-STRATEGY-collectibles-asymmetry-framework-2026-09-14.md`
   - Card Scout = vertical #1 of multi-vertical framework
   - Future verticals: coins, comics, vintage toys, watches, stamps, vinyl, wine
   - Real moat = customer relationships across verticals
   - **HARD RULE: Never publish card-domain actors to Apify Store**

3. **Self-host + Apify Store plan exists**: `For You/Plans/self-host-migration-and-store-revenue-plan-2026-09-14.md`
   - Self-host triggers at $70/mo Apify spend (10+ customers)
   - If we want store revenue, build NEW general-domain actors (not card ones)

4. **Cost Reconciliation**: `For You/Plans/handoff-cost-reconciliation-2026-09-14.md`
   - Real Apify data: eBay actor $0.0353/run, PSA $0.0114/run, Sportscardspro $0.0033/run
   - Per card per run: ~$0.05 (with PSA pop) or ~$0.04 (without)
   - Bot's `run_history.apify_cost` is **always NULL** — never recorded
   - Fixed at DB level for all 8 sports cards

5. **Customer #2 not yet in DB** (Hugo's session said "ready" but DB shows 1 customer)

## Files For Hugo To Pick Up Tomorrow

### ACTIVE
- `For You/Plans/card-scout-ticker-system-spec-2026-09-14.md` (11.4KB, V1 implemented)
- `For You/Plans/MASTER-STRATEGY-collectibles-asymmetry-framework-2026-09-14.md` (11.2KB, LOCKED)
- `For You/Plans/handoff-cost-reconciliation-2026-09-14.md` (4.7KB, NEW)
- `For You/Plans/self-host-migration-and-store-revenue-plan-2026-09-14.md` (17.3KB)

### SUPERSEDED (don't implement)
- `For You/Plans/card-scout-graded-focus-spec-2026-09-14.md`

### RESOLVED (read for context)
- `For You/Plans/hugo-handoff-empty-title-bug-2026-09-14-RESOLVED.md`
- `For You/Plans/hugo-handoff-includesold-broken-2026-09-14-RESOLVED.md`
- `For You/Plans/hugo-handoff-psa-sold-2026-09-13-RESOLVED.md`

### Originals (for archival, not implementation)
- `For You/Plans/hugo-handoff-empty-title-bug-2026-09-14.md`
- `For You/Plans/hugo-handoff-includesold-broken-2026-09-14.md`
- `For You/Plans/hugo-handoff-psa-sold-2026-09-13.md`

## Reading Order For Future Cosmo (Per README-First Rule)

1. `README.md` (top-level) — orient to project
2. `MASTER-STRATEGY-collectibles-asymmetry-framework-2026-09-14.md` — the WHY
3. `scripts/README.md` — the HOW (bot code)
4. `card-scout-ticker-system-spec-2026-09-14.md` — the WHAT (V1)
5. Module READMEs (grade_detector, grade_range_calculator, ticker_formatter)
6. THEN read `discord_alert_bot_v3.py`

## Priority Tasks (from today's discussion)

### P0 — Today's Verifications
1. ❓ Cron ID verification (still says "UNVERIFIED" in README)
2. ❓ Run full 12-card live test (only 1/8 sports verified by Hugo)
3. ❓ Verify cron path points to NEW repo location

### P1 — Next 2-3 days
4. Onboard customer #2 (form → DB → webhook)
5. Add `apify_cost` recording to bot (Hugo — heavy lifting)
6. Set $30/mo spending cap in Apify console (user action)
7. Set `include_pop=False` by default to save $0.0114/run

### P2 — Next 1-2 weeks
8. Build Form 2 (Update Existing Customer)
9. Wire grade filter checkboxes to bot
10. Stripe LIVE mode + rename to "Card Scout Pro"
11. SMTP setup for welcome emails

### P3 — Next Month
12. Reddit warm-up + first post
13. Beckett (BGS) pop actor
14. SQLAlchemy → Supabase migration (at 10 customers)

### DEFERRED (Future)
- Self-host migration (at $70/mo Apify spend, 10+ customers)
- Build NEW general-domain actors for Apify Store (NEVER publish card actors)
- Mega Deluxe tier (advisor mode)
- Market maker mode

## Key Numbers To Remember

| Item | Value | Source |
|---|---|---|
| Per-card cost (no PSA) | $0.0386 | Apify usage data |
| Per-card cost (with PSA) | $0.0500 | Apify usage data |
| Per-customer MWF (12 cards) | $7.20/mo | Calculation |
| Per-customer daily (12 cards) | $18/mo | Calculation |
| Per-customer daily (20 cards) | $30-42/mo | Calculation |
| Free BD tier | 5K req/mo | Bright Data |
| Current customers | 1 (Jim) | DB query |
| Current cards | 12 | DB query |
| All 8 sports cards | include_sold=0 (was 1) | DB fix commit 1f3e87a |
| Bot version | v4.286 (v4 latest) | Git log |

## Roles (LOCKED)

**Cosmo**: specs, customer flow, DB queries, bug discovery + handoff docs, light config
**Hugo**: actor code, parser updates, grade detection logic, statistical math, output formatter, cost recording
**User**: vision, decisions, business model, Stripe + Apify console actions

## Critical Context For Future Sessions

1. **Always read MASTER-STRATEGY first** — Card Scout is vertical #1, not the whole business
2. **NEVER publish card-domain actors to Apify Store** — leaks our moat
3. **Always include cost recording in actor call writes** — currently NULL in run_history
4. **Cost is real money** — at $50/mo per customer × 100 customers = $5K/mo revenue, but $1.8-2.5K/mo Apify cost
5. **MWF cadence is best margin** (~$7/mo per customer) vs daily (~$18/mo)

## What Changed Since Last Session Save (Hugo's late session)

| Item | Last Save (Hugo) | Now |
|---|---|---|
| Customer #2 | "Ready" | NOT in DB yet |
| Live 12-card test | "Only card #1 verified" | Same (still need verification) |
| Master Strategy | Not mentioned | **NEW: 11.2KB doc, framework strategy** |
| Self-host plan | Not mentioned | **NEW: 17.3KB doc** |
| Cost reconciliation | Estimate only | **NEW: Real Apify data** |
| Cron status | Unverified | Still unverified |
| Bot DB state | 12 cards, all working | Same (DB fix verified) |

## Status

**V1 SHIPPED. Framework strategy locked. Cost data captured. Customer #2 pending.**
