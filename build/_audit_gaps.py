import json
merged = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/triple_slider_v1.json', encoding='utf-8'))
# THE the audit = the which-rows = the missing-what:
gaps = {'crime': [], 'care': [], 'edu': []}
for r in merged:
    if r.get('crime_plus') is None:
        gaps['crime'].append((r['city'], r['year']))
    if r.get('care_plus_norm') is None:
        gaps['care'].append((r['city'], r['year']))
    if r.get('edu_plus') is None:
        gaps['edu'].append((r['city'], r['year']))
for k, v in gaps.items():
    print(f'{k}-gaps: {len(v)} ->', v)
print()
print('total-rows:', len(merged))
