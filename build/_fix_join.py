import json, re
from collections import defaultdict

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

# THE ROBUST-JOIN v2 = the fuzzy-year + the city-name-normalize!
def norm_city(c):
    c = (c or '').lower().strip()
    fixes = {"new york city": "new york city", "st. louis": "st. louis", "st louis": "st. louis"}
    return fixes.get(c, c)

def norm_year(y):
    m = re.search(r'((19|20)\d\d)', str(y))
    return int(m.group(1)) if m else None

# CRIME (both waves):
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

# CARE v2 normalized:
cc = json.load(open(B + 'crime_plus_care_plus_v2.json', encoding='utf-8'))
care = {}
for r in cc:
    c = norm_city(r.get('city')); y = norm_year(r.get('year'))
    if r.get('care_cage_ratio') is not None:
        care[(c, y)] = {'ratio': r.get('care_cage_ratio'), 'norm': r.get('care_plus_normalized')}

# EDU:
edu = {}
for r in json.load(open(B + 'edu_plus_v1_computed.json', encoding='utf-8')):
    c = norm_city(r.get('city')); y = norm_year(r.get('year'))
    if r.get('edu_plus') is not None:
        edu[(c, y)] = {'edu_plus': r.get('edu_plus'), 'basis': r.get('basis'), 'epc': r.get('epc')}

# BUILD-all-union-table (every key from the three lanes!):
all_keys = sorted(set(list(crime.keys()) + list(care.keys()) + list(edu.keys())))
field_crime = defaultdict(list)
for (c, y), v in crime.items():
    if not v.get('partial'):
        field_crime[y].append(v['rate'])
meds = {y: sorted(v)[len(v)//2] for y, v in field_crime.items() if len(v) >= 2}

out = []
for (c, y) in all_keys:
    v = crime.get((c, y)); ca = care.get((c, y)); e = edu.get((c, y))
    rate = v.get('rate') if v else None
    partial = v.get('partial') if v else False
    if rate and not partial and y in meds:
        crime_plus = round(rate/meds[y]*100, 1)
    elif rate and not partial:
        crime_plus = None
    else:
        crime_plus = None
    care_plus = ca.get('norm') if ca else None
    care_raw = ca.get('ratio') if ca else None
    out.append({'city': c, 'year': y, 'murders': v.get('murders') if v else None,
                'rate': rate, 'crime_plus': crime_plus, 'partial': partial,
                'care_raw': care_raw, 'care_plus_norm': care_plus,
                'edu_plus': e.get('edu_plus') if e else None,
                'edu_basis': e.get('basis') if e else None})

json.dump(out, open(B + 'triple_slider_v2.json', 'w', encoding='utf-8'), indent=1)
# THE the gap-count-after:
g = {'crime': 0, 'care': 0, 'edu': 0}
for r in out:
    if r.get('crime_plus') is None: g['crime'] += 1
    if r.get('care_plus_norm') is None: g['care'] += 1
    if r.get('edu_plus') is None: g['edu'] += 1
print(f'the union-table = {len(out)}-rows')
print('gaps-after-the-robust-join:', g)
