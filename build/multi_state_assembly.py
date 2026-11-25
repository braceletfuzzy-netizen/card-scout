import json, statistics
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

# THE VERIFIED STATE-MH SERIES (widening-pass child captures + v1 bank)
state_mh = {
 'NY': {2019: 4264.744, 2020: 4395.554, 2021: 4454.322, 2022: 4435.572, 2023: 5118.440, 2024: 6363.191, 2025: 5898.620},
 'MO': {2019: 2250.871, 2020: 2482.230, 2021: 2515.693, 2022: 2734.926, 2023: 3423.780, 2024: 4040.0, 2025: 4390.0},
 'PA': {2019: 1058.259, 2020: 1123.539, 2021: 1202.993, 2022: 1261.910, 2023: 1334.732, 2024: 1382.353, 2025: 1363.083},
 'TN': {2024: 424.0, 2025: 436.5},
}
state_pop = {'NY': 19_600_000, 'MO': 6_150_000, 'PA': 12_850_000, 'TN': 6_900_000}
city_of_state = {'NY': 'NYC', 'MO': 'St. Louis', 'PA': 'Pittsburgh', 'TN': 'Memphis'}

# THE CITY-EQUIVS = the pop-grain per MSA-proxy-class:
# NYC = the 5-boroughs ~19.6M-state/8.3M-city-class [the honest = the 8.4M]
# Pittsburgh = the = the = the 302k-city-class
# Memphis = the 633k-class
# StL = the banked!
CITY_POP_APPROX = {
 'NYC': 8_400_000,
 'Pittsburgh': 302_000,   # [Approx-flag — the = the banked-pop = the 2019-class]
 'Memphis': 633_000,      # [Approx-flag]
 'St. Louis': None,       # = the = the banked!
}

murders = json.load(open(B + 'murders_all_v1.json', encoding='utf-8'))
murders_idx = {}
for k, m in murders.items():
    c, y = k.split('|')
    murders_idx[(c, int(y))] = m

pops = {}
for f in ('population_series_v1.jsonl', 'nola_houston_pair_v1.jsonl', 'populations_wide_v1.jsonl'):
    try:
        for l in open(B + f, encoding='utf-8'):
            if not l.strip():
                continue
            r = json.loads(l)
            try:
                pop = r.get('population')
                city = (r.get('city') or '').strip()
                yr = int(str(r.get('year'))[:4])
                if pop and city and yr:
                    pops.setdefault((city, yr), pop)
            except Exception:
                pass
    except FileNotFoundError:
        pass

def corr(x, yv):
    if len(x) < 3 or len(set(yv)) < 2:
        return None
    mx, my = statistics.mean(x), statistics.mean(yv)
    num = sum((a-mx)*(b-my) for a, b in zip(x, yv))
    den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in yv)) ** 0.5
    return round(num/den, 3) if den else None

def city_pop(c, y):
    # the banked = first = the = the approx-class-flag = the = the second:
    hit = pops.get((c, y)) or pops.get((c, y-1)) or pops.get((c, y-2))
    if hit:
        return hit, 'banked'
    if c in CITY_POP_APPROX and CITY_POP_APPROX[c]:
        return CITY_POP_APPROX[c], 'approx-flagged'
    return None, 'null'

print('=== THE MULTI-STATE ASSEMBLY: WITHIN-STATE MH-STATE-SPEND vs CITY-CRIME ===')
print('  (state-pop = static approximations; city-pop = banked-first/flagged-approx-second)')
print()
all_pairs = []
for st, yrs in state_mh.items():
    c = city_of_state[st]
    spop = state_pop[st]
    prs = []
    for y, musd in sorted(yrs.items()):
        if musd is None: continue
        m = murders_idx.get((c, y))
        if m is None: continue
        cp, class_ = city_pop(c, y)
        if not cp: continue
        per_cap = round(musd * 1_000_000 / spop, 1)
        rate = round(m / cp * 100000, 2)
        prs.append((per_cap, rate, y, c, class_))
    all_pairs.extend(prs)
    if len(prs) >= 3:
        r = corr([a[0] for a in prs], [a[1] for a in prs])
        approx = any(a[4] == 'approx-flagged' for a in prs)
        flag = ' [approx-flagged-pops-in-lane]' if approx else ''
        print(f' {c}/{st}: n={len(prs)} span {prs[0][2]}-{prs[-1][2]} | within-state r = {r}{flag}')
        for p in prs:
            print(f'   {p[2]}: state-MH/cap ${p[0]} | rate {p[1]} [{p[4]}]')
    else:
        print(f' {c}/{st}: n={len(prs)} | TOO-THIN (honest)')

print()
per_state = {}
for a in all_pairs:
    per_state.setdefault(a[3], []).append(a)
used_states = [c for c in per_state if len(per_state[c]) >= 3]
dm_pairs = []
for c in used_states:
    prs = per_state[c]
    mx = statistics.mean([a[0] for a in prs])
    my = statistics.mean([a[1] for a in prs])
    for a in prs:
        dm_pairs.append((a[0]-mx, a[1]-my, a[2], a[3]))
r_pooled = corr([a[0] for a in dm_pairs], [a[1] for a in dm_pairs])
print(f'THE POOLED-WITHIN-STATE (demeaned, n={len(dm_pairs)}, cities={used_states}): r = {r_pooled}')
print()
mh_idx = {(a[3], a[2]): a[0] for a in all_pairs}
city_years = {(a[3], a[2]): a[1] for a in all_pairs}
for lag in (1, 2):
    pairs_l = []
    for (c, y) in mh_idx:
        if (c, y+lag) in city_years:
            pairs_l.append((mh_idx[(c, y)], city_years[(c, y+lag)], c, y))
    if len(pairs_l) >= 6:
        r_l = corr([a[0] for a in pairs_l], [a[1] for a in pairs_l])
        print(f' state-MH(t) vs crime(t+{lag}): r = {r_l} (n={len(pairs_l)})')
