import json

# POLYSCOUT — CRIME+ v0 (the field-normalized crime metric = the ERA+-port!)
crime_plus = {
    'built': '2026-11-22',
    'name': 'CRIME+ (the founder-designed = the ERA+-port: "run crime rates like baseball stats measured against the field, where 100 = in-line")',
    'the_definition': {
        'formula': 'CRIME+ = 100 x (city_crime_rate / BAND_field_crime_rate)',
        'the_field': 'the cohort-band median (like-to-like law — Band-A smalls compared to Band-A, never NYC!)',
        'direction': 'HIGHER = MORE CRIME (the inverse-ERA+ — Skenes-200-good/bad flips: here 200-crime = 2x-field TROUBLE; 50-crime = the safer city!)',
        'the_basis_point': '100 = in-line = the instant-readable ruler',
        'care_plus_twin': 'CARE+ = 100 x (city_care_ratio / band_median_care_ratio) — the higher = the more care = the straight-read (no inversion!)',
        'the_composite_read': 'CARE+/CRIME+ = THE THE-BALANCE-INDEX = the one-number-per-city-per-year!'
    },
    'the_method (the founder\u0027s whole-arc-decoded = the same-as-the-baseball!)': [
        'STEP-1 = the rough-pass: compute CRIME+/CARE+ for all-band-a cities = LOOK-FOR-DIFFERENCES (the outliers!)',
        'STEP-2 = the outlier-why: the anomalous-rows (e.g., Memphis-Task-Force years, NO-rebuild-trough) = the investigate-drivers = the the named-mechanisms!',
        'STEP-3 = the predict-from-the-accounted-inputs: the composite-of-variables (care-ratio/admin-%/budget-size/population/policy-events) -> the crime+ prediction = THE FAME-COMPOSITE-PORTED!',
        'STEP-4 = the Y+n-honesty (the founder\u0027s-phrase = "planting-trees-because-you-need-shade" = the effects-we-can\u0027t-fully-instrument = the named-and-carried!)',
        'STEP-5 = the backwards-inflection-points (the 1995-Boston/the 2011-NO = the the known-flips = the the causality-seekers!)'
    ],
    'the_worked_example (the the demo-from-the-band-a!)': {
        'note': 'the care+ = computable-TONIGHT (the budgets-landed); the crime+ = awaits-the-crime-ingest!',
        'demo_care_plus_band_a (approx, the the FY26-vintage)': {
            'Memphis': 'care ~0.52 vs band-A-median ~0.42 -> CARE+ ~124 (the care-tilted-city!)',
            'New Orleans': '0.365 post-recovery -> CARE+ ~87 (the still-rebuilding-class!)',
            'St Louis': '0.118 GF -> CARE+ ~low (the GF-lens = the fund-aware-v2-pending!)',
            'Cincinnati': '0.728 -> CARE+ ~173 (the care-leader-of-the-band!)'
        }
    },
    'the_data_needs': [
        'the crime-ingest = the UCR/state-annual per-city-year = THE next-substrate-run!',
        'the the band-medians = the per-year-per-band = the the field!'
    ],
    'the_lineage': 'the ERA+/OPS+ = the league-adjusted = 100 = average = the the founder\u0027s-design = the the instant = the the famous-scales!'
}
import json as j
j.dump(crime_plus, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/crime_plus_v0.json', 'w', encoding='utf-8'), indent=1)
print('WROTE crime_plus_v0.json')
