import json, os, glob
import re
from collections import defaultdict
SOC = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/_soc/'
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

# THE city-FRED-mapping:
fred_map = {
    'LAUCN220710000000003A': 'New Orleans', 'LAUCN360610000000003A': 'NYC',
    'LAUCN390610000000003A': 'Cincinnati', 'LAUCN482010000000003A': 'Houston',
    'LAUCN261630000000003A': 'Detroit', 'LAUCN471570000000003A': 'Memphis',
    'LAUCN400270000000003A': 'Oklahoma City', 'LAUCN420030000000003A': 'Pittsburgh',
    'LAUCN295100000000003A': 'St. Louis'}

# THE 1 = the unemployment = the FRED-years-1990-2025:
unemp = defaultdict(dict)
for f in glob.glob(SOC + 'fred_LAUCN*.csv'):
    series = f.split('fred_')[1].replace('.csv', '')
    city = fred_map.get(series)
    if not city: continue
    lines = open(f, encoding='utf-8').read().strip().split(chr(10))
    for l in lines[1:]:
        parts = l.split(',')
        if len(parts) >= 2:
            y = parts[0][:4]
            v = parts[1]
            if v and v not in ('.', 'NA', ''):
                unemp[city][int(y)] = float(v)
# the 50-largest-scrape = the city-proper-2021-25-bonus:
try:
    big50 = json.load(open(SOC + 'laus_50largest_2021_2025.json', encoding='utf-8'))
    print('the 50-largest = the keys:', list(big50.keys())[:3], '| count:', len(big50))
except Exception as e:
    big50 = {}
    print('the 50-largest = missing:', e)

# THE 2 = the ACS = the 2021-2025:
acs = json.load(open(SOC + 'acs_pov_bch.json', encoding='utf-8'))
acs_idx = defaultdict(dict)
for a in acs:
    acs_idx[(a['city'], a['year'])] = a

# THE 3 = the populations = the inherit:
pops = {}
for f in ('population_series_v1.jsonl', 'nola_houston_pair_v1.jsonl'):
    try:
        for l in open(B + f, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l)
            c = r.get('city') or r.get('era') or ''
            y = None
            m = re.match(r'^(19|20)\d\d', str(r.get('year') or r.get('era') or ''))
            if m: y = int(m.group(0)[:4])
            if not y: continue
            if r.get('population'):
                pops[(c if r.get('city') else r.get('era').split()[0], y)] = r['population']
    except FileNotFoundError:
        pass

# THE the union = the years = the each-city = the from-the-unemployment-arc (the 1990-2025) + the acs-2021-25:
out = []
cities = set(list(unemp.keys()))
all_years = set()
for c in cities:
    for y in unemp[c]:
        all_years.add((c, y))
for (c, y) in sorted(all_years):
    pass
# build = the per-city-year = the unemployment-primary:
all_years = set()
for c in cities:
    for y in unemp[c].keys():
        all_years.add((c, y))
for a in acs:
    all_years.add((a['city'], a['year']))

out = []
for (c, y) in sorted(all_years):
    u = unemp.get(c, {}).get(y)
    a = acs_idx.get((c, y))
    # the pop = the inherited = the approximate-match:
    p = pops.get((c, y))
    if not p:
        for dy in (1, -1, 2, -2, 3, -3):
            p = pops.get((c, y+dy))
            if p: break
    out.append({'city': c, 'year': y,
                'unemployment_rate': u,
                'poverty_rate': a.get('poverty_rate') if a else None,
                'children_poverty_pct': a.get('children_poverty_pct') if a else None,
                'median_income': a.get('median_income') if a else None,
                'bachelors_pct': a.get('bachelors_pct') if a else None,
                'single_parent_pct': None,  # B11001 = the next-pass lane!
                'population': p,
                'anchor_class': 'acs' if a else 'pep/interpolated',
                'source_refs': 'unemp: BLS-via-FRED-keyless(county-proxy-labeled; city-proper-STL); acs: ACS-table-based-SF-2021-25-keyless; pop: inherited-banks',
                'notes': 'unemp = county-proxy per FRED for 8-cities (the STL = city-proper); the city-proper-2021-25 = from-BLS-50largest-where-available'                        })

open(B + 'socioeconomic_series_v1.jsonl', 'w', encoding='utf-8', newline='').write(chr(10).join(json.dumps(r) for r in out) + chr(10))
print(f'WROTE socioeconomic_series_v1.jsonl: {len(out)} rows')
# the summary:
from collections import Counter
cs = Counter(r['city'] for r in out)
print('per-city:', dict(cs))
# the spot-check:
for r in out:
    if r['city'] == 'St. Louis' and r['year'] in (1995, 2002, 2017, 2024):
        print(' STL', r['year'], '| unemp', r.get('unemployment_rate'), '| poverty', r.get('poverty_rate'), '| pop', r.get('population'))
    if r['city'] == 'Boston' and r['year'] == 1995:
        print(' BOS 1995 | unemp', r.get('unemployment_rate'), '| poverty', r.get('poverty_rate'))
