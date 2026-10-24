# WALL-E BRIEF 6 — SINGLE-PARSE INVARIANT (contributor paste analyzer)
*Written by Hermes (verifier) Oct 24, 2026. Bug found live: founder's two-channel
paste test caught it same morning. Repro proven by running code, not code-reading.*

## THE BUG (one paragraph)
`parse_pull_dump` in `C:/Users/J/Documents/LLM/card-scout/dashboard/contributor_bp.py`
parses HTML pastes TWICE. Path: bs4 extracts `s-item`/`s-card` listing blocks into
`records` (~line 210-227) — correct. Then the flow falls through and sets
`text_for_lines = soup.get_text("\n")` (~line 232) and re-runs the ENTIRE page text
through line mode (~line 237-241). Every real listing row is therefore parsed again
by line mode, spawning ghost rows from its fragments ("+$5.99 delivery" → $5.99
print, "New (Other)" → price row with carried title), AND page chrome outside the
listing blocks (recently-viewed rails, delivery-fee lines anywhere on the page)
leaks in as rows. Measured damage: founder's Mis pull (page header declares
"153 results for jacob misiorowski topps chrome") rendered as **251 "clean prints"**
with fake $0.78 low and fake $12,000 high (a Turang 1/1 sitting in the
recently-viewed rail). Turang pull (declares 109) inflated the same way.

## THE FIX (one fall-through line + fallback behavior)
WANT: SINGLE-PARSE INVARIANT. When bs4 successfully extracts one or more listing
blocks, the block list IS the complete row set — the page text must NOT go through
line mode at all. Line mode remains ONLY for: (a) non-HTML (typed) pastes —
unchanged, including the Oct-23 context-carry fix; (b) HTML pages where bs4 found
ZERO blocks (unexpected layout) — degrade to today's line mode as the honest fallback;
(c) bs4 import failure / parse exception — same fallback (already exists).

DERIVATION PATH (the exact edit target, contributor_bp.py ~line 231-232):
```python
        # fall through to line mode with the page TEXT for anything blocks missed
        text_for_lines = soup.get_text("\n") if soup is not None else blob
```
Replace with:
```python
        # SINGLE-PARSE INVARIANT (Brief 6, Oct 24): if bs4 extracted blocks, the
        # rows are complete — never re-parse page text through line mode (that
        # double-counted every row and let page chrome in as ghost prints).
        text_for_lines = blob if (soup is None or not records) else ""
```
BUILDERS ADD, NEVER REMOVE: this is a one-line behavioral change; do not
refactor parse_pull_dump, do not touch the row-dominance / search-term /
context-carry resolvers, do not touch band_pages.py, do not "clean up"
anything else in the file.

## ACCEPTANCE TESTS (all must pass; verifier = Hermes alone writes stamps)
A1. **Real-paste fidelity**: take the stored founder HTML deposits in
    `C:/Users/J/Documents/LLM/cardscout-2.0/data_lake/raw/contributor/c3b7db6e562/`
    (Oct 23 pastes) + the synthetic-repro fixture below. Row count for an SRP
    paste must be within ±10% of the page's declared "N results" figure parsed
    from the header; the $0.78/$5.99/$12,000 ghost classes must yield ZERO rows.
A2. **Repro fixture goes green** (paste this test into the new battery):
```python
html = """
<html><body>
<div class="s-item">
  <div class="s-item__title">2026 TOPPS CHROME SAPPHIRE ROOKIE AUTO GOLD JACOB MISIOROWSKI RC /50 PSA 9</div>
  <div>Pre-Owned $1,725.00 82 bids +$5.99 delivery</div>
</div>
<div>
Sold Oct 23, 2026
New (Other)
$1,725.00
82 bids
+$5.99 delivery
</div>
<div class="s-item">
  <div class="s-item__title">TURANG PLATINUM 1/1 RECENTLY VIEWED CHROME</div>
  <div>Pre-Owned $12,000.00 or Best Offer</div>
</div>
<div>+$0.78 delivery</div>
</body></html>"""
res = contributor_bp.parse_pull_dump(html, player_hint=None)
prices = sorted(r["price"] for r in res["rows"])
assert prices == [1725.0] or prices == [12000.0, 1725.0], prices  # NO 5.99, NO 0.78, NO double 1725
```
    (Expected post-fix: exactly the s-item rows, once each. The bare non-s-item
    $12,000 div may legitimately survive via line-mode fallback IF bs4 still
    found blocks — that case is fine ONLY if it cannot double with a block row;
    if it survives, the row must be excluded as chrome — assert no ghost
    delivery-fee rows regardless.)
