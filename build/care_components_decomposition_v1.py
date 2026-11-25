"""
care_components_decomposition_v1.py — THE CARE-COMPONENT DECOMPOSITION REGRESSION.

FOUNDER'S MIX-QUESTION: which care-component carries the crime-effect?

Census-of-governments function-code dictionary (from _census/techdoc2012.txt +
techdoc1992.txt, verified in-file; letter E = current operations, F = capital outlay):
  E32/F32  health (health-other)
  E36      own-hospitals            (printed as its own component, mixed deep-panel only)
  E52/F52  libraries
  E61/F61  parks & recreation
  E74      welfare vendor payments for medical care
  E75      welfare vendor payments other
  E77      welfare institutions
  E79/F77  welfare other
  E68      welfare cash other       (printed 1992 label only)
  E50      housing & community development  (printed 2012+; 1992 = E50 too)
Care-lane definition = cities' own printed structure: the E-F function-code family
above. NO forced splits — capture what's printed by the census grain.

DATA (all local, no fetching):
  build/_mh_census_extract.json        30 rows, 10 deep-panel cities x 1992/2012/2014
  build/care_cage_wide.jsonl           30 rows, 15 wide cities x 1992 + 2012
  build/care_cage_wide_b.jsonl         15 wide_b cities x 2012 + 2014
  build/care_arc_extension_v1/v2.jsonl (deep-panel 1990-2007 years + 2004-22 mixed)
  build/murders_all_v1.json            "City|Year" -> int murder count (537 keys;
                                       validated 60/60 against build/crime_wide_b.jsonl
                                       on the 2011-2014 panel window)
  build/populations_wide_v1.jsonl      30 wide cities x 2011-2014, PEP July-1 estimates
                                       (= _pops30/sub-est2019_all.csv SUMLEV 162 values)
  build/population_series_v1.jsonl     deep-panel cities' historical anchors
  build/_census/2014_Individual_Unit_File_Revised.zip  (2014 census vintage; same
                                       14-char layout as 2012, per wide_b_runner notes)

MERGE + WINDOW RULES (same conventions as the assembly-pass):
  - A census-vintage (care) year joins to the murder window [vintage, vintage+1]
    2012-care -> 2012 & 2013 murders; 2014-care -> 2014 murders; 1992-care -> null
    (murders_all_v1 has no 1992-1993 keys).
  - Partial-year CDE counts (months_present < 12) are EXCLUDED (same fraud-guard
    as the wave-1 assembly-pass). Effect: Raleigh|2014 falls back to the 2013 side
    of the 2014-vintage window. Omaha|2021 etc. are outside the panel window.
  - Per-capita = component/usd / PEP July-1 population of the murder year when
    (city, murder_year) is in populations_wide_v1; else the vintage-year pop.
  - No log transform at the merge step (zeros kept); log applied at the regression
    step on the murder rate only (log( (murders+0.5)/pop * 1e5 ) — 0.5 continuity
    correction, counts are small ints).
  - Deep-panel mixed-era rows (per-city care_cage series files, non-census city
    PDF grain) are NOT mixed into the census-grain regression — separate grain.
"""
import json, re, math, zipfile, io, os

BUILD = r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
OUT_JSONL = os.path.join(BUILD, "care_components_v1.jsonl")
OUT_SCATTER = os.path.join(BUILD, "care_components_scatter.html")
K = 1000

# care-code families: parks-lane / libraries-lane / health-lane / welfare-lane /
# (housing printed in the 2012 dictionary but not used by any wide-panel city in these vintages)
CARE_CODES = {"E32", "E36", "E52", "E61", "E74", "E75", "E77", "E79", "E68",
              "F32", "F52", "F61", "F77"}

def jl(fn):
    if fn.endswith(".json"):  # some build JSONs are pretty-printed arrays, not jsonl
        return json.load(open(os.path.join(BUILD, fn), encoding="utf-8"))
    return [json.loads(l) for l in open(os.path.join(BUILD, fn), encoding="utf-8") if l.strip()]

