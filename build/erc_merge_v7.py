import json, re
from collections import defaultdict

# THE ERC-CHUNK-MERGE (the 5-chunks = the unit-dedup = the the final-totals):
path = 'C:/Users/J/Documents/LLM/cardscout-2.0/data_lake/gold/nyc_erc_units.jsonl'
merged = defaultdict(lambda: {'otps': None, 'ps': None, 'chunks': []})
for line in open(path, encoding='utf-8'):
    line = line.strip()
    if not line:
        continue
    rec = json.loads(line)
    for k, v in rec['units'].items():
        m = merged[k]
        m['chunks'].append(rec['chunk'])
        if v.get('otps') and (m['otps'] is None or v['otps'] > m['otps']):
            m['otps'] = v['otps']
        if v.get('ps') and (m['ps'] is None or v['ps'] > m['ps']):
            m['ps'] = v['ps']

# THE name-clean (the 'AGENCY' = the trailing-artifact [the regex-caught = the 'AGENCY'-suffix-class]):
clean = {}
for k, v in merged.items():
    k2 = re.sub(r'\s*AGENCY\s*$', '', k).strip()
    clean[k2] = {'otps': v['otps'], 'ps': v['ps']}

with_tot = {k: v for k, v in clean.items() if v['otps'] or v['ps']}
print('units-matched:', len(clean), '| WITH-dollar-totals:', len(with_tot))
otps_sum = sum(v['otps'] or 0 for v in with_tot.values())
ps_sum = sum(v['ps'] or 0 for v in with_tot.values())
print(f'OTPS-sum: ${otps_sum:,}')
print(f'PS-sum: ${ps_sum:,}')
print(f'COMBINED: ${otps_sum + ps_sum:,}')
print()
top = sorted(with_tot.items(), key=lambda x: -((x[1]['otps'] or 0) + (x[1]['ps'] or 0)))
print('THE TOP-25:')
for k, v in top[:25]:
    print(f" - {k[:54]:56s} OTPS: {(v['otps'] or 0):>14,}  PS: {(v['ps'] or 0):>14,}")

json.dump(clean, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/nyc_erc_units_v7_FINAL.json', 'w', encoding='utf-8'), indent=1)
print()
print('WROTE nyc_erc_units_v7_FINAL.json')
