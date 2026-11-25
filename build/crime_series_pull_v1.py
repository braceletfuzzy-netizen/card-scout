"""CRIME-LANE WAVE-1: FBI CDE keyless summarizer pull for Boston/NYC/NO/StL -> crime_series_wave1.jsonl"""
import urllib.request, urllib.error, json, time, os, sys

UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
BASE = "https://cde.ucr.cjis.gov/LATEST"
OUT = r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/crime_series_wave1.jsonl"

def cde(url, timeout=120):
    for att in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
            return json.loads(r.read().decode()), None
        except urllib.error.HTTPError as e:
            try: body = e.read().decode()[:250]
            except Exception: body = ''
            return None, f'{e.code} {body}'
        except Exception as e:
            time.sleep(1.5)
            last = str(e)
    return None, last

def agency_rate(ori, year):
    """Return (annual_homicide_count, months_present, agency_label, monthly_rate_avg_denom-> None)"""
    data, err = cde(f"{BASE}/summarized/agency/{ori}/HOM?from=01-{year}&to=12-{year}&type=counts")
    if not data:
        data, err = cde(f"{BASE}/summarized/agency/{ori}/HOM?from=01-{year}&to=12-{year}&type=totals")
    if not data:
        return None, err
    off = data.get("offenses", {})
    act = off.get("actuals", {})
    series = None; label = None
    for k, months in act.items():
        if "Clearances" in k: continue
        series = months; label = k; break
    if series is None:
        return None, "no offense series"
    total = sum(v for v in series.values() if isinstance(v, (int, float)))
    present = sum(1 for v in series.values() if isinstance(v, (int, float)))
    return {"sum": total, "present": present, "label": label, "monthly": series, "raw_url": f"{BASE}/summarized/agency/{ori}/HOM?from=01-{year}&to=12-{year}&type=counts"}, None

def agency_year_month(ori, ym_from, ym_to, offense="HOM"):
    """monthly counts over arbitrary window (for partial-year pulls like 2026 YTD)"""
    data, err = cde(f"{BASE}/summarized/agency/{ori}/{offense}?from={ym_from}&to={ym_to}&type=counts")
    if not data:
        return None, err
    act = data.get("offenses", {}).get("actuals", {})
    series = None; label = None
    for k, months in act.items():
        if "Clearances" in k: continue
        series = months; label = k; break
    if series is None:
        return None, "no offense series"
    return {"label": label, "monthly": series, "sum": sum(v for v in series.values() if isinstance(v, (int, float)))}, None

CITIES = {
    "Boston":      ("MA0130100", "Boston Police Department"),
    "New York City":("NY0303000", "New York City Police Department"),
    "New Orleans": ("LANPD0000",  "New Orleans Police Department"),
    "St. Louis":   ("MOSPD0000",  "St. Louis Police Department"),
}

YEARS = {
    "Boston": [1980, 1983, 1990, 1991, 1993, 1994, 1995, 1999, 2001, 2019, 2020, 2021, 2022, 2025, 2026],
    "New York City": [1998, 1999, 2000, 2001, 2019, 2020, 2021, 2022, 2025, 2026],
    "New Orleans": [2004, 2005, 2006, 2007, 2009, 2011, 2017, 2019, 2022, 2025, 2026],
    "St. Louis": [1998, 1999, 2000, 2001, 2010, 2011, 2012, 2013, 2014, 2015, 2019, 2025, 2026],
}

def write_row(row):
    with open(OUT, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def main(city):
    ori, dept = CITIES[city]
    print(f"== {city} ({ori}) ==", flush=True)
    for y in YEARS[city]:
        if y == 2026:
            # 2026 is partial-year: full-year CDE figures don't exist yet for 2026; probe Jan-Sep 2026
            r, e = agency_year_month(ori, "01-2026", "09-2026")
            if r:
                print(f"{city} 2026 (Jan-Sep): sum={r['sum']} months_present={len([v for v in r['monthly'].values() if isinstance(v,(int,float))])} label={r['label']}", flush=True)
            else:
                print(f"{city} 2026 N/A: {e}", flush=True)
            continue
        r, e = agency_rate(ori, y)
        if r:
            print(f"{city} {y}: murders={r['sum']} months={r['present']}/12 label={r['label']}", flush=True)
        else:
            print(f"{city} {y}: N/A ({e})", flush=True)
        time.sleep(0.1)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "Boston")
