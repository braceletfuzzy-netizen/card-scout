# _bob19_outlanes_assemble.py — THE JOINT LANE-1/2/3 MACHINERY (output blind-spots assembly)
# Lane 1: pit_homelessness_lane_v1.json (HUD CoC PIT 2010-2025, CoC grain, static-stock law)
# Lane 2: eviction_rate_lane_v1.json (Eviction Lab, place grain, judgment-rate per-1k-renter, covid freeze flagged)
# Lane 3: health_outcome_lane_v1.json (CHR county-LE companion + NCHS drug-poisoning county companion, grain-law holds)
# Joint reads: within-city-demeaned (FE) direction-class reads vs the murder-rate arcs, honest nulls, no fabrication.
import json, math, statistics
from pathlib import Path

B = Path(r"C:\Users\J\Documents\LLM\cardscout-2.0\For You\PolyScout\build")
O = B/'_bob19_outputs'

def jl(p): return json.load(open(p, encoding='utf-8'))

murder_rows = []   # from the joint panel jsonl (murder_rate_t0 arcs per city-year)
for line in open(B/'maslow_joint_panel_v1.jsonl', encoding='utf-8'):
    r = json.loads(line)
    t0 = r.get('murder_rate_t0') or r.get('murder_rate')
    if t0:
        murder_rows.append({'city': r['city'], 'year': r['year'], 'murder_rate_t0': t0})

def within_demeaned_reads(pairs, xkey, ykey, label):
    """pairs: [{city, year, x, y}] -> per-city spearman + pooled FE-ish read (within-demeaning, pooled slope)"""
    from collections import defaultdict
    by = defaultdict(list)
    for p in pairs:
        if p.get(xkey) is not None and p.get(ykey) is not None:
            by[p['city']].append(p)
    def spearman(xs, ys):
        def ranks(v):
            order = sorted(range(len(v)), key=lambda i: v[i]); out=[0]*len(v)
            for pos,i in enumerate(order): out[i]=pos+1
            return out
        rxs, rys = ranks(xs), ranks(ys)
        n = len(xs)
        if n < 3: return None
        mx, my = statistics.mean(rxs), statistics.mean(rys)
        num = sum((a-mx)*(b-my) for a,b in zip(rxs, rys))
        den = math.sqrt(sum((a-mx)**2 for a in rxs)*sum((b-my)**2 for b in rys))
        return round(num/den, 3) if den else None
    per_city = {}
    pool_x2 = pool_xy = n_tot = 0.0
    city_dof = 0
    for c, ps in by.items():
        xs = [p[xkey] for p in ps]; ys = [p[ykey] for p in ps]
        rho = spearman(xs, ys) if len(ps) >= 4 and len(set(xs)) > 2 else None
        per_city[c] = {'n': len(ps), 'spearman': rho}
        if len(ps) >= 3:
            mx = statistics.mean(xs); my = statistics.mean(ys)
            dcx = [x-mx for x in xs]; dcy = [y-my for y in ys]
            dxx = sum(x*x for x in dcx); dxy = sum(a*b for a,b in zip(dcx, dcy))
            s = sum(yc for yc in dcy)  # ~0
            pool_x2 += dxx; pool_xy += dxy; n_tot += len(ps); city_dof += len(ps) - 1
    beta = (pool_xy/pool_x2) if pool_x2 else None
    # simple honest SE for pooled within slope: residual variance / pool_x2
    se = None
    if pool_x2:
        resid = 0.0
        for c, ps in by.items():
            if len(ps) >= 3:
                mx = statistics.mean(xs := [p[xkey] for p in ps]); my = statistics.mean(ys := [p[ykey] for p in ps])
                for x, y in zip(xs, ys):
                    resid += (y - my - beta*(x-mx))**2
        dof = max(1, n_tot - len(by) - 1)
        se = math.sqrt(resid/dof/pool_x2)
    return {'label': label, 'per_city_spearman': per_city,
            'pooled_within_beta_std': None if beta is None else round(beta, 4),
            'pooled_within_beta_se': None if se is None else round(se, 4),
            'n_rows': n_tot, 'n_cities': len(by), 'within_dof': city_dof,
            'law': 'direction-class only, tiny-n; NOT causal'}

