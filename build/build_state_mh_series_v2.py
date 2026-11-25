# Build state_mh_series_v2.jsonl: v1 rows (unchanged, verbatim) + this-pass widening rows appended.
# Reproducibility header + honest nulls with routes-tried; value_kind per row; approx-pops flagged at test time.
import json, datetime, copy

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
v1 = [json.loads(l) for l in open(B + 'state_mh_series_v1.jsonl', encoding='utf-8') if l.strip()]

HDR = ('STATE-MH-WIDENING v2 REPRODUCIBILITY HEADER. one-row-per-state-year. Every USD in rows with source_refs of this pass was read '
       'in-session from the cited keyless document (pdftotext -layout, visual render parse via PyMuPDF for scrambled tables, or printed figures '
       'in HFA/LBB briefs). v1 rows carried verbatim (values, value_kind, notes, sources unchanged). null = routes-tried-no-capture, never a placeholder. '
       'value_kind per vintage: actual/available/budgeted/recommended/estimated/exec-basis/TAFP — actual and budgeted vintages are NEVER blended in the '
       'per-capita test (the test script drops non-matching kinds to the budgeted-or-actual-baseline flag). State-appropriation rows for MI = '
       'combined behavioral-health gross appropriations (Traditional-Medicaid BH + HMP BH + Non-Medicaid/State-Psych), a broader grain than other states: '
       'flagged mh_grain=combined-BH. OK rows are requested/budgeted BPR appropriations (dept 452). LA rows are OBH agency 09-330 total expenditures / '
       'total means of finance in the executive-budget supporting documents. TX rows are BIENNIUM cross-article all-funds totals (value_kind=biennial) — '
       'not annual, NOT used in the within-state test. Built ' + datetime.date.today().isoformat() + ' by build_state_mh_series_v2.py; sources cached in '
       '_stmh2/ and _stmh/. State-pop conversions: static-approx state pops FLAGGED per row at test time; city pops banked-first law kept.')

rows = []
def add(state, fy, usd, kind, county_table, where, srcs, notes, grain='dept-MH'):
    rows.append({
        'state': state, 'fiscal_year': fy, 'state_mh_budget_usd': usd,
        'value_kind': kind, 'county_allocation_table_available': county_table,
        'per_county_usd_where': where, 'source_refs': srcs, 'notes': notes,
        'mh_grain': grain, 'series': 'v2',
    })

# ---- NY (v1 had FY23-26; this pass adds FY19-22 from DOB appropdata pages) ----
NY = [(2019, 4264744000, 'available col (FY20 exec appropdata page)'),
      (2020, 4395554000, 'recommended (FY20 appropdata page; also 4,403,776,500 available per FY21 page)'),
      (2021, 4454322000, 'recommended (FY21 appropdata page; 4,467,462,000 available per FY22 page)'),
      (2022, 4435572000, 'recommended (FY22 appropdata page; 4,487,892,000 available per FY23 page)')]
for fy, usd, kind in NY:
    add('NY', fy, usd, kind, False,
        'no per-county table (see v1 note)', 
        ['https://budget.ny.gov/pubs/archive/fy20/ex/agencies/appropdata/MentalHealthOfficeof.html',
         'https://budget.ny.gov/pubs/archive/fy21/ex/agencies/appropdata/MentalHealthOfficeof.html',
         'https://budget.ny.gov/pubs/archive/fy22/ex/agencies/appropdata/MentalHealthOfficeof.html',
         'https://budget.ny.gov/pubs/archive/fy23/ex/agencies/appropdata/MentalHealthOfficeof.html'],
        ['grain: OMH (Office of Mental Health) agency appropriation; OMH only = subset of NY state MH spend (OMH vs OASAS vs OTDA separate agencies)',
         'browser-lane fetched (curl TLS-refused on budget.ny.gov); extracts in _stmh2/ny_omh_fy2{0,1,2}_browser.txt + ny_omh_fy23_browser.txt'])

# ---- MO (v1 FY24-26; pass adds FY19-23) ----
MO = [(2019, 2250870738, 'TAFP-after-veto grand total'),
      (2020, 2482230394, 'TAFP'),
      (2021, 2515693209, 'gov-recs (exec basis)'),
      (2022, 2734925718, 'gov-recs (exec basis)'),
      (2023, 3423779593, 'TAFP (exec basis) / 3,441,720,822 as-printed TAFP')]
