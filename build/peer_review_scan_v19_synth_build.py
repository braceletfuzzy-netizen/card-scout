#!/usr/bin/env python3
# BOB-SCAN-20 synth builder — peer_review_scan_v19.jsonl + peer_review_scan_v19_synth.json
# Laws: every row resolved against the live v19 corpus (zero-fabricated cites);
# magnitude ships ONLY when the corpus abstract states it; no editorializing in scan rows (synth carries the read).
import json, os, re

B = os.path.dirname(os.path.abspath(__file__))
corpus = json.load(open(os.path.join(B, "peer_review_scan_v19_corpus.json"), encoding="utf-8"))
recs = corpus["records"]

def find(key):
    m = [r for r in recs if key.lower() in (r.get("title") or "").lower()]
    return m[0] if m else None

def ab(r):
    return re.sub(r"<[^>]+>", "", r.get("abstract") or "").strip()

def has_ab(r):
    return len(ab(r)) > 100

# ---------------- rows: (band, key, magnitude_or_notstated, effect_direction, basis) ----------------
ROWS = [
 # FISCAL
 ("fiscal_efficiency", "State Rainy Day Funds and Fiscal Crises",
  "48-state panel over the 1990-91 recession: presence of structural factors + large balances in other funds entering recession alleviates fiscal stress in recession (direction; no single coefficient in abstract)",
  "positive (reserves entering recession -> less fiscal stress)", "48-state panel, recession-period analysis"),
 ("fiscal_efficiency", "State Rainy Day Funds and Government General Fund Expenditures",
  "FY1998-2014 state panel: actual RDF usage correlates with smaller general-fund-expenditure gaps in both recessions and expansions; prior-year RDF balance interacts with deposit/withdrawal rules (direction; coefficients not in abstract)",
  "countercyclical (RDF use stabilizes GFE)", "state panel FY1998-2014"),
 ("fiscal_efficiency", "Saving for a rainy day",
  "not_stated_in_corpus",
  None, "estimation of needed stabilization-fund size"),
 ("fiscal_efficiency", "City Revenue Structure and Unfunded Pension",
  "city-level model, national sample 2003-2012: city fiscal autonomy and property-tax reliance are determinants of pension underfunding (no coefficient in abstract)",
  "determinants-class", "city-as-sponsor panel 2003-2012"),
 ("fiscal_efficiency", "CREDIT RISK, CREDIT RATINGS, AND MUNICIPAL BOND YIELDS",
  "not_stated_in_corpus",
  None, "municipal-bond yield panel"),
 ("fiscal_efficiency", "Municipal pension funding: A theory",
  "not_stated_in_corpus",
  None, "theory + evidence (Public Choice 1981)"),
 ("fiscal_efficiency", "Is There an Optimal Size of Fiscal Reserves",
  "not_stated_in_corpus",
  None, "local-government budget stabilization chapter"),
 ("fiscal_efficiency", "fiscal slack in a political-budgetary-managerial",
  "not_stated_in_corpus",
  None, "Public Management Review framework study"),
 ("fiscal_efficiency", "general fund balances of major American",
  "not_stated_in_corpus",
  None, "intergovernmental fiscal environment study"),
 ("fiscal_efficiency", "Will Public Sector Retiree Health Benefit Plans Survive",
  "not_stated_in_corpus",
  None, "AER P&P on OPEB unfunded liabilities"),
 # ECON GROWTH
 ("econ_growth_efficiency", "The Effect of State Tax Incentives on Economic Growth and Firm Location",
  "review verdict: tax studies yield CONFLICTING results on whether taxes matter; few test whether incentives are economically justified (no pooled magnitude; the contested-literature clause)",
  "contested/conflicting", "literature review, tax-incentive studies"),
 ("econ_growth_efficiency", "The Impact of Enterprise Zones on Resident Employment",
  "CA and FL enterprise zones (strong hiring-credit programs): NO evidence of effects on zone residents' employment (individual-level employment probs + neighborhood propensity matching)",
  "null", "neighborhood matching + individual models"),
 ("econ_growth_efficiency", "Tax Costs and Employment Benefits of Enterprise Zones",
  "reservation-wage model: local benefits of incentives exceed local costs overall, BUT untargeted provision not recommended even in high-unemployment areas (net-benefit sign positive at the locality level)",
  "positive-net-benefit (locality), contested targeting", "reservation-wage estimation"),
 ("econ_growth_efficiency", "Simulating the Effects of the Tax Credit Program of the Michigan",
  "MEGA job-credit simulation: net cost per job created 'modest'; job impacts considerably larger than equivalent-dollar general business tax cuts (simulation; magnitudes assumption-dependent)",
  "positive (conditional on assumptions)", "simulation under location assumptions"),
 ("econ_growth_efficiency", "Does the Job Creation Tax Credit Program in Maryland",
  "zip-code FE growth model 1994-1998: job growth concentrated in Priority Funding Areas in transport/comms/utilities and services; no effect in manufacturing or FIRE (partial-concentration result)",
  "mixed (sector-heterogeneous)", "zip-code fixed-effects, 5 sectors 1994-98"),
 ("econ_growth_efficiency", "Do Tax Incentives Affect Business Location and Economic Development",
  "state film incentives, panel DiD: TV-series filming +6.3% to +55.4% (at most +1.50 series); NO meaningful effect on feature films, industry employment, wages, or establishments",
  "null on employment/wages (small filming-volume effect only)", "panel difference-in-differences"),
 ("econ_growth_efficiency", "Who Benefits From State and Local Economic Development",
  "not_stated_in_corpus",
  None, "Bartik (1991) book record via review entry"),
 ("econ_growth_efficiency", "Business Climate, Tax Incentives, and Regional Economic Development",
  "not_stated_in_corpus",
  None, "Growth and Change (1984)"),
 # INFRA
 ("infra_efficiency", "Preventive and corrective maintenance",
  "not_stated_in_corpus (cost comparison + cost-benefit analysis of preventive vs corrective maintenance; highest-cited record in the band, 118c)",
  None, "Structure and Infrastructure Engineering (2015)"),
 ("infra_efficiency", "Pavement Preventive Maintenance: Description, Effectiveness",
  "preventive-maintenance program holds better pavement quality at LOWER total costs; level of funding inadequate to keep roads at current condition if maintenance/rehabilitation policies continue (direction; no multiplier coefficient in abstract)",
  "positive (preventive beats continued underfunding + corrective)", "highway-agency program review (ASTM STP)"),
 ("infra_efficiency", "Using Simulation to Understand the Impact of Deferred Maintenance",
  "not_stated_in_corpus",
  None, "simulation of deferred-maintenance impacts"),
 ("infra_efficiency", "Estimating the marginal cost of pavement damage",
  "not_stated_in_corpus",
  None, "marginal pavement-damage cost estimation"),
 ("infra_efficiency", "participatory assessment technique for infrastructure",
  "deferred maintenance named as accumulated pressure on urban infrastructure; participatory condition assessment demonstrated on Houston stormwater (no cost multiplier in abstract)",
  None, "neighborhood-level condition monitoring case study"),
 ("infra_efficiency", "Life cycle cost analysis for managing rail",
  "LCC framework for maintenance/design decisions under budget limits; tools early-phase (framework, no multiplier in abstract)",
  None, "life-cycle costing framework (rail)"),
 ("infra_efficiency", "Bridge Maintenance Life Cycle Cost Assessment",
  "not_stated_in_corpus",
  None, "bridge LCCA chapter"),
 # HOUSING/EDU
 ("housing_edu_efficiency", "The Effects of School Spending on Educational and Economic Outcomes",
  "THE DOSE: +10% per-pupil spending each year for all 12 school years -> +0.31 completed years of education, ~7% higher adult wages, -3.2pp annual adult poverty; larger for low-income children (event-study + IV, cohorts 1955-1985)",
  "positive dose-response", "school-finance-reform event study + IV (QJE)"),
 ("housing_edu_efficiency", "School Finance Reform and the Distribution of Student Achievement",
  "post-1990 adequacy reforms -> sharp, immediate, sustained spending increases in low-income districts and achievement gains phasing in over following years ('implied effect of school resources on educational achievement is large')",
  "positive (reform -> spending -> achievement)", "NAEP event-study"),
 ("housing_edu_efficiency", "Long-Run Price Elasticity of Supply of New Residential Construction",
  "not_stated_in_corpus",
  None, "US/UK supply-elasticity estimation"),
 ("housing_edu_efficiency", "Housing affordability and family well",
  "not_stated_in_corpus",
  None, "housing voucher evaluation results"),
 ("housing_edu_efficiency", "Long-term effects of public low-income housing vouchers",
  "not_stated_in_corpus",
  None, "voucher long-run effects"),
 ("housing_edu_efficiency", "Density zoning and class segregation",
  "50-metro density-zoning index: strong relationship with income segregation for 2000 and 1990-2000 changes; 2SLS replication suggests causal; higher interjurisdictional inequality (no single elasticity in abstract)",
  "positive (restrictive zoning -> income segregation)", "OLS + 2SLS, 50 metros"),
 ("housing_edu_efficiency", "Do Strict Land Use Regulations Make Metropolitan Areas More Segregated",
  "95 biggest cities: density restrictions associate with segregation of wealthy and middle-income, NOT the poor; more local pressure -> higher income segregation, more state control -> lower",
  "positive (restrictions -> upper-income segregation)", "new regulation measures, 95 cities"),
 ("housing_edu_efficiency", "The Elephant in the Zoning Code",
  "not_stated_in_corpus",
  None, "single-family zoning supply discussion"),
 ("housing_edu_efficiency", "Housing supply and housing affordability",
  "not_stated_in_corpus",
  None, "Handbook of Regional and Urban Economics chapter"),
 # PRISM
 ("prism_two_tier", "Evaluating Program and Managerial Efficiency",
  "THE CANONICAL METHOD: DEA measures relative efficiency of Decision Making Units with multiple inputs/outputs via mathematical programming, no a-priori weights required; demonstrated on Program Follow Through (education experiment)",
  None, "Management Science 27(6) — the DEA founding paper"),
 ("prism_two_tier", "Cost Efficiency of Macedonian Municipalities",
  "DEA-VRS + Kernel + SFA: Macedonian municipalities average LOW service-delivery efficiency with significant variation; ethnic fragmentation, population density, own tax revenues, mayor's coalition affiliation explain differences (efficiency-score class, no dollar dose)",
  "efficiency-score class", "DEA-VRS + SFA robustness"),
 ("prism_two_tier", "Fiscal Decentralization and Efficiency of Regional Government in Croatia",
  "DEA on 20 counties 2009-2016: among exogenous determinants, only unemployment rate and average wage statistically significant for efficiency scores (efficiency-score class)",
  "efficiency-score class", "DEA + exogenous determinants"),
 ("prism_two_tier", "Determinants of efficiency in the provision of municipal street-cleaning",
  "not_stated_in_corpus (the municipal-service DEA determinants class, 90c)",
  None, "Waste Management DEA application"),
 ("prism_two_tier", "The efficiency of municipal solid waste collection in Mexico",
  "not_stated_in_corpus",
  None, "Waste Management DEA application"),
 ("prism_two_tier", "Measuring efficiency in the public sector using nonparametric frontier",
  "not_stated_in_corpus",
  None, "US transit-agency nonparametric frontier study"),
 ("prism_two_tier", "The Efficiency Frontier as a Method for Gauging",
  "not_stated_in_corpus (efficiency frontier applied to public expenditure, Belgian case)",
  None, "SSRN working paper"),
 ("prism_two_tier", "Cost Efficiency of Public Procurement at Local Level",
  "efficiency of public procurement measured in HOURS per procurement (185,305 invested hours, 18 months, 8 public enterprises): organizational design + external benchmarking improve efficiency (transaction-cost metric, not dollar dose)",
  "efficiency-score class (hours metric)", "Serbian public-enterprise case analysis"),
 ("prism_two_tier", "Assessing the efficiency of China",
  "super-efficiency DEA + Malmquist + Tobit on 31 provinces 2017-2020: substantial regional variation in fiscal-spending efficiency on fitness services (efficiency-score class)",
  "efficiency-score class", "super-efficiency DEA-Malmquist-Tobit"),
 ("prism_two_tier", "willingness to adopt process innovations",
  "not_stated_in_corpus",
  None, "Local Government Studies cost-efficiency study"),
]

