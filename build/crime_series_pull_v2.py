"""CRIME-LANE WAVE-1 v2: FBI CDE pull (keyless) -> crime_series_wave1.jsonl.
Years: full-year CDE (1980-2025) + 2026 YTD through latest available month."""
import urllib.request, urllib.error, json, time, sys

UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
BASE = "https://cde.ucr.cjis.gov/LATEST"
OUT = r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/crime_series_wave1.jsonl"

def cde(url, timeout=150, attempts=3):
    last = None
    for _ in range(attempts):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
            return json.loads(r.read().decode()), None
        except urllib.error.HTTPError as e:
            try: body = e.read().decode()[:250]
            except Exception: body = ''
            return None, f'{e.code} {body}'
        except Exception as e:
            last = str(e); time.sleep(1.5)
    return None, last

def agency_homicide_series(ori, ym_from, ym_to):
    data, err = cde(f"{BASE}/summarized/agency/{ori}/HOM?from={ym_from}&to={ym_to}&type=counts")
    if not data:
        return None, err
    act = data.get("offenses", {}).get("actuals", {})
    rates = data.get("offenses", {}).get("rates", {})
    pops = data.get("populations", {}).get("participated_population", {})
    series = None; label = None
    for k, months in act.items():
        if "Clearances" in k: continue
        series = months; label = k; break
    if series is None:
        return None, "no offense series"
    total = sum(v for v in series.values() if isinstance(v, (int, float)))
    present = sum(1 for v in series.values() if isinstance(v, (int, float)))
    # monthly city rate for the agency, if present
    arate = rates.get(label, {})
    # monthly city participated population (sum across months approximates nothing; take per-month dict)
    return {"label": label, "total": total, "months_present": present,
            "monthly": series, "monthly_rate": arate,
            "raw_url": f"{BASE}/summarized/agency/{ori}/HOM?from={ym_from}&to={ym_to}&type=counts"}, None

def city_rate(ori, ym_from, ym_to):
    """population + violent-crime totals via LATEST/uof? No - use 'rates' from homicide call (has per-100k) for murder_rate; violent total needs other offense codes."""
    return None

CITIES = {
    "Boston":        ("MA0130100", "Boston Police Department"),
    "New York City": ("NY0303000", "New York City Police Department"),
    "New Orleans":   ("LANPD0000",  "New Orleans Police Department"),
    "St. Louis":     ("MOSPD0000",  "St. Louis Police Department"),
}

YEARS = {
    "Boston":        [1980, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
    "New York City": [1998, 1999, 2000, 2001, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
    "New Orleans":   [1980, 1990, 1994, 2004, 2005, 2006, 2007, 2009, 2011, 2017, 2019, 2022, 2023, 2024, 2025],
    "St. Louis":     [1998, 1999, 2000, 2001, 2010, 2011, 2012, 2013, 2014, 2015, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
}

def write_row(row):
    with open(OUT, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def pull_city(city):
    ori, dept = CITIES[city]
    results = {}
    for y in YEARS[city]:
        r, e = agency_homicide_series(ori, f"01-{y}", f"12-{y}")
        results[y] = r
        if r:
            print(f"{city} {y}: murders={r['total']:.0f} months={r['months_present']}/12", flush=True)
        else:
            print(f"{city} {y}: N/A ({e})", flush=True)
        time.sleep(0.08)
    # 2026 YTD
    r26, e26 = agency_homicide_series(ori, "01-2026", "09-2026")
    if r26:
        print(f"{city} 2026YTD: murders(Jan-Sep?)={r26['total']:.0f} months={r26['months_present']}", flush=True)
    else:
        print(f"{city} 2026YTD: N/A ({e26})", flush=True)

    for y in YEARS[city]:
        r = results.get(y)
        if not r:
            write_row({"city": city, "year": y, "murders": None, "violent_crime_total": None, "population": None,
                       "murder_rate_per_100k": None,
                       "source_refs": ["FBI CDE summarizer (cde.ucr.cjis.gov/LATEST/summarized/agency/.../HOM) returned no data"],
                       "data_quality": "official",
                       "notes": f"CDE summarizer has no monthly homicide counts for {dept} in {y} (likely no pre-1985 UCR monthly entry or agency not reporting).",
                       "honest_gaps": ["murders unknown", "violent_crime_total unknown", "population unknown"]})
            continue
        monthly_nums = [v for v in r["monthly"].values() if isinstance(v, (int, float))]
        full_year = r["months_present"] == 12
        # annual murder rate = sum(monthly counts)/avg participated pop *100k; CDE monthly rate uses monthly agency pop; approximate annual rate from counts/population when possible
        write_row({"city": city, "year": y, "murders": int(r["total"]), "violent_crime_total": None,
                   "population": None, "murder_rate_per_100k": None,
                   "source_refs": [r["raw_url"]],
                   "data_quality": "official",
                   "notes": f"Sum of {r['months_present']} monthly UCR summary-reporting 'Offenses' counts for {dept} via FBI CDE (full_year={full_year}). Violent-crime index & population not in this pull.",
                   "honest_gaps": [] if full_year else ["partial-year: only " + str(r['months_present']) + " months in CDE for " + str(y)]})
    if r26:
        r26nums = [v for v in r26["monthly"].values() if isinstance(v, (int, float))]
        write_row({"city": city, "year": 2026, "murders": int(r26["total"]), "violent_crime_total": None,
                   "population": None, "murder_rate_per_100k": None,
                   "source_refs": ["CDE summarizer Jan-Sept-2026 partial-year"],
                   "data_quality": "official",
                   "notes": f"2026 partial-year (Jan-Sep) UCR summary 'Offenses' count for {dept}: {int(r26['total'])} through {r26['months_present']} months of data. Not a full-year figure.",
                   "honest_gaps": ["partial-year Jan-Sep only", "no full-year 2026 exists yet"]})
    else:
        write_row({"city": city, "year": 2026, "murders": None, "violent_crime_total": None, "population": None, "murder_rate_per_100k": None,
                   "source_refs": ["CDE summarizer (no 2026 data yet)"], "data_quality": "official",
                   "notes": "CDE has no 2026 homicide counts (year not yet closed/released).",
                   "honest_gaps": ["murders unavailable until FBI release"]})

if __name__ == "__main__":
    which = sys.argv[1:] or ["Boston"]
    for c in which:
        pull_city(c)
