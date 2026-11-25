import json
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
rows = [json.loads(l) for l in open(B + 'crime_series_wave1.jsonl', encoding='utf-8') if l.strip()]
d = json.load(open(B + 'nyc_dcjs_index.json', encoding='utf-8'))
fixed = 0
for r in rows:
    if 'new york' in str(r.get('city','')).lower() or 'NYC' in str(r.get('city','')):
        y = str(r.get('year'))
        if y in d and r.get('murders') is None:
            r['murders'] = d[y]['murder']
            r['violent_crime_total'] = d[y]['violent']
            fixed += 1
open(B + 'crime_series_wave1.jsonl', 'w', encoding='utf-8', newline='').write(chr(10).join(json.dumps(r) for r in rows) + chr(10))
print('NYC-murders-FIXED:', fixed)
# the the v6c = the the re-inject = the the same-fix!
merged = json.load(open(B + 'triple_slider_v6c.json', encoding='utf-8'))
# the NYC-populations = the the 1998-2001 = the the ~7.4M-anchored:
nyc_pop = {1998: 7423978, 1999: 7454757, 2000: 7475250, 2001: 7499958, 2019: 8370000, 2020: 8882000, 2021: 8797000, 2022: 8836000, 2023: 8891000, 2024: 8910000}
count2 = 0
field_all = defaultdict(list)
import re
from collections import defaultdict
# rebuild the field-median-from-the-merged:
allrates = {(r['city'], r['year']): r.get('rate') for r in merged if r.get('rate')}
for r in merged:
    if r['city'] == 'NYC':
        y = int(r['year'])
        if y in d and r.get('murders') is None:
            r['murders'] = d[y]['murder']
        if r.get('population') is None and y in nyc_pop:
            r['population'] = nyc_pop[y]
        if r.get('murders') and r.get('population'):
            r['rate'] = round(r['murders']/r['population']*100000, 2)
            count2 += 1
# the field = the recompute = the the ALL-rates:
rates_all = {}
for r in merged:
    if r.get('rate'):
        rates_all[(r['city'], r['year'])] = r['rate']
field_y = defaultdict(list)
for (c, y), v in rates_all.items():
    if str(y) != '2026':
        field_y[y].append(v)
meds = {y: sorted(v)[len(v)//2] for y, v in field_y.items() if len(v) >= 2}
for r in merged:
    if r['city'] == 'NYC' and r.get('rate'):
        y = int(r['year'])
        if y in meds:
            r['crime_plus'] = round(r['rate']/meds[y]*100, 1)
json.dump(merged, open(B + 'triple_slider_v6d.json', 'w', encoding='utf-8'), indent=1)
print('NYC-merged-fixed:', count2)
for r in merged:
    if r['city'] == 'NYC':
        print(f" NYC {r['year']}: murders {r.get('murders')} | rate {r.get('rate')} | CRIME+ {r.get('crime_plus')} | care {r.get('care_ratio')}")
