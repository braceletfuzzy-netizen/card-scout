import json
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
rows = [json.loads(l) for l in open(B + 'care_cage_wide_b.jsonl', encoding='utf-8') if l.strip()]
print('the b-count:', len(rows))
print('the b-keys-of-tx:', [k for k in rows[0].keys() if 'care' in k or 'cage' in k])
# the care-values = the per-row:
for r in rows[:3]:
    print(' ', r.get('city'), '| care_2012:', r.get('care_2012'), '| cage_2012:', r.get('cage_2012'), '| care_2014:', r.get('care_2014'))
