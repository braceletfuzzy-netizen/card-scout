"""Assemble MENTAL-HEALTH-LANE panel: mental_health_series_v1.jsonl (one-row-per-city-year).

Reproducibility header note inside the file (founder steer #7).
Inputs (all built earlier in build/):
  _mh_census_extract.json          Census COG E-code family extract 1992/2012/2014
  _samhsa_city_attributed.json     USASpending SAMHSA-CFDA grants, recipient-name city attribution
  _facilities_county.jsonl         findtreatment.gov locator county-grain facility counts
  _suicide_county_all.json         CDC Socrata psx4-wq38 All_Suicide county rows 2019-2024
  _mh_subline_bank.json            printed MH sublines (capture-as-declared)
"""
import json, os

B = os.path.dirname(os.path.abspath(__file__))
DEEP = ['Boston', 'NYC', 'New Orleans', 'St. Louis', 'Cincinnati', 'Houston',
        'Detroit', 'Memphis', 'OKC', 'Pittsburgh']
NORM = {'Boston': 'Boston', 'New York': 'NYC', 'New Orleans': 'New Orleans',
        'St. Louis': 'St. Louis', 'Cincinnati': 'Cincinnati', 'Houston': 'Houston',
        'Detroit': 'Detroit', 'Memphis': 'Memphis', 'Oklahoma City': 'OKC',
        'Pittsburgh': 'Pittsburgh'}

sam = json.load(open(os.path.join(B, '_samhsa_city_attributed.json')))
sam2 = {NORM.get(c, c): ys for c, ys in sam.items()}

cen_rows = json.load(open(os.path.join(B, '_mh_census_extract.json')))
cen2 = {}
for r in cen_rows:
    if 'error' in r:
        continue
    cen2[(NORM.get(r['city'], r['city']), r['year'])] = r

fac = {}
for l in open(os.path.join(B, '_facilities_county.jsonl')):
    d = json.loads(l)
    fac[d['geoid']] = d
FACMAP = {'42003': 'Pittsburgh', '48201': 'Houston', '26163': 'Detroit',
          '47157': 'Memphis', '39061': 'Cincinnati', '22071': 'New Orleans',
          '25017': 'Boston', '40109': 'OKC', '29510': 'St. Louis'}
FACNYC = ['36061', '36047', '36081', '36085', '36005']  # NYC = sum of 5 borough counties

su_rows = json.load(open(os.path.join(B, '_suicide_county_all.json')))
SUMAP = {'42003': 'Pittsburgh', '48201': 'Houston', '26163': 'Detroit',
         '47157': 'Memphis', '39061': 'Cincinnati', '22071': 'New Orleans',
         '25017': 'Boston', '40109': 'OKC', '29510': 'St. Louis',
         '36005': 'NYC', '36047': 'NYC', '36061': 'NYC', '36081': 'NYC', '36085': 'NYC'}
sui = {}
for r in su_rows:
    g = SUMAP.get(r['geoid'])
    if not g:
        continue
    sui.setdefault((g, int(r['period'])), []).append(
        {'geoid': r['geoid'], 'rate': float(r['rate']), 'count': int(r['count_sup'])})

# printed sublines, capture-as-declared (verified extractions this pass)
HOUSTON_MH = {2024: 6732000, 2025: 6990000, 2026: 7227000}   # Police Dept Mental Health program
OKC_MIH = {2025: 4171088, 2026: 4360706, 2027: 4619468}      # Mobile Integrated Health program