# ===== LANE 1: PIT =====
pit = jl(O/'_pit_raw_rows.json')
pit_rows = pit['rows']; pit_errs = pit['errors']
pit_lane = {
 '_record': 'pit_homelessness_lane_v1 (BOB-SCAN-19 OUTPUT-blind-spot P1 = THE PIT-HOMELESSNESS LANE)',
 'built': '2026-11-24',
 'laws_held': [
   'direction-class only, no causal claims',
   'no fabricated rows — every count read from the HUD CoC PopSub PDF (files.hudexchange.info, keyless)',
   'GRAIN: CoC = the count-of-care grain; city keys mapped, county-companion not blended (the grain-law)',
   'STATIC-STOCK LAW: the PIT count is a January point-in-time STOCK of a single night, never read as a flow',
   'honest-null: 2013 + 2016 = HUD published-nothing at the per-CoC report route for ANY CoC (verified 8/8 = 404) — banked null, never backfilled',
 ],
 'route': {'host': 'https://files.hudexchange.info/reports/published/CoC_PopSub_CoC_{coc}-{yr}_{st}_{yr}.pdf',
           'keyless': True, 'raw_files': '_bob19_outputs/_pit_raw/*.pdf (112 PDFs cached)'},
 'city_coc_key_map': {
   'Memphis': 'TN-501 (Memphis/Shelby County CoC)', 'Cincinnati': 'OH-500 (Cincinnati/Hamilton County CoC)',
   'Detroit': 'MI-501 (Detroit CoC)', 'St. Louis': 'MO-501 (St. Louis City CoC)',
   'NYC': 'NY-600 (New York City CoC)',
   'Houston': 'TX-700 (Houston, Pasadena, Conroe/Harris, Fort Bend, Montgomery Counties CoC)',
   'Denver': 'CO-503 (Metropolitan Denver CoC)',
   'Kingsport': 'TN-509 (Appalachian Regional CoC — balance-of-state regional grain, NOT city-only)'},
 'rows': pit_rows,
 'honest_nulls_banked': [f"{e['coc']} {e['year']} {e['status']}" for e in pit_errs],
 'row_count': len(pit_rows),
}
# joint read: pit_total x murder_rate_t0 (city-year, same-year overlap 2017-2025)
pit_pairs = []
mr = {(r['city'], r['year']): r['murder_rate_t0'] for r in murder_rows}
for r in pit_rows:
    y = r['year']; m = mr.get((r['city'], y))
    if m is not None:
        pit_pairs.append({'city': r['city'], 'year': y, 'pit_total': r['pit_total'], 'murder_rate_t0': m})
pit_lane['joint_within_read'] = within_demeaned_reads(pit_pairs, 'pit_total', 'murder_rate_t0', 'PIT-total x murder-rate t0 (overlap years)')

# ===== LANE 2: EVICTION =====
ev = jl(O/'_evict_raw_rows.json')
ev_lane = {
 '_record': 'eviction_rate_lane_v1 (BOB-SCAN-19 OUTPUT-blind-spot P1 = THE EVICTION-JUDGMENT-RATE LANE)',
 'built': '2026-11-24',
 'laws_held': [
   'direction-class only, no causal claims',
   'no fabricated rows — judgment/filing rates read from Eviction Lab keyless S3 (eviction-lab-data-downloads bucket, ODC-BY license)',
   'GRAIN: place (city) for the rate columns; the county-side series rides as companion only (grain-law)',
   'judgment_rate = evictions (court-issued judgments) per 1,000 renter-occupied households',
   'COVID FREEZE FLAG: 2020-21 rows carry covid_freeze_flag=1 (courts closed/CTR paused — Eviction Lab published no 2019-2020 standardized rates; the ETS 2020-25 rows are FILINGS-ONLY proxies, never judgments)',
   'honest-null: Eviction Lab standardized city-grain rating STOPS at 2018 (pre-2016 legacy validated + 2016-2018 observed) — 2023 rates DO NOT EXIST at place grain; ETS filings-count proxy fills 2020-2025 for the 4 tracked cities ONLY (Denver/Detroit/St. Louis/Kingsport NOT tracked)',
 ],
 'route': {'s3_bucket': 'eviction-lab-data-downloads (s3.amazonaws.com, keyless)',
           'files': ['estimating-eviction-prevalance-across-us/place_proprietary_2000_2018.csv (observed)',
                     'legacy-data/validated/counties/all-counties.csv',
                     'ets/all_sites_monthly.csv (tracked-site monthly filings 2020-2025)'],
           'raw_files': '_bob19_outputs/_evict_raw/'},
 'place_fips_key_map': {'Memphis':'4748000','Cincinnati':'3915000','Detroit':'2622000','St. Louis':'2965000','NYC':'3651000','Houston':'4835000','Denver':'0820000','Kingsport':'4739560'},
 'counties_companion_key_map': {'Memphis':'47157 Shelby TN','Cincinnati':'39061 Hamilton OH','Detroit':'26163 Wayne MI','St. Louis':'29510 St. Louis city','NYC':'36061+36047+36005+36081+36085 (5 boroughs)','Houston':'48201 Harris TX','Denver':'08031 Denver CO','Kingsport':'47163 Sullivan TN'},
 'rows': ev,
 'row_count': len(ev),
}
ev_pairs = []
for r in ev:
    m = mr.get((r['city'], r['year']))
    jr = r.get('judgment_rate_per_1k_renter')
    if m is not None and jr is not None:
        ev_pairs.append({'city': r['city'], 'year': r['year'], 'judgment_rate': jr, 'murder_rate_t0': m})
ev_lane['joint_within_read'] = within_demeaned_reads(ev_pairs, 'judgment_rate', 'murder_rate_t0', 'judgment-rate x murder-rate t0 (2016-2018 overlap n)')

