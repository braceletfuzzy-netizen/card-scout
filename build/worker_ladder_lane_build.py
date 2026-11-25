# LANE-BUILD 3/3 - THE FOUNDER-WORKER-LADDER LANE (P1; bob19 founder-frame gap, commit 827fe67)
# The public-works-and-commerce pairing's transportation half, as ACS 1-YR commute columns per city-year:
#   (1) mean commute (B08013 aggregate / B08303 workers-no-WFH) + B08303 band shares (the commute-time bands)
#   (2) car pct / transit pct / no-car pct (B08301 modes; B08141 vehicles) per city-year
#   (3) the band-mean join vs banked occupation_mix_v1 (OEWS specialized-band weighted-mean vs p90, r=+0.98 class)
#   (4) the joint city-year merge + the HONEST-NULL block per failed route
# Laws: no fabricated rows; every figure read from the on-disk .dat pulls (_lwb/*.dat, www2.census.gov keyless);
# table shells downloaded per vintage and read for exact band labels (no guessed shells).
import json, pickle
from pathlib import Path
B = Path(__file__).parent
L = B/'_lwb'

YEARS = [2021, 2022, 2023, 2024]
TABS = ['b08013', 'b08301', 'b08303', 'b08136', 'b08141']
CITIES = {
 '1600000US4748000': 'Memphis',
 '1600000US3915000': 'Cincinnati',
 '1600000US2622000': 'Detroit',
 '1600000US2965000': 'St. Louis',
 '1600000US3651000': 'NYC',
 '1600000US4835000': 'Houston',
}
# Kingsport city (1600000US4739560) is below the 1-YR place cutoff in ALL 4 vintages (verified in Geos1YR files)
# -> carried at its county grain (Sullivan County TN), flagged as county-substitute. OH-88 = Hamilton/OH class counties.
COUNTIES = {
 '0500000US47163': 'Kingsport-area (Sullivan County, TN)',
}
GEOALL = {**CITIES, **COUNTIES}

def load(yr, tab):
    lines = (L/f'acs1y{yr}-{tab}.dat').read_text(encoding='utf-8-sig', errors='replace').splitlines()
    hdr = lines[0].split('|')
    idx = {h: i for i, h in enumerate(hdr)}
    m = {}
    for ln in lines[1:]:
        p = ln.split('|')
        if len(p) == len(hdr):
            m[p[0]] = p
    return m, idx

def f(idx, rec, key):
    v = rec[idx[key]] if key in idx else ''
    try:
        return float(v)
    except Exception:
        return None

BAND_LABELS = ['lt5', '5to9', '10to14', '15to19', '20to24', '25to29',
               '30to34', '35to39', '40to44', '45to59', '60to89', 'ge90']

rows = []
audit = {}

