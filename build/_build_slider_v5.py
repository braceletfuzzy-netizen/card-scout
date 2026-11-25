"""triple_slider_v5 = v4 merge + (a) care_arc_extension_v2.jsonl rows, (b) +/-2yr window-normalized CRIME+ for solo-field years.

Field-extension rule (task LANE-2): for any (city,year) row where the murder RATE is computable but
CRIME+ is None because the same-year field has <2 computable rates, normalize against the pooled
rates of ALL cities within [year-2, year+2] (median). Rows are flagged 'window-normalized' in notes.
"""
import json, re, os
from statistics import median
from collections import defaultdict

P = os.path.dirname(os.path.abspath(__file__))

def norm_city(c): return (c or '').lower().strip()
def norm_year(v):
    """Year from a value. Handles 'FY98'/'FY2016-17'-style eras: FYnn < 90 means 19nn,
    FYnn >= 90 also 19nn (e.g. FY98=1998); FY2x means 20nn."""
    s = str(v)
    m = re.search(r'((19|20)\d\d)', s)
    if m: return int(m.group(1))
    m = re.search(r'\bFY\s*(\d{2})\b', s, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        return 1900 + n if n >= 30 else 2000 + n
    return None

# ---------- reproduce v4 rate/care maps ----------
murders, pops = {}, {}
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl'):
    path = os.path.join(P, f)
    if not os.path.exists(path): continue
    for l in open(path, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        c, y = norm_city(r.get('city')), norm_year(r.get('year'))
        if not y: continue
        if r.get('murders') is not None:
            if (c, y) not in murders or murders[(c, y)] < r['murders']:
                murders[(c, y)] = r['murders']
        if r.get('population'):
            pops.setdefault((c, y), r['population'])
fp = os.path.join(P, 'population_series_v1.jsonl')
if os.path.exists(fp):
    for l in open(fp, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        c, y = norm_city(r.get('city')), norm_year(r.get('year'))
        if r.get('population') and y:
            pops.setdefault((c, y), r['population'])

partials = set()
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl'):
    path = os.path.join(P, f)
    if not os.path.exists(path): continue
    for l in open(path, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        y = norm_year(r.get('year'))
        blob = str(r.get('notes','')) + str(r.get('data_quality','')) + str(r.get('year'))
        if ('YTD' in blob or 'Nov' in blob or 'partial' in blob.lower() or y == 2026) and y == 2026:
            partials.add((norm_city(r.get('city')), y))

rates = {}
for (c, y), m in murders.items():
    p = pops.get((c, y))
    if p and m:
        rates[(c, y)] = round(m / p * 100000, 1)

field = defaultdict(list)
for (c, y), rate in rates.items():
    if (c, y) not in partials:
        field[y].append(rate)
# v4 convention (preserved so v4 and v5 are the SAME statistic): median = sorted(v)[len(v)//2]
meds = {y: sorted(v)[len(v)//2] for y, v in field.items() if len(v) >= 2}

care = {}
for f in ('boston_care_cage_series_v1.jsonl', 'neworleans_care_cage_series_v1.jsonl',
          'stlouis_care_cage_series_v1.jsonl', 'cincinnati_care_cage_series_v1.jsonl',
          'memphis_care_cage_series_v1.jsonl', 'detroit_care_cage_series_v1.jsonl',
          'okc_care_cage_series_v1.jsonl', 'nyc_care_cage_series_v1.jsonl'):
    path = os.path.join(P, f)
    if not os.path.exists(path): continue
    for l in open(path, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        era = str(r.get('era_or_year') or r.get('era') or r.get('year') or '')
        y = norm_year(era)
        cc = r.get('city') or f.split('_')[0]
        cu, ga = r.get('care_usd_total'), r.get('cage_usd_total')
        if cu and ga and y and y > 1970:
            care[(norm_city(cc), y)] = round(cu / ga, 3)
for f in ('care_arc_extension_v1.jsonl', 'care_arc_extension_v2.jsonl'):
    path = os.path.join(P, f)
    if not os.path.exists(path): continue
    for l in open(path, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        y = norm_year(r.get('year'))
        cu, ga = r.get('care_usd_total'), r.get('cage_usd_total')
        if cu and ga and y:
            care[(norm_city(r.get('city')), y)] = round(cu / ga, 3)

edu = {}
ep = os.path.join(P, 'edu_plus_v1_computed.json')
if os.path.exists(ep):
    for r in json.load(open(ep, encoding='utf-8')):
        c, y = norm_city(r.get('city')), norm_year(r.get('year'))
        if r.get('edu_plus') is not None:
            edu[(c, y)] = {'edu_plus': r['edu_plus'], 'basis': r.get('basis')}

# ---------- assemble ----------
keys = sorted(set(list(rates.keys()) + list(care.keys()) + list(edu.keys())))
window_notes = {}
out = []
for (c, y) in keys:
    if y is None or y < 1980: continue
    rate = rates.get((c, y))
    partial = (c, y) in partials
    crime_plus, note = None, None
    if rate is not None and not partial:
        if y in meds:
            crime_plus = round(rate / meds[y] * 100, 1)
        else:
            pool = [rates[(cc, yy)] for (cc, yy) in rates
                    if abs(yy - y) <= 2 and (cc, yy) not in partials]
            if len(pool) >= 4:
                wm = sorted(pool)[len(pool)//2]  # match v4's median convention for comparability
                crime_plus = round(rate / wm * 100, 1)
                note = {
                    'window_normalized': True,
                    'window': [y - 2, y + 2],
                    'window_pool_n': len(pool),
                    'window_median_rate': round(wm, 1),
                    'reason': 'solo-field year (same-year computable rates < 2); normalized against pooled +/-2yr field rates'
                }
                window_notes[(c, y)] = note
    care_ratio = care.get((c, y))
    e = edu.get((c, y))
    title = c.title().replace('St Louis', 'St. Louis')
    row = {'city': title, 'year': y, 'murders': murders.get((c, y)),
           'population': pops.get((c, y)), 'rate': rate,
           'crime_plus': crime_plus, 'partial_flag': partial,
           'care_ratio': care_ratio, 'care_plus': round(care_ratio * 100, 1) if care_ratio else None,
           'edu_plus': e.get('edu_plus') if e else None, 'edu_basis': e.get('basis') if e else None}
    if note:
        row['normalization_note'] = note
    out.append(row)

out.sort(key=lambda x: (x['city'], x['year']))
json.dump(out, open(os.path.join(P, 'triple_slider_v5.json'), 'w', encoding='utf-8'), indent=1)

# ---------- v5b: only extend crime_plus to fill care side? Keep single v5 as specified ----------
v4 = json.load(open(os.path.join(P, 'triple_slider_v4.json'), encoding='utf-8'))

def pattern(r):
    c, k, e = r.get('care_plus'), r.get('crime_plus'), r.get('edu_plus')
    s = ('C' if c is not None else '-') + ('A' if k is not None else '-') + ('E' if e is not None else '-')
    return s

before = defaultdict(int)
for r in v4: before[pattern(r)] += 1
after = defaultdict(int)
for r in out: after[pattern(r)] += 1

# v5 count: also count window-normalized rows
wn = sum(1 for r in out if r.get('normalization_note'))
rows_added_care = sum(1 for r in out if r.get('care_plus') is not None) - sum(1 for r in v4 if r.get('care_plus') is not None)
rows_added_crime = sum(1 for r in out if r.get('crime_plus') is not None) - sum(1 for r in v4 if r.get('crime_plus') is not None)

print('PATTERN-COUNT TABLE (before v4 -> after v5)')
pats = sorted(set(before) | set(after))
print(f"{'pattern':<10}{'v4':>6}{'v5':>6}{'delta':>8}")
for p in pats:
    print(f'{p:<10}{before[p]:>6}{after[p]:>6}{after[p]-before[p]:>+8}')
print()
print('rows window-normalized in v5:', wn, sorted([(r['city'], r['year']) for r in out if r.get('normalization_note')]))
print('care_plus rows added by v2 extension:', rows_added_care)
print('crime_plus rows added by window extension:', rows_added_crime)
print('total rows v4:', len(v4), 'v5:', len(out))

# print the exact rows the window-extension touched
print()
print('WINDOW-NORMALIZED ROWS DETAIL:')
for r in out:
    if r.get('normalization_note'):
        print(f"  {r['city']} {r['year']}: rate={r['rate']} -> CRIME+={r['crime_plus']} (window median rate {r['normalization_note']['window_median_rate']}, pool n={r['normalization_note']['window_pool_n']})")
