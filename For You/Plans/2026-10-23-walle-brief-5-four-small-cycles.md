# WALL-E BRIEF 5: FOUR SMALL CYCLES (self-contained polish, no live-logic changes)
*Issued Oct 23 late, founder GO for "build another part." Each job is independent, small, and
zero-risk to verified flows. Do them in order A → B → C → D; report after each, or all at once.*

## JOB A — YEAR-MATCHED LANE RESOLVER (the queued fix)
- File: `dashboard/contributor_bp.py`, function `parse_pull_dump` (the lane-grouping +
  `refine_lanes` resolution path).
- Bug (founder live test, Oct 23): a 2025-season paste resolved to
  `brice-turang-2023-topps-chrome-mass-raw` (a 2023 lane). The resolver matches
  product/parallel tokens but ignores the YEAR.
- Fix: when several registry lanes match a paste lane-group, prefer the lane whose
  slug contains a year ALSO present in the paste text (titles or the declared
  search header). If only one year-matched candidate exists, take it. If the paste
  names no year, keep current behavior (no regression). NEVER guess between two
  year-matched candidates — pick only when unambiguous, else leave the honest None
  (same as now).
- Test: the Turang 2025 paste must resolve to `brice-turang-2025-topps-*`, never 2023.

## JOB B — CARD-PAGE META + OG TAGS (template consistency)
- File: `dashboard/band_pages.py` (the lane templates).
- The homepage carries the site-verification meta; lane pages don't carry ANY head meta
  beyond charset/viewport. Add to every lane template `<head>`:
  1. The Impact verification meta (template-consistency: same tag as home)
  2. `<title>{Player} {Lane} price band & live listings — Card Scout</title>`
  3. `<meta name="description">` (one line: lane + band state, no numbers)
  4. OG tags (og:title, og:description, og:url, og:type=website) for clean social sharing
- NO numbers, positions, or band values in any of these — states only.

## JOB C — OPT-OUT CONFIRMATION EMAIL (CAN-SPAM polish)
- File: `scripts/email_alerts.py` (+ one helper read from `contributor_bp`).
- When a user follows `/unsubscribe?t=...` and the opt-out FLIPS (not when already out),
  send one short confirmation email via the existing Brevo path:
  subject "Card Scout — you're unsubscribed"
  body: 3 lines (alerts stopped immediately · bands stay public · re-subscribe link with
  their token) + NO footer needed on a transactional confirmation (keep the one-liner).
  Send errors: logged, never raised (same discipline as the send path).
- Guard: if BREVO_API_KEY missing, skip silently (log-only), like the send path does.

## JOB D — WORKSPACE STAT-BLOCK (the credit made visible)
- File: `dashboard/contributor_bp.py`, `WORKSPACE_TEMPLATE` (the interior view).
- Above the intake form, render a compact stat-strip from the contributor's OWN ledger:
  `X pastes · Y prints contributed · Z lanes touched · credit since {first_ts}`
  (all four numbers exist in the ledger — pure render, zero new computation).
- Below it one line: "Every deposit sharpens the bands for the whole community —
  your searches built these."
- Do NOT render other contributors' data (P11) or any band numbers (P4).

## THE NEVER-LIST (short form, all inherited)
- No advice copy anywhere; no band $ values; no positions/engine output; no other-
  contributor data; no new network paths; no changes to verified trigger/heatmap logic
  (P17/P18 behavior frozen — your changes are additive).

## ACCEPTANCE (Hermes after your self-test)
- PA: year-matched resolution — 2025 paste -> 2025 lane (and no-year paste unaffected)
- PB: lane pages carry verification + title + description + OG (template-consistency probe)
- PC: opt-out sends one confirmation; already-out sends nothing; no-key degrades to log-only
- PD: stat-strip renders own-numbers only, P11/P4 re-proof
- FULL REGRESSION: P9–P19 all re-pass; DEPLOY-ENV-REPRO 3.14 --with-requirements; prod probes

## STATUS: GO. Order A→B→C→D. Report per job or batch. Hermes verifies + stamps.