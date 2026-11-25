import json, statistics
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

# THE V2-SERIES from the = the = the = the = the = the!
rows = [json.loads(l) for l in open(B + 'state_mh_series_v2.jsonl', encoding='utf-8') if l.strip()]
state_vals = {}
for r in rows:
    st = r.get('state') or r.get('st')
    fy = r.get('fiscal_year') or r.get('year')
    v = r.get('state_mh_budget_usd')
    if not st or not fy or not v:
        continue
    try:
        y = int(str(fy)[-4:])
    except Exception:
        continue
    state_vals.setdefault(st, {})[y] = (v, r.get('value_kind', ''))

state_pop = {'NY': 19_600_000, 'MO': 6_150_000, 'PA': 12_850_000, 'TN': 6_900_000,
             'OH': 11_800_000, 'MI': 10_000_000, 'OK': 3_950_000, 'LA': 4_650_000}
city_of_state = {'NY': 'NYC', 'MO': 'St. Louis', 'PA': 'Pittsburgh', 'TN': 'Memphis',
                 'OH': 'Cincinnati', 'MI': 'Detroit', 'OK': 'Oklahoma City', 'LA': 'New Orleans'}
CITY_POP_APPROX = {'NYC': 8_400_000, 'Pittsburgh': 302_000, 'Memphis': 633_000,
                   'Cincinnati': 309_000, 'Detroit': 633_000, 'Oklahoma City': 681_000,
                   'New Orleans': 391_000}

murders = json.load(open(B + 'murders_all_v1.json', encoding='utf-8'))
murders_idx = {}
for k, m in murders.items():
    c, y = k.split('|')
    murders_idx[(c, int(y))] = m
pops = {}
for f in ('population_series_v1.jsonl', 'nola_houston_pair_v1.jsonl', 'populations_wide_v1.jsonl'):
    try:
        for l in open(B + f, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l)
            try:
                pop = r.get('population'); city = (r.get('city') or '').strip(); yr = int(str(r.get('year'))[:4])
                if pop and city and yr:
                    pops.setdefault((city, yr), pop)
            except Exception: pass
    except FileNotFoundError: pass

def corr(x, yv):
    if len(x) < 3 or len(set(yv)) < 2: return None
    mx, my = statistics.mean(x), statistics.mean(yv)
    num = sum((a-mx)*(b-my) for a, b in zip(x, yv))
    den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in yv)) ** 0.5
    return round(num/den, 3) if den else None

def city_pop(c, y):
    hit = pops.get((c, y)) or pops.get((c, y-1)) or pops.get((c, y-2))
    if hit: return hit, 'banked'
    if c in CITY_POP_APPROX: return CITY_POP_APPROX[c], 'approx'
    return None, 'null'

print('=== THE EXPANDED MULTI-STATE (the = the = the = the = the) ===')
all_pairs = []
for st in sorted(state_vals):
    if st not in state_pop: continue
    c = city_of_state[st]
    spop = state_pop[st]
    lane = []
    for y, (v, kind) in sorted(state_vals[st].items()):
        m = murders_idx.get((c, y))
        if m is None: continue
        cp, cls = city_pop(c, y)
        if not cp: continue
        lane.append((y, round(v*1_000_000/spop if v < 1e12 else v/spop, 1), round(m/cp*100000, 2), cls))
    if lane:
        all_pairs.append((st, c, lane))
    if len(lane) >= 3:
        r = corr([p[1] for p in lane], [p[2] for p in lane])
        approx = any(p[3] == 'approx' for p in lane)
        print(f' {c}/{st}: n={len(lane)} | same-year r = {r} {" [approx-pops]" if approx else ""} span {lane[0][0]}-{lane[-1][0]}')
        for lag in (1, 2):
            ll = [(lane[i][1], lane[i+lag][2]) for i in range(len(lane)-lag)]
            if len(ll) >= 3:
                print(f'   t vs t+{lag} (n={len(ll)}): r = {corr([a[0] for a in ll], [a[1] for a in ll])}')
    else:
        print(f' {c}/{st}: n={len(lane)} | TOO-THIN (honest)')

# THE POOLED-WITHIN-STATE
per_city = {}
for triple in all_pairs:
    st, c, lane = triple
    if len(lane) >= 3:
        per_city.setdefault(c, lane)
dm_pairs = []
for c, lane in per_city.items():
    mx = statistics.mean([p[1] for p in lane]); my = statistics.mean([p[2] for p in lane])
    for p in lane:
        dm_pairs.append((p[1]-mx, p[2]-my, p[0], c))
print()
r_pooled = corr([a[0] for a in dm_pairs], [a[1] for a in dm_pairs])
print(f'THE POOLED-WITHIN-STATE (demeaned, n={len(dm_pairs)}, cities={sorted(per_city)}): r = {r_pooled}')
