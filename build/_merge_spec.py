import json, re
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
rows = json.load(open(B + 'triple_slider_v6.json', encoding='utf-8'))
# THE the inject = the the STL-specifics + the the wave2 = the the rebuild!
wave2 = [json.loads(l) for l in open(B + 'crime_series_wave2_holefill.jsonl', encoding='utf-8') if l.strip()]
# the the new = the murders:
murders6 = {(r['city'].lower(), r['year']): r.get('murders') for r in rows}
pops6 = {(r['city'].lower(), r['year']): r.get('population') for r in rows}
for r in wave2:
    c = (r.get('city') or '').lower().replace('st. louis','st louis').replace('st louis','st louis')
    y = None
    m = re.search(r'((19|20)\d\d)', str(r.get('year') or r.get('era_or_year') or ''))
    if m: y = int(m.group(1))
    if mv := r.get('murders'):
        murders6[(c, y)] = mv
    if pv := r.get('population'):
        pops6.setdefault((c, y), pv)
# the rates-again = the from-the-file = the the care-rows-stay:
def get_rate(city, y):
    for r in rows:
        if r['city'].lower() == city and r['year'] == y:
            return r
    return None
# THE the field-median-again (the from-the-murders+pop!):
from collections import defaultdict
rates = {}
for k, m in murders6.items():
    p = pops6.get(k)
    if m and p:
        rates[k] = round(m/p*100000, 1)
field = defaultdict(list)
for (c, y), rate in rates.items():
    if str(y) != '2026':
        field[y].append(rate)
meds = {y: sorted(v)[len(v)//2] for y, v in field.items() if len(v) >= 2}
for r in rows:
    c = r['city'].lower().replace('st. louis', 'st louis').replace('st louis','st louis')
    k = (c, r['year'])
    m = murders6.get(k); p = pops6.get(k)
    if m and p and r.get('murders') is None:
        r['murders'] = m; r['population'] = p
        r['rate'] = round(m/p*100000, 1)
        y = r['year']
        if str(y) != '2026' and y in meds:
            r['crime_plus'] = round(r['rate']/meds[y]*100, 1)
json.dump(rows, open(B + 'triple_slider_v6b.json', 'w', encoding='utf-8'), indent=1)
# the STL = the the print:
for r in rows:
    if 'st louis' == r['city'].lower() and r['year'] in (2002, 2016, 2017, 2018, 2019):
        print('STL', r['year'], '| murders', r.get('murders'), '| CRIME+', r.get('crime_plus'))
print('rows:', len(rows))
