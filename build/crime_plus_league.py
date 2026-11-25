import json
import math
from collections import defaultdict

# POLYSCOUT — CRIME+ & CARE+ v1 = THE FIRST LEAGUE TABLE (the founder-designed!)
# THE METHOD = the like-to-like + the field-normalized!

# THE CRIME ROWS (both waves):
crime = defaultdict(dict)
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl'):
    p = f'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/{f}'
    for l in open(p, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        y = r.get('year'); m = r.get('murders'); pop = r.get('population')
        if m is None or pop is None: continue
        # partial-year flags → annualize honestly, mark
        note = str(r.get('notes','')) + str(r.get('data_quality'))
        partial = 'YTD' in note or '2026' == str(y)
        crime[r['city']][int(y)] = {'murders': m, 'pop': pop, 'rate': m/pop*100000, 'partial': partial}

# THE CARE ROWS (from the fingerprint runs — the care/cage ratios per city-year):
care_files = {
    'Boston': 'boston_care_cage_series_v1.jsonl',
    'New York City': None,  # NYC = the ratio-window FY98-02 exists in nyc_care_cage_series_v1.jsonl
    'New Orleans': 'neworleans_care_cage_series_v1.jsonl',
    'St. Louis': 'stlouis_care_cage_series_v1.jsonl',
    'Cincinnati': 'cincinnati_care_cage_series_v1.jsonl',
    'Houston': 'nola_houston_pair_v1.jsonl',
    'Detroit': 'detroit_care_cage_series_v1.jsonl',
    'Memphis': 'memphis_care_cage_series_v1.jsonl',
}
care = defaultdict(dict)
for city, f in care_files.items():
    if f is None: continue
    p = f'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/{f}'
    try:
        for l in open(p, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l)
            era = str(r.get('era_or_year') or r.get('era') or r.get('year'))
            care_usd = r.get('care_usd_total'); cage_usd = r.get('cage_usd_total')
            if care_usd and cage_usd:
                import re
                ym = re.search(r'(19|20)\d\d', era)
                if ym:
                    y = int(ym.group(0))
                    care[city][y] = {'care': care_usd, 'cage': cage_usd, 'ratio': round(care_usd/cage_usd, 3)}
    except FileNotFoundError:
        pass

# NYC ratio lanes from its own file:
try:
    for l in open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/nyc_care_cage_series_v1.jsonl', encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        y = r.get('year')
        if y:
            c = r.get('care_usd_total') or r.get('care'); g = r.get('cage_usd_total') or r.get('cage')
            if c and g:
                care.setdefault('New York City', {})[int(y)] = {'care': c, 'cage': g, 'ratio': round(c/g,3)}
except FileNotFoundError:
    pass

# THE FIELD COMPUTATION (per-year across all cities = the field median):
all_rows = []
field = defaultdict(list)
for city, ys in crime.items():
    for y, v in ys.items():
        if not v.get('partial'):
            field[y].append(v['rate'])
field_medians = {y: sorted(v)[len(v)//2] for y, v in field.items() if len(v) >= 2}

print('=== THE CRIME+ / CARE+ LEAGUE TABLE v1 (the field-normalized = 100 = in-line) ===')
print()
print(f"{'CITY':14s} {'YR':6s} {'murders':>8s} {'rate':>7s} {'CRIME+':>7s} {'care/cage':>9s} {'CARE+':>6s}")
print('-'*64)
out_rows = []
for city in sorted(crime.keys()):
    for y in sorted(crime[city].keys()):
        v = crime[city][y]
        if v.get('partial'):
            continue
        fm = field_medians.get(y)
        crime_plus = round(v['rate']/fm*100, 1) if fm else None
        cr = care.get(city, {}).get(y)
        care_plus = None; ratio_str = '—'
        if cr:
            ratio_str = f"{cr['ratio']}"
        out_rows.append({'city': city, 'year': y, 'murders': v['murders'], 'rate': round(v['rate'],1),
                         'crime_plus': crime_plus, 'care_cage_ratio': cr['ratio'] if cr else None,
                         'care_usd': cr['care'] if cr else None})
        print(f"{city:14s} {y:<6d} {v['murders']:>8} {v['rate']:>7.1f} {str(crime_plus):>7s} {ratio_str:>9s} {str(round(cr['ratio']*100,1) if cr else ''):>6s}")

json.dump(out_rows, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/crime_plus_care_plus_v1.json', 'w', encoding='utf-8'), indent=1)
print()
print(f'WROTE crime_plus_care_plus_v1.json ({len(out_rows)} paired rows)')
