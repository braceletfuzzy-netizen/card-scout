import json, statistics
from collections import defaultdict

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
rows = json.load(open(B + 'triple_slider_v6d.json', encoding='utf-8'))
edu = json.load(open(B + 'edu_plus_v2_computed.json', encoding='utf-8'))

def ny(y):
    import re
    m = re.search(r'((19|20)\d\d)', str(y))
    return int(m.group(1)) if m else None

# the EDU+-index = the city-year:
edu_idx = {}
for r in edu:
    c = (r.get('city') or '').lower(); y = ny(r.get('year'))
    if r.get('edu_plus') is not None:
        edu_idx[(c, y)] = r.get('edu_plus')

# THE merged = the care+crime+edu = the triple-panel!
tri = []
for r in rows:
    c = (r['city'] or '').lower(); y = ny(r['year'])
    ep = edu_idx.get((c, y))
    if r.get('care_ratio') is not None and r.get('crime_plus') is not None and ep is not None:
        # the care-plus = the normalized-care = the care_ratio*100 = the the convention!
        tri.append({'city': r['city'], 'year': y, 'care': r['care_ratio']*100, 'crime': r['crime_plus'], 'edu': ep})

print(f'=== THE PHASE-2b = THE THREE-SLIDER-COMPOSITE [panel n={len(tri)}] ===')
for t in tri:
    print(f" {t['city']:12s} {t['year']}: care {t['care']:.1f} | edu {t['edu']:.1f} | crime {t['crime']:.1f}")
print()

def corr(x, y):
    mx, my = statistics.mean(x), statistics.mean(y)
    num = sum((a-mx)*(b-my) for a, b in zip(x, y))
    den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in y)) ** 0.5
    return round(num/den, 3) if den else None

x1 = [t['care'] for t in tri]; x2 = [t['edu'] for t in tri]; yv = [t['crime'] for t in tri]
print('THE PAIRED-CORRELATIONS:')
print(f'  care-vs-crime:  r = {corr(x1, yv)}')
print(f'  edu-vs-crime:   r = {corr(x2, yv)}')
print(f'  care-vs-edu:    r = {corr(x1, x2)} (the pie-constraint test!)')
# THE THE-2-SLIDER-COMPOSITE = the simple-avg = the (care+edu)/2 = the vs-crime:
comp2 = [(a+b)/2 for a, b in zip(x1, x2)]
print(f'  composite-(care+edu)/2-vs-crime: r = {corr(comp2, yv)}')
json.dump(tri, open(B + 'phase2b_panel.json', 'w', encoding='utf-8'), indent=1)
print('WROTE phase2b_panel.json')
