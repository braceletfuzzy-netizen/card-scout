import json, re, statistics
from collections import defaultdict
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
exec(open(B + '_rerun2.py').read().split('# THE the normalize')[0])
# THE the pooled = the the ratios = the the ranked-within-the-year-bucket = the simpler = the the raw:
# = THE THE-PAIR = the care-ratio-vs-the-crime-rate = the the both-raw = the the pooled-corr:
def corr(x, yv):
    mx, my = statistics.mean(x), statistics.mean(yv)
    num = sum((a-mx)*(b-my) for a, b in zip(x, yv))
    den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in yv)) ** 0.5
    return round(num/den, 3) if den else None
print(f'THE RAW-WIDE-PAIR = care-ratio-vs-murder-rate: r = {corr([p_["care_ratio"] for p_ in pairs], [p_["rate"] for p_ in pairs])} (n={len(pairs)})')
# THE the log = the the skew-fix:
import math
log_pairs = [(math.log(p_['care_ratio']), math.log(p_['rate'])) for p_ in pairs if p_['care_ratio'] > 0 and p_['rate'] > 0]
print(f'THE LOG-LOG: r = {corr([a for a, b in log_pairs], [b for a, b in log_pairs])} (n={len(log_pairs)})')
# THE the cities = the the list:
print('the panel-cities:', sorted(set(p_['city'] for p_ in pairs)))
json.dump(pairs, open(B + 'wide_panel_pairs_v1.json', 'w', encoding='utf-8'), indent=1)
print('WROTE wide_panel_pairs_v1.json')
