import json, statistics, re
from collections import defaultdict

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

def norm(c):
    c = (c or '').lower().strip()
    if c == 'new york city' or c == 'new york': return 'NYC'
    if c == 'st. louis': return 'St. Louis'
    if c == 'oke': return 'Oklahoma City'
    return c.title().replace('St Louis', 'St. Louis')

def ny(y):
    m = re.search(r'((19|20)\d\d)', str(y))
    return int(m.group(1)) if m else None

# THE sources:
tri = json.load(open(B + 'triple_slider_v6d.json', encoding='utf-8'))
soc = [json.loads(l) for l in open(B + 'socioeconomic_series_v1.jsonl', encoding='utf-8') if l.strip()]
pol = [json.loads(l) for l in open(B + 'policy_series_v1.jsonl', encoding='utf-8') if l.strip()]
out2 = [json.loads(l) for l in open(B + 'outcomes_series_v1.jsonl', encoding='utf-8') if l.strip()]

# THE indexes = the city-year:
def idx(rows, fields):
    d = {}
    for r in rows:
        c = norm(r.get('city')); y = ny(r.get('year'))
        if not c or not y: continue
        d.setdefault((c, y), {})
        for f in fields:
            if r.get(f) is not None:
                d[(c, y)].setdefault(f, r.get(f))
    return d

soc_idx = idx(soc, ('unemployment_rate', 'poverty_rate', 'median_income', 'bachelors_pct'))
pol_idx = idx(pol, ('officers_per_100k', 'state_eitc_flag', 'housing_burden_pct'))
out_idx = idx(out2, ('grad_rate', 'life_expectancy', 'net_migration', 'tax_base_per_capita_est'))

# THE PANEL = the budget-care + crime from-the-tri + the soc + the pol:
panel = []
for r in tri:
    c = norm(r.get('city')); y = ny(r['year'])
    if r.get('care_ratio') is None or r.get('crime_plus') is None: continue
    s = soc_idx.get((c, y), {}); p = pol_idx.get((c, y), {}); o = out_idx.get((c, y), {})
    panel.append({'city': r['city'], 'year': y,
                  'care': r['care_ratio']*100, 'crime_plus': r['crime_plus'],
                  'unemp': s.get('unemployment_rate'), 'poverty': s.get('poverty_rate'),
                  'officers': p.get('officers_per_100k'), 'grad': o.get('grad_rate'),
                  'migration': o.get('net_migration')})

# THE the counts:
have_unemp = sum(1 for p_ in panel if p_.get('unemp') is not None)
have_off = sum(1 for p_ in panel if p_.get('officers') is not None)
have_pov = sum(1 for p_ in panel if p_.get('poverty') is not None)
print(f'PANEL-ROWS: {len(panel)} | with-unemp: {have_unemp} | with-officers: {have_off} | with-poverty(ACS): {have_pov}')
print()

def corr(x, yv):
    mx, my = statistics.mean(x), statistics.mean(yv)
    num = sum((a-mx)*(b-my) for a, b in zip(x, yv))
    den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in yv)) ** 0.5
    return round(num/den, 3) if den else None

# A = the care-vs-each:
yv = [p_['crime_plus'] for p_ in panel]
for f, label in (('care', 'CARE+'), ('unemp', 'unemployment'), ('officers', 'officers-100k'), ('poverty', 'poverty(ACS)')):
    xs = [p_.get(f) for p_ in panel if p_.get(f) is not None]
    ys = [p_['crime_plus'] for p_ in panel if p_.get(f) is not None]
    if len(xs) >= 8:
        print(f'{label}-vs-CRIME+: r = {corr(xs, ys)} (n={len(xs)})')

# B = THE BROKEN-STICK (the founder's-inflection-guess!): the care-per-100k = the threshold-test:
# the simple = the split-at-the-median-care = the two-side-slopes:
xs = [p_['care'] for p_ in panel if p_.get('unemp') is not None]
print()
print('THE BROKEN-STICK ON CARE (the inflection-test):')
cs = sorted(set(p_['care'] for p_ in panel))
med_c = sorted(p_['care'] for p_ in panel)[len(panel)//2]
low = [(p_['care'], p_['crime_plus']) for p_ in panel if p_['care'] <= med_c]
high = [(p_['care'], p_['crime_plus']) for p_ in panel if p_['care'] > med_c]
for nm, side in (('below-median-care', low), ('above-median-care', high)):
    lx = [a for a, b in side]; ly = [b for a, b in side]
    print(f'  {nm}: mean-CRIME+ {round(statistics.mean(ly),1)} (n={len(side)})')
print()
print('CRITICAL-MASS-READ: the below-vs-above = the care-threshold = the the flat-or-steeper = the the printed!')
json.dump(panel, open(B + 'full_panel_v1.json', 'w', encoding='utf-8'), indent=1)
print('WROTE full_panel_v1.json')