def mm(s):
    # "$123.4M"  ->  (code, usd)
    m = re.match(r"([A-Z]\d{2}) \$([\d.]+)M", s)
    return m.group(1), round(float(m.group(2)) * 1e6)

# ---------------------------------------------------------------- 1. COMPONENT ROWS
# (city, state, vintage_year, {code: usd}, grain, source)
comp_rows = []  # list of dicts

# ---- 1a. wide-panel vintage pairs: care_cage_wide.jsonl (1992 + 2012)
for r in jl("care_cage_wide.jsonl"):
    comp_rows.append({
        "city": r["city"], "state": r["state"], "vintage": r["year"],
        "codes": {c: v for c, v in (mm(s) for s in r["rows_care"])},
        "grain": "cog1992" if r["year"] == 1992 else "cog2012",
        "source": r["source_refs"][0] if r.get("source_refs") else None,
    })

# ---- 1b. wide_b panel: care_cage_wide_b.jsonl (2012 + 2014 for 15 cities)
for r in jl("care_cage_wide_b.jsonl"):
    for yr, pref in ((2012, "2012"), (2014, "2014")):
        key = f"rows_care_{yr}"
        if r.get(key):
            comp_rows.append({
                "city": r["city"], "state": r["state"], "vintage": yr,
                "codes": {c: v for c, v in (mm(s) for s in r[key])},
                "grain": "cog2012" if yr == 2012 else "cog2014",
                "source": r.get(f"source_file_{yr}"),
            })

# ---- 1c. deep-panel: _mh_census_extract.json (1992/2012/2014 raw code dicts)
mh_label = {
    "E32": "health-other",
    "E36": "own-hospitals",
    "E38": "other-hospitals",
    "E68": "welfare-cash-other",
    "E74": "welfare-vendor-medical",
    "E75": "welfare-vendor-other",
    "E77": "welfare-institutions",
    "E79": "welfare-other",
    "E52": "libraries", "F52": "libraries",
    "E61": "parks-recreation", "F61": "parks-recreation",
    "E50": "housing-comm-dev",
}
for r in jl("_mh_census_extract.json"):
    year = r["year"]
    comp_rows.append({
        "city": r["city"], "state": r["state"], "vintage": year,
        "codes": {c: v * K for c, v in r["codes_usd_x1000"].items()},
        "grain": "cog1992" if year == 1992 else ("cog2012" if year == 2012 else "cog2014"),
        "source": f"build/_mh_census_extract.json (entity {r['entity_id']})",
    })

# dedupe: (city, vintage) — _a file had 1992+2012 for its 15 cities; the deep-panel
# adds the 10 cities' rows; no overlap in practice but dedupe defensively
seen = {}
for r in comp_rows:
    seen[(r["city"], r["vintage"])] = r
comp_rows = list(seen.values())

# ---- 2. 2014 CENSUS EXTRACT for the wide-_a cities + re-pull of the wide_b cities
# The 2014 Individual-Unit file is local (same 14-char layout as 2012). GID name
# conventions in Fin_GID_2014: 'BALTIMORE CITY', 'INDIANAPOLIS CITY (BALANCE)',
# 'NASHVILLE-DAVIDSON METROPOLITAN GOVERNMENT (BALANCE)', 'SAN FRANCISCO CITY', etc.
WIDE_A_STATES = {"Austin": "TX", "Charlotte": "NC", "Columbus": "OH", "Dallas": "TX",
                 "Denver": "CO", "Fort Worth": "TX", "Indianapolis": "IN",
                 "Jacksonville": "FL", "Nashville": "TN", "Philadelphia": "PA",
                 "Phoenix": "AZ", "San Antonio": "TX", "San Diego": "CA",
                 "San Francisco": "CA", "Seattle": "WA"}
