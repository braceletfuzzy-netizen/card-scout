import json
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/_outcomes/'
rows = []
# THE 1 = the migration = the 196-direct:
mig = json.load(open(B + 'pep_mig_rows.json', encoding='utf-8'))
mig_idx = {}
for m in mig:
    mig_idx[(m['city'], str(int(m['year'])))] = m['net_migration']
# THE 2 = the LE = the 2020-22-banked:
le = {'Boston': 80.1, 'New Orleans': 73.7, 'St. Louis': 71.5, 'Cincinnati': 75.5, 'Houston': 77.3,
      'Detroit': 72.9, 'Memphis': 71.8, 'Oklahoma City': 73.8, 'Pittsburgh': 76.9}
# THE 3 = the grads:
grads = {}
nyc = json.load(open(B + 'nyc_grad_cohorts.json', encoding='utf-8'))
for y, v in nyc.items():
    grads[('NYC', y)] = float(v['rate'])
bos = json.load(open(B + 'bos_grad_raw.json', encoding='utf-8'))
for y, v in bos.items():
    # the rate = the 4th-element (index-3):
    try:
        grads[('Boston', y)] = float(v[3])
    except Exception:
        pass
hisd = json.load(open(B + 'hisd_4yr_grad.json', encoding='utf-8'))
for y, v in hisd.items():
    try:
        grads[('Houston', y)] = float(v[2])
    except Exception:
        pass
orl = json.load(open(B + 'orleans_grad.json', encoding='utf-8'))
for y, v in orl.items():
    grads[('New Orleans', y)] = float(v)
ed = {'Cincinnati': (2023, 80.0), 'Memphis': (2023, 81.0), 'Oklahoma City': (2023, 70.0), 'Detroit': (2023, 74.0), 'Houston': (2023, 83.0), 'St. Louis': (2023, 70.0), 'Pittsburgh': (2023, 86.0), 'Boston': (2023, 81.0)}
for c, (y, g) in ed.items():
    grads.setdefault((c, str(y)), g)
# THE 4 = the tax-base:
tb = json.load(open(B + 'tax_base_est.json', encoding='utf-8'))
tb_idx = {}
for c, yrs in tb.items():
    for y, v in yrs.items():
        tb_idx[(c, str(int(y)))] = v.get('est')
# THE THE-ASSEMBLE = the union-keys = the city-years:
all_keys = set()
for idx in (mig_idx, tb_idx):
    for (c, y) in idx:
        all_keys.add((c, y))
for (c, y) in grads:
    all_keys.add((c, str(int(y))))
out = []
le_years = ('2020', '2021', '2022')
for (c, y) in sorted(all_keys):
    le_v = le.get(c) if y in le_years else None
    row = {'city': c, 'year': y,
           'grad_rate': grads.get((c, str(int(y)))),
           'life_expectancy': le_v,
           'net_migration': mig_idx.get((c, str(int(y)))),
           'tax_base_per_capita_est': tb_idx.get((c, str(int(y)))),
           'source_refs': 'net-migration: Census PEP county components (co-est2020/co-est2024); grad: district-series + EDFacts-2023; LE: CHR-2020-22-bank; tax-base: budget-proxy-est',
           'notes': 'stitched-by-parent-from-the-lane-c-verified-intermediates'
           }
    rows.append(row)
    rows_r = json.dumps(row)
open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/outcomes_series_v1.jsonl', 'w', encoding='utf-8', newline='').write(chr(10).join(json.dumps(r) for r in rows) + chr(10))
print('WROTE outcomes_series_v1.jsonl:', len(rows), 'rows')
# THE the spot-checks:
for r in rows:
    if r['city'] == 'New Orleans' and r['year'] in ('2011', '2017'):
        print(' NO', r['year'], '| grad', r.get('grad_rate'), '| mig', r.get('net_migration'), '| tb', r.get('tax_base_per_capita_est'))
    if r['city'] == 'NYC' and r['year'] in ('2001', '2019'):
        print(' NYC', r['year'], '| grad', r.get('grad_rate'), '| mig', r.get('net_migration'))
