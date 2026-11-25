import json, statistics
from collections import defaultdict
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
panel = json.load(open(B + 'full_panel_v1.json', encoding='utf-8'))
def corr(x, yv):
    mx, my = statistics.mean(x), statistics.mean(yv)
    num = sum((a-mx)*(b-my) for a, b in zip(x, yv))
    den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in yv)) ** 0.5
    return round(num/den, 3) if den else None
# THE the WITHIN-CITY-LAGGED = the the honest-lagged (the the cross-city-confound-REMOVED!):
cities = defaultdict(dict)
for p_ in panel:
    cities[p_['city']][p_['year']] = p_
print('THE THE-WITHIN-CITY-LAGGED [the honest-lag = the confound-removed!]:')
for lag in (1, 2, 3):
    lags = []
    for c, yrs in cities.items():
        my_ = statistics.mean(x['crime_plus'] for x in yrs.values())
        mc = statistics.mean(x['care'] for x in yrs.values())
        for y, p_ in yrs.items():
            if y+lag in yrs:
                lags.append((p_['care']-mc, yrs[y+lag]['crime_plus']-my_))
    if len(lags) >= 8:
        print(f'  care-residual-t -> crime-residual-t+{lag}: r = {corr([a for a, b in lags], [b for a, b in lags])} (n={len(lags)})')
