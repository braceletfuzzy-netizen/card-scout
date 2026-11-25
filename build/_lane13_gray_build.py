"""Build gray_safety city-year panel: 311/service-request volume x murder-rate arcs, within-city demeaned."""
import json, collections, statistics, math

B = "C:/Users/J"
IN = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"

cities = ["Memphis", "Cincinnati", "Detroit", "St. Louis", "NYC", "Houston"]

# ---- load gray (311) by-year counts -------------------------------------------------
gray = {}
m = json.load(open(f"{B}/_lane13_gray_memphis_311_raw.json"))
gray["Memphis"] = {int(k): v for k, v in m["year_counts"].items()}
d = json.load(open(f"{B}/_lane13_gray_detroit_raw.json"))
gray["Detroit"] = {int(k): v for k, v in d["by_year"].items()}
c = json.load(open(f"{B}/_lane13_gray_cincinnati_raw.json"))
gray["Cincinnati"] = {int(k): v for k, v in c["by_year"].items()}
h = json.load(open(f"{B}/_lane13_gray_houston_raw.json"))
hy = {int(k): v for k, v in h["archives_by_year"].items()}
hy[int(next(k for k in h["recent_by_year"]))] = None  # 2026 recent only; archives end 2025
hy = {int(k): v for k, v in h["archives_by_year"].items()}
hy[2026] = h["recent_by_year"]["2026"]  # different system (recent SR) — flag
gray["Houston"] = hy
s = json.load(open(f"{B}/_lane13_gray_stlouis_raw.json"))
gray["St. Louis"] = {int(k): v for k, v in s["by_year"].items() if k != "2015"}  # 2015 file empty — honest missing
n = json.load(open(f"{B}/_lane13_gray_nyc_year_counts.json"))
ny = {int(k): v for k, v in n["2010_2019"].items()}
ny.update({int(k): v for k, v in n["2020_present"].items()})
gray["NYC"] = ny

# ---- load murder counts + population ------------------------------------------------
mur = json.load(open(f"{IN}/murders_all_v1.json"))
Alias = {"New York": "NYC"}
mur = {f"{Alias.get(k.split('|')[0], k.split('|')[0])}|{k.split('|')[1]}": v for k, v in mur.items()}

pop = {}
def addpop(city, year, population, src):
    if city is None or population in (None, ""):
        return
    city = Alias.get(city, city)
    try:
        year = int(year); p = float(population)
    except (TypeError, ValueError):
        return
    if year not in pop or src == "census-decennial":
        pop[(city, year)] = (p, src)

for line in open(f"{IN}/population_series_v1.jsonl", encoding="utf-8"):
    if line.strip():
        r = json.loads(line); addpop(r.get("city"), r.get("year"), r.get("population"), r.get("anchor_or_estimate"))
for line in open(f"{IN}/populations_cities_v2.jsonl", encoding="utf-8"):
    if line.strip():
        r = json.loads(line); addpop(r.get("city"), r.get("year"), r.get("population"), "populations_cities_v2")
for line in open(f"{IN}/populations_wide_v1.jsonl", encoding="utf-8"):
    if line.strip():
        r = json.loads(line); addpop(r.get("city"), r.get("year"), r.get("population"), "populations_wide_v1")
phase2 = json.load(open(f"{B}/phase2_pop_table.json"))
for r in phase2:
    addpop(r.get("city"), r.get("year"), r.get("population"), r.get("population_source"))

# ---- per-1k rates -------------------------------------------------------------------
rows = []
for city in cities:
    for yr, calls in sorted(gray.get(city, {}).items()):
        if calls is None:
            continue
        p = pop.get((city, yr))
        murders = mur.get(f"{city}|{yr}")
        calls_per1k = round(calls * 1000 / p[0], 2) if p else None
        rows.append({"city": city, "year": yr, "calls": calls, "population": p[0] if p else None,
                     "calls_per_1k": calls_per1k,
                     "calls_per1k_t+1": None, "calls_per1k_t+2": None,
                     "murders": murders, "murder_rate_t0": None, "murder_rate_t+1": None, "murder_rate_t+2": None,
                     "population_class": p[1] if p else None})

# murder-rate arcs
mr = {}
for r in rows:
    if r["murders"] is not None and r["population"]:
        mr[(r["city"], r["year"])] = r["murders"] * 100000 / r["population"]
for r in rows:
    k0 = (r["city"], r["year"])
    if k0 in mr:
        r["murder_rate_t0"] = round(mr[k0], 2)
    for lag, key in [(1, "murder_rate_t+1"), (2, "murder_rate_t+2")]:
        if k0 in mr and (r["city"], r["year"] + lag) in mr:
            r[key] = round(mr[(r["city"], r["year"] + lag)], 2)

# call-rate arcs
cp = {(r["city"], r["year"]): r["calls_per_1k"] for r in rows if r["calls_per_1k"] is not None}
for r in rows:
    for lag, key in [(1, "calls_per1k_t+1"), (2, "calls_per1k_t+2")]:
        v = cp.get((r["city"], r["year"] + lag))
        if v is not None:
            r[key] = v

json.dump(rows, open(f"{B}/gray_safety_lane_panel_v1.json", "w"), indent=1)
print("rows:", len(rows))
for city in cities:
    ys = sorted(r["year"] for r in rows if r["city"] == city)
    full = [r for r in rows if r["city"] == city and r["murder_rate_t0"] is not None]
    print(city, "years", ys[0] if ys else None, "-", ys[-1] if ys else None, len(ys), "| murder-matched:", len(full))
