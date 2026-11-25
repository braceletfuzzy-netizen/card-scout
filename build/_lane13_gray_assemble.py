"""Assemble gray_safety_lane_v1.json — the BOB-19 gray-safety/code-enforcement lane artifact."""
import json, collections, os
from datetime import datetime

B = "C:/Users/J"
IN = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
NOW = "2026-11-24"

panel = json.load(open(f"{B}/gray_safety_lane_panel_v1.json"))
tests = json.load(open(f"{B}/gray_safety_lane_tests_v1.json"))
mem = json.load(open(f"{B}/_lane13_gray_memphis_311_raw.json"))
det = json.load(open(f"{B}/_lane13_gray_detroit_raw.json"))
cin = json.load(open(f"{B}/_lane13_gray_cincinnati_raw.json"))
hou = json.load(open(f"{B}/_lane13_gray_houston_raw.json"))
stl = json.load(open(f"{B}/_lane13_gray_stlouis_raw.json"))
nyc = json.load(open(f"{B}/_lane13_gray_nyc_year_counts.json"))
lit_pnas = open(f"{B}/_lane13_gray_lit_pnas_abstracts.json").read()
lit_core = open(f"{B}/_lane13_gray_lit_core_abstracts.json").read()

n_rows = len(panel)
cities = sorted({r["city"] for r in panel})
murder_matched = sum(1 for r in panel if r["murder_rate_t0"] is not None)

# top-8 code-enforcement-class types for Memphis 2026 (the built-environment core)
mem_t = mem["types_by_year"]["2026"]
ce_classes = [
    k for k in mem_t
    if any(s in k for s in ["Overgrown", "Vacant", "Graffiti", "Illegal Parking", "Illegal Dumping",
                             "Dangerous Premise", "Junk Vehicle", "Structure Maintenance", "Permit"])
]
ce_2026 = {k: mem_t[k] for k in ce_classes}
ce_total_2026 = sum(ce_2026.values())

# Detroit 2026 top types
det_t = det["types_by_year"]["2026"]
det_top = dict(sorted(det_t.items(), key=lambda x: -x[1])[:6])

