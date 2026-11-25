"""triple_slider_v6 = v5 + HOLE-CLOSERS (final resolution pass).

LANE-1 care:
 - New Orleans 2004-2011 (+2017/2019/2022/2026) care/cage CARRIED VERBATIM from nola_houston_pair_v1.jsonl
   (the pair file already carried the FY2011-book Statement of Expenditures rows; re-parsed, not re-fetched).
 - Houston 2004/05/06/07/22/24/26 care/cage likewise carried from the pair file.
 - HOUSTON 2011/2019 care/cage: the brief said the pair file carries them - VERIFIED FALSE (both the .jsonl
   and the .json pair files hold only FY04/05/06/07/22/24/26/27). Honest structural gap, labeled.
 - Boston 2019-2022 care from care_arc_extension_v2.jsonl: the v5 merge DROPPED these because the file
   stores year as 2-digit int (19/20/21/22) and norm_year() returned None. Fixed here.
 - City-key normalize bug: wave1 rows keyed 'New Orleans'/'St. Louis' while pair/bank files key
   'Neworleans'/'Stlouis' - v5 emitted them as SEPARATE duplicate rows (that's the 121-row split).
   v6 merges them into one canonical row per year (canonical display names fixed).
LANE-2 crime:
 - Cincinnati full arc: t9kw-3jfx Socrata for 2020-2026 + FBI CDE OHCIP0000 for 2015/16/17/2019
   (t9kw has NO 2015-16 rows and a broken 2019); 2026 = partial YTD (dataset max eventdate 2026-11-16).
 - Boston 1980/1983 from archived CIUS national volumes (archive.org scans, vision-read of Table pages).
 - Detroit 2012 + Houston 2006/2007/2024 from FBI CDE agency homicide series.
 - New Orleans 2025 CDE '0' is a NON-REPORTING zero (NOPD left the UCR summary program; actuals null,
   0/12 months) - excluded; murders null with honest note (press ~mid-90s NOT carried: unfounded).
 - populations inherit v5 chains; new rows get pops from the sources their murders came from
   (CDE/CIUS books/pair file), provenance-tagged.
Field-extension rule (v5 convention kept): same-year field median >=2 computable rates -> CRIME+;
else +/-2yr pooled window normalization (flagged, pool>=4).
NOTE: because the merged rows now pool the FULL field (v5 counted the split duplicates separately),
same-year medians shifted slightly; all CRIME+ renormalized consistently on the merged field.
"""
import json, os, re, sys
from statistics import median
from collections import defaultdict

P = os.path.dirname(os.path.abspath(__file__))

