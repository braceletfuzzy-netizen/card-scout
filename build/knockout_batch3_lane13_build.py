# LANE-13 — THE TRANSPORT-LEVER (one-pager #3, the founder's transport-to-opportunity queue-line)
# Deliverable: the Memphis commute/transport-access table vs comparison set, ACS 5yr 2022, keyless www2.census.gov table-based-SF .dat files.
# Tables: B08303 (travel time dist), B08301 (means of transport), B08013 (aggregate travel time by sex -> overall mean), B08136 (agg travel time by VEHICLES AVAILABLE = the income-proxy band), B08141 (means of transport by veh availability)
# Laws: no fabricated rows; honest-null per failed route; direction-class only; provenance + confidence tags per row.
import urllib.request, json, io, time
from pathlib import Path

B = Path('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build')
YR = '2022'
BASE = f'https://www2.census.gov/programs-surveys/acs/summary_file/{YR}/table-based-SF/data/5YRData/acsdt5y{YR}-'

COUNTIES = {  # anchor + comparison set (county = the commute-shed grain)
 '0500000US47157' : 'Memphis (Shelby County, TN)',
 '0500000US29510' : 'St. Louis County, MO',
 '0500000US39061' : 'Cincinnati (Hamilton County, OH)',
 '0500000US26163' : 'Detroit (Wayne County, MI)',
 '0500000US17031' : 'Chicago (Cook County, IL)',
 '0500000US48453' : 'San Antonio (Bexar County, TX)',
 '0500000US12086' : 'Jacksonville (Duval County, FL)',
 '0500000US40109' : 'Oklahoma City (Oklahoma County, OK)',
 '0500000US42101' : 'Philadelphia County, PA',
 '0500000US06075' : 'San Francisco County, CA',
}
CITYPROPER = {  # city-place grain for the 4 anchors (the service-decision geo)
 '1600000US4748000' : 'Memphis city, TN',
 '1600000US2966000' : 'St. Louis city, MO',
 '1600000US3915000' : 'Cincinnati city, OH',
 '1600000US2622000' : 'Detroit city, MI',
}
GEOALL = {**COUNTIES, **CITYPROPER}

TABLES = ['b08303','b08301','b08013','b08136','b08141']

def fetch_dat(tid):
    url = BASE + tid + '.dat'
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read().decode('utf-8-sig', errors='replace')
        except Exception as e:
            err = f'{type(e).__name__}: {str(e)[:120]}'
            time.sleep(4)
    return None

def parse_dat(txt):
    lines = txt.splitlines()
    hdr = lines[0].split('|')
    recs = {}
    for line in lines[1:]:
        parts = line.split('|')
        if len(parts)!=len(hdr): continue
        d = dict(zip(hdr, parts))
        recs[d['GEO_ID']] = {k:v for k,v in d.items() if k.endswith('E') or k=='GEO_ID'}
    return recs

def num(d, key):
    v = d.get(key, '')
    try: return float(v)
    except Exception: return None

def fnum(s):
    try: return float(s)
    except Exception: return None

rows = []
audit = {}
for tid in TABLES:
    txt = fetch_dat(tid)
    if txt is None:
        audit[tid] = 'HONEST-NULL: fetch failed 3x'
        continue
    recs = parse_dat(txt)
    audit[tid] = f'captured: {len(recs)} geo rows'
    time.sleep(1)
print('AUDIT:', json.dumps(audit, indent=1))

tbl = {}
for tid in TABLES:
    if audit[tid].startswith('captured'):
        txt = fetch_dat(tid)
        tbl[tid] = parse_dat(txt)
        time.sleep(1)

for geo, name in GEOALL.items():
    r = {'geo_id': geo, 'geo_name': name, 'grain': 'county' if geo in COUNTIES else 'city-proper'}
    # travel time distribution B08303 (13 cols)
    d = tbl.get('b08303', {}).get(geo)
    if d:
        t = num(d,'B08303_E001') or 0
        lt10 = num(d,'B08303_E002') or 0
        b15_59 = sum(num(d,f'B08303_E{n:03d}') or 0 for n in range(5,11))   # 15-19..50-59 (E005..E010)
        t60 = (num(d,'B08303_E011') or 0)+(num(d,'B08303_E012') or 0)
        long65 = num(d,'B08303_E013') or 0
        workers_carp = sum(num(d,f'B08303_E{n:03d}') or 0 for n in range(2,13))
        if t and workers_carp:
            r['workers'] = t
            r['under15_share'] = round(100.0*lt10/workers_carp,1)
            r['long60_share'] = round(100.0*(t60+long65)/workers_carp,1)  # 60+ share of car/bus/etc commuters
            r['time_dist'] = {f'm{n}': num(d,f'B08303_E{n:03d}') for n in range(2,14)}
    # means of transport B08301
    d = tbl.get('b08301', {}).get(geo)
    if d:
        tot = num(d,'B08301_E001')
        da = num(d,'B08301_E003'); cp = num(d,'B08301_E004')
        tr = num(d,'B08301_E010'); taxioth = None
        wfh = num(d,'B08301_E019')
        if tot:
            r['drove_alone_share'] = round(100.0*da/tot,1)
            r['carpool_share'] = round(100.0*cp/tot,1)
            r['transit_share'] = round(100.0*tr/tot,2)
            r['wfh_share'] = round(100.0*wfh/tot,1)
    # overall mean commute B08013 (aggregate by sex; col001 total aggregate? check labels: B08013_001 total aggregate, then male/female breakdown)
    d = tbl.get('b08013', {}).get(geo)
    if d and 'workers' in r and r['workers']:
        agg = num(d,'B08013_E001')
        if agg and agg>0:
            r['mean_commute_min'] = round(agg/r['workers'],1)
    # VEHICLE-LADDER (the income-proxy band): B08136 aggregate travel time by veh availability
    d = tbl.get('b08136', {}).get(geo)
    if d:
        # discover structure: E001 total aggregate? then veh0, veh1, veh2, veh3plus? verify by label later
        ks = [k for k in sorted(d, key=lambda x: int(x[-3:]) if x[-3:].isdigit() else 999) if k!='GEO_ID']
        r['b08136_cols'] = ks
    if 'b08141' in tbl:
        d = tbl['b08141'].get(geo)
        if d:
            tot = num(d,'B08141_E001')
            v0 = num(d,'B08141_E002')
            if tot and v0 is not None:
                r['no_vehicle_share'] = round(100.0*v0/tot,1)
    rows.append(r)

rawdir = B/'_lane13'
rawdir.mkdir(exist_ok=True)
for tid in tbl:
    (rawdir/f'acs5y2022_{tid}.dat').write_text('\n'.join('\t'.join([txt.splitlines()[0]]) if False else '') or '', encoding='utf-8')  # placeholder removed below
# actually save raw dat text properly
for tid in TABLES:
    t2 = fetch_dat(tid)
    if t2 is None:
        audit[tid+'_saved'] = 'HONEST-NULL'
    else:
        (rawdir/f'acs5y2022_{tid}.dat').write_text(t2, encoding='utf-8')
        audit[tid+'_saved'] = len(t2)
    time.sleep(1)

out = {'_record':'lane13_transport_lever_pull','built':'2026-11-24','acs_vintage':'5yr 2022 table-based-SF (www2.census.gov, keyless)','tables':TABLES,'audit':audit,'rows':rows}
(B/'lane13_pull_debug.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print('rows:', len(rows))
for r in rows[:3]:
    print(json.dumps(r)[:400])