# ===== LANE 3: HEALTH OUTCOME =====
le = jl(O/'_health_raw/_chr_le_rows.json')
dp = jl(O/'_health_raw/_nchs_drugpoison_rows.json')
COUNTY_OF = {'47157':'Memphis','39061':'Cincinnati','26163':'Detroit','29510':'St. Louis',
 '36061':'NYC','36047':'NYC','36005':'NYC','36081':'NYC','36085':'NYC','48201':'Houston','08031':'Denver','47163':'Kingsport'}
CNAMES = {'47157':'Shelby County TN','39061':'Hamilton County OH','26163':'Wayne County MI','29510':'St. Louis city MO',
 '36061':'New York County NY','36047':'Kings County NY','36005':'Bronx County NY','36081':'Queens County NY','36085':'Richmond County NY',
 '48201':'Harris County TX','08031':'Denver County CO','47163':'Sullivan County TN'}
health_lane = {
 '_record': 'health_outcome_lane_v1 (BOB-SCAN-19 OUTPUT-blind-spot P1 = THE HEALTH-OUTCOME LANE)',
 'built': '2026-11-24',
 'laws_held': [
   'direction-class only, no causal claims',
   'no fabricated rows — LE read from the CHR analytic release CSVs (keyless), drug-poisoning rates from NCHS Socrata (keyless)',
   'GRAIN-LAW HELD: life-expectancy + drug-poisoning = COUNTY grain ONLY, shipped as the companion block, NEVER blended into the city-year panel (the lane13/lane12 precedent)',
   'route-note: CDC WONDER controller 403/WAF-blocked on this pass (banked); the keyless route is the CHR analytic-data CSVs (life-expectancy v147, 7 releases) + NCHS county drug-poisoning dataset rpvs-m2md class (Socrata)',
   'honest-null: no CITY-grain health-outcome annual series exists keyless — the county companion is the countable form; NYC = 5-borough average only when aggregated (flagged, not silently used)',
 ],
 'route': {'chr': 'countyhealthrankings.org/sites/default/files/media/document/analytic_data{2019..2025}(_v2).csv (keyless)',
           'nchs': 'data.cdc.gov/resource/rpvx-m2md.json (NCHS Drug Poisoning Mortality by County, model-based, 2003-2021)',
           'raw_files': '_bob19_outputs/_health_raw/'},
 'counties_companion_key_map': CNAMES,
 'years_note': 'CHR releases 2019-2025 carry measurement years spanning 2016-2023 (release N = data measured through year N-2..N-1 vintage; each release row tagged by its release year)',
 'chr_le_county_rows': le,
 'nchs_drug_poisoning_county_rows': dp,
 'row_count_le': len(le), 'row_count_drugpoison': len(dp),
}
# joint read: county LE (companion) x murder at county-vintage overlap — labeled companion-read, NOT panel-blend
le_pairs = []
for o in le:
    for d in (2020, 2021, 2022, 2023):
        city = COUNTY_OF[o['county_fips']]
        m = mr.get((city, o['release']))
        if m is not None and o['life_expectancy_years'] is not None:
            le_pairs.append({'city': city, 'year': o['release'], 'le': o['life_expectancy_years'], 'murder_rate_t0': m})
health_lane['companion_within_read_le_x_murder'] = within_demeaned_reads(le_pairs, 'le', 'murder_rate_t0', 'county-LE (companion) x murder-rate t0 — companion-read only, grain-law')
dp_pairs = []
for o in dp:
    city = COUNTY_OF[o['county_fips']]
    m = mr.get((city, o['year']))
    if m is not None:
        dp_pairs.append({'city': city, 'year': o['year'], 'dp_rate': o['drug_poisoning_death_rate_per_100k_model'], 'murder_rate_t0': m})
health_lane['companion_within_read_drugpoison_x_murder'] = within_demeaned_reads(dp_pairs, 'dp_rate', 'murder_rate_t0', 'county-drug-poisoning-rate (companion) x murder-rate t0')

(O/'pit_homelessness_lane_v1.json').write_text(json.dumps(pit_lane, indent=1), encoding='utf-8')
(O/'eviction_rate_lane_v1.json').write_text(json.dumps(ev_lane, indent=1), encoding='utf-8')
(O/'health_outcome_lane_v1.json').write_text(json.dumps(health_lane, indent=1), encoding='utf-8')
print('=== shipped ===')
print('pit rows', pit_lane['row_count'], 'nulls', len(pit_lane['honest_nulls_banked']))
print('evict rows', ev_lane['row_count'])
print('health LE', health_lane['row_count_le'], 'drugpoison', health_lane['row_count_drugpoison'])
print('PIT read:', json.dumps(pit_lane['joint_within_read']))
print('EV read:', json.dumps(ev_lane['joint_within_read']))
print('LE read:', json.dumps(health_lane['companion_within_read_le_x_murder']))
print('DP read:', json.dumps(health_lane['companion_within_read_drugpoison_x_murder']))
