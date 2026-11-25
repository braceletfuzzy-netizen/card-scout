import json

# POLYSCOUT — THE ACCOMPLISHMENT-LEDGER v1 (the founder-named-lanes = the verified) + the term-length
update = {
    'built': '2026-11-21',
    'term_length_verified': {
        'answer': 'the NYC mayor = the FOUR-YEAR terms, the limited-to-TWO-consecutive (the may-run-again-after-a-four-year-break)',
        'mamdani': 'the took-office-Jan-1-2026 = the first-term-runs-through-2029 [Certain]'
    },
    'accomplishments_in_progress': [
        {
            'promise': 'CMP-004 (the city-owned-grocery-stores)',
            'status': 'STARTED — the momentum-real [Certain]',
            'evidence': [
                'the FIRST-SITE = the identified: La Marqueta, East Harlem (the announced ~May-2026 + the re-confirmed [the 9-hours-ago-class news: the unveils-first-site])',
                'the NETWORK = the planned: one-municipal-grocery-store-per-each-of-the-FIVE-boroughs (the mayor\u0027s-own-statement)',
                'the first-store = the expected-to-open-late-2027 (the April-2026-report-class; the 8-figure-taxpayer-sum = the critics\u0027-cost-tag [the noted-not-scored])'
            ],
            'score_logic': 'the promise = the network-of-five = the delivered-when-the-stores-OPEN (the not-announced!) — the clock = the late-2027 = the first-store-opening = the first-scoreable-ticket',
            'honest_column': 'the cost-per-store = the countable (the 8-figure-class = the critics\u0027-number = the needs-the official-figure = the null-until-sourced)'
        },
        {
            'promise': 'THE PUBLIC-WORKS/ROADS (the not-a-formal-campaign-promise = the GOVERNANCE-IMPLEMENTATION lane = the the founder\u0027s-named-big-deal)',
            'status': 'ACTIVE-AND-QUANTIFIED [Certain]',
            'evidence': [
                'the NYC-DOT = the 200,000th-pothole-filled of-2026 (the Sept-17-2026 = the mayor-repaired-it-personally = the milestone-event; the nyc.gov = the official-page: the street-repair-effort-accelerated)',
                'the 80-crews-mobilized = the 7,200-potholes (the recent-video-claim [2-days-old])',
                'the winter-mitigation = the DOT-measures (the mitigate-formation = the per-the Sept-report)'
            ],
            'score_logic': 'the pothole-count = the Tier-1-countable = the annual-rows (the FY2025-Adams-baseline = the pending-source → the Mamdani-delta = the scoreable); the 200k-in-9-months = the pace-figure-class'
        }
    ],
    'laws_held': [
        'the CMP-004 = the scored-on-OPENINGS not-announcements (the the site-identification = the momentum, the not-the delivery)',
        'the potholes = the countable = the annual-vs-the-baseline (the the founder-named-big-deal = the the gauge-native!)',
        'the critics\u0027-numbers = the noted-not-adopted (the the official-figures = the null-until-sourced)'
    ]
}

import json as j
# THE merge-into-the-term-file:
tf_path = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/mamdani_term_file_v2.json'
tf = j.load(open(tf_path, encoding='utf-8'))
tf['term_length_verified'] = update['term_length_verified']
tf['accomplishments_in_progress'] = update['accomplishments_in_progress']
# THE CMP-004-live-update:
for p in tf['campaign_promises']:
    if p['id'] == 'CMP-004':
        p['progress'] = 'STARTED: the first-site = La-Marqueta-East-Harlem (the identified-May-2026); the network = one-store-per-the-five-boroughs; the first-opening = the expected-late-2027'
with open(tf_path, 'w', encoding='utf-8') as f:
    j.dump(tf, f, indent=1)
print('the term-file = updated (the term-length + the accomplishments + the CMP-004-progress)')
