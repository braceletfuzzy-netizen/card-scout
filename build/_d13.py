import json, re
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
def norm(c):
    c = (c or '').strip()
    c = {'New York City': 'NYC', 'New York': 'NYC'}.get(c, c)
    return c
count = 0
for l in open(B + 'care_cage_wide_b.jsonl', encoding='utf-8'):
    if not l.strip(): continue
    r = json.loads(l)
    if r.get('care_2012') and r.get('cage_2012'):
        print(' WOULD-FILL:', norm(r.get('city')), 2012)
        count += 1
print('the b-fillable:', count)
