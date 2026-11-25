import json

# POLYSCOUT #2 — THE MEMPHIS-DIVISION-OUTS v1: the KPI-page (the p362 = the GOLD = the Tier-1 rows = the city's-own-KPIs!)
kpi = {
    'city': 'Memphis',
    'source': 'FY26 Adopted Budget Book, Police Services KPI page (p.360-363 class, the Key-Performance-Indicator page)',
    'url': 'https://www.memphistn.gov/wp-content/uploads/2025/10/FY26-Adopted-Budget-Book.pdf',
    'built': '2026-11-21',
    'note': 'the budget-book = the carries-the KPI-tables = the Tier-1 countables SOURCE-natively (the next-divisions = the fire/library/parks/works = the same-pattern, the next-pass)',
    'kpis': [
        {'metric': '% police recruits completed academy', 'fy24_actual': '81%', 'fy25_goal': '83%', 'fy25_actual': '79%', 'fy26_goal': '85%'},
        {'metric': 'Turnover (% sworn officers voluntarily left)', 'fy24_actual': '3%', 'fy25_goal': '5%', 'fy25_actual': '4%', 'fy26_goal': '4%'},
        {'metric': '% exit interviews completed', 'fy24_actual': '84%', 'fy25_goal': '95%', 'fy25_actual': '87%', 'fy26_goal': '95%'},
        {'metric': '% incoming calls answered within 20 seconds', 'fy24_actual': '94%', 'fy25_goal': '94%', 'fy25_actual': '94.3%', 'fy26_goal': '95%'},
        {'metric': '% patrol officers trained as fingerprint technicians', 'fy24_actual': '81%', 'fy25_goal': '80%', 'fy25_actual': '81%', 'fy26_goal': '80%'},
        {'metric': 'Crime Stoppers tips resulting in arrests (#)', 'fy24_actual': 316, 'fy25_goal': 320, 'fy25_actual': 234, 'fy26_goal': 350},
        {'metric': 'Part I violent crime rate (per 100k)', 'fy24_actual': 1696, 'fy25_goal': '-1%', 'fy25_actual': 1589, 'fy26_goal': '-10%'},
        {'metric': 'Part I violent crime incidents (#)', 'fy24_actual': 10740, 'fy25_goal': '-1%', 'fy25_actual': 9833, 'fy26_goal': '-10%'},
        {'metric': 'Part I property crime rate (per 100k)', 'fy24_actual': 7715, 'fy25_goal': '-3%', 'fy25_actual': 6162, 'fy26_goal': '-10%'},
        {'metric': 'Part I property crime incidents (#)', 'fy24_actual': 48841, 'fy25_goal': '-3%', 'fy25_actual': 38122, 'fy26_goal': '-10%'},
        {'metric': 'Total Part I crime incidents (#)', 'fy24_actual': 59581, 'fy25_goal': '-2%', 'fy25_actual': 47957, 'fy26_goal': '-10%'},
        {'metric': 'Arrests of youth gun offenders age 16-24 (#)', 'fy24_actual': 1122, 'fy25_goal': 1583, 'fy25_actual': 1249, 'fy26_goal': '-10%'},
        {'metric': 'City-wide gun recoveries (#)', 'fy24_actual': 4625, 'fy25_goal': 5518, 'fy25_actual': 4680, 'fy26_goal': 5518},
        {'metric': 'Clearance rate violent Blue Crush crimes', 'fy24_actual': '21%', 'fy25_goal': '33%', 'fy25_actual': '23.9%', 'fy26_goal': '38%'},
        {'metric': 'Clearance rate property Blue Crush crimes', 'fy24_actual': '6%', 'fy25_goal': '12%', 'fy25_actual': '7.43%', 'fy26_goal': '20%'},
        {'metric': 'C.O.P.S community programs conducted (#)', 'fy24_actual': 303, 'fy25_goal': 330, 'fy25_actual': 374, 'fy26_goal': 700}
    ],
    'cross-reads': [
        'the FY25-actuals-vs-goals = the mixed-honest-class (the recruits-missed 79-vs-83; the calls-met 94.3; the Crime-Stoppers-missed 234-vs-320; the crime-rate = the BEAT-the-goal: the -6.3%-actual vs-the -1%-goal!)',
        'THE clearance-rates = the Tier-1-countables = the gauge-native (the p = the caught-probability = the SS003.11-crime-price-lane LIVE: the violent-23.9% vs-the-goal-33% = the honest-gap-col!)',
        'the violent-crime-rate = the 1589-per-100k = the city\u0027s-own-number = the mayors-40%-down-claim = the scoreable-context'
    ]
}
with open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/memphis_kpis_v1.json', 'w', encoding='utf-8') as f:
    json.dump(kpi, f, indent=1)
print('WROTE memphis_kpis_v1.json — the Tier-1s = the found (the city\u0027s-own-KPI-pages!)')
