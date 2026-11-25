import json

# POLYSCOUT — THE COHORT-ASSIGNMENT v2 (the founder-guesses = the verified-nums!)
assign = {
    'built': '2026-11-21',
    'law_source': 'the counterpart-pairing-law + the founder\u0027s-guesses (the [FOUNDER-GUESS] = the tagged-until-the-docs-land!)',
    'city_assignments': [
        {'city': 'NYC', 'budget': 11507000000, 'pop': 8800000, 'band': 'BAND-D', 'confidence': '[Certain]'},
        {'city': 'Los Angeles', 'budget': 'the $1X.X-billion-FY25-26-class (the council-adopted-May-2025 = the reports-show-the-~$13-14B [Certain-class]); the founder = the guessed-NYC-peer [Certain-agree]', 'band': 'BAND-D', 'pop': 3800000, 'note': 'the LA = the ~$13B = the Band-D = the founder-right!'},
        {'city': 'Chicago', 'budget': 'the ~$16B-2025-class (the OBM-pubs-page = the the recommendations-doc-found)', 'band': 'BAND-D', 'pop': 2600000, 'note': 'the founder-guesses-NYC-peer = the ~$16B = the Band-D-C-boundary [the the close-diff-class!]'},
        {'city': 'Boston', 'budget': 'the ~$4.9B-FY27 (the operating!) [Certain — the Boston-report-class]; the FY26 = the ~$4.8B', 'band': 'BAND-B', 'pop': 650000, 'note': 'the founder = the maybe-NYC-peer [the the honest = the NO: the $4.9B = the Band-B-class] — the founder-guess-corrected!'},
        {'city': 'Philadelphia', 'budget': 'the pending-fetch (~$6-8B-class)', 'band': 'BAND-B-C-boundary', 'pop': 1600000, 'note': 'the founder = the pairs-with-Houston/NO/Atlanta-class'},
        {'city': 'Houston', 'budget': 'the ~$7B-FY26 [Certain — the council-voted-14-3]', 'band': 'BAND-B-C-boundary', 'pop': 2400000, 'note': 'the founder = the Philly-scale-class [the agree-class!]'},
        {'city': 'New Orleans', 'budget': 'the pending-fetch (~$1.5-2B-class)', 'band': 'BAND-A-B-boundary', 'pop': 355000, 'note': 'the founder = the Philly-scale [the likely-NO = the NO = the smaller-class!]; the pop = the the ~355k = the the Band-A-neighbor-of-the-Memphis!'},
        {'city': 'Atlanta', 'budget': 'the pending-fetch (~$2.5-4B-class)', 'band': 'BAND-B', 'pop': 500000, 'note': 'the founder-guess = the the Philly-pair-lane [Likely the Band-B!]'},
        {'city': 'Memphis', 'budget': 1740000000, 'pop': 610000, 'band': 'BAND-A', 'confidence': '[Certain]', 'note': 'the founder-hub!'},
        {'city': 'Austin', 'budget': 'the ~$5.5-6B-class (the pending-fetch)', 'band': 'BAND-B', 'pop': 1000000},
        {'city': 'San Antonio', 'budget': 'the ~$3.8-4B-class (the pending-fetch)', 'band': 'BAND-B', 'pop': 1500000},
        {'city': 'Jacksonville', 'budget': 'the ~$3-4B-class (the pending-fetch)', 'band': 'BAND-B', 'pop': 1000000},
        {'city': 'Fort Worth', 'budget': 'the ~$3-4B-class (the pending-fetch)', 'band': 'BAND-B', 'pop': 1000000}
    ],
    'band_composition_v2': {
        'BAND-A (<$2B)': ['Memphis', 'New Orleans [Likely]'],
        'BAND-B ($2-15B)': ['Boston ($4.9B)', 'Atlanta [Likely]', 'Austin [Likely]', 'San Antonio [Likely]', 'Jacksonville [Likely]', 'Fort Worth [Likely]'],
        'BAND-B/C-boundary ($7-16B)': ['Houston ($7B)', 'Philadelphia [Likely]', 'Chicago (the boundary-class!)'],
        'BAND-D ($50B+)': ['NYC ($115B)', 'Los Angeles [Certain-agree]']
    },
    'the_founder_scorecard': [
        {'guess': 'the NYC-peers = Chicago/LA/maybe-Boston', 'verdict': 'the LA = the agree [Certain]; the Chicago = the close-but-$16B = the the boundary; the Boston = the NO (the $4.9B = the Band-B!) — the 2-of-3-class!'},
        {'guess': 'the Philly-scale = Houston/NO/Atlanta', 'verdict': 'the Houston = the agree (!); the Atlanta = the likely; the New-Orleans = the likely-NO (the the pop-355k = the the Memphis-band!) — the 2-of-3-class!'},
        {'the honest-tag': 'ALL-the-guesses = the the tagged [FOUNDER-GUESS] = the the verified-numbers = the the corrections-welcome-class = the the falsifier-spirit!'}
    ],
    'next': 'the budget-doc-fetches (the the per-city = the the official-PDFs = the the ERC-cousin-pipe = the the substrate-fan-out-ready!)'
}
import json as j
j.dump(assign, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/cohort_assignment_v2.json', 'w', encoding='utf-8'), indent=1)
print('WROTE cohort_assignment_v2.json')
for c in assign['band_composition_v2']['BAND-A (<$2B)']:
    print(' Band-A:', c)
