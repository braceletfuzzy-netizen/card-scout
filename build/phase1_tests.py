import json, math
from collections import defaultdict

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
rows = json.load(open(B + 'triple_slider_v6d.json', encoding='utf-8'))
# THE paired = the care+crime:
pairs = [(r['city'], r['year'], r['care_ratio'], r['crime_plus']) for r in rows if r.get('care_ratio') and r.get('crime_plus')]
print(f'=== THE PHASE-1 = THE FOUR-MODELS [the paired n={len(pairs)}] ===')
print()

# MODEL-1 = THE POOLED-CORRELATION:
import statistics
cs = [p[2] for p in pairs]; ks = [p[3] for p in pairs]
def corr(x, y):
    mx, my = statistics.mean(x), statistics.mean(y)
    num = sum((a-mx)*(b-my) for a, b in zip(x, y))
    den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in y)) ** 0.5
    return round(num/den, 3) if den else None
r_pooled = corr(cs, ks)
print(f'MODEL-1 POOLED: care-vs-CRIME+ correlation r = {r_pooled} (n={len(pairs)})')

# MODEL-2 = FIXED-EFFECTS = the within-city (the the de-meaned-per-city!):
cities = defaultdict(list)
for c, y, care, cp in pairs:
    cities[c].append((y, care, cp))
w_pairs = []
for c, lst in cities.items():
    if len(lst) >= 2:
        mc = statistics.mean(x[1] for x in lst); mk = statistics.mean(x[2] for x in lst)
        for y, care, cp in lst:
            w_pairs.append((c, y, care-mc, cp-mk))
r_within = corr([p[2] for p in w_pairs], [p[3] for p in w_pairs])
print(f'MODEL-2 FIXED-EFFECTS (within-city): r = {r_within} (n={len(w_pairs)} city-years, {len([c for c in cities if len(cities[c])>=2])} cities)')

# MODEL-3 = THE LAGGED (the crown!): care-at-t vs crime+-at-t+1..+5 (within-city):
lag_results = {}
for lag in (1, 2, 3, 4, 5):
    lags = []
    for c, lst in cities.items():
        ymap = {y: cp for y, care, cp in lst}
        caremap = {y: care for y, care, cp in lst}
        for y, care, cp in lst:
            if y+lag in ymap:
                lags.append((c, y, care, ymap[y+lag]))
    if len(lags) >= 6:
        r_lag = corr([p[2] for p in lags], [p[3] for p in lags])
        lag_results[lag] = (r_lag, len(lags))
        print(f'MODEL-3 LAGGED care-t -> CRIME+-t+{lag}: r = {r_lag} (n={len(lags)})')

# MODEL-4 = THE FLIP-EVENT-SLOPES (the Boston-95 + the NO-2006-11 + the NYC-98):
print()
print('MODEL-4 FLIP-EVENTS:')
# Boston: pre 1990-94 vs post 1995-2001 = the care-ratio-vs-CRIME+ windows:
for city_name, pre_years, post_years in [('Boston', (1990,1991,1993,1994), (1995,1999,2001)), ('New Orleans', (2004,2005,2006), (2011,2017,2019,2022)), ('NYC', (1998,), (1999,2000,2001))]:
    pre = [(y, care, cp) for c, y, care, cp in pairs if c == city_name and y in pre_years and cp is not None]
    post = [(y, care, cp) for c, y, care, cp in pairs if c == city_name and y in post_years and cp is not None]
    if pre and post:
        pre_m = statistics.mean(x[2] for x in pre); post_m = statistics.mean(x[2] for x in post)
        prek = statistics.mean(x[2] for x in pre); postk = statistics.mean(x[2] for x in post)
        print(f'  {city_name}: pre-CRIME+-mean {round(statistics.mean(x[2] for x in pre),1)} (n={len(pre)}) vs post {round(statistics.mean(x[2] for x in post),1)} (n={len(post)})')
