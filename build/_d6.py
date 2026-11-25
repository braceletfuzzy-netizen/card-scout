import json, re
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
count = 0
for l in open(B + 'care_cage_wide.jsonl', encoding='utf-8'):
    if not l.strip(): continue
    r = json.loads(l)
    y = r.get('year')
    cu = r.get('care_usd_total'); ga = r.get('cage_usd_total')
    m = re.search(r'((19|20)\d\d)', str(r.get('year') or ''))
    if m: y2 = int(m.group(0))
    print(cu, ga, y, '->', y2, '| the both-ok:', bool(cu and ga))
    count += 1
    if count >= 4: break
