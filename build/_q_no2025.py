import json
import re
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
# THE the v6 = the the rows-near-the-years = the the check:
rows = json.load(open(B + 'triple_slider_v6.json', encoding='utf-8'))

print('=== THE NO-2025-QUESTION ===')
for r in rows:
    if 'new orleans' in r['city'].lower() and r['year'] in (2022, 2023, 2024, 2025, 2026):
        print(f" NO {r['year']}: care {r.get('care_ratio')} | murders {r.get('murders')} | crime+ {r.get('crime_plus')}")

print()
print('=== THE THE-PAIR-FILE = the the NO-2025-actual-content-check ===')
pair = [json.loads(l) for l in open(B + 'nola_houston_pair_v1.jsonl', encoding='utf-8') if l.strip()]
no_rows = [(p.get('era'), p.get('year'), p.get('care_usd_total'), p.get('cage_usd_total')) for p in pair if 'ew orleans' in str(p.get('city','')).lower()]
for x in no_rows[-6:]:
    print(' pair-row:', x)