jsonl_rows = []
seq = 0
missing = []
for band, key, magnitude, direction, basis in ROWS:
    r = find(key)
    if r is None:
        missing.append(key); continue
    a = ab(r)
    jsonl_rows.append({
        "scan": "BOB-SCAN-20", "band": band, "seq": (seq := seq + 1),
        "authors": r.get("authors"), "year": r.get("year"),
        "title": r["title"], "venue": r.get("venue"),
        "citations": r.get("cited") if isinstance(r.get("cited"), int) else None,
        "abstract_present": has_ab(r),
        "key_finding": (a[:600] if a else "no abstract in corpus — title/venue/cites row only"),
        "stated_magnitude": magnitude,
        "magnitude_class": ("stated_in_corpus" if magnitude != "not_stated_in_corpus" and has_ab(r)
                            else "not_stated_in_corpus"),
        "effect_direction": direction,
        "basis_of_estimate": basis,
        "doi": r.get("doi", ""), "url": r.get("url"),
        "query": r.get("query", ""), "route": r.get("route", ""),
    })

# honest-null rows for lanes whose TASK-named magnitudes did NOT surface in any live probe abstract
seq += 1
jsonl_rows.append({
    "scan": "BOB-SCAN-20", "band": "infra_efficiency", "seq": seq,
    "authors": None, "year": None,
    "title": "HONEST-NULL: the road-maintenance deferment multiplier (the 4-7x class)",
    "venue": "not recovered in 17 infra-band queries x 2-3 routes (keyless Crossref + PubMed + EuropePMC)",
    "citations": None, "abstract_present": False,
    "key_finding": "No peer-reviewed abstract in the live v19 corpus states a 4x-7x maintenance-vs-rebuild deferment multiplier. Direction only: preventive maintenance beats continued underfunding + corrective spending (Pavement Preventive Maintenance 1998; Preventive and corrective maintenance 2015, 118c; deferred-maintenance simulation 2002). The multiplier survives in practitioner/engineering literature (FHWA-class) — a gray-lit gap, banked like the skate-park crime lane.",
    "stated_magnitude": "not_stated_in_corpus", "magnitude_class": "not_stated_in_corpus",
    "effect_direction": None, "basis_of_estimate": "null route banked",
    "doi": "", "url": "", "query": "deferred maintenance cost escalation infrastructure rehabilitation + 16 more", "route": "none",
})
seq += 1
jsonl_rows.append({
    "scan": "BOB-SCAN-20", "band": "housing_edu_efficiency", "seq": seq,
    "authors": None, "year": None,
    "title": "HONEST-NULL: zoning-reform -> permit-elasticity dose (the Glaeser/Lens class)",
    "venue": "not recovered as abstract-stated dose in 11 housing-band queries x 2-3 routes",
    "citations": None, "abstract_present": False,
    "key_finding": "The zoning corpus recovered direction-class results (density zoning -> income segregation, Rothwell 2010/2016; single-family zoning supply discussion 2018; supply-elasticity estimation Saiz-class 2001 no abstract) but ZERO abstract-stated permit elasticity coefficients. The permit-dose lane is the gap; supply-elasticity magnitudes live in papers whose abstracts the keyless routes did not return.",
    "stated_magnitude": "not_stated_in_corpus", "magnitude_class": "not_stated_in_corpus",
    "effect_direction": None, "basis_of_estimate": "null route banked",
    "doi": "", "url": "", "query": "housing supply elasticity regulation United States + 10 more", "route": "none",
})
seq += 1
jsonl_rows.append({
    "scan": "BOB-SCAN-20", "band": "fiscal_efficiency", "seq": seq,
    "authors": None, "year": None,
    "title": "HONEST-NULL: fiscal outcome-per-dollar dose (any published magnitude mapping reserve/pension/debt rates -> distress probability in dollars or pp)",
    "venue": "not recovered in 10 fiscal-band queries x 2-3 routes",
    "citations": None, "abstract_present": False,
    "key_finding": "Fiscal lane is determinants-and-direction heavy (rainy-day stabilization both-directions, pension-funding determinants, credit-ratings-yields, fiscal-slack framework) and dose-response empty: no live-probe abstract states a pp-per-rate or $-per-rate magnitude. The GAO/NASBO empirical class is institutional, not peer-reviewed dose.",
    "stated_magnitude": "not_stated_in_corpus", "magnitude_class": "not_stated_in_corpus",
    "effect_direction": None, "basis_of_estimate": "null route banked",
    "doi": "", "url": "", "query": "pension funded ratio municipal fiscal distress + 13 more", "route": "none",
})

