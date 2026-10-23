# WALL-E BRIEF 3: WORKSPACE AMENDMENT (§227 direction + target-price + seller-watch) + UNSUBSCRIBE ENDPOINT
*Issued Oct 23 afternoon. Founder GO ("whatever you recommend"). Builds ON the verified contributor workspace (37cc095) — same module, amendment not rewrite. Verify: Hermes P13–P16 + inherited battery.*

## READ FIRST
- Base module: `dashboard/contributor_bp.py` (VERIFIED-2026-10-23 — extend it, never rewrite it)
- Banked laws you're implementing: cardscout-2.0 study file `website-endstate-architecture.md`:
  - §227 SELLER-WATCH (reversed alerts, negotiation ledger)
  - §227.1 DIRECTIONALITY (buying/selling checkbox at point-of-capture)
  - §227.2 USER-OWNED-TRIGGER (their ceiling/floor; the machine only watches; NO hints/pre-fill)

## JOB 1 — THE INTAKE AMENDMENT (the paste form grows two fields)
On the workspace paste form, ABOVE the textarea, add:
1. **Direction:** two radio-style buttons — `Buying` / `Selling` (default: nothing selected; the parse proceeds either way but the reward copy branches on it)
2. **Target price** (optional, numeric): one field, labeled by direction contextually —
   - Buying → "Your ceiling — alert me below this"
   - Selling → "Your floor — alert me above this"
   - **NEVER pre-filled, no hints, no band-suggested values anywhere in this field (§227.2 un-anchored rule)**
3. Optional text field: `seller_id` (only relevant when Direction = Selling; label "Your eBay seller ID (optional)")

Storage: extend the deposit row + ledger row with `direction` (BUY|SELL|null), `target_price` (float|null), `seller_id` (string|null). Persist on the 2.0 ledger (same file, same append-only discipline).

## JOB 2 — THE REWARD RENDER BRANCH
After parse, the reward page adds one line under the lane-refined section:
- If Buying: "Entry watch: if this lane prints below YOUR ceiling ($X), your next alert says so."
- If Selling: "Repricing watch: if this lane prints above YOUR floor ($X), your next alert says so."
- Numbers render from THE USER'S OWN input only. The site NEVER renders its own band thresholds here (P4 law unchanged).
- If no target set: skip the line (no placeholder nagging).

## JOB 3 — SELLER-WATCH REGISTRY (§227)
If `seller_id` provided: write to `data_lake/gold/seller_watch_registry.json` (append-only):
`{ts, contributor_email_hash, seller_id, lanes:[parsed lane ids]}`.
This is a LEDGER, not a feature yet — the alert-side reversal ships in a later cycle. Do not build the seller-alert sending in this brief.

## JOB 4 — UNSUBSCRIBE ENDPOINT (CAN-SPAM closure; the email footer already links here)
- Route: `GET /unsubscribe?t=<token>` (public, no auth, robots-disallowed)
- Token: HMAC of the email using SECRET_KEY (stateless; no DB lookup needed) — helper `make_unsub_token(email)` / `verify_unsub_token(token) -> email|null`
- Behavior: valid token → set `opt_out: true` + `opt_out_ts` on the contributor's ledger entry (append-only style), render branded confirmation page ("You're unsubscribed. The bands stay public at cardscout.pro — your alerts stop immediately."), include the one-click RE-subscribe link (`/resubscribe?t=...` same mechanism, flips back)
- Invalid/expired token → same page with "link expired — contact jonathan@cardscout.pro" (honest-200, never a 500)
- The alert-sender (`email_alerts.py`) gains the token generation + skips opted-out emails (one-line filter at the send loop)

## THE NEVER-LIST (inherited + amendment-specific)
- NEVER pre-fill or suggest prices in the target field
- NEVER render band thresholds/number values in reward copy (user's own number excepted)
- NEVER send any email from this build (unsub/resub only flip flags; zero sends)
- NEVER break the verified workspace behavior (this is an amendment — the P9–P12 battery must still pass after your changes)

## ACCEPTANCE (Hermes battery after your self-test)
- P13 intake: direction + target + seller_id persist to ledger/deposit rows (null-safe all three)
- P14 reward-copy branch: buyer-vs-seller framing renders correctly from user input only; no band-number leaks (P4 re-run included)
- P15 unsub loop: token makes/verifies; end-to-end opt_out flag flips + confirmation renders + email loop filter holds; resub reverses; invalid token = honest-200
- P16 regression: the FULL P9–P12 battery re-passes untouched workspace behavior
- Parse OK + import OK before you report built (battery runs after)

## OUT OF SCOPE (explicitly)
- Seller-alert sending (Job 3 is ledger-only), search heatmap, card-page meta tags, any new pages beyond the two routes in Job 4
- Any change to band_pages.py or public_site.py

## STATUS: BRIEF ISSUED, WALL-E GO. Build → self-test P13–P16 + P9–P12 re-run → report. Hermes verifies and stamps. No stamps until then.
---
## BUILD VERIFIED 2026-10-23 (Hermes fresh-run, c63da3d)
P13 direction+target persist: BUY/SELL normalized, target float-nullsafe, ledger rows carry direction/target_price/seller_id; entry/repricing watch-lines render from USER input only
P14 un-anchored proven: watch-line contains exactly the user's number ($25.00 = theirs), zero site numbers
P15 unsub loop: HMAC token gen/verify, opt_out+ts flag flips, email_alerts filter holds, resub reverses, invalid token = honest-200 branded page
P16 regression: full P9-P12 re-pass; non-roster 302-clean, interior never renders
Seller-watch registry: 2 rows written (ts, hashed-email, seller_id) — append-only, negotiation ledger live
WALL-E = 3/3 verified briefs (card pages, workspace, amendment). Stamped VERIFIED-2026-10-23.

---
## PROD-PARITY CATCH + FIX (b1177a2): the founder asked "did you check the ACTUAL website?" — the honest answer was NO.
PROBE: /contributor/* + /unsubscribe = 500 on prod (200 locally) — root cause: brief-3's
LANE_TAXONOMY import ladder had no terminal fallback → on Render (no 2.0 repo) the import
died, killing the whole contributor blueprint. Reproduced EXACTLY via `uv run --python 3.14`
(Render's python) + degraded env = NEW VERIFY CLASS: DEPLOY-ENV-REPRO. Fix = graceful
degradation (2.0 repo → deployed-registry taxonomy → empty + honest causes).
POST-FIX PRODUCTION: /contributor/health 200, /contributor/login 200 (disclosure terms live),
/unsubscribe 200, /resubscribe 200. LESSON BANKED: brief-3's battery ran LOCAL-only —
the same PROD-PARITY miss as the Oct-22 freeze; rule extended: verify-battery includes
uv-3.14 --with-requirements repro BEFORE stamps when a brief touches imports.
