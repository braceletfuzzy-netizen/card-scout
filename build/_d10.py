import json
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
r = json.loads(open(B + 'acs_wide.jsonl', encoding='utf-8').readline())
print('the acs-keys:', list(r.keys()))
r2 = json.loads(open(B + 'officers_wide.jsonl', encoding='utf-8').readline())
print('the officers-keys:', list(r2.keys()))
r3 = json.loads(open(B + 'care_cage_wide_b.jsonl', encoding='utf-8').readline())
print('the wide-b-care-keys:', list(r3.keys())[:10])