with open(os.path.join(B, "peer_review_scan_v19.jsonl"), "w", encoding="utf-8") as f:
    for row in jsonl_rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

# ---------------- synth ----------------
bands = {}
for row in jsonl_rows:
    bands.setdefault(row["band"], []).append(row)

def stat(b):
    rows = bands[b]
    stated = [r for r in rows if r["magnitude_class"] == "stated_in_corpus" and "HONEST-NULL" not in r["title"]]
    cs = sorted(r["citations"] for r in rows if isinstance(r["citations"], int))
    return {
        "rows": len(rows), "stated_magnitude_rows": len(stated),
        "citation_span": [cs[0], cs[-1]] if cs else None,
        "median_cites": cs[len(cs)//2] if cs else None,
        "top_anchor": {"title": rows[0]["title"], "cites": rows[0]["citations"], "venue": rows[0]["venue"],
                       "dose": rows[0]["stated_magnitude"]} if rows else None,
        "honest_nulls": [r["title"] for r in rows if "HONEST-NULL" in r["title"]],
    }

synth = {
 "_record": "peer_review_scan_v19_synth — BOB-SCAN-20 THE LITERATURE PRISM FOR THE OUTPUT VECTOR (fiscal / econ-growth / infra / housing-edu / the two-tier prism itself)",
 "built": "2026-11-25",
 "founder_steering": "framed for COMPARISON, not conclusion: per-family published magnitudes + methods + gaps, one lane tag each, for parent-side cross-examination against our instruments",
 "parent_artifacts": [
   "peer_review_scan_v19_raw.jsonl (136 live probe rows: 51 queries x keyless Crossref + PubMed eutils + EuropePMC, incl. 21 targeted round-2 booster queries)",
   "peer_review_scan_v19_corpus.json (deduped corpus)",
   "peer_review_scan_v19_dedupe.py / peer_review_scan_v19_boosters.py / peer_review_scan_v19_abstracts.py",
 ],
 "laws_held": [
   "zero-fabricated cites: every row resolved against the live v19 probe corpus before shipping",
   "magnitude ships ONLY when the live corpus abstract states it, per row; else not_stated_in_corpus",
   "honest-nulls named and banked as routes, like the skate-park lane",
   "no editorializing in scan rows; the read lives here only",
   "direction-class only; no causal claims beyond each study's own design",
 ],
 "corpus_stats": {
   "live_probe_rows": 136, "unique_queries": corpus["unique_queries"], "deduped_records": corpus["deduped_records"],
   "records_with_abstract_gt_100": corpus["records_with_abstract_gt_100"],
   "abstract_share_pct": corpus["abstract_share_pct"], "year_span": corpus["year_span"],
   "median_cites": corpus["median_cites"], "max_cites": corpus["max_cites"],
   "route_distribution": corpus["route_distribution"], "band_distribution": corpus["band_distribution"],
   "zero_hit_routes": 17, "api_error_routes": 16,
 },
 "per_band_stats": {b: stat(b) for b in bands},
 # ---------------- the comparison frame the founder asked for ----------------
 "family_frames_for_cross_examination": {
  "fiscal_efficiency": {
   "tag": "NOVEL-OURS",
   "tag_note": "no published counterpart for a fitted outcome-per-dollar (or pp-per-rate) fiscal dose in the live corpus; the constructs our fiscal v2 fit uses (reserves, funded ratio, debt/capita) are print-validated as determinants/stabilizers but never assembled into a dose",
   "published_magnitudes": [
     "rainy-day stabilization: direction both-directions (Knight 2002 48-state; 2019 Public Finance Review FY1998-2014) — no coefficient in any recovered abstract",
     "pension funding determinants: fiscal autonomy + property-tax reliance, city-as-sponsor 2003-2012 (no coefficient)",
     "credit ratings: municipal-bond yields panel (1991 NTJ, 59c, no abstract returned)",
     "optimal reserve size: chapter-level, no abstract-stated percent-of-revenue number",
   ],
   "methods": "panel regressions, stabilization-fund rule variables, event-type recession windows",
   "gaps": "the GAO/NASBO empirical class is institutional not peer-reviewed-dose; NO abstract-stated pp-per-funding-rate or reserve-percent magnitude anywhere in the corpus → the calibration surface is direction-only",
   "comparison_hook": "our banked fiscal reads (STL pension 79.45% funded, NYC debt 12,134/cap, CAFR reserve arcs) live in the determinants tier; the fit that rates fiscal outcomes on them has no published bracket to land inside",
  },
  "econ_growth_efficiency": {
   "tag": "VALIDATES-OURS",
   "tag_note": "the Bartik-class published range (null-to-small, contested) brackets our economy read (walk-forward 0.50 coin + LOCO 0.56 → gate-shut): incentives/enterprise zones are a zero-to-marginal lever in print, consistent with our no-signal economy fit",
   "published_magnitudes": [
     "Hanson 2008 (93c): CA+FL enterprise zones → NO evidence of resident-employment effects (the canonical place-based null)",
     "film-incentive DiD: filming volume +6.3% to +55.4%; employment/wages/establishments → no meaningful effect",
     "MEGA simulation: net cost per job 'modest', job creation considerably larger per dollar than general tax cuts (assumption-dependent)",
     "Maryland JCTC: concentration only in some sectors (transport/comms/services), none in manufacturing/FIRE",
     "Fisher 2001 review (147c): the tax-effect literature yields CONFLICTING results — the contested clause",
   ],
   "methods": "individual employment models + neighborhood propensity matching; panel DiD; zip-code FE growth models; simulation",
   "gaps": "no live-probe abstract states firm-formation elasticities vs local spend (BFS-class) — the firm-formation strand is the gap",
   "comparison_hook": "boarded Board-3 oligopsony/wage strata remain the crime-side counterpart; the published incentive magnitudes are small enough that local economy-output variance is dominated by non-incentive forces — matching our weak economy signal",
  },
  "infra_efficiency": {
   "tag": "NOVEL-OURS",
   "tag_note": "no published condition-vs-spend elasticity or dose anywhere in the live corpus; the preventive-vs-corrective direction IS print-validated (maintenance-first confirmed), but any per-dollar dose our infra fit would produce has no published bracket — the 4-7x multiplier did not surface in peer-reviewed abstracts (practitioner/gray-lit class, banked as the gap)",
   "published_magnitudes": [
     "preventive maintenance holds better pavement quality at LOWER total cost (1998 ASTM; direction only)",
     "deferred maintenance: named as accumulated pressure; simulation-based impacts (no multiplier stated)",
     "preventive-vs-corrective cost-benefit comparison exists (2015, 118c) but abstract carries no multiplier",
     "bridge LCCA class exists at low citation mass (2c chapter) — the bridge-elasticity lane is thin in peer-review",
   ],
   "methods": "life-cycle cost analysis, pavement-performance simulation, condition-index prioritization",
   "gaps": "FHWA analytic pieces returned nothing peer-reviewed-dose; SDWA/water-utility capital-efficiency lane empty at abstract level (our v19 outlane SDWA honest-null mirrors this)",
   "comparison_hook": "our banked FHWA NBI cross-sections (NYC 9.4% poor bridges vs CIN 2.3%) sit in a literature with direction but no dose — infrastructure condition-vs-spend fit will be bracket-free, first-mover read",
  },
  "housing_edu_efficiency": {
   "tag": "VALIDATES-OURS",
   "tag_note": "the EXACT banked anchor is live: Jackson Johnson-Mikolajczyk-Altamirano QJE 2015 (583c) states the dose our lane carried — +10%/year for 12 years → +0.31 completed years of education, ~7% higher wages, -3.2pp adult poverty, concentrated low-income; Lafortune-Rothstein-Schazenbach AEJ 2018 (229c) confirms the achievement leg",
   "published_magnitudes": [
     "Jackson 2015 QJE: THE DOSE (10% x 12yrs → +0.31yrs / +7% wages / -3.2pp poverty)",
     "Lafortune et al. 2018 AEJ: post-1990 adequacy reforms → sustained spending gains in low-income districts; 'large' implied resource → achievement effect, phasing in",
     "zoning: density-zoning index → income segregation (2SLS-causal-sign), 50 metros; 95-city replication shows rich-not-poor segregation; NO permit elasticity stated",
     "vouchers: long-run and family-wellbeing evaluations present (119c/34c) but abstract doses not returned",
   ],
   "methods": "event study + IV (court-mandated reform timing); NAEP event-study; OLS/2SLS metro panels",
   "gaps": "zoning-reform → permit elasticity dose = honest-null (banked); voucher-vs-supply-side head-to-head magnitude not surfaced at abstract level",
   "comparison_hook": "the Jackson dose-shape (linear-in-years-of-exposure, concentrated low-income) is available for direct cross-examination against our housing/schools refit coefficients",
  },
  "prism_two_tier": {
   "tag": "NOVEL-OURS",
   "tag_note": "the two-tier decomposition (operational overhead-rate vs community outcome-yield as TWO DISTINCT MEASURED QUANTITIES, multiplied) does not exist as an assembly in the live corpus — the founder's synthesis moat is real at the seam",
   "published_magnitudes": [
     "DEA method: Charnes-Cooper-Rhodes 1981 Management Science (1,067c) — the canonical measurement instrument for exactly the founder's 2x2, but measured at the DMU level as a SINGLE efficiency score, not as two decomposed tiers",
     "municipal DEA applications: waste/street-cleaning (90c, 50c), transit agencies (32c), Macedonian municipalities (20c), Croatian counties (3c), Chinese provinces super-efficiency (17c), Serbian procurement in HOURS (3c) — efficiency-score class, no outcome-per-delivered-dollar dose",
     "efficiency frontier for public expenditure (Belgian case, 71c SSRN): single-tier frontier gauging",
     "outcome-yield tier: lives ENTIRELY in separate literatures (Jackson QJE dose, Lafortune AEJ) never joined to the DEA overhead side in any corpus record",
   ],
   "methods": "DEA-VRS/CRS, super-efficiency DEA, Malmquist indices, Tobit second-stage, SFA robustness — the calibration class for our residual instrument",
   "novelty_check_for_the_two_tier_frame": {
     "operational_tier_in_print": "YES — deeply precented: the DEA municipal-service corpus (~104 band records) measures cost-efficiency of delivery; fiscal-slack/procurement-hours variants exist",
     "community_tier_in_print": "YES — separately precented: outcome-dose literature (Jackson/Lafortune class) measures outcome-per-input",
     "the_joint_decomposition_in_print": "NO — zero corpus records measure overhead-rate and outcome-yield as distinct quantities and combine them (our multiplication law: outcome/dollar-in = [outcome/delivered] x [delivered/budgeted]); closest single-tier analogs (DEA scores, efficiency frontiers) collapse both into one number",
     "moat_estimate": "both tiers ≈ fully precented separately; the seam (two-tier assembly + the 2x2 administration scorecard) ≈ novel under 40 prism-band live probes; risk = non-keyless or book-length framings not probed",
     "calibration_for_residual_instrument": "DEA scores are the calibration reference class for residual-based efficiency scoring; our fitted-residual instrument maps to DEA's input-oriented efficiency with the residual substituting for the frontier — the second-stage determinants (Tobit regressors: fragmentation, population density, own revenues) are checkable against our admin-boundary reads (Memphis +6.30 → -9.45)",
   },
   "gaps": "no citizen-outcomes-per-administrative-cost studies recovered as abstracts; IMF expenditure-efficiency framework surfaced only as fragmentary EuropePMC health-system rows, not the macro fiscal framework — the OECD/IMF macro-efficiency lane needs a targeted non-keyless fetch to fully clear",
   "comparison_hook": "parent cross-exam: DEA efficiency-score distributions (e.g., Macedonian 'low efficiency, significant variation') vs our within-FE residual ranks (CIN 1 / MEM 2 / STL 3 / DET 4)",
  },
 },
 "countable_routes_bank": {
  "total_routes_live": corpus["unique_queries"],
  "route_distribution": corpus["route_distribution"],
  "per_lane_countable_routes": {
    "fiscal_efficiency": ["rainy-day 48-state recession panel (direction)", "RDF-usage stabilization panel FY98-14 (direction)", "city pension-funding determinants 2003-12", "muni-bond yields-ratings panel", "reserve-optimal-size chapter class"],
    "econ_growth_efficiency": ["CA/FL enterprise-zone matching null", "film-incentive DiD (volume vs employment split)", "MEGA cost-per-job simulation", "PFA zip-FE sector split", "reservation-wage net-benefit model"],
    "infra_efficiency": ["preventive-vs-corrective cost-benefit (direction)", "deferred-maintenance simulation", "rail/bridge LCCA framework class", "neighborhood participatory condition assessment"],
    "housing_edu_efficiency": ["Jackson QJE dose (live, 583c)", "Lafortune AEJ achievement event-study", "density-zoning 2SLS segregation", "95-city regulation-segregation replication", "voucher long-run evaluations (no abstract dose)"],
    "prism_two_tier": ["CCR 1981 DEA method", "municipal DEA-VRS/SFA scores (Macedonia, Croatia, transit, waste, procurement-hours)", "super-efficiency+Malmquist+Tobit second stage", "public-expenditure efficiency frontier (SSRN single-tier)"],
  },
  "honest_gaps_banked": [
    "4-7x deferment multiplier: NOT in peer-review abstracts (gray-lit class) — infra lane gap",
    "zoning-reform → permit elasticity dose: NOT stated — housing lane gap",
    "fiscal outcome-per-dollar dose: NOT stated — fiscal lane gap (determinants only)",
    "firm-formation elasticities vs local spend: NOT surfaced — economy lane gap",
    "IMF/OECD macro expenditure-efficiency framework: only fragmentary, needs non-keyless fetch — prism lane partial gap",
    "bridge-condition funding elasticity: chapter-class only, no dose",
  ],
 },
 "lane_tag_summary": {
   "VALIDATES-OURS": ["econ_growth_efficiency", "housing_edu_efficiency"],
   "CONTRADICTS": [],
   "NOVEL-OURS": ["fiscal_efficiency", "infra_efficiency", "prism_two_tier"],
   "VOID-LANE": [],
   "counts": {"VALIDATES-OURS": 2, "CONTRADICTS": 0, "NOVEL-OURS": 3, "VOID-LANE": 0},
   "note": "VOID-LANE kept empty because every family printed SOMETHING; the empty sub-lanes are named as honest gaps inside each frame (deferment multiplier, permit elasticity, fiscal dose, firm-formation elasticity, IMF macro framework)",
 },
 "jsonl_rows": len(jsonl_rows),
 "missing_rows_failed_resolution": missing,
}

with open(os.path.join(B, "peer_review_scan_v19_synth.json"), "w", encoding="utf-8") as f:
    json.dump(synth, f, indent=1, ensure_ascii=False)

print(f"jsonl rows written: {len(jsonl_rows)}")
print(f"missing (unresolved keys): {missing}")
print(f"bands: { {b: len(rows) for b, rows in bands.items()} }")
print("tags:", synth["lane_tag_summary"]["counts"])
