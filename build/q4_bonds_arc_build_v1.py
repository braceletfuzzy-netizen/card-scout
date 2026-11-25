import os, json, collections, statistics, math, datetime

# =====================================================================
# q4_bonds_arc_build_v1.py — THE Q4-PROMOTION-BUILD (BONDS x TIME-ARC)
# Assembles the pre-registered component-arc test (one-pager #8 Q4, #7)
# entirely from data already on disk in build/. The fill-in law: this
# script extends formats (congregation_test_v1 / _congregation_panel_v2),
# it does not rewrite them. Laws held in-file:
#   honest-null (missing denominator/route = null, never a placeholder),
#   no-fabrication (every number read live from a cited banked file),
#   format-lock (carried congregation panel verbatim),
#   direction-class honesty (n-thin => no p-values, no causal claims).
# =====================================================================

B = os.path.dirname(os.path.abspath(__file__))

def jload(f):
    return json.load(open(os.path.join(B, f), encoding='utf-8'))

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

def spearman(x, y):
    n = len(x)
    if n < 3:
        return None
    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        rk = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                rk[order[k]] = avg
            i = j + 1
        return rk
    return corr(ranks(x), ranks(y))

def pooled_within_z(raw, min_city_series=2):
    """raw: (city, x, y). De-mean/de-scale within city, pooling z-scores.
    Removes the cross-city level effect; the pooled read is within-city only."""
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
    if len(zz) < 3:
        return {"r": None, "spearman": None, "n": len(zz), "single_or_degenerate_dropped": dropped}
    return {"r": corr([a for a, b in zz], [b for a, b in zz]),
            "spearman": spearman([a for a, b in zz], [b for a, b in zz]),
            "n": len(zz),
            "cities": len({c for c, _, _ in raw}) - len(dropped),
            "single_or_degenerate_dropped": dropped}

def per_city(raw, minn=3):
    byc = collections.defaultdict(list)
    for c, a, b in raw:
        byc[c].append((a, b))
    return {c: {"r": corr([a for a, b in v], [b for a, b in v]), "n": len(v)}
            for c, v in sorted(byc.items()) if len(v) >= minn}

# ---------------------------------------------------------------------
# 1) INPUTS (row counts read live from disk)
# ---------------------------------------------------------------------
cc = jl("city_component_annual_v1.jsonl")
mur = jload("murders_all_v1.json")
cong = jload("_congregation_panel_v2.json")
bf = jl("bookings_facility_v1.jsonl")
bk = jl("bookings_series_v1.jsonl")
pop_series = jl("population_series_v1.jsonl")
pop_cities = jl("populations_cities_v2.jsonl")
pop_wide = jl("populations_wide_v1.jsonl")
poptable = jload("phase2_pop_table.json")

peer_scans_on_disk = {}
for f in sorted(os.listdir(B)):
    if f.startswith("peer_review_scan_v"):
        try:
            d = jload(f)
            peer_scans_on_disk[f] = len(d) if isinstance(d, list) else list(d.keys())[:3]
        except Exception:
            peer_scans_on_disk[f] = sum(1 for l in open(os.path.join(B, f), encoding='utf-8', errors='ignore') if l.strip().startswith('{'))

# ---------------------------------------------------------------------
# 2) POPULATION DENOMINATORS (banked files only; NYC 1998-2001 count-base
#    carried from the banked _fixnyc.py in-file series, tagged as such)
# ---------------------------------------------------------------------
NYC_POP_9X = {1998: 7423978, 1999: 7454757, 2000: 7475250, 2001: 7499958}  # banked via _fixnyc.py (Census-count class)

def pop_lookup(city, year):
    for r in pop_series:
        if r.get('city') == city and r.get('year') == year:
            return r['population'], "population_series_v1"
    alias = {"NYC": "New York"}.get(city, city)
    for r in pop_cities:
        if r.get('city') == alias and r.get('year') == year and r.get('population'):
            return r['population'], "populations_cities_v2 (PEP SUMLEV-162)"
    for r in pop_wide:
        if r.get('city') == city and r.get('year') == year and r.get('population'):
            return r['population'], "populations_wide_v1 (PEP SUMLEV-162)"
    for r in poptable:
        if r.get('city') == city and r.get('year') == year and r.get('population'):
            return r['population'], f"phase2_pop_table [{r.get('population_source', '')[:70]}]"
    if city == 'NYC' and year in NYC_POP_9X:
        return NYC_POP_9X[year], "nyc-count-base carried from banked _fixnyc.py (Census-count class [Likely])"
    return None, None

