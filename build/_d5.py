import json
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
cs = sorted(set(json.loads(l).get('city') for l in open(B + 'crime_wide.jsonl', encoding='utf-8') if l.strip()))
print('the crime_wide-cities:', cs)
cs2 = sorted(set(json.loads(l).get('city') for l in open(B + 'crime_wide_b.jsonl', encoding='utf-8') if l.strip()))
print('the crime_wide_b-cities:', cs2)
