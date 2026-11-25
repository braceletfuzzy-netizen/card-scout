"""
census_universal_parser_v1.py — 387-era universal Census of Governments care/cage parser.

T1-25 CENSUS-PILOT WAVE-2. Pattern proven by the Pittsburgh run (census92_pittsburgh.json
/ pittsburgh_care_cage_series_v1.jsonl), generalized to any (state, city_name, year).

Signature (387-feed-it):
    from census_universal_parser_v1 import parse_city_care_cage
    d = parse_city_care_cage('MO', 'Kansas City', 'cog2012')

Function-code rules (same as fingerprint runs; Census COG classification):
  CARE  = parks/recreation (E61/F61), libraries (E52/F52), health (E32/F32),
          public welfare (E79/F77 + E75/E77), natural resources E59/E60
  CAGE  = police protection (E62/F62), corrections (E04/E05/F04/F05), judicial (E29/F29)
  FIRE  = fire protection (E25/F24, 2012) / E24/F24 (1992 vintage) — flagged separately, NOT in cage.

Data model: Census unit IDs (9-char 1992 / 14-char 2012-style) carry state(2)+type(1)+county(3)+unit(3).
Data sources (all public-use fixed-width, https://www2.census.gov/govs/...):
  cog1992 : estimate/92censusindunit.zip + 92censusindunitdirectory.zip  (1992 Census of Governments)
  cog2012 : local/2012_Individual_Unit_File_Revised.zip -> Fin_Data_2012.zip
            + Fin_GID_2012.zip                                           (2012 survey year)
"""
import os
import re
import zipfile

BUILD_DIR = r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
_CACHE = {}

# ---------------------------------------------------------------------------
# Code dictionaries (from 2012 tech doc + 1992 estimate tech doc, verified in-
# file; the letter encodes the item family: E=current operation, F=capital outlay)
# ---------------------------------------------------------------------------
CARE_CODES = {
    'cog1992': {'E32', 'E52', 'E61', 'E74', 'E75', 'E77', 'E79',
                'F32', 'F52', 'F61', 'F77'},
    'cog2012': {'E32', 'E52', 'E61', 'E79', 'E75', 'E77',
                'F32', 'F52', 'F61', 'F77'},
}
CAGE_CODES = {
    'cog1992': {'E62', 'E04', 'E05', 'E25',
                'F62', 'F04', 'F05'},
    'cog2012': {'E62', 'E04', 'E05', 'E29',
                'F62', 'F04', 'F05', 'F29'},
}
# 1992 vintage: E24 = Fire Protection (estimatetechdoc1992.pdf line 1238);
# 2012 vintage: E25 = Local Fire Protection (E24 = financial admin in 2012+)
FIRE_CODES = {
    'cog1992': {'E24', 'F24'},
    'cog2012': {'E24', 'F24'},
}

FILES = {
    'cog1992': {
        'units': r"_census/92censusindunit_x/92CensusIndUnit.txt",
        'directory': r"_census/92censusindunitdirectory_x/92CensusIndUnitDirectory.txt",
        'url': "https://www2.census.gov/govs/estimate/92censusindunit.zip",
        'gid_len': 9,
    },
    'cog2012': {
        'units': r"_census/fin2012/2012FinEstDAT_08172017modp_pu.txt",
        'directory': r"_census/gid2012/Fin_GID_2012.txt",
        'url': "https://www2.census.gov/govs/local/2012_Individual_Unit_File_Revised.zip",
        'gid_len': 14,
    },
}

