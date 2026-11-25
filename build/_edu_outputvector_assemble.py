# BOARD-2 final assemble: edu_outputvector_v1.json (grad lane + NAEP lane + joint reads + panel join)
import json, os, statistics as st

RAW = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/_edu_raw/'
BUILD = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

ftp = json.load(open(RAW + 'grad_lane_b15003_ftp_years.json'))['rows']
dat = json.load(open(RAW + 'grad_lane_b15003_dat_years.json'))
naep = [json.loads(l) for l in open(RAW + 'naep_testscore_lane_raw.jsonl') if l.strip()]

grad_cells = {}
for r in ftp + dat:
    if r.get('flag'):
        continue
    grad_cells[(r['state'], r['year'])] = r

naep_cells = {}
for r in naep:
    if r.get('displayable') != 1:
        continue
    naep_cells[(r['jurisdiction'], r['subject'], r['grade'], r['year'])] = round(r['mean_scale'], 2)

states = ['MS', 'MI', 'NY', 'OH', 'MO', 'CO', 'TN', 'MA']
state_year = []
for s in states:
    ys = sorted({y for (ss, y) in grad_cells if ss == s} |
                {yy for (j, sb, g, yy) in naep_cells if j == s})
    for y in ys:
        g = grad_cells.get((s, y))
        state_year.append({
            'state': s, 'year': y,
            'hs_grad_or_higher_share': g['hs_grad_or_higher_share'] if g else None,
            'bachelors_or_higher_share': g['bachelors_or_higher_share'] if g else None,
            'pop25_plus': g['pop25_plus'] if g else None,
            'naep_g4_math': naep_cells.get((s, 'mathematics', 4, y)),
            'naep_g4_reading': naep_cells.get((s, 'reading', 4, y)),
            'naep_g8_math': naep_cells.get((s, 'mathematics', 8, y)),
            'naep_g8_reading': naep_cells.get((s, 'reading', 8, y)),
        })

def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0]*len(v)
        for pos, i in enumerate(order):
            r[i] = pos + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = st.mean(rx), st.mean(ry)
    num = sum((a-mx)*(b-my) for a, b in zip(rx, ry))
    den = (sum((a-mx)**2 for a in rx)*sum((b-my)**2 for b in ry))**0.5
    return num/den

reads = []
pairs = [(r['naep_g8_math'], r['hs_grad_or_higher_share']) for r in state_year
         if r['naep_g8_math'] and r['hs_grad_or_higher_share']]
reads.append({'pair': 'naep_g8_math x state_hs_grad_or_higher_share',
              'n': len(pairs), 'rho': round(spearman([p[0] for p in pairs], [p[1] for p in pairs]), 3)})
pairs2 = [(r['naep_g8_math'], r['bachelors_or_higher_share']) for r in state_year
          if r['naep_g8_math'] and r['bachelors_or_higher_share']]
reads.append({'pair': 'naep_g8_math x state_bachelors_or_higher_share',
              'n': len(pairs2), 'rho': round(spearman([p[0] for p in pairs2], [p[1] for p in pairs2]), 3)})
arcs = {}
for s in states:
    pts = [(y, naep_cells.get((s, 'mathematics', 8, y))) for y in [2013, 2015, 2017, 2019, 2022, 2024]]
    pts = [(y, v) for y, v in pts if v]
    if len(pts) >= 2:
        arcs[s] = {'from': pts[0], 'to': pts[-1], 'delta': round(pts[-1][1] - pts[0][1], 2)}
reads.append({'pair': 'naep_g8_math within-state arc delta (first->last captured)', 'per_state': arcs})

# grad arc deltas 2011->2024 within state
garc = {}
for s in states:
    gys = sorted(y for (ss, y) in grad_cells if ss == s)
    if len(gys) >= 2:
        v0 = grad_cells[(s, gys[0])]['hs_grad_or_higher_share']
        v1 = grad_cells[(s, gys[-1])]['hs_grad_or_higher_share']
        garc[s] = {'from': [gys[0], v0], 'to': [gys[-1], v1], 'delta': round(v1 - v0, 2)}
reads.append({'pair': 'state hs_grad_or_higher_share arc delta', 'per_state': garc})

# joint-panel city-year join (city->own-state)
CITY2STATE = {'Cincinnati':'OH', 'Denver':'CO', 'Detroit':'MI', 'Memphis':'TN', 'NYC':'NY', 'St. Louis':'MO'}
panel = [json.loads(l) for l in open(BUILD + 'maslow_joint_panel_v1.jsonl', encoding='utf-8') if l.strip()]
joint = []
for r in panel:
    s = CITY2STATE.get(r['city'])
    if not s:
        continue
    y = r['year']
    g = grad_cells.get((s, y))
    n8m = naep_cells.get((s, 'mathematics', 8, y))
    n8r = naep_cells.get((s, 'reading', 8, y))
    if g or n8m or n8r:
        joint.append({'city': r['city'], 'state': s, 'year': y,
                      'hs_grad_or_higher_share': g['hs_grad_or_higher_share'] if g else None,
                      'bachelors_or_higher_share': g['bachelors_or_higher_share'] if g else None,
                      'naep_g8_math': n8m, 'naep_g8_reading': n8r})

n_joint_cells = sum(1 for r in joint for k in ('hs_grad_or_higher_share','bachelors_or_higher_share','naep_g8_math','naep_g8_reading')
                    if r[k] is not None)

