#!/usr/bin/env python3
# gauntlet6_lou_inputs_final.py — Louisville ACS 1-yr 2023/2024 inputs, geo 1600000US2148006
# (Census place 48006 = Louisville Metro consolidated govt, pop 623k — matches the CDE jurisdiction
# pop 691630 closely; the CDE pop is the AGENCY jurisdiction, labeled separately).
import urllib.request, socket, json, time
socket.setdefaulttimeout(120)
BASE = "https://www2.census.gov/programs-surveys/acs/summary_file/{yr}/table-based-SF/data/1YRData/"
GEO = "1600000US2148006"
TABLES = {
 "b17001":  ["B17001_E001", "B17001_E002"],                       # poverty total / in-poverty
 "b08301":  ["B08301_E001", "B08301_E003", "B08301_E010"],        # commuters total / drove / transit
 "b15003":  ["B15003_E001", "B15003_E022", "B15003_E023", "B15003_E025"],  # edu 25+ / bachelor / masters / doctorate
 "b25070": ["B25070_E001", "B25070_E007", "B25070_E010"],          # rent burden
 "b19013": ["B19013_E001"],                                        # median HH income
 "b01001": ["B01001_E001"],                                        # pop
}
OUT = {}
for yr in (2023, 2024):
    for tab, fields in TABLES.items():
        url = BASE.format(yr=yr) + f"acsdt1y{yr}-{tab}.dat"
        try:
            txt = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})).read().decode("utf-8", "replace").splitlines()
        except Exception as e:
            print("FAIL", yr, tab, str(e)[:80]); continue
        hdr = txt[0].split("|"); idx = {h: i for i, h in enumerate(hdr)}
        row = next((l for l in txt if l.split("|")[0] == GEO), None)
        if not row: continue
        v = row.split("|")
        OUT[f"{yr}_{tab}"] = {f: int(v[idx[f]]) for f in fields if f in idx}
        time.sleep(0.15)

# derived
d = {}
for yr in (2023, 2024):
    try:
        pov = OUT[f"{yr}_b17001"]; d[f"poverty_rate_{yr}"] = round(pov["B17001_E002"]/pov["B17001_E001"]*100, 2)
        cm = OUT[f"{yr}_b08301"];  d[f"transit_share_{yr}"] = round(cm["B08301_E010"]/cm["B08301_E001"]*100, 2)
        ed = OUT[f"{yr}_b15003"];  d[f"bachelors_plus_pct_{yr}"] = round((ed["B15003_E022"]+ed["B15003_E023"]+ed["B15003_E025"])/ed["B15003_E001"]*100, 2)
        rb = OUT[f"{yr}_b25070"];  d[f"rent_burden50_share_{yr}"] = round((rb["B25070_E007"]+rb["B25070_E010"])/rb["B25070_E001"]*100, 2)
        d[f"median_hh_income_{yr}"] = OUT[f"{yr}_b19013"]["B19013_E001"]
        d[f"acs_pop_{yr}"] = OUT[f"{yr}_b01001"]["B01001_E001"]
    except KeyError as e:
        d[f"{yr}_missing"] = str(e)
print(json.dumps(d, indent=1))
json.dump({"geo": GEO, "geo_class": "Census place 48006 Louisville Metro consolidated government",
           "acs_1yr_raw": OUT, "derived": d,
           "route": "www2.census.gov/programs-surveys/acs/summary_file/{yr}/table-based-SF/data/1YRData/acsdt1y{yr}-{tab}.dat (keyless, the banked panel route)",
           "pulled": "2026-11-25"},
          open("civic_call_lou_acs_v1.json", "w", encoding="utf-8"), indent=1)