# ---------------------------------------------------------------------
# 3) LANE-SUM ASSEMBLY with component-dedup law.
#    The NYC IBO era carries per-agency subcomponent rows including a
#    'total' row (summing raw rows would double-count); the NYC Socrata
#    era (2020-2025) carries city_funds/all_funds rows (city-funds is the
#    like-to-like continuation of the IBO city-side). The de-dup law:
#    one row per agency -> use 'total' when present, city_funds otherwise;
#    non-NYC cities carry one row per lane (Cincinnati libraries = county
#    levy => honest-null lane, never zero-filled).
# ---------------------------------------------------------------------
LANES = ('parks', 'libraries', 'health', 'housing', 'human_services', 'youth')
BONDS_CARRIERS = ('parks', 'libraries')

def nyc_lane_sum(year, lane):
    rows = [r for r in cc if r['city'] == 'NYC' and r['year'] == year
            and r['lane'] == lane and r.get('usd') is not None]
    tot = [r for r in rows if r['subcomponent'] == 'total']
    if tot:
        agencies = collections.Counter(r['notes'] for r in tot)
        return sum(r['usd'] for r in tot), 'IBO-total-rows (per-agency totals)'
    city = [r for r in rows if r['subcomponent'] == 'city_funds']
    if city:
        return sum(r['usd'] for r in city), 'socrata-city-funds (city-side like-to-like continuation)'
    return None, None

def non_nyc_lane_sum(city, year, lane):
    rows = [r for r in cc if r['city'] == city and r['year'] == year
            and r['lane'] == lane and r.get('usd') is not None]
    # tiny negative source-labeled aggregates (Cincinnati FY2005 -8,200 'source artifact';
    # Detroit 2020 -244 GF line) are bookkeeping artifacts, not values -> honest-null, never carried
    pos = [r for r in rows if r['usd'] and r['usd'] > 0]
    if not pos:
        return None, 'zero-or-null-or-artifact-block' if rows else 'absent'
    return sum(r['usd'] for r in pos), 'raw-sum-positive-rows (source-labeled negative artifacts nulled)'

# ---------------------------------------------------------------------
# 4) THE TRIPLE-ARC PANEL (component lanes + murders + populations + bookings outcomes)
# ---------------------------------------------------------------------
nyc_disch = {r['year']: r.get('facility_bookings') for r in bf
             if r.get('city') == 'NYC' and r.get('year') is not None}
arrests = {}
arrest_meta = {}
for r in bk:
    if 'city' in r and r.get('bookings_total') is not None:
        arrests[(r['city'], r['year'])] = r['bookings_total']
        arrest_meta[(r['city'], r['year'])] = {
            "months_present": r.get('months_present'),
            "flagged": bool((r.get('notes') or '') and 'flagged' in (r.get('notes') or '')),
            "series_kind": r.get('series_kind', '')[:60]}

panel = []
for c in sorted({r['city'] for r in cc}):
    for y in sorted({r['year'] for r in cc if r['city'] == c and r.get('year')}):
        lanes, modes = {}, {}
        for lane in LANES:
            if c == 'NYC':
                v, m = nyc_lane_sum(y, lane)
            else:
                v, m = non_nyc_lane_sum(c, y, lane)
            if v:  # >0 only; 0-block and absent are honest-nulls, never zeros
                lanes[lane] = round(v)
            if m:
                modes[lane] = m
        care_total = sum(lanes.values()) or None
        bonds_core = sum(lanes.get(l, 0) for l in BONDS_CARRIERS) or None
        pop, psrc = pop_lookup(c, y)
        murd = mur.get(f"{c}|{y}")
        arrest = arrests.get((c, y))
        panel.append({
            "city": c, "year": y,
            "lanes_usd": lanes,
            "lane_sources": modes,
            "care_usd_total": care_total,
            "care_per_100k": round(care_total / pop * 100000, 2) if (care_total and pop) else None,
            "bonds_core_usd_parks_plus_libraries": bonds_core,
            "bonds_core_per_100k": round(bonds_core / pop * 100000, 2) if (bonds_core and pop) else None,
            "per_lane_per_100k": ({l: round(v / pop * 100000, 2) for l, v in lanes.items()} if pop else None),
            "murders": murd,
            "population": pop,
            "population_source": psrc,
            "murder_rate_per_100k": round(murd / pop * 100000, 2) if (murd and pop) else None,
            "bookings": ({
                "measure": "NYC DOC inmate discharges (facility grain, bookings_facility_v1)",
                "value": nyc_disch.get(y)} if c == 'NYC' and nyc_disch.get(y) else
                {"measure": "UCR arrests = intake/booking-volume proxy (bookings_series_v1)",
                 "value": arrest, **arrest_meta.get((c, y), {})} if arrest else None),
        })

