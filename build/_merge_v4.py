import json, re
from collections import defaultdict

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

def norm_city(c):
    return (c or '').lower().strip()

def norm_year(y):
    m = re.search(r'((19|20)\d\d)', str(y))
    return int(m.group(1)) if m else None

# Step 1: collect murders
murders = {}
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl'):
    for l in open(B + f, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        c = norm_city(r.get('city')); y = norm_year(r.get('year'))
        if r.get('murders') is not None and y:
            if (c, y) not in murders or murders[(c, y)] < r.get('murders'):
                murders[(c, y)] = r.get('murders')

# Step 2: inject populations
pops = {}
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl'):
    for l in open(B + f, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        c = norm_city(r.get('city')); y = norm_year(r.get('year'))
        if r.get('population') and y:
            pops.setdefault((c, y), r.get('population'))
for l in open(B + 'population_series_v1.jsonl', encoding='utf-8'):
    if not l.strip(): continue
    r = json.loads(l)
    c = norm_city(r.get('city')); y = norm_year(r.get('year'))
    if r.get('population') and y:
        pops.setdefault((c, y), r.get('population'))

# Step 3: partials (2026 YTD across cities)
partials = set()
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl'):
    for l in open(B + f, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        c = norm_city(r.get('city')); y = norm_year(r.get('year'))
        blob = str(r.get('notes','')) + str(r.get('data_quality','')) + str(r.get('year'))
        if 'YTD' in blob or 'Nov' in blob or 'partial' in blob.lower() or y == 2026:
            if y == 2026:
                partials.add((c, y))

# Step 4: rates everywhere
rates = {}
for (c, y), m in murders.items():
    p = pops.get((c, y))
    if p and m:
        rates[(c, y)] = round(m/p*100000, 1)

field = defaultdict(list)
for (c, y), rate in rates.items():
    if (c, y) not in partials:
        field[y].append(rate)
meds = {y: sorted(v)[len(v)//2] for y, v in field.items() if len(v) >= 2}

# Step 5: care + edu
care = {}
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
            cc = r.get('city') or f.split('_')[0]
            cu = r.get('care_usd_total'); ga = r.get('cage_usd_total')
            if cu and ga and y and y > 1970:
                care[(norm_city(cc), y)] = round(cu/ga, 3)
    except FileNotFoundError:
        pass
for l in open(B + 'care_arc_extension_v1.jsonl', encoding='utf-8'):
    if not l.strip(): continue
    r = json.loads(l)
    y = norm_year(r.get('year'))
    cu = r.get('care_usd_total'); ga = r.get('cage_usd_total')
    if cu and ga and y:
        care[(norm_city(r.get('city')), y)] = round(cu/ga, 3)

edu = {}
for r in json.load(open(B + 'edu_plus_v1_computed.json', encoding='utf-8')):
    c = norm_city(r.get('city')); y = norm_year(r.get('year'))
    if r.get('edu_plus') is not None:
        edu[(c, y)] = {'edu_plus': r.get('edu_plus'), 'basis': r.get('basis')}

Step6 = sorted(set(list(rates.keys()) + list(care.keys()) + list(edu.keys())))
out = []
for (c, y) in Step6:
    if y is None or y < 1980: continue
    rate = rates.get((c, y))
    partial = (c, y) in partials
    crime_plus = round(rate/meds[y]*100, 1) if (rate is not None and not partial and y in meds) else (round(rate/meds[y]*100,1) if rate and not partial and y in meds else None)
    care_ratio = care.get((c, y))
    e = edu.get((c, y))
    title = c.title().replace("St Louis", "St. Louis")
    out.append({'city': title, 'year': y, 'murders': murders.get((c, y)),
                'population': pops.get((c, y)), 'rate': rate,
                'crime_plus': crime_plus, 'partial_flag': partial,
                'care_ratio': care_ratio, 'care_plus': round(care_ratio*100,1) if care_ratio else None,
                'edu_plus': e.get('edu_plus') if e else None, 'edu_basis': e.get('basis') if e else None})

out.sort(key=lambda x: (x['city'], x['year']))
json.dump(out, open(B + 'triple_slider_v4.json', 'w', encoding='utf-8'), indent=1)

filled = {
    'crime_plus': sum(1 for r in out if r.get('crime_plus') is not None),
    'care_plus': sum(1 for r in out if r.get('care_plus') is not None),
    'edu_plus': sum(1 for r in out if r.get('edu_plus') is not None),
    'both_crime_care': sum(1 for r in out if r.get('crime_plus') is not None and r.get('care_plus') is not None),
    'triple': sum(1 for r in out if r.get('crime_plus') is not None and r.get('care_plus') is not None and r.get('edu_plus') is not None),
    'total_rows': len(out)
}
print('THE TRUE-FILLED-COUNTS (values, not keys):', json.dumps(filled))
# the the Boston-1990-2001-crime+-spot-check = the the proof!
for r in out:
    if r['city'] == 'Boston' and r['year'] in (1990, 1995, 2001, 1999):
        print(' Boston', r['year'], '| rate', r['rate'], '| CRIME+', r['crime_plus'])
    if r['city'] == 'New Orleans' and r['year'] in (1990, 2011, 2019, 2022):
        print(' NO', r['year'], '| rate', r['rate'], '| CRIME+', r['crime_plus'], '| CARE+', r['care_plus'])
