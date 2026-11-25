import json, re, statistics
from collections import defaultdict
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

# THE care = the the simplified-single-source-union:
care = {}
for f in ('care_arc_extension_v1.jsonl', 'care_arc_extension_v2.jsonl', 'care_cage_wide.jsonl', 'care_cage_wide_b.jsonl', 'nola_houston_pair_v1.jsonl',
          'boston_care_cage_series_v1.jsonl', 'neworleans_care_cage_series_v1.jsonl', 'stlouis_care_cage_series_v1.jsonl',
          'cincinnati_care_cage_series_v1.jsonl', 'memphis_care_cage_series_v1.jsonl', 'detroit_care_cage_series_v1.jsonl',
          'okc_care_cage_series_v1.jsonl', 'nyc_care_cage_series_v1.jsonl'):
    try:
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
            c_key = {'New York City': 'NYC', 'New York': 'NYC'}.get(cc, cc.replace('St. Louis', 'STLOUIS').replace('St Louis', 'STLOUIS'))
            care[(c_key, y)] = round(cu/ga, 3)
    except FileNotFoundError:
        pass
print('care-keys:', len(care), '| cities:', len(set(c for c, y in care)))

# THE the murders-idx = the already = the:
murders_idx = {}
for k, m in json.load(open(B + 'murders_all_v1.json', encoding='utf-8')).items():
    c, y = k.split('|')
    c_key = {'NYC': 'NYC'}.get(c, c.replace('St. Louis', 'STLOUIS').replace('St Louis', 'STLOUIS'))
    murders_idx[(c_key, int(y))] = m
print('murders-keys:', len(murders_idx))

# THE pops = the merge:
pops = {}
for f in ('population_series_v1.jsonl', 'nola_houston_pair_v1.jsonl', 'socioeconomic_series_v1.jsonl', 'policy_series_v1.jsonl', 'acs_wide.jsonl', 'acs_wide_b.jsonl', 'officers_wide.jsonl', 'officers_wide_b.jsonl'):
    try:
        for l in open(B + f, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l)
            cc = (r.get('city') or '').strip()
            if not cc: continue
            y = None
            m2 = re.search(r'((19|20)\d\d)', str(r.get('year') or r.get('era') or ''))
            if m2: y = int(m2.group(0))
            pv = r.get('population')
            if y and pv:
                c_key = {'New York City': 'NYC', 'New York': 'NYC'}.get(cc, cc.replace('St. Louis', 'STLOUIS').replace('St Louis', 'STLOUIS'))
                pops.setdefault((c_key, y), pv)
    except FileNotFoundError:
        pass
print('pops:', len(pops))

# THE the pairs = the care-year = the the nearest-crime-year (the the ±1 = the the same-budget-year-class!):
pairs = []
for (c, y), cu in care.items():
    m = murders_idx.get((c, y)) or murders_idx.get((c, y+1)) or murders_idx.get((c, y-1))
    my = y if murders_idx.get((c, y)) else (y+1 if murders_idx.get((c, y+1)) else (y-1 if murders_idx.get((c, y-1)) else None))
    if m is None: continue
    p = pops.get((c, my)) or pops.get((c, y))
    if not p: continue
    if p < 50000: continue
    rate = round(m/p*100000, 1)
    pairs.append({'city': c, 'care_year': y, 'crime_year': my, 'care_ratio': cu, 'murders': m, 'rate': rate})
print('PAIRS:', len(pairs))
# THE the normalize:
cfield = defaultdict(list); kfield = defaultdict(list)
for p_ in pairs:
    cfield[p_['care_year']].append(p_['care_ratio']); kfield[p_['crime_year']].append(p_['rate'])
cmeds = {y: sorted(v)[len(v)//2] for y, v in cfield.items() if len(v) >= 3}
kmeds = {y: sorted(v)[len(v)//2] for y, v in kfield.items() if len(v) >= 3}
for p_ in pairs:
    if p_['care_year'] in cmeds:
        p_['care_plus'] = round(p_['care_ratio']/cmeds[p_['care_year']]*100, 1)
    if p_['crime_year'] in kmeds:
        p_['crime_plus'] = round(p_['rate']/kmeds[p_['crime_year']]*100, 1)
both = [p_ for p_ in pairs if p_.get('care_plus') and p_.get('crime_plus')]
print('the both-pairs:', len(both))
def corr(x, yv):
    mx, my = statistics.mean(x), statistics.mean(yv)
    num = sum((a-mx)*(b-my) for a, b in zip(x, yv))
    den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in yv)) ** 0.5
    return round(num/den, 3) if den else None
print(f'CARE+ vs CRIME+ (the wide-panel): r = {corr([p_["care_plus"] for p_ in both], [p_["crime_plus"] for p_ in both])} (n={len(both)})')
cs = sorted(p_['care_plus'] for p_ in both)
med = cs[len(cs)//2]
low = [p_['crime_plus'] for p_ in both if p_['care_plus'] <= med]
high = [p_['crime_plus'] for p_ in both if p_['care_plus'] > med]
print(f'THE BROKEN-STICK: below {round(statistics.mean(low),1)} (n={len(low)}) vs above {round(statistics.mean(high),1)} (n={len(high)})')
json.dump(both, open(B + 'wide_panel_pairs_v1.json', 'w', encoding='utf-8'), indent=1)
print('WROTE wide_panel_pairs_v1.json')
# the the cities-count:
print('the cities-in-panel:', len(set(p_['city'] for p_ in both)))