for fy, usd, kind in MO:
    add('MO', fy, usd, kind, False, 'no per-county table (v1 note)',
        ['https://archive.org/download/2019mdmhbudgetsumrpt/2019MDMHBudgetSumRpt.pdf',
         'https://archive.org/download/2020mdmhbudgetsumrpt/2020MDMHBudgetSumRpt.pdf',
         'https://archive.org/download/2023MDMHBudgetSumRpt/2023MDMHBudgetSumRpt.pdf',
         'https://budplan.oa.mo.gov/fy2021/fy-dmh-budget-request-book1-gov-rec.pdf',
         'https://oa.mo.gov/sites/default/files/FY_2022_DMH_Budget_Request_Gov_Rec_Book_1.pdf'],
        ['grain: DMH department-wide totals; 2019-20 mdmh budget summary reports banked in _stmh2'])

# ---- PA (v1 FY24-26 + approx 2019; pass adds exact FY19-23 from Blue Books) ----
PA = [(2019, 1058259000, 'actual (FY20-21 Blue Book)'),
      (2020, 1123539000, 'actual (FY21-22 Blue Book; also 1,118,582K avail)'),
      (2021, 1202993000, 'available (FY21-22 BB; 1,150,210K budgeted / 1,166,753K actual in FY22-23 BB)'),
      (2022, 1261910000, 'actual (FY24-25 BB; 1,249,611K as 22-23 BB)'),
      (2023, 1334732000, 'actual (FY23-24 BB / 24-25 BB)')]
for fy, usd, kind in PA:
    add('PA', fy, usd, kind, False, 'county grain partial inside county-submitted plans (v1 note)',
        ['https://www.pa.gov/content/dam/copaparks-pa/assets/website/budget-information/20-21%20DHS%20Blue%20Book.pdf (wayback)',
         'https://www.pa.gov/content/dam/copaparks-pa/assets/website/budget-information/2022-23%20DHS%20Blue%20Book.pdf (wayback)',
         'https://www.pa.gov/content/dam/copaparks-pa/assets/website/budget-information/2024-2025%20DHS%20Blue%20Book.pdf'],
        ['multi-vintage actual/available/budgeted columns captured verbatim in _stmh2/pa_bb_*.txt — kind field tracks which vintage'])

# ---- OH state-grain (v1 was county-grain only; this pass adds the dept-wide FY totals) ----
OH = [(2019, 164573756, 'Total col (LSC statewide table, visual re-parse)'),
      (2020, 206600198, 'Total col (LSC statewide table)'),
      (2021, 210187151, 'Total col (LSC statewide table)'),
      (2022, 249158646, 'Total col (LSC statewide table, visual re-parse)'),
      (2023, 213466002, 'Total col (LSC statewide table, visual re-parse)'),
      (2024, 246400280, 'Total col (LSC statewide table, visual re-parse)'),
      (2025, 543142029, 'Subsidy col (LSC FY25 dbh line; prior pass)'),
      (2026, 646278746, 'Subsidy col (LSC FY26 Department of Behavioral Health line; prior pass)')]
for fy, usd, kind in OH:
    add('OH', fy, usd, kind, True,
        'yes — LSC per-county series (v1 county rows stay as their own rows); state-grain row added by this pass',
        ['https://www.legislature.oh.gov/LSC/State_Spending_by_County/Statewide%20Spending%20by%20Category/fy-YYYY-state-spending-by-county-statewide-spending-by-category-table.pdf',
         'renders: _stmh/oh_render/sw_fy*.png (visual parse verified against pdftotext -layout)'],
        ['column-scramble fix: PDF value baselines offset one row from labels — pdftotext misassigns values; rendered-image visual parse verified each row against the printed column header',
         'FY19 row = MHAS Subsidy 144,181,440 + Capital 20,392,317 = Total 164,573,756 (Subsidy+Capital printed as Total)'],
        grain='dept-MHAS/DBH (Subsidy+Capital Total)')

