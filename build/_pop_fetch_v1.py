# THE LANE-1 POP-FETCH v2: real Census PEP state-pops (SUMLEV 040) + city-pops (SUMLEV 162) 2019-2025, keyless.
# populations_states_v1.jsonl + populations_cities_v2.jsonl. Law: fetch-or-fail, never placeholder.
import urllib.request, urllib.error, json, csv, io, time, datetime

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
UA = {'User-Agent': 'Mozilla/5.0 (research; keyless census use)'}
HDR = ('POP-FETCH v1 REPRODUCIBILITY HEADER. states 2020-2025 = Census PEP vintage-2025 annual resident-population '
       'estimates (SUMLEV 040, POPESTIMATE2020..2025) from NST-EST2025-ALLDATA.csv (www2.census.gov/.../2020-2025/state/totals/); '
       'states 2019 = PEP vintage-2019 sub-est2019_all.csv SUMLEV 040 row. cities 2019 = sub-est2019_all.csv SUMLEV 162 '
       '(POPESTIMATE2019); cities 2020-2025 = vintage-2025 sub-est2025_<fips>.csv SUMLEV 162 per-state files (same '
       'sub-est lane as populations_wide_v1.jsonl). 2026 deliberately ABSENT: Census PEP has no 2026 vintage published '
       '(no fabrication). Built ' + datetime.date.today().isoformat() + ' by _pop_fetch_v1.py.')

STATES = {'NY': 'New York', 'MO': 'Missouri', 'PA': 'Pennsylvania', 'TN': 'Tennessee',
          'OH': 'Ohio', 'MI': 'Michigan', 'OK': 'Oklahoma', 'LA': 'Louisiana'}
STATE_FIPS = {'NY': '36', 'MO': '29', 'PA': '42', 'TN': '47', 'OH': '39',
              'MI': '26', 'OK': '40', 'LA': '22'}
STATE_OF_CITY = {'New York': 'NY', 'Pittsburgh': 'PA', 'Memphis': 'TN', 'Cincinnati': 'OH',
                 'Detroit': 'MI', 'Oklahoma City': 'OK', 'New Orleans': 'LA'}

def fetch(url, tries=3, timeout=150):
    last = None
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
            return r.read().decode('latin-1'), None   # sub-est files are cp1252-ish; latin-1 never throws
        except Exception as e:
            last = str(e); time.sleep(2)
    return None, last

failures = []
state_rows, city_rows = [], []

# ---------- STATES 2020-2025: vintage-2025 ALLDATA ----------
ST25 = 'https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/state/totals/NST-EST2025-ALLDATA.csv'
txt, err = fetch(ST25)
if txt is None:
    failures.append(('NST-EST2025-ALLDATA', ST25, err)); print('STATE25 FAIL:', err)
else:
    open(B + '_pop_nst_est2025_alldata_cache.csv', 'w', encoding='utf-8').write(txt)
    want = {v.upper(): k for k, v in STATES.items()}
    for row in csv.DictReader(io.StringIO(txt)):
        name = (row.get('NAME') or '').strip().upper()
        if (row.get('SUMLEV') or '').strip() == '40' or name in want:
            ab = want.get(name)
            if not ab:
                continue
            for y in range(2020, 2026):
                col = f'POPESTIMATE{y}'
                if row.get(col):
                    state_rows.append({'state_abbr': ab, 'state_name': row.get('NAME','').strip(), 'year': int(y),
                                       'population': int(row[col]),
                                       'measure': 'PEP vintage-2025 annual state resident population estimate (July 1)',
                                       'sumlev': '40', 'source_file': 'NST-EST2025-ALLDATA.csv',
                                       'source_url': ST25, 'source_vintage': 'PEP vintage-2025'})

# ---------- STATES 2019: vintage-2019 sub-est SUMLEV 40 ----------
SUB19 = 'https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/cities/totals/sub-est2019_all.csv'
txt19, e19 = fetch(SUB19)
if txt19 is None:
    failures.append(('sub-est2019_all', SUB19, e19)); print('SUB19 FAIL:', e19)
