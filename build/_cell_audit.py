import json
rows = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/triple_slider_v4.json', encoding='utf-8'))
# THE THE-CELL-BY-CELL = the the every-row:
print('THE THE-CELL-AUDIT (the the rows = the the dash-cells = the the what-the-founder-sees!):')
print()
from collections import Counter
patterns = Counter()
cell_rows = []
for r in sorted(rows, key=lambda x: (x['city'], x['year'])):
    cp = r.get('crime_plus'); carep = r.get('care_plus'); ep = r.get('edu_plus')
    tag = ('C' if cp else '-') + ('A' if carep else '-') + ('E' if ep else '-')
    patterns[tag] += 1
    if tag in ('---', '--E', 'C--', 'CA-', '-A-', 'C-E', '--E'):
        cell_rows.append((r['city'], r['year'], tag, r.get('murders'), r.get('rate')))
print('the patterns:', dict(patterns))
print()
print('the weak-rows (the the visible-dashes = the what-on-the-board!):', len(cell_rows))
for c in cell_rows[:40]:
    print(' *', c)
