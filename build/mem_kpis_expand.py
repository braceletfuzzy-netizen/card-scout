import json

# POLYSCOUT #B — THE MEMPHIS-KPI-EXPANSION v1: the Fire = the narrative-based (the KPI-table = the header-page-empty = the Fire's-KPI-table = the not-in-the-BFA-format [the honest-null!]) + the narrative-outputs = the countables-embedded:
fire = {
    'city': 'Memphis',
    'division': 'Fire Services',
    'source': 'FY26 Adopted Budget Book p.295-301',
    'note': 'the Fire = the KPI-header-page-empty [p.298 = the 92-chars] = the table-format = the NOT-carried for-this-division (the honest-null!) — the outputs = the narrative-embedded [p.296] = the countables-pulled:',
    'service_out_v1': [
        {'metric': 'citizens reached via fire-education/outreach', 'value': 183053, 'period': 'FY25'},
        {'metric': 'fire-communications calls-for-service', 'value': 304075, 'period': 'FY25'},
        {'metric': 'incidents', 'value': 163948, 'period': 'FY25'},
        {'metric': 'responses', 'value': 366641, 'period': 'FY25'},
        {'metric': '% emergency-911-calls answered within-20-seconds', 'value': '93%', 'period': 'FY24'},
        {'metric': 'new firefighters hired', 'value': 184, 'note': 'from-24-states, 119-with-NR-EMS-certs'}
    ],
    'comparative': 'the Police = the calls-answered-within-20s = 94.3% (the FY25-actual) vs-the Fire = the 93% (the FY24) — the same-metric-class across-the-safety-divisions!'
}
# THE LIBRARY-KPIs = the p335-341 + the Parks = the p349-355 + the Works = the p371-377 (the scan = the pattern-check):
import pymupdf as fitz
doc = fitz.open('C:/Users/J/AppData/Local/Temp/memphis_fy26_adopted.pdf')
found = {}
for p, div in ((334, 'Library Services'), (348, 'Memphis Parks'), (370, 'Public Works')):
    # the KPI-table = the search-near (the +2):
    for pp in (p, p+1, p+2):
        t = doc[pp].get_text()
        if 'FY24' in t or 'FY 2024' in t:
            found[div] = pp
            break
print('the KPI-tables-found:', found)
# the pull-each:
divs = {}
for div, pp in found.items():
    t = doc[pp].get_text()
    divs[div] = {'page': pp, 'raw': t[:2200]}

out = {'city': 'Memphis', 'built': '2026-11-21', 'fire': fire, 'kpi_tables_found': {k: v['page'] for k, v in divs.items()}, 'raw_tables': {k: v['raw'] for k, v in divs.items()}}
json.dump(out, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/memphis_kpis_expanded_v1.json', 'w', encoding='utf-8'), indent=1)
print('WROTE memphis_kpis_expanded_v1.json')
for div, pp in found.items():
    print(f'--- {div} (p{pp}):')
    print(divs[div]['raw'][:600])
