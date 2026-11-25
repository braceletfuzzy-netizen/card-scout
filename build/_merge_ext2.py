import json, re
from collections import defaultdict

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

def norm_city(c):
    c = (c or '').lower().strip()
    c = c.replace('st. louis', 'st louis').replace('st louis', 'st. louis')
    c = c.replace('new orleans', 'new orleans')
    return c

def city_key(c):
    # THE the canonical = the the normalized:
    c = norm_city(c)
    return {'new york city': 'new york city'}.get(c, c)

def norm_year(y):
    m = re.search(r'((19|20)\d\d)', str(y))
    return int(m.group(1)) if m else None

crime = {}
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl'):
    for l in open(B + f, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        c = city_key(r.get('city')); y = norm_year(r.get('year'))
        m = r.get('murders'); pop = r.get('population')
        if m is not None and pop:
            rate = round(m/pop*100000, 1)
            note = str(r.get('data_quality')) + str(r.get('notes')) + str(r.get('year'))
            partial = 'YTD' in note or r.get('data_quality') == 'C'
            crime[(c, y)] = {'murders': m, 'rate': rate, 'partial': partial}

care = {}
def add_care(city_raw, y, cu, ga):
    if cu and ga and y and y > 1970:
        care[(city_key(city_raw), y)] = {'care': cu, 'cage': ga, 'ratio': round(cu/ga, 3)}

for f in ('boston_care_cage_series_v1.jsonl', 'neworleans_care_cage_series_v1.jsonl',
          'stlouis_care_cage_series_v1.jsonl', 'cincinnati_care_cage_series_v1.jsonl',
          'memphis_care_cage_series_v1.jsonl', 'detroit_care_cage_series_v1.jsonl',
          'okc_care_cage_series_v1.jsonl', 'nyc_care_cage_series_v1.jsonl'):
    try:
        for l in open(B + f, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l)
            era = str(r.get('era_or_year') or r.get('era') or r.get('year') or '')
            y = norm_year(era)
            add_care(r.get('city') or f.split('_')[0], y, r.get('care_usd_total'), r.get('cage_usd_total'))
    except FileNotFoundError:
        pass

for l in open(B + 'care_arc_extension_v1.jsonl', encoding='utf-8'):
    if not l.strip(): continue
    r = json.loads(l)
    add_care(r.get('city'), norm_year(r.get('year')), r.get('care_usd_total'), r.get('cage_usd_total'))

edu = {}
for r in json.load(open(B + 'edu_plus_v1_computed.json', encoding='utf-8')):
    c = city_key(r.get('city')); y = norm_year(r.get('year'))
    if r.get('edu_plus') is not None:
        edu[(c, y)] = {'edu_plus': r.get('edu_plus'), 'basis': r.get('basis')}

field_crime = defaultdict(list)
for (c, y), v in crime.items():
    if not v.get('partial'):
        field_crime[y].append(v['rate'])
meds = {y: sorted(v)[len(v)//2] for y, v in field_crime.items() if len(v) >= 2}

all_keys = sorted(set(list(crime.keys()) + list(care.keys()) + list(edu.keys())))
out = []
for (c, y) in all_keys:
    if y is None or y < 1980: continue
    v = crime.get((c, y)); ca = care.get((c, y)); e = edu.get((c, y))
    rate = v.get('rate') if v else None
    partial = v.get('partial') if v else False
    crime_plus = round(rate/meds[y]*100, 1) if (rate and not partial and y in meds) else None
    care_ratio = ca.get('ratio') if ca else None
    ep = e.get('edu_plus') if e else None
    title = c.title().replace("St Louis", "St. Louis")
    out.append({'city': title, 'year': y, 'murders': v.get('murders') if v else None,
                'rate': rate, 'crime_plus': crime_plus, 'partial_flag': partial,
                'care_ratio': care_ratio, 'care_plus': round(care_ratio*100,1) if care_ratio else None,
                'edu_plus': ep, 'edu_basis': e.get('basis') if e else None})

json.dump(out, open(B + 'triple_slider_v3.json', 'w', encoding='utf-8'), indent=1)
# THE the fill-count:
g = {'crime': 0, 'care': 0, 'edu': 0}
filled_care = sum(1 for r in out if r.get('care_plus'))
both = sum(1 for r in out if r.get('crime_plus') and r.get('care_plus'))
print(f'union = {len(out)}-rows | care-filled = {filled_care} | crimexcare-both = {both} | gaps = {g}')
