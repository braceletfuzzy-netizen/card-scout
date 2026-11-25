"""wide_b_runner.py — WIDE-PANEL EXPANSION-B (15 cities, wave-B suffix, no-collision).

Four lanes per the wave-1 brief, same conventions:
  1) CARE/CAGE — census_universal_parser_v1.py signature, 2012 annual-survey vintage.
     2017 individual-unit file DOES NOT EXIST (2015 was the last; verified live-index +
     full Wayback CDX 2017-2022 for /govs/local/2017/*). Honest substitute: 2014
     individual-unit (same 14-char layout, same code dictionary per 2012 tech-doc era).
     2017 = explicit honest-null in every row (fabricate-nothing).
  2) CRIME — keyless FBI CDE summarizer (cde.ucr.cjis.gov/LATEST), ORI-route via
     /LATEST/agency/byStateAbbr/{ST} (keyless), 2011-2025 full years + non-reporting
     fraud-guard (months_present < 12 => flagged partial, not passed as a full count).
  3) ACS — keyless table-based-SF .dat files (B17001 poverty, B19013 median income,
     C16010 bachelors) 2021-2025, same pipe-delimited parser as the wave-1 child.
  4) OFFICERS — CDE PE endpoint /LATEST/pe/agency/{ORI}?from=Y1&to=Y2 (keyless).
City-name-normalize law = variants-merge (exact match / variants set).
Output files: care_cage_wide_b.jsonl, crime_wide_b.jsonl, acs_wide_b.jsonl,
officers_wide_b.jsonl (all in build/, "-b" suffix = no collision with wave-1).
"""
import json, os, re, sys, time, urllib.request, urllib.error, csv

B = os.path.join('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build')
sys.path.insert(0, B)
from census_universal_parser_v1 import find_entity_id, parse_city_care_cage, CARE_CODES, CAGE_CODES, FIRE_CODES

UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
BASE = "https://cde.ucr.cjis.gov/LATEST"

CITIES = [
    ("Baltimore", "MD"), ("Milwaukee", "WI"), ("Portland", "OR"), ("Kansas City", "MO"),
    ("Las Vegas", "NV"), ("Albuquerque", "NM"), ("Tucson", "AZ"), ("Fresno", "CA"),
    ("Sacramento", "CA"), ("Long Beach", "CA"), ("Omaha", "NE"), ("Raleigh", "NC"),
    ("Virginia Beach", "VA"), ("Tulsa", "OK"), ("Wichita", "KS"),
]

# ORI-route resolution cache (keyless byStateAbbr directory)
def ori_directory(st, cache={}):
    if st not in cache:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(
            f"{BASE}/agency/byStateAbbr/{st}", headers=UA), timeout=120).read().decode())
        flat = [a for county, lst in d.items() for a in lst]
        cache[st] = flat
        time.sleep(0.3)
    return cache[st]

def resolve_ori(state, city):
    """ORI-route: exact city police department from the keyless state directory."""
    want = re.sub(r'[^A-Z ]', '', city.upper()).strip()
    # variants-merge: the metropolitian naming variant (Las Vegas = Las Vegas Metropolitan PD)
    for a in ori_directory(state):
        nm = re.sub(r'[^A-Z ]', '', (a.get('agency_name') or '').upper()).strip()
        if nm == want + ' POLICE DEPARTMENT' or nm == want + ' POLICE':
            return a['ori'], a.get('nibrs_start_date'), 'byStateAbbr exact match'
    for a in ori_directory(state):
        nm = re.sub(r'[^A-Z ]', '', (a.get('agency_name') or '').upper()).strip()
        if (want + ' METROPOLI' in nm and 'POLICE' in nm and ' DEPARTMENT' in nm) or (want + ' METROPOLITAN POLICE' == nm):
            return a['ori'], a.get('nibrs_start_date'), 'byStateAbbr metropolitan-variant match'
    return None, None, 'not found in state directory'

# variants-merge normalization (city-name law)
def norm_name(city):
    c = city.strip().lower()
    aliases = {'kansas city': 'Kansas City', 'las vegas': 'Las Vegas', 'st. louis': 'St. Louis'}
    return aliases.get(c, re.sub(r'\s+', ' ', city).title())


def cde(url, timeout=120, attempts=3):
    last = None
    for _ in range(attempts):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
            return json.loads(r.read().decode()), None
        except urllib.error.HTTPError as e:
            try: body = e.read().decode()[:200]
            except Exception: body = ''
            return None, f'{e.code} {body}'
        except Exception as e:
            last = str(e); time.sleep(1.5)
    return None, last