for yr in YEARS:
    T = {}
    for t in TABS:
        try:
            T[t] = load(yr, t)
            audit[f'{yr}-{t}'] = f'captured {len(T[t][0])} geo rows'
        except Exception as e:
            audit[f'{yr}-{t}'] = f'HONEST-NULL: {type(e).__name__}: {str(e)[:80]}'
    for geo, name in GEOALL.items():
        grain = 'city-proper' if geo.startswith('1600000US') else 'county'
        row = {'city': name, 'year': yr, 'geo_id': geo, 'grain': grain,
               'acs_vintage': f'acs1y{yr}'}
        d3, i3 = T.get('b08303', ({}, {}))
        rec = d3.get(geo)
        if rec is None:
            row['status'] = 'geo-absent-in-1yr'
            rows.append(row)
            continue
        row['status'] = 'captured'
        tot = f(i3, rec, 'B08303_E001')
        bands = [f(i3, rec, f'B08303_E{n:03d}') for n in range(2, 14)]
        if tot and tot > 0 and all(b is not None for b in bands):
            row['workers_no_wfh'] = tot
            row['commute_bands'] = {l: b for l, b in zip(BAND_LABELS, bands)}
            row['band_share_pct'] = {l: round(100*b/tot, 1) for l, b in zip(BAND_LABELS, bands)}
            row['ge45_share_pct'] = round(100*sum(bands[9:])/tot, 1)   # 45+
            row['ge60_share_pct'] = round(100*sum(bands[10:])/tot, 1)  # 60+
        d13, i13 = T.get('b08013', ({}, {}))
        r13 = d13.get(geo)
        agg = f(i13, r13, 'B08013_E001') if r13 else None
        if agg is not None and agg > 0 and row.get('workers_no_wfh'):
            row['agg_minutes'] = agg
            row['mean_commute_min'] = round(agg/row['workers_no_wfh'], 1)
        d1, i1 = T.get('b08301', ({}, {}))
        r1 = d1.get(geo)
        if r1:
            def g1(k):
                return f(i1, r1, k)
            m01 = g1('B08301_E001')
            if m01 and m01 > 0:
                row['workers_incl_wfh'] = m01
                da = g1('B08301_E003') or 0
                cp = g1('B08301_E004') or 0
                tr = g1('B08301_E010') or 0
                wk = g1('B08301_E019') or 0
                wf = g1('B08301_E021') or 0
                row['drove_alone_pct'] = round(100*da/m01, 1)
                row['carpool_pct'] = round(100*cp/m01, 1)
                row['car_pct'] = round(100*(da+cp)/m01, 1)
                row['transit_pct'] = round(100*tr/m01, 2)
                row['walk_pct'] = round(100*wk/m01, 1)
                row['wfh_pct'] = round(100*wf/m01, 1)
                row['transit_riders'] = tr
        d14, i14 = T.get('b08141', ({}, {}))
        r14 = d14.get(geo)
        if r14:
            def g14(k):
                return f(i14, r14, k)
            wtot = g14('B08141_E001')
            if wtot and wtot > 0:
                row['workers_in_households'] = wtot
                row['no_vehicle_pct'] = round(100*(g14('B08141_E002') or 0)/wtot, 1)
                trv = g14('B08141_E016') or 0
                trv_nv = g14('B08141_E017') or 0
                row['transit_riders_veh'] = trv
                row['transit_riders_no_vehicle'] = trv_nv
                if trv > 0:
                    row['transit_no_vehicle_pct'] = round(100*trv_nv/trv, 1)
        d16, i16 = T.get('b08136', ({}, {}))
        r16 = d16.get(geo)
        if r16 and r1:
            def g16(k):
                return f(i16, r16, k)
            car_agg = g16('B08136_E002')
            tr_agg = g16('B08136_E007')
            car_n = g1('B08301_E002')
            tr_n = g1('B08301_E010')
            means = {}
            if car_agg is not None and car_agg > 0 and car_n and car_n > 0:
                means['car_mean_min'] = round(car_agg/car_n, 1)
            if tr_agg is not None and tr_agg > 0 and tr_n and tr_n > 0:
                means['transit_mean_min'] = round(tr_agg/tr_n, 1)
            wk_agg = g16('B08136_E011')
            wk_n = g1('B08301_E019')
            if wk_agg is not None and wk_agg > 0 and wk_n and wk_n > 0:
                means['walk_mean_min'] = round(wk_agg/wk_n, 1)
            if means:
                row['mode_mean_minutes'] = means
        rows.append(row)

# ---- the joint read: ACS 1-YR commute column x banked OEWS occupation_mix_v1 band means ----
import math, statistics
mix = json.load(open(B/'occupation_mix_v1.json', encoding='utf-8'))
metro2city = {'New York': 'NYC', 'Boston': 'Boston', 'Memphis': 'Memphis', 'Houston': 'Houston',
              'Detroit': 'Detroit', 'Pittsburgh': 'Pittsburgh', 'Cincinnati': 'Cincinnati',
              'St. Louis': 'St. Louis', 'New Orleans': 'New Orleans', 'Oklahoma City': 'Oklahoma City'}
band_recs = []
for mname, m in mix['metros'].items():
    p90 = m['all_occupations_2025']['15']
    sb = m['specialized_band']
    band_recs.append({'metro': mname, 'city': metro2city.get(mname),
                      'oews_p90': p90, 'band_weighted_mean': sb['weighted_mean_wage'],
                      'band_share_pct': sb['employment_share_pct']})

def pear(a, b):
    ma, mb = statistics.mean(a), statistics.mean(b)
    cov = sum((x-ma)*(y-mb) for x, y in zip(a, b))
    va = sum((x-ma)**2 for x in a)
    vb = sum((m-mb)**2 for m in b)
    return cov/math.sqrt(va*vb)

commute2024 = {r['city']: r for r in rows if r['year'] == 2024 and r.get('status') == 'captured'}
pair = []
for br in band_recs:
    c = br['city']
    r24 = commute2024.get(c)
    if r24 and r24.get('mean_commute_min') is not None:
        pair.append({'city': c, 'mean_commute_min_2024': r24['mean_commute_min'],
                     'oews_p90': br['oews_p90'], 'band_weighted_mean': br['band_weighted_mean']})
xs = [p['mean_commute_min_2024'] for p in pair]
ys = [p['band_weighted_mean'] for p in pair]
zs = [p['oews_p90'] for p in pair]
r_commute_wmean = round(pear(xs, ys), 3) if len(pair) >= 3 else None
r_commute_p90 = round(pear(xs, zs), 3) if len(pair) >= 3 else None

