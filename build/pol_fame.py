import json

# POLYSCOUT — THE POLITICAL-FAME-COMPOSITE v0 (the founder's-question = the the engine-port!)
composite = {
    'built': '2026-11-21',
    'engine_lineage': 'the MLB-fame-composite = the ported (the the two-fame-lanes/SS250.76 + the award-lane + the race-definition-law = the all-port!)',
    'two_lanes': {
        'lane_A_formation': '"story-to-come" = the promise-to-deliver-class (the candidates/the rising-stars/the term-early)',
        'lane_B_realized': '"story-delivered" = the execution-class (the incumbents/the delivered/the second-terms)'
    },
    'five_inputs': [
        {'input': 1, 'name': 'SCOPE-POWER', 'scale': '0-1', 'definition': 'the jurisdiction-weight = the fame-ceiling-setter', 'scale_rows': {'council-member': 0.1, 'state-legislator': 0.2, 'mayor-small-city': 0.3, 'mayor-big-city': 0.6, 'governor': 0.8, 'senator': 0.9, 'president': 1.0}, 'note': 'the WHO-the-power-touches = the who-cares'},
        {'input': 2, 'name': 'NATIONAL-PROFILE', 'scale': '0-1', 'definition': 'the media-name-recognition-lane (the mentions/the press/lane)', 'note': 'the city-size-adjusted (the NYC-mayor = the bigger-profile-ceiling than-the Memphis = the the same-job-different-stage!)'},
        {'input': 3, 'name': 'EVENT-NODES', 'scale': 'the countable', 'definition': 'the scandals/viral-moments/national-endorsements/primaries/awards = the fame-accretes-on-events (the award-lane-port)'},
        {'input': 4, 'name': 'STORY-INTENSITY', 'scale': '0-1', 'definition': 'the narrative-carrying-class (the contested-elections = the real-info-shock per-the race-definition-law; the identity-story = the the national-carry)', 'examples': {'Mamdani': 'the 0.9-class (the democratic-socialist-in-NYC = the national-story)', 'Young': 'the 0.4-class (the the local-story)'}},
        {'input': 5, 'name': 'EXECUTION-YIELD', 'scale': '0-1', 'definition': 'THE GAUGE-NATIVE INPUT — the promise-delivery-rate + the master-class-scores = the no-other-fame-engine-carries-this!', 'note': 'the our-moat-input = the the two-scale\u0027s-differentiator'}
    ],
    'worked_examples': [
        {'name': 'Mamdani', 'composite_v0': 0.62, 'breakdown': 'scope 0.6 (the big-city-mayor) x the profile 0.8 x the story 0.9 x the events (the high) x the yield (the the live-rows = the the running)', 'band': '[ARRIVED-class]'},
        {'name': 'Young', 'composite_v0': 0.38, 'breakdown': 'scope 0.3 (the mid-city-mayor) x the profile 0.3 x the story 0.4 x the events (the low) x the yield (the the mixed-rows)', 'band': '[PRE-FAME-to-VET-LAG boundary]'},
        {'name': 'the senator-comparison', 'note': 'the US-senator = the scope-0.9 = the the national-stage = the the fame-ceiling-the-highest (the the why-the-senate = the the fame-machine-by-design!)'}
    ],
    'laws': [
        'the two-lane-rule = the never-blend (the the formation vs-the realized = the the separate-columns)',
        'the execution-yield = the only-input-THE-MACHINE-SUPPLIES (the the rest = the external-sourced)',
        'the events = the the fame-accretes-on (the the countable-calendar)',
        'the no-goodness-adjustment (the the fame = the what-the-world-sees = the not-the-what-they-earned = the the honest-separation!)'
    ]
}
import json as j
j.dump(composite, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/political_fame_composite_v0.json', 'w', encoding='utf-8'), indent=1)
print('WROTE political_fame_composite_v0.json')