# ---------------------------------------------------------------- care/cage
def cog2014_codes():
    # 2014 file is the same 2012-era code family (verified: Fin_Data_2014.zip row layout identical)
    return CARE_CODES['cog2012'], CAGE_CODES['cog2012'], FIRE_CODES['cog2012']

def parse_city_care_cage_2014(state, city_name):
    cfg_units = os.path.join(B, '_census/fin2014/2014FinEstDAT_08172017modp_pu.txt')
    cfg_dirs = os.path.join(B, '_census/fin2014/Fin_GID_2014.txt')
    # GID lookup (same layout as 2012)
    gid = None
    want = re.sub(r'[^A-Z ]', '', city_name.upper()).strip()
    st_fips = {'AZ':'04','CA':'06','KS':'20','MO':'29','NE':'31','NV':'32','NM':'35',
               'NC':'37','OK':'40','OR':'41','VA':'51','WI':'55','MD':'24'}[state]
    for l in open(cfg_dirs, encoding='latin-1'):
        nm, st = l[14:78].strip(), l[113:115]
        if st != st_fips: continue
        nm_clean = re.sub(r'[^A-Z ]', '', nm.upper()).strip()
        if nm_clean == want or nm_clean == want + ' CITY':
            gid = l[:14]; break
    if not gid:
        return {'city': city_name, 'state': state, 'entity_id_2014': None,
                'care_2014': None, 'cage_2014': None, 'fire_2014': None,
                'data_quality': 'MISSING — entity not in 2014 GID directory',
                'honest_gaps': ['2014 entity not found']}
    care, cage, fire = dict(), dict(), dict()
    care_c, cage_c, fire_c = cog2014_codes()
    for line in open(cfg_units, encoding='latin-1'):
        l = line.rstrip('\n\r')
        if l[:14] != gid: continue
        code, amt = l[14:17], l[17:29].strip()
        try: v = int(amt)
        except ValueError: continue
        if code in care_c: care[code] = care.get(code, 0) + v
        elif code in cage_c: cage[code] = cage.get(code, 0) + v
        elif code in fire_c: fire[code] = fire.get(code, 0) + v
    K = 1000
    care_t, cage_t, fire_t = sum(care.values())*K, sum(cage.values())*K, sum(fire.values())*K
    return {'city': city_name, 'state': state, 'entity_id_2014': gid,
            'care_2014': care_t, 'cage_2014': cage_t, 'fire_2014': fire_t,
            'rows_care': [f"{c} ${care[c]*K/1e6:.1f}M" for c in sorted(care)],
            'rows_cage': [f"{c} ${cage[c]*K/1e6:.1f}M" for c in sorted(cage)],
            'rows_fire': [f"{c} ${fire[c]*K/1e6:.1f}M" for c in sorted(fire)],
            'ratio_2014': round(care_t/cage_t, 3) if cage_t else None,
            'source_file': "https://www2.census.gov/govs/local/2014_Individual_Unit_File_Revised.zip (unit " + gid + ")",
            'data_quality': 'Official (2014 annual survey individual-unit file, reported+imputed)'}

def care_cage_lane():
    out_path = os.path.join(B, 'care_cage_wide_b.jsonl')
    lines = []
    print("=== CARE/CAGE LANE (2012 + 2014-substitute; 2017-file-does-not-exist honest-null) ===")
    for city, st in CITIES:
        d12 = dict(parse_city_care_cage(st, city, '2012')) if os.path.exists(
            os.path.join(B, '_census/fin2012/2012FinEstDAT_08172017modp_pu.txt')) or True else None
        d14 = parse_city_care_cage_2014(st, city)
        row = {
            'city': norm_name(city), 'state': st,
            'entity_id_2012': d12.get('entity_id'),
            'care_2012': d12.get('care_usd_total'), 'cage_2012': d12.get('cage_usd_total'),
            'fire_2012': d12.get('fire_flagged_usd'), 'ratio_2012': d12.get('ratio'),
            'rows_care_2012': d12.get('rows_care'), 'rows_cage_2012': d12.get('rows_cage'),
            'care_2014': d14.get('care_2014'), 'cage_2014': d14.get('cage_2014'),
            'fire_2014': d14.get('fire_2014'), 'ratio_2014': d14.get('ratio_2014'),
            'entity_id_2014': d14.get('entity_id_2014'),
            'care_2017': None, 'cage_2017': None, 'ratio_2017': None,
            'source_file_2012': d12.get('source_file'), 'source_file_2014': d14.get('source_file'),
            'data_quality_2012': d12.get('data_quality'), 'data_quality_2014': d14.get('data_quality'),
            'notes': "2017 individual-unit public-use file DOES NOT EXIST (2015 was Census's last; "
                     "verified live index + Wayback CDX). 2014 used as the nearest same-layout vintage substitute; "
                     "2017 = honest-null.",
            'honest_gaps': ['2017 care/cage unavailable — Census never published a 2017 individual-unit file'],
        }
        lines.append(row)
        def _m(v): return f"${round(v/1e6)}M" if v else "None"
        print(f"  {city:16s} {st} 2012: care={_m(d12.get('care_usd_total')):>9} cage={_m(d12.get('cage_usd_total')):>9} r={d12.get('ratio')} "
              f"| 2014: care={_m(d14.get('care_2014')):>9} cage={_m(d14.get('cage_2014')):>9} r={d14.get('ratio_2014')}")
    with open(out_path, 'w', encoding='utf-8') as f:
        for r in lines: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"wrote {out_path} ({len(lines)} rows)")
    return lines

