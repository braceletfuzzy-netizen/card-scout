#!/usr/bin/env python3
# gauntlet_step5.py — THE PANEL-CHURN AUDIT: every city-year DROP event the panel carries,
# from banked gap lists + months-guard fails + partial-year flags. Question: how much history
# exists ONLY because a city kept publishing?
import json
import numpy as np

BUILD = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
outcome = json.load(open(f"{BUILD}/_backwards_outcome_series_v1.json", encoding="utf-8"))
panel = [json.loads(l) for l in open(f"{BUILD}/maslow_joint_panel_v1.jsonl", encoding="utf-8") if l.strip()]
O = {(k.split("|")[0], int(k.split("|")[1])): v for k, v in outcome.items()}

import collections
by = collections.defaultdict(list)
for (c, y) in O: by[c].append(y)
for c in by: by[c].sort()

# interior gap lists (recomputed from the banked file itself — every number traces)
GAPS = {}
for c, ys in by.items():
    lo, hi = ys[0], max([y for y in ys if y <= 2025])  # 2026 partials excluded from span logic
    missing = [y for y in range(lo, hi + 1) if y not in by[c]]
    if missing:
        GAPS[c] = {"window": f"{lo}-{hi}", "missing_years": missing, "n_missing": len(missing),
                   "span_years": hi - lo + 1, "present": len([y for y in by[c] if y <= 2025])}

# months-guard events (banked)
MONTHS_GUARD = {}
for fn in ["crime_wide.jsonl", "crime_wide_b.jsonl", "crime_wide_c.jsonl"]:
    for l in open(f"{BUILD}/{fn}", encoding="utf-8"):
        if not l.strip() or l.startswith("#"): continue
        r = json.loads(l)
        m = r.get("months_present", r.get("months_reported"))
        if m is None: continue
        mp = int(r.get("months_reported", m)) if r.get("months_reported") is not None else int(m)
        if mp < 12:
            c = r.get("city") or "?"
            MONTHS_GUARD.setdefault(c, {})[int(r["year"])] = {"months": mp, "src_file": fn}
# dedupe years
MG = {c: {y: v for y, v in sorted(d.items())} for c, d in MONTHS_GUARD.items()}

# partial-year class (banked)
PARTIALS = sorted([k for k, v in O.items() if "partial_year_flag" in v])

# the panel's own cities: how much of each city's span is PRESENT
panel_cities = sorted({r["city"] for r in panel})
panel_span = {}
for c in panel_cities:
    ys = by.get(c, [])
    years_panel = sorted({r["year"] for r in panel if r["city"] == c})
    lo, hi = min(years_panel), max(years_panel)
    panel_span[c] = {"panel_rows": len(years_panel), "panel_span": f"{lo}-{hi}",
                     "panel_span_years": hi - lo + 1,
                     "outcome_cells_present": len(ys),
                     "outcome_interior_gaps": GAPS.get(c, {}).get("missing_years", []),
                     "input_lane": "care/cage city-books (Cincinnati 2004-2025; Detroit 2012+; Memphis 2021+; NYC IBO 1980+; St. Louis 2019+; Denver 2021-2023 no-denominator)"}

# the headline fraction: cells carried vs window-size if everything published
sweep = []
for c, ys in sorted(by.items()):
    ys_eff = [y for y in ys if y <= 2025]
    if not ys_eff: continue
    lo, hi = min(ys_eff), max(ys_eff)
    span = hi - lo + 1
    present = len(ys_eff)
    sweep.append({"city": c, "window": f"{lo}-{hi}", "span_years": span, "present": present,
                  "carry_fraction": round(present / span, 3),
                  "dropped_years": GAPS.get(c, {}).get("n_missing", 0),
                  "class": ("panel city" if c in panel_cities else
                            "months-guard (non-reporting years dropped, never zeroed)" if c in MG else
                            "wide-lane (input $ never pulled — outcome cells only, no fit)")}
                 )
tot_present = sum(s["present"] for s in sweep)
tot_span = sum(s["span_years"] for s in sweep)
tot_dropped = sum(s["dropped_years"] for s in sweep) + sum(len(v) for v in MG.values())

audit = {
  "headline": {
    "outcome_cells_banked": len(O),
    "city_year_window_span_total": tot_span,
    "city_years_present": tot_present,
    "city_years_dropped_interior": tot_dropped,
    "history_carry_fraction": round(tot_present / (tot_present + tot_dropped), 3),
    "read": "of every city-year that EXISTS in the banked windows, this fraction survived to a banked cell; the rest are drop events (publication stops, month-guards, format breaks) — the panel's history exists only where a city kept publishing through all of these.",
  },
  "per_city_sweep": sweep,
  "months_guard_events": MG,
  "partials_2026_class": PARTIALS,
  "panel_city_spans": panel_span,
  "banked_drop_events_named": {
    "St. Louis 2003-2009": "7-year interior publication gap (banked outcome series)",
    "New Orleans 1990-2024": "22 interior missing years across the span (banked); NOLA 2025 = 0/12 months non-reporting excluded (banked months-guard)",
    "Houston 2004-2026": "13 interior missing years (banked); care-gap years 2011/2019-class carried labeled (nola_houston_pair banked)",
    "Raleigh 2015-2018": "4-year gap after the 5/12-months 2014 report (banked months-guard)",
    "Boston 1980-2026": "33 interior missing years (banked); 2026 partial excluded",
    "Jacksonville 2011-2020": "10 consecutive non-reporting years 0/12 months (banked NULL-guard class) — the no-bookings class founder-named",
    "Omaha/Fresno/Baltimore/Long Beach/Sacramento/Tucson/SF/Phoenix/Pittsburgh": "single-year or two-year months-guard drops (banked)",
    "Detroit 2014/2017/2018 + 2026 11-months": "interior publication gaps + partial (banked)",
    "Denver": "care dollars only, no murder denominator in the panel window (eff-panel guard, banked)",
    "NYC pre-2021": "no ACS inputs (honest-null input side); NYC carries 45 panel rows on IBO care lane but only ONE complete predicted city-year (2001; eff-panel banked)",
    "PIT homelessness 2013/2016": "HUD published nothing at per-CoC route (banked honest-null, never backfilled)",
    "eviction judgments 2020-21": "COVID freeze flags (banked)",
    "TX state MH budget biennial": "state-lane years excluded (banked)",
  },
}
with open(f"{BUILD}/_gauntlet5_churn_audit.json", "w", encoding="utf-8") as f:
    json.dump(audit, f, indent=1, ensure_ascii=False)
print(json.dumps(audit["headline"], indent=1))
print()
for s in sweep:
    if s["class"].startswith("panel") or s["dropped_years"] or s["carry_fraction"] < 1:
        print(f'{s["city"]:16s} {s["window"]:10s} span {s["span_years"]:3d} present {s["present"]:3d} dropped {s["dropped_years"]:3d} carry {s["carry_fraction"]}')
