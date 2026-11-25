import json
from collections import defaultdict

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

# EDU+ v1 COMPUTE: per-capita education spend, band-normalized (100 = in-line)
def jl(p):
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]

rows = jl(B + 'edu_series_v1.jsonl')

# collect (city, year, edu, pop) with basis flag
data = []
for r in rows:
    e = r.get('edu_total_usd'); pop = r.get('population')
    if e and pop:
        epc = round(e / pop, 1)
        data.append({'city': r['city'], 'year': str(r.get('year')), 'edu': e, 'pop': pop,
                     'epc': epc, 'basis': r.get('basis', '?')})

# band-median per year
field = defaultdict(list)
for d in data:
    field[d['year']].append(d['epc'])
meds = {y: sorted(v)[len(v)//2] for y, v in field.items() if len(v) >= 2}

out = []
print('=== EDU+ v1 (100 x city-edu-per-capita / year-band-median; basis-flagged) ===')
print(f"{'CITY':14s} {'YEAR':6s} {'edu':>13s} {'epc':>9s} {'basis':9s} {'EDU+':>7s}")
print('-'*64)
for d in sorted(data, key=lambda x: (x['year'], -x['epc'])):
    med = meds.get(d['year'])
    eplus = round(d['epc']/med*100, 1) if med else None
    d['edu_plus'] = eplus
    out.append(d)
    print(f"{d['city']:14s} {d['year']:6s} {d['edu']:>13,} {d['epc']:>9,} {d['basis']:9s} {str(eplus):>7s}")

json.dump(out, open(B + 'edu_plus_v1_computed.json', 'w', encoding='utf-8'), indent=1)
print(f"\nWROTE edu_plus_v1_computed.json ({len(out)} rows), medians per year: {meds}")
