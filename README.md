# Card Scout

**Project**: Card Scout V1 (Bloomberg Terminal for trading cards)
**Status**: ✅ Production-ready (12 cards alerting)
**Last major update**: 2026-09-14 (migration from vostok-tools)

> ## ⚠️ READ THIS FIRST: Master Strategy
>
> Card Scout is **vertical #1** of a multi-vertical collectibles asymmetry
> framework. The business is not "card tool" — it's "narrowing bid-ask spreads
> in markets with imperfect information." Cards is just the first market
> we attached to.
>
> **Master strategy doc**: `For You/Plans/MASTER-STRATEGY-collectibles-asymmetry-framework-2026-09-14.md`
>
> Read it before designing any vertical, product, or customer flow.

## What This Project Does

Card Scout is a Discord alert bot that watches eBay and Sportscardspro for
mispriced trading cards. It uses Apify actors (3 we own, no third-party data
purchases) to scrape listings, then sends Discord alerts when a card is listed
below its per-grade market average.

**The product**: A Bloomberg-style ticker showing **price per grade** (PSA 10,
PSA 9, BGS 9.5, Raw) with 90% confidence intervals. Customers see the market
state and decide for themselves whether to buy. We don't recommend — we surface
the data.

**Why this exists**: Vostok-tools (the parent project) needed a price-discovery
side hustle for low-volume markets. Trading cards fit perfectly — high-value,
fragmented, sold by individual hobbyists, not catalogs. Card Scout launched as
a v0.9 prototype and grew into its own product.

## Repository Structure

```
card-scout/
├── README.md                       ← you are here
├── .gitignore
│
├── scripts/                        ← Python bot code
│   ├── discord_alert_bot_v3.py     ← main bot (SQLAlchemy + Discord)
│   ├── db_models.py                ← Customer, Card, Snapshot, RunHistory
│   ├── snapshot_system.py          ← price trend detection
│   ├── psa_pop_lookup.py           ← PSA actor wrapper (with retry)
│   ├── sportscardspro_lookup.py    ← Sportscardspro actor wrapper
│   ├── grade_detector.py           ← regex for PSA/BGS/CGC strings
│   ├── grade_detector.README.md    ← module doc
│   ├── grade_range_calculator.py   ← per-grade 90% CI from sales data
│   ├── grade_range_calculator.README.md
│   ├── ticker_formatter.py         ← Discord embed for ticker output
│   └── ticker_formatter.README.md
│
├── actors/                         ← Apify actors we own
│   └── ebay-etsy-watch-scraper-monetized/  ← eBay actor (build 0.4.11)
│
├── config/                         ← secrets (gitignored)
│   ├── apify-token.txt             ← Apify CLI auth
│   ├── bright-data-token.txt       ← Bright Data proxy auth
│   ├── discord-webhook.txt         ← Discord webhook URL
│   └── card-scout-sheet.json       ← Google Sheets sync config
│
├── card_scout.db                   ← SQLite bot DB (12 cards, 4 customers)
│
└── For You/                        ← user-curated content (NOT a code folder)
    ├── Brand/                      ← logo, avatar, favicon
    ├── Plans/                      ← specs + handoff docs
    ├── Marketing & Sales/          ← pitch docs, DM templates
    └── Research/                   ← customer research notes
```

## Quick Start

```bash
# From card-scout/ root
cd C:/Users/J/Documents/LLM/card-scout

# Verify imports
python -c "import sys; sys.path.insert(0, 'scripts'); import discord_alert_bot_v3"

# Run a test on one card
python -c "
import sys
sys.path.insert(0, 'scripts')
from discord_alert_bot_v3 import get_session, run_apify_search, filter_matching_items
from db_models import Card
session = get_session()
card = session.query(Card).filter_by(id=1).first()
result = run_apify_search(card.search_query, preset=card.preset, max_listings=15, include_sold=False)
print(f'{len(result[\"items\"])} items in {result[\"duration\"]:.0f}s')
session.close()
"
```

## How The Bot Works

