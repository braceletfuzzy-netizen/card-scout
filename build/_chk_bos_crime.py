import json, re
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl'):
    for l in open(B + f, encoding='utf-8'):
        if l.strip():
            r = json.loads(l)
            if r.get('city') == 'Boston':
                print(f, '->', r.get('city'), r.get('year'), '| murders:', r.get('murders'), '| pop:', r.get('population'))
