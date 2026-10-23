# WALL-E BRIEF 2: THE CONTRIBUTOR WORKSPACE (paste → parse → reward)
*Issued Oct 23 AM, founder GO ("Let's do it") — auth shape = SECRET URLs (founder default accepted). Build NOW, this cycle. Spec base = CARD-PAGE-BUILD-SPEC-v1.md + access-tenure + reward loop.*

## THE JOB (one sentence)
Build the gated contributor surface: contributors paste eBay pull-dumps into a private
page → the machine parses them (the standard funnel, locally) → the page returns their
REWARD: the custom graph (their paste's distribution curve, the lane's refined band,
the before/after width delta with their credit line, BIN-sorted listings for the refined
lane, the gratitude state) + the contributor-ledger tick.

## AUTH (FOUNDERS REVISED AM Oct 23: GOOGLE LOGIN — attribution to PERSON, not token)
- Auth = Google OAuth2 (the EXISTING /admin/login/google pattern in app.py —
  GOOGLE_CLIENT_ID/SECRET env flow, requests_oauthlib already in requirements).
- Attribution: OAuth email → contributor identity → ledger rows keyed BY PERSON.
  (Founder-corrected rationale: track attribution to the PERSON across devices,
  tokens-by-URL lose attribution the moment a URL is shared.)
- Workspace gating: contributor must exist in the contributor roster (email-match
  in .env CONTRIBUTOR_EMAILS list — founder-curated roster, config-not-hardcode);
  any OTHER Google-email = clean redirect to /bands, zero interior render (P9).
- No password created (founder hates new passwords; Google = the banked
  login preference). The old secret-URL pattern = FALLBACK ONLY (documented,
  not primary) for offline/local sessions if needed.

## THE PASTE → REWARD LOOP (the page's flow)
1. PASTE: one large textarea, accepts any pull-dump text (multi-page pastes fine,
   ~200KB cap). 'Analyze paste' button.
2. PARSE: deposit row lands (data_lake/raw/contributor/<name>/<ts>_paste.txt) +
   the STANDARD parser runs (lane-split, print/ask/gate per Two-Class law —
   engine-grade always, locally).
3. REWARD RENDER (the graph page after parse):
   - YOUR PASTE'S DISTRIBUTION: the histogram/curve of prices from THEIR paste,
     lane-split by the parser (their search's yield, shown honestly — junk
     excluded w/ NO-IN-SPEC cause counted, never silent)
   - THE LANE REFINED: before/after band comparison IF their paste feeds a known
     lane: 'this lane's band went from $[wider] → $[narrower] — YOUR paste
     narrowed it 42%. Credit: freshest pull.' (the credit-decay display)
   - BIN-SORTED LISTINGS for the refined lane (the standard lower-half, with
     EPN-tagged links if armed — plain otherwise)
   - GRADE STATE: the lane's honesty label after their contribution
     (PROVISIONAL n=X → maybe ENGINE-GRADE n=Y — the upgrade moment called out)
   - LEDGER TICK: their contributor row +1 (the ledger = append-only json,
     data_lake/contributor_ledger.json, auto-maintained)
4. THANKS + NEXT: gratitude text + the refinement tip (teaching-the-search law:
   ONE sentence suggesting a refined query for a tighter band next time)

## BOUNDS (the never-list, inherited + new)
- NEVER publish anything from this workspace (one-way private surface; no public
  links; no index; robots-disallow)
- NEVER leak positions/engine output/z-scores/band-numbers in the reward render
  (band display = mechanics per public law; the graph = DISTRIBUTIONS not thresholds)
- NEVER send Discord/email push from this surface (beta push = separate lane, untouched)
- NEVER break if the parse fails: 'analysis failed — paste was not parseable' +
  the NO-IN-SPEC cause = an honest 200, never a 500 (P10e)
- PII ledger rule (revised): the ledger keys on GOOGLE EMAIL (person-attribution,
  founder-directed) — name+email+counts+lanes only; no other PII ever

## ACCEPTANCE (P9–P11; Hermes runs after build)
- P9 AUTH: non-roster Google email, logged-out direct-access → all redirect to
  /bands; zero interior render; robots.txt gains the workspace disallow;
  roster-emails → interior renders; attribution = email-keyed ledger rows
- P10 END-TO-END: real paste (use a sample from data_lake raw pastes) → parses →
  lane refines → before/after renders → ledger ticks +1 → listings render. PLUS
  paste-fail → honest-200 error page w/ cause (never 500)
- P11 PRIVACY: workspace HTML contains zero contributor data of OTHER contributors
  (Jim sees only Jim); the ledger rendered = own rows only
- Inherited: P4 secrets sweep re-run on every new render path
## REFERENCES
- Spec v1 (the parent): For You/plans/2026-10-22-CARD-PAGE-BUILD-SPEC-v1.md (cardscout-2.0)
- Tenure law + credit-decay display: same file, Oct-23 appendices
- Registry/artifact pattern: dashboard/registry/card_page_registry.json (built)
- Parser to invoke: the 2.0 funnel's lane-splitter — copy of
  scripts/build_card_page_registry.py's parsing core, imported LOCALLY (not Render-side)
- NOTE: workspace = LOCAL-ONLY PHASE 1 (localhost bind, founder + Jim when he visits
  the machine) OR Render-deploy behind tokens — FOUNDER CALL AT BRIEF REVIEW (deploy
  later if Jim is remote; localhost now is legal: Jim sends pastes by Discord to the
  founder who pastes into the workspace = fully manual, no infra).

## STATUS: BRIEF REVISED IN PLACE (founder correction AM): auth = GOOGLE LOGIN (person-attribution; roster-gated). WALL-E GO stands. Verify = Hermes P9-P11 (P9 = roster-gate tests) + inherited sweeps. No stamps until then.
