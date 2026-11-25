import json
import pandas as pd

# POLYSCOUT — THE ADMIN-% GOLD RECOMPUTE (the dept-grain = the the all-10 = the the v3-lane-complete!)
# THE rule-set = the SAME-as-the-v2-admin (the the published-class!):
import re
ADMIN_IN = r'(general government|office of the mayor|mayor\u2019?s office|city council|board of (alder|estimate|supervisors)|finance|treasurer|comptroller|controller|auditor|city clerk|human resources|department of personnel|personnel|law department|department of law|procurement|purchasing|risk management|budget|management and budget|assessor|election|technology|information technology|it department|communications|public affairs|311|non-?departmental|general services|administrative services|executive administration|employee relations|civil service)'
FRONT_LINE = r'(police|sheriff|fire|ems|emergency medical|sanitation|solid waste|street|transport|traffic|water|sewer|wastewater|parks|recreation|library|health department|health and mental|housing|airport|aviation|convention|harbor|port\u2019?s|planning|permits|building inspection|code enforcement|coroner|medical examiner|meals|aging|child|youth|homeless|social services|development services|economic development|sustainability|animal)'
NON_DEPT = r'(non-?dept|general city purposes|fringe benefits|sinking fund|bond redemption|debt service|capital finance|transo|proprietary|finance general|grand total|total-)'

def classify(n):
    n = n.lower()
    if re.search(NON_DEPT, n):
        return 'excluded'
    if re.search(ADMIN_IN, n) and not re.search(FRONT_LINE, n):
        return 'admin'
    if re.search(FRONT_LINE, n):
        return 'frontline'
    return 'other'

# THE the citywide-totals (the the from-the-positions-engine!):
TOTALS = {'Memphis': 1740000000, 'New Orleans': 1600000000, 'St. Louis': 1414518857, 'Cincinnati': 1279450580,
          'Boston': 4942400000, 'Atlanta': 3002085354, 'Austin': 7089913688, 'San Antonio': 4421957497,
          'Jacksonville': 3310000000, 'Fort Worth': 11004000000, 'Houston': 3047770272, 'Philadelphia': 6842559000,
          'Los Angeles': 5638075801, 'Chicago': 18668568460, 'New York City': 11507000000, 'Oklahoma City': 2116632648}

# THE the dept-rows = the the both-batches (the the 10-new = the the dept-grain!):
dept_rows_map = {}
for b in (1, 2):
    p = f'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/dept_depth_batch{b}.jsonl'
    for l in open(p, encoding='utf-8'):
        if l.strip():
            r = json.loads(l)
            dept_rows_map[r['city']] = r.get('per_department_totals') or {}

# THE the per-city-admin-compute:
results = []
for city, depts in dept_rows_map.items():
    admin = 0; excl = 0; counts = {'admin': 0, 'frontline': 0, 'other': 0, 'excluded': 0}
    for k, v in depts.items():
        cls = classify(k)
        counts[cls] = counts.get(cls, 0) + 1
        if cls == 'excluded' or not isinstance(v, (int, float)):
            excl += v if isinstance(v, (int, float)) else 0
        elif cls == 'admin':
            admin += v
    base = admin  # numerator = the admin-countable
    denom = sum(v for k, v in depts.items() if isinstance(v, (int, float)) and classify(k) != 'excluded')
    pct = round(base / denom * 100, 1) if denom else None
    results.append({'city': city, 'n_dept': len(depts), 'admin_pct_v3_gold': pct,
                    'admin_usd': admin, 'basis': 'dept-grain', 'counts': counts})

for r in sorted(results, key=lambda x: -(x['admin_pct_v3_gold'] or 0)):
    print(f" {r['city']:14s} n:{r['n_dept']:5d} admin-gold: {str(r['admin_pct_v3_gold'])+'%':>7} ({r['admin_usd']:>14,})")

json.dump(results, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/admin_v3_gold.json', 'w', encoding='utf-8'), indent=1)
print()
print('WROTE admin_v3_gold.json')
