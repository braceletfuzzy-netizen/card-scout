# _prepost_test.py — the Raleigh Springs pre/post TEST (the real pass)
# THE HONEST DESIGN: no pre-2016 corridor baseline exists (MPD dataset starts 2020).
# So the test = DIFFERENTIAL: corridor trend vs citywide trend over the same
# 2020-2026 window (a difference-in-trends, not a before/after).
# IF the corridor falls FASTER than the citywide arc, the site-treatment effect
# survives the citywide-crime-wave control — that's the honest read available.

import json

d = json.load(open('raleigh_springs_site_v2.json', encoding='utf-8'))
mem = d['lanes']['1a_tibrs_baseline_lane']['memphis_pd_series']
cl = d['lanes']['1_crime_series']

corr_annual = cl['annual_counts_bbox']
corr_viol = cl['violent_counts_bbox']
corr_prop = cl['property_counts_bbox']

# Citywide post-years (2020-2026), same window as corridor
city = {}
for y in mem:
    if int(y['year']) >= 2020:
        city[y['year']] = {
            'murder': (y.get('murder') or {}).get('cases'),
            'agg': (y.get('agg_assault') or {}).get('cases'),
            'rob': (y.get('robbery') or {}).get('cases'),
            'total': None,
        }
# citywide total = agg+rob+mvt+murder (Group-A proxy from TIBRS cards present)
for k, v in city.items():
    parts = [x for x in (v['murder'], v['agg'], v['rob']) if x is not None]
    v['index3'] = sum(parts)

years = sorted(corr_annual)
print('=== THE DIFFERENTIAL-TEST: corridor vs citywide, 2020-2026 ===')
print()
print('CITYWIDE (TIBRS cards: murder+agg+rob index3):')
for yr in years:
    c = city.get(str(yr))
    if c:
        print(f'  {yr}: {c["index3"]:,}')
c20 = city.get('2020'); c26 = city.get('2026')
city_delta = (c26['index3'] - c20['index3']) / c20['index3'] * 100
print(f'  citywide index3 2020->2026: {city_delta:+.1f}%')

print()
print('MURDER:')
for yr in years:
    cm = city[str(yr)]['murder']
    print('  %s: citywide %s' % (yr, cm))

mur20 = city['2020']['murder']; mur26 = city['2026']['murder']
city_mur_delta = (mur26 - mur20) / mur20 * 100
print(f'  citywide murder 2020->2026: {city_mur_delta:+.1f}%')

print()
print('CORRIDOR (MPD bbox):')
corr_i20 = corr_annual['2020']; corr_i26 = corr_annual['2026']
corr_delta_all = (corr_i26 - corr_i20) / corr_i20 * 100
cv20 = corr_viol['2020']; cv26 = corr_viol['2026']
corr_v_delta = (cv26 - cv20) / cv20 * 100
cp20 = corr_prop['2020']; cp26 = corr_prop['2026']
corr_p_delta = (cp26 - cp20) / cp20 * 100
print(f'  all-incidents 2020->2026: {corr_i20} -> {corr_i26} = {corr_delta_all:+.1f}%')
print(f'  violent        2020->2026: {cv20} -> {cv26} = {corr_v_delta:+.1f}%')
print(f'  property       2020->2026: {cp20} -> {cp26} = {corr_p_delta:+.1f}%')

print()
print('=== THE HONEST VERDICT ===')
print(f'corridor all-incidents: {corr_delta_all:+.1f}%  | citywide index3: {city_delta:+.1f}%')
print(f'corridor differential vs citywide: {corr_delta_all - city_delta:+.1f} points')
print(f'corridor violent: {corr_v_delta:+.1f}%  | citywide murder+agg+rob proxy: {city_mur_delta:+.1f}%')

# The 2024-2026 tail (post-treatment maturity: library opened 2020-11)
t24, t26 = corr_annual['2024'], corr_annual['2026']
tail_delta = (t26 - t24) / t24 * 100
print()
print(f'corridor 2024->2026 tail: {tail_delta:+.1f}%')
city24, city26 = city['2024'], city['2026']
city_tail = (city26['index3'] - city24['index3']) / city24['index3'] * 100
print(f'citywide 2024->2026 tail: {city_tail:+.1f}%')
print(f'corridor differential-tail: {tail_delta - city_tail:+.1f} points')
