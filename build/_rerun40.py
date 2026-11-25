import json, re, statistics
from collections import defaultdict
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

def norm(c):
    c = (c or '').strip()
    if c in ('NYC', 'New York City', 'New York'): return 'NYC'
    c = c.replace('St. Louis', 'STLOUIS').replace('St Louis', 'STLOUIS')
    return c

def title(c):
    c = norm(c)
    return {'STLOUIS': 'St. Louis', 'NYC': 'NYC'}.get(c, c.title() if c not in ('STLOUIS',) else 'St. Louis')

# THE care = the all-sources = the the canonical:
care = {}
for f in ('boston_care_cage_series_v1.jsonl', 'neworleans_care_cage_series_v1.jsonl', 'stlouis_care_cage_series_v1.jsonl',
          'cincinnati_care_cage_series_v1.jsonl', 'memphis_care_cage_series_v1.jsonl', 'detroit_care_cage_series_v1.jsonl',
          'okc_care_cage_series_v1.jsonl', 'nyc_care_cage_series_v1.jsonl', 'care_arc_extension_v1.jsonl',
          'care_arc_extension_v2.jsonl', 'care_cage_wide.jsonl', 'care_cage_wide_b.jsonl', 'nola_houston_pair_v1.jsonl'):
    try:
        for l in open(B + f, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l)
            era = str(r.get('era_or_year') or r.get('era') or r.get('year') or '')
            cc = r.get('city')
            cu = r.get('care_usd_total'); ga = r.get('cage_usd_total')
            y = None
            m = re.search(r'((19|20)\d\d)', era)
            if m: y = int(m.group(0))
            if cu and ga and y and y > 1970:
                if cc:
                    c_key = cc.strip().replace('St. Louis', 'STLOUIS').replace('St Louis', 'STLOUIS')
                    care[(c_key, y)] = round(cu/ga, 3)
                # the wide = the census-parser-rows = the the city-in-the-other-key:
                for k in ('city', 'city_name', 'name'):
                    if r.get(k):
                        c2 = str(r[k]).strip().replace('St. Louis', 'STLOUIS')
                        care[(c2, y)] = round(cu/ga, 3)
                        break
    except FileNotFoundError:
        pass

# THE murders = the all:
murders = json.load(open(B + 'murders_all_v1.json', encoding='utf-8'))
murders_idx = {}
for k, m in murders.items():
    c, y = k.split('|')
    murders_idx[(c.replace('St. Louis', 'STLOUIS'), int(y))] = m

# THE the pops = the the merge = the the all (the rough = the the pairs + the series + the acs-rows-with-pop):
pops = {}
for f in ('population_series_v1.jsonl', 'nola_houston_pair_v1.jsonl', 'socioeconomic_series_v1.jsonl', 'policy_series_v1.jsonl', 'acs_wide.jsonl', 'acs_wide_b.jsonl'):
    try:
        for l in open(B + f, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l)
            cc = (r.get('city') or '').strip()
            y = None
            m2 = re.search(r'((19|20)\d\d)', str(r.get('year') or r.get('era') or ''))
            if m2: y = int(m2.group(0))
            pv = r.get('population')
            if cc and y and pv:
                c_key = cc.replace('New York City', 'NYC').replace('New York', 'NYC').replace('St. Louis', 'STLOUIS').replace('St Louis', 'STLOUIS')
                if (c_key, y) not in pops:
                    pops[(c_key, y)] = pv
    except FileNotFoundError:
        pass
print('pops:', len(pops))

# THE the pairs = the care-x-crime = the both + the the rate = the pop:
pairs = []
for (c, y), cu in care.items():
    if y < 2011 or y > 2025: continue
    m = murders_idx.get((c, y))
    if m is None: continue
    p = pops.get((c, y))
    if not p: continue
    rate = round(m/p*100000, 1)
    pairs.append({'city': c, 'year': y, 'care_ratio': cu, 'murders': m, 'rate': rate})

# THE CRIME+ = the pooled-median-per-year!
field = defaultdict(list)
for p_ in pairs: field[p_['year']].append(p_['rate'])
meds = {y: sorted(v)[len(v)//2] for y, v in field.items() if len(v) >= 3}
for p_ in pairs:
    if p_['year'] in meds:
        p_['crime_plus'] = round(p_['rate']/meds[p_['year']]*100, 1)
# THE care+ = the the care-normalized-per-year:
cfield = defaultdict(list)
for p_ in pairs: cfield[p_['year']].append(p_['care_ratio'])
cmeds = {y: sorted(v)[len(v)//2] for y, v in cfield.items() if len(v) >= 3}
for p_ in pairs:
    if p_['year'] in cmeds:
        p_['care_plus'] = round(p_['care_ratio']/cmeds[p_['year']]*100, 1)

pairs = [p_ for p_ in pairs if p_.get('crime_plus') and p_.get('care_plus')]
json.dump(pairs, open(B + 'wide_panel_pairs_v1.json', 'w', encoding='utf-8'), indent=1)
print('THE PAIRS:', len(pairs))
def corr(x, yv):
    mx, my = statistics.mean(x), statistics.mean(yv)
    num = sum((a-mx)*(b-my) for a, b in zip(x, yv))
    den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in yv)) ** 0.5
    return round(num/den, 3) if den else None
print(f'CARE+-vs-CRIME+ (the 40-city): r = {corr([p_["care_plus"] for p_ in pairs], [p_["crime_plus"] for p_ in pairs])} (n={len(pairs)})')
cs = sorted(p_['care_plus'] for p_ in pairs)
med_c = cs[len(cs)//2]
low = [p_['crime_plus'] for p_ in pairs if p_['care_plus'] <= med_c]
high = [p_['crime_plus'] for p_ in pairs if p_['care_plus'] > med_c]
print(f'BROKEN-STICK: below {round(statistics.mean(low),1)} (n={len(low)}) vs above {round(statistics.mean(high),1)} (n={len(high)})')