```
For each card in cards table:
  1. eBay search (30 items in ~31s)
       ↓ actor: AtQq66Qn8FB7aLq2l (cost ~$0.04/run)
  2. Filter + match by customer keywords
  3. Compute summary (Q bands, median, deal count)
  4. Optional: PSA pop lookup (with retry, 180s timeout)
       ↓ actor: DgLihiFRCa1Qf781s (cost ~$0.012/run)
  5. Sportscardspro lookup (per-grade prices)
       ↓ actor: PGRtI1ZjuqUELHCGr (cost ~$0.005/run)
  6. Format alert with per-grade ticker + below-market deals
  7. Send to Discord webhook
```

## Cost

- Per-card cost: ~$0.05 (no PSA) or ~$0.07 (with PSA)
- Daily scan (12 cards × MWF = 156 runs/year): ~$10-15/year
- See `../vostok-tools/config/monthly-budget.json` for cap details

## Status — P0 Items

- ✅ P0-HUGO-EMPTY-TITLE — RESOLVED (commit eff2bf0)
- ✅ P0-HUGO-ACTOR-QUERY-CONFLICT — RESOLVED (commit c7e964a)
- ✅ P0-HUGO-INCLUDESOLD-BROKEN — RESOLVED (commit 1f3e87a)
- ✅ P0-HUGO-PSA-SOLD — RESOLVED (commit cc0f38c)
- ✅ Migration from vostok-tools — COMPLETE (2026-09-14)

## Documentation Map

| To learn about... | Read... |
|---|---|
| Product vision | `For You/Plans/card-scout-ticker-system-spec-2026-09-14.md` |
| Old/superseded spec | `For You/Plans/card-scout-graded-focus-spec-2026-09-14.md` (SUPERSEDED) |
| EBay actor internals | `actors/ebay-etsy-watch-scraper-monetized/README.md` |
| Grade parser logic | `scripts/grade_detector.README.md` |
| Per-grade math | `scripts/grade_range_calculator.README.md` |
| Discord output format | `scripts/ticker_formatter.README.md` |
| Resolved bugs (context) | `For You/Plans/hugo-handoff-*-RESOLVED.md` |
| Bot run flow | `scripts/discord_alert_bot_v3.py` (header comments) |

## Agents Working On This

