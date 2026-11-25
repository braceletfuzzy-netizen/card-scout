import json, collections, math
import numpy as np

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
OUT = B + 'care_bookings_ordering_v1.json'

bank = json.load(open(B + '_test2_merge_bank.json'))
care_cy = bank['care_city_year']          # city|year -> {component: usd or None}
care_total = bank['care_total']           # city|year -> usd (sum of component units)
care_partial = bank['care_partial']
bk = bank['bookings_series']              # city|year -> bookings (arrests proxy)
bk_meta = bank['bookings_series_meta']
fac_nyc = bank['fac_nyc']                 # year-str -> {discharges, admitted, flags}
mur = bank['murders']                     # city|year -> murders
pop_pri = bank['pop']                     # city|year -> {population, pop_source}

# supplementary: triple_slider_v6d (pop + cage + care cross-check, band-normalized master)
slider = json.load(open(B + 'triple_slider_v6d.json', encoding='utf-8'))
sup = {}
for r in slider:
    key = f"{r['city']}|{r['year']}"
    cp = r.get('care_provenance') or {}
    sup[key] = {
        'population': r.get('population'),
        'cage_usd_total': (cp or {}).get('cage_usd_total'),
        'care_usd_total_alt': (cp or {}).get('care_usd_total'),
        'murders_alt': r.get('murders'),
        'source': 'triple_slider_v6d.json (care_arc bank: books-grain care/cage + pop)',
    }

def merge_pop_cage(key):
    row = {}
    p = pop_pri.get(key)
    s = sup.get(key)
    if p and p.get('population'):
        row['population'] = p['population']; row['pop_source'] = p['pop_source']
    elif s and s.get('population'):
        row['population'] = s['population']; row['pop_source'] = s['source']
    else:
        row['population'] = None; row['pop_source'] = None
    row['cage_usd_total'] = (s or {}).get('cage_usd_total')
    row['care_usd_total_alt'] = (s or {}).get('care_usd_total_alt')
    return row

# ---------------- panel ----------------
cities = sorted({k.split('|')[0] for k in care_cy})
panel = {}
for key, comps in care_cy.items():
    c, y = key.split('|'); y = int(y)
    extra = merge_pop_cage(key)
    care = care_total.get(key)
    ct = care.get if False else care
    row = {
        'city': c, 'year': y,
        'care_usd_total': care,
        'care_components': {k: v for k, v in comps.items()},
        'care_partial_nulls': (care_partial.get(key) or {}).get('null_components'),
        'bookings_total': bk.get(key),
        'bookings_measure': 'UCR arrests by agency (intake/booking proxy)' if key in bk else None,
        'bookings_months_present': (bk_meta.get(key) or {}).get('months_present'),
        'murders': mur.get(key),
        'population': extra['population'],
        'pop_source': extra['pop_source'],
        'cage_usd_total_books': extra['cage_usd_total'],
        'care_usd_total_alt_books': extra['care_usd_total_alt'],
        # derived (None if either side None — never zero-substituted)
        'care_per_capita': (care / extra['population']) if (care is not None and extra['population']) else None,
        'murder_rate_per100k': (mur.get(key) / extra['population'] * 1e5) if (mur.get(key) is not None and extra['population']) else None,
        'care_ratio_cage': (care / extra['cage_usd_total']) if (care is not None and extra['cage_usd_total']) else None,
    }
    panel[key] = row

# NYC facility lane rows
nyc_fac_panel = {}
for ys, v in fac_nyc.items():
    y = int(ys)
    key = f'NYC|{y}'
    extra = merge_pop_cage(key)
    nyc_fac_panel[y] = {
        'city': 'NYC', 'year': y,
        'facility_discharges': v['discharges'],
        'facility_admitted': v['admitted'],
        'flags': v['flags'],
        'nypd_arrests_8h9b': bk.get(key),
        'population': extra['population'], 'pop_source': extra['pop_source'],
        'discharges_per_arrest': (v['discharges'] / bk[key]) if (v['discharges'] is not None and bk.get(key)) else None,
        'facility_admitted_per_capita': (v['admitted'] / extra['population']) if (v['admitted'] is not None and extra['population']) else None,
        'care_usd_total': care_total.get(key),
        'murders': mur.get(key),
        'murder_rate_per100k': (mur.get(key) / extra['population'] * 1e5) if (mur.get(key) is not None and extra['population']) else None,
    }

# ---------------- stats helpers ----------------
def pearson(xs, ys):
    n = len(xs)
    if n < 3 or n > len(xs):  # need >=3
        return None
    mx, my = np.mean(xs), np.mean(ys)
    sx, sy = np.std(xs, ddof=1), np.std(ys, ddof=1)
    if sx == 0 or sy == 0:
        return None
    r = np.corrcoef(xs, ys)[0, 1]
    if n > 3:
        t = r * math.sqrt((n - 2) / (1 - r * r))
    else:
        t = float('nan')
    return r, t, n

