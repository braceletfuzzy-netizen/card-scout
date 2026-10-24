# WALL-E BRIEF 7 — YEAR-ATTRIBUTED LANE GROUPING + REGISTRY RELABEL SWEEP
*Written by Hermes (verifier) Oct 24, 2026. Founder GO received. Two bugs proven
live by founder check-pastes Oct 24 (§229.1 + §229.2 in the 2.0 study file).*

## WHY (the two proven failure modes, one design flaw)
The Oct-24 founder deposits exposed BOTH sides of the same flaw — year
resolution happens at the wrong layer (paste-level pool, not row-level title):

- MODE 1 (mixed-year paste, Chourio mega-paste, 147 decl): refine_lanes
  (contributor_bp.py:388-419) requires exactly ONE candidate year in the
  paste pool; mixed {2024,2025,2026} -> len(year_cands)!=1 -> match=None ->
  honest miss -> 23 bid-supported 2026 orange prints credited NO lane.
- MODE 2 (single-year paste, Turang 2023 pull, 148 decl): paste pool
  {2023,2024,2026} vs registry candidates ALL legacy-slugged 2025
  (brice-turang-2025-topps-gold-raw n=36 engine-grade etc. — built when
  2025 pulls dominated; Turang's true RC year = 2023). 2025 ∉ pool -> every
  candidate fails year-verification -> honest miss -> zero refinements
  (verified on prod: n=36/n=2 unchanged post-paste).

WORKING AS CODED, WRONG AS DESIGNED: the richest deposit class (mega-paste)
and the cleanest (single-year RC) are BOTH un-creditable today.

## JOB A — YEAR-ATTRIBUTED ROW GROUPING (parse layer)
WANT: each parsed ROW inherits its card year, extracted from THAT ROW'S title
(not the page pool). Group rows by (year, lane, grade_bucket) before refine
matching, so one mixed paste credits each year-lane separately.

DETAILS:
- Year extraction per row: the row title already carries "2023"/"2025"/"2026"
  tokens. Reuse the existing date-stripping logic (contributor_bp.py:331-334)
  at ROW level: strip Sold-date patterns first, then find \b20\d{2}\b. A row
  with NO year token = year None (legacy paths keep working).
- The lane key per group becomes (year, lane_name, grade_bucket) instead of
  (lane_name, grade_bucket).
- refine_lanes matching, per group: candidates already filtered by
  (player, lane_name, grade_bucket) — the year layer then becomes a ROW
  attribute, so a group with year=2023 matches ONLY 2023-slugged lanes;
  a group with year=None falls back to today's exact behavior (legacy match
  or honest miss — never a guess).
- paste_years stays computed (unchanged) for the reward render.
- Honest-miss render text per group should say WHY ("rows say 2023; lanes we
  have for this parallel are labeled 2025" once the relabel sweep exists).

## JOB B — REGISTRY YEAR-RELABEL SWEEP (corpus layer)
WANT: every lane slug's year matches the TRUE card year of the prints it
holds, restored from row-title evidence.

DETAILS:
- Build scripts/relabel_year_sweep.py (2.0 repo): for every registry lane,
  re-derive the majority year from the lane's stored prints' source rows
  (title-year majority; prints store row provenance — if title text is not
  retained per print, derive from the lane's deposit artifacts under
  data_lake/raw/contributor/*/; log per-lane evidence counts).
- Where majority-year != slug-year: create the corrected slug
  (player-year-product-lane-grade per existing format), MIGRATE the lane's
  prints/band/class, and leave the old slug as a REDIRECT alias (band_page
  already 404s unknowns; add slug alias map so old links keep working).
- BUILDERS ADD, NEVER REMOVE: no lane data deleted; the sweep MIGRATES and
  aliases. The old slug never dies.
- REPORT the sweep: per-lane table (old slug -> new slug, n moved, evidence).
  Expected: Turang RC-era family (gold n=36, true-gold n=8, auto-gold n=7,
  gold-refractor n=19, sapphire n=18, wave n=11, numbered n=9, auto cases…)
  relabeled 2025 -> 2023. DO NOT hand-decide which lanes flip except by the
  evidence rule; honest-FAIL any lane with ambiguous evidence and leave it.
- Registry rebuild output stays byte-compatible with load_registry().

## ACCEPTANCE (verifiable, in order)
B1. MODE-2 HEAL: after Job B, re-run the founder's Oct-24 Turang paste text
    (stored in data_lake/raw/contributor deposits / the 2.0 repo scratch if
    not — if absent, reconstruct from the study §229.2 transcription) through
    parse_pull_dump + refine_lanes: the 2023 rows must NOW refine
    brice-turang-2023-topps-chrome-gold-raw (n grows from its post-sweep seed)
    and / or seed correct 2023 lanes from forming state. Prove with before/after
    n values.
B2. MODE-1 HEAL: a mixed-year paste (the Chourio deposit text, same rule)
    credits SEPARATE year-lanes: 2024-orange, 2025-orange, 2026-orange groups
    resolved or honestly-missed PER GROUP (each group's own year, no pooling).
B3. NO MIS-CREDIT REGRESSION: the 2026 gold lane (n=2) does NOT gain 2023-era
    prints (today it survived only because of honest-miss; the fix must keep
    it clean under active matching — assert year layer prevents leakage).
B4. CONTEXT-CARRY + TYPED REGRESSION: typed pastes (no HTML) still parse 1:1
    (Brief 6 LM contract); year=None rows match legacy behavior exactly —
    a typed paste with no year tokens must produce ZERO behavior change.
B5. FULL REGRESSION: brief5_four_cycles_battery.py + brief6_single_parse_battery.py
    + contributor_workspace_battery.py all green, zero new failures.
B6. DEPLOY-ENV-REPRO (uv -p 3.14 --with-requirements) + PROD: /health,
    /bands, /contributor/login, /unsubscribe?t=x -> 200; relabeled slugs 200;
    old slugs 200 via alias redirect (not 404).

## PASS / FAIL / NEVER-DELETE (per tasking doctrine)
- PASS = B1-B6 green + registry sweep report committed + zero unexplained
  deletions (builders ADD; only migrations-with-alias legal here).
- FAIL-legal: any lane/year ambiguity logged as honest FAIL with cause in the
  sweep report. Editing asserts to pass = violation. No fabricated evidence counts.
- NEVER DELETE: any lane/prints/band data, existing batteries, P-contracts,
  the Brief 5/6 comment blocks, the abp->abort fix (a048b2b), redirect aliases
  once created.
- OUT OF SCOPE: lane taxonomy changes (LANE_TAXONOMY untouched), reward-render
  wording beyond the miss-reason line in Job A, watch-tick/email/EPN lanes,
  any price-logic change (bands still founder-governed; this brief touches
  attribution only).

## REPORTING
One commit per repo (dashboard fix in card-scout; sweep script + battery in
cardscout-2.0). Report = SHAs + B1-B6 lines verbatim + the relabel table + the
honest-FAIL list if any. No self-stamps — verifier re-runs everything and
stamps; final live confirmation = founder re-paste of the Turang golds pull.