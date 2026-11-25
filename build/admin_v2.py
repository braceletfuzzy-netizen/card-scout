import json, re

# POLYSCOUT — THE ADMIN-% V2 STANDARDIZATION (the the rule-set = the per-city-chart-mapping!)
# THE RULE-SET (the the published = the the lens-law!): the ADMIN-CATEGORY = the the departments-that-
#   support-governance-WITHOUT-delivering-frontline-services:
#   IN: general-government/executive/council/mayor/finance/treasurer/controller/audit/comptroller/
#       clerk/human-resources/personnel/legal-law-department/procurement-purchasing/
#       technology-IT-when-not-service/communication-public-affairs/elections/risk-management/
#       budget-management-and-budget/assessor (the non-service-side!)
#   OUT: police/fire/EMS/sanitation/streets-transport/water-sewer/parks-recreation (the frontline!)/
#       health/libraries/housing/airport-convention (the enterprise-class = the flagged-separately!)/
#       planning-permits (the debatable = the tagged-debatable!)
#   AMBIGUOUS: the finance-in-the-public-safety-chains, the capital = the excluded-from-the-operating-admin!
#   THE CITY-ADJUSTMENTS (the the per-city-chart-of-accounts = the the named-rows-class):

ADMIN_IN = r'(general government|office of the mayor|mayor\u2019?s office|city council|board of (alder|estimate|supervisors)|finance|treasurer|comptroller|controller|auditor|city clerk|human resources|department of personnel|personnel|law department|department of law|procurement|purchasing|risk management|budget|management and budget|assessor|election|technology|information technology|it department|communications|public affairs|311|non-?departmental|general services|administrative services|executive administration|employee relations|civil service)'
FRONT_LINE = r'(police|sheriff|fire|ems|emergency medical|sanitation|solid waste|street|transport|traffic|water|sewer|wastewater|parks|recreation|library|health department|health and mental|housing|airport|aviation|convention|harbor|port\u2019?s|planning|permits|building inspection|code enforcement|coroner|medical examiner|meals|aging|child|youth|homeless|social services|development services|economic development|sustainability|animal)'
ENTERPRISE = r'(water|sewer|wastewater|airport|aviation|harbor|port\u2019?s|convention|utility|park\u2019?s? revenue|golf|cemetery|transit enterprise)'

def classify(name, total):
    n = (name or '').lower()
    if not n or not isinstance(total, (int, float)):
        return 'skip'
    if re.search(ADMIN_IN, n) and not re.search(FRONT_LINE, n):
        return 'admin'
    if re.search(FRONT_LINE, n):
        return 'frontline'
    return 'other'

results = {'built': '2026-11-22', 'rule_set': {'in': ADMIN_IN[:80], 'out': FRONT_LINE[:80]}, 'cities': []}

# BAND-A:
d = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/band_a_ingestion_v1.json', encoding='utf-8'))
for c in (d if isinstance(d, list) else d.get('cities', [])):
    tot = c.get('budget_total_adopted'); depts = c.get('per_department_totals') or {}
    admin = 0; rows = {'admin': [], 'frontline': [], 'other': []}
    for k, v in depts.items():
        cls = classify(k, v)
        rows[cls if cls != 'skip' else 'other'].append(k)
        if cls == 'admin': admin += v
    results['cities'].append({'city': c.get('city'), 'total': tot, 'admin_v2': admin,
                              'admin_pct': round(admin/tot*100, 1) if tot and admin else None,
                              'rows_classified': {k: len(v) for k, v in rows.items()},
                              'ambiguous_rows': rows['other'][:6]})

# B/C/D:
for line in open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/bands_bcd_ingestion_v1.json', encoding='utf-8'):
    if not line.strip(): continue
    c = json.loads(line)
    tot = c.get('budget_total_adopted'); depts = c.get('per_department_totals') or {}
    admin = 0; rows = {'admin': [], 'frontline': [], 'other': []}
    for k, v in depts.items():
        cls = classify(k, v)
        rows[cls if cls != 'skip' else 'other'].append(k)
        if cls == 'admin': admin += v
    results['cities'].append({'city': c.get('city'), 'total': tot, 'admin_v2': admin,
                              'admin_pct': round(admin/tot*100, 1) if tot and admin else None,
                              'rows_classified': {k: len(v) for k, v in rows.items()},
                              'ambiguous_rows': rows['other'][:6]})

# THE SUMMARY (the impossible-gate = the the v1-vs-v2):
print('=== THE ADMIN-% V2 (the rule-set = the per-city-rows-classified) ===')
for c in results['cities']:
    pct = c.get('admin_pct')
    flag = 'IMPOSSIBLE!' if pct and pct > 60 else ('check' if pct and pct > 35 else 'ok')
    print(f" - {c['city']:14s} admin-v2: {str(pct)+'%':>8} [{flag}] rows: {c['rows_classified']}")
    if c['ambiguous_rows']:
        print(f"      other-rows: {c['ambiguous_rows'][:3]}")

json.dump(results, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/admin_v2_standardized.json', 'w', encoding='utf-8'), indent=1)
print('WROTE admin_v2_standardized.json')
