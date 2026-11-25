import json

# THE BUCKET-MAPPING v1 (the 15-agencies -> the 7-buckets per SPINOFF-003's classification; the human-services-heavy-BFA = the HHS-focused-volume):
buckets = {
    'public_safety': ['Police Department', 'Department Of Correction'],
    'infrastructure_environment': ['Department Of Environmental Protect.', 'Department Of Transportation', 'Department Of Sanitation', 'Department Of Parks And Recreation'],
    'human_services_health': ["Admin For Children's Services", 'Department Of Health And Mental Hygiene', 'Department Of Social Services', 'Department Of Homeless Services', 'Department For The Aging', 'Department Of Youth & Community Dev'],
    'housing': ['Housing Preservation And Development'],
    'admin_general_econ': ['Department Of Finance', 'Department Of Small Business Services'],
}

agency_data = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/nyc_agencies_bfa_v2.json', encoding='utf-8'))

# THE honest-note: the BFA-volume = the HHS-focused-volumes (the 15 = the BFA\u0027s-covered-agencies — the NYPD/ACS/HP/DOHMH etc = the social-services-heavy-class);
# the citywide-total = $115.07B (all-funds) — THESE agencies = the subset (the sum $1.853B-city-share-class = the per-agency-FY26 = the BFA\u0027s-own-volume-rows [Likely the city-funds-share-class]).
# THE honest-flag-banked: the agency-sum (1.853B) ≪ the 115.07B-all-funds = the BFA = the covers-15-agencies = the PARTIAL-instrument (the v2-fully-complete = the all-80-class via-the ERC).

result = {'city': 'NYC', 'fiscal_year': 2026, 'source': 'the BFA (adopt25/adopt25-bfa.pdf)', 'bucket_note': 'the BFA = the 15-agency-volume (the HHS-heavy coverage); the citywide = the $115.07B-all-funds = the NOT-summed-here (the partial-instrument honest-flag)', 'buckets': {}}
for bname, members in buckets.items():
    tot = sum(agency_data.get(m, {}).get('fy2026_thousands', 0) for m in members)
    result['buckets'][bname] = {
        'usd': tot * 1000,
        'members': {m: agency_data[m]['fy2026_thousands'] * 1000 for m in members if m in agency_data}
    }
    print(f'{bname:28s} ${tot*1000:>14,}')

json.dump(result, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/nyc_buckets_v2.json', 'w', encoding='utf-8'), indent=1)
print('WROTE nyc_buckets_v2.json')
