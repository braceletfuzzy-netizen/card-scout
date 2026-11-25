import json

# POLYSCOUT — THE COHORT-BANDS v1 (the counterpart-pairing-law = the applied!)
cohorts = {
    'built': '2026-11-21',
    'law': 'the cross-city = the paired-counterparts-by-the-budget-band + the population-band; the admin-costs = the compared-as-a-%-of-budget = the fantasy-cap-analog',
    'bands': [
        {'band': 'BAND-A', 'budget_range': 'under $2B', 'pop_range': 'under ~800k', 'members_known': ['Memphis ($1.74B, 610k)'], 'note': 'the founder-hub-band!'},
        {'band': 'BAND-B', 'budget_range': '$2-15B', 'pop_range': '~800k-2M', 'members_known': [], 'note': 'the Austin/Jacksonville/Fort-Worth-class (the the census-11 = the the candidates!)'},
        {'band': 'BAND-C', 'budget_range': '$15-50B', 'pop_range': '~2-5M', 'members_known': [], 'note': 'the Philadelphia-class'},
        {'band': 'BAND-D', 'budget_range': '$50-150B+', 'pop_range': '~5M+', 'members_known': ['NYC ($115.07B, 8.8M)'], 'note': 'the mega-band'}
    ],
    'comparison_laws': [
        'the outcomes = the compared-within-the-band (the never-cross-band)',
        'THE ADMIN-% = the universal-ratio (the admin-cost / the total-budget = THE comparable-across-bands = the the fantasy-cap-class!)',
        'the z-scores = the against-the-BAND-median (the the peer-median-law-port!)',
        'the per-capita = the the secondary-ratio (the the $-per-resident = the the scale-incomprehensibility-cure = the SS004.4-law!)'
    ],
    'the_fantasy_analog': 'the the founder\u0027s-own: the admin-% = THE SALARY-CAP-CLASS (the the league-normalized = the the is-the-roster-spending-lean-or-the-bloated-vs-the-peers = the the fame-density-gauge-the-civic-twin!)',
    'existing_census': 'the the 11-city-cohort (the SPINOFF-002.6: the NYC/LA/Chicago/Houston/Phoenix/Philadelphia/San-Antonio/Jacksonville/Fort-Worth/Austin/Memphis) = the the band-assignment-ready (the the the population-rows = the the known!)'
}
import json as j
j.dump(cohorts, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/cohort_bands_v1.json', 'w', encoding='utf-8'), indent=1)
# THE assign-the-census-11 (the the population-rows = the the banked):
census = {
    'NYC': {'pop': 8800000, 'budget': 11507000000, 'band': 'BAND-D'},
    'LA': {'pop': 3800000, 'band': 'BAND-C-or-D'},
    'Chicago': {'pop': 2600000, 'band': 'BAND-C'},
    'Houston': {'pop': 2400000, 'band': 'BAND-C'},
    'Phoenix': {'pop': 1600000, 'band': 'BAND-B-C'},
    'Philadelphia': {'pop': 1600000, 'band': 'BAND-B-C'},
    'San Antonio': {'pop': 1500000, 'band': 'BAND-B-C'},
    'Jacksonville': {'pop': 1000000, 'band': 'BAND-B'},
    'Fort Worth': {'pop': 1000000, 'band': 'BAND-B'},
    'Austin': {'pop': 1000000, 'band': 'BAND-B'},
    'Memphis': {'pop': 610000, 'budget': 1740000000, 'band': 'BAND-A'}
}
census_out = {'note': 'the budgets = the null-until-fetched (the the pop-rows = the banked); the band-assignments = the provisional-until-the-budget-rows-land', 'cities': census}
j.dump(census_out, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/cohort_census_11_v1.json', 'w', encoding='utf-8'), indent=1)
print('WROTE cohort_bands_v1.json + cohort_census_11_v1.json')
