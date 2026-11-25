import json

# THE LIBRARY-OUTS (the p340-342 = the countables-embedded):
library = {
    'city': 'Memphis',
    'division': 'Library Services (MPL)',
    'source': 'FY26 Adopted Budget Book p.340-342',
    'service_out_v1': [
        {'metric': 'people served per-year (in-person + virtual)', 'value': '2,000,000+', 'note': 'the p342-stated'},
        {'metric': 'new/renovated libraries opened', 'value': 'Orange Mound (2024), Frayser (2025)', 'note': 'the Southwest Twin + the Parkway-Village = the coming'},
        {'metric': 'Teen Innovation Centers', 'value': 'installed-in-almost-all-branches', 'note': 'the FY26 = the additional-locations-scheduled'},
        {'metric': 'programs', 'value': 'thousands-per-year', 'note': 'the workforce-development + the STEAM + the grade-level-reading + the Explore-Memphis-summer'},
        {'metric': 'Discover READ Early-Literacy-Centers', 'value': 'the interactive-play-areas for-children-0-5'}
    ]
}
# THE Works + the Parks = the KPI-tables = the not-found-in-the-scan (the p371 = the legal-levels only — the honest-null):
works = {'division': 'Public Works', 'note': 'the KPI-table = the not-found-in-the-scanned-pages (the p371 = the legal-levels-class) — the honest-null + the street-maintenance = the pothole-repairs/the ROW-maintenance = the identified-lane (the deep-scan = the queued)'}
parks = {'division': 'Memphis Parks', 'note': 'the KPI-table = the not-found-in-the-scanned-pages (the p349-351 = the legal-levels/managed-properties) — the honest-null; the managed-properties = the Overton/the Zoo/the Brooks-Museum-class = the partner-fee-lane'}

out = {'city': 'Memphis', 'built': '2026-11-21', 'fire': json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/memphis_kpis_expanded_v1.json', encoding='utf-8'))['fire'], 'library': library, 'public_works': works, 'parks': parks}
json.dump(out, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/memphis_kpis_divisions_v1.json', 'w', encoding='utf-8'), indent=1)
print('WROTE memphis_kpis_divisions_v1.json')
print('the library-outs =', json.dumps(library['service_out_v1'][:2]))
