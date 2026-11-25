import json, collections, math, datetime

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
stats = json.load(open(B + '_test2_stats_bank.json'))
bank = json.load(open(B + '_test2_merge_bank.json'))

panel = stats['panel']
care_keys = {k for k, v in panel.items() if v['care_usd_total'] is not None}
bk_keys = {k for k, v in panel.items() if (v['bookings_total'] or 0) is not None and v['bookings_total'] is not None}
mur_keys = {k for k, v in panel.items() if v['murders'] is not None}
pop_keys = {k for k, v in panel.items() if v['population'] is not None}
all4 = care_keys & bk_keys & mur_keys & pop_keys

coverage = {
    'care_book_rows': {
        'city_component_annual_v1.jsonl rows_in': 2509,
        'city-years_out': len(care_keys),
        'cities': sorted({k.split('|')[0] for k in care_keys}),
    },
    'bookings_rows_in': {
        'bookings_series_v1.jsonl city-years': len(bank['bookings_series']),
        'nulls_carried': 1,
        'bookings_facility_v1.jsonl facility-years': 1965,
        'NYC facility years usable': len(bank['fac_nyc']),
    },
    'murder_city_years': len(bank['murders']),
    'panel_care+bookings+murders+pops_full_quad': len(all4),
    'panel_care+bookings+murders': len(care_keys & bk_keys & mur_keys),
    'panel_care+murders': len(care_keys & mur_keys),
    'panel_care+bookings': len(care_keys & bk_keys),
    'panel_rows_total': len(panel),
    'test_pairs_by_lag': {
        'A_care_to_bookings': {lag: stats['testA_care2bookings_rate']['pooled'][lag]['n'] for lag in map(str, range(5))},
        'B_care_to_murders': {lag: stats['testB_care2murders_rate']['pooled'][lag]['n'] for lag in map(str, range(5))},
        'C_bookings_to_murders': {lag: stats['testC_bookings2murders_rate']['pooled'][lag]['n'] for lag in map(str, range(5))},
    },
}

hdr = {
    'artifact': 'care_bookings_ordering_v1',
    'built_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'frame': 'TEST-2 THE CARE->BOOKINGS ORDERING TEST - the two-book frame completed: '
             'Book-1 (care) = city_component_annual_v1.jsonl component-USD; '
             'Book-2 (bookings) = bookings_series_v1.jsonl (UCR-arrest intake proxy 2015-2024, 9 cities) '
             '+ bookings_facility_v1.jsonl (facility grain, NYC DOC discharges/admissions usable); '
             'outcome = murders_all_v1.json; denominator = layered pops (PEP vintage-2025 SUMLEV-162 / '
             'vintage-2019 SUMLEV-162 / decennial-anchor series).',
    'question': 'does care-spending lead the bookings channel (Simes-and-Jahn proximate-series frame) '
                'and in what ORDER do care -> bookings -> murders line up by lag?',
    'laws': [
        'check-us-not-kill-us reproducibility header',
        'non-reporting != zero (honest-null, routes carried)',
        'no fabricated years (lag pairs only where BOTH years exist in sources)',
        'split-if-accounted-only (basis + partial-null flags carried per row)',
        'lag-pair n carried with every r/t (thin-n flagged, never hidden)',
    ],
    'conventions': {
        'care_usd_total': 'city_component_annual_v1 units: source rows with subcomponent=="total" summed when present '
                          '(dedup law - never sums total + PS/OTPS breakouts); else sum of non-total rows; '
                          'not_applicable rows (e.g. Cincinnati county-levy libraries) contribute honest-null, '
                          'counted in care_partial_nulls',
        'bookings_total': 'bookings_series_v1 city-year arrests = intake/booking volume PROXY '
                          '(not jail-facility admissions) - measure label carried per panel row',
        'murders': 'murders_all_v1 (max-of-source dedupe per _merge_murders.py conventions)',
        'population': 'priority: population_series_v1 (decennial anchors) > populations_wide_v1 (PEP v2019) > '
                      'populations_cities_v2 (PEP v2025) > triple_slider_v6d fallback (labeled inline)',
        'per_capita': 'None-propagating: population None -> per-capita None (never zero-substituted)',
        'corr_report': 'r + t + n per lag; per-city tables require >=3 pairs; pooled pools WITHIN-CITY-DEMEANED '
                       'pairs (fixed-effect lens) after dropping cities with <3 pairs at that lag',
    },
}

