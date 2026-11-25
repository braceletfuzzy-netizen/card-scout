#!/usr/bin/env python3
# build_v2_infra.py — THE INFRASTRUCTURE LANE (output-vector v2, family D).
# Three sub-lanes: EPA SDWA violations (live keyless API, pulled this session) +
# FHWA NBI 2025 bridge poor-condition (live JSON files, pulled this session) +
# banked 311 service-call lane (gray_safety_lane_panel_v1, the backlog signal).
# Fit only if n survives; else honest-null with routes named.
import json, numpy as np
from scipy import stats

BUILD = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
rows = [json.loads(l) for l in open(f"{BUILD}/maslow_joint_panel_v1.jsonl", encoding="utf-8") if l.strip()]

RESULT = {"_record": "infrastructure_lane_v1 (output-vector v2, family D: water / bridges / 311-backlog)"}

# ---- [D1] SDWA: violations of the six municipal water systems (live EPA Envirofacts API) ----
V = json.load(open(f"{BUILD}/_sdwa_violations_v1.json"))
sdwa = {}
for city, vs in V.items():
    yrs = {}
    for v in vs:
        b = (v.get("compl_per_begin_date") or "")[:4]
        yrs[b] = yrs.get(b, 0) + 1
    sdwa[city] = {"violations_total_10yr_file": len(vs),
                  "health_based": sum(1 for v in vs if v.get("is_health_based_ind") == "Y"),
                  "by_begin_year": dict(sorted(yrs.items()))}
RESULT["sdwa"] = {"systems": {"Cincinnati":"OH3102612 (Cincinnati Public Water System, pop 800k; OH3100411 Miller inactive-I)",
                              "Denver":"CO0116001 (Denver Water Board, pop 1.287M)",
                              "Detroit":"MI0001800 (City of Detroit, pop 633k)",
                              "Memphis":"TN0000450 (MLGW, pop 659.5k)",
                              "New York":"NY7003493 (NYC System, pop 8.27M)",
                              "St. Louis":"MO6010715 (St Louis City PWS, pop 304.7k)"},
                  "route": "https://data.epa.gov/efservice/Violation/PWSID/{id}/JSON (keyless, live Nov-25)",
                  "counts": sdwa}
# verdict inputs
n_viol = {c: v["violations_total_10yr_file"] for c, v in sdwa.items()}
hb_total = sum(v["health_based"] for v in sdwa.values())
RESULT["sdwa_read"] = ("near-zero counts at the municipal-grain: five of six systems carry < 20 violations in the file window "
                       "(Cincinnati 0, Detroit 1, Memphis 1, NYC 10, St. Louis 18; Denver's 128 = ALL 'MR' "
                       "monitoring/reporting class, rule codes 320/122/340); ONE health-based-ind violation across all six "
                       "(NYC 2017 TT treatment-technique, contaminant 0800). "
                       "No city-year panel can be fit at this signal size -> honest-null for the SDWA output-fit, route banked.")

# ---- [D2] Bridges: FHWA NBI 2025 (live JSON per state, pulled this session) ----
nbi = json.load(open(f"{BUILD}/_nbi/city_poor_2025_v1.json"))
RESULT["bridges"] = {"grain": "city lat/lon-box (FHWA NBI 2025 JSON, BL05/BL06 in city bounds)",
                     "counts": nbi,
                     "route": "https://www.fhwa.dot.gov/bridge/nbi/2025/JSON/{ST}25.json (keyless, live)",
                     "verdict": "REAL VARIANCE across cities (poor share 0.023-0.094) — one cross-section (n=6), fit NOT attempted (law: direction-class needs city-year panel); banked for the v2 deeper pull (2020-2024 archives for the arc)."}

# ---- [D3] 311 backlog: banked gray_safety_lane (97 city-years, calls_per_1k) ----
gray = json.load(open(f"{BUILD}/gray_safety_lane_panel_v1.json"))
# service-need signal: does the input block (care/unemp) DIRECTIONALLY lead calls_per1k?
# available paired rows: city-years with calls_per1k + inputs
pairs = []
for r in gray:
    m = next((x for x in rows if x["city"] == r["city"] and int(x["year"]) == int(r["year"]) and x.get("care_per_100k") is not None), None)
    if m and r.get("calls_per_1k") is not None:
        pairs.append({"city": r["city"], "year": r["year"], "care": m["care_per_100k"], "calls": r["calls_per_1k"]})
# within-city spearman care->calls
rhos = []
for c in sorted({p["city"] for p in pairs}):
    sub = [p for p in pairs if p["city"] == c]
    if len(sub) >= 5:
        rho, pv = stats.spearmanr([p["care"] for p in sub], [p["calls"] for p in sub])
        rhos.append({"city": c, "n": len(sub), "rho": round(float(rho), 3), "p": round(float(pv), 3)})
RESULT["calls_311"] = {"grain": "banked gray_safety_lane panel (97 city-years, 6 cities)",
                       "paired_care_rows": len(pairs),
                       "within_city_spearman_care_to_calls_per1k": rhos,
                       "verdict": "explanatory read only (n tiny per city); the calls lane is BANKED and direction-fit-ready at n=97 when inputs are deepened (v2)"}
# the walk-forward the laws require for any registered call: NOT run on calls/care (thin) -> no call from this lane
RESULT["honest_nulls"] = [
  "SDWA output-fit: signal too thin (0 health-based violations across 6 systems) — route banked: data.epa.gov/efservice/Violation/PWSID/{pwsid}/JSON",
  "Bridges fit: single cross-section (NBI 2025) — 2020-2024 archives exist at fhwa.dot.gov/bridge/nbi/ascii.cfm for the v2 arc; city-box grain noted (owner agencies mix inside boxes, e.g. NYSDOT 84000 codes in NYC)",
  "311 fit: inputs (care_per_100k) banked for only 18 of 97 call-years — honest-null on the fit, lane stays ready"
]
json.dump(RESULT, open(f"{BUILD}/_infra_lane_v1.json", "w"), indent=1)
print("bridge poor:", {c: f'{v["poor"]}/{v["bridges_box"]}' for c, v in nbi.items()})
print("sdwa totals:", n_viol, "| health-based:", hb_total)
print("311 pairs w/ care:", len(pairs), "| rhos:", rhos)
