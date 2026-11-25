import json, statistics
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

state_mh = {
 'NY': {2019: 4264.744, 2020: 4395.554, 2021: 4454.322, 2022: 4435.572, 2023: 5118.440, 2024: 6363.191, 2025: 5898.620, 2026: 6271.935},
 'MO': {2019: 2250.871, 2020: 2482.230, 2021: 2515.693, 2022: 2734.926, 2023: 3423.780, 2024: 4040.0, 2025: 4390.0},
 'PA': {2019: 1058.259, 2020: 1123.539, 2021: 1202.993, 2022: 1261.910, 2023: 1334.732, 2024: 1382.353, 2025: 1363.083, 2026: 1428.067},
 'TN': {2024: 424.0, 2025: 436.5, 2026: 441.3},
}
state_pop = {'NY': 19_600_000, 'MO': 6_150_000, 'PA': 12_850_000, 'TN': 6_900_000}
city_of_state = {'NY': 'NYC', 'MO': 'St. Louis', 'PA': 'Pittsburgh', 'TN': 'Memphis'}
murders = json.load(open(B + 'murders_all_v1.json', encoding='utf-8'))
murders_idx = {}
for k, m in murders.items():
    c, y = k.split('|')
    murders_idx[(c, int(y))] = m
pops = {}
for f in ('population_series_v1.jsonl', 'nola_houston_pair_v1.jsonl'):
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
    mx, my = statistics.mean(x), statistics.mean(yv)
    num = sum((a-mx)*(b-my) for a, b in zip(x, yv))
    den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in yv)) ** 0.5
    return round(num/den, 3) if den else None

print('=== THE WITHIN-STATE MH vs CRIME TEST ===')
all_pairs = []
for st, yrs in state_mh.items():
    c = city_of_state[st]
    spop = state_pop[st]
    prs = []
    for y, musd in yrs.items():
        if musd is None: continue
        m = murders_idx.get((c, y))
        if m is None: continue
        per_cap = round(musd * 1_000_000 / spop, 1)
        pop_c = pops.get((c, y)) or pops.get((c, y-1)) or pops.get((c, y-2))
        if not pop_c: continue
        rate = round(m / pop_c * 100000, 2)
        prs.append((per_cap, rate, y, c))
    all_pairs.extend(prs)
    if len(prs) >= 3:
        r = corr([a[0] for a in prs], [a[1] for a in prs])
        print(f' {c}/{st}: n={len(prs)} ({prs[0][2]}-{prs[-1][2]}) | within-state r = {r}')
        for p in prs:
            print(f'   {p[2]}: state-MH/capita ${p[0]} | rate {p[1]}')
print()
n = len(all_pairs)
r_all = corr([a[0] for a in all_pairs], [a[1] for a in all_pairs])
print(f'THE POOLED-WITHIN-STATE (n={n}, states={sorted(set(a[3] for a in all_pairs))}): r = {r_all}')
mh_idx = {(a[3], a[2]): a[0] for a in all_pairs}
city_years = {(a[3], a[2]): a[1] for a in all_pairs}
for lag in (1, 2):
    lags = [(mh_idx[(c, y)], city_years[(c, y+lag)]) for (c, y) in mh_idx if (c, y+lag) in city_years]
    if len(lags) >= 6:
        print(f' state-MH/capita at t vs crime at t+{lag}: r = {corr([a for a, b in lags], [b for a, b in lags])} (n={len(lags)})')