else:
    open(B + '_pop_sub_est2019_cache.csv', 'w', encoding='utf-8').write(txt19)
    want = {v.upper(): k for k, v in STATES.items()}
    for row in csv.DictReader(io.StringIO(txt19)):
        if (row.get('SUMLEV') or '').strip() != '40':
            continue
        ab = want.get((row.get('NAME') or '').strip().upper())
        if not ab:
            continue
        col = 'POPESTIMATE2019'
        if row.get(col):
            state_rows.append({'state_abbr': ab, 'state_name': row.get('NAME','').strip(), 'year': 2019,
                               'population': int(row[col]),
                               'measure': 'PEP vintage-2019 annual state resident population estimate (July 1)',
                               'sumlev': '40', 'source_file': 'sub-est2019_all.csv', 'source_url': SUB19,
                               'source_vintage': 'PEP vintage-2019'})

# ---------- CITIES 2020-2025: per-state sub-est2025_<fips>.csv ----------
def city_extract(txt, fips2, years, ofile, ourl, vintage):
    out = []
    want_keys = {(STATES[ab], f'{c} city'): (ab, c) for c, ab in STATE_OF_CITY.items()}
    want_keys.update({(STATES[ab], c): (ab, c) for c, ab in STATE_OF_CITY.items()})
    for row in csv.DictReader(io.StringIO(txt)):
        if (row.get('SUMLEV') or '').strip() != '162':
            continue
        st = (row.get('STNAME') or '').strip()
        key = (st, (row.get('NAME') or '').strip())
        if key not in want_keys:
            continue
        ab, cname = want_keys[key]
        pl = (row.get('PLACE') or '').strip()
        mfips = (row.get('STATE') or '').strip().zfill(2) + pl.zfill(5)
        for y in years:
            col = f'POPESTIMATE{y}'
            if row.get(col):
                out.append({'city': cname, 'state': st, 'year': int(y), 'population': int(row[col]),
                            'measure': 'PEP annual city resident population estimate (July 1)', 'sumlev': '162',
                            'place_fips': mfips, 'name_in_file': row.get('NAME','').strip(),
                            'source_file': ofile, 'source_url': ourl, 'source_vintage': vintage})
    return out

for ab, fips in STATE_FIPS.items():
    U = f'https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/cities/totals/sub-est2025_{fips}.csv'
    t, e = fetch(U, tries=2)
    if t is None:
        failures.append((f'sub-est2025_{fips}', U, e)); print(f'CITY25 {ab} FAIL:', e); continue
    open(B + f'_pop_sub_est2025_{fips}_cache.csv', 'w', encoding='utf-8').write(t)
    got = city_extract(t, fips, range(2020, 2026), f'sub-est2025_{fips}.csv', U, 'PEP vintage-2025')
    print(f'{ab} 2020-25 city rows: {len(got)}')
    city_rows += got

# ---------- CITIES 2019: sub-est2019_all (already fetched) ----------
if txt19 is not None:
    got = city_extract(txt19, 'all', [2019], 'sub-est2019_all.csv', SUB19, 'PEP vintage-2019')
    print('2019 city rows:', len(got), sorted(set((r["city"]) for r in got)))
    city_rows += got

for name, rows, fn in (('pop-states', state_rows, 'populations_states_v1.jsonl'),
                       ('pop-cities', city_rows, 'populations_cities_v2.jsonl')):
    with open(B + fn, 'w', encoding='utf-8') as f:
        f.write(json.dumps({'record': 'reproducibility_header', 'header': HDR}) + '\n')
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    yrs = {}
    for r in rows:
        k = (r.get('state_abbr') or r.get('city'), None)
        yrs.setdefault(r.get('state_abbr') or r.get('city'), []).append(r['year'])
    print(f'{fn}: {len(rows)} rows; per-key years:', {k: sorted(v) for k, v in sorted(yrs.items())})
print('FAILURES:', failures if failures else 'none')
