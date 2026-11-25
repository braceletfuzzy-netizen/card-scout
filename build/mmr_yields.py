import json

# POLYSCOUT — THE NYC YIELDS-LANE v1 (the PMMR = the Mayor's-Management-Report = the FOUNDED-2026-lane)
yields = {
    'built': '2026-11-21',
    'source': {'document': 'THE 2026 MAYOR\u2019S MANAGEMENT REPORT (MMR)', 'url': 'https://www.nyc.gov/assets/operations/downloads/pdf/mmr2026/2026_mmr.pdf', 'fetched': '2026-11-21', 'pages': 544, 'released': 'September 2026', 'mandate': 'the City-Charter (the annual-public-account-class!)', 'authors': 'the Office-of-Operations (Annie Levers, Director) + the Chief-of-Staff Elle Bisgaard-Church'},
    'structure': [
        'the per-agency-chapters', 
        'the each = the WHAT-WE-DO + the SERVICES-and-GOALS + the HOW-WE-PERFORMED (the narrative) + the PERFORMANCE-INDICATORS-TABLE',
        'the indicator-table = the FY22/FY23/FY24/FY25/FY26-actuals + the FY26-target + the FY27-target + the 5-yr-trend + the desired-direction = THE FIVE-YEAR-TIME-SERIES-per-indicator!'
    ],
    'nypd_sample_rows': [
        {'indicator': 'Major felony crime (#)', 'fy22': 119748, 'fy23': 127393, 'fy24': 126212, 'fy25': 121750, 'fy26': 118866, 'note': 'the -2.4%-YoY; the 4-of-the-7-felonies-down [Certain]'},
        {'indicator': 'Murder (#)', 'note': 'the -20% (the 339\u2192272 = the surpassing-the-2019-decade-low!)'},
        {'indicator': 'Robbery (#)', 'note': 'the -9% (the 15,607\u219214,263)'},
        {'indicator': 'Burglary (#)', 'note': 'the -9% (13,107\u219211,888)'},
        {'indicator': 'Shooting incidents', 'note': 'the -16% (804\u2192673)'},
        {'indicator': 'Rape', 'note': 'the +9% BUT-the DEFINITION-CHANGE-adopted-FY26 (the the honest-metric-shift-flag = the the units-shuffled = the OBFUSCATION-signature-class-OR-the honest-broadening = the the needs-the-definition-column!)'},
        {'indicator': 'Grand larceny', 'note': 'the +<1% (the the only-property-crime-up)'}
    ],
    'mamdani_sotc_quote_from_pmmr_p3': 'Since our administration took office just over eight months ago, we have sought to waste no time delivering for the working people... From launching the city\u2019s first free child care program for 2[-year-olds]...',
    'obfuscation_check': 'the MMR = the SELF-PUBLISHED-full-detail = the NOT-an-obfuscation-signature (the the opposite-class = the the transparency-artifact!); the rape-definition-shift = the the FIRST-metric-shift-flag-logged (the the signature-watch-on!)',
    'score_law': 'the MMR-indicators = the Tier-1-countables = the the time-series = THE YIELD-SIDE-OF-THE-STATLINE (the the budget-in [the ERC] + the yield-out [the MMR] = THE NYC-TWO-SCALE-COMPLETE!)'
}
import json as j
j.dump(yields, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/nyc_yields_mmr_v1.json', 'w', encoding='utf-8'), indent=1)
print('WROTE nyc_yields_mmr_v1.json')
