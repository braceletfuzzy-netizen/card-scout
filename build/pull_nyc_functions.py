import json, re
import requests
from collections import defaultdict

# THE NYC-AGENCY-FUNCTION-PULL: the Socrata = the "Agency Spending by Budget Function" (gzfs-3h4m) = the free-API (the no-keys).
# THE GOAL: the FY2026 = the per-agency + per-budget-function $ = the fills-the-7-bucket-mapping.
Q = {'User-Agent': 'Mozilla/5.0'}
base = 'https://data.cityofnewyork.us/resource/gzfs-3h4m.json'

def pull(offset=0, limit=50000):
    r = requests.get(base, headers=Q, timeout=90)  # plain = returns 1000/page
    return r.json()

# page through (the Socrata = the 1000-row-pages plain):
all_rows = []
offset = 0
while True:
    r = requests.get(f'{base}?$offset={offset}&$limit=1000', headers=Q, timeout=90)
    page = r.json()
    if not isinstance(page, list) or not page:
        break
    all_rows.extend(page)
    offset += 1000
    if offset >= 200000:
        break
print('total-rows-pulled:', len(all_rows))

# the FY2026-filter (the first_plan_fiscal_year = "2026"):
fy26 = [r for r in all_rows if str(r.get('first_plan_fiscal_year')) == '2026']
print('FY2026-rows:', len(fy26))

# the per-budget_function-totals (the $ = the plan_amount_year_1 = the $-thousands per the NYC-budget-convention):
by_function = defaultdict(float)
by_function_agencies = defaultdict(set)
for r in fy26:
    fn = (r.get('budget_function') or 'UNSPECIFIED').strip()
    amt = re.sub(r'[^0-9.\\-]', '', str(r.get('plan_amount_year_1') or '0'))
    try:
        by_function[fn] += float(amt)
    except ValueError:
        pass
    by_function_agencies[fn].add(r.get('agency_name'))

print()
print('=== THE BUDGET-FUNCTIONS (the FY2026, the $-thousands-class) ===')
for fn, amt in sorted(by_function.items(), key=lambda x: -x[1]):
    n_agencies = len(by_function_agencies[fn])
    print(f'{fn[:44]:46s} ${amt:>14,.0f}  ({n_agencies} agencies)')

json.dump({
    'pulled_rows': len(all_rows),
    'fy2026_rows': len(fy26),
    'by_function_thousands': {k: v for k, v in sorted(by_function.items(), key=lambda x: -x[1])},
    'publication_date_range': sorted({r.get('publication_date') for r in fy26})[-3:],
}, open('nyc_agency_function_fy2026.json', 'w', encoding='utf-8'), indent=1)
print()
print('WROTE nyc_agency_function_fy2026.json')
