# WALL-E BRIEF 8 — FAME-VECTOR v2: REMOVE THE FOUNDER FROM F
*Hermes-written (verifier), Oct 24 evening, founder go assumed from session*
*context ("give me a spec for Hugo so it isn't dependent on me"). One-liner
handoff: "Brief 8: fame-vector v2. Read the brief, build to the spec, run
the B1-B6 battery, report with SHAs — no self-verify."*

---

## WANT (the deliverable)

`src/fame_engine/fame_vector_v2.py` + calibration store, replacing the
founder-filled F-E ladder (§190) as the fame (F) input to the pricing
matrix (§230.2-§230.3):

    Price = $1 base × Scarcity_rung × [ F(WAR_accum, converted) + g·E(WAR_future) ]

F becomes COMPUTED from three triangulation channels (§232), CALIBRATED
against measured price-shadows, and REFRESHED per pull — with the founder
ladder retained only as a cold-start prior when n < 3 measured players
exist at a fame class.

## DERIVATION PATH (mandated, per GN0 — every value traced or it fails)

**Channel 1 (CAUSES — predicts):**
- Source of truth: `data_lake/silver/mlb_stats/fangraphs/player_war_seasonal.parquet` (184k rows, verified this session) + award/honor tables already in-lake (award_predictions / alpha_award_signals) + Cot's contract pages if needed for context only (never for F).
- Honor exchange-rates (frozen constants, cite §230.3 banked values): MVP=25.7, CY=17.5, ASG=10.0, RING=4.0, GG=3.0, ROY=2.0. NO invented fifth honors class without founder note in the PR.
- Accumulated book per player = Σ(career WAR) × retention-prior × honor-WAR-eq added on top. Retention priors FROZEN at banked values: hitters 0.67, pitchers 0.55, young-pitcher 0.56 (§191). Availability/chronicity discount = §203/§206 engine outputs where present.

**Channel 2 (PRICE-SHADOWS — calibrates):**
- Source of truth: measured fame floors, already banked: role $15–25 / star $70–90 / mega $140–225 (11-for-11, §184). These enter ONLY as calibration targets, never as F inputs.
- Per player with measured floor: calibration residual = computed-F class vs measured-floor class; store row in `fame_calibration.jsonl` (append-only).

**Channel 3 (DYNAMICS — classes):**
- Quiet-accumulator score = consecutive-AS-count + milestone-proximity (2000H/250W/300SV from in-lake career totals) + rolling top-15% persistence (window 3yr). Output: class label (ACCUMULATOR | SPIKE-FADE | MIXED) + score 0-100.
- Retention prior SELECTED by class (accumulator keeps prior; spike-fade
  multiplies prior × 0.8 — §232 spike-counter-gauge).

## OUTPUT CONTRACT (compute the F number, not a label)

    F_score 0.0-1.0 normalized (the band input), per player, with channel decomposition:
      { "player": str, "F_score": float, "class": str, "channels":
        { "causes": float, "shadows_calibrated": bool, "dynamics_class": str },
        "war_accum_converted": float, "e_war_future": float, "g_gate": float,
        "priors_used": {...}, "frozen_constants_version": "2026-10-24" }
- g gate: 1.0 active, 0.0 retired (§230.3), fractional for injured/unavail per §203.
- NO founder judgment anywhere in the compute path. Founder ladder (role/star/mega)
  = COLD-START PRIOR ONLY when the calibration store has <3 rows at that class.

## BOUNDS

- BUILD ONLY: `src/fame_engine/` (new dir) + one entry in
  `config/model-construction-registry.yaml` (REUSE/REFINE/BUILD-NEW parse protocol).
- DO NOT touch: band_pages.py, contributor_bp.py, bands.json, watch loop,
  E3 digest, public_site.py, any route, any existing module's signature.
  (BUILDERS-ADD-NEVER-REMOVE + Brief-6/7 files locked.)
- Oct-23 fix comments locked (row-dominance etc.) per NEVR-DELETE contract.
- NO network in the compute path (lake data only; Cot's/web are spec-time, not runtime).
- NO secrets rendering; no .env reads in fame module (award keys read in-place
  by the existing ingest only).

## ACCEPTANCE — B1–B6 (builder runs; Hermes independently re-runs before stamp)

- B1 KNOWN-PLAYERS FIDELITY: computed F classifies Turang (0.80 composite,
  MVP-14th signature) / Kwan (star-production role-priced) / Chapmans
  (priced-in decay) consistently with banked verdicts — Turang=DISLOCATION,
  Chapman=PRICED-IN must NOT flip classes. Tolerance: class matches, score ±0.05.
- B2 CALIBRATION TABLE: ≥3 measured-floor players produce calibration rows;
  residual <1 class-step for each; store grows append-only (NEVER delete rows).
- B3 G-GATE KILL-SHOT: retired-player probe (e.g. a banked HOF row) computes
  with g=0.0 and future term exactly 0 — no NaN, no silent skip; assert in test.
- B4 RETENTION KILL-SHOT: spike-fade probe (e.g. 40HR-3yr synthetic career)
  drops class vs same-WAR accumulator — assert separation ≥ one class-step.
- B5 DETERMINISM: same inputs → same F twice (§verify-gate pattern); score
  drift <0.01 across reruns in same session.
- B6 COVERAGE HONESTY: every player attempted logs an OUTPUT row — computed,
  or NO-DATA with cause named (player not found / season missing / honors
  table gap). Exit-0-masking-missing-players = FAIL (§evaluation-coverage
  standard, 3rd-instance class — builder knows this one).
- SELF-VERIFY FORBIDDEN. Verifier (Hermes) re-runs all six + diff audit +
  kill-shots before any stamp. Builder reports SHAs only.

## WHY THIS NOW (context for the builder)

- §232 (tonight): fame quantification = the LAST founder-judgment dependency
  in the pricing matrix. §232's spec is this brief's skeleton; exchange rates
  + retention priors + floors are all measured/banked constants — build is
  wiring, not research.
- Feeds: FMV engine Layer-2 (§230.2 intercept), flash-to-bang upgrade rule
  (§231.2), and every future band-build (F becomes computed input).
- Success looks like: founder pastes rows → arms run → F values arrive
  computed-with-provenance → nobody waits on founder judgment for F.

## OUT OF SCOPE (next briefs, not this one)

- OBV-store scanner (bars exist post-CardHedge, separate build).
- Two-book decomposition production build (§230.3 Hugo-queue item — lands
  AFTER F-v2, since it consumes F).
- Any customer-facing output; the DEAL-faucet wiring; Brief 7 year-attribution
  (separate, in flight).