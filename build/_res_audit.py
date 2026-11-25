import json
rows = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/triple_slider_v5.json', encoding='utf-8'))
from collections import Counter
pats = Counter(); details = {}
for r in sorted(rows, key=lambda x: (x['city'], x['year'])):
    cp = r.get('crime_plus'); carep = r.get('care_plus'); ep = r.get('edu_plus')
    tag = ('C' if cp else '-') + (str('A') if carep else '-') + ('E' if ep else '-')
    pats[tag] += 1
    details.setdefault(tag, []).append((r['city'], r['year']))
print('THE REMAINING-PATTERNS:', dict(pats))
print()
for k in ('-A-','C--','---','--E','C-E','-AE','CA-','CAE'):
    ks = details.get(k, [])
    print(f'{k} ({len(ks)}):', ks[:14])