gaps = {
    'Denver': 'care book 2021-2023 only; no bookings (CDE agency route not banked for Denver); care+murder+pop '
              'triple = 0 rows -> Denver rides raw lanes only, honest',
    'care_years_beyond_bookings': 'care book runs to 2026-2028 (budget/forecast-basis rows); bookings series ends 2024 - '
                                  'lag pairs beyond 2024 exist only for the murder lane',
    'bookings_2024_NewOrleans': 'bookings_total = honest-null (NOPD non-reporting), carried null, never zero',
    'nyc_murders_gap': 'NYC murders exist 1998-2001 + 2019-2024 only (DCJS-verified + 2020s pull); interior '
                       '2002-2018 honest-gap',
    'facility_lane_non_NYC': 'bookings_facility_v1 non-NYC panel rows (Detroit/Harris/Shelby/Orleans/StLouisMetro: '
                             '65/78 rows) are honest-null facility counts (routes-tried documented in source header) - '
                             'facility lane = NYC-only honest; NY-statewide county jails = different state lane, not merged',
    'nyc_facility_pre2013': 'NYC DOC admitted-coverage starts ~2013 per source flags; facility deep-lane uses the '
                            'admitted rows 2013-2025',
    'nyc_care_book_seam': 'NYC IBO agency-expenditure seam: HRA rows are 0 post-DSS-merge (DSS/HRA consolidation '
                          'printed as one agency) - carried as printed, flagged',
    'thin_tail': 't+3/t+4 lag pairs thin (test A: n=11/7) - the negative tail values are thin-n-flagged, '
                 'carried as pattern-leads, NOT verdicts',
}

flags = [
    'NYC test-B per-city r=-0.994 (n=9) = MONOTONE-TREND ARTIFACT class: NYC care-USD grows smoothly 2019-2025 while '
    'murders fall 2020-2024 - the near-perfect r is the trend artifact, not a causal estimate [flag-not-verdict]',
    'test-A short-lags positive (t+0 +0.14 / t+1 +0.27 / t+2 +0.26, within-city per-capita) = the money-follows-crisis '
    'signature now visible IN THE CARE LANE (the officers +0.243 / SAMHSA +0.394 class) - the t+3/t+4 negative tail '
    'is the thin-N Cincinnati-concentrated flips [flag-not-verdict]',
    'test-C mid-stream ordering is RATE-SENSITIVE: raw-lane pooled t+0/t+1 negative (-0.46/-0.40 - arrest-heavy years '
    'co-move with murder-heavy years) while the per100k lane flips t+1 positive (+0.36) - population-growth cities '
    '(Houston) own much of the raw-lane inverse [flag-not-verdict]',
    'per-city test-B sign-consistency lane (Detroit -0.82..-0.90 across t+1..t+4; Memphis t+1 -0.84; STL t+1 -0.81) '
    'is consistent-with-thesis but each city n=4-7 thin - the PATTERN (negative + deepening-with-lag) is the finding',
]

verdict = {
    'ordering_read': (
        'THREE-LANE ORDERING RESULT (associational; honest-n carried):\n'
        '1. CARE->BOOKINGS (test A): short-lags POSITIVE - t+0 +0.14 (n=30) / t+1 +0.27 (n=26) / t+2 +0.26 (n=19), '
        'within-city demeaned per-capita; NYC alone t+0 +0.99 (n=5) - care dollars and arrest-intake co-move in the '
        'same window; the negative t+3/t+4 tail (-0.86/-0.87) is thin-n (11/7 pairs, Cincinnati-concentrated).\n'
        '2. CARE->MURDERS (test B): NEGATIVE at every lag, pooled deepening -0.16 (t+0) -> -0.42 (t+4, n=15); '
        'per-city lane Detroit/Memphis/STL consistently negative through t+1-t+3 - the care-raises-precede-'
        'crime-falls ordering signature survives in the component-book panel.\n'
        '3. BOOKINGS->MURDERS (test C, mid-stream): raw-lane pooled inverted at t+0/t+1 (-0.46/-0.40, n=51/49) - '
        'intake co-moves with violence in-year - while per-city t+3 lane (Boston +0.78 / STL +0.67 / CIN +0.75) '
        'hints intake-waves precede later declines, thin-n. The Simes-and-Jahn sharpest-test frame is now '
        'data-live but needs facility-grain widening before any mechanism claim.\n'
        'NET: the ORDERING the thesis needs is VISIBLE - care co-moves with intake now (A short-lag +) and precedes '
        'murder declines (B negative all lags, deepening with lag) - but every strong tail cell is thin-n and the '
        'NYC near-perfect cells are trend-artifact-flagged. PATTERN-LEAD, NOT VERDICT (the reproducibility law).'
    ),
    'sharpest_next': 'facility-grain widening: NYC facility-deep-lane (test D) shows care->admitted t+0 +0.98 (n=7) '
                     'and the discharges_per_arrest ratio falls 0.18->0.09 across 2015-2024 - the NYC facility book '
                     'is the only facility-grain city; widening = one more facility-key city (Fulton GA is banked '
                     'reference-only) or an NYC sub-borough lane.',
}