# Census 'State code' per census vintage: the 2012+ files use FIPS state codes,
# but the 1992 Census of Governments uses its OWN sequential numbering
# (estimatetechdoc1992.pdf "State Abbreviations": Alabama=01 Missouri=26,
#  Oregon=37, Wisconsin=49 — different from FIPS!).
STATE_FIPS = {'01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA', '08': 'CO',
              '09': 'CT', '10': 'DE', '11': 'DC', '12': 'FL', '13': 'GA', '15': 'HI',
              '16': 'ID', '17': 'IL', '18': 'IN', '19': 'IA', '20': 'KS', '21': 'KY',
              '22': 'LA', '23': 'ME', '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN',
              '28': 'MS', '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH',
              '34': 'NJ', '35': 'NM', '36': 'NY', '37': 'NC', '38': 'ND', '39': 'OH',
              '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI', '45': 'SC', '46': 'SD',
              '47': 'TN', '48': 'TX', '49': 'UT', '50': 'VT', '51': 'VA', '53': 'WA',
              '54': 'WV', '55': 'WI', '56': 'WY'}

STATE_CENSUS_92 = {'AL': '01', 'AK': '02', 'AZ': '03', 'AR': '04', 'CA': '05',
                   'CO': '06', 'CT': '07', 'DE': '08',  'DC': '09', 'FL': '10',
                   'GA': '11', 'HI': '12', 'ID': '13', 'IL': '14', 'IN': '15',
                   'IA': '16', 'KS': '17', 'KY': '18', 'LA': '19', 'ME': '20',
                   'MD': '21', 'MA': '22', 'MI': '23', 'MN': '24', 'MS': '25',
                   'MO': '26', 'MT': '27', 'NE': '28', 'NV': '29', 'NH': '30',
                   'NJ': '31', 'NM': '32', 'NY': '33', 'NC': '34', 'ND': '35',
                   'OH': '36', 'OK': '37', 'OR': '38', 'PA': '39', 'RI': '40',
                   'SC': '41', 'SD': '42', 'TN': '43', 'TX': '44', 'UT': '45',
                   'VT': '46', 'VA': '47', 'WA': '48', 'WV': '49', 'WI': '50',
                   'WY': '51'}


def _ensure_downloads():
    """Idempotent download+unzip; files live under build/_census/."""
    import urllib.request
    base = os.path.join(BUILD_DIR, '_census')
    os.makedirs(base, exist_ok=True)
    have = {
        'cog1992': r"_census/92censusindunit_x/92CensusIndUnit.txt",
        'cog2012': r"_census/fin2012/2012FinEstDAT_08172017modp_pu.txt",
    }
    for yr, rel in have.items():
        if not os.path.exists(os.path.join(BUILD_DIR, rel)):
            if yr == 'cog1992':
                z = '92censusindunit.zip'
                url = FILES['cog1992']['url']
                # also need directory
                ud = "https://www2.census.gov/govs/estimate/92censusindunitdirectory.zip"
                zd = '92censusindunitdirectory.zip'
            else:
                z = '2012_Individual_Unit_File_Revised.zip'
                url = FILES['cog2012']['url']
                ud = "https://www2.census.gov/govs/local/Fin_GID_2012.zip"
                zd = 'Fin_GID_2012.zip'
            for zf, u in ((z, url), (zd, ud)):
                p = os.path.join(base, zf)
                if not os.path.exists(p):
                    urllib.request.urlretrieve(u, p)
                with zipfile.ZipFile(p) as zf_:
                    zf_.extractall(os.path.join(base, zf_._namelist()[0].split('/')[0]))
                # unzip nested zips
                top = os.path.join(base, zf.replace('.zip', '_x'))
                if os.path.isdir(top):
                    for f2 in os.listdir(top):
                        if f2.lower().endswith('.zip'):
                            with zipfile.ZipFile(os.path.join(top, f2)) as z2:
                                z2.extractall(os.path.join(base, f2.replace('.zip', '')))


_CACHE_GID = {}


ABBR_TO_FIPS = {v: k for k, v in STATE_FIPS.items()}  # 2012 files carry FIPS state codes


