import json, statistics, math
from collections import defaultdict
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

def norm(c):
    c = (c or '').strip()
    c = {'New York City': 'NYC', 'New York': 'NYC'}.get(c, c)
    if 'balance' in c.lower() and 'indianapolis' in c.lower(): return 'Indianapolis'
    return c

# POPS (the wide + the original-inherit!):
pops = {}
for l in open(B + 'populations_wide_v1.jsonl', encoding='utf-8'):
    if l.strip():
        r = json.loads(l)
        pops[(norm(r.get('city')), int(r['year']))] = r['population']

care = {}
# THE WIDE-B-1st = the the care_2012-2014-fields:
for l in open(B + 'care_cage_wide_b.jsonl', encoding='utf-8'):
    if not l.strip(): continue
    r = json.loads(l)
    c = norm(r.get('city'))
    if r.get('care_2012') and r.get('cage_2012'):
        care[(c, 2012)] = round(r['care_2012']/r['cage_2012'], 3)
    if r.get('care_2014') and r.get('cage_2014'):
        care[(c, 2014)] = round(r['care_2014']/r['cage_2014'], 3)
# THE WIDE-A = the year-field:
for l in open(B + 'care_cage_wide.jsonl', encoding='utf-8'):
    if not l.strip(): continue
    r = json.loads(l)
    if r.get('year') is None: continue
    c = norm(r.get('city'))
    if r.get('care_usd_total') and r.get('cage_usd_total'):
        y = int(r['year'])
        care[(c, y)] = round(r['care_usd_total']/r['cage_usd_total'], 3)
print('care-keys:', len(care))

murders = {}
for k, m in json.load(open(B + 'murders_all_v1.json', encoding='utf-8')).items():
    c, y = k.split('|')
    cc = {'New York City': 'NYC'}.get(c, c)
    murders[(cc, int(y))] = m

pairs = []
for (c, y), cu in care.items():
    m = murders.get((c, y))
    my = y
    if m is None:
        m = murders.get((c, y+1)); my = y+1
    if m is None:
        m = murders.get((c, y-1)); my = y-1
    if m is None: continue
    p = pops.get((c, my)) or pops.get((c, y))
    if not p or p < 100000: continue
    pairs.append({'city': c.title(), 'care_year': y, 'crime_year': my, 'care_ratio': cu, 'murders': m, 'population': p, 'rate': round(m/p*100000, 2)})
print('PAIRS:', len(pairs))
def corr(x, yv):
    mx, my = statistics.mean(x), statistics.mean(yv)
    num = sum((a-mx)*(b-my) for a, b in zip(x, yv))
    den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in yv)) ** 0.5
    return round(num/den, 3) if den else None
lp = [(math.log(p['care_ratio']), math.log(p['rate'])) for p in pairs if p['care_ratio'] > 0]
print(f'LOG-CARE-vs-LOG-RATE: r = {corr([a for a, b in lp], [b for a, b in lp])} (n={len(lp)})')
raw = corr([p['care_ratio'] for p in pairs], [p['rate'] for p in pairs])
print(f'RAW: r = {raw} (n={len(pairs)})')
cs = sorted(p['care_ratio'] for p in pairs)
med = cs[len(cs)//2]
low = [p['rate'] for p in pairs if p['care_ratio'] <= med]
high = [p['rate'] for p in pairs if p['care_ratio'] > med]
print(f'SPLIT: below {round(statistics.mean(low),1)} (n={len(low)}) vs above {round(statistics.mean(high),1)} (n={len(high)})')
# THE the within- = the same-city-diff-vintage = the the 2012-14-care-change-vs-rate-change = the 15-pairs-classes!
print()
print('THE WITHIN-CITY (the 2012-14-care-change = the the 2-vintage-delta!):')
w = []
for c in set(p['city'] for p in pairs):
    c12 = next((p for p in pairs if p['city'] == c and p['care_year'] == 2012), None)
    c14 = next((p for p in pairs if p['city'] == c and p['care_year'] == 2014), None)
    if c12 and c14:
        d_care = c14['care_ratio'] - c12['care_ratio']
        d_rate = c14['rate'] - c12['rate']
        w.append((c, c12['care_ratio'], c14['care_ratio'], c12['rate'], c14['rate'], round(d_care, 2), round(d_rate, 1)))
for x in w:
    print(f'  {x[0]}: care {x[1]}->{x[2]} (d{x[5]}) | rate {x[3]}->{x[4]} (d{x[6]})')
if len(w) >= 5:
    print(f'  d-care-vs-d-rate: r = {corr([x[5] for x in w], [x[6] for x in w])} (n={len(w)})')
json.dump(pairs, open(B + 'wide_panel_pairs_v3.json', 'w', encoding='utf-8'), indent=1)
print('WROTE wide_panel_pairs_v3.json | cities:', len(set(p['city'] for p in pairs)))