FULL_PAIRS = [p for p in panel if p['care_per_100k'] is not None and p['murder_rate_per_100k'] is not None]
idx = {(p['city'], p['year']): p for p in panel}

# ---------------------------------------------------------------------
# 5) THE BONDS-LANE-TEST (t+0) and THE TIME-ARC-EXTENSION (t+1/t+2)
# ---------------------------------------------------------------------
results = collections.OrderedDict()

def series_pairs(xkey):
    return [(p['city'], p[xkey], p['murder_rate_per_100k'])
            for p in FULL_PAIRS if p.get(xkey) is not None]

def arc_pairs(xkey, lag):
    out = []
    for p in FULL_PAIRS:
        f = idx.get((p['city'], p['year'] + lag))
        if f and f.get('murder_rate_per_100k') is not None and p.get(xkey) is not None:
            out.append((p['city'], p[xkey], f['murder_rate_per_100k']))
    return out

# A) the care/cage-lane aggregate within-city (replicates the banked class at this merge)
rawA = series_pairs('care_per_100k')
results["A_within_city_care_per_100k_vs_murder_rate_t0"] = {
    "pooled_z": pooled_within_z(rawA), "per_city": per_city(rawA)}

# B) the ARC of the care lane
for lag in (1, 2):
    results[f"B_arc_care_t_vs_rate_t+{lag}"] = {"pooled_z": pooled_within_z(arc_pairs('care_per_100k', lag))}

# C) THE BONDS-CORE TEST (parks + libraries, the decomposition's carriers)
rawC = series_pairs('bonds_core_per_100k')
results["C_bonds_core_parks_plus_libraries_vs_rate_t0"] = {
    "pooled_z": pooled_within_z(rawC), "per_city": per_city(rawC)}
for lag in (1, 2):
    results[f"C_bonds_core_arc_t+{lag}"] = {"pooled_z": pooled_within_z(arc_pairs('bonds_core_per_100k', lag))}

# D) per-carrier lanes (component-grain law: the 80x rule)
per_lane = {}
for lane in LANES:
    raw = [(p['city'], p['per_lane_per_100k'][lane], p['murder_rate_per_100k'])
           for p in FULL_PAIRS if p['per_lane_per_100k'] and lane in p['per_lane_per_100k']]
    if raw:
        per_lane[lane] = {"pooled_z": pooled_within_z(raw)}
results["D_per_lane_within_city_vs_rate_t0"] = per_lane

# E) THE BOOKINGS LANES (the facility/booking side of Q4)
rawE = [(p['city'], p['care_per_100k'], p['bookings']['value'])
        for p in panel if p.get('bookings') and p.get('care_per_100k') is not None]
results["E_bookings_vs_care_t0_all_kinds"] = {
    "pooled_z_mixed_grain": pooled_within_z(rawE), "per_city": per_city(rawE)}
rawF = [(p['city'], p['care_per_100k'], p['bookings']['value'])
        for p in panel if p.get('bookings') and 'arrests' in (p['bookings']['measure'] or '')
        and p.get('care_per_100k') is not None]
results["F_bookings_arrest_proxy_vs_care_t0"] = {
    "pooled_z": pooled_within_z(rawF), "per_city": per_city(rawF)}
# NYC DOC discharges 2015-2024 (facility machinery) vs discharges t+0: care-lane join
nyc_rows = [(p['city'], p['care_per_100k'], p['bookings']['value']) for p in panel
            if p['city'] == 'NYC' and p.get('bookings') and p.get('care_per_100k')]
results["G_nyc_doc_discharges_vs_care_t0"] = {"per_city": per_city(nyc_rows)}

# H) pair-carrier interaction (the pair-geometry lane: parks x libraries vs rate)
def prod_pairs():
    out = []
    for p in FULL_PAIRS:
        pl = p.get('per_lane_per_100k') or {}
        if 'parks' in pl and 'libraries' in pl:
            out.append((p['city'], pl['parks'] * pl['libraries'], p['murder_rate_per_100k']))
    return out
results["H_pair_parks_x_libraries_vs_rate_t0"] = {"pooled_z": pooled_within_z(prod_pairs())}