def find_entity_id(state_abbr, city_name, year='cog2012'):
    """Look up the census entity (GID) id by CITY NAME inside the GID directory.
    Returns the exact 14-char (2012) or 9-char (1992) unit id, or None if not found."""
    cfg = FILES[year]
    if year == 'cog1992':
        state_code = STATE_CENSUS_92[state_abbr.upper()]  # census-own numbering, NOT FIPS
    else:
        state_code = ABBR_TO_FIPS[state_abbr.upper()]
    dirpath = os.path.join(BUILD_DIR, cfg['directory'])
    if year not in _CACHE_GID:
        _CACHE_GID[year] = open(dirpath, encoding='latin-1').read().splitlines()
    rows = _CACHE_GID[year]
    # 2012 layout: [0:14]=gid, [14:78]=name, [113:115]=state_fips
    # 1992 layout: [0:9]=gid, [9:65]=name
    wanted = re.sub(r'[^A-Z ]', '', city_name.upper()).strip()
    for l in rows:
        if year == 'cog2012':
            gid, nm, st = l[:14], l[14:78].strip(), l[113:115]
        else:
            gid, nm, st = l[:9], l[9:65].strip(), l[:2]
        nm_clean = re.sub(r'[^A-Z ]', '', nm.upper()).strip()
        if st != state_code:
            continue
        # 'CITY' type = municipal; require the token 'CITY' in the name for a
        # municipality lookup (1992 'MILWAUKEE CITY', 'PORTLAND CITY', 'KANSAS CITY').
        if nm_clean == wanted or nm_clean == wanted + ' CITY':
            return gid
    return None


