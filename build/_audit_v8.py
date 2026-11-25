import json
rows = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/triple_slider_v3.json', encoding='utf-8'))
# THE THE-AUDIT-BY-ROW = the which-rows = the what-blank:
blanks = []
for r in sorted(rows, key=lambda x: (x['city'], x['year'])):
    missing = []
    if r.get('murders') is None: missing.append('crime')
    if r.get('care_plus') is None: missing.append('care')
    if r.get('edu_plus') is None: missing.append('edu')
    if missing:
        blanks.append((r['city'], r['year'], '+'.join(missing), 'partial' if r.get('partial_flag') else 'no-crime-or-care'))
print('the blank-rows = the total:', len(blanks), 'of', len(rows))
from collections import Counter
c = Counter((b[2], b[3]) for b in blanks)
for k, v in c.most_common():
    print(f' {k}: {v}')
print()
for b in blanks[:30]:
    print(' *', b)
