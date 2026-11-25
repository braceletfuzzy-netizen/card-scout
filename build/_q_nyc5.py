import json
for l in open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/crime_series_wave1.jsonl', encoding='utf-8'):
    if l.strip():
        r = json.loads(l)
        if 'New York City' in str(r.get('city','')):
            print(' wave1:', r.get('city'), r.get('year'), '| murders', r.get('murders'), '| pop', r.get('population'))
