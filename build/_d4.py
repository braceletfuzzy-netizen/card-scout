import json
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
for f in ('care_cage_wide.jsonl', 'care_cage_wide_b.jsonl'):
    cs = sorted(set(json.loads(l).get('city') for l in open(B + f, encoding='utf-8') if l.strip()))
    print(f, cs)