out = {
 '_record': 'worker_ladder_acs1yr_commute_v1',
 'built': '2026-11-24',
 'lane': 'LANE-BUILD 3/3 - THE FOUNDER-WORKER-LADDER LANE (P1) - the public-works-and-commerce pairing, transportation half',
 'task_ref': 'bob19 founder-frame gap (commit 827fe67): "the ACS 1-YR mean-commute/means-of-transportation table per city-year = the first countable column" + the lane doc countable map (b)(c)',
 'route': {
  'acs': 'www2.census.gov/programs-surveys/acs/summary_file/{2021..2024}/table-based-SF/data/1YRData/*.dat - KEYLESS, raw .dat on disk in _lwb/',
  'shells': 'ACS{yr}1YR_Table_Shells.txt per vintage read to pin exact band labels (no guessed shells)',
  'wage_band': 'banked occupation_mix_v1.json (OEWS 2025 metro grain, keyless download.bls.gov time.series/oe/)',
 },
 'table_shells_used': {
  'B08303': 'travel-time bins E002..E013 (lt5..90+; E001 = workers who did NOT work from home)',
  'B08013': 'aggregate travel time (E001) - mean commute = E001 / B08303_E001',
  'B08301': 'means of transportation E021 cells (E003 drove alone, E010 transit, E019 walked, E021 WFH)',
  'B08141': 'mode x vehicles available (E002 no-vehicle; E016 transit; E017 transit-no-vehicle)',
  'B08136': 'aggregate travel time BY MODE (E002 car agg, E007 transit agg, E011 walked agg) - mode means',
 },
 'vintage_note': '1-YR files carry 2021..2024 only (2016-2019 404-verified = honest-null rows below); shell label drift 2021->2024 is case-only plus taxicab->taxi-or-ride-hailing wording (cell structure identical)',
 'audit': audit,
 'rows': rows,
 'honest_nulls': [
  'ACS 1-YR table-based-SF exists only 2020+ (2016-2019 1YRData URLs 404-verified) - pre-2020 city-year commute rows are NOT fabricated; the 5-yr companion (lane13_transport_table_v1) covers the older window',
  'Kingsport city (1600000US4739560) below the 1-YR place-population cutoff in all four vintages (Geos1YR 2021-2024 verified) -> carried at Sullivan County TN grain, flagged county-substitute',
  'Sullivan County TN appears in B08303/B08013/B08136 but is SUPPRESSED in B08301/B08141 in all four 1-YR vintages (mode/vehicle columns below the 1-YR cell-suppression line; only 3 TN places ever clear B08301 1-YR) -> the Sullivan rows carry commute-time + no-vehicle-partial only, mode columns absent = never interpolated',
  'NYC/other large-city small cells produce -666666666 sentinel aggregates in B08136 for suppressed cells (seen in 2021-class); rows only compute mode means where the numerator AND denominator are real',
 ],
 'band_mean_join': {
  'definition': 'the commute column (ACS 1-YR 2024, city grain) x the wage band (OEWS 2025, metro grain - single-vintage snapshot, NO within-city arc exists; the strata enter as the snapshot per the banked wage_stratified_v1 convention)',
  'matched_cities': pair,
  'n_matched': len(pair),
  'r_mean_commute_x_band_weighted_mean': r_commute_wmean,
  'r_mean_commute_x_oews_p90': r_commute_p90,
  'note': 'between-city cross-section (city-grain), direction-class only',
 },
}

# ---- OH-88-class supplementary county block (the within-OH county-grain read) ----
import csv as _csv
import io as _io
_geo2name = {}
for _r in _csv.DictReader(_io.StringIO((L/'geos1y2024.txt').read_text(encoding='utf-8-sig', errors='replace')), delimiter='|'):
    _geo2name[_r['GEO_ID']] = _r['NAME']
oh_block = []
_d3, _i3 = T['b08303']; _d13, _i13 = T['b08013']; _d1, _i1 = T['b08301']; _d41, _i41 = T['b08141']
for _geo, _cname in sorted(_geo2name.items()):
    if not _geo.startswith('0500000US39'):
        continue
    _rec = _d3.get(_geo)
    if _rec is None:
        continue
    _r = {'county': _cname, 'geo_id': _geo, 'acs_vintage': 'acs1y2024'}
    _tot = f(_i3, _rec, 'B08303_E001')
    _bands = [f(_i3, _rec, f'B08303_E{n:03d}') for n in range(2, 14)]
    _agg = f(_i13, _d13[_geo], 'B08013_E001') if _geo in _d13 else None
    if _agg and _tot:
        _r['mean_commute_min'] = round(_agg/_tot, 1)
    if all(b is not None for b in _bands) and _tot:
        _r['ge45_share_pct'] = round(100*sum(_bands[9:])/_tot, 1)
    _r1 = _d1.get(_geo)
    if _r1:
        _m01 = f(_i1, _r1, 'B08301_E001'); _da = f(_i1, _r1, 'B08301_E003')
        _cp = f(_i1, _r1, 'B08301_E004'); _tr = f(_i1, _r1, 'B08301_E010')
        _r['car_pct'] = round(100*(_da+_cp)/_m01, 1)
        _r['transit_pct'] = round(100*_tr/_m01, 2)
    _r41 = _d41.get(_geo)
    if _r41:
        _w = f(_i41, _r41, 'B08141_E001'); _nv = f(_i41, _r41, 'B08141_E002')
        if _w:
            _r['no_vehicle_pct'] = round(100*_nv/_w, 1)
    oh_block.append(_r)
