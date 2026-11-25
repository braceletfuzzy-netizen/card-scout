import json

# POLYSCOUT — THE MAMDANI TERM-FILE v2: the campaign-promise-list (the pre-MMD-001/002/003 = the the-platform-promises = the pre-registered) + the year-prior-baselines (the FY2025 = the Adams-era = the scoring-baseline)
term_file = {
    'statline': 'Mayor Zohran Mamdani — New York City',
    'term': {'took_office': '2026-01-01', 'term_end': '2029-12-31'},
    'built': '2026-11-21',
    'office_duration_note': 'the founder-recalled-class: the in-office ~10-11-months at-build (the Jan-2026-takeover = the per the term-row); the term = the 4-year (the 2026-2029)',
    'campaign_promises': [
        {'id': 'CMP-001', 'promise': 'Fare-free buses (the fast-and-free-class: the bus-service-speed-up + the fare-elimination for-buses)', 'category': 'CURE-side/transit', 'clock': 'the MTA-funding = the state-partner-dependent (the note: the buses = the MTA-controlled = the city-lane = the limited [the honest-scope-flag])', 'status': 'PENDING'},
        {'id': 'CMP-002', 'promise': 'Rent freeze for rent-stabilized tenants (the every-year-of-the-term)', 'category': 'CURE-side/housing', 'clock': 'the Rent-Guidelines-Board (RGB = the annual-vote = the mayoral-appointees = the city-controllable!)', 'status': 'PENDING'},
        {'id': 'CMP-003', 'promise': 'Universal no-cost child care', 'category': 'CURE-side/families', 'clock': 'the multi-year-phase (the budget-scale = the billions-class)', 'status': 'PENDING'},
        {'id': 'CMP-004', 'promise': 'City-owned grocery stores (the municipal-groceries = the food-affordability)', 'category': 'CURE-side/food', 'clock': 'the pilot-stores = the term-lane', 'status': 'PENDING'},
        {'id': 'CMP-005', 'promise': 'Minimum wage $30/hour (the city-call = the state-action-needed [the honest-scope-flag])', 'category': 'CURE-side/wages', 'clock': 'the state-legislature-dependent', 'status': 'PENDING'},
        {'id': 'CMP-006', 'promise': 'The Rikers-closure (the MMD-001 = the already-registered)', 'category': 'CURE-side/justice', 'clock': '2032', 'status': 'PENDING'},
        {'id': 'CMP-007', 'promise': 'Crime-down-40% (the MMD-002 = the already-registered)', 'category': 'DETERRENCE-lane', 'clock': 'the 12-month referee', 'status': 'PENDING'},
        {'id': 'CMP-008', 'promise': 'The housing-strategy (the MMD-003 = the already-registered)', 'category': 'CURE-side/housing', 'clock': 'annual', 'status': 'PENDING'}
    ],
    'year_prior_baselines': {
        'note': 'the FY2025 = the Adams-era-final-year = the scoring-baseline (the service-yield vs-the-YoY = the delta-scoring-lane)',
        'budget_total_all_funds_fy2025': 119791000000,
        'budget_total_all_funds_fy2026': 115065000000,
        'personal_service': {'fy2025': 57232000000, 'fy2026': 59657000000},
        'otps': {'fy2025': 58488000000, 'fy2026': 50051000000},
        'debt_service': {'fy2025': 7654000000, 'fy2026': 8741000000},
        'nypd': {'fy2025_plan': 7003334000, 'fy2026_adopted': 6276536000, 'delta_pct': -10.4},
        'source': 'the OMB sum5-25.pdf (the five-year-financial-plan-table, the p5-class)'
    },
    'service_yield_baselines_fy2025': {
        'note': 'the prior-year service-yields = the FY2025-adams-era = the baseline-rows (the gauge-delta = the Mamdani-yields vs-these)',
        'crime': 'the Part-I-crime = the Adams-era trajectory = the NYC-specific-figure pending (the null by-law until-sourced)',
        'existing_rows': 'the NYPD-BFA-rows = the FY2025-plan + the FY2026-adopted = the budget-side-done; the yield-side = the queue'
    },
    'laws': [
        'every promise = the pre-registered at-claim-date',
        'the scope-flags = the banked (the CMP-001 = the MTA-dependent; the CMP-005 = the state-dependent = the honest-scope-columns!)',
        'the score = promise-vs-delivery, never-the-goodness',
        'the baseline-deltas = the FY2025-vs-the-Mamdani-years = the service-yield-scoring-lane'
    ]
}

with open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/mamdani_term_file_v2.json', 'w', encoding='utf-8') as f:
    json.dump(term_file, f, indent=1)
print('WROTE mamdani_term_file_v2.json — the campaign-promises + the baselines')