CHANNEL = {
    'Boston': {
        'channel_class': 'merged-into-health-line',
        'channel_cite': "Boston Public Health Commission (BPHC) carries BH incl. MH + substance-abuse prevention (bos_fy23_budget narrative: 'substance abuse prevention and treatment programs' inside PHC); no separately-printed MH department line",
    },
    'NYC': {
        'channel_class': 'city-county-consolidated (not-countable city-separate grain this pass)',
        'channel_cite': "NYC DOHMH = city-county consolidated; behavioral-health is an executive-division grain, not a printed separate MH line in dept-level data",
    },
    'New Orleans': {
        'channel_class': 'merged-into-health-line',
        'channel_cite': "NOHD Health (Core) carries BH; Justice & Mental Health Collaboration + Mobile Crisis Intervention Unit (MCIU, 2023) are program/grant sublines not separately printed USD in operating tables",
    },
    'St. Louis': {
        'channel_class': 'separate-city-department (Human Services dept) + city MH board (separate levy entity)',
        'channel_cite': "St. Louis City Dept of Human Services + the City Mental Health Board (St. Louis Mental Health Board, prop-N levy) sits parallel to the city ledger",
    },
    'Cincinnati': {
        'channel_class': 'county-runs-it',
        'channel_cite': "Hamilton County Mental Health & Recovery Services Board (levy-funded) is the BH funder; Houston-class city Health dept does not print an MH line",
        'county_entity': 'Hamilton County Mental Health & Recovery Services Board',
    },
    'Houston': {
        'channel_class': 'separate-printed-program',
        'channel_cite': "Houston Police Dept 'Mental Health' program printed in FY2026 Adopted Budget program tables (CIRT/HOT/CIT); SUD via Houston Opioid Abatement Fund (separately-constituted fund)",
    },
    'Detroit': {
        'channel_class': 'merged-into-health-line + county/state channels',
        'channel_cite': "Detroit Health & Wellness Promotion GF carries public-health grain (FY26 20.9M); BH services mostly Wayne County / MDHHS channels",
    },
    'Memphis': {
        'channel_class': 'state-runs-it',
        'channel_cite': "TN Dept of Mental Health & Substance Abuse Services is the funder; city/county Health dept grain is public-health only",
    },
    'OKC': {
        'channel_class': 'state-runs-it + city-printed-program',
        'channel_cite': "ODMHSAS funds the county system; OKC prints Mobile Integrated Health (crisis/behavioral-health response) program inside Operations Services and MAPS4 Mental Health capital projects",
    },
    'Pittsburgh': {
        'channel_class': 'county-runs-it',
        'channel_cite': "Allegheny County DHS Office of Behavioral Health is the BH funder; Pittsburgh city Health dept does not carry BH service lines",
        'county_entity': 'Allegheny County DHS Office of Behavioral Health',
    },
}

HDR = {
    '_method_note': (
        'REPRODUCIBILITY HEADER. Every row carries method + sources + routes in source_refs/notes so any '
        'entity can rerun the same path. Routes: (a) census = Census COG 1992/2012/2014 individual-unit '
        'public-use files (_census/ dir; parser census_universal_parser_v1-class, E-code letter dictionary '
        'verified against each vintage tech doc; NO literal mental-health code exists in any COG vintage — '
        'the E50/51/52 public-welfare reference maps to Housing&CD E50 / Libraries E52, E51 does not exist; '
        'the MH-proximal countable family is E32 health/E36+E38 hospitals/E67-E79 welfare-vendor-cash-'
        'institutional family: banked as census_welfare_health_family_usd); (b) SAMHSA = USASpending v2 '
        'spending_by_award, SAMHSA-CFDA award set {93.242, 93.243, 93.958, 93.959, 93.944, 93.977, 93.230, '
        '93.245, 93.244, 93.952, 93.941}, state place-of-performance universe then recipient-name city '
        'attribution (POP city fields are null in USASpending feed; rule = case-insensitive token match on '
        'recipient name, undercounts non-city-named recipients — noted-grain); year = federal FY of award '
        'start; SAMHSA = federal_external channel: noted-never-summed (fund-aware-v2); (c) facilities = '
        'SAMHSA treatment locator backend (findtreatment.gov /locator/listing county-grain, snapshot Nov '
        '2026, dedupe on name+street+zip); (d) suicide = CDC Socrata psx4-wq38 Mapping IOV All_Suicide '
        'county rows 2019-2024, NYC = unweighted mean of 5 counties (flagged), Boston row = geoid 25017 '
        'Middlesex County proxy (NOT Suffolk — honest-flag); (e) MH/SUD sublines = capture-as-declared '
        'from local budget books only where the books PRINT the line (books\' own structure IS the '
        'taxonomy; no forced split; combined lines stay combined; the bh_combined column stays null unless '
        'a printed combined line was captured).'
    ),
    '_federal_channel': 'samhsa_grants_usd = noted-never-summed (fund-aware-v2 federal_external).',
    '_channel_class_legend': 'merged-into-health-line | separate-printed-program | county-runs-it | state-runs-it | city-county-consolidated (not-countable city-separate grain this pass)',
}

