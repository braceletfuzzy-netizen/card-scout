# BOARD-2 GRAD-LANE extractor: B15003 (25+ educational attainment) from ACS 1-YR state zips
# Law: L_k = parts[start-1 + (k-1)]  (1-based start position from the year's sequence lookup)
import zipfile, os, json
RAW = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/_edu_raw/'
STATES = {'MS':'28','MI':'26','NY':'36','OH':'39','MO':'29','TN':'47','CO':'08','MA':'25'}

def seq_start(y):
    p = RAW + f'lookups/seqtable_{y}.txt'
    seq = start = None
    for line in open(p, 'r', encoding='latin-1'):
        parts = [x.strip().strip('"') for x in line.strip().split(',')]
        if len(parts) >= 6 and parts[1] == 'B15003':
            if parts[2] and parts[2] != '.':
                seq = parts[2].zfill(4)
            if parts[3] in ('','.') and parts[4] and parts[4] != '.':
                start = int(parts[4])
    return seq, start

rows = []; audit = {}
for y in range(2012, 2020):
    seq, start = seq_start(y)
    if not seq or not start:
        audit[f'{y}'] = 'no lookup'; continue
    for ab, fips in STATES.items():
        zp = RAW + f'acs{y}_1yr_{ab}_allgeo.zip'
        if not os.path.exists(zp) or os.path.getsize(zp) < 100000:
            audit[f'{y}-{ab}'] = 'missing zip'; continue
        try:
            z = zipfile.ZipFile(zp)
            names = z.namelist()
            gname = sorted([n for n in names if n.startswith(f'g{y}1{ab.lower()}') and n.endswith('.csv')])
            seqfile = [n for n in names if n.startswith(f'e{y}1{ab.lower()}') and n.endswith(f'{seq}000.txt')]
            if not (gname and seqfile):
                audit[f'{y}-{ab}'] = 'file-missing'; continue
            g = z.read(gname[0]).decode('latin-1').splitlines()
            d = z.read(seqfile[0]).decode('latin-1').splitlines()
            state_idx = None
            for i, l in enumerate(g):
                if f'04000US{fips}' in l:
                    nm = l.lower()
                    if any(t in nm for t in ('-- u','-- r','inside','outside','not ')):
                        continue
                    state_idx = i; break
            if state_idx is None or state_idx >= len(d):
                audit[f'{y}-{ab}'] = 'no state row'; continue
            parts = d[state_idx].split(',')
            if len(parts) < start + 24:
                audit[f'{y}-{ab}'] = 'short seq row'; continue
            L1 = int(parts[start-1])
            if L1 <= 0:
                audit[f'{y}-{ab}'] = 'null total'; continue
            L2_25 = [int(x) for x in parts[start:start+24]]   # L2..L25
            hs_block = L2_25[15:]   # L17..L25 = HS grad or higher
            ba_block = L2_25[20:]   # L22..L25 = bachelors or higher
            hs = sum(hs_block); ba = sum(ba_block)
            okcons = (sum(L2_25) == L1)
            rows.append({'year': y, 'state': ab, 'pop25_plus': L1,
                         'hs_grad_or_higher': hs,
                         'hs_grad_or_higher_share': round(100*hs/L1, 2),
                         'bachelors_or_higher_share': round(100*ba/L1, 2),
                         'consistency_total_eq_sum': okcons,
                         'geo_id': f'04000US{fips}',
                         'source': f'ACS 1-YR {y} B15003 seq {seq}'})
            audit[f'{y}-{ab}'] = 'ok'
        except Exception as e:
            audit[f'{y}-{ab}'] = 'ERR ' + str(e)[:60]

print('rows:', len(rows))
bad = {k: v for k, v in audit.items() if v != 'ok'}
print('bad:', bad)
cons_bad = [(r['year'], r['state']) for r in rows if not r['consistency_total_eq_sum']]
print('consistency failures:', cons_bad)
for r in sorted(rows, key=lambda x: (x['state'], x['year'])):
    print(r['year'], r['state'], 'HS+:', r['hs_grad_or_higher_share'], 'BA+:', r['bachelors_or_higher_share'], 'cons:', r['consistency_total_eq_sum'])
json.dump({'rows': rows, 'audit': audit}, open(RAW + 'grad_lane_b15003_ftp_years.json', 'w'), indent=1)
print('saved')