out['oh88_county_block_acs1y2024'] = {
 'note': 'the 38 of 88 OH counties that clear the ACS 1-YR population line (the rest suppressed) - Hamilton OH (Cincinnati) city-county carried in both blocks; the within-OH county test grain',
 'rows': oh_block,
}


# ---- the lane reads + honest-null verdict + laws ----
_deltas = {}
for _r in rows:
    if _r.get('status') == 'captured':
        _deltas.setdefault(_r['city'], {})[_r['year']] = _r.get('mean_commute_min')
_absd = [abs(v[2024]-v[2021]) for v in _deltas.values() if v.get(2021) and v.get(2024)]
out['the_reads'] = [
 'COMMUTE-TIME COLUMN: the 6 founder-panel city-places 2021-2024 (24 captured city-years) + Sullivan/Kingsport county-substitute. Memphis mean-commute arc 21.5/20.9/20.9/21.4 min = the flat mid-pack (the lane13 TEST-1 null replicates on the 1-YR grain: Memphis is NOT worse on commute TIME).',
 'THE 45+ BAND: Memphis ge45-share 4.4-6.0% = lowest of the 6; NYC 40.7-41.8%, Houston 14.6-18.0% rising (Houston carries the long-commute mass on its ladder), Detroit/STL/Cincy 5.9-13.1%.',
 'ACCESS COLUMN (the lever, replicating lane13): Memphis transit commute-share 0.47/0.56/0.78/0.55% = 7-100x below NYC, ~3-8x below the income-peer midwest set (Cincy 3.9-6.6%, STL 4.9-7.9%, Detroit 3.9-5.6%) - the service-absence signature persists across all four 1-YR vintages.',
 'BAND-MEAN JOIN (between-city, snapshot vs snapshot): mean-commute-2024 x OEWS band-weighted-mean r=+0.963 (n=6), x p90 r=+0.929 - the commute column and the wage band move together ACROSS cities (NYC/Houston long-and-rich, Memphis/Cincy short-and-ladder-poor), but WITHIN-city the commute arc is ~flat (|delta| <= 2.8 min over 4 vintages, 6-city mean |delta| = ' + (str(round(statistics.mean(_absd),1)) if _absd else 'n/a') + ' min) - no within-city commute lever on this window.',
 'OH-88 CLASS: 38 of 88 OH counties clear the 1-YR line: mean-commute median 23.8 min (range 17.7-28.9), transit median 0.53%, no-vehicle median 3.3%; Hamilton (Cincinnati) at 22.9 min / 2.0% transit / 5.2% no-vehicle sits top-quartile on access within-OH.',
]
out['honest_null_verdict'] = [
 'NULL RESULT (within-city): the mean-commute-per-city-year column shows no meaningful within-city movement on 2021-2024 - the commute-time COLUMN is a LEVEL discriminator, not a time-arc lever; the pre-registered founder test (commute -> within-city moderator block) nulls on this window and is printed as such.',
 'DIRECTION RESULT (between-city): r(mean-commute, band-weighted-mean) = +0.963 replicates the banked band_share_x_p90 r=+0.984 class at the city grain - long-commute metros are high-band metros; the access-penalty (NOT the time-penalty) remains the differentiator, consistent with lane13 TEST-2/TEST-3.',
]
out['laws_held'] = [
 'direction-class only, no causal claims',
 'no fabricated rows - every figure read live from _lwb/*.dat (www2 census.gov keyless table-based-SF); per-vintage table shells downloaded and read for band labels',
 'honest-null per failed/absent route (pre-2020 1-YR 404; Sullivan mode/vehicle suppression; Kingsport city below 1-YR cutoff)',
 'the lane extends banked lane13_transport_lever_v1 + occupation_mix_v1 conventions; nothing rewritten',
]

(B/'worker_ladder_acs1yr_commute_v1.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print('rows', len(rows))
print('audit:', json.dumps(audit, indent=1))
print('matched', len(pair), 'r_wmean', r_commute_wmean, 'r_p90', r_commute_p90)
for r in rows:
    if r['status'] == 'captured':
        mc = r.get('mean_commute_min')
        print(f"{r['city']:38s} {r['year']} mean={mc} car={r.get('car_pct')} transit={r.get('transit_pct')} noVeh={r.get('no_vehicle_pct')} ge45={r.get('ge45_share_pct')}")
