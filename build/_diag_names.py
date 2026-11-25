import json
# DIAG the remaining-gaps = the city-names-normalize-mismatch!:
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
crime = []
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl'):
    for l in open(B + f, encoding='utf-8'):
        if l.strip():
            r = json.loads(l)
            crime.append(r.get('city'))
print('crime-cities-as-written:', sorted(set(crime)))
care = json.load(open(B + 'crime_plus_care_plus_v2.json', encoding='utf-8'))
print('care-cities:', sorted(set(r.get('city') for r in care)))
edu = [json.loads(l) for l in open(B + 'edu_series_v1.jsonl', encoding='utf-8') if l.strip()]
print('edu-cities:', sorted(set(r.get('city') for r in edu)))
