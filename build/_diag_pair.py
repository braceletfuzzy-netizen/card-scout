import json, re
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
# the care-keys = the sample:
care_cities = set()
for l in open(B + 'care_cage_wide.jsonl', encoding='utf-8'):
    if l.strip():
        r = json.loads(l)
        care_cities.add((r.get('city'), r.get('era_or_year') or r.get('year'), list(r.keys())[:8]))
print('the wide-care-sample:', list(care_cities)[:3])
murders = json.load(open(B + 'murders_all_v1.json', encoding='utf-8'))
m_cities = sorted(set(k.split('|')[0] for k in murders))
print('the murders-cities:', m_cities[:18])
