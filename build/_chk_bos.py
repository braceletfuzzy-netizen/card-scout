import json
rows = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/triple_slider_v3.json', encoding='utf-8'))
# THE Boston-1995 = the the check:
for r in rows:
    if r['city'] == 'Boston' and r['year'] in (1990, 1995, 2024):
        print('Boston', r['year'], ': murders', r.get('murders'), '| care_ratio', r.get('care_ratio'), '| care_plus', r.get('care_plus'), '| crime_plus', r.get('crime_plus'))
# AND the the source-file = the the check:
ext = [json.loads(l) for l in open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/care_arc_extension_v1.jsonl', encoding='utf-8') if l.strip()]
for r in ext[:3]:
    print('ext-row:', r.get('city'), r.get('year'), '| care:', r.get('care_usd_total'), '| cage:', r.get('cage_usd_total'))
