import json
rows = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/triple_slider_v6.json', encoding='utf-8'))
for r in rows:
    if 'Louis' in r['city'] and '2002' in str(r.get('year','')) or 'Louis' in r['city'] and '2001' == str(r.get('year')):
        print('STL', r['year'], '| care', r.get('care_ratio'), '| murders', r.get('murders'))
# the all-STL-rows:
print()
print('the STL-rows = the years:', sorted(r.get('year') for r in rows if 'Louis' in r['city']))
