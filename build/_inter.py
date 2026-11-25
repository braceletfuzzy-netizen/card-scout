import json, statistics
from collections import defaultdict
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
panel = json.load(open(B + 'full_panel_v1.json', encoding='utf-8'))

def corr(x, yv):
    mx, my = statistics.mean(x), statistics.mean(yv)
    num = sum((a-mx)*(b-my) for a, b in zip(x, yv))
    den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in yv)) ** 0.5
    return round(num/den, 3) if den else None

# THE the interaction = the care-x-unemp = the the diminished-choices-test:
# = the does-the-care-matter-MORE-where-the-unemp-high?(the the choices-diminished!)
print('=== THE INTERACTION-LANE = THE CARE-x-UNEMP (the diminished-choices!) ===')
# = the split = the the high-unemp-half = the the care-crime-within:
us = [p_['unemp'] for p_ in panel if p_.get('unemp') is not None]
med_u = sorted(us)[len(us)//2]
for label, side in (('HIGH-unemp (the choices-diminished)', True), ('LOW-unemp', False)):
    sub = [p_ for p_ in panel if p_.get('unemp') is not None and ((p_['unemp'] >= med_u) == side)]
    xs = [p_['care'] for p_ in sub]
    ys = [p_['crime_plus'] for p_ in sub]
    print(f'  {label}: care-vs-crime r = {corr(xs, ys)} (n={len(sub)}, med-split-at {med_u})')
print()
# THE the migration-lane = the the outcomes = the the care-vs-migration (the the wage-loop!):
mig = [(p_['care'], p_['migration']) for p_ in panel if p_.get('migration') is not None]
print(f'THE CARE-vs-NET-MIGRATION (the wage-loop-test!): r = {corr([a for a, b in mig], [b for a, b in mig])} (n={len(mig)})')
# THE the grad-lane:
gr = [(p_['care'], p_['grad']) for p_ in panel if p_.get('grad') is not None]
print(f'THE CARE-vs-GRAD (the outcomes-beyond-crime!): r = {corr([a for a, b in gr], [b for a, b in gr])} (n={len(gr)})')
