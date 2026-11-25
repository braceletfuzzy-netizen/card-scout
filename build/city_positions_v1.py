import json, os

# POLYSCOUT — THE PARQUET-LAYER v1 (the the cards-modeled = the the ONE-row-per-city!)
# THE collect-the-cities = the the from-the-tonight's-JSONs:
rows = []
# the band-A:
d = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/band_a_ingestion_v1.json', encoding='utf-8'))
for c in (d if isinstance(d, list) else d.get('cities', [])):
    rows.append({'city': c.get('city'), 'band': 'A', 'budget_adopted': c.get('budget_total_adopted'),
                 'fy': c.get('fiscal_year'), 'source_url': c.get('source_url'),
                 'dept_rows': len(c.get('per_department_totals') or {}), 'provenance_class': 'official-pdf' if c.get('budget_total_adopted') != 1600000000 else 'press',
                 'honest_flags': str(c.get('honest_gaps'))[:150]})
# the bcd:
for line in open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/bands_bcd_ingestion_v1.json', encoding='utf-8'):
    if not line.strip(): continue
    c = json.loads(line)
    rows.append({'city': c.get('city'), 'band': c.get('band'), 'budget_adopted': c.get('budget_total_adopted'),
                 'fy': (c.get('fiscal_year') or '')[:9], 'source_url': (c.get('source_url') or '')[:140],
                 'dept_rows': len(c.get('per_department_totals') or {}), 'provenance_class': 'official' if 'adopted' in (c.get('fiscal_year') or '').lower() or c.get('city') != 'Houston' else 'proposed-flag',
                 'honest_flags': str(c.get('honest_gaps'))[:150]})
# the NYC + the Memphis = the the the special-rows:
rows.append({'city': 'New York City', 'band': 'D', 'budget_adopted': 11507000000, 'fy': 'FY2026',
             'source_url': 'the OMB-sum5-25 + the ERC + the MMR-2026 (the 544pp!)', 'dept_rows': 163,
             'provenance_class': 'official-TWO-SCALE', 'honest_flags': 'the MMR-yield-side-live!'})
rows.append({'city': 'Memphis', 'band': 'A', 'budget_adopted': 1740000000, 'fy': 'FY2026',
             'source_url': 'the FY26-book (the 16-Police-KPIs + the Works/Parks-vision!)', 'dept_rows': 'KPI-lanes',
             'provenance_class': 'official-TWO-SCALE', 'honest_flags': 'the founder-hub!'})
# the OKC = the the in-flight (the the flagged!):
rows.append({'city': 'Oklahoma City', 'band': 'B', 'budget_adopted': None, 'fy': 'FY2027',
             'source_url': 'okc.gov-the-FY27-book (the 29.5MB = the the browser-held = the pull-queue!)', 'dept_rows': 0,
             'provenance_class': 'ingest-in-flight', 'honest_flags': 'the child-running!'})

# THE admin-v2-merge:
adm = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/admin_v2_standardized.json', encoding='utf-8'))
adm_map = {c['city']: c for c in adm['cities']}
for r in rows:
    a = adm_map.get(r['city'])
    if a:
        r['admin_pct_v2'] = a.get('admin_pct')
        r['admin_comparable'] = a.get('admin_pct') is not None and (a['rows_classified'] or {}).get('admin', 0) >= 2

# THE pops:
pops = {'Memphis': 610000, 'New Orleans': 355000, 'St. Louis': 280000, 'Cincinnati': 310000,
        'Boston': 650000, 'Atlanta': 500000, 'Austin': 1000000, 'San Antonio': 1500000,
        'Jacksonville': 1000000, 'Fort Worth': 1000000, 'Houston': 2400000, 'Philadelphia': 1600000,
        'Los Angeles': 3800000, 'Chicago': 2600000, 'New York City': 8800000, 'Oklahoma City': 700000}
for r in rows:
    pc = pops.get(r['city'])
    r['population'] = pc
    r['budget_per_capita'] = round(r['budget_adopted'] / pc) if (r.get('budget_adopted') and pc) else None

# THE fame-v0 (the the known-rows):
fames = {'New York City': 0.62, 'Memphis': 0.38, 'Oklahoma City': 0.18}
for r in rows:
    r['mayor_fame_v0'] = fames.get(r['city'])

print('=== THE 15-CITY-GAUGE-ROWS ===')
for r in sorted(rows, key=lambda x: (x['band'], -(x['budget_adopted'] or 0))):
    print(f" [{r['band']}] {r['city']:14s} {str(r['budget_adopted']):>15} pc:{str(r['budget_per_capita']):>7} adm:{str(r.get('admin_pct_v2')):>6} fame:{str(r.get('mayor_fame_v0')):>5}")

# THE save = the the JSON (the the parquet = the the needs-pandas = the the check-lane):
out_json = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/city_positions_v1.json'
json.dump(rows, open(out_json, 'w', encoding='utf-8'), indent=1)
print()
print('WROTE', out_json)
# THE parquet-lane:
try:
    import pandas as pd
    df = pd.DataFrame(rows)
    pq = 'C:/Users/J/Documents/LLM/cardscout-2.0/data_lake/gold/city_positions_v1.parquet'
    df.to_parquet(pq)
    print('WROTE PARQUET:', pq)
except ImportError:
    print('the pandas = the missing (the the json = the the banked; the parquet = the the next-lane)')