lane = {
    "_record": "gray_safety_lane_v1",
    "built": NOW,
    "built_by": "LANE-BUILD 2/3 subagent — BOB-scan-19 blind-spot lane 'safety_gray_band' (the-bob_scan_19_blindspot_v1.json @827fe67 + lane_bob19_safety_gray.md brief)",
    "parent": {
        "scan": "bob_scan_19_blindspot_v1.json (commit 827fe67, cardscout-2.0)",
        "lane_doc": "For You/PolyScout/build/_bob19_blindspot_lanes/lane_bob19_safety_gray.md",
        "priority": "P1 — 'the STRONGEST live lit of any blind-spot lane'",
    },
    "laws_held": [
        "direction-class only, no causal claims",
        "honest-null = routes-tried-no-capture, never a placeholder (2015 STL file byte-empty = missing row, not zero)",
        "no fabricated rows — every count read live from keyless APIs or downloaded open files this pass",
        "the grain-law: county/static inputs named as companion pulls, never blended into the city-year panel",
        "format-lock: extends the lane12 arc-column convention (murder_rate_t0/t+1/t+2 mirrors lane12_component_timearcs)",
        "system-change flags: Houston 2026 count is a DIFFERENT upstream system (Recent-SR FeatureServer, not the archives MapServer) — flagged, never silently spliced into the archive series trend",
    ],
    "panel": {
        f"gray_safety_lane_panel_v1.json": {
            "rows": n_rows,
            "cities": cities,
            "cities_covered": len(cities),
            "grain": "city x year",
            "columns": ["city", "year", "calls", "population", "calls_per_1k",
                        "calls_per1k_t+1", "calls_per1k_t+2", "murders",
                        "murder_rate_t0", "murder_rate_t+1", "murder_rate_t+2", "population_class"],
            "murder_matched_rows": murder_matched,
        }
    },
    "exposure_side": {
        "definition": "gray = the built-environment enforcement channel: 311/service-request volume + code-enforcement class shares per city-year (calls-by-type at city-year grain)",
        "pull_routes_verified_live": {
            "Memphis": {"platform": "ArcGIS FeatureServer (services.arcgis.com g1fRTDLeMgspWrYp, City of Memphis org)",
                         "dataset": "311 All Service Calls (dataset 754d5490... on data.memphistn.gov hub api/v3)",
                         "auth": "keyless AGOL query — NO Socrata (data.memphistn.gov is ArcGIS Hub, NOT Socrata; /api/catalog 404s)",
                         "years": {str(k): v for k, v in mem["year_counts"].items()},
                         "note": "system only carries bulk volume 2024+ (2020-2023 rows ~1-640/yr are carry-over artifacts); within-city test restricted to the 2024-2026 dense window via 2024 anchor",
                         "calls_by_type_top2026": dict(sorted(mem_t.items(), key=lambda x: -x[1])[:8]),
                         "code_enforcement_class_2026": {"classes": ce_2026, "class_total": ce_total_2026,
                                                          "share_of_all_calls": round(ce_total_2026 / sum(mem_t.values()), 4)}},
            "Cincinnati": {"platform": "Socrata (gcej-gmiw 'Cincinnati 311 (Non-Emergency) Service Requests')",
                            "auth": "keyless Socrata — full open portal, NO AUTH",
                            "years": {str(k): v for k, v in cin["by_year"].items()},
                            "calls_by_type_groups_per_year": "up-to-82 group_desc classes per year captured in raw file"},
            "Detroit": {"platform": "ArcGIS FeatureServer (services2.arcgis.com qvkbeam7Wirps6zC 'improve_detroit')",
                         "auth": "keyless AGOL (data.detroitmi.gov is ArcGIS Hub Utility, not Socrata)",
                         "years": {str(k): v for k, v in det["by_year"].items()},
                         "total_rows_platform": 767131,
                         "calls_by_type_top2026": det_top},
            "StLouis": {"platform": "stlouis-mo.gov CSB open-data zip (one CSV per year) + PowerNap API (keyless, api_key-in-page)",
                         "auth": "keyless download (data-files/csb.zip, 129 MB, 19 year-files)",
                         "years": {str(k): v for k, v in stl["by_year"].items()},
                         "honest_nulls": ["2015.csv shipped byte-empty in the official zip = 2015 row is MISSING-not-zero (routes-tried: zip re-read twice, file is 0 bytes on the city server)"]},
            "NYC": {"platform": "Socrata erm2-nwe9 (2020-present) + 76ig-c548 (2010-2019)",
                     "auth": "keyless Socrata groupBy",
                     "years": {**{str(k): v for k, v in nyc["2010_2019"].items()}, **{str(k): v for k, v in nyc["2020_present"].items()}}},
            "Houston": {"platform": "mycity2.houstontx.gov AGOL: Houston311_Archives/MapServer (5,849,463 rows, 2012-2025) + HOUSTON311_RECENT_SR_SNOW FeatureServer (2025-2026)",
                         "auth": "keyless REST queries on the city's own GIS host",
                         "years": {**{str(k): v for k, v in hou["archives_by_year"].items()},
                                    "2026": hou["recent_by_year"]["2026"]},
                         "system_change_flag": "2026 count comes from the newer Recent-SR system (50k-row slice); archives MapServer ends 2025. NOT summed across systems.",
                         "calls_by_type_examples": {"2023": dict(sorted(hou["archives_types_by_year"]["2023"].items(), key=lambda x: -x[1])[:5])}},
        },
    },
    "outcome_side": {
        "murder_rate": "banked murders_all_v1.json (558 city-years) + population bank (population_series_v1 + populations_cities_v2 + populations_wide_v1 + phase2_pop_table), same series and classes as lane12 — never re-derived",
    },
    "tests": {
        "design": "within-city-demeaned pooled Pearson (mirrors lane12 'pooled-within-city-z' machinery; n-thin panels -> direction-class + t-approx, no p-value claims)",
        "cells": tests["tests"],
        "per_city_within_r_raw_t0": tests["per_city"],
    },
    "verdict": [
        f"{len(cities)} of 6 cities CAPTURED (Memphis, Cincinnati, Detroit, St. Louis, NYC, Houston — all keyless, no-auth): {n_rows} city-year gray rows, {murder_matched} murder-arc-matched",
        "WITHIN-CITY-Demeaned joint verdict: t0 ~ZERO (r=+0.006, n=53) — same-year gray-call volume does NOT track same-year murder rate within cities",
        "the FORWARD arc is POSITIVE and consistent: t+1 r=+0.344 (n=43), t+2 r=+0.394 (n=37) — years with MORE gray/311-call volume tend to be followed by HIGHER murder rates",
        "reverse arc ~zero (murder_t0 -> calls_t+1 r=+0.027) — the pull does NOT run from murder to later calls; direction runs enforcement-volume -> or co-driver with -> the lagged margin, direction-class only",
        "per-city signs are non-uniform (Memphis -0.76, Cincinnati -0.40, Detroit -0.42, Houston -0.86 vs St. Louis +0.51, NYC +0.24): the pooled forward-positive is NOT a within-city law — honest read is city-heterogeneous",
        "HONEST-NULL banked: STL 2015 absent (empty official file); Memphis pre-2024 (system carries volume only 2024+); Houston system-change flag on 2026",
    ],
    "lit_magnitude": {
        "pull": "PubMed eutils (keyless) full abstracts stored in _lane13_gray_lit_core_abstracts.json + _lane13_gray_lit_pnas_abstracts.json",
        "AJPH_2016_Branas (PMID 27736217, dj 10.2105/AJPH.2016.303434)": {
            "design": "quasi-experimental, 5,112 abandoned buildings/vacant lots, Philadelphia 1999-2013",
            "magnitudes": ["abandoned-building remediation: firearm violence -39% (95%CI -28 to -50, p<0.05)",
                            "vacant-lot remediation: firearm violence -4.6% (95%CI -4.2 to -5.0, p<0.001)",
                            "ROI: $5 taxpayer / $79 societal per $1 on building remediation; $26 / $333 per $1 on lot remediation",
                            "neither program significantly affected NON-firearm violence"],
        },
        "PLoS_ONE_2015_Kondo (PMID 26153687, doi 10.1371/journal.pone.0129582)": {
            "design": "DiD, Philadelphia Doors-and-Windows Ordinance, 2011-2013, n=676 remediated + permits + matched controls",
            "magnitudes": ["remediation significantly associated with citywide reductions in overall crimes, total assaults, gun assaults, nuisance crimes (p<0.001)",
                            "no significant spatial displacement; some increases in narcotics + property crimes around remediated buildings (p<0.001)"],
        },
        "PNAS_2026_Asa (PMID 43038466, doi 10.1073/pnas.2620725123)": {
            "design": "10-year follow-up of the 2013 Philadelphia clustered RCT of vacant-lot greening",
            "magnitudes": ["intent-to-treat: any intervention -> -9% any-crime and -9% violent-crime density per sq-mile-year (0.91, 95%CI 0.86-0.97)",
                            "contamination-adjusted sustained greening -> -12% any-crime (0.88, 0.83-0.93), -11% violent (0.89, 0.83-0.95) — the durability half the scan named"],
        },
        "lane_read": "the lit is lot/building-grain causal with double-digit % effects; our countable is city-year enforcement-VOLUME (the input machinery), so the city-year lane runs on direction-class, per the grain-law",
    },
    "reproducibility_header": ("Built from live keyless pulls this pass (scripts _lane13_gray_*.py): Memphis AGOL FeatureServer year x TypeName; "
                                "Cincinnati Socrata gcej-gmiw groupBy; Detroit AGOL improve_detroit year x request_type; St. Louis csb.zip CSV row-counts + GROUP counters; "
                                "NYC Socrata erm2-nwe9 + 76ig-c548 groupBy; Houston AGOL Archives/MapServer + Recent FeatureServer. "
                                "Murder/population banks read from banked build/ files (never re-derived). Panel: gray_safety_lane_panel_v1.json (97 rows); "
                                "tests: _lane13_gray_tests.py -> gray_safety_lane_tests_v1.json"),
    "honest_nulls_and_flags": [
        "Houston: no Socrata (CKAN portal lacks 311); route banked = city AGOL GIS host directly",
        "Memphis: data.memphistn.gov is ArcGIS-Hub (NOT Socrata) — federated Socrata catalog returns 0 Memphis-owned datasets; the AGOL FeatureServer IS the keyless route",
        "Detroit: data.detroitmi.gov ArcGIS Hub Utility — no Socrata /api/catalog; AGOL org item 'Improve Detroit Issues' is the keyless route (767,131 rows)",
        "St. Louis 2015: official zip ships an EMPTY csv for 2015 — recorded as missing, not zero",
        "2016 STL row 107,916 vs 2014 100,713 with 2013+ full-launch caveat in city README (2008-2012 are partial soft-launch years, kept but flagged)",
        "Memphis 2020-2023: sparse carry-over rows (1/4/14/36) = system switch artifacts, kept with flag; the dense series is 2024-2026",
    ],
    "outputs": [
        "gray_safety_lane_v1.json (this file)",
        "gray_safety_lane_panel_v1.json (97 city-year rows)",
        "gray_safety_lane_tests_v1.json",
        "_lane13_gray_{memphis_311_raw,detroit_raw,cincinnati_raw,houston_raw,stlouis_raw,nyc_year_counts}.json (raw per-city pulls)",
        "_lane13_gray_lit_core_abstracts.json + _lane13_gray_lit_pnas_abstracts.json (lit anchors, PubMed-verbatim)",
    ],
}

json.dump(lane, open(f"{B}/gray_safety_lane_v1.json", "w"), indent=1)
print("WROTE gray_safety_lane_v1.json", os.path.getsize(f"{B}/gray_safety_lane_v1.json"), "bytes")
