import json
rows = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/triple_slider_v6b.json', encoding='utf-8'))
for r in rows:
    if 'louis' in r['city'].lower() and r['year'] in (2002, 2016, 2017, 2018):
        print('STL', r['year'], '| murders', r.get('murders'), '| crime+', r.get('crime_plus'), '| care', r.get('care_ratio'))
