import json

# POLYSCOUT — THE METRIC-TAXONOMY v1 (the founder's question: "how-do-we-find-more-metrics-for-the-scoring-attribution")
taxonomy = {
    'built': '2026-11-21',
    'principle': 'the master-class-headers = the scale-across-the-board (the transparency/the-governance-yield/etc = the founder-ratified-shape)',
    'master_classes': [
        {'class': 'GOVERNANCE YIELD', 'definition': 'the service-countables-per-dollar (the potholes/the calls-answered/the lanes-miles/the permits-days)', 'sources': ['the city-KPI-pages', 'the PMMR-class-reports', 'the federal-mandates']},
        {'class': 'TRANSPARENCY', 'definition': 'the what-the-city-releases-vs-withholds (the records-pages/the portals/the voluntary-vs-forced)', 'sources': ['the FOIA-volumes', 'the court-settlements', 'the portal-launches', 'the scorecard-releases']},
        {'class': 'INSTITUTION BUILDING', 'definition': 'the new-permanent-bodies (the grocery-network/the portals/the offices)', 'sources': ['the announcements + the opening-verifications (the score-on-open-not-announce!)']},
        {'class': 'FISCAL DISCIPLINE', 'definition': 'the budget-vs-actual + the one-time-fills + the deferred-liabilities', 'sources': ['the budget-books', 'the comptroller/audits', 'the bond-ratings']},
        {'class': 'OBFUSCATION SIGNATURE', 'definition': 'the how-hard-they-make-it-to-check (the THE founder-named-lane!)', 'sources': ['the missing-KPI-pages (the Memphis-fire = caught-today!)', 'the metrics-dropped (the prior-had-it-now-gone)', 'the units-shuffled', 'the Friday-dumps', 'the FOIA-denial-rates']}
    ],
    'discovery_methods': [
        {'method': 'THE SELF-REPORT-MINE', 'description': 'every-city = the budget-book-KPI-pages + the annual-perf-reports (the Memphis-model = the proven-today!)', 'effort': 'low', 'yield': 'high'},
        {'method': 'THE MANDATED-REPORTS-LANE', 'description': 'the federal/state-required-filings = the UCR-crime/the EMS/ACA-code-inspections = the standardized-across-cities (the comparable-by-construction!)', 'effort': 'low', 'yield': 'high'},
        {'method': 'THE MILESTONE-NEWS-SCAN', 'description': 'the 200,000th-pothole-class = the milestone-announcements = the machine-scan (the our twitter-pipeline = the ready-rail!)', 'effort': 'low', 'yield': 'medium'},
        {'method': 'THE COURT/AUDIT-MINE', 'description': 'the settlements + the comptroller-findings + the what-was-released-only-by-court-order (the 9/11-model!)', 'effort': 'medium', 'yield': 'high'},
        {'method': 'THE OBFUSCATION-GAP-CHECK', 'description': 'the peer-city-A-publishes-X = the does-the-city-B? THE missing = the scoreable (the wayback-machine = the the archaeology!)', 'effort': 'medium', 'yield': 'unique'},
        {'method': 'THE FOIA-METER (the build-class)', 'description': 'the request-volumes + the denial-rates + the days-to-comply = the THE transparency-meter (the city-published-or-recordable)', 'effort': 'build', 'yield': 'unique'},
        {'method': 'THE FOUNDER-EYES-LANE', 'description': 'the lived-reality = the the ground-truth-validation (the the Katy-class + the the Memphis-hub-design = the built-in!)', 'effort': 'zero', 'yield': 'the irreplaceable'}
    ],
    'laws': [
        'the score-on-the-controls-scope (the never-penalize-what-not-control)',
        'the score-on-openings-not-announcements',
        'the voluntary-vs-forced = the distinguishable-column (the the 9/11-model)',
        'the MISSING = the data-too (the the Fire-empty-KPI-page = the caught-today = the the absence-is-a-signal!)'
    ]
}
import json
json.dump(taxonomy, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/metric_taxonomy_v1.json', 'w', encoding='utf-8'), indent=1)
print('WROTE metric_taxonomy_v1.json')
