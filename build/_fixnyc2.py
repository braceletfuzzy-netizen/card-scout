import json
from collections import defaultdict
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
merged = json.load(open(B + 'triple_slider_v6c.json', encoding='utf-8'))
d = json.load(open(B + 'nyc_dcjs_index.json', encoding='utf-8'))
nyc_pop = {1998: 7423978, 1999: 7454757, 2000: 7475250, 2001: 7499958, 2019: 8370000, 2020: 8882000, 2021: 8797000, 2022: 8836000, 2023: 8891000, 2024: 8910000}
count2 = 0
for r in merged:
    if r['city'] == 'NYC':
        y = int(r['year'])
        if str(y) in d and r.get('murders') is None:
            r['murders'] = d[str(y)]['murder']
        if r.get('population') is None and y in nyc_pop:
            r['population'] = nyc_pop[y]
        if r.get('murders') and r.get('population'):
            r['rate'] = round(r['murders']/r['population']*100000, 2)
            count2 += 1
rates_all = {(r['city'], r['year']): r.get('rate') for r in merged if r.get('rate')}
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
print('NYC-fixed:', count2)
for r in merged:
    if r['city'] == 'NYC':
        print(f" NYC {r['year']}: rate {r.get('rate')} | CRIME+ {r.get('crime_plus')} | care {r.get('care_ratio')}")
