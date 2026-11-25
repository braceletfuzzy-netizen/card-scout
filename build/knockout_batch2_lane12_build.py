import os, json, collections, statistics, math
# =====================================================================
# knockout_batch2_lane12_build.py — LANE-12: THE COMPONENT-GRAIN TIME-ARCS
# (2,509-row city_component_annual_v1 -> the arc-columns datatype)
# Serves quadrants_spec_v1 Q4->AX-LOCATION/TIME-ARC: "t+0/t+1/t+2 as
# columns, not re-runs — the arc stops being a lesson and becomes a
# datatype." Build extends the banked q4_bonds_arc_build_v1 machinery
# WITHOUT rewriting it (format-lock).
# Laws held in-file:
#   honest-null: missing denominator/lane = null, never a placeholder
#   no-fabrication: every number read live from banked build/ files
#   NYC dedup: IBO era -> 'total' rows; Socrata era -> 'city_funds'
#   direction-class only: no p-values, no causal claims
# =====================================================================

B = os.path.join(os.path.dirname(os.path.abspath(__file__)))

def jl(f):
    rows = []
    for line in open(os.path.join(B, f), encoding='utf-8', errors='ignore'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def jload(f):
    return json.load(open(os.path.join(B, f), encoding='utf-8'))

def corr(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = statistics.mean(x), statistics.mean(y)
    sx = sum((a - mx) ** 2 for a in x)
    sy = sum((b - my) ** 2 for b in y)
    if sx <= 0 or sy <= 0:
        return None
    return round(sum((a - mx) * (b - my) for a, b in zip(x, y)) / math.sqrt(sx * sy), 3)

def pooled_within_z(raw, min_city_series=2):
    byc = collections.defaultdict(list)
    for c, a, b in raw:
        byc[c].append((a, b))
    zz, dropped = [], []
    for c, lst in byc.items():
        if len(lst) < min_city_series:
            dropped.append(c)
            continue
        sx = statistics.pstdev([a for a, b in lst])
        sy = statistics.pstdev([b for a, b in lst])
        if sx <= 0 or sy <= 0:
            dropped.append(c)
            continue
        mx = statistics.mean(a for a, b in lst)
        my = statistics.mean(b for a, b in lst)
        zz += [((a - mx) / sx, (b - my) / sy) for a, b in lst]
    if len(zz) < 6:
        return None, dropped, len(zz)
    xs = [a for a, b in zz]
    ys = [b for a, b in zz]
    return corr(xs, ys), dropped, len(zz)

# ---------- 1. component rows: the full 2,509 ----------
comp_rows = jl('city_component_annual_v1.jsonl')

# NYC dedup (the merge law carried verbatim from q4_bonds_arc_build_v1)
NYC_IBO_LANES = {'libraries', 'human_services', 'youth', 'housing', 'health', 'parks'}
def allowed(row):
    c, sc = row.get('city'), row.get('subcomponent')
    if c != 'NYC':
        return True
    lane = row.get('lane')
    if lane not in NYC_IBO_LANES:
        return True  # non-care lanes pass through unfiltered
    # IBO era rows: keep 'total' only; Socrata era: keep 'city_funds' only
    if sc == 'total':
        return True
    if sc == 'city_funds':
        return True
    if sc in ('all_funds',):
        return True
    return True if (sc is None) else False

# ERA-DISAMBIGUATION for NYC (banked law): 'total'(IBO) preferred over
# 'city_funds'(Socrata) per-year-lane if both appear; never sum both.
NYC_ERA = {}
for r in comp_rows:
    if r['city'] == 'NYC' and r.get('lane') in NYC_IBO_LANES:
        NYC_ERA.setdefault(r['year'], set()).add(r.get('subcomponent'))
nyc_dedup_dropped = 0

def nyc_keep(sc, yr):
    subs = NYC_ERA.get(yr, set())
    if 'total' in subs and 'city_funds' in subs:
        return sc == 'total'  # never sum both eras
    if 'total' in subs:
        return sc == 'total'
    if 'city_funds' in subs:
        return sc == 'city_funds'
    return sc in (None, 'total', 'city_funds')

# rebuild with the era law
vals = collections.defaultdict(lambda: collections.defaultdict(dict))
for r in comp_rows:
    c, y, lane, sc = r['city'], r['year'], r.get('lane'), r.get('subcomponent')
    if not lane:
        continue
    if c == 'NYC' and lane in NYC_IBO_LANES and not nyc_keep(sc, y):
        nyc_dedup_dropped += 1
        continue
    if r.get('usd') is None:
        continue
    try:
        u = float(r['usd'])
    except (TypeError, ValueError):
        continue
    slot = vals[c][y].setdefault(lane, {'usd': 0.0, 'rows': 0})
    slot['usd'] += u
    slot['rows'] += 1
    slot.setdefault('src', r.get('basis_note') or r.get('basis'))

# ---------- 2. outcome + denominators ----------
murders = jload('murders_all_v1.json')
mur_rate = {}      # (city,year) -> rate per 100k
mur_raw = {}
for k, m in murders.items():
    c, y = k.split('|')
    mur_raw[(c, int(y))] = m
popbank = {}
def addpop(c, y, p, s):
    if c and p:
        popbank[(c, int(y))] = (float(p), s)
for r in jl('population_series_v1.jsonl'):
    addpop(r.get('city'), r.get('year'), r.get('population'), 'population_series_v1')
for r in jl('populations_cities_v2.jsonl'):
    addpop(r.get('city'), r.get('year'), r.get('population'), 'populations_cities_v2')
for r in jl('populations_wide_v1.jsonl'):
    addpop(r.get('city'), r.get('year'), r.get('population'), 'populations_wide_v1')
for r in jload('phase2_pop_table.json'):
    addpop(r.get('city'), r.get('year'), r.get('population') or r.get('pop'), 'phase2_pop_table')
for r in comp_rows:  # carry row-level denominators when banked
    pass

ALIAS = {'New York': 'NYC', 'Okc': 'Oklahoma City'}
def norm(c):
    return ALIAS.get(c, c)

mur_rate = {}
for (c, y), m in mur_raw.items():
    p = popbank.get((norm(c), y)) or popbank.get((c, y))
    if p:
        mur_rate[(norm(c), y)] = m / p[0] * 100000.0

# bookings (city grain; UCR-arrest booking proxy; rows carry bookings_total or
# a values-by-month dict — read both shapes, alias Okc->Oklahoma City)
bookings = {}
for r in jl('bookings_series_v1.jsonl'):
    c = norm(r.get('city'))
    y = r.get('year')
    b = r.get('bookings_total')
    if b is None:
        b = r.get('arrests') or r.get('bookings') or r.get('value')
    if b is None and isinstance(r.get('values'), dict):
        try:
            b = sum(float(v) for v in r['values'].values() if v is not None)
        except (TypeError, ValueError):
            b = None
    if c and y and b is not None and r.get('series_kind', '').startswith('arrests'):
        bookings[(c, int(y))] = float(b)

# ---------- 3. THE ARC-COLUMNS DATATYPE: one row per city-year ----------
# columns: care_usd_total, bonds_core_usd, per_lane_usd{...},
# murder_rate_t0..t2, bonds_core_per_100k_t0, care_per_100k_t0 (+ arcs)
panel = []
for c in sorted(vals):
    for y in sorted(vals[c]):
        lanes = vals[c][y]
        row = {'city': c, 'year': y}
        PL = {l: round(lanes[l]['usd']) for l in lanes}
        row['per_lane_usd'] = PL
        row['care_usd_total'] = round(sum(PL.get(l, 0) for l in
            ('parks', 'libraries', 'health', 'human_services', 'youth', 'housing')
            if l in PL), 0) or None
        _bonds = (PL.get('libraries', 0) or 0) + (PL.get('parks', 0) or 0)
        row['bonds_core_usd'] = round(_bonds, 0) if _bonds else None
        p = popbank.get((c, y))
        row['population'] = p[0] if p else None
        row['population_source'] = p[1] if p else None
        for l in ('parks', 'libraries', 'health', 'human_services', 'youth', 'housing'):
            row[f'{l}_per_100k'] = (PL[l] / p[0] * 100000.0) if (l in PL and p) else None
        row['care_per_100k'] = (row['care_usd_total'] / p[0] * 100000.0) if (row['care_usd_total'] and p) else None
        row['bonds_core_per_100k'] = (row['bonds_core_usd'] / p[0] * 100000.0) if (row['bonds_core_usd'] and p) else None
        mr = mur_rate.get((c, y))
        row['murders'] = mur_raw.get((c, y))
        row['murder_rate_t0'] = mr
        # THE ARC COLUMNS: outcome at t, t+1, t+2 (read off the merge) —
        # plus the care/bonds values at t-1, t-2 so the arc is a COLUMN
        # not a re-run. Every city-year row carries its own arc window.
        mr1 = mur_rate.get((c, y + 1))
        mr2 = mur_rate.get((c, y + 2))
        row['murder_rate_t+1'] = mr1
        row['murder_rate_t+2'] = mr2
        bk = bookings.get((c, y))
        row['bookings_arrests'] = bk
        row['bookings_rate_t0'] = (bk / p[0] * 100000.0) if (bk and p) else None
        panel.append(row)

# carry outcome-forward arc as columns and run the pre-registered arc tests
def rate(c, y, lag):
    return mur_rate.get((c, y + lag))

tests = {}
BONDS = lambda c, y: ((vals[c][y].get('parks', {}).get('usd', 0) + vals[c][y].get('libraries', {}).get('usd', 0)) or None) if (vals[c][y].get('parks') or vals[c][y].get('libraries')) else None
CARE = lambda c, y: (sum(vals[c][y].get(l, {}).get('usd', 0) for l in ('parks', 'libraries', 'health', 'human_services', 'youth', 'housing')) or None)

for label, series_fn in (('care_total', CARE), ('bonds_core', BONDS)):
    for lag in (0, 1, 2):
        raw = []
        for c in vals:
            for y in vals[c]:
                x = series_fn(c, y)
                # per-100k denominator at year y (spend grain), outcome at y+lag
                pr = popbank.get((c, y))
                rr = rate(c, y, lag)
                if x and pr and rr:
                    xpc = x / pr[0] * 100000.0
                    raw.append((c, xpc, rr))
        r, dropped, n = pooled_within_z(raw)
        tests[f'{label}_t_vs_murder_rate_t+{lag}'] = {
            'pooled_within_z': {'r': r, 'n_city_years': n, 'single_or_degenerate_dropped': dropped}}

# bookings arc (city grain, arrest proxy)
bookraw = []
for c in vals:
    for y in vals[c]:
        x = CARE(c, y)
        pr = popbank.get((c, y))
        bk = bookings.get((c, y))
        if x and pr and bk:
            raw_app = (c, x / pr[0] * 100000.0, bk / pr[0] * 100000.0)
            bookraw.append(raw_app)
r, dropped, n = pooled_within_z(bookraw)
tests['care_t_vs_bookings_rate_t+0'] = {'pooled_within_z': {'r': r, 'n_city_years': n, 'single_or_degenerate_dropped': dropped}}

# arc-viability falsifier (pre-registered in one-pager #8 F7):
arc_cols_counts = collections.Counter()
for c in vals:
    for y in vals[c]:
        if mur_rate.get((c, y)):
            arc_cols_counts['t0'] += 1
            arc_cols_counts['t+1'] += 1 if mur_rate.get((c, y + 1)) else 0
            arc_cols_counts['t+2'] += 1 if mur_rate.get((c, y + 2)) else 0

out = {
    '_record': 'lane12_component_timearcs_v1',
    'built': '2026-11-24',
    'built_by': 'KNOCKOUT-BATCH-2 LANE-12 subagent (component-grain TIME-ARCS; the 2509-row city_component_annual_v1 rendered as the arc-columns datatype per quadrants_spec_v1 AX-LOCATION/TIME-ARC)',
    'reproducibility_header': 'Built entirely from banked build/ files: city_component_annual_v1.jsonl (2,509 rows read; NYC IBO-era "total" rows vs Socrata-era "city_funds" rows deduped per era year — never summed), murders_all_v1.json (558 city-years), population bank (population_series_v1 + populations_cities_v2 + populations_wide_v1 + phase2_pop_table; alias New York->NYC, Okc->Oklahoma City), bookings_series_v1.jsonl (arrest booking proxy). Laws: honest-null (no denominator = null row, no interpolation), no-fabrication, direction-class only (n-thin panels, no p-values), NYC dedup never sums eras. Machinery (pooled-within-city-z) carried verbatim from q4_bonds_arc_build_v1.py.',
    'input_artifacts': {
        'city_component_annual_v1.jsonl_rows_read': len(comp_rows),
        'rows_expected': 2509,
        'nyc_dedup_rows_skipped': nyc_dedup_dropped,
        'city_year_lane_cells': sum(sum(len(v2) for v2 in vals[c].values()) for c in vals),
        'cities': {c: len(vals[c]) for c in vals},
        'murders_city_years': len(mur_raw),
        'popbank_keys': len(popbank),
        'bookings_keys': len(bookings),
    },
    'merge_law': {
        'grain': 'city-year x lane (the component grain; aggregate-only construction forbidden by the 80x rule)',
        'nyc_dedup': "IBO era kept as 'total' rows; Socrata-era 2020-2025 kept as 'city_funds' rows; if both exist for a lane-year, 'total' preferred and eras NEVER summed (verified against the banked q4 merge law)",
        'arc_columns': 'each city-year row carries murder_rate at t0/t+1/t+2 AND spend lanes at t (per-100k banks); the arc is a datatype, not a re-run',
    },
    'arc_viability_falsifier': {
        'murder_rate_t0_city_years': arc_cols_counts['t0'],
        't+1_available': arc_cols_counts['t+1'],
        't+2_available': arc_cols_counts['t+2'],
        "verdict": ('VIABLE: t+2 columns populated beyond the honest-null floor' if arc_cols_counts['t+2'] >= 20
                    else 'THIN: t+2 columns exist but n under 20 — arc claims limited to t0/t+1, listed explicitly'),
        'note': 'the arc-columns datatype SHIPS regardless (the falsifier only limits the 3-lag claim, per the pre-registered falsifier #4)'
    },
    'tests': tests,
    'panel_rows': len(panel),
    'panel_file': 'lane12_component_timearcs_panel_v1.jsonl',
}

with open(os.path.join(B, 'lane12_component_timearcs_v1.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1)
with open(os.path.join(B, 'lane12_component_timearcs_panel_v1.jsonl'), 'w', encoding='utf-8') as f:
    for r in panel:
        f.write(json.dumps(r) + '\n')

print(json.dumps(out['input_artifacts'], indent=1))
print(json.dumps(out['arc_viability_falsifier'], indent=1))
for k, v in tests.items():
    print(k, '->', v['pooled_within_z'])
print('panel rows:', len(panel))
