# Card Scout Working Notes (Updated Sept 24, 2026 evening)

## Time
Sept 24, 2026 (evening)

## Session cadence
**Daily sessions** (confirmed Sept 16, founder preference)

## Timezone
CDT (UTC-05:00)

## Privacy rules
- NEVER share customer webhooks in plain text outside this repo
- NEVER share GCP SA key (use `C:\Users\J\.secrets\<project>\`)
- NEVER publish Card Scout's 3 actors to Apify Store
- **NEVER volunteer competitor intel to vendors** (per Sept 17 GemRate inquiry guidance)

## Current state (Sept 24, 2026 evening)

### CardScout 2.0 — MLB Analytics Platform
Built comprehensive analytics system at `C:\Users\J\Documents\LLM\cardscout-2.0\`

### Daily Automation
| Time | Task | Method |
|---|---|---|
| 8:00 AM | News feed scan (10 RSS feeds) | Windows Task Scheduler (`CardScout_News_Scan`) |
| 9:00 AM | Playoff tracker + hero moment detection | Windows Task Scheduler (`CardScout_Playoff_Tracker`) |

Both configured with `WakeToRun=true` and `StartWhenAvailable=true`.

### Pricing Model (New)
| Product | Price | Description |
|---|---|---|
| Single Sport | $30/mo | Weekly scouting report |
| All Sports Bundle | $75/mo | 25% discount |
| Alpha Signals (max 50) | $199/mo | Real-time Discord alerts |

### Business Strategy
- **Layer 1 (Free):** Track 5 players, basic FMV
- **Layer 2 ($30/mo):** Weekly scouting report with top 10 buys, 5 sells, HOF projections
- **Layer 3 ($199/mo):** Real-time buy/sell alerts with exact entry/exit prices

**Key insight:** Give away the framework (divergence thresholds, HOF appreciation theory), keep the execution (exact prices, real-time timing).

### Model v2.1 — Key Changes from v1.0
- Vintage HOF (25+ years since induction) = 8x floor multiplier
- Iconic players (top-50 all-time) = 2.5x premium
- Floor appreciation rates: Vintage 20%, Retired 15%, Active HOF 10%, Young 8%
- Ken Griffey Jr. floor: $3,185 (was $956) — BUY signal
- Randy Johnson floor: $4,346 — STRONG_BUY at $250 CH
- Methodology stripped from public reports ("black box" approach)

### Key Files
| File | Purpose |
|---|---|
| `src/fmv_proprietary_v2.py` | FMV model (run on-demand) |
| `src/price_cache.py` | On-demand HLOC/Sharpe/volatility |
| `src/news_feed_aggregator.py` | Daily RSS news scan |
| `src/playoff_tracker.py` | Daily playoff hero detection |
| `src/scouting_report.py` | Weekly PDF report |
| `CHANGELOG.md` | Model version history |
| `README.md` | Full project documentation |

### Data Sources
- Card Hedge API: `C:\Users\J\.secrets\card-scout\card-hedger-api-key.txt`
- eBay API: `.env` (APP_ID, DEV_ID, CERT_ID)
- FanGraphs: pybaseball
- News Feeds: 10 RSS sources
- Playoff rosters: 12 teams, ~60 tracked players

### Business Model Expansion
| Sport | Timeline |
|---|---|
| MLB (playoffs → spring training) | Now - March 2027 |
| NBA (playoffs + MLB overlap) | March - July 2027 |
| NFL (longest season, biggest TAM) | July 2027 - Feb 2028 |
| NHL + soccer | Sept 2027+ |

### Beta Testers
- Jim (12 cards, beta #1)
- Alan (large volume, potential $200/mo alpha subscriber)
- Hingle (3 cards, beta #2)

### Lessons Learned
- Vintage HOF cards appreciate 10-25%/year — floors are NOT static
- "Sell the news" — World Series champions peak immediately, then drop 15-30%
- Liquidity discounts create deep value (Arozarena at $7.75 with 5.3 WAR season)
- Methodology must stay private — "black box" approach
- Card Hedge already surfaces eBay data — direct API integration may be unnecessary

### Cost Ledger (Sept 24)
| Item | Cost | Status |
|---|---|---|
| Card Hedge | $49/mo | Active |
| eBay API | $0 | Keys secured |
| Render | $8/mo | Active |
| Porkbun domain | $3.09/yr | Active |
| Apify STARTER | $29/mo | Active |
| **Total monthly** | **~$86** | |

---

## Founder preferences (CRITICAL — load first)

- **Distrusts flattery** → provide PROOF
- **NON-DEVELOPER PRODUCT FOUNDER** → plain English + decision tables
- **"STOP AND READ" PROTOCOL** → read full doc, then ONE clean solution
- **"ONE FIRE AT A TIME"** → serial, not parallel
- **"FULL PICTURE BEFORE COMMIT"** → proactively flag costs, risks
- **Channel for pricing**: pull frequency (not card count)
- **Security**: founder never types passwords; agent stays in control

## Resume pattern

1. `session_search` for most recent save (or read `Sessions/handoff.md` directly)
2. Read open fires section in handoff.md
3. Pick ONE fire
4. Execute, save, move forward

## Cross-agent coordination

**For any agent starting work on Card Scout:**

1. Read `Sessions/README.md` (agent-agnostic contract)
2. Read `Sessions/handoff.md` (current state)
3. Read `For You/Plans/2026-09-17-agent-coordination.md` (full coordination note)
4. Skim `.hermes/memory/working-notes.md` (context)

When you finish: update `Sessions/handoff.md` with what you did.

### Founder name
- **Jonathan** (first name) — use for founder-to-founder outreach
- **Fuzzy Bracelet** (brand) — use for service signups (Card Ladder trial, GitHub, Porkbun)
- Jim = beta tester (NOT the founder)

### Customers (3 total)
- `buddy_test_001` (Jim, beta #1) — 12 cards
- `hingle_mccringleberry_1789525909` (Hingle, beta #2) — 3 cards
- `cs_CZYAJYA00001` (test, DEAD webhook 404) — 1 card

### Latest pricing decision
**Casual $15 / Standard $30 / Dealer $75 / Pro $150**
(Margins 71-95%, pull frequency is the lever)

### Cost-cutting roadmap (REVISED Sept 17 after GemRate discovery)

| Stage | Trigger | Action | Status |
|---|---|---|---|
| 0 | 0-10 customers | Apify SCPRO actor | Active |
| 1 | Now (verified) | **eBay Browse API** (FREE) — listing spread for deal detection | Pending verification |
| 2 | TBD (decision) | **GemRate** Partner API (PSA+BGS+SGC+CGC pop data) — $TBD/mo | Contact form sent Sept 17, awaiting pricing |
| 3 | 25+ customers | Inline search UX (PL-008) using GemRate + SCPro | Designed, not built |
| 4 | 50+ customers | Player Index feature (PL-006) using GemRate history | Designed, not built |
| 5 | 500+ customers | DIY infrastructure or upgrade GemRate tier | TBD |
| 6 | 1000+ customers | Strategic partnerships | TBD |

**DEFERRED Sept 17:**
- ~~Pricecharting Collector ($6/mo)~~ — no API on Collector tier
- ~~Card Ladder Pro ($20/mo)~~ — cancelled Sept 17 (no API, dashboard only)

### Active blockers
1. eBay Developer Account verification (started Sept 16, Day 2 of ~2)
2. GemRate pricing response (form sent Sept 17, expected 1-3 business days)

### Open fires (priority order, Sept 17 evening)
1. ⏳ **GemRate response** (1-3 business days) — pricing + API key
2. ⏳ **eBay verification** (Day 2 of ~2) — paste App ID + Cert ID
3. 🎯 **Next fire when you return** — pending your call after break

### Today's deployed code (unchanged)
- deal_detector.py (z-score lower-third threshold)
- url_parser.py + url_orchestrator.py + url_resolver.py
- V3 alert layout (Jim + founder feedback)
- public_site.py source-strip (Sept 16, live on cardscout.pro)

### Lessons learned
- patch tool indents inconsistently in Python source
- "STOP AND READ" protocol — read docs in full before iterating fixes
- "one fire at a time" workflow
- Founder has shower-thoughts that change the game (PSA URL ownership, z-score, GemRate competitor-evaporation)
- NEVER `git add -A` — leaked GCP SA key in 1f3e87a
- Vendor outreach: generic technical questions only, no product positioning leakage

## File system rules

### Project root
`C:\Users\J\Documents\LLM\card-scout\`

### "For You" folder
Personal artifacts (Reddit, Sourcing, Sales, Research, Plans, Personal Collection, Listings, Authenticity)

### Sessions (Sept 17 NEW: agent-agnostic working state)
- `Sessions/README.md` — agent-agnostic contract (READ FIRST)
- `Sessions/handoff.md` — current state for any agent picking up
- `Sessions/parking_lot.md` — deferred items (PL-001 through PL-010)
- `Sessions/YYYY-MM-DD-{topic}.md` — per-topic session pages
- **Gitignored** along with `.hermes/sessions/` (per .gitignore rule)

### Per-agent scratch
- `.hermes/sessions/scratch.md` — Hermes private notes (only Hermes reads/writes)

### Plans
`For You/Plans/{topic}-{YYYY-MM-DD}.md` (markdown)
`For You/Plans/{topic}-NOTEPAD-{YYYY-MM-DD}.txt` (plain text for notepad)

## Founder preferences (CRITICAL — load first)

- **Distrusts flattery** → provide PROOF (billion-dollar examples, math)
- **NON-DEVELOPER PRODUCT FOUNDER** → plain English + decision tables + cost + risk
- **"STOP AND READ" PROTOCOL** → read full doc, then ONE clean solution
- **"ONE FIRE AT A TIME"** → serial, not parallel
- **"FULL PICTURE BEFORE COMMIT"** → proactively flag setup time, config
  decisions, ongoing costs, risks — never bare-minimum pricing
- **Channel for pricing**: pull frequency (not card count)
- **Security**: founder never types passwords; agent stays in control
- **PSA credentials**: in Apify secrets manager (not local)
- **Plaintext PSA.txt**: DELETED 2026-09-13

## Founder workflow

- Sketches design ideas on paper before typing into chat
- Shower = best product insights
- "When I come back from a break with an idea..." — capture it cleanly
- Lead with diagrams/tables, not raw SQL/Python
- Future-readiness pattern: "if this gains traction I want to be ready without a rewrite"
- "No slippage" UX principle — minimize redirects that pull customers off cardscout.pro

## Resume pattern

When founder returns from 15-min break:

1. `session_search` for most recent save (or read `Sessions/handoff.md` directly)
2. Read open fires section in handoff.md
3. Pick ONE fire (founder's "one at a time" rule)
4. Execute, save, move forward

## Pending cron jobs

| Job ID | Schedule | Purpose | Status |
|---|---|---|---|
| `509a458e7bfd` | 2026-09-23 09:00 CDT | Card Ladder Day-6 cancel reminder | NO-OP (cancelled early); leave or disable |

## Cost ledger (Sept 17 evening)

| Item | Cost | Status |
|---|---|---|
| Card Ladder | $0 (trial) → $0/mo (cancelled Sept 17) | RESOLVED |
| Render | $8/mo | Active |
| Porkbun domain | $3.09/yr | Active |
| Apify STARTER | $29/mo | Active |
| eBay Browse API | $0 | Pending verification |
| GemRate | TBD | Awaiting response |
| **Total monthly (today)** | **$37** | |
| **Total if GemRate +$50/mo** | **$87** | Pending GemRate response |

## Cross-agent coordination

**For any agent (Hermes, Claude Code, Codex, OpenCode) starting work on Card Scout:**

1. Read `Sessions/README.md` (5 min) — agent-agnostic contract
2. Read `Sessions/handoff.md` (2 min) — current state
3. Read `For You/Plans/2026-09-17-agent-coordination.md` — full coordination note
4. Skim `.hermes/memory/working-notes.md` — context

When you finish work: update `Sessions/handoff.md` with what you did.
When you defer work: add a PL-NNN entry to `Sessions/parking_lot.md`.

This is the durable agreement. New sessions inherit it via the
coordination note in git history.

## Today's session deliverables (Sept 17)

| Deliverable | Location | Status |
|---|---|---|
| Sessions infrastructure (README + handoff + parking_lot) | `Sessions/` | Created |
| Inline card search UX spec (PL-008) | `Sessions/2026-09-17-inline-card-search.md` | Drafted |
| GemRate research + inquiry draft | `Sessions/2026-09-17-gemrate-discovery.md` + `...-inquiry-draft.md` | Drafted, sent |
| Card Ladder trial data shape observations | `Sessions/2026-09-17-card-ladder-trial.md` | Captured |
| Plan doc corrections (CL no-API, PC Legendary, GemRate discovery) | `For You/Plans/data-provider-comparison-2026-09-16.md` | Updated |
| Founder name (Jonathan) | Memory + working notes | Recorded |
| Parking lot items PL-001 through PL-010 | `Sessions/parking_lot.md` | Captured |
| .gitignore update (Sessions/ + .hermes/sessions/ ignored) | `.gitignore` | Done |
| Card Ladder Day-6 cancel reminder | Cron `509a458e7bfd` | Set (now no-op) |
| Card Ladder subscription | Card Ladder → Account → Cancel | CANCELLED Sept 17 |
| GemRate contact form | gemrate.com/partner | SENT Sept 17 |
