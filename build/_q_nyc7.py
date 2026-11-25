import json
rows = [json.loads(l) for l in open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/crime_series_wave1.jsonl', encoding='utf-8') if l.strip()]
nyc = [(r.get('year'), r.get('murders')) for r in rows if 'new york' in str(r.get('city','')).lower()]
print('NYC-rows-in-file:', sorted(nyc))
# AND the nyc_dcjs_index.json = the the still = the the values?
import os
p = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/nyc_dcjs_index.json'
print('exists:', os.path.exists(p))
if os.path.exists(p):
    d = json.load(open(p, encoding='utf-8'))
    for k in d:
        print(' dcjs:', k, '->', d[k])
