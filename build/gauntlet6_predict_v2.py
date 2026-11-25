#!/usr/bin/env python3
# gauntlet6_predict_v2.py — complete Louisville inputs: per-year CDE pops (07-month of each year),
# then ACS 1-yr via the api.census.gov route with the correct Louisvile place code discovery,
# then the FE-3-arc prediction with honest moment handling (train-only betas + Louisville's own
# descriptive stats for centering, banked convention).
import json, urllib.request, socket, time
import numpy as np
socket.setdefaulttimeout(60)
BUILD = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"

def getjson(url, tries=3):
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(url).read())
        except Exception as e:
            if i == tries-1: print("FAIL", url[:100], str(e)[:100]); return None
            time.sleep(3)

# 1) per-year pops from CDE (agency jurisdiction pop, monthly vectors)
lou_pop = {}
for y in range(2013, 2026):
    d = getjson(f"https://cde.ucr.cjis.gov/LATEST/summarized/agency/KY0568000/HOM?from=01-{y}&to=12-{y}")
    if not d: continue
    pv = (d.get("populations", {}).get("population", {}) or {}).get("Louisville Metro Police Department", {})
    p = pv.get(f"07-{y}") or pv.get(f"01-{y}")
    if p: lou_pop[y] = p
    time.sleep(0.2)
print("CDE pops:", lou_pop)

# 2) poverty + commute via api.census.gov (https keyless) — Louisville/Jefferson County metro govt (balance)
# place code for Louisville Metro government: 48066 is 'Louisville/Jefferson County...' balance? discover:
disc = getjson("https://api.census.gov/data/2023/acs/acs1?get=NAME&for=place:*&in=state:21")
lou_places = [r for r in (disc or [])[1:] if "louisville" in r[0].lower()]
print("Louisville places:", lou_places)
place_code = lou_places[0][1] if lou_places else None
pov = comm = None
if place_code:
    pov = getjson(f"https://api.census.gov/data/2023/acs/acs1?get=NAME,B17001_001E,B17001_002E&for=place:{place_code}&in=state:21")
    comm = getjson(f"https://api.census.gov/data/2023/acs/acs1?get=NAME,B08301_001E,B08301_010E,B08301_003E&for=place:{place_code}&in=state:21")
    hh  = getjson(f"https://api.census.gov/data/2023/acs/acs1?get=NAME,B25070_001E,B25070_007E,B25070_010E&for=place:{place_code}&in=state:21")
    edu = getjson(f"https://api.census.gov/data/2023/acs/acs1?get=NAME,B15003_001E,B15003_022E,B15003_023E,B15003_025E&for=place:{place_code}&in=state:21")
    medhh = getjson(f"https://api.census.gov/data/2023/acs/acs1?get=NAME,B19013_001E&for=place:{place_code}&in=state:21")
print("poverty:", pov)
print("commute:", comm)
print("housing-burden(B25070):", hh)
print("edu(B15003):", edu)
print("medhhinc:", medhh)

json.dump({"cde_pops": lou_pop, "place_code": place_code,
           "acs_2023": {"poverty": pov, "commute": comm, "housing_burden": hh, "edu": edu, "medhhinc": medhh}},
          open(f"{BUILD}/civic_call_lou_inputs_v2.json", "w", encoding="utf-8"), indent=1)