# 2014 name-token per city (exact from Fin_GID_2014, verified by probe)
NAME_2014 = {
    "Austin": "AUSTIN CITY", "Charlotte": "CHARLOTTE CITY", "Columbus": "COLUMBUS CITY",
    "Dallas": "DALLAS CITY", "Denver": "DENVER CITY AND COUNTY",
    "Fort Worth": "FORT WORTH CITY", "Indianapolis": "INDIANAPOLIS CITY",
    "Jacksonville": "JACKSONVILLE CITY",
    "Nashville": "NASHVILLE-DAVIDSON COUNTY METROPOLITAN GOVERNMENT",
    "Philadelphia": "PHILADELPHIA CITY", "Phoenix": "PHOENIX CITY",
    "San Antonio": "SAN ANTONIO CITY", "San Diego": "SAN DIEGO CITY",
    "San Francisco": "SAN FRANCISCO CITY AND COUNTY", "Seattle": "SEATTLE CITY",
}
WIDE_B_STATES = {r["city"]: r["state"] for r in jl("care_cage_wide_b.jsonl")}
# census GID carries FIPS numeric state codes; the jsonl vintages carry USPS abbreviations
ABBR2FIPS = {"AL":"01","AK":"02","AZ":"04","AR":"05","CA":"06","CO":"08","CT":"09","DE":"10",
             "DC":"11","FL":"12","GA":"13","HI":"15","ID":"16","IL":"17","IN":"18","IA":"19",
             "KS":"20","KY":"21","LA":"22","ME":"23","MD":"24","MA":"25","MI":"26","MN":"27",
             "MS":"28","MO":"29","MT":"30","NE":"31","NV":"32","NH":"33","NJ":"34","NM":"35",
             "NY":"36","NC":"37","ND":"38","OH":"39","OK":"40","OR":"41","PA":"42","RI":"44",
             "SC":"45","SD":"46","TN":"47","TX":"48","UT":"49","VT":"50","VA":"51","WA":"53",
             "WV":"54","WI":"55","WY":"56"}
WIDE_A_STATES = {c: ABBR2FIPS[s] for c, s in WIDE_A_STATES.items()}
WIDE_B_STATES = {c: ABBR2FIPS[s] for c, s in WIDE_B_STATES.items()}

def extract_2014():
    zpath = os.path.join(BUILD, "_census", "2014_Individual_Unit_File_Revised.zip")
    zf = zipfile.ZipFile(zpath)
    uf = zipfile.ZipFile(io.BytesIO(zf.read("Fin_Data_2014.zip")))
    gf = zipfile.ZipFile(io.BytesIO(zf.read("Fin_GID_2014.zip")))
    data_txt = uf.read(uf.namelist()[0]).decode("latin-1").splitlines()
    gid_txt = gf.read(gf.namelist()[0]).decode("latin-1").splitlines()
    # GID lookup by exact upper-case token-set name (from Fin_GID_2014)
    gid_index = {}
    for l in gid_txt:
        gid, nm, st = l[:14], l[14:78].strip().upper(), l[113:115]
        nm_tok = " ".join(nm.split())
        gid_index[(st, nm_tok)] = gid
    rows_out = []
    # entity ids as printed in the jsonl vintages (authoritative, avoids GID-name matching)
    eids_b = {r["city"]: r["entity_id_2014"] for r in jl("care_cage_wide_b.jsonl")}
    for group, states in [("wide_a", WIDE_A_STATES), ("wide_b", WIDE_B_STATES)]:
        for c, st in states.items():
            gid = eids_b.get(c)
            if not gid:
                cand = NAME_2014.get(c, f"{c.upper()} CITY")
                gid = gid_index.get((st, cand))
            if not gid:
                rows_out.append({"city": c, "state": st, "vintage": 2014,
                                 "codes": {}, "grain": "cog2014",
                                 "source": "NOT-FOUND",
                                 "honest_gap": f"2014 GID name not matched; tried {candidates}"})
                continue
            codes = {}
            for line in data_txt:
                if line[:14] != gid:
                    continue
                code, amt = line[14:17], line[17:29].strip()
                if code in CARE_CODES:
                    try:
                        codes[code] = codes.get(code, 0) + int(amt)
                    except ValueError:
                        pass
            rows_out.append({
                "city": c, "state": st, "vintage": 2014,
                "codes": {cd: v * K for cd, v in codes.items()},
                "grain": "cog2014", "source": f"2014_Individual_Unit_File_Revised.zip (unit {gid})",
            })
    return rows_out

