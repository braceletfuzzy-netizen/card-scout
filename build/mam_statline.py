import json
from datetime import date

# POLYSCOUT #4 — THE MAYOR-ROW v1: the first career-statline (the Mamdani promise-ledger seed)
# EVERY promise = the pre-registered (the claimed + the clock) per SPINOFF-005; the delivery = scored against the record, never the goodness.

row = {
    'statline': 'Mayor Zohran Mamdani — New York City',
    'term': {'took_office': '2026-01-01', 'term_end': '2029-12-31'},
    'built': '2026-11-21',
    'laws': [
        'every promise = pre-registered at claim-date with its own falsifier-clock',
        'the unavailable = null + note, never fabricated',
        'the score = promise-vs-delivery (the objective claims), never the goodness',
        'the deadline-changes = logged in the delivery-risk column, not editorialized'
    ],
    'promises': [
        {
            'id': 'MMD-001',
            'promise': 'Close Rikers Island; replace with 4 borough-based jails near communities (family/court access) + mental-health facilities as first-response',
            'claim_date': '2026-11-20',
            'claim_source': 'the plan-release (the Friday), the news-verified [Certain]: the first-comprehensive-plan',
            'delivery_deadline_stated': 2032,
            'deadline_note': 'the original 2027 deadline delayed to 2032 — the delay = the LOGGED in the delivery-risk column (the countable fact, the first entry)',
            'clock': 'six-year falsifier-window',
            'delivery_evidence': None,  # null by law
            'score': 'PENDING',
            'category_tag': 'CURE-side (the mental-health-first-response = the founder-classified)'
        },
        {
            'id': 'MMD-002',
            'promise': 'Crime DOWN ~40% under the current Task-Force surge (the mayor\u0027s SOTC claim)',
            'claim_date': '2026-11-20 (the SOTC)',
            'claim_source': 'the State-of-the-City (the mayor\u0027s-own-number; the not-the machine-verified)',
            'clock': 'the suppression-vs-prevention referee: the monthly NYPD-data = the returns-or-sustains test',
            'delivery_evidence': None,
            'score': 'PENDING — the 12-month window decides (the choice-set vs the deterrence weights, per SS003.11)',
            'category_tag': 'DETERRENCE-lane (the surge = the treatment-class)'
        },
        {
            'id': 'MMD-003',
            'promise': 'Housing strategy: growth + affordability (the SOTC pillar)',
            'claim_date': '2026-11-20 (the SOTC)',
            'claim_source': 'the mayor\u0027s-address',
            'delivery_denominator': 'the city-shortage = the ~28,000-units (the 2026-State-of-Memphis-Housing-report analog for NYC: pending the NYC-specific figure — null by honest law)',
            'clock': 'the permits-built + the affordable-completions = the annual-scored rows',
            'delivery_evidence': None,
            'score': 'PENDING',
            'category_tag': 'CURE-side (the supply)'
        }
    ],
    'fame_composite': {
        'note': 'the hand-set v0 per the gauge-laws; the formal-fit = the calibration-lane',
        'value': 0.62,
        'band': '[ARRIVED-class $100-300]'
    },
    'notes': [
        'the first career-statline in the PolyScout ledger — the SPINOFF-005 shape made tangible',
        'the Rikers-delay = the honest-included (the not-hidden: the gauge records the deadline-slip as data)',
        'the founder-intuition pre-registered separately: [FOUNDER-INTUITION] — \u002cawesome\u0027 — scores via these rows\u0029 outcomes by 2032'
    ]
}

with open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/mamdani_statline_v1.json', 'w', encoding='utf-8') as f:
    json.dump(row, f, indent=1)
print('WROTE mamdani_statline_v1.json — the first career-statline')