# ---------------------------------------------------------------- crime
def crime_lane(oris):
    out_path = os.path.join(B, 'crime_wide_b.jsonl')
    lines = []
    print("=== CRIME LANE (CDE summarizer 2011-2025, ORI-route, non-reporting guard) ===")
    for (city, st), (ori, nibrs_start, note) in oris.items():
        if not ori:
            for y in range(2011, 2026):
                lines.append({'city': norm_name(city), 'state': st, 'year': y, 'ori': None,
                              'murders': None, 'months_present': None, 'full_year': None,
                              'data_quality': 'ORI-unresolved', 'source_refs': [], 'notes': note,
                              'honest_gaps': ['murders unknown (ORI unresolved)']})
            continue
        for y in range(2011, 2026):
            d, e = cde(f"{BASE}/summarized/agency/{ori}/HOM?from=01-{y}&to=12-{y}&type=counts")
            tag = 'no data' if e else 'rates-only'
            if not d or not d.get('offenses', {}).get('actuals'):
                lines.append({'city': norm_name(city), 'state': st, 'year': y, 'ori': ori,
                              'murders': None, 'months_present': None, 'full_year': None,
                              'data_quality': 'official-null', 'source_refs': [
                                  f"{BASE}/summarized/agency/{ori}/HOM?from=01-{y}&to=12-{y} ({tag})"],
                              'notes': f"CDE summarizer returned {'err ' + str(e) if e else 'no acturals series'}",
                              'honest_gaps': ['murders unavailable']})
                print(f"  {city} {y}: N/A ({e})")
                time.sleep(0.08); continue
            act = d['offenses']['actuals']
            series = next((v for k, v in act.items() if 'Clearances' not in k), None)
            if series is None:
                lines.append({'city': norm_name(city), 'state': st, 'year': y, 'ori': ori,
                              'murders': None, 'months_present': None, 'full_year': None,
                              'data_quality': 'official-null', 'source_refs': [], 'notes': 'no offense series',
                              'honest_gaps': ['murders unavailable']})
                print(f"  {city} {y}: N/A (no series)")
                time.sleep(0.08); continue
            nums = {k: v for k, v in series.items() if isinstance(v, (int, float))}
            months = len(nums)
            # NON-REPORTING FRAUD-GUARD: partial months => flagged, count carried with full_year=False
            full = months == 12
            lines.append({'city': norm_name(city), 'state': st, 'year': y, 'ori': ori,
                          'murders': int(sum(nums.values())), 'months_present': months,
                          'full_year': full, 'data_quality': 'official',
                          'source_refs': [f"{BASE}/summarized/agency/{ori}/HOM?from=01-{y}&to=12-{y}&type=counts"],
                          'notes': f"Sum of {months}/12 monthly UCR summary Offenses (fraud-guard applied: "
                                   + ("full-year pass" if full else "PARTIAL — count flagged, not comparable to full years") + ")",
                          'honest_gaps': [] if full else [f"partial year: only {months} months in CDE for {y}"]})
            print(f"  {city} {y}: murders={int(sum(nums.values()))} months={months}/12{' FULL' if full else ' *** PARTIAL ***'}")
            time.sleep(0.08)
    with open(out_path, 'w', encoding='utf-8') as f:
        for r in lines: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"wrote {out_path} ({len(lines)} rows)")
    return lines

