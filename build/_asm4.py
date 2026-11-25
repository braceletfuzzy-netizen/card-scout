import json
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
rows = [json.loads(l) for l in open(B + 'socioeconomic_series_v1.jsonl', encoding='utf-8') if l.strip()]
# THE the merge = the New-York-into-NYC + the Boston-5 = the check (the Boston-5-cities = the the acs-only = the FRED-MA = the Suffolk-was-not-in-the-list = the the Boston-FRED-missing = the honest-noted!):
merged = []
bykey = {}
for r in rows:
    c = r['city']
    if c == 'New York':
        c = 'NYC'
    r['city'] = c
    k = (c, r['year'])
    if k in bykey:
        # merge = the fill-the-nulls:
        ex = bykey[k]
        for f in ('poverty_rate','children_poverty_pct','median_income','bachelors_pct','unemployment_rate','population'):
            if ex.get(f) is None and r.get(f) is not None:
                ex[f] = r[f]
    else:
        bykey[k] = r
        merged.append(r)
merged.sort(key=lambda x: (x['city'], x['year']))
open(B + 'socioeconomic_series_v1.jsonl', 'w', encoding='utf-8', newline='').write(chr(10).join(json.dumps(r) for r in merged) + chr(10))
from collections import Counter
print('rows-after:', len(merged))
print('per-city:', dict(Counter(r['city'] for r in merged)))
# the spot = the NYC:
for r in merged:
    if r['city'] == 'NYC' and r['year'] in (2000, 2011, 2023):
        print('NYC', r['year'], '| unemp', r.get('unemployment_rate'), '| poverty', r.get('poverty_rate'), '| med-income', r.get('median_income'))