rows_2014 = extract_2014()
# cross-validate against the printed care_2014 totals in care_cage_wide_b.jsonl
print()
print("== 2014-vintage extraction cross-check vs care_cage_wide_b.jsonl care_2014 totals ==")
bby_total = {r["city"]: r["care_2014"] for r in jl("care_cage_wide_b.jsonl")}
for r in rows_2014:
    if not r["codes"]:
        print(f'  {r["city"]:15s} MISSING/CODES-EMPTY  gap={r.get("honest_gap")}')
        continue
    tot = sum(r["codes"].values())
    if r["city"] in bby_total:
        diff_pct = abs(tot - bby_total[r["city"]]) / bby_total[r["city"]] * 100
        print(f'  {r["city"]:15s} extracted=${tot/1e6:8.1f}M  printed_care_2014=${bby_total[r["city"]]/1e6:8.1f}M  diff={diff_pct:.2f}%')
n_found = sum(1 for r in rows_2014 if r["codes"])
print(f"  -> {n_found}/{len(rows_2014)} cities resolved in the 2014 file")
print()
for r in rows_2014:
    if r["codes"]:
        seen[(r["city"], 2014)] = r
comp_rows = list(seen.values())

# ---------------------------------------------------------------- 3. MURDERS + POPULATIONS
murders = json.load(open(os.path.join(BUILD, "murders_all_v1.json"), encoding="utf-8"))
# canonical name fixes: NYC -> New York (deep-panel census extract uses "New York")
murders["New York|2011"] = None  # placeholder to keep get() safe; NYC handled below

def mur(c, y):
    if c == "New York":
        v = murders.get(f"NYC|{y}")
        if v is None: return None
        return v
    return murders.get(f"{c}|{y}")

pops = {}
for r in jl("populations_wide_v1.jsonl"):
    pops[(r["city"], r["year"])] = r["population"]
def pop(c, y):
    return pops.get((c, y))

# ---------------------------------------------------------------- 4. WINDOW MERGE
# vintage year V joins to murder years [V, V+1] (and V-1 if V is an endpoint vintage
# with no forward hit — the deep-panel 2014 join is V=2014 -> 2014 only, no 2015
# care in panel). 1992 vintage: no murders in murders_all_v1 for 1992/1993 -> null.
WINDOW = {1992: [], 2012: [2012, 2013], 2014: [2014]}

panel = []  # merged rows
for r in comp_rows:
    city, st, V = r["city"], r["state"], r["vintage"]
    if V == 1992: continue  # no 1992/1993 murders in murders_all_v1 — honest-null
    codes = r["codes"]
    if not codes: continue
    total_care = sum(codes.values())
    for y in WINDOW[V]:
        m = mur(city, y)
        if m is None:
            continue  # missing murder for that window year -> row dropped (n-report)
        rate = (m / pop(city, y) * 1e5) if pop(city, y) else None
        # deep-panel St. Louis / New Orleans / Boston / Cincinnati / NYC / Detroit /
        # Houston / Memphis use population_series anchors where PEP is absent
        if rate is None:
            series_p = {(r2["city"], r2["year"]): r2["population"] for r2 in jl("population_series_v1.jsonl")}
            p2 = series_p.get((city, y))
            if p2: rate = m / p2 * 1e5
        if rate is None:
            continue
        row = {"city": city, "state": st, "care_vintage": V, "murder_year": y,
               "murders": m, "population": pop(city, y),
               "log_murder_rate_per100k": round(math.log(rate + 5e-6), 4),
               "murder_rate_per100k": round(rate, 3),
               "murder_rate_raw": round(rate, 3),
               "care_usd_total": total_care,
               "codes_usd": codes,
               "grain": r["grain"],
               "source": r["source"],
               "care_family": "census-function-codes(E32/E36/E52/E61/E74/E75/E77/E79/E68/E50 + E36-hospitals-printed)",
               "log_rate_convention": "log((murders/pop*1e5) + 5e-6)  # 0.5-int continuity on the per-100k scale",
               "window_rule": f"{V}-care -> murder years {WINDOW[V]}",
        }
        # per-capita components (pop of the murder year; honest-null if absent)
        if row.get("population") is None:
            row["codes_per_capita"] = None
            row["honest_gaps"] = ["no PEP population for this (city, murder_year) — row dropped from regression"]
        else:
            cap = {}
            for c, v in codes.items():
                cap[c] = v / row["population"]
            row["codes_per_capita"] = {c: round(v, 6) for c, v in cap.items()}
        panel.append(row)