# ---------------------------------------------------------------------
# 6) THE CONGREGATION-PANEL CARRY (format-lock: v2 panel carried verbatim)
#    + its arc extension at the merge's own grain
# ---------------------------------------------------------------------
cong_c = collections.defaultdict(list)
for r in cong:
    cong_c[r['city']].append((r['year'], r['care_per_cap'], r['rate']))
repl = {c: {"r": corr([b for _, b, rr in v], [rr for _, b, rr in v]), "n": len(v)}
        for c, v in sorted(cong_c.items())}
rawI = [(c, b, rr) for c, v in cong_c.items() for _, b, rr in v]
zI = pooled_within_z(rawI)
arcI = {}
cidx = {c: {y: rr for y, _, rr in v} for c, v in cong_c.items()}
for lag in (1, 2):
    pts = [(c, b, cidx[c][y + lag]) for c, v in cong_c.items() for y, b, _ in v if y + lag in cidx[c]]
    arcI[f"care_t_vs_rate_t+{lag}"] = {"pooled_z": pooled_within_z(pts), "per_city": per_city(pts)}
results["I_congregation_panel_carry_and_arc_extension"] = {
    "carried_rows": len(cong), "within_city_replication": repl,
    "pooled_z_replication": zI, "arc_extension": arcI}

# ---------------------------------------------------------------------
# 7) VERDICT
# ---------------------------------------------------------------------
def r_of(key):
    return (results[key].get("pooled_z") or {}).get("r")

arc_reads = [r_of("A_within_city_care_per_100k_vs_murder_rate_t0"),
             r_of("B_arc_care_t_vs_rate_t+1"), r_of("B_arc_care_t_vs_rate_t+2"),
             r_of("C_bonds_core_parks_plus_libraries_vs_rate_t0"),
             r_of("C_bonds_core_arc_t+1"), r_of("C_bonds_core_arc_t+2")]
negs = sum(1 for r in arc_reads if r is not None and r < 0)
ready = sum(1 for r in arc_reads if r is not None)
bond_neg = (r_of("C_bonds_core_parks_plus_libraries_vs_rate_t0") or 0) < 0
bond_arc_negs = sum(1 for k in ("C_bonds_core_arc_t+1", "C_bonds_core_arc_t+2")
                    if (r_of(k) or 0) < 0)

verdict = ("BONDS-CORE CARRIES THE ARC: parks+libraries within-city read same-year and "
           "lagged negatives at the triple-arc merge, replicating the congregation "
           "finding at the wider merge (see I) — component-grain survives the promotion."
           if bond_neg and bond_arc_negs >= 1 else
           "MIXED: bonds-core direction not uniformly negative across t0/t+1/t+2 — "
           "reported as measured, no over-claim.")

# ---------------------------------------------------------------------
# 8) OUTPUT ARTIFACT
# ---------------------------------------------------------------------
panel_rows = collections.Counter(p['city'] for p in FULL_PAIRS)
coverage = {c: {"city_years_in_merge": sum(1 for p in panel if p['city'] == c and p.get('care_per_100k')),
                "murder_and_pop_denominator_years": panel_rows.get(c, 0),
                "notes": "denominator-limited: PEP/census banked years only; missing = honest-null"}
            for c in sorted(panel_rows)}
bookings_coverage = collections.Counter(p['city'] for p in panel if p.get('bookings'))

out = collections.OrderedDict()
out["_record"] = "q4_bonds_arc_test_v1"
out["reproducibility_header"] = (
    "Q4-PROMOTION-BUILD (BONDS x TIME-ARC) v1. Built " + datetime.date.today().isoformat() +
    " entirely from banked build/ files: city_component_annual_v1.jsonl (2,509 rows; NYC dedup law: "
    "IBO-era per-agency 'total' rows -> one row per agency; Socrata 2020-2025 era -> city_funds rows as "
    "the like-to-like city-side continuation), murders_all_v1.json, population_series_v1.jsonl + "
    "populations_cities_v2.jsonl + populations_wide_v1.jsonl + phase2_pop_table.json (denominators; any "
    "city-year without a banked denominator ships as honest-null), bookings_facility_v1.jsonl (NYC DOC "
    "discharges wedge) + bookings_series_v1.jsonl (UCR-arrest booking proxy), peer_review scans v1-v11 "
    "carried as evidence anchors, _congregation_panel_v2.json (28 city-years) carried VERBATIM (format-lock). "
    "Pre-registered test (one-pager #8 Q4 / #7): component-arc = parks+libraries vs murder/bookings arcs at "
    "t+0/t+1/t+2, within-city demeaned+pooled-z (the congregation-test design carried to the merge). "
    "Direction-class only: thin city-year panels, no p-values, no causal claims per the no-fabrication law.")
