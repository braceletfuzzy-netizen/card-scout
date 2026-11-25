import json
rows = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/triple_slider_v6.json', encoding='utf-8'))
print('=== THE STL-2002/2017/2018-QUESTION ===')
for r in rows:
    if 'st' in r['city'].lower()[:2] and 'louis' in r['city'].lower() and r['year'] in range(2015, 2027):
        print(f" STL {r['year']}: care {r.get('care_ratio')} | murders {r.get('murders')} | crime+ {r.get('crime_plus')} | edu {r.get('edu_plus')}")
# AND the the ext-file = the the which-STL-years-actually-fetched:
ext = [json.loads(l) for l in open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/care_arc_extension_v1.jsonl', encoding='utf-8') if l.strip()]
stl_years = [(r.get('year'), r.get('care_usd_total') is not None) for r in ext if 'St' in str(r.get('city'))]
print()
print('the ext-STL-years:', stl_years)