def norm_city(c): return (c or '').lower().strip().replace('.', '').replace(' ', '')
def norm_year(v):
    s = str(v)
    m = re.search(r'((19|20)\d\d)', s)
    if m: return int(m.group(1))
    m = re.search(r'\bFY\s*(\d{2})\b', s, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        return 1900 + n if n >= 30 else 2000 + n
    return None

# ---------- murders/populations (max-wins dedupe like v5) ----------
murders, pops = {}, {}
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl',
          'crime_series_wave2_holefill.jsonl'):
    path = os.path.join(P, f)
    if not os.path.exists(path): continue
    for l in open(path, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        c, y = norm_city(r.get('city')), norm_year(r.get('year'))
        if not y: continue
        # NOPD 2025: CDE summary 0/12 months (actuals null) = NON-REPORTING, not zero murders
        if c == 'neworleans' and y == 2025:
            continue
        if r.get('murders') is not None:
            if (c, y) not in murders or murders[(c, y)] < r['murders']:
                murders[(c, y)] = r['murders']
        if r.get('population'):
            pops.setdefault((c, y), r['population'])
fp = os.path.join(P, 'population_series_v1.jsonl')
for l in open(fp, encoding='utf-8'):
    if not l.strip(): continue
    r = json.loads(l)
    c, y = norm_city(r.get('city')), norm_year(r.get('year'))
    if r.get('population') and y:
        pops.setdefault((c, y), r['population'])

partials = set()
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl',
          'crime_series_wave2_holefill.jsonl'):
    path = os.path.join(P, f)
    if not os.path.exists(path): continue
    for l in open(path, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l)
        y = norm_year(r.get('year'))
        blob = str(r.get('notes', '')) + str(r.get('data_quality', ''))
        if y == 2026 and ('YTD' in blob or 'partial' in blob.lower() or 'Nov' in blob):
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
meds = {y: sorted(v)[len(v) // 2] for y, v in field.items() if len(v) >= 2}

# ---------- care ----------
care = {}
care_provenance = {}
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
            care_provenance[(norm_city(cc), y)] = {'source': f, 'care_usd_total': cu, 'cage_usd_total': ga}
# care_arc_extension_v1: full-year ints only (its Boston 19/20/21/22 ints were superseded by v2)
for l in open(os.path.join(P, 'care_arc_extension_v1.jsonl'), encoding='utf-8'):
    if not l.strip(): continue
    r = json.loads(l)
    yy = r.get('year')
    y = yy if isinstance(yy, int) and yy > 1000 else norm_year(yy)
    cu, ga = r.get('care_usd_total'), r.get('cage_usd_total')
    if cu and ga and y:
        care[(norm_city(r.get('city')), y)] = round(cu / ga, 3)
        care_provenance[(norm_city(r.get('city')), y)] = {'source': 'care_arc_extension_v1.jsonl', 'care_usd_total': cu, 'cage_usd_total': ga}
# care_arc_extension_v2: Boston rows are 2-digit ints (19/20/21/22) -> THE v5 join-miss, fixed here
for l in open(os.path.join(P, 'care_arc_extension_v2.jsonl'), encoding='utf-8'):
    if not l.strip(): continue
    r = json.loads(l)
    yy = r.get('year')
    c = norm_city(r.get('city'))
    if isinstance(yy, int) and yy < 100 and yy > 10:
        y = 2000 + yy              # Boston FY19-22 2-digit fix
    else:
        y = yy if isinstance(yy, int) and yy > 1000 else norm_year(yy)
    cu, ga = r.get('care_usd_total'), r.get('cage_usd_total')
    if cu and ga and y:
        care[(c, y)] = round(cu / ga, 3)
        care_provenance[(c, y)] = {'source': 'care_arc_extension_v2.jsonl', 'care_usd_total': cu, 'cage_usd_total': ga}
# pair-file carry for NO/Houston (fills only; banked series grain wins on key collision)
for l in open(os.path.join(P, 'nola_houston_pair_v1.jsonl'), encoding='utf-8'):
    if not l.strip(): continue
    r = json.loads(l)
    c, y = norm_city(r.get('city')), norm_year(r.get('era_or_year'))
    cu, ga = r.get('care_usd_total'), r.get('cage_usd_total')
    if c and y and cu and ga and y > 1970:
        if (c, y) not in care:
            care[(c, y)] = round(cu / ga, 3)
            care_provenance[(c, y)] = {'source': 'nola_houston_pair_v1.jsonl (carried verbatim)', 'care_usd_total': cu, 'cage_usd_total': ga}

# ---------- edu ----------
education = {}
for r in json.load(open(os.path.join(P, 'edu_plus_v1_computed.json'), encoding='utf-8')):
    c, y = norm_city(r.get('city')), norm_year(r.get('year'))
    if r.get('edu_plus') is not None:
        education[(c, y)] = {'edu_plus': r['edu_plus'], 'basis': r.get('basis')}

# ---------- assemble ----------
keys = sorted(set(list(rates.keys()) + list(care.keys()) + list(education.keys())))
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
                wm = sorted(pool)[len(pool) // 2]
                crime_plus = round(rate / wm * 100, 1)
                note = {'window_normalized': True, 'window': [y - 2, y + 2],
                        'window_pool_n': len(pool), 'window_median_rate': round(wm, 1),
                        'reason': 'solo-field year (same-year computable rates < 2); normalized against pooled +/-2yr field rates'}
    care_ratio = care.get((c, y))
    e = education.get((c, y))
    # canonical display name: wave1 and pair/bank key spellings merge (norm strips spaces/dots)
    title = {'neworleans': 'New Orleans', 'stlouis': 'St. Louis'}.get(c, c.title().replace('Nyc', 'NYC'))
    row = {'city': title, 'year': y, 'murders': murders.get((c, y)),
           'population': pops.get((c, y)), 'rate': rate,
           'crime_plus': crime_plus, 'partial_flag': partial,
           'care_ratio': care_ratio, 'care_plus': round(care_ratio * 100, 1) if care_ratio else None,
           'edu_plus': e.get('edu_plus') if e else None,
           'edu_basis': e.get('basis') if e else None}
    if note:
        row['normalization_note'] = note
    cp = care_provenance.get((c, y))
    if cp:
        row['care_provenance'] = cp
    out.append(row)

out.sort(key=lambda x: (x['city'], x['year']))
json.dump(out, open(os.path.join(P, 'triple_slider_v6.json'), 'w', encoding='utf-8'), indent=1)

# ---------- pattern-count table v5 vs v6 ----------
v5 = json.load(open(os.path.join(P, 'triple_slider_v5.json'), encoding='utf-8'))

def pattern(r):
    s = ('C' if r.get('care_plus') is not None else '-') \
      + ('K' if r.get('crime_plus') is not None else '-') \
      + ('E' if r.get('edu_plus') is not None else '-')
    return s

before, after = defaultdict(int), defaultdict(int)
for r in v5: before[pattern(r)] += 1
for r in out: after[pattern(r)] += 1
pats = sorted(set(before) | set(after))
print(f"{'pattern':<10}{'v5':>6}{'v6':>6}{'delta':>8}")
for p in pats:
    print(f"{p:<10}{before[p]:>6}{after[p]:>6}{after[p]-before[p]:>+8}")