out = {
    '_header': hdr,
    'coverage': coverage,
    'honest_gaps': gaps,
    'flags_flags_not_verdicts': flags,
    'verdict': verdict,
    'tests': {
        'A_care_to_bookings': {
            'measure': 'care_usd_total (raw + per-capita) at year t vs bookings_total (UCR-arrest intake proxy, '
                       'raw + per-100k) at year t+lag, within-city pooled and per-city',
            'cities_in_frame': ['Cincinnati', 'Detroit', 'Memphis', 'NYC', 'St. Louis'],
            'pooled_within_city_per100k': stats['testA_care2bookings_rate']['pooled'],
            'pooled_raw': stats['testA_care2bookings_raw']['pooled'],
            'per_city_per100k': stats['per_city_A'],
        },
        'B_care_to_murders': {
            'measure': 'care_usd_total (raw + per-capita) at year t vs murders (rate per 100k + raw) '
                       'at year t+lag',
            'pooled_within_city_rate': stats['testB_care2murders_rate']['pooled'],
            'pooled_raw': stats['testB_care2murders_raw']['pooled'],
            'per_city_rate': stats['per_city_B'],
        },
        'C_bookings_to_murders': {
            'measure': 'bookings_total (per-100k + raw) at year t vs murders at t+lag; 9-city bookings panel',
            'pooled_within_city_rate': stats['testC_bookings2murders_rate']['pooled'],
            'pooled_raw': stats['testC_bookings2murders_raw']['pooled'],
            'per_city_rate': stats['per_city_C'],
            'per_city_raw': stats['per_city_C_raw'],
        },
        'D_nyc_facility_deep_lane': {
            'measure': 'NYC only: care_per_capita vs DOC facility_admitted_per_capita (Socrata 94ri-3ium) by lag; '
                       '+ discharges_per_arrest cross-check vs NYPD arrests (8h9b-rp9u override)',
            'pooled_care_to_admit': stats['testD_nyc_care2admit']['pooled'],
            'xcheck_discharges_per_arrest': stats['nyc_xcheck'],
            'xcheck_read': 'ratio 0.181 (2015) -> 0.089 (2024) = discharge/arrest FALLS monotonically while arrests '
                           'rebound post-2020 - consistent with fewer facility exits per intake (longer stays / '
                           'case-flow shift) - mechanism-adjacent, flagged-not-verdict',
        },
    },
    'panel': panel,
    'bookings_panel_9city': stats['bookings_panel'],
    'nyc_facility_panel': stats['nyc_fac_panel'],
    'files_in': [
        'city_component_annual_v1.jsonl (2,509 rows -> 95 city-years, 6 cities)',
        'bookings_series_v1.jsonl (90 city-years, 9 cities, 2015-2024, 1 honest-null)',
        'bookings_facility_v1.jsonl (1,965 facility-years, 74 facility names, NYC lane usable)',
        'murders_all_v1.json (558 city-years, 40 cities)',
        'population_series_v1.jsonl + populations_wide_v1.jsonl + populations_cities_v2.jsonl '
        '+ triple_slider_v6d.json (pops fallback, labeled)',
    ],
    'files_out': ['care_bookings_ordering_v1.json'],
}

json.dump(out, open(B + 'care_bookings_ordering_v1.json', 'w', encoding='utf-8'), indent=1, default=str)
print('WROTE care_bookings_ordering_v1.json')
print('panel rows:', len(panel), '| bookings 9-city panel rows:', len(stats['bookings_panel']),
      '| full-quad city-years:', len(all4))
