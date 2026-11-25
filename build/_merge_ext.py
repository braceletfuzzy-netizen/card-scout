import json, re
from collections import defaultdict

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

def norm_city(c):
    return (c or '').lower().strip()

def norm_year(y):
    m = re.search(r'((19|20)\d\d)', str(y))
    return int(m.group(1)) if m else None

# CRIME:
crime = {}
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl'):
    for l in open(B + f, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        c = norm_city(r.get('city')); y = norm_year(r.get('year'))
        m = r.get('murders'); pop = r.get('population')
        if m is not None and pop:
            rate = round(m/pop*100000, 1)
            note = str(r.get('data_quality')) + str(r.get('notes')) + str(r.get('year'))
            partial = 'YTD' in note or r.get('data_quality') == 'C'
            crime[(c, y)] = {'murders': m, 'rate': rate, 'partial': partial}

# CARE = the the PRIOR-banks + the EXTENSION (the merged!):
care = {}
for f in ('boston_care_cage_series_v1.jsonl', 'neworleans_care_cage_series_v1.jsonl',
          'stlouis_care_cage_series_v1.jsonl', 'cincinnati_care_cage_series_v1.jsonl',
          'memphis_care_cage_series_v1.jsonl', 'detroit_care_cage_series_v1.jsonl',
          'okc_care_cage_series_v1.jsonl', 'nyc_care_cage_series_v1.jsonl',
          'care_arc_extension_v1.jsonl'):
    try:
        for l in open(B + f, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l)
            era = str(r.get('era_or_year') or r.get('era') or r.get('year') or '')
            c_city = r.get('city') or ''
            # the the city-from-the-file = the the filename-per-run = the the extension-has-the-city:
            if not c_city:
                continue
            c = norm_city(c_city.split()[0]); y = norm_year(era)
            cu = r.get('care_usd_total'); ga = r.get('cage_usd_total')
            if cu and ga and y and y > 1970:
                care[(c, y)] = {'care': cu, 'cage': ga, 'ratio': round(cu/ga, 3)}
    except FileNotFoundError:
        pass

# EDU:
edu = {}
for r in json.load(open(B + 'edu_plus_v1_computed.json', encoding='utf-8')):
    c = norm_city(r.get('city')); y = norm_year(r.get('year'))
    if r.get('edu_plus') is not None:
        edu[(c, y)] = {'edu_plus': r.get('edu_plus'), 'basis': r.get('basis')}

# THE field-medians = the per-year-crime:
field_crime = defaultdict(list)
for (c, y), v in crime.items():
    if not v.get('partial'):
        field_crime[y].append(v['rate'])
meds = {y: sorted(v)[len(v)//2] for y, v in field_crime.items() if len(v) >= 2}

all_keys = sorted(set(list(crime.keys()) + list(care.keys()) + list(edu.keys())))
out = []; filled = 0
for (c, y) in all_keys:
    v = crime.get((c, y)); ca = care.get((c, y)); e = edu.get((c, y))
    rate = v.get('rate') if v else None
    partial = v.get('partial') if v else False
    crime_plus = round(rate/meds[y]*100, 1) if (rate and not partial and y in meds) else None
    care_ratio = ca.get('ratio') if ca else None
    care_plus = round(care_ratio*100, 1) if care_ratio else None
    ep = e.get('edu_plus') if e else None
    if care_ratio: filled += 1
    out.append({'city': c.title(), 'year': y, 'murders': v.get('murders') if v else None,
                'rate': rate, 'crime_plus': crime_plus, 'partial_flag': partial,
                'care_ratio': care_ratio, 'care_plus': care_plus,
                'edu_plus': ep, 'edu_basis': e.get('basis') if e else None})

json.dump(out, open(B + 'triple_slider_v3.json', 'w', encoding='utf-8'), indent=1)
g = {'crime': 0, 'care': 0, 'edu': 0}
for r in out:
    if r.get('crime_plus') is None: g['crime'] += 1
    if r.get('care_plus') is None: g['care'] += 1
    if r.get('edu_plus') is None: g['edu'] += 1
print(f'union = {len(out)}-rows | care-filled-total = {filled} | gaps = {g}')