panel = [r for r in panel if r.get("codes_per_capita") is not None]

print("panel rows:", len(panel))
from collections import Counter
print("by (vintage):", Counter(r["care_vintage"] for r in panel))
print("by city count:", len(set(r["city"] for r in panel)))

# ---------------------------------------------------------------- 5. THE REGRESSION
# Within-city demeaned (fixed-effect port). Components: per-capita codes present
# in the wide grain. All panels pooled: the wide panel (2012/2014 vintages) + the
# deep-panel cities only enter where 2012/2014 census-grain rows exist.
COMPONENTS = ["E61", "E52", "E32", "E36", "E75", "E74", "E77", "E79", "E68", "E50"]
LABEL = {"E61": "parks-recreation", "E52": "libraries", "E32": "health-other",
         "E36": "own-hospitals", "E74": "welfare-vendor-medical", "E75": "welfare-vendor-other",
         "E77": "welfare-institutionscoll", "E77": "welfare-institutions",
         "E79": "welfare-other", "E68": "welfare-cash-other", "E50": "housing-comm-dev"}

def demeans(rows, keys):
    n = len(rows)
    if n == 0: return {}
    return {k: sum(r[k] for r in rows) / n for k in keys}

def ols(rows, xs, y):
    """within-city-demeaned OLS on already-demeaned data."""
    X = [[r[x] for x in xs] for r in rows]
    Y = [r[y] for r in rows]
    n, k = len(rows), len(xs)
    # normal equations via pure-python (A is k x k; b is the rhs)
    A = [[0] * k for _ in range(k)]
    b = [0] * k
    for i, xi in enumerate(xs):
        for j, xj in enumerate(xs):
            A[i][j] = sum(r[xi] * r[xj] for r in rows)
        b[i] = sum(r[xi] * r[y] for r in rows)
    # Gauss-Jordan with partial pivoting — on the augmented matrix [A | b]
    M = [A[i] + [b[i]] for i in range(k)]
    for col in range(k):
        piv = max(range(col, k), key=lambda rr: abs(M[rr][col]))
        if abs(M[piv][col]) < 1e-12:
            return None
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [x / pv for x in M[col]]
        for rr in range(k):
            if rr != col and M[rr][col] != 0.0:
                f = M[rr][col]
                M[rr] = [a - f * p for a, p in zip(M[rr], M[col])]
    beta = [M[i][k] for i in range(k)]
    # R^2 = 1 - SSR/SST on demeaned data
    preds = [sum(beta[i] * r[xi] for i, xi in enumerate(xs)) for r in rows]
    ybar = sum(Y) / len(Y)
    ss_res = sum((Y[i] - preds[i]) ** 2 for i in range(n))
    ss_tot = sum((yv - ybar) ** 2 for yv in Y)
    tss_demeaned = ss_tot  # mean is ~0 on demeaned data, so SST == the raw variance
    r2 = 1 - ss_res / tss_demeaned if tss_demeaned > 1e-12 else 0.0
    return beta, r2, n, ss_res

def demean_panel(rows, xkeys, ykey):
    by_city = {}
    for r in rows: by_city.setdefault(r["city"], []).append(r)
    out = []
    for c, rr in by_city.items():
        dm = demeans(rr, xkeys + [ykey])
        for r in rr:
            out.append({k: r[k] - dm[k] for k in xkeys + [ykey]} | {"city": r["city"], "murder_year": r["murder_year"]})
    return out

