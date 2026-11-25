import json, statistics, re
from collections import defaultdict
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
panel = json.load(open(B + 'full_panel_v1.json', encoding='utf-8'))

def corr(x, yv):
    mx, my = statistics.mean(x), statistics.mean(yv)
    num = sum((a-mx)*(b-my) for a, b in zip(x, yv))
    den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in yv)) ** 0.5
    return round(num/den, 3) if den else None

print('=== THE DEEP-PANEL = THE INTERACTION-LANE (the diminished-choices-test!) ===')
print(f'panel: {len(panel)}-rows')
print()

# THE 1 = the MULTI-VAR = the simultaneous = the partial-correlations-class:
# the semi-partial = the care-vs-crime-CONTROLLING-unemp = the the residual-r!
# = the practical = the per-city-fixed-effects-THEN-pool (the the like-to-like-lane!):
cities = defaultdict(list)
for p_ in panel:
    cities[p_['city']].append(p_)
# THE within-city-care-crime (the v6d-panel):
w_pairs = []
for c, lst in cities.items():
    if len(lst) >= 2:
        mc = statistics.mean(x['care'] for x in lst); mk = statistics.mean(x['crime_plus'] for x in lst)
        for x in lst:
            w_pairs.append((c, x['care']-mc, x['crime_plus']-mk))
print(f'THE WITHIN-CITY = the care-residuals-vs-crime-residuals: r = {corr([w[1] for w in w_pairs], [w[2] for w in w_pairs])} (n={len(w_pairs)})')

# THE 2 = the LAGGED = the care-t vs the crime-t+2/t+3 = the the within-the-panel:
print()
print('THE LAGGED-LANE:')
lag_idx = {}
for c, lst in cities.items():
    for x in lst:
        lag_idx.setdefault(c, {})[x['year']] = x
for lag in (1, 2, 3):
    lags = []
    for c, yrs in lag_idx.items():
        for y, x in yrs.items():
            if y+lag in yrs:
                lags.append((x['care'], yrs[y+lag]['crime_plus']))
    if len(lags) >= 8:
        print(f'  care-t -> crime-t+{lag}: r = {corr([a for a, b in lags], [b for a, b in lags])} (n={len(lags)})')

# THE 3 = the BROKEN-STICK-REFINED = the multiple-thresholds = the scan-the-cut:
print()
print('THE BROKEN-STICK-SCAN = the the threshold-sweep (the find-the-bend!):')
q = sorted(p_['care'] for p_ in panel)
for pct in (25, 33, 40, 50, 60, 67, 75):
    cut = q[int(len(q)*pct/100)]
    low = [p_['crime_plus'] for p_ in panel if p_['care'] <= cut]
    high = [p_['crime_plus'] for p_ in panel if p_['care'] > cut]
    print(f'  cut-at-{pct}%-quantile (care={round(cut,1)}): below-mean {round(statistics.mean(low),1)} (n={len(low)}) vs above {round(statistics.mean(high),1)} (n={len(high)})')
