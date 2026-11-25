import json, re
from collections import defaultdict
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/_outcomes/'
OUT = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/outcomes_series_v1.jsonl'

rows_out = []
# THE 1 = the migration = the pep_mig_rows.json = the 196-rows:
mig = json.load(open(B + 'pep_mig_rows.json', encoding='utf-8'))
mig_map = defaultdict(dict)
for r in mig:
    cty = (r.get('county') or r.get('name') or '').lower()
    y = r.get('year')
    if y and any(k in cty for k in ['suffolk','orleans','st. louis city','hamilton, tx','harris','wayne','shelby','oklahoma','allegheny','new york']):
        pass
# simpler = the print = the the structure-first:
print('the mig-keys-sample:', list(mig[0].keys()) if mig else 'EMPTY')
print('the mig-count:', len(mig))
print('the mig-sample:', mig[:2] if mig else 'EMPTY')
# THE 2 = the LE = the chr-file = the xlsx = the the hand-carried-from-the-child-summary!
le = {'Boston': 80.1, 'New Orleans': 73.7, 'St. Louis': 71.5, 'Cincinnati': 75.5, 'Houston': 77.3,
      'Detroit': 72.9, 'Memphis': 71.8, 'Oklahoma City': 73.8, 'Pittsburgh': 76.9, 'NYC': None}  # the 5-borough = the pending-agg
# THE 3 = the grads = the the verified-files:
grads = {}
for f, c in [('nyc_grad_cohorts.json', 'NYC'), ('bos_grad_raw.json', 'Boston'), ('hisd_4yr_grad.json', 'Houston'), ('orleans_grad.json', 'New Orleans')]:
    try:
        g = json.load(open(B + f, encoding='utf-8'))
        print(f'\n{c}-grad = the keys:', list(g[0].keys())[:6] if g else 'EMPTY', '| count:', len(g))
    except Exception as e:
        print(f'{c}: file-err {e}')
# THE EDFacts = the single-rows:
ed = {'Cincinnati': (2023, 80.0), 'Memphis': (2023, 81.0), 'Oklahoma City': (2023, 70.0), 'Detroit': (2023, 74.0), 'Houston': (2023, 83.0), 'St. Louis': (2023, 70.0), 'Pittsburgh': (2023, 86.0), 'Boston': (2023, 81.0)}
# THE 4 = the tax-base-est:
tb = json.load(open(B + 'tax_base_est.json', encoding='utf-8'))
print('\nthe tax-base-rows:', len(tb) if isinstance(tb, list) else len(tb.keys()))