ykey = "log_murder_rate_per100k"
xkeys = [c for c in COMPONENTS if sum(1 for r in panel if r["codes_per_capita"].get(c, 0) != 0) >= 8]
print("components kept (>=8 nonzero obs):", xkeys)

# build design rows: missing component -> 0.0, but honest n-report per component
design = []
for r in panel:
    row = {"city": r["city"], "murder_year": r["murder_year"],
           ykey: r[ykey],
           "care_sum": sum(r["codes_per_capita"].values())}
    for c in xkeys:
        row[c] = r["codes_per_capita"].get(c, 0.0)
    design.append(row)

dm = demean_panel(design, xkeys + ["care_sum"], ykey)
# single-sum fit
res_sum = ols(dm, ["care_sum"], ykey)
# joint fit
res_joint = ols(dm, xkeys, ykey)

print()
print("=" * 88)
print(f"WITHIN-CITY DEMEANED REGRESSION:  panel = {len(panel)} obs, {len(set(r['city'] for r in panel))} cities")
print("=" * 88)
print(f"components regression: n={res_joint[2]}, joint R2(demeaned)={res_joint[1]:.3f}")
print(f"care-sum regression:   n={res_sum[2]},   R2(demeaned)={res_sum[1]:.3f}")
print()

# ---- THE BETA TABLE (the mix-ranking), sorted by |beta| ----
# betas are per-$100/resident of care spend (display scale; level is $/resident)
beta_table = []
for i, c in enumerate(xkeys):
    bb = res_joint[0][i]
    beta_table.append({"component": c, "label": LABEL[c],
                       "beta_per_100_resident": round(bb * 100, 4),
                       "beta_raw_per_dollar_resident": round(bb, 8),
                       "direction": "negative" if bb < 0 else "positive",
                       "n_nonzero": sum(1 for r in design if r[c] != 0),
                       "n_panel": len(design)})
beta_table.sort(key=lambda d: -abs(d["beta_per_100_resident"]))
print(f"{'component':10s} {'label':22s} {'beta/$100-res':>13s} {'dir':>9s} {'n_nz':>5s} {'n':>4s}")
for d in beta_table:
    print(f'{d["component"]:10s} {d["label"]:22s} {d["beta_per_100_resident"]:13.4f} {d["direction"]:>9s} {d["n_nonzero"]:5d} {d["n_panel"]:4d}')
print()
print(f"component-sum-check: sum of component betas = {sum(d['beta_raw_per_dollar_resident']*100 for d in beta_table):+.4f}/$100 vs single care-sum beta = {res_sum[0][0]*100:+.4f}/$100")
print()

