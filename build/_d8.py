import json, re
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
# the replicate = the the rerun2-care = the print-the-keys-per-city:
care = {}
for f in ('care_cage_wide.jsonl', 'care_cage_wide_b.jsonl'):
    for l in open(B + f, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        era = str(r.get('era_or_year') or r.get('era') or r.get('year') or '')
        y = None
        m = re.search(r'((19|20)\d\d)', era)
        if m: y = int(m.group(0))
        if not y or y < 1992: continue
        cu = r.get('care_usd_total'); ga = r.get('cage_usd_total')
        if not (cu and ga): continue
        cc = (r.get('city') or '').strip()
        if not cc: continue
        c_key = cc.replace('St. Louis', 'STLOUIS')
        care[(c_key, y)] = round(cu/ga, 3)
# the print = the per-city:
from collections import defaultdict
byc = defaultdict(list)
for (c, y) in care:
    byc[c].append(y)
for c, ys in sorted(byc.items()):
    print(c, ys)
print('total-keys:', len(care))
