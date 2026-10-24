# WALL-E BRIEF 9 — PER-PLAYER RC INDEX: MASS + AUTO BASKETS, VELOCITY, FLIGHT-TO-QUALITY RATIO, CH CROSS-VALIDATION
*Hermes-written (verifier), Oct 24 late night. Founder GO received ("I say we
build it"). One-liner handoff: "Brief 9: per-player RC index. Read the brief,
build to spec, run the B1- B6 battery, report with SHAs — no self-verify."*

---

## WANT (the deliverable)

`src/rc_index/` — per-player, per-lane-class price indices computed from the
paste archive, with bar cadence = paste cadence, printed as an append-only
bar store:

1. **RC-INDEX-MASS** — basket: plain refractor + parallels /99-and-below
   (liquid retail lane)
2. **RC-INDEX-AUTO** — basket: RC-year autos + graded-autos (the store lane)
3. **Derived columns per bar:** `velocity_pct` (Δ vs prior bar), `auto_mass_ratio`
   (the §205 flight-to-quality gauge), `n_mass`, `n_auto`, `confidence` tag.
4. **CH cross-validation table:** our auto-index vs CardHedge player-index
   (weekly pull, already-verified endpoint §209.1) — per player, per week:
   `ch_index`, `our_auto_index`, `ch_vs_raw_spread`. CH sees the graded side;
   we see raw/serial; the SPREAD is a new, named gauge (their sourcing validity,
   measured continuously).

## DERIVATION PATH (mandated — every constant traced or the gate fails)

- Basket membership via `lane_class` from the EXISTING lane parser (no new
  parsing logic); year-attribution = Brief 7's resolver output if available,
  else raw lane_class with the year-mix flag set (honest: index carries the
  same year-attribution debt Brief 7 fixes downstream — build must NOT
  attempt its own year-splitting).
- Base-100 = first MEASURED bar (confidence=n≥3) per player per lane.
- Weights = print-weighted (n-weighted median), NOT value-weighted — a $2,000
  1/1 must not drag the basket (§193 dashboard-mean trap, forbidden here).
- Confidence tags, frozen rules: n≥3 = MEASURED · 1≤n<3 = PROVISIONAL ·
  n=0 = UNMEASURED. Velocity claims only from MEASURED→MEASURED bar pairs;
  PROVISIONAL bars NEVER set velocity (§163 thin-flow doctrine).
- Integrity flag: single instrument >25% of basket weight → WARN + exclude
  that bar from velocity (the CH withheld-rule adopted, banked §209).
- CH pulls use the runtime key (.secrets, read-in-place, never echoed/copied);
  1 call/player/week, inside verified tier limits (10/min, 5k/day).
- Cold-start provenance: a player with <3 bars records `basis: "insufficient"
  in the bar store; no index value published until 3 bars exist.

## OUTPUT CONTRACT (append-only line per bar, per player)

    { "player", "ts", "bars": {"mass": {"index", "n", "velocity_pct", "confidence"},
                               "auto": {...}},
      "auto_mass_ratio", "integrity_flag",
      "ch_cross": {"ch_index", "spread_pct"} | null,
      "index_version": "v1", "constants_version": "2026-10-24" }

## BOUNDS

- BUILD ONLY: `src/rc_index/` + battery script + registry entry (BUILD-NEW,
  same-commit rule, yaml-quoted flow-sequences — the Brief 8 yaml lesson).
- DO NOT touch: bands.json, band_pages.py, contributor_bp.py, watch loop,
  fame_engine (Brief 8 files locked), routes, signatures, Brief 6/7 files.
- NO new parsing logic (reuse lane parser); NO network in the COMPUTE path
  (CH fetch = explicit, separate function, called by weekly job only).
- Index store append-only per player (never rewrite bars).

## ACCEPTANCE — B1–B6 (builder runs; Hermes re-runs independently)

- B1 BANKED-EVIDENCE REPRODUCTION (the answer-key test): rebuild Turang's
  paste history from his parquets (10-16 archives) → mass index must
  reproduce the banked +40% Oct lift (§179) AND the silent-plain-lane
  anomaly (§229.4: plain lane flat while orange rung +43%) — index must
  SEE both banked effects or the baskets are wrong.
- B2 FLIGHT-TO-QUALITY DIRECTION: on the §229.4 corpus, auto_mass_ratio
  must classify OCT as flight-to-quality (ratio rising, bid-supported)
  vs the August baseline — matches the banked divergence read.
- B3 THIN-BAR KILL-SHOT: a synthetic 1-print bar gets confidence=
  PROVISIONAL; velocity from a PROVISIONAL bar = null, not a number.
  Assert no velocity ever emitted from n<3 pairs.
- B4 OUTLIER KILL-SHOT: inject a $2,000 1/1 print into a mass basket —
  median-based weighting must hold the index within ±10% of the n-weighted
  expectation (no dashboard-mean trap).
- B5 DETERMINISM: same parlays → same index twice, byte-identical store rows.
- B6 COVERAGE HONESTY: every player with ≥1 paste logs a row (computed /
  INSUFFICIENT-basis named); CH cross-table rows log even when CH returns
  withheld/missing (spread = null with cause, not skipped).

## VALIDATION AGAINST BANKED EVIDENCE (why the acceptance is strong)

The index doesn't need my expectations as its answer key — the study file
already contains measured events the index MUST reproduce if the baskets are
right: Turang +40% mass lift (§179), plain-lane silence (§229.4), orange-rung
+43% (§229.4), PCA 61→649 index trajectory (§233, CH-side cross-check). If
the index reproduces all four, it's validated against the study's own
history — the same pattern that made F-v2 buildable in one pass.

## OUT OF SCOPE

- Year-attribution split (Brief 7's deliverable; this build flags year-mix,
  doesn't resolve it).
- OBV-store scanner (needs ≥3 consecutive bars/player — this index IS the
  bar-maker for it downstream; §207 spec consumes this output).
- Two-book production build (§230.3, queued behind Brief 7).
- Any customer-facing surface — internal gauge only.
- Founder-ladder changes; award ingests; new event classes.

## STAMP PROTOCOL (unchanged)

Builder reports SHAs only. Hermes: diff audit (no deletions, no locked-file
touches), independent B1-B6 re-run, verifier kill-shots (fake-player no-fab,
append-only, constants-unmutated, plus a new one: velocity-from-provisional
must fail to compute), push, stamp. Verifier alone writes stamps.