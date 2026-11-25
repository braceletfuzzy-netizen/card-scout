import json
from collections import defaultdict
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
rows = json.load(open(B + 'triple_slider_v6b.json', encoding='utf-8'))
# THE rates-pool:
rates = {(r['city'].lower(), r['year']): r.get('rate') for r in rows if r.get('rate')}
# THE windows = the the solo-rows-with-rate-but-no-crime+:
count = 0
for r in rows:
    if r.get('rate') and r.get('crime_plus') is None and str(r['year']) != '2026':
        y = r['year']; c = r['city'].lower()
        pool = [v for (cc, yy), v in rates.items() if abs(yy - y) <= 2 and cc != c and v]
        pool_all = [v for (cc, yy), v in rates.items() if abs(yy - y) <= 2 and v]
        if len(pool_all) >= 3:
            med = sorted(pool_all)[len(pool_all)//2]
            r['crime_plus'] = round(r['rate']/med*100, 1)
            r['window_normalized'] = f'±2yr-window pool n={len(pool_all)}'
            count += 1
json.dump(rows, open(B + 'triple_slider_v6c.json', 'w', encoding='utf-8'), indent=1)
print('window-filled:', count)
for r in rows:
    if 'louis' in r['city'].lower() and r['year'] in (2002, 2016, 2017, 2018):
        print('STL', r['year'], '| CRIME+', r.get('crime_plus'))
