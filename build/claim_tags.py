import json

# POLYSCOUT BUILD-1 — THE CLAIM-SOURCE-TAGS: the every-claim-row = the provenance-tagged
# (the same source-law as-the-numbers: the claim-itself = the carries-the-class!)

def tag_claims(path, out_path):
    tf = json.load(open(path, encoding='utf-8'))
    # THE MAMDANI-TAGS:
    if 'mamdani' in path:
        tags = {
            'MMD-001': {'claim_source_class': 'OFFICIAL-PLAN-RELEASE', 'claim_source_detail': 'the mayor\u0027s-own released-plan (the Friday), the multiple-news-confirmed [Certain] + the news-verified by-the-machine'},
            'MMD-002': {'claim_source_class': 'MAYOR\u0027S-OWN-CLAIM', 'claim_source_detail': 'the SOTC-statement = the the mayor\u0027s-own-40%-number = the NOT-yet-machine-verified (the the NYPD-monthly-data = the the cross-check-pending!) [Claim-source honest-flag]'},
            'MMD-003': {'claim_source_class': 'MAYOR\u0027S-OWN-CLAIM (SOTC)', 'claim_source_detail': 'the housing-strategy = the the SOTC-pillar'},
            'CMP-001': {'claim_source_class': 'CAMPAIGN-PLATFORM', 'claim_source_detail': 'the 2025-platform (the the multiple-news-confirmed)'},
            'CMP-002': {'claim_source_class': 'CAMPAIGN-PLATFORM + RGB-OFFICIAL-VOTE', 'claim_source_detail': 'the platform-promise + the two-year-freeze-official-vote [Certain] = the DOUBLE-SOURCED (the the strongest-class!)'},
            'CMP-003': {'claim_source_class': 'CAMPAIGN-PLATFORM + OFFICIAL-LAUNCH', 'claim_source_detail': 'the platform + the pilot-launched-Apr (the the nyc.gov-announce) but-the expansion-troubles = the the reporting-hedged'},
            'CMP-004': {'claim_source_class': 'CAMPAIGN-PLATFORM + OFFICIAL-SITE-ANNOUNCE', 'claim_source_detail': 'the La-Marqueta = the the city-announced (the the mayor\u0027s-office)'},
            'CMP-005': {'claim_source_class': 'CAMPAIGN-PLATFORM', 'claim_source_detail': 'the wage = the platform (the the state-dependent-scope-flag = the honest)'},
        }
        for p in tf.get('campaign_promises', []):
            p.update(tags.get(p['id'], {}))
        for p in tf.get('promises', []):
            p.update(tags.get(p['id'], {}))
    # THE YOUNG-TAGS:
    else:
        tags = {
            'YM-001': {'claim_source_class': 'CAMPAIGN-PLATFORM (2023)', 'claim_source_detail': 'the public-safety-first = the the campaign-coverage-confirmed'},
            'YM-002': {'claim_source_class': 'ELECT-INTERVIEW (FOX13)', 'claim_source_detail': 'the priorities = the the mayor-elect-interview'},
            'YM-003': {'claim_source_class': 'CAMPAIGN-ISSUES-PAGE', 'claim_source_detail': 'the clean-city = the the issues-page-framing'},
        }
        for p in tf.get('campaign_promises', []):
            p.update(tags.get(p['id'], {}))
    # THE CLAIM-NEWS-TAGS (the the Young-claims = the mayor\u0027s-own):
    if 'young' in path:
        for c in tf.get('claims_in_news', []):
            c['claim_source_class'] = 'MAYOR\u0027S-OWN-CLAIM'
            c['claim_source_detail'] = 'the mayor-cited-numbers = the NOT-yet-machine-verified (the UCR/TBI-state-lane = the the cross-check-pending!)'
    json.dump(tf, open(out_path, 'w', encoding='utf-8'), indent=1)
    print('tagged:', out_path)

tag_claims('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/mamdani_term_file_v2.json',
           'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/mamdani_term_file_v2.json')
tag_claims('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/paul_young_statline_v1.json',
           'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/paul_young_statline_v1.json')
print('BUILD-1 = the claim-source-tags = the DONE (the zero-founder-touch)')
