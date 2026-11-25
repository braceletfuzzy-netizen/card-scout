# POLYSCOUT PHASE-A BRIEF — THE EXECUTION-YIELD ENGINE v1
*Compiled Nov-20-2026 by Hermes from the banked spec (SPINOFF-003 through 003.5). Brief-format: WANT / BOUNDS / DERIVATION-PATH / PROVENANCE per the model-agnostic build protocol.*

## WANT
Build **`build/polyscout_v1_engine.py`** — a Python pipeline that produces one output file: **`build/polyscout_v1_output.jsonl`**, containing one JSON line per city (two cities), plus companion **`build/polyscout_v1_board.html`** (a simple render is optional-Phase-B; the engine deliverable is the JSONL).

## THE SCOPE (BOUNDS)
- **Cities: exactly two.** NEW YORK CITY (NYC) and MEMPHIS (TEN).
- **Metric: exactly one.** EXECUTION-YIELD = municipal budget-in vs service-out, per the banked frame (SPINOFF-002.3/002.7).
- **Time period: the most recent COMPLETE fiscal year** for which both cities have audited or adopted final budgets (per city; label the year per row).
- **NO political commentary, NO promise-scoring, NO subjective "good/bad" language.** Numbers + source-URLs only. This is the study-phase instrument, not an editorial product.

## THE DATA (DERIVATION-PATH)
For EACH city:
1. **Budget-in**: total adopted operating budget for the scored fiscal year. Source = the city's official budget document (NYC: nyc.gov OMB "Adopted Budget" page; Memphis: memphistn.gov finance/budget pages). Record the URL + the retrieval date per row.
2. **Allocation buckets**: parse the budget into the seven banked buckets (SPINOFF-003 L1): mandatory/debt+pensions, public-safety, infrastructure, human-services, education (if city-carried), admin/general, capital. Per-bucket $ + %. If a bucket is unlabeled in the source, record null + note.
3. **Service-outs** (the yield side; the countable-today class per SPINOFF-002.8 Tier-1): for each city gather ANY of the following that the public record supports — police average response time or calls-served; transit boardings; road/pothole counts or lane-miles treated; building-permit days-to-decision; library visits; tons collected. Record each with its source-URL. **Null is a legal value** — never fabricate an unavailable number.
4. **Derived rows**: per-bucket share of total; the execution-yield framing rows (service-out figures with their denominators; a $-per-unit where both budget and count are available for the same service).

## THE OUTPUT SHAPE (one JSON line per city)
```json
{"city": "NYC", "fiscal_year": 2026, "budget_total_usd": 0, "buckets": {"mandatory": {"usd": 0, "share": 0.0, "source": "URL"}, ...}, "service_out": {"transit_boardings": {"value": 0, "denominator_note": "...", "source": "URL"}, ...}, "derived": {"cost_per_transit_ride_usd": 0.0}, "retrieved": "ISO-date", "notes": "null-where-unavailable"}
```

## PROVENANCE RULES (NON-NEGOTIABLE)
- Every number carries its source-URL.
- Unavailable = `"value": null` + a note. **A fabricated number is a build-failure regardless of how complete the table looks.**
- If a document is PDF-heavy, extract what is extractable; bank partial rows honestly.

## VERIFICATION NOTES FOR THE VERIFIER (Hermes)
- Check 3 spot-rows per city against the source-URLs.
- The Memphis rows get founder-eyes ground-truth sampling (the banked arrangement).
- Output = the JSONL + the honest-nulls; the render (HTML board) is Phase-B and NOT part of this build's acceptance.

## RUNTIME
- Walle runs qwen2.5-coder:14b (local). Chunked parsing expected (32k context). No API keys needed — public documents only.
