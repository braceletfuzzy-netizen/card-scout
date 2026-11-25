import json
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
# the the wide-b-care = the per-city = the care_2012-care_2014 (the wide-b = the the different-schema!):
rows = [json.loads(l) for l in open(B + 'care_cage_wide_b.jsonl', encoding='utf-8') if l.strip()]
print('the wide-b-sample:', {k: rows[0][k] for k in ('city', 'care_2012', 'cage_2012', 'care_2014', 'cage_2014') if k in rows[0]})
# the officers = the participated-pop?
r2 = json.loads(open(B + 'officers_wide.jsonl', encoding='utf-8').readline())
print('the officers-sample:', {k: r2[k] for k in ('city', 'year', 'total_officers') if k in r2})