out = {
  '_record': 'edu_outputvector_v1 — BOARD-2 THE EDU-OUTPUT-VECTOR LANES (grad + test-score pulls, joint panel)',
  'built': '2026-11-24',
  'laws_held': [
    'direction-class only, no causal claims',
    'honest-null = routes-tried-no-capture, never a placeholder',
    'every number read live from pulled files; consistency check (B15003 L1 = sum L2..L25) enforced per row',
    'static-vintage separation: NAEP year labels are NAEP administration years; ACS rows are labeled by ACS vintage'
  ],
  'lane_grad': {
    'what': 'ACS B15003 educational attainment, population 25 years and over, state level',
    'correction_banked': 'the dispatch said B14005; B14005 is the 16-19 school-enrollment table — the 25+ attainment table is B15003 (verified against the ACS 1-yr sequence lookup, Universe line)',
    'definition_law': 'HS+ = sum of lines 17..25 (B15003 categories are mutually exclusive, NOT cumulative — summing L17+L18 only gives ~30% and is the banked first-pass mistake)',
    'route_grad_2011_2019': 'ftp.census.gov per-state All_Geographies zips -> B15003 seq (per-year lookup) -> state 040 row',
    'route_grad_2021_2024': 'www2.census.gov table-based-SF acsdt1y{y}-b15003.dat (keyless)',
    'rows': len([1 for (s, y) in grad_cells]),
    'states': {s: sorted(y for (ss, y) in grad_cells if ss == s) for s in states},
    'honest_nulls': [
      '2020: 1-YR experiment released without B15003 for these states — honest-null, not interpolated',
      '2025: www2 .dat file structurally truncated at E023 (professional/doctorate cells absent) — HS+/BA+ shares would be lower-bound-biased; shipped honest-null with the flag banked',
      '2010: state-zip route exists but zip was not pulled before the FTP job window — left for a later pass, honest-null in the meantime'
    ],
    'mistake_guards_banked': [
      'off-by-one at (start-1): L_k = parts[start-1 + (k-1)]; the first pass read L18..L25+1 as L17..L25 and printed CO = 110.58% — caught by the >100% sanity tripwire, fixed, re-run',
      'some-college/associate cells dropped in the first re-run (HS+ = 51-61%) — caught against the API-truth MS 2019 ~86 % check',
      'two state zips (2015-MS, 2017-TN) were corrupt partials from a killed FTP job — re-downloaded size-verified before extraction'
    ],
    'truth_checks': [
      'MS 2019: total 25+ = 1,979,664 (sum-consistency exact)',
      'MS 2021 HS+ = 86.49 % (known truth ~85.9 % class)',
      'CO 2019 = 92.4 / BA+ 42.66, MA 2019 = 91.32 / 44.98 — both match public ACS reads'
    ]
  },
  'lane_test_scores': {
    'what': 'NAEP main-NAEP mean scale scores, state level, all students (variable TOTAL, stattype MN:MN), grades 4 and 8, mathematics (MRPCM) and reading (RRPCM)',
    'route': 'nationsreportcard.gov DataService GetAdhocData.aspx (keyless; param contract learned by probe:',
    'endpoint_template': 'type=data&subject={mathematics|reading}&grade={4|8}&subscale={MRPCM|RRPCM}&jurisdiction={XX}&year={Y}&variable=TOTAL&stattype=MN:MN',
    'years_pulled': [2013, 2015, 2017, 2019, 2022, 2024],
    'rows': len(naep),
    'states': {s: sorted(yy for (j, sb, g, yy) in naep_cells if j == s) for s in states},
    'mistake_guards_banked': [
      'param-name discovery: juris->jurisdiction, years->year, + required variable & stattype (learned from API 400 error text, no guessing)',
      'isStatDisplayable flag respected — non-displayable cells would ship honest-null'
    ]
  },
  'joint_panel': {
    'grain': 'state-year (edu-output cells) + city-year join back to maslow_joint_panel_v1 (6 panel cities mapped to own states: Cincinnati->OH, Denver->CO, Detroit->MI, Memphis->TN, NYC->NY, St. Louis->MO)',
    'state_year_rows': len(state_year),
    'city_year_joint_rows': len(joint),
    'city_year_joint_cells_filled': n_joint_cells,
  },
  'state_year_table': state_year,
  'city_year_joint_rows': joint,
  'first_joint_reads_direction_class': reads,
  'files_banked': [
    '_edu_raw/grad_lane_b15003_ftp_years.json (66 rows + audit)',
    '_edu_raw/grad_lane_b15003_dat_years.json (40 rows, 2025 rows flagged)',
    '_edu_raw/naep_testscore_lane_raw.jsonl (192 rows)',
    '_edu_raw/acs[year]_1yr_[state]_allgeo.zip (raw FTP pulls, size-verified)',
    '_edu_raw/acs1y_b15003_[2021-2025].dat (raw www2 pulls)',
    '_edu_raw/lookups/seqtable_[2010-2019].txt (per-year B15003 seq/start lookups)',
    '_edu_ftp_fetch.py + _edu_grad_lane_extract.py (the reproducible route)'
  ]
}

with open(BUILD + 'edu_outputvector_v1.json', 'w') as f:
    json.dump(out, f, indent=1)
print('edu_outputvector_v1.json written')
print('state_year_rows:', len(state_year), '| joint rows:', len(joint), '| joint cells:', n_joint_cells)
for r in reads:
    print(r.get('pair'), r.get('rho'), r.get('n', ''))