out_path = os.path.join(B, 'mental_health_series_v1.jsonl')
rows = []
for c in DEEP:
    ch = CHANNEL[c]
    for y in range(2009, 2027):
        row = {'city': c, 'year': y,
               'city_mh_line_usd': None,
               'mental_health_subline_usd': None,
               'sud_subline_usd': None,
               'bh_combined_line_usd': None,
               'census_welfare_health_family_usd': None,
               'samhsa_grants_usd': None,
               'samhsa_n_awards': None,
               'facilities_count': None,
               'suicide_rate': None,
               'channel_class': ch['channel_class'],
               'channel_class_cite': ch['channel_cite'],
               'source_refs': [],
               'notes': []}
        if ch.get('county_entity') and y == 2009:
            row['notes'].append('county_entity: ' + ch['county_entity'])
        r = cen2.get((c, y))
        if r:
            tot = sum(r['codes_usd_x1000'].values()) * 1000
            row['census_welfare_health_family_usd'] = tot
            row['source_refs'].append(
                "Census COG %d individual-unit public-use file (unit %s; E32/E36/E68/E74/E75/E77/E79 "
                "current-operation entries x1000; file: %s)" % (y, r['entity_id'],
                'https://www2.census.gov/govs/' + ('estimate/92censusindunit.zip' if y == 1992
                 else 'local/2012_Individual_Unit_File_Revised.zip' if y == 2012
                 else 'local/2014_Individual_Unit_File_Revised.zip')))
            if not r['codes_usd_x1000']:
                row['notes'].append('honest-null: city prints no countable welfare/health E-code entries in %d COG file (Memphis 2012/2014 = merged into county/shelby channels)' % y)
        ys = sam2.get(c, {})
        sv = ys.get(str(y))
        if sv:
            row['samhsa_grants_usd'] = sv['usd']
            row['samhsa_n_awards'] = sv['n_awards']
            row['source_refs'].append(
                'USASpending v2 spending_by_award; SAMHSA-CFDA set; recipient-name city attribution; FY=start-year; federal_external noted-never-summed')
        elif 2010 <= y <= 2025:
            row['samhsa_grants_usd'] = 0.0
        g = [k for k, v in FACMAP.items() if v == c]
        if g:
            row['facilities_count'] = fac[g[0]]['facilities_count_dedupe']
            row['source_refs'].append(
                'SAMHSA treatment locator findtreatment.gov /locator/listing county %s; snapshot Nov 2026; dedupe name+street+zip' % g[0])
        if c == 'NYC' and all(k in fac for k in FACNYC):
            row['facilities_count'] = sum(fac[k]['facilities_count_dedupe'] for k in FACNYC)
            row['source_refs'].append('SAMHSA treatment locator findtreatment.gov county-grain, NYC = SUM of 5 borough counties (%s); snapshot Nov 2026' % ','.join(FACNYC))
        if y >= 2019:
            sl = sui.get((c, y))
            if sl:
                row['suicide_rate'] = round(sum(x['rate'] for x in sl) / len(sl), 1)
                row['source_refs'].append(
                    'CDC Socrata psx4-wq38 Mapping-IOV All_Suicide county rows %s (per 100k)' % ','.join(sorted(x['geoid'] for x in sl)))
                if c == 'NYC':
                    row['notes'].append('suicide_rate = UNWEIGHTED mean of 5 NYC counties (Bronx/Kings/New York/Queens/Richmond) — flagged proxy')
        if c == 'Boston' and y >= 2019:
            row['notes'].append('HONEST-FLAG: suicide geoid 25017 = Middlesex County (proxy), NOT Suffolk/Boston')
        if c == 'Houston' and y in HOUSTON_MH:
            row['mental_health_subline_usd'] = HOUSTON_MH[y]
            row['source_refs'].append('hou26_FY2026_Adopted_Budget pdftotext p-PD Mental Health program table (thousands x1000): FY2024 Actual / FY2025 Estimate / FY2026 Budget')
        if c == 'OKC' and y in OKC_MIH:
            row['mental_health_subline_usd'] = OKC_MIH[y]
            row['source_refs'].append('okc_fy27_budget.pdf pdftotext C-60 Mobile Integrated Health program table: FY25 Actual / FY26 Adopted / FY27 Adopted')
        if c == 'Houston' and y == 2026:
            row['notes'].append('SUD vein printed channel: Houston Opioid Abatement Fund (separately-constituted fund; program USD not itemized in scanned pages) — noted')
        if c == 'New Orleans' and y in (2019, 2020):
            row['notes'].append('SUD-vein printed subline: Sobering Center $600,000 General Fund (fy2019/fy2020_bib books) — capture-as-declared candidate')
        if c == 'New York' and y >= 2010:
            row['notes'].append('SAMHSA-attribution heavy-caveat: NYC recipient names (NYU/Columbia/Mt Sinai/Cornell/RFMH) carry big NYC-attributed grants; state-agency recipients (NYS OASAS/OMH via RFMH) included via RFMH token rule')
        rows.append(row)

# prune: keep rows that have at least one data field beyond channel_class
def has_data(r):
    return any(r[k] is not None for k in
               ('city_mh_line_usd', 'mental_health_subline_usd', 'sud_subline_usd',
                'bh_combined_line_usd', 'census_welfare_health_family_usd',
                'samhsa_grants_usd', 'facilities_count', 'suicide_rate'))
kept = [r for r in rows if has_data(r)]
with open(out_path, 'w') as f:
    f.write(json.dumps(HDR) + "\n")
    for r in kept:
        f.write(json.dumps(r) + "\n")
print('wrote', out_path, len(kept), 'data rows of', len(rows), 'skeleton rows')
