import json
rows = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/triple_slider_v6.json', encoding='utf-8'))
print('=== THE STL-murders-years = the what-crime-lane-has ===')
for r in rows:
    if 'st louis' in r['city'].lower():
        print(f" {r['year']}: care {r.get('care_ratio')} | murders {r.get('murders')}")