A3. **Typed-paste regression**: the Oct-23 context-carry behavior survives —
    a title line followed by "Sold ... $X" lines still yields rows with the
    carried title (existing P10/P18 battery contracts unchanged).
A4. **Full regression**: run `scripts/brief5_four_cycles_battery.py` and
    `scripts/contributor_workspace_battery.py` — P9-P19 green, zero new failures.
A5. DEPLOY-ENV-REPRO under uv --python 3.14 --with-requirements dashboard/requirements.txt
    (bs4 present, DOM-mode analyze 200).
A6. PROD-PARITY: after deploy, /health /bands /contributor/login /unsubscribe?t=x all 200.

## PASS / FAIL / NEVER-DELETE (per tasking doctrine)
- PASS = A1-A6 all green + git diff shows ONLY the fall-through change + the new
  battery script (additive).
- FAIL-legal: any acceptance test that cannot pass honestly gets logged as FAIL
  with cause in the battery output. A hidden failure or an edited assert to make
  it pass = the violation. No fabricating row counts.
- NEVER DELETE: existing battery files, P18's results_n 71→73 assert contract,
  any comment block documenting the Oct 23 fixes (row-dominance, search-term,
  context-carry).
- OUT OF SCOPE: lane resolution changes, reward-render wording, watch-tick,
  email lane, year-resolver (Brief 5, already shipped).

## REPORTING
One commit. Report = commit SHA + the seven battery lines (A1-A6 + line-mode
contract) verbatim. No DONE stamp — verifier stamps after re-running the battery
independently. Do not re-verify your own build.
---
## VERIFIER STAMP — VERIFIED-2026-10-24 (Hermes, independent re-run)
BUILDS: card-scout 1578133 (fix, +4/−2 verbatim) + cardscout-2.0 7ebca50 (battery,
additive) — both pushed (af1d42a..1578133 / 3b389cf..8f56fde). WALL-E = 6/6 BRIEFS.

INDEPENDENT VERIFY (verifier re-ran everything, never trusted the report):
- K1 (verifier's own repro): ghost classes CLEARED — no $5.99, no $0.78, $1,725
  exactly once, fixture rows [1725.0, 12000.0] s-items-only ✔
- K2 (verifier's own typed regression): context-carry intact, both rows carry title ✔
- Builder battery re-run verbatim: 6/6 PASS (LM/A1/A2/A3/A5/A4) incl. P9-P19
  subprocess regression + brief5 6/6 + workspace 5/5 ✔
- A6 PROD: pushed → redeployed → /health (3x healthy, db ok), /bands,
  /contributor/login, /unsubscribe?t=x all 200; OG tags still on band page ✔

AMENDMENTS LOGGED (measured, both lawfully grounded in the brief's own invariants):
1. A1's ±10%-of-declared-N: eBay's "N results" heading = CROSS-PAGE TOTAL, so the
   band is unsatisfiable on any real SRP. Fidelity proven STRONGER: rows == blocks
   − "Shop on eBay" chrome, EXACT per slice, ghost classes zero.
2. A2's fixture assert listed the expectation in descending order while sorting
   ascending — asserted per the brief's own comment (s-item rows once each).
   Brief's comment was authoritative; assert order corrected on the builder side.

FINAL LIVE CONFIRMATION (honest residual): code + battery + probes = verified;
the one test that needs the founder's OAuth = re-paste the Mis page through
/contributor — expected post-fix: sane low/high (no $0.78/$12,000), row count
≈ the page's grid. Founder-paste = the acceptance, per the two-channel doctrine
that caught this bug in the first place.
