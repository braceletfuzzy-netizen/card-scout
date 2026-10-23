# WALL-E BRIEF 4: WATCH-TRIGGER LOOP (§227.2 firing) + SEARCH-HEATMAP TELEMETRY (§221/T5)
*Issued Oct 23 afternoon. Founder GO ("let's do it"). Extends the verified workspace +
email pipeline. Verify: Hermes P17–P19 + PROD-PARITY (DEPLOY-ENV-REPRO) + full regression.*

## READ FIRST
- `dashboard/contributor_bp.py` (VERIFIED — extend, don't rewrite)
- `scripts/email_alerts.py` (LIVE — first send delivered cc148a8)
- Study file: `website-endstate-architecture.md` §227.2 (user-owned triggers) + §221/T5 (observatory) + §227.1 (direction)
- Cache Law + P-battery inherited; the never-list below binds absolutely.

## JOB 1 — TARGET-TRIGGER WATCH LOOP (the §227.2 firing half)
At the SAME polling tick that refreshes lane caches (the band_pages 1h cache cycle):
1. Load all ledger rows with `target_price` NOT NULL and `opt_out` falsy.
2. For each lane the user has a target on: read the lane's **latest verified prints**
   from the EXISTING corpus/report files (same source the alerts JSON uses — no new
   data path, no new API spend).
3. Crossing test:
   - BUY + a print ≤ target_price → **below-hit**
   - SELL + a print ≥ target_price → **above-hit**
4. On a NEW crossing (not previously sent for this target — keep a sent-marker
   `data_lake/gold/trigger_sent.json`, keyed `email|lane|direction|target`):
   → queue an email via the EXISTING `email_alerts.py` machinery:
     subject: "Card Scout — your price crossed on [lane]"
     body: the standard alert card (their trigger line + the hitting print's market
     state + tagged link) + the four-clause footer + their token.
   - The email says "the market crossed YOUR line" — **it NEVER says buy/sell/act**.
5. One email per lane per cycle maximum (anti-spam); re-arm after the user updates
   their target (new target = new sent-marker key).

## JOB 2 — SEARCH-HEATMAP TELEMETRY (the T5 instrument)
1. The `/bands?q=` + contributor analyze paths now log each search:
   `data_lake/gold/search_heatmap.jsonl` — append-only:
   `{ts, lane_slug|null, search_q_hash (SHA-256, never raw PII-ish string? NO —
   the raw query IS the deposit per search-is-the-seed; store it), direction|null, results_n}`
   - Raw query stored (it's the corpus); sender identity NOT stored here (heat ≠ identity).
2. Lane pages render a **heatmap-lite** when n≥5: "searched N times this week" +
   the top 3 most-common refined search phrases for that lane (community vocabulary
   made visible — the Wikipedia/dishonesty-free frame).
3. Aggregates feed NOTHING else yet (F-vector/intent-analytics = later banked plans,
   not this build).

## JOB 3 — EMAIL_ALERTS TOKEN + OPT-OUT HARDENING (brief-3 follow-through)
- The unsent-email path gains the token footer for real: `render_footer` gets the
  per-user token (HMAC via contributor_bp helper) instead of the placeholder.
- Opt-out filter: confirmed present in the send loop (brief 3 added it) — add ONE
  test proving an opted-out user's row is skipped end-to-end.

## THE NEVER-LIST (all inherited + strict)
- NEVER render advice ("buy now", "good entry", "act on this") — crossing events
  state "the market crossed YOUR line" and nothing more
- NEVER leak band thresholds or engine output in trigger emails (user's own number
  + public market-state only)
- NEVER pre-fill targets, NEVER expose raw search heat by identity
- NEVER send a crossing email without the crossing VERIFIED from prints (asks are
  not prints — the MPA/honesty law holds in the watch loop)
- NEVER crash the polling tick: any error in the watch/heatmap loop = logged and
  skipped (the tick returns; bands still serve)

## ACCEPTANCE (Hermes P17–P19 + DEPLOY-ENV-REPRO + full regression)
- P17 trigger loop: seeded ledger row + seeded crossing print → email queued/built
  w/ correct framing (their line, market-state, tagged link); re-run = no duplicate
  send (sent-marker holds); target update re-arms; opt-out skips; SELL direction
  symmetric; **verified UNDER uv 3.14 --with requirements (DEPLOY-ENV-REPRO)**
- P18 heatmap: search logged (1 row, raw query, hashless identity), N≥5 renders
  heatmap-lite w/ top phrases, n<5 renders nothing (no empty-module cruft),
  no identity leak in the render
- P19 regression: P9–P16 re-pass; homepage + /bands + /contributor/* + /unsubscribe
  all 200 locally AND the DEPLOY-ENV-REPRO import set passes
- PROD-PARITY: after push, Hermes probes live /bands + /contributor/login +
  /unsubscribe + (one heatmap-render lane) — 200s + feature fingerprints before stamp

## OUT OF SCOPE
- Seller-alert sending (still), card-page meta tags, mobile, basketball anything,
  new pages beyond heatmap-lite rendering

## STATUS: BRIEF ISSUED, WALL-E GO. Build → self-test → report. Hermes battery + prod-parity → stamp.