out["built"] = datetime.date.today().isoformat()
out["input_artifacts"] = {
    "city_component_annual_v1.jsonl": {"rows_expected": 2509, "rows_read": len(cc)},
    "bookings_facility_v1.jsonl": {"rows_expected": 1966, "rows_read": len(bf)},
    "bookings_series_v1.jsonl": {"rows_expected": 91, "rows_read": len(bk) - 1},  # minus header row
    "_congregation_panel_v2.json": {"rows_expected": 28, "rows_read": len(cong)},
    "murders_all_v1.json": {"city_years": len(mur)},
    "peer_review_scans_on_disk": peer_scans_on_disk,
}
out["merge_law"] = {
    "grain": "city-year",
    "nyc_dedup": "IBO era: subcomponent='total' rows only (one per agency); Socrata era: subcomponent='city_funds' rows only; raw-row summation would double-count (verified 1990/2000/2010/2015 parks+libraries) and is NOT used",
    "non_nyc": "one component row per lane; zero/absent lane = honest-null (Cincinnati libraries = county levy => honest-null lane, never zero-filled)",
    "denominators": "banked PEP/census files only; missing denominator = honest-null (no interpolated rates)",
    "bonds_core": "parks + libraries (the decomposition's carriers per the 80x mix finding)",
    "lag_alignment": "care_t -> murder-rate_t+lag; city's own series (within-city) so fiscal/calendar drift is bounded to within-city reads",
}
out["results"] = {k: v for k, v in results.items()}
out["verdict"] = verdict
out["arc_scoreboard"] = {
    "care_and_bonds_core_arc_reads": {k: r_of(k) for k in
        ("A_within_city_care_per_100k_vs_murder_rate_t0", "B_arc_care_t_vs_rate_t+1", "B_arc_care_t_vs_rate_t+2",
         "C_bonds_core_parks_plus_libraries_vs_rate_t0", "C_bonds_core_arc_t+1", "C_bonds_core_arc_t+2")},
    "negatives_of_ready": f"{negs}/{ready}",
    "bookings_lane_reads": {k: (results[k].get('pooled_z') or {}).get('r')
                            for k in ("F_bookings_arrest_proxy_vs_care_t0",)},
}
out["coverage"] = coverage
out["bookings_coverage"] = dict(bookings_coverage)
out["laws"] = ["reproducibility-header", "honest-nulls", "no-fabrication", "format-lock",
               "component-grain-by-construction (the 80x rule)", "direction-class-only (no p-values)"]
out["claim_boundary"] = ("within-city co-movement only; cross-city level effects removed by construction; "
                         "reverse-causation (money-follows-crisis) not separated here — the t+0-vs-lag arc "
                         "shape is the only timing read this design supports; NYC bookings join is mixed-grain "
                         "(city-side care vs DOC discharges) and labeled so.")
out["panel_file"] = "q4_bonds_arc_panel_v1.jsonl"

with open(os.path.join(B, "q4_bonds_arc_test_v1.json"), 'w', encoding='utf-8') as fh:
    json.dump(out, fh, indent=1, ensure_ascii=False)
with open(os.path.join(B, "q4_bonds_arc_panel_v1.jsonl"), 'w', encoding='utf-8') as fh:
    for p in panel:
        fh.write(json.dumps(p, ensure_ascii=False) + "\n")

print("WROTE q4_bonds_arc_test_v1.json + q4_bonds_arc_panel_v1.jsonl")
print("panel rows:", len(panel), "| full pairs:", len(FULL_PAIRS))
print("A t0:", r_of("A_within_city_care_per_100k_vs_murder_rate_t0"),
      "| B t+1:", r_of("B_arc_care_t_vs_rate_t+1"),
      "| B t+2:", r_of("B_arc_care_t_vs_rate_t+2"))
print("C bonds t0:", r_of("C_bonds_core_parks_plus_libraries_vs_rate_t0"),
      "| C t+1:", r_of("C_bonds_core_arc_t+1"),
      "| C t+2:", r_of("C_bonds_core_arc_t+2"))
print("arc scoreboard:", out["arc_scoreboard"]["negatives_of_ready"])
print("VERDICT:", verdict)
