import json, re
rows = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/triple_slider_v3.json', encoding='utf-8'))
# the the filled-care = the which-city-years:
filled = [(r['city'], r['year'], r['care_ratio']) for r in rows if r.get('care_ratio')]
print('the care-filled:', len(filled))
for f in filled:
    print(' *', f)