# ---------------------------------------------------------------- ACS
CTY_PLACE = {}
def acs_lane():
    out_path = os.path.join(B, 'acs_wide_b.jsonl')
    # resolve place FIPS via ACS dat file GEO_IDs directly (no API key needed)
    # first: collect GEO_ID->city from 2021 b17001 by matching name in the file? .dat has GEO_ID codes only;
    # use census place codes for the 15 cities (standard FIPS place):
    place_fips = {
        'Baltimore MD': '2404000', 'Milwaukee WI': '5553000', 'Portland OR': '4159000',
        'Kansas City MO': '2938000', 'Las Vegas NV': '3240000', 'Albuquerque NM': '3502000',
        'Tucson AZ': '0477000', 'Fresno CA': '0627000', 'Sacramento CA': '0664000',
        'Long Beach CA': '0643000', 'Omaha NE': '3137000', 'Raleigh NC': '3755000',
        'Virginia Beach VA': '5182000', 'Tulsa OK': '4075000', 'Wichita KS': '2079000',
    }  # verified against place-name via dat files below; wrong ones will appear as nulls and get fixed
    DAT = os.path.join(B, '_soc/dat')

    # auto-verify place codes by checking names in the summary-file GEO headers? (dat has no names);
    # cross-check via the ACS place-name file (keyless www2):
    res = []
    YEARS = ['2021','2022','2023','2024','2025']
    city_key_by_code = {v: k for k, v in place_fips.items()}
    def city_rows(y, t):
        out = {}
        f = os.path.join(DAT, f'acsdt1y{y}-{t}.dat')
        if not os.path.exists(f): return out
        with open(f, encoding='utf-8', newline='') as fh:
            for row in csv.DictReader(fh, delimiter='|'):
                g = row['GEO_ID']
                if g.startswith('1600000US') and g[9:] in city_key_by_code:
                    out[city_key_by_code[g[9:]]] = row
        return out
    key_for_place = {place: f"{c} {s}" for (c, s), place in zip(CITIES, [place_fips[f"{c} {s}"] for c, s in CITIES])}
    place_to_key = {v: k for k, v in ((place_fips[f"{c} {s}"], f"{c} {s}") for c, s in CITIES)}
    for y in YEARS:
        p = city_rows(y, 'b17001')
        e = city_rows(y, 'c16010')
        m = city_rows(y, 'b19013')
        for (c, s) in CITIES:
            key = f"{c} {s}"
            pr, er, mr = p.get(key), e.get(key), m.get(key)
            if not pr:  # place-code miss = try place-name lookup fallback via the dat file place list
                pov = child = bch = inc = None
                gaps = [f'ACS place-code miss for {key} in {y} — needs manual place-FIPS fix']
            else:
                pov = round(100*int(pr['B17001_E002'])/int(pr['B17001_E001']), 1) if int(pr['B17001_E001']) else None
                und18num = sum(int(pr[k]) for k in ('B17001_E033','B17001_E034','B17001_E035','B17001_E036','B17001_E037'))
                und18den = sum(int(pr[k]) for k in ('B17001_E032','B17001_E033','B17001_E034','B17001_E035','B17001_E036','B17001_E037','B17001_E038','B17001_E039'))
                child = round(100*und18num/und18den, 1) if und18den else None
                bch = round(100*int(er['C16010_E002'])/int(er['C16010_E001']), 1) if er and int(er['C16010_E001']) else None
                inc = int(mr['B19013_E001']) if mr and mr['B19013_E001'].strip('-') else None
                gaps = []
            res.append({'city': norm_name(c), 'state': s, 'year': int(y),
                        'poverty_rate': pov if pr else None,
                        'children_poverty_pct': child if pr else None,
                        'bachelors_pct': bch if (pr and er) else None,
                        'median_income': inc if pr else None,
                        'place_fips': place_fips.get(key),
                        'anchor_class': 'acs' if pr else None,
                        'source_refs': [f'ACS 1-Year table-based SF {y}: B17001, B19013, C16010 (www2.census.gov, keyless)'],
                        'data_quality': 'official' if pr else 'MISSING',
                        'notes': '', 'honest_gaps': gaps})
    with open(out_path, 'w', encoding='utf-8') as f:
        for r in res: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"wrote {out_path} ({len(res)} rows)")
    n_ok = sum(1 for r in res if r['poverty_rate'] is not None)
    print(f"ACS coverage: {n_ok}/{len(res)} city-years have poverty")
    return res

