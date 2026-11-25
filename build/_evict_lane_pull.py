# _evict_lane_pull.py — EVICTION-JUDGMENT-RATE LANE (bob19 output-blind-spot P1)
# Eviction Lab keyless S3 (eviction-lab-data-downloads bucket, Open Data Commons BY license):
#   place_proprietary_2000_2018.csv = observed city-grain filings/judgments 2000-2018 (judgment_rate per 1k renter)
#   legacy validated cities.csv = cross-check eviction-rate 2000-2016
#   ets/all_sites_monthly.csv = COVID-era ETS monthly filings 2020-2025 for tracked sites (aggregate = city filings-count proxy, NOT a judgment rate — filings-freeze flagged)
# Covid freeze: 2020-21 flagged; ETS rows give filings only (no judgments).
import csv, json, collections
from pathlib import Path
B = Path(r"C:\Users\J\Documents\LLM\cardscout-2.0\For You\PolyScout\build")
R = B/'_bob19_outputs'/'_evict_raw'
O = B/'_bob19_outputs'

GEO = {'4748000':'Memphis','3915000':'Cincinnati','2622000':'Detroit','2965000':'St. Louis','3651000':'NYC','4835000':'Houston','0820000':'Denver','4739560':'Kingsport'}
ROWS = []
with open(R/'evl_est_place_estimates.txt_hdr', encoding='utf-8-sig') as f:
    rd = csv.DictReader(f)
    for r in rd:
        if r['id'] in GEO and r['year'] >= '2016':
            ROWS.append({'place_fips': r['id'], 'place_name': r['name'], 'city': GEO[r['id']], 'year': int(r['year']),
                'eviction_filings': float(r['filings']) if r['filings'] else None,
                'filing_rate_per_1k_renter': float(r['filing_rate']) if r['filing_rate'] else None,
                'evictions_judgments': float(r['judgements']) if r['judgements'] else None,
                'judgment_rate_per_1k_renter': float(r['judgement_rate']) if r['judgement_rate'] else None,
                'threatened_rate_per_1k_renter': float(r['threatened_rate']) if r['threatened_rate'] else None,
                'grain': 'place', 'source': 'evictionlab place_proprietary_2000_2018 (observed)',
                'covid_freeze_flag': 1 if r['year'] in ('2020','2021') else 0})
# legacy validated 2016 cross-check
LEG = {}
with open(R/'evl_cities_all.csv', encoding='utf-8-sig') as f:
    rd = csv.DictReader(f)
    for r in rd:
        if r['GEOID'] in GEO and r['year'] == '2016':
            LEG[GEO[r['GEOID']]] = {'legacy_2016_eviction_rate': float(r['eviction-rate']) if r['eviction-rate'] else None,
                                    'legacy_2016_filing_rate': float(r['eviction-filing-rate']) if r['eviction-filing-rate'] else None}
# ETS 2020-2025 filings aggregate per tracked city (tracts/zip summed monthly)
ETS = collections.defaultdict(lambda: collections.defaultdict(float))
ETS_GEOS = collections.defaultdict(set)
with open(R/'evl_ets_all_sites_monthly.csv', encoding='utf-8-sig') as f:
    rd = csv.DictReader(f)
    for r in rd:
        yr = r['month'][-4:]
        if r['city'] in ('Memphis, TN','Cincinnati, OH','New York, NY','Houston, TX'):
            ETS[r['city']][yr] += float(r['filings_2020'] or 0)
            ETS_GEOS[r['city']].add(r['GEOID'])
print('ETS cities found:', list(ETS), {c: len(g) for c, g in ETS_GEOS.items()})

# merge ETS + legacy into ROWS per city-year
idx = {(r['city'], r['year']): r for r in ROWS}
for (c, yr) in list(idx):
    r = idx[(c, yr)]
    r['legacy_2016_crosscheck'] = LEG.get(c, {}).get('legacy_2016_eviction_rate') if r['year'] == 2016 else None
ets_names = {'Memphis, TN':'Memphis','Cincinnati, OH':'Cincinnati','New York, NY':'NYC','Houston, TX':'Houston'}
for cname, years in ETS.items():
    for yr, filings in sorted(years.items()):
        if int(yr) in (2020, 2021, 2022, 2023, 2024, 2025):
            ROWS.append({'place_fips': None, 'city': ets_names[cname], 'year': int(yr),
                'eviction_filings_monthly_sum_ets': filings, 'ets_geoids_summed': len(ETS_GEOS[cname]),
                'judgment_rate_per_1k_renter': None, 'filing_rate_per_1k_renter': None,
                'grain': 'place (ETS tract-sum proxy)', 'source': 'evictionlab ETS all_sites_monthly',
                'covid_freeze_flag': 1})
ROWS.sort(key=lambda r: (r['city'], r['year']))
(O/'_evict_raw_rows.json').write_text(json.dumps(ROWS, indent=1), encoding='utf-8')
per = collections.defaultdict(list)
for r in ROWS: per[r['city']].append(r['year'])
for c, ys in sorted(per.items()): print(c, len(ys), sorted(ys))
print('DONE', len(ROWS), 'rows')