# ---- MI (v1 had county + null state-grain; pass adds the state-grain combined-BH appropriations) ----
MI = [(2020, 3822355000, 'gross approp sum of BH components (HFA briefing pie: TradMedicaid BH 2,818,435,400 + HMP BH 371,843,300 + Non-Medicaid/StatePsych 632,076,300)'),
      (2021, 4424900900, 'gross approp sum (3,194,979,200 + 589,941,900 + 639,979,800)'),
      (2022, 4927099400, 'gross approp sum (3,605,430,100 + 603,614,300 + 718,055,000)'),
      (2023, 5283203100, 'gross approp sum (3,594,216,900 + 570,067,600 + 1,118,918,600)'),
      (2024, 5427194300, 'gross approp sum (3,975,261,300 + 590,860,800 + 861,072,200)'),
      (2025, 5764615200, 'gross approp sum (4,391,669,100 + 527,784,600 + 845,161,500)'),
      (2026, 6449723700, 'gross approp sum (4,958,105,400 + 570,436,500 + 921,181,800)')]
for fy, usd, kind in MI:
    add('MI', fy, usd, kind, True,
        'county grain inside CMHSP contract letters (v1 partial) + Section 940(4) tables',
        ['https://www.house.mi.gov/hfa/PDF/Briefings/HHS_Medicaid_BudgetBriefing_fy19-20.pdf (wayback ts 20200308004841)',
         'https://www.house.mi.gov/hfa/PDF/Briefings/HHS_Medicaid_BudgetBriefing_fy25-26.pdf (wayback ts 20260715035036)'],
        ['grain flag: combined behavioral health (includes Medicaid BH capitation AND non-Medicaid MH + state psychiatric hospitals) — BROADER than other states’ dept-MH grain; per-capita comparisons use the flagged mh_grain field',
         'fiscal_year here = the FY of the budget (briefing FY19-20 = FY2020)'])

# ---- OK (v1 FY25; pass adds FY19-24 appropriations) ----
OK = [(2019, 337108145, 'FY19 Projected grand total appropriations (FY19 BPR; also FY18 Actual 306,485,149 on same page)'),
      (2020, 500388273, 'FY20 Requested grand total appropriations (FY20 BPR)'),
      (2021, 540135330, 'FY21 Requested grand total appropriations (FY21 BPR)'),
      (2022, 334915240, 'FY21 Budgeted appropriations total printed in FY22 BPR (requested was 314,320,023 in FY22 BPR)'),
      (2023, 341693539, 'FY23 Requested appropriations total (FY23 BPR)'),
      (2024, 340077785, 'FY23 Budgeted = FY24 Requested appropriations total (FY24 BPR, flat-budget request)')]
for fy, usd, kind in OK:
    add('OK', fy, usd, kind, False, 'no per-county table (v1 note)',
        ['https://oksenate.gov/sites/default/files/2025-01/FY%2719-DMHSAS-BPR.pdf (wayback 20250302110241)',
         'https://oksenate.gov/sites/default/files/2025-01/FY%2720-DMHSAS-BPR.pdf (wayback 20250302020713)',
         'https://oksenate.gov/sites/default/files/2025-01/FY%2721-DMHSAS-BPR.pdf (wayback 20250302110240)',
         'https://oksenate.gov/sites/default/files/2025-01/FY%2722-DMHSAS-BPR.pdf (wayback 20250301181941)',
         'https://oksenate.gov/sites/default/files/2025-01/FY%2723-DMHSAS-BPR.pdf (wayback 20250301211355)',
         'https://oksenate.gov/sites/default/files/2025-01/FY%2724-DMHSAS-BPR.pdf (wayback 20250302110240)'],
        ['FY19 value is the requested/projected grain (BPR published pre-legislature); flagged requested-vs-budgeted per row',
         'note the FY21 double-entry: FY21-requested 540,135,330 (FY21 BPR) vs FY21-budgeted 334,915,240 (FY22 BPR) — test uses the budgeted grain where both exist, kind field distinguishes'])

# ---- LA (v1 explicit-null FY25/26; pass replaces with OBH agency totals) ----
LA = [(2019, 258639525, 'Recommended FY2018-2019 (LDH Budget Summary table row Office of Behavioral Health)'),
      (2021, 283145371, 'Total Expenditures & Request Recommended FY2021-2022 (OBH agency summary)'),
      (2022, 287627774, 'Continuation FY2021-2022 col printed in FY23 volume (prior-year actuals 278,068,480; EOB 306,065,184 also captured)'),
      (2023, 350226050, 'Total Expenditures & Request Recommended FY2022-2023 (OBH summary)'),
      (2024, 392924759, 'Continuation FY2023-2024 (EOB 353,090,627; recommended 377,573,134 all-funds incl fed)'),
      (2025, 450190884, 'Continuation FY2024-2025 (recommended 436,462,850)'),
      (2026, 483526273, 'Continuation FY2025-2026 (recommended 500,343,728)'),
      (2027, 500071156, 'Continuation FY2026-2027 (recommended 490,114,774)')]
