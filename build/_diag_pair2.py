import json
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
row = json.loads(open(B + 'care_cage_wide.jsonl', encoding='utf-8').readline())
print('the wide-care-row-keys:', list(row.keys()))
print('the row:', row)
