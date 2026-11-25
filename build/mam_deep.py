import json

deep = {
    'built': '2026-11-21',
    'statline': 'Mayor Zohran Mamdani - NYC',
    'lanes': {
        'DELIVERED [Certain]': [
            {'promise': 'CMP-002 RENT-FREEZE', 'status': 'DELIVERED - the RGB voted the TWO-YEAR-FREEZE for rent-stabilized tenants = ONE-MILLION apartments (AP + many outlets [Certain]) - the FIRST two-year freeze in city history!',
             'score': 'KEPT - the first major campaign promise cleared (the clock = city-controllable = the fastest lane won)',
             'note': 'landlord-math reshaped (coverage class)'}
        ],
        'IN-PROGRESS [Certain]': [
            {'promise': 'CMP-004 GROCERY', 'status': 'La Marqueta East Harlem = first site identified; 5-borough network planned; first opening expected late-2027'},
            {'promise': 'CMP-003 CHILDCARE', 'status': 'PILOT launched in the 100 days (Apr-2026 announce) BUT expansion funding-delay-SNARLED (POLITICO/News: payment delays threatening the rollout; mayor pledged payment reforms Aug-31) = rollout troubled but alive'},
            {'promise': 'CMP-001 FREE-BUSES', 'status': 'IBO cost-estimate published (Jun-2026); preliminary budget SHORTCHANGES MTA (Feb-20 Post); 200M-unpaid-bill critics lane (Post, 4 days ago) - honestly incomplete yet'},
            {'promise': 'POTHOLES/ROADS', 'status': '200,000th pothole filled Sept-17 (nyc.gov official) + 80 crews active'},
            {'promise': 'CMP-006 RIKERS', 'status': 'plan released (2032 clock running)'}
        ],
        'CONTESTED [honest lanes]': [
            'MTA-funding: shortchanges-critics [Post] vs the $20M congestion investment [nyc.gov May-5 World-Asthma-Day]',
            'childcare-money-problem = POLITICO (tax-hikes pitched as pay-for, Aug-4)',
            'MIXED-CITY-SCORECARD: released BY HIS OWN OFFICE (with Adams comparisons) = the self-scrutiny class, notable!'
        ],
        'TRANSPARENCY-ARTIFACTS': [
            'FIRST-100-DAYS website = mayor-released (achievements tracking site = self-scrutiny architecture = THE scoreboard mirror)',
            'mixed-city-scorecard released by his office (with Adams comparisons = honest self-reporting class)'
        ]
    },
    'statline_updates': [
        'CMP-002 = PENDING -> DELIVERED (two-year freeze, one million apartments, first major campaign promise KEPT)',
        'CMP-003 = PENDING -> IN-PROGRESS-TROUBLED (pilot launched + funding snags, both countable)'
    ],
    'honest_notes': ['deep-dive v1 (news sweep, 5 lanes); mayor self-tracks via the 100-days site = the gauge-architecture mirror']
}
json.dump(deep, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/mamdani_deep_dive_v1.json', 'w', encoding='utf-8'), indent=1)
print('WROTE mamdani_deep_dive_v1.json')

tf_path = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/mamdani_term_file_v2.json'
tf = json.load(open(tf_path, encoding='utf-8'))
for p in tf['campaign_promises']:
    if p['id'] == 'CMP-002':
        p['status'] = 'DELIVERED - RGB two-year freeze, one million apartments (first two-year freeze in city history); vote = 2026 cycle'
    if p['id'] == 'CMP-003':
        p['status'] = 'IN-PROGRESS-TROUBLED - pilot launched (Apr-2026) + expansion funding-delay-snarled (mayor pledged payment reforms Aug-31)'
    if p['id'] == 'CMP-001':
        p['status'] = 'IN-PROGRESS - IBO cost estimate (Jun-2026) + preliminary budget shortchanges MTA (Post critics) = not yet'
json.dump(tf, open(tf_path, 'w', encoding='utf-8'), indent=1)
print('term-file updated (CMP-002 = DELIVERED)')
