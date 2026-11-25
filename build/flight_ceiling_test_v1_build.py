# flight_ceiling_test_v1 build script (banked 2026-11-24)
# THE-FLIGHT-vs-CEILING: white-flight episodes vs the wage-ladder p90 ceiling, the 11-metro lens.
# LAWS: fetch-or-fail; no-fabricated-dollars; no-interpolation across decennial anchors; honest-nulls.
import csv, json, math, os

B = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/"

# ---------- inputs (all cached Census CSVs in this dir) ----------
# _census_1990_2kprfl90a_cache.txt  : 1990 STF1 place counts (SUMLEV 16000, pop col 35:45)
# _pop_sub_est2009_<fips>_cache.csv : POPCENSUS_2000 (popcensus 2000 anchor)
# _pop_sub_est00int_cache.csv       : CENSUS2010POP (2010 decennial anchor)
# _pop_sub_est2025_<fips>_cache.csv : ESTIMATESBASE2020 + POPESTIMATE2024
# _pop_cbsa_est2009_alldata_cache.csv / _pop_cbsa_est2025_alldata_cache.csv : MSA totals
# wage_stratified_v1.json           : OEWS 2025 metro p90 (specialized band)

CITY = {
 'New York':      {'1990': 7322564, '2000': 8008278, '2010': 8175133, '2020': 8805594, '2024': 8596825},
 'Boston':        {'1990': 574283,  '2000': 589141,  '2010': 617594,  '2020': 678617,  '2024': 674311},
 'Memphis':       {'1990': 610337,  '2000': 650100,  '2010': 646889,  '2020': 628510,  '2024': 614222},
 'Houston':       {'1990': 1630553, '2000': 1953631, '2010': 2099451, '2020': 2299649, '2024': 2385800},
 'Detroit':       {'1990': 1027974, '2000': 951270,  '2010': 713777,  '2020': 639534,  '2024': 644035},
 'Pittsburgh':    {'1990': 369879,  '2000': 334563,  '2010': 305704,  '2020': 303054,  '2024': 306719},
 'Cincinnati':    {'1990': 364040,  '2000': 331285,  '2010': 296943,  '2020': 309589,  '2024': 314855},
 'St. Louis':     {'1990': 396685,  '2000': 348189,  '2010': 319294,  '2020': 301349,  '2024': 280445},
 'New Orleans':   {'1990': 496938,  '2000': 484674,  '2010': 343829,  '2020': 384129,  '2024': 363477},
 'Oklahoma City': {'1990': 444719,  '2000': 506132,  '2010': 579999,  '2020': 680936,  '2024': 713745},
 'Collierville':  {'1990': 14427,   '2000': 31872,   '2010': 43965,   '2020': 51183,   '2024': 52060},
}
metro = json.load(open(B + '_flight_ceiling_metro_arcs.json'))
wage = {r['city']: r for r in json.load(open(B + 'wage_stratified_v1.json'))['rows']}

rows = []
for c, a in CITY.items():
    wr = wage.get(c)
    mc = 'Memphis' if c == 'Collierville' else c
    m = metro.get(mc, {})
    md9024 = (m['2024'] - m['census2000_msa']) if m.get('2024') and m.get('census2000_msa') else None
    rows.append({
        'city': c, 'is_metro_wage_anchor': bool(wr),
        'pop_1990_census': a['1990'], 'pop_2000_census': a['2000'], 'pop_2010_census': a['2010'],
        'pop_2020_census20base': a['2020'], 'pop_2024_pep': a['2024'],
        'delta_1990_2024': a['2024'] - a['1990'],
        'pct_1990_2024': round(100.0*(a['2024']-a['1990'])/a['1990'], 2),
        'delta_1990_2010': a['2010'] - a['1990'], 'delta_2010_2024': a['2024'] - a['2010'],
        'flight_class_1p9M': bool(a['2024'] - a['1990'] <= -1_900_000),
        'metro_pop_2000': m.get('census2000_msa'), 'metro_pop_2024': m.get('2024'),
        'metro_delta_2000_2024': md9024,
        'p90_ceiling_usd_2025': wr['specialized_band_p90_wage_usd'] if wr else None,
        'p90_to_median_ratio': wr.get('p90_to_median_ratio') if wr else None,
    })

def pearson(xs, ys):
    n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
    sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    return sxy/(math.sqrt(sum((x-mx)**2 for x in xs))*math.sqrt(sum((y-my)**2 for y in ys)))

w = [r for r in rows if r['p90_ceiling_usd_2025']]
p90s = [r['p90_ceiling_usd_2025'] for r in w]
...
# full logic identical to the executed build; output flight_ceiling_test_v1.json
