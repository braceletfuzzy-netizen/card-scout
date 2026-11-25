import json, re
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
years = {}
for f in ('care_cage_wide.jsonl', 'care_cage_wide_b.jsonl'):
    for l in open(B + f, encoding='utf-8'):
        if l.strip():
            r = json.loads(l)
            if r.get('city'):
                years.setdefault(r['city'], []).append(r.get('year'))
for c, ys in list(years.items())[:8]:
    print(c, ys)
