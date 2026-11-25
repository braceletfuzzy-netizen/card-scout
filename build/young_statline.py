import json

# POLYSCOUT — THE MEMPHIS MAYOR STATLINE v1: Paul Young (the second-statline = the pair-complete!)
young = {
    'built': '2026-11-21',
    'statline': 'Mayor Paul Young — Memphis, TN',
    'term': {'took_office': '2024-01-01 [Certain — the 2023-race = the Jan-2024-takeover, the Memphis-mayoral-cycle]', 'term_end': '2027-12-31', 'note': 'the Memphis-mayors = the four-year-terms (the state-law-class); the founder-dissent = the pre-registered: [FOUNDER-INTUITION] "not-too-impressed-with-Mayor-Young-or-his-policies" = the falsifiable-by-these-rows'},
    'campaign_promises': [
        {'id': 'YM-001', 'promise': ' PUBLIC-SAFETY-FIRST (the 2023-campaign = the crime-the-foremost-priority: the enhance-the-police/the violence-reduction)', 'category': 'DETERRENCE-lane', 'clock': 'the annual-crime-rows', 'status': 'PENDING-scored-annually'},
        {'id': 'YM-002', 'promise': 'THE DEVELOPMENT + the youth-opportunities (the the FOX13-priorities-class: the crime/the-development/the opportunities-for-the-young)', 'category': 'CURE-side/skill', 'clock': 'the youth-employment-rows = the pending-source', 'status': 'PENDING'},
        {'id': 'YM-003', 'promise': 'THE CLEAN-CITY (the 1940-51 = the cleanest-city-callback: the blight/the dumping = the issues-page-framing)', 'category': 'CURE-side/quality-of-life', 'clock': 'the blight-rows = the 100-Demo-campaign = the countable', 'status': 'PENDING'}
    ],
    'sotc_pillars': ['public safety', 'housing', 'youth', 'culture'],
    'claims_in_news': [
        {'claim': 'the overall-crime = the DOWN-41%-IN-TWO-YEARS', 'source': 'the mayor\u0027s-own (the Yahoo-hed)', 'status': 'PENDING-verify [the the founder\u0027s-lived-check = the the referee!]'},
        {'claim': 'the serious-crime = the 25-YEAR-LOW in-2025', 'source': 'the mayor-cited-data', 'status': 'PENDING-verify'},
        {'claim': 'the no-exit-timeline for-the-Memphis-Safe-Task-Force (the as-homicides-move)', 'source': 'the mayor-direct', 'status': 'the honest-column: the task-force = the federal-multi-agency = the attribution-complexity!'}
    ],
    'attribution_complexities': [
        'THE CRITICAL-HONEST-FLAG: the Memphis-Safe-Task-Force = the FEDERAL-operation (the the 12,000-arrests/2,100-guns = the the NTF-lane!) — the crime-delta = the MULTI-actor (the federal + the state + the city) = THE ATTRIBUTION-QUESTION = the the gauge\u0027s-hardest-class!',
        'the mayor\u0027s-claims = the the credit-claim-vs-the-attribution = the the scorable-CONTEXT (the claim-the-41% = the countable-claim; the who-delivered = the separate-column!)'
    ],
    'yield_rows': [
        {'row': 'the crime-rates', 'source': 'the city-own-KPI-pages (the the FY26-budget-book = the police-16-KPIs = the DONE-today!)', 'note': 'the violent-crime-rate = the 1,589/100k = the FY25-actual = the -6.3% vs-the -1%-goal = the OUTPERFORMANCE [Certain]'},
        {'row': 'the clearance-rates', 'source': 'the same (the violent = the 23.9%-vs-the-33%-goal = the MISS [Certain])', 'note': 'the p-caught = the the crime-price-lane = the the gauge-native'},
        {'row': 'the calls-answered-20s', 'source': 'the 94.3% = the met [Certain]'},
        {'row': 'the academy-completion', 'source': 'the 79%-vs-the-83%-goal = the MISS [Certain]'},
        {'row': 'the turnover', 'source': 'the 4%-vs-the-5% = the BETTER-than-the-goal [Certain]'}
    ],
    'scope_note': 'the KPI-tables = the SELF-REPORTED = the Memphis = the the publishes-metrics-city-class (the NOT-an-obfuscation-signature on-the-safety-lane!); the Fire-empty-page = the the signature-flag-still-on',
    'honest_flags': [
        'the founder-dissent = the pre-registered (the the not-impressed = the scores-via-these-rows — the the same-falsifier-discipline as-the-Mamdani-claim!)',
        'the attribution = the federal-task-force-contaminated (the the Young-gets-no-full-credit = the the honest-column!)',
        'the 41%-claim = the the mayor\u0027s-own-number = the the verify-pending (the the UCR/TBI-state-data = the the cross-check-rail!)'
    ]
}
import json
json.dump(young, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/paul_young_statline_v1.json', 'w', encoding='utf-8'), indent=1)
print('WROTE paul_young_statline_v1.json')