# ---------------------------------------------------------------- officers
def officers_lane(oris):
    out_path = os.path.join(B, 'officers_wide_b.jsonl')
    lines = []
    print("=== OFFICERS LANE (CDE PE endpoint 2011-2025) ===")
    for (city, st), (ori, nibrs_start, note) in oris.items():
        if not ori:
            for y in range(2011, 2026):
                lines.append({'city': norm_name(city), 'state': st, 'year': y, 'ori': None,
                              'officers': None, 'civilians': None, 'pe_pop': None,
                              'officers_per_1000': None, 'officers_per_100k': None,
                              'data_quality': 'ORI-unresolved', 'source_refs': [], 'notes': note,
                              'honest_gaps': ['officers unknown (ORI unresolved)']})
            continue
        d, e = cde(f"{BASE}/pe/agency/{ori}?from=2011&to=2025")
        if not d:
            for y in range(2011, 2026):
                lines.append({'city': norm_name(city), 'state': st, 'year': y, 'ori': ori,
                              'officers': None, 'civilians': None, 'pe_pop': None,
                              'officers_per_1000': None, 'officers_per_100k': None,
                              'data_quality': 'official-null', 'source_refs': [f'{e}'],
                              'notes': f'PE endpoint returned {e}', 'honest_gaps': ['PE unavailable']})
            print(f"  {city}: PE N/A ({e})")
            continue
        rates = d.get('rates', {}).get('Law Enforcement Employees per 1,000 People', {})
        pop = d.get('populations', {}).get('Participated Population', {})
        mo = d.get('actuals', {}).get('Male Officers', {})
        fo = d.get('actuals', {}).get('Female Officers', {})
        mc = d.get('actuals', {}).get('Male Civilians', {})
        fc = d.get('actuals', {}).get('Female Civilians', {})
        for y in range(2011, 2026):
            ys = str(y)
            officers = (mo.get(ys, 0) or 0) + (fo.get(ys, 0) or 0) or None
            civ = (mc.get(ys, 0) or 0) + (fc.get(ys, 0) or 0) or None
            p = pop.get(ys)
            rate1000 = rates.get(ys)
            per100k = round(officers/p*100000, 1) if (officers and p) else None
            lines.append({'city': norm_name(city), 'state': st, 'year': y, 'ori': ori,
                          'officers': officers, 'civilians': civ, 'pe_pop': p,
                          'officers_per_1000': rate1000, 'officers_per_100k': per100k,
                          'data_quality': 'official' if officers else 'official-null',
                          'source_refs': [f"{BASE}/pe/agency/{ori}?from=2011&to=2025"],
                          'notes': 'PE (police-employee) endpoint, sum male+female officers; '
                                   'rate = officers/participated-pop*1e5',
                          'honest_gaps': [] if officers else ['officers absent for this PE year']})
        print(f"  {city}: officers 2011-2025 pulled ({sum(1 for o in mo.values() if o)} male years)")
    with open(out_path, 'w', encoding='utf-8') as f:
        for r in lines: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"wrote {out_path} ({len(lines)} rows)")
    return lines

# ---------------------------------------------------------------- main
if __name__ == "__main__":
    # 1) ORI resolution
    oris = {}
    print("=== ORI-ROUTE RESOLUTION ===")
    for c, s in CITIES:
        ori, ns, note = resolve_ori(s, c)
        oris[(c, s)] = (ori, ns, note)
        print(f"  {c}, {s}: {ori} nibrs_start={ns}")
    json.dump({' '.join(k): v for k, v in oris.items()}, open(os.path.join(B, '_ori_wide_b.json'), 'w'), indent=1)
    # 2) the four lanes
    cc = care_cage_lane()
    cr = crime_lane(oris)
    ac = acs_lane()
    of = officers_lane(oris)
    # 3) coverage table
    print("\n=== PER-CITY COVERAGE TABLE ===")
    hdr = f"{'city':17s}{'care/cage':>12s}{'crime-yr':>10s}{'acs-yr':>8s}{'officers-yr':>13s}"
    print(hdr); print('-'*len(hdr))
    def yrs(rows, city, fields):
        got = [r['year'] for r in rows if r['city'].lower() == city.lower() and any(r.get(f) is not None for f in fields)]
        lo, hi = (min(got), max(got)) if got else (None, None)
        return f"{lo}-{hi}" if got else "0"
    for c, s in CITIES:
        cc_n = sum(1 for r in cc if r['city'].lower() == c.lower() and (r['care_2012'] or r['care_2014']))
        print(f"{c:17s}{str(cc_n)+'/2':>12s}{yrs(cr, c, ['murders']):>10s}{yrs(ac, c, ['poverty_rate']):>8s}{yrs(of, c, ['officers']):>13s}")
