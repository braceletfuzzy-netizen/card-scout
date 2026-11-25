import json, collections, math, statistics, re, os

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
OUT = B + 'care_bookings_ordering_v1.json'

# ---------- 1. CARE BOOK: city_component_annual_v1.jsonl ----------
care_rows = []
with open(B + 'city_component_annual_v1.jsonl', encoding='utf-8') as f:
    for line in f:
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        care_rows.append(json.loads(s))

# group into city-year-lane-component "units"; a unit is the source's own subcomponent
# breakouts. Unit total = the row with subcomponent 'total' if it exists, else the
# sum of the non-total rows (dedup law: never sum both).
by_unit = collections.defaultdict(list)
for r in care_rows:
    by_unit[(r['city'], r['year'], r['component'])].append(r)

units = {}
for (city, year, comp), rows in by_unit.items():
    has_total = any(r.get('subcomponent') == 'total' and r['usd'] is not None for r in rows)
    if has_total:
        usd = sum(r['usd'] for r in rows if r.get('subcomponent') == 'total')
        method = 'source-total-row'
    else:
        non_na = [r for r in rows if r['usd'] is not None]
        if non_na:
            usd = sum(r['usd'] for r in non_na)
            method = 'sum-non-total-rows'
        else:
            usd = None
            method = 'honest-null (not_applicable / no usd rows)'
    lanes = sorted({r['lane'] for r in rows if r.get('lane')})
    na_flag = any(r['basis'] == 'not_applicable' for r in rows)
    units[(city, year, comp)] = {
        'usd': usd, 'method': method, 'lanes': lanes,
        'basis': sorted({r['basis'] for r in rows}),
        'na_flag': na_flag
    }

care_lane_usd = collections.defaultdict(float)
care_city_year_components = collections.defaultdict(dict)
care_honest_null_units = []
for (city, year, comp), u in units.items():
    care_city_year_components[(city, year)][comp] = u['usd']
    if u['usd'] is not None:
        for ln in u['lanes']:
            care_lane_usd[(city, year, ln)] += u['usd']
    else:
        care_honest_null_units.append({'city': city, 'year': year, 'component': comp,
                                       'reason': u['method'],
                                       'basis_note_na': u['na_flag']})

care_city_year = {k: {c: v for c, v in d.items()} for k, d in care_city_year_components.items()}
care_total = {}
for (c, y), d in care_city_year.items():
    vals = [v for v in d.values() if v is not None]
    care_total[(c, y)] = sum(vals) if vals else None
    # coverage note: components with null
    nulls = [k for k, v in d.items() if v is None]
    if nulls:
        care_total_nulls[(c, y)] = nulls if (care_total_nulls := {}) is not None else nulls
care_partial = {}
for (c, y), d in care_city_year.items():
    nulls = [k for k, v in d.items() if v is None]
    if nulls:
        care_partial[(c, y)] = {'null_components': nulls}

print('care city-years:', len(care_total))

# ---------- 2. BOOKINGS BOOK A: bookings_series_v1.jsonl (UCR arrests proxy) ----------
book_series = []
with open(B + 'bookings_series_v1.jsonl', encoding='utf-8') as f:
    for line in f:
        s = line.strip()
        if not s or s.startswith('{  "_header"'):
            continue
        book_series.append(json.loads(s))
bookings_series = {}
series_meta = {}
for r in book_series:
    bookings_series[(r['city'], r['year'])] = r['bookings_total']
    series_meta[(r['city'], r['year'])] = {
        'months_present': r.get('months_present'), 'jurisdiction': r.get('jurisdiction'),
        'notes': r.get('notes')}
print('bookings series (city-years):', len(bookings_series), 'nulls:',
      sum(1 for v in bookings_series.values() if v is None))

# ---------- 3. BOOKINGS BOOK B: bookings_facility_v1.jsonl (facility grain; NYC usable) ----------
fac_rows = []
with open(B + 'bookings_facility_v1.jsonl', encoding='utf-8') as f:
    for line in f:
        s = line.strip()
        if not s or '_header' in s[:30]:
            continue
        fac_rows.append(json.loads(s))
fac_nyc = {}
for r in fac_rows:
    if r['city'] == 'NYC':
        fac_nyc[r['year']] = {
            'discharges': r['facility_bookings'],
            'admitted': r.get('admitted_annual'),
            'flags': r.get('flags', [])}
print('NYC facility years:', len(fac_nyc),
      'with data:', sum(1 for v in fac_nyc.values() if v['discharges'] is not None or v['admitted'] is not None))

# ---------- 4. MURDERS ----------
murders = {tuple(k.split('|')): v for k, v in json.load(open(B + 'murders_all_v1.json')).items()
           if v is not None}
murders = {(c, int(y)): v for (c, y), v in murders.items()}
print('murder city-years:', len(murders))

# ---------- 5. POPULATIONS (layered) ----------
pop = {}
popsrs = collections.defaultdict(dict)
with open(B + 'population_series_v1.jsonl', encoding='utf-8') as f:
    for line in f:
        s = line.strip()
        if not s: continue
        r = json.loads(s)
        popsrs[r['city']][r['year']] = r['population']
wide = collections.defaultdict(dict)
with open(B + 'populations_wide_v1.jsonl', encoding='utf-8') as f:
    for line in f:
        s = line.strip()
        if not s: continue
        r = json.loads(s)
        wide[r['city']][r['year']] = r['population']
v2 = collections.defaultdict(dict)
with open(B + 'populations_cities_v2.jsonl', encoding='utf-8') as f:
    for line in f:
        s = line.strip()
        if not s: continue
        r = json.loads(s)
        if r.get('record') == 'reproducibility_header':
            continue
        v2[r['city']][r['year']] = r['population']

NAME_MAP = {}  # dataset-city name -> frame-city name

def frame_city(c):
    return ({'New York': 'NYC', 'New York City': 'NYC'}.get(c, c))

def add_pop(city, year, population, source):
    if population is None: return
    fc = frame_city(city)
    key = (fc, year)
    pop[key] = {'population': population, 'pop_source': source}

for c, ys in popsrs.items():
    for y, p in ys.items(): add_pop(c, y, p, 'population_series_v1 (decennial anchors + linear interp)')
for c, ys in wide.items():
    for y, p in ys.items(): add_pop(c, y, p, 'populations_wide_v1 (PEP vintage-2019 SUMLEV 162)')
for c, ys in v2.items():
    for y, p in ys.items(): add_pop(c, y, p, 'populations_cities_v2 (PEP vintage-2025 SUMLEV 162)')
print('pop city-years:', len(pop))

json.dump({
    '_meta': 'stage-merge bank: care components + bookings + murders + pops',
    'care_city_year': {f'{c}|{y}': v for (c, y), v in care_city_year.items()},
    'care_total': {f'{c}|{y}': v for (c, y), v in care_total.items()},
    'care_partial': {f'{c}|{y}': v for (c, y), v in care_partial.items()},
    'bookings_series': {f'{c}|{y}': v for (c, y), v in bookings_series.items()},
    'bookings_series_meta': {f'{c}|{y}': v for (c, y), v in series_meta.items()},
    'fac_nyc': {str(y): v for y, v in sorted(fac_nyc.items())},
    'murders': {f'{c}|{y}': v for (c, y), v in sorted(murders.items())},
    'pop': {f'{c}|{y}': v for (c, y), v in sorted(pop.items())},
    'care_honest_null_units': care_honest_null_units,
}, open(B + '_test2_merge_bank.json', 'w', encoding='utf-8'), indent=1)
print('stage bank written')
