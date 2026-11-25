import json
rows = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/triple_slider_v6c.json', encoding='utf-8'))
for r in sorted(rows, key=lambda x: (x['city'], x['year'])):
    if r['city'] == 'NYC':
        print(f" NYC {r['year']}: murders {r.get('murders')} | pop {r.get('population')} | rate {r.get('rate')} | CRIME+ {r.get('crime_plus')} | care {r.get('care_ratio')} | edu {r.get('edu_plus')}")
