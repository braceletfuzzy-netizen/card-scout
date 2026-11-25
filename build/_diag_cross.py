import json
# DIAG-4 = the the care-lane-years-vs-the-crime-years = the the exact-cross-check-per-city:
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
import re
def ny(s):
    m = re.search(r'((19|20)\d\d)', str(s))
    return int(m.group(1)) if m else None
# care:
care_keys = set()
for r in json.load(open(B + 'crime_plus_care_plus_v2.json', encoding='utf-8')):
    c = r.get('city'); y = ny(r.get('year'))
    if r.get('care_cage_ratio') is not None and y:
        care_keys.add((c, y))
# crime:
crime_keys = set()
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl'):
    for l in open(B + f, encoding='utf-8'):
        if l.strip():
            r = json.loads(l)
            c = r.get('city'); y = ny(r.get('year'))
            if r.get('murders') is not None and y:
                crime_keys.add((c, y))
print('care-keys:', sorted(care_keys))
print()
print('crime-keys:', sorted(crime_keys))
print()
print('in-care-not-crime:', sorted(care_keys - crime_keys))
print('in-crime-not-care:', sorted(crime_keys - care_keys))
