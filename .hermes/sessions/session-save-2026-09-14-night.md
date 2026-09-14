# Session Save — Sept 14, 2026 (Night)

**Saved by**: Hugo
**Type**: Session-end save after major strategic session
**Today's partner agents**: Cosmo (orchestration, handoff pickup earlier)

## What This Session Accomplished

This was a **strategic + infrastructure session**. Three big things happened:

### 1. Project Migration (COMPLETED, commits 868377f + vostok-tools commit)

Card Scout was extracted from vostok-tools into its own project repo:
- 33 files moved to `C:\Users\J\Documents\LLM\card-scout\`
- 4 hardcoded paths updated (scripts now point to card-scout/)
- Actor republished as build 0.4.11 from new location
- Bot verified working end-to-end (Bo Jackson card #1: 30 items, 42s)
- Cosmo's own workspace created at `C:\Users\J\Documents\LLM\cosmo\`
- Top-level READMEs written for: card-scout/, cosmo/, hugo/ (updated)
- vostok-tools got migration banner

### 2. P0 Bug Fix (commit 1f3e87a) — Earlier in Session

Cosmo caught on a 12-card live test: all 8 sports cards had `include_sold=1`
in the DB, which triggered broken actor code path (200s timeout, 0 items).
One SQL statement (`UPDATE cards SET include_sold = 0 WHERE include_sold = 1`)
fixed it. Verified: Bo Jackson now returns 30 items in 31s.

### 3. Master Strategy Captured (commits 757e134, 3a1f7a9, 70fa20c, 026aee2)

User articulated the actual business thesis (verbatim):
> "Each market (cards, coins, comicbooks etc) are markets that we can attach
> this framework to, and lower the spread between the buy and ask price.
> I am not trying to solely do one market, the end goal is to do markets
> with wide pricing bands due to information/geographical dislocation/ etc
> asymmetries that people trade."

This is the FIRST time this has been written down. Captured in 4 places:

1. **Master strategy doc**: `card-scout/For You/Plans/MASTER-STRATEGY-collectibles-asymmetry-framework-2026-09-14.md`
2. **Cosmo's README**: ⚠️ banner near top telling him to read it
3. **Card Scout README**: reference near top
4. **Hugo's README**: multi-vertical build pattern

## Final State

### Repos
- **card-scout/** — Own git repo, 5 commits today (migration, plan, hard policy, multi-vertical, master strategy)
- **vostok-tools/** — Back to original focus (watches), migration commit today
- **hugo/** — Hugo's actor workspace, working notes updated
- **cosmo/** — NEW, parallel to hugo/

### Docs (in card-scout/For You/Plans/)
- card-scout-ticker-system-spec-2026-09-14.md (master spec, 11.4KB)
- self-host-migration-and-store-revenue-plan-2026-09-14.md (17.3KB)
- MASTER-STRATEGY-collectibles-asymmetry-framework-2026-09-14.md (11.2KB) ← **NEW**
- hugo-handoff-empty-title-bug-2026-09-14.md (SUPERSEDED)
- hugo-handoff-empty-title-bug-2026-09-14-RESOLVED.md
- hugo-handoff-includesold-broken-2026-09-14.md (SUPERSEDED)
- hugo-handoff-includesold-broken-2026-09-14-RESOLVED.md
- hugo-handoff-psa-sold-2026-09-13.md (SUPERSEDED)
- hugo-handoff-psa-sold-2026-09-13-RESOLVED.md
- card-scout-graded-focus-spec-2026-09-14.md (SUPERSEDED)
- handoff-cost-reconciliation-2026-09-14.md
- card-scout-elevator-pitches.md

### The Strategic Frame (canonical)

**Card Scout = vertical #1 of a multi-vertical collectibles asymmetry framework.**

The business is NOT "card tool." The business IS "narrow the bid-ask spread
for buyers in markets where they don't know fair prices." Cards is the first
market. Coins, comics, toys, watches, vinyl = future verticals.

**The 5 layers of the stack** (with competitive moat per layer):

| Layer | Reusable? | Our moat | Time to clone |
|---|---|---|---|
| 1. Scrapers (data) | Per-vertical code | 6mo R&D | 6mo (or instant if leaked) |
| 2. Statistical engine (math) | Across verticals | 90% CI math | 1 weekend |
| 3. Alert bot (orchestration) | Fully reusable | The flow | 1 week |
| 4. Ticker format (presentation) | Across verticals | Bloomberg-style | 1 week |
| 5. Customer relationships | Across verticals | Multi-vertical credibility | **18-24mo** |

**The real moat is Layer 5.** A competitor cloning scrapers (Layer 1) still
needs 18-24mo to build layers 2-5 across 3+ verticals.

### The Hard Policy (Card Scout actors stay PRIVATE)

User-confirmed rule (2026-09-14 evening):
- ❌ AtQq66Qn8FB7aLq2l (eBay actor) — NEVER publish
- ❌ DgLihiFRCa1Qf781s (PSA actor) — NEVER publish
- ❌ PGRtI1ZjuqUELHCGr (sportscardspro actor) — NEVER publish
- ✅ May publish: generic framework parts (HTTP fetcher, math, formatter)

**When to revisit publishing**: 10+ customers in a vertical, OR 3+ verticals
live (so the framework itself is the moat).

### Cost State

- Our 3 actors cost $6.97/mo (Card Scout only)
- 4 orphan actors cost $94.48/mo (NOT ours — billing dispute)
- Total cycle: $115.67 vs $100 budget cap → $15.67 over
- Decision: stay on Apify ($7/mo is fine); revisit at $30/mo Apify spend
- Self-host migration plan documented for when scale demands it

## P0 Status

- ✅ P0-HUGO-EMPTY-TITLE — RESOLVED
- ✅ P0-HUGO-ACTOR-QUERY-CONFLICT — RESOLVED
- ✅ P0-HUGO-INCLUDESOLD-BROKEN — RESOLVED
- ✅ P0-HUGO-PSA-SOLD — RESOLVED
- ✅ MIGRATION-VOSTOK-TO-CARD-SCOUT — COMPLETED

All P0 closed.

## What's Open (Non-Blocking)

1. **Card Scout customer #2 onboarding** — code is ready, repo is ready
2. **Apify billing dispute** — recover $94.48 from orphan actors (4th party actors)
3. **Document framework's generic parts** — preparation for future Coin Scout
4. **10+ customer trigger** — revisit publishing strategy
5. **Self-host migration** — at $30/mo Apify spend
6. **Coin Scout scoping** — at 25-50 customers

## Critical Cross-Agent Context (Cosmo MUST Read)

When you (Cosmo) start your next session:

1. **Read master strategy doc FIRST**: `card-scout/For You/Plans/MASTER-STRATEGY-collectibles-asymmetry-framework-2026-09-14.md`
2. **Your README has ⚠️ banner** telling you to read master strategy
3. **Hugo's role**: heavy code (parsers, math, formatters, actor main.js)
4. **Your role**: specs, customer flow, DB queries, bug discovery, handoff docs
5. **Card Scout actors stay PRIVATE** (hard policy)
6. **All 12 cards now alert correctly** (8 sports + 4 TCG, after DB fix)

## Commits Today (card-scout/ repo)

```
026aee2  HUGO: Master strategy captured — multi-vertical collectibles asymmetry framework
70fa20c  HUGO: Multi-vertical framework strategy documented
3a1f7a9  HUGO: Apply HARD POLICY — Card Scout actors NEVER published to Apify Store
757e134  HUGO: Self-host migration plan + Apify Store revenue strategy
868377f  Initial commit: Card Scout V1 migrated from vostok-tools.
```

Plus 1 commit to vostok-tools for the migration (extraction).

## Files Hugo Touched This Session

- card-scout/For You/Plans/MASTER-STRATEGY-collectibles-asymmetry-framework-2026-09-14.md (NEW, 11.2KB)
- card-scout/For You/Plans/self-host-migration-and-store-revenue-plan-2026-09-14.md (NEW + updated, 17.3KB)
- card-scout/For You/Plans/card-scout-ticker-system-spec-2026-09-14.md (Strategic Framework section appended)
- card-scout/README.md (master strategy reference)
- card-scout/scripts/README.md (paths updated)
- card-scout/actors/README.md (paths updated)
- card-scout/scripts/discord_alert_bot_v3.py (BD_TOKEN_PATH)
- card-scout/scripts/psa_pop_lookup.py (bd_path)
- card-scout/scripts/sportscardspro_lookup.py (APIFY_TOKEN + BD_TOKEN)
- card-scout/card_scout.db (DB include_sold fix, commit 1f3e87a was earlier)
- vostok-tools/README.md (migration banner)
- hugo/README.md (multi-vertical build pattern)
- hugo/working-notes.md (Sessions 9-13 appended, 49.4KB total)
- hugo/HUGO_HANDOFF.md (paths updated post-migration)
- C:\Users\J\Documents\LLM\cosmo\README.md (⚠️ master strategy banner)

## Decision Triggers (From Master Strategy)

| Trigger | Action |
|---|---|
| 1 customer (Jim) | Focus on Card Scout. Don't expand yet. |
| 5 customers | Start documenting framework's generic parts |
| 10 customers | Consider publishing generic framework parts |
| 25 customers (1-2 verticals) | Consider scoping Coin Scout |
| 50 customers | Begin building Coin Scout (~50h dev) |
| 100 customers (2-3 verticals) | Publish framework as commercial product |

## Next Steps (For User to Choose)

1. Onboard customer #2 (Card Scout V1 is ready)
2. File Apify billing dispute for $94.48 (orphan actor charges)
3. Take a break — this was a massive session

## Next Steps (For Cosmo)

1. Read master strategy doc
2. Update your session-save to reference the master strategy
3. Continue with normal Card Scout work (customer flow, onboarding scripts)

## Next Steps (For Hugo)

1. Wait for next user request
2. If asked: help Cosmo with any orchestration handoff
3. If asked: prepare framework documentation for Coin Scout (50h dev)
4. If asked: implement publish-able generic parts (HTTP fetcher, math, formatter)