def within_city_pairs(panel, xv, yv, lag, value_of, require_pop_rate=False):
    """pairs: (x_t, y_{t+lag}) same city; x from xv source dict, y from yv."""
    xs, ys, tags = [], [], []
    for key, row in panel.items():
        c, y = key.split('|'); y = int(y)
        xval = value_of(row, 'x')
        yrow = panel.get(f'{c}|{y + lag}')
        yval = value_of(yrow, 'y') if yrow else None
        if xval is None or yval is None:
            continue
        xs.append(xval); ys.append(yval); tags.append(f'{c}|y{y}->+{lag}')
    return xs, ys, tags

def lag_profile(panel, xvalue_of, yvalue_of, lags=(0, 1, 2, 3, 4), demean_within=True):
    """pooled within-city (demeaned) + per-city lags"""
    out = {}
    per_city = collections.defaultdict(dict)
    for lag in lags:
        xs, ys, tags = within_city_pairs(panel, None, None, lag, lambda r, side: (
            xvalue_of(r) if side == 'x' else yvalue_of(r)))
        # within-city demean (pooled FE-style)
        if demean_within:
            byc = collections.defaultdict(list)
            for (x, yy, tg) in zip(xs, ys, tags):
                c = tg.split('|')[0]
                byc[c].append((x, yy))
            dx, dy = [], []
            ns = 0
            for c, prs in byc.items():
                if len(prs) < 3:
                    continue
                mx = np.mean([p[0] for p in prs]); my = np.mean([p[1] for p in prs])
                for x, yy in prs:
                    dx.append(x - mx); dy.append(yy - my)
            xs_d, ys_d = dx, dy
        else:
            xs_d, ys_d = xs, ys
        # per-city
        for c, prs in byc.items():
            if len(prs) >= 3:
                cx = [p[0] for p in prs]; cy = [p[1] for p in prs]
                st = pearson(cx, cy)
                if st: per_city[c][lag] = {'r': round(st[0], 4), 't': round(st[1], 2), 'n': st[2]}
        st = pearson(xs_d, ys_d) if len(xs_d) >= 3 else None
        out[lag] = {'r': round(st[0], 4), 't': round(st[1], 2), 'n': st[2]} if st else None
    return out, per_city

def care_x(row):
    return row['care_per_capita']

def bk_y(row):
    b = row['bookings_total']
    p = row['population']
    return (b / p * 1e5) if (b is not None and p) else None

def bk_raw(row):
    return row['bookings_total']

def mur_y(row):
    return row['murder_rate_per100k']

def mur_raw(row):
    return row['murders']

# ---------------- TEST A: care (city_component book) -> bookings (UCR series) ----------------
lags = (0, 1, 2, 3, 4)
testA_rate, testA_rate_pc = lag_profile(panel, care_x, bk_y, lags)
testA_raw, testA_raw_pc = lag_profile(panel, lambda r: r['care_usd_total'], bk_raw, lags)

# ---------------- TEST B: care -> murders ----------------
testB_rate, testB_rate_pc = lag_profile(panel, care_x, mur_y, lags)
testB_raw, testB_raw_pc = lag_profile(panel, lambda r: r['care_usd_total'], mur_raw, lags)

# ---------------- TEST C: bookings -> murders (mid-stream of the chain) ----------------
# bookings book spans 2015-2024 for 9 cities — run on bookings-panel (not just care cities)
bookings_panel = {}
for key, v in bk.items():
    c, y = key.split('|'); y = int(y)
    extra = merge_pop_cage(key)
    row = {
        'city': c, 'year': y,
        'bookings_total': v,
        'bookings_per100k': (v / extra['population'] * 1e5) if (v is not None and extra['population']) else None,
        'murders': mur.get(key),
        'murder_rate_per100k': (mur.get(key) / extra['population'] * 1e5) if (mur.get(key) is not None and extra['population']) else None,
        'population': extra['population'],
    }
    if v is None:
        row['bookings_total'] = None
    bookings_panel[key] = row
testC_rate, testC_rate_pc = lag_profile(bookings_panel, lambda r: r['bookings_per100k'], mur_y, lags)
testC_raw, testC_raw_pc = lag_profile(bookings_panel, lambda r: r['bookings_total'], mur_raw, lags)