- **Hugo** (actor code, parser, statistical math, output formatter)
  Workspace: `C:\Users\J\Documents\LLM\hugo\`
- **Cosmo** (specs, customer flow, DB queries, bug discovery)
  Workspace: `C:\Users\J\Documents\LLM\cosmo\`

## Customer Status

- **Jim** (`buddy_test_001`) — first beta customer. 12 cards on watchlist. Active.
- **Customer #2** — onboarding pending after V1 stable (this month).
- **Customer #3+** — TBD. V1 + 1-2 months of customer feedback before V2 (Ticker Pro).

## Contact

For questions, check the agent workspace (`hugo/` or `cosmo/`) for session notes.
Per the README-first protocol: **read before changing**.

---

## CARD PAGES (`/bands`) — Oct 23, 2026

Public card pages per spec `cardscout-2.0/For You/Plans/2026-10-22-CARD-PAGE-BUILD-SPEC-v1.md`:
one page per instrument-lane — market band (upper) + live eBay listings (lower half).

- **Blueprint**: `dashboard/band_pages.py` (registered in `dashboard/app.py`).
  Routes: `GET /bands` (index) · `GET /bands/<slug>` (card page) · `GET /bands/health`.
- **Band data**: `dashboard/registry/card_page_registry.json` — PUBLISHED ONE-WAY from
  `cardscout-2.0/scripts/build_card_page_registry.py` (corpus = `data_lake/gold/ebay_lanes/`
  print pastes). Band numbers live SERVER-SIDE ONLY; the page renders the band as a
  shape-visual (median marker + deal-zone ribbon position), never as text.
- **Live listings**: eBay Browse API via eBay client-credentials OAuth (pattern from
  `cardscout-2.0/scripts/ebay_left_tail.py`). CACHE LAW: 1 hour per lane; stale-serve +
  silent refresh; the page NEVER hard-fails (429/timeout degrade to cached/band-only).
- **EPN gate (MPA guard)**: `EPN_CAMPAIGN_ID` (Render env / `.env`) = arming switch.
  Armed -> every buy-link tagged with `campid` + `customid=<lane-slug>`.
  NOT armed -> affiliate-tagged links NEVER render (plain links only). Explicit empty
  env value = disarmed.
- **Client-side sorts**: Lowest BIN (default) / Price / Score / Feedback / Free ship /
  BIN-Auction / Date — all in-browser on cached rows, zero API cost, no rows dropped.
- **All sellers visible**: score/feedback/shipping beside price; no seller-filter logic
  exists in the code (verified by AST probe).
- **Search = the seed**: `cardscout.pro/bands?q=<search>` — a hit redirects to the lane;
  a miss renders the gratitude page. Every q= visit appends exactly one deposit row to
  `data/search_deposits.jsonl`.
- **Favorites**: localStorage (`cardscout.favorites.v1`), no account (Phase 1).
- **Battery**: `cardscout-2.0/scripts/card_page_battery.py` (P1-P8; hermetic, mocks the
  network). Builder pre-verify only — Hermes is the verifier.
---

## CONTRIBUTOR WORKSPACE (`/contributor`) — Oct 23, 2026 (AM)

Private paste→parse→reward surface per brief `cardscout-2.0/For You/Plans/2026-10-23-walle-brief-contributor-workspace.md`.
**Private: robots-disallowed, roster-gated, NEVER published, no public links.**

- **Blueprint**: `dashboard/contributor_bp.py` (+ `static/contrib.css`), registered in `app.py`.
- **Auth**: Google OAuth2 (same flow as `/admin/login/google`; `GOOGLE_CLIENT_ID`/`SECRET` env).
  Attribution = the PERSON (email) → ledger rows keyed by Google email. No passwords.
- **Roster gate**: `CONTRIBUTOR_EMAILS` in `.env` (comma-separated, founder-curated). Any
  other Google login → clean redirect to `/bands`, zero interior render.
- **Flow**: paste (200KB cap) → local parse funnel (lane-split + Two-Class print/ask law,
  every exclusion counted by cause) → reward page: the paste's own histogram, the refined
  lane (before/after as a WIDTH-DELTA PERCENT — band $ values never render), BIN-sorted
  live listings via the same cache-law/EPN-gated path as /bands, grade-state after the
  contribution, ledger tick.
- **Deposits** (local, in 2.0 data lake): `data_lake/raw/contributor/<contributor-id>/<ts>_paste.txt`;
  **Ledger**: `data_lake/contributor_ledger.json` (append-only rows; private; PII = name+email+
  counts+lanes only).
- **Disclosure (P12)**: Google-info consent block (sole-use / never-sell / nothing-leaves /
  disconnection guarantee) + the three no-advice clauses, on the login view + footer.
- **Battery**: `cardscout-2.0/scripts/contributor_workspace_battery.py` (P9–P12 + inherited
  P4/P5 sweep; hermetic). Builder pre-verify = 5/5 PASS; Hermes runs the gate — no stamps.
- **The 405 fix**: the legacy catch-all `@app.errorhandler(Exception)` was converting
  Flask HTTPExceptions (404/405) into 500s — now passes them through unchanged (this
  also restores true 404s site-wide).
---

## WORKSPACE AMENDMENT (§227 + CAN-SPAM) — Oct 23, 2026 (PM)

Brief 3 (`cardscout-2.0/For You/Plans/2026-10-23-walle-brief-3-workspace-amendment.md`) —
extends the verified contributor workspace in place (same module, no rewrite):

- **Intake** (on the paste form): Direction `Buying/Selling` (no default) · Target price
  (user's own ceiling/floor — **never pre-filled, no hints, no band-suggested values**,
  §227.2) · eBay seller ID (optional). Persists to the deposit sidecar + ledger row
  (`direction`/`target_price`/`seller_id`, null-safe).
- **Reward branch**: BUY → "Entry watch … YOUR ceiling ($X)"; SELL → "Repricing watch …
  YOUR floor ($X)". Users' own numbers only; band values never render here.
- **Seller-watch registry** (§227, LEDGER-ONLY): `data_lake/gold/seller_watch_registry.json`
  — append-only rows `{ts, contributor_email_hash, seller_id, lanes}`; hash-keyed; the
  alert-side reversal ships later (nothing sends).
- **Unsubscribe loop** (CAN-SPAM): `GET /unsubscribe?t=<token>` + `/resubscribe` at the
  ROOT (prefix-less blueprint; the email footer links to root). Token = HMAC-SHA256 of
  `email|ts|v1` under `SECRET_KEY` — stateless, tamper-rejecting. Valid → `opt_out:true`
  + `opt_out_ts` on the ledger entry, branded page with one-click resubscribe;
  invalid → honest-200 "Link expired" + contact. **ZERO email is sent by this build.**
- **email_alerts.py**: send loop now skips opted-out addresses; real tokens generated
  for real addresses (placeholder addresses keep the placeholder footer).
- **Battery**: `workspace_amendment_battery.py` P13–P16 = 4/4 PASS + P9–P12 re-run 5/5
  + P1–P8 band battery 8/8. Hermes verifies — no stamps.
---

## WATCH-TRIGGER LOOP + SEARCH HEATMAP (Brief 4) — Oct 23, 2026 (evening)

The §227.2 firing half + the T5 instrument, built on the verified surfaces:

- **Watch-trigger loop** (`contributor_bp.watch_trigger_tick`): every
  ledger row with a user-set target + direction, opt-out falsy, is checked
  against the lane's VERIFIED prints in the deployed registry (completed
  sales only — asks were excluded at parse; asks are never prints).
  BUY + print ≤ target → below-hit; SELL + print ≥ target → above-hit.
- **Crossing email**: subject "your price crossed on [lane]" + their trigger
  line + the hitting print's market state (position among the lane's corpus
  prints) + tagged lane link + four-clause footer + their real HMAC token.
  The email says the market crossed THEIR line — never buy/sell/act. Band
  numbers never render in mail.
- **Anti-spam/re-arm**: one email per lane per cycle; sent-markers live in
  `data_lake/gold/trigger_sent.json` keyed `email|lane|direction|target` —
  a NEW target = a NEW key = automatic re-arm. Opted-out users are skipped
  before any crossing test.
- **Queue, not send**: drafts land in `data_lake/gold/draft_outbox/`
  (uuid-suffixed, `sent:false`) for the `email_alerts.py --send` loop. The
  polling tick itself NEVER sends and NEVER crashes (every error logged +
  skipped; bands still serve). Thread rides app.py (30 min; the same polling
  half-cycle as the 1h lane-cache refresh); `WATCH_TICK_DISABLED=1` disables.
- **Search heatmap** (`band_pages.heatmap_log` + `collect_search_heat`):
  `/bands?q=` hits and misses + contributor analyze searches append
  `{ts, lane_slug, search_q, direction, results_n}` to
  `data_lake/gold/search_heatmap.jsonl` — the RAW query is kept (it is the
  seed deposit / the corpus); sender identity is NOT (heat ≠ identity).
  Lane pages render a heatmap-lite strip only at n ≥ 5 searches this week:
  "searched N times this week" + top-3 community phrases. Below the gate:
  nothing renders. Aggregates feed nothing else yet.
- **email_alerts hardening**: one send path in the `--all` loop (per-address
  failures logged, loop continues); opt-out filter now env-redirectable for
  hermetic testing; proved end-to-end in P17.
- **Batteries**: `brief4_trigger_heatmap_battery.py` — P17 trigger, P18
  heatmap, P19 full regression (P9–P12 5/5, P13–P16 4/4, P1–P8 8/8, app 200s)
  + DEPLOY-ENV-REPRO (uv `-p 3.14 --with-requirements`) = **4/4 PASS**.
  Hermes verifies — no stamps.
---

## BRIEF 5 — FOUR SMALL CYCLES (Oct 23, 2026 late)

All additive on verified modules; P17/P18 logic frozen. Builder battery
`brief5_four_cycles_battery.py` = **6/6 PASS** (PA–PD + full regression + DEPLOY-ENV-REPRO).

- **Job A — year-matched lane resolver** (`contributor_bp`): the paste's CARD
  years (listing titles + declared search header; sale dates stripped as noise)
  now gate lane resolution. Among same-(lane, grade) registry candidates:
  exactly one candidate year in the paste → take it; declared year matching
  zero/multiple candidate years → **honest miss** (no credit, never a guess);
  year-less pastes keep legacy behavior. The founder's Turang-2026-declared
  paste no longer credits the 2023 lane.
- **Job B — meta + OG on card pages** (`band_pages`): lane pages, /bands, and
  gratitude carry the byte-identical Impact site-verification block (both
  forms, same as home), `<title>{Player} {Lane} price band & live listings —
  Card Scout`, a state-only `meta description` (band-state word, zero
  numbers), and `og:title/description/url/type` for clean social sharing.
- **Job C — opt-out confirmation email** (`email_alerts` + the unsub route):
  a FRESH opt-out flip sends one transactional confirmation via Brevo
  ("you're unsubscribed" · alerts stopped · bands stay public · one-click
  re-subscribe link with a fresh HMAC token; one-line disclosure only).
  Already-out users get nothing; missing `BREVO_API_KEY` = log-only skip;
  send errors are logged and never touch the page.
- **Job D — workspace stat-block** (`contributor_bp`): the interior renders
  the contributor's OWN ledger strip — `X pastes · Y prints contributed ·
  Z lanes touched · credit since {date}` — plus the credit line. Own data
  only (P11 re-proved), zero band numbers (P4 re-proved), clean zero-state.

Probe updates (probe-side only, resolution-law consequences): P10/P18 of the
older batteries updated where the declared-search + year laws lawfully changed
what the sample paste resolves; module contracts (heat row shape, reward
render shapes, ticker contracts) unchanged.

---

## YEAR-ATTRIBUTED LANES + REGISTRY RELABEL (Brief 7) — Oct 24, 2026

Spec: `For You/Plans/2026-10-24-walle-brief-7-year-attribution.md` (two founder-proven
failure modes, one design flaw — year resolution happened at the paste-pool layer, not the
row-title layer).

- **Job A — row-level year grouping** (`contributor_bp.py`): every parsed row is stamped
  with ITS OWN title year (Sold-date noise stripped: ISO + "Mon D, YYYY"; zero/multiple
  distinct tokens = year None, never a guess) and prices group on `(card_year, lane)`.
  `refine_lanes` matches each group ONLY against registry lanes whose slug year equals the
  row year — exactly one same-year candidate = match (`match_reason: "year-lane"`); several
  = honest miss; none = honest miss with the reason rendered ("rows say 2023; lanes for
  this parallel are labeled 2025"). Product-line discrimination: when a relabel leaves
  same-year lanes differing only in product (2023 Topps vs 2023 Topps Chrome), the rows'
  own vocabulary (e.g. "chrome" named in titles) picks the exact lane — never a size vote.
  Year-None groups keep the Brief 5 legacy branch byte-for-byte. Typed price lines that
  name the card keep their own text (year tokens stay visible); Sold-only lines keep the
  Oct-23 context-carry law.
- **Job B — registry year-relabel sweep** (`cardscout-2.0/scripts/relabel_year_sweep.py`):
  evidence = the registry builder's own row pipeline (reproduces all 757 lane groups
  exactly). Majority title-year per lane; `slug-year != evidence` -> MIGRATE in place
  (same entry object + position; prints/band/deal intact) + retired slug preserved in the
  registry's new `slug_aliases` block; ties / no-evidence / collisions = honest-FAIL
  (logged with evidence counts, never flipped). Result this run: **96 lanes migrated**
  (Turang mass 39 -> 2023-mass, gold 36 -> 2026-gold, sapphire 18 -> 2026, wave 11 -> 2026,
  numbered 9 -> 2023, true-gold 8 -> 2023, auto-family per its own evidence; Chourio/Kwan/
  Bibee/ Wood/Murakami families likewise), 46 ties + 51 no-evidence lanes honest-FAILED.
  Full table: `cardscout-2.0/scripts/relabel_year_sweep_report.json`.
  **Re-run this sweep after any `build_card_page_registry.py` rebuild** (a rebuild resets
  slug years to title-blind derivation).
- **Aliases keep everything alive**: `lane_by_slug` falls back through `slug_aliases`
  (old card-page links render 200, never 404); the watch-trigger tick resolves ledger
  slugs through the same map — pre-sweep trigger markers keep suppressing (checked under
  BOTH slug keys; the §228 armed SELL@30 trigger follows its lane).
- **Acceptance**: `cardscout-2.0/scripts/brief7_year_attribution_battery.py` B1-B6 = 6/6
  (B1 2023-paste heal + B2 Chourio per-year heal + B3 no-mis-credit + B4 typed/year-less
  regression + B5 full-regression brief5 6/6 · brief6 6/6 · workspace 5/5 · brief4 ·
  cardpage + B6 uv-3.14 repro + prod 200s incl. old-slugs-via-alias).