for fy, usd, kind in LA:
    add('LA', fy, usd, kind, False, 'no per-county table (LGEs = regions, v1 note)',
        ['https://www.doa.la.gov/media/ccxe3nys/09a_louisiana_department_of_health.pdf (FY2018-2019 vol)',
         'https://www.doa.la.gov/media/3hrj1z3f/09a_louisiana_department_of_health.pdf (FY2022-2023 vol)',
         'https://www.doa.la.gov/media/qocd0x3p/louisianadepartmentofhealth.pdf (FY2023-2024 vol)',
         'https://www.doa.la.gov/media/ydeps5wd/louisianadepartmentofhealth.pdf (FY2024-2025 vol)',
         'https://www.doa.la.gov/media/ommi3or4/louisianadepartmentofhealth.pdf (FY2025-2026 vol)',
         'https://www.doa.la.gov/media/slyl1orp/louisianadepartmentofhealth.pdf (FY2026-2027 vol)'],
        ['grain: LDH Office of Behavioral Health (agency 09-330) total funding (expenditures/means-of-finance) — includes federal funds; broader than purely state GF',
         'FY2020 null: FY19-20 volume not captured this pass (page-2 summary printed FY19 vol covers 2018-2019; FY20 row needs the 2019-2020 volume — route open)'],
        grain='OBH agency total incl federal')

# ---- TX (biennium flag; NOT for within-state test) ----
add('TX', 2017, 3727016349, 'biennial non-Medicaid/CHIP cross-article total, 2016-17 estimated/budgeted (LBB ID 3740 Feb-2017; GR 2,773,694,817)',
    False, 'no per-county state MH allocation table published',
    ['https://www.lbb.texas.gov/Documents/HAC_Summary_Recs/85R/3740_Behavioral_Health_Overview.pdf (wayback 20220119112944)'],
    ['BIENNIAL — not an annual figure; two fiscal years inside one number; flagged and EXCLUDED from the per-capita test',
     '2018-19 biennium recommended 3,548,482,248 all-funds non-Medicaid (same source)'])
add('TX', 2024, 4694614183, 'biennial non-Medicaid/CHIP cross-article total, 2020-21 estimated/budgeted (LBB ID 6820 Feb-2021; GR 3,304,258,502) → bookended FY2021',
    False, 'no per-county state MH allocation table published',
    ['https://www.lbb.texas.gov/Documents/HAC_Summary_Recs/87R/HAC_Behavioral_Health_Overview.pdf (wayback 20220124000916)'],
    ['BIENNIAL — excluded from the per-capita test; noted FY2022-23 House recommendations 4,241,586,793 all-funds non-Medicaid (same source, kind=biennial-recommended)'])

# ---- MA honest null FY19-21 (routes-tried) ----
for fy in [2019, 2020, 2021]:
    add('MA', fy, None, 'null-with-routes-tried', False,
        'mass.gov FY-26 Report on the Distribution of Funds = HTTP 403 to keyless fetch (v1 note)',
        ['routes tried this pass: mass.gov/info-details/fy21-budget (403)',
         'abh.memberclicks.net FY22 assets folder (not archived; folder fetch non-200)',
         'mamh-web.files.svdcdn.com FY23/FY24 briefs (returns blocking XML)',
         'wayback CDX on mass.gov/doc/* (archive.org intermittent 503/offline)',
         'massbudget.org budget-monitor CDX (no FY19-21 monitor hits in the 1500-row window)'],
        ['MA series stands at FY2022-FY2025 (4 years from v1) — below the >=5-year gate; no value invented'])

json.dump(rows, open(B + '_stmh2/pass2_rows.json', 'w', encoding='utf-8'), indent=1)

# ---- assemble v2: header line + v1 rows verbatim + pass rows ----
out = {'_method_note': HDR}
with open(B + 'state_mh_series_v2.jsonl', 'w', encoding='utf-8') as f:
    f.write(json.dumps(out, ensure_ascii=False) + '\n')
    for r in v1:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print('v2 rows written:', len(v1) + len(rows), '(v1', len(v1), '+ pass', len(rows), ')')
