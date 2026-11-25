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
CITY_POP_APPROX = {'NYC': 8_400_000, 'Pittsburgh': 302_000, 'Memphis': 633_000}

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
    hit = pops.get((c, y)) or pops.get((c, y-1)) or pops.get((c, y-2))
    if hit:
        return hit, 'banked'
    if c in CITY_POP_APPROX:
        return CITY_POP_APPROX[c], 'approx-flagged'
    return None, 'null'

# ==== THE SAME-YEAR + LAG PER CITY ====
print('=== THE STATE-MH(t) vs CITY-CRIME(t and t+lag) ARC, PER CITY ===')
print()
all_pairs = []
for st, yrs in state_mh.items():
    c = city_of_state[st]
    spop = state_pop[st]
    lane = []
    for y, musd in sorted(yrs.items()):
        if musd is None: continue
        cp, class_ = city_pop(c, y)
        m = murders_idx.get((c, y))
        if not cp or m is None: continue
        lane.append((y, round(musd*1_000_000/spop, 1), round(m/cp*100000, 2)))
    all_pairs.append((st, c, lane))
    if len(lane) >= 3:
        r = corr([p[1] for p in lane], [p[2] for p in lane])
        print(f' {c}/{st}: n={len(lane)} | same-year r = {r}')
        # the t+1-lag lane:
        lag1 = [(lane[i][1], lane[i+1][2]) for i in range(len(lane)-1)]
        if len(lag1) >= 3:
            r1 = corr([a[0] for a in lag1], [a[1] for a in lag1])
            print(f'   t vs t+1 (n={len(lag1)}): r = {r1}')
        # the = the t+2:
        lag2 = [(lane[i][1], lane[i+2][2]) for i in range(len(lane)-2)]
        if len(lag2) >= 3:
            r2 = corr([a[0] for a in lag2], [a[1] for a in lag2])
            print(f'   t vs t+2 (n={len(lag2)}): r = {r2}')

# ==== THE THE-2-WAY-TIME = the THE WITHIN-STATE-DIFF = the ====
print()
print('=== THE WITHIN-STATE DELTA-LANES (t vs t-1 = the CHANGES-class) ===')
dmn = []
for st, c, lane in all_pairs:
    if len(lane) < 3: continue
    dl = [(lane[i][1]-lane[i-1][1], lane[i][2]-lane[i-1][2]) for i in range(1, len(lane))]
    if len(dl) >= 3:
        r = corr([a[0] for a in dl], [a[1] for a in dl])
        print(f' {c}/{st}: n={len(dl)} | delta-MH vs delta-rate r = {r}')