# ---------------- TEST D: NYC facility deep-lane ----------------
# care book NYC spans 1980-2025; facility admitted 2013-2025; murders 2019-2024 (+1998-2001 no facility).
# Ordering pieces: (1) care_per_capita vs admitted_per_capita lag profile; (2) discharges_per_arrest cross-check.
nyc_panel = {}
for y, r in nyc_fac_panel.items():
    if r['facility_admitted'] is not None and r['population']:
        nyc_panel[f'NYC|{y}'] = r
testD_care2admit, testD_care2admit_pc = lag_profile(
    nyc_panel, lambda r: (r['care_usd_total'] / r['population'] if r['care_usd_total'] and r['population'] else None),
    lambda r: r['facility_admitted_per_capita'], lags)
# NYPD-arrests cross-check years and ratios
xcheck = []
for y in sorted(nyc_fac_panel):
    r = nyc_fac_panel[y]
    if r['nypd_arrests_8h9b'] and r['facility_discharges']:
        xcheck.append({'year': y, 'discharges': r['facility_discharges'], 'nypd_arrests': r['nypd_arrests_8h9b'],
                       'ratio': round(r['discharges_per_arrest'], 4)})

# ---------------- per-city lag tables for the merged care+bookings cities ----------------
def per_city_table(panel_, x_of, y_of, lags=(0, 1, 2, 3)):
    tbl = {}
    cities_ = sorted({r['city'] for r in panel_.values()})
    for c in cities_:
        rows = [(int(k.split('|')[1]), r) for k, r in panel_.items() if r['city'] == c]
        d = {}
        for lag in lags:
            pairs = []
            for y, r in rows:
                xr = x_of(r)
                yr_row = panel_.get(f'{c}|{y + lag}')
                yval = y_of(yr_row) if yr_row else None
                if xr is None or yval is None:
                    continue
                pairs.append((xr, yval))
            if len(pairs) >= 3:
                st = pearson([p[0] for p in pairs], [p[1] for p in pairs])
                d[lag] = {'r': round(st[0], 4), 't': round(st[1], 2), 'n': st[2]}
            # honest-n ledger: pairs that would exist but had nulls
            attempts = sum(1 for y, r in rows if (panel_.get(f'{c}|{y + lag}') and
                          (x_of(r) is not None or True) and (y_of(panel_[f'{c}|{y+lag}']) is None or x_of(r) is None)))
        ns = {lag: sum(1 for y, r in rows if (panel_.get(f'{c}|{y + lag}')
              and x_of(r) is not None and y_of(panel_[f'{c}|{y + lag}']) is not None)) for lag in lags}
        tbl[c] = {'lags': d, 'n_available': ns, 'y_years': sorted(y for y, _ in rows)}
    return tbl

per_city_A = per_city_table(panel, care_x, bk_y)
per_city_B = per_city_table(panel, care_x, mur_y)
per_city_C = per_city_table(bookings_panel, lambda r: r['bookings_per100k'], mur_y)
per_city_C_raw = per_city_table(bookings_panel, lambda r: r['bookings_total'], mur_raw)

def clean(tbl):
    return tbl

json.dump({
    'panel': panel, 'bookings_panel': bookings_panel, 'nyc_fac_panel': nyc_fac_panel,
    'testA_care2bookings_rate': {'pooled': testA_rate, 'per_city': testA_rate_pc},
    'testA_care2bookings_raw': {'pooled': testA_raw, 'per_city': testA_raw_pc},
    'testB_care2murders_rate': {'pooled': testB_rate, 'per_city': testB_rate_pc},
    'testB_care2murders_raw': {'pooled': testB_raw, 'per_city': testB_raw_pc},
    'testC_bookings2murders_rate': {'pooled': testC_rate, 'per_city': testC_rate_pc},
    'testC_bookings2murders_raw': {'pooled': testC_raw, 'per_city': testC_raw_pc},
    'testD_nyc_care2admit': {'pooled': testD_care2admit, 'per_city': testD_care2admit_pc},
    'nyc_xcheck': xcheck,
    'per_city_A': per_city_A, 'per_city_B': per_city_B, 'per_city_C': per_city_C, 'per_city_C_raw': per_city_C_raw,
}, open(B + '_test2_stats_bank.json', 'w', encoding='utf-8'), indent=1, default=str)
print('stats bank written')

# quick headline print
def show(name, prof):
    for lag, st in prof.items():
        print(f'  {name} t+{lag}:', st)
print('A care->bookings (per100k, within-city demeaned):')
show('A', testA_rate)
print('B care->murders (rate, within-city):')
show('B', testB_rate)
print('C bookings->murders (per100k->rate, within-city, 9-city bookings panel):')
show('C', testC_rate)
print('C raw count lane:')
show('Craw', testC_raw)
print('D NYC care->facility-admit per capita:')
show('D', testD_care2admit)
print('nyc xcheck rows:', len(xcheck))