# ---------------------------------------------------------------- 6. PAIR-WISE INTERACTION SCAN
print("=" * 88)
print("PAIR-WISE INTERACTION SCAN (within-city demeaned, |r| sorted)")
print("=" * 88)
def corr(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((ai - ma) * (bi - mb) for ai, bi in zip(a, b))
    da = sum((ai - ma) ** 2 for ai in a) ** .5
    db = sum((bi - mb) ** 2 for bi in b) ** .5
    return num / (da * db) if da * db > 1e-12 else 0.0

pair_table = []
for i in range(len(xkeys)):
    for j in range(i + 1, len(xkeys)):
        ca, cb = xkeys[i], xkeys[j]
        # interaction = product of the two demeaned component-per-capitas
        inter = [r[ca] * r[cb] for r in dm]
        yv = [r[ykey] for r in dm]
        pair_r = corr(inter, yv)
        # n-report = obs where BOTH components nonzero in level (before demeaning)
        nb = sum(1 for r in design if r[ca] != 0 and r[cb] != 0)
        pair_table.append({"pair": f"{LABEL[ca]} x {LABEL[cb]}", "codes": f"{ca} x {cb}",
                           "interaction_r": round(pair_r, 4), "n_both_nonzero": nb,
                           "direction": ("synergy-class" if pair_r < 0 else "substitution-class")})
pair_table.sort(key=lambda d: -abs(d["interaction_r"]))
for p in pair_table:
    print(f'  {p["pair"]:47s} r={p["interaction_r"]:+.3f}  n={p["n_both_nonzero"]:2d}  {p["direction"]}')

# ---------------------------------------------------------------- 7. BIN-SLICE TEST + SCATTER HTML
print()
print("=" * 88)
print("BIN-SLICE TEST (care-sum per-capita quintiles; the level panel, within-city demeaned)")
print("=" * 88)
vals = sorted(r["care_sum_demeaned"] if "care_sum_demeaned" in r else r["care_sum"] for r in dm)
# use the demeaned care_sum for the bin test (per the founder's "demeaned" convention)
pairs = sorted(dm, key=lambda r: r["care_sum"])
n = len(pairs)
q = 5
bins = []
edges = [pairs[min(int(n * i / q), n - 1)]["care_sum"] for i in range(0, 6)]
edges[0] = -1e18
edges[-1] = 1e18
for i in range(5):
    grp = [r for r in pairs if edges[i] <= r["care_sum"] < edges[i + 1]]
    mv = sum(r[ykey] for r in grp) / len(grp)
    cv = sum(r["care_sum"] for r in grp) / len(grp)
    bins.append({"quintile": i + 1, "n": len(grp),
                 "mean_care_sum_demeaned": round(cv, 4),
                 "mean_log_murder_rate": round(mv, 4)})
    print(f'  Q{i+1}: n={len(grp):2d} care_sum_dm={cv:+.4f}  mean log-rate={mv:+.4f}')
print()

# monotonicity diagnostic: per-city murder delta between high-care and low-care within-city obs
print("per-city within-city deltas (min->max care_sum obs):")
for city in sorted(set(r["city"] for r in design)):
    rr = [r for r in dm if r["city"] == city]
    if len(rr) < 2: continue
    rr = sorted(rr, key=lambda r: r["care_sum"])
    lo, hi = rr[0], rr[-1]
    print(f'  {city:15s} care_dm {lo["care_sum"]:+.4f}->{hi["care_sum"]:+.4f}   log-rate {lo[ykey]:+.4f}->{hi[ykey]:+.4f}  delta={hi[ykey]-lo[ykey]:+.4f}')

# ---------------------------------------------------------------- 8. HTML SCATTER
def esc(x): return f"{x:.6g}"
# THE STEPPING-STONE VISUAL: within-city demeaned points (same convention as the
# regression) — x = demeaned care-sum per-capita, y = demeaned log murder rate.
pts = []
for r in dm:
    pts.append((r["care_sum"], r[ykey], r["city"]))
cities_sorted = sorted(set(p[2] for p in pts))
palette = ["#e05a5a", "#5ab4e0", "#5ae08f", "#e0c05a", "#a05ae0", "#e08f5a",
           "#5ae0d8", "#e05ab4", "#8fe05a", "#5a78e0", "#e0e05a", "#5aa0e0",
           "#e0aa5a", "#5ae05a", "#d85ae0", "#5ad8e0", "#aae05a", "#e05ad8",
           "#5ae0aa", "#e0d85a", "#785ae0", "#5ae05a", "#e05a78", "#d8e0ff",
           "#ffd8e0", "#e0ffd8", "#d8ffe0", "#b4fffd", "#fdb4ff", "#fffeb4"]
def colr(c): return palette[cities_sorted.index(c) % len(palette)]
series_blocks = []
for city in cities_sorted:
    sub = [(p[0], p[1]) for p in pts if p[2] == city]
    s = ",".join(f"[{esc(x)},{esc(y)}]" for x, y in sub)
    series_blocks.append(
        f'{{ name: "{city}", color: "{colr(city)}", data: [{s}], type: "scatter", '
        f'marker: {{ radius: 5, symbol: "circle" }}, tooltip: {{ pointFormat: "{city}: care=${{point.x}}, log-rate=${{point.y}}" }} }}'
    )
# binned overlay: 5 equal-count bins of care_sum
pts_by_x = sorted(pts, key=lambda p: p[0])
bn = len(pts_by_x)
bin_means = []
for i in range(5):
    grp = pts_by_x[int(bn * i / 5): int(bn * (i + 1) / 5)]
    bx = sum(p[0] for p in grp) / len(grp)
    by = sum(p[1] for p in grp) / len(grp)
    bin_means.append((bx, by, len(grp)))
overlay = ",".join(f'{{ x: {esc(bx)}, y: {esc(by)}, marker: {{ radius: 9, symbol: "diamond", \
lineColor: "#fff", lineWidth: 2, fillColor: "#ffffff" }} }}' for bx, by, _ in bin_means)
html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Care Components Scatter (within-city demeaned)</title>
<script src="https://code.highcharts.com/highcharts.js"></script>
<style>body{{background:#0d1117;color:#e6edf3;font-family:monospace;margin:0;padding:16px}}
#chart{{width:100%;max-width:1100px;height:640px}}
.note{{color:#8b949e;max-width:1100px}}
h2{{color:#58a6ff}} a{{color:#58a6ff}}
</style></head><body>
<h2>Care-component decomposition: care-per-capita (x) vs log murder-rate (y), within-city demeaned</h2>
<div class="note">
<!-- REPRODUCIBILITY HEADER
method: within-city demeanted panel regression + quintile-binned means overlay;
panel: build/care_components_v1.jsonl (care_components_decomposition_v1.py output);
care grain: Census of Governments function codes E61/F61 parks, E52/F52 libraries,
E32/F32 health, E36 hospitals, E74/75/77/79 welfare, E68 welfare-cash, E50 housing
(cities' own printed structure; no forced splits);
murders: build/murders_all_v1.json (validated 60/60 vs build/crime_wide_b.jsonl on 2011-2014);
pops: build/populations_wide_v1.jsonl (PEP July-1, = sub-est2019_all.csv SUMLEV162);
window: 2012-care -> murders 2012+2013; 2014-care -> murders 2014;
partial CDE years excluded (fraud-guard; Raleigh-2014 fell to the 2013 side);
log: log(rate_per_100k + 5e-6) with 0.5-count continuity on the per-100k scale.
-->
Panel n = {len(pts)} obs across {len(cities_sorted)} cities. Each point = one
(city, care-vintage, murder-year) observation. Colored by city; white diamonds =
quintile-bin means of the (demeaned) care-per-capita vs murder-rate.
</div>
<div id="chart"></div>
<script>
Highcharts.chart('chart', {{
  chart: {{ backgroundColor: '#0d1117', type: 'scatter', zoomType: 'xy' }},
  title: {{ text: 'Care-per-capita (all components, $/resident) vs log murder rate — within-city demeaned', style: {{ color: '#e6edf3' }} }},
  xAxis: {{ title: {{ text: 'care-per-capita demeaned ($/resident)', style: {{ color: '#8b949e' }} }}, gridLineColor: '#30363d' }},
  yAxis: {{ title: {{ text: 'log murder rate per 100k (demeaned)', style: {{ color: '#8b949e' }} }}, gridLineColor: '#30363d' }},
  legend: {{ itemStyle: {{ color: '#8b949e', fontSize: '10px' }} }},
  series: [{",  ".join(series_blocks)},
    {{ name: "quintile-bin means", type: "scatter", data: [{overlay}],
       marker: {{ radius: 9 }}, showInLegend: false,
       tooltip: {{ pointFormat: "bin mean: ${{point.x}} / ${{point.y}}" }} }}],
  tooltip: {{ backgroundColor: '#161b22', style: {{ color: '#e6edf3' }} }}
}});
</script>
</body></html>"""
open(OUT_SCATTER, "w", encoding="utf-8").write(html)
print("wrote", OUT_SCATTER)

# ---------------------------------------------------------------- 9. OUTPUT JSONL
with open(OUT_JSONL, "w", encoding="utf-8") as f:
    for r in panel:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("wrote", OUT_JSONL, f"({len(panel)} rows)")