def parse_city_care_cage(state, city_name, census_file_year, verbose=False):
    """
    387-feed-it signature. census_file_year: 'cog2012' or 'cog1992' (also accepts
    '2012' / '1992'). Returns dict:
    {city, state, entity_id, care_usd_total, cage_usd_total, fire_flagged_usd,
     rows_care, rows_cage, rows_fire, source_file, data_quality, notes, honest_gaps, ratio}
    """
    ymap = {'2012': 'cog2012', '1992': 'cog1992', 'cog2012': 'cog2012', 'cog1992': 'cog1992'}
    y = ymap[str(census_file_year)]
    cfg = FILES[y]
    gid = find_entity_id(state, city_name, y)
    if not gid:
        return {'city': city_name, 'state': state, 'entity_id': None,
                'care_usd_total': None, 'cage_usd_total': None, 'fire_flagged_usd': None,
                'rows_care': [], 'rows_cage': [], 'rows_fire': [],
                'source_file': cfg['url'], 'data_quality': 'MISSING',
                'notes': f'{city_name} {state}: entity {y} record not found in GID directory',
                'honest_gaps': ['entity not in file']}
    unitpath = os.path.join(BUILD_DIR, cfg['units'])
    care_codes = CARE_CODES[y]
    cage_codes = CAGE_CODES[y]
    fire_codes = FIRE_CODES[y]
    care, cage, fire = {}, {}, {}
    for line in open(unitpath, encoding='latin-1'):
        l = line.rstrip('\n\r')
        u = l[:14] if y == 'cog2012' else l[:9]
        if u != gid:
            continue
        # 2012 record layout: [14:17] item, [17:29] amount (thousands), [29:33] year, [33] flag
        # 1992 record layout: identical, just 9-char gid prefix -> item at [9:12]... (fallback by split)
        if y == 'cog2012':
            code, amt = l[14:17], l[17:29].strip()
        else:
            code, amt = l[14:17], l[17:29].strip()
        try:
            v = int(amt)
        except ValueError:
            continue
        if code in care_codes:
            care[code] = care.get(code, 0) + v
        elif code in cage_codes:
            cage[code] = cage.get(code, 0) + v
        elif code in fire_codes:
            fire[code] = fire.get(code, 0) + v
    # Census public-use files report in THOUSANDS of dollars — x1000 to dollars
    K = 1000
    care_total = sum(care.values()) * K
    cage_total = sum(cage.values()) * K
    fire_total = sum(fire.values()) * K
    rows_care = [f"{c} ${care[c]*K/1e6:.1f}M" for c in sorted(care)]
    rows_cage = [f"{c} ${cage[c]*K/1e6:.1f}M" for c in sorted(cage)]
    rows_fire = [f"{c} ${fire[c]*K/1e6:.1f}M" for c in sorted(fire)]
    src_label = ("1992 Census of Governments, Vol 4 No 4 individual-unit public-use file"
                 if y == 'cog1992' else
                 "2012 Census of Governments Annual Survey of Public Finances (state & local), individual-unit public-use file")
    # quality: 2012 file is the Revised (post-imputation) survey-year file, reported+imputed
    missing_care = [c for c in ('E61', 'E32', 'E52') if c not in care]
    missing_cage = [c for c in ('E62',) if c not in cage]
    gaps = [f"missing-care-func codes {missing_care}" if missing_care else "",
            f"missing-cage-func codes {missing_cage}" if missing_cage else "",
            "corrections/jail mostly county-level in all 3 states — city cage is police-dominated"]
    gaps = [g for g in gaps if g]
    # 1992 code E66 = protective inspection; E29 = judicial; E04/E05 = corrections
    notes = {
        'cog1992': "1992 Census vintage dictionary: E24=Fire Protection, E25=Judicial, "
                   "E29=Central Staff, E36/E38=Hospitals (estimatetechdoc1992.pdf; "
                   "state codes are census-own numbering: MO=26 OR=37 WI=49).",
        'cog2012': "2012 vintage dictionary: E25=Financial Admin, E24=Local Fire Protection, "
                   "E29=Judicial; FIPS state codes (2012-sl-indiv-unit-data-file-tech-doc.pdf).",
    }[y]
    return {'city': city_name, 'state': state, 'entity_id': gid,
            'care_usd_total': care_total, 'cage_usd_total': cage_total,
            'fire_flagged_usd': fire_total,
            'rows_care': rows_care, 'rows_cage': rows_cage, 'rows_fire': rows_fire,
            'source_file': cfg['url'] + f"  (unit {gid})",
            'data_quality': "High (1992 Census of Governments, full-coverage city data)"
                            if y == 'cog1992' else
                            "Medium (2012 annual survey file: reported + imputed items)",
            'notes': notes, 'honest_gaps': gaps,
            'ratio': round(care_total / cage_total, 3) if cage_total else None}


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    _ensure_downloads()
    import json
    out_path = os.path.join(BUILD_DIR, 't1_census_pilot_v1.jsonl')
    pilot = [('MO', 'Kansas City', '2012'), ('WI', 'Milwaukee', '2012'),
             ('OR', 'Portland', '2012'), ('MO', 'Kansas City', '1992'),
             ('WI', 'Milwaukee', '1992'), ('OR', 'Portland', '1992')]
    lines_out = []
    print("\n%-16s %-13s %14s %14s %7s %s" %
          ("city", "entity_id", "care", "cage", "ratio", "quality"))
    print("-" * 80)
    for st, c, yr in pilot:
        key = {'2012': 'cog2012', '1992': 'cog1992'}[yr]
        d = parse_city_care_cage(st, c, yr)
        d['source_file'] = FILES[key]['url'] + f"  (unit {d['entity_id']})"
        lines_out.append(d)
        print("%-16s %-13s %14s %14s %7s %s" %
              (f"{c} {st} {yr}", d['entity_id'],
               f"${(d['care_usd_total'] or 0)/1e6:,.1f}M",
               f"${(d['cage_usd_total'] or 0)/1e6:,.1f}M",
               d['ratio'], d['data_quality'][:40]))
        print(f"    fire_flagged=${(d['fire_flagged_usd'] or 0)/1e6:,.1f}M  care_rows={d['rows_care']}  cage_rows={d['rows_cage']}")
        if d['honest_gaps']:
            print(f"    gaps: {d['honest_gaps']}")
    with open(out_path, 'w') as f:
        for d in lines_out:
            f.write(json.dumps(d) + "\n")
    print("\nwrote", out_path, len(lines_out), "rows")
