#!/usr/bin/env python3
# gauntlet6_predict.py — THE PRE-REGISTERED CIVIC CALL: prediction step.
# Louisville KY (LMPD, KY0568000) selected — better keyless routes verified: FBI CDE summarizer
# returns FULL monthly actuals (Jacksonville hub API gates 401; Jax CDE 2024-2025 also pulled as cross-check).
#
# Inputs -> prediction, banked FE betas, honest-moment handling labeled at every step.
import json, urllib.request, socket, time
import numpy as np
socket.setdefaulttimeout(60)

BUILD = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
def getjson(url, tries=3):
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(url).read())
        except Exception as e:
            if i == tries-1: print("FAIL", url[:90], str(e)[:120]); return None
            time.sleep(3)

pull = json.load(open(f"{BUILD}/civic_call_inputs_v1.json", encoding="utf-8"))
larc = pull["annual"]["Louisville (LMPD)"]
annual = {int(y): v["annual_total"] for y, v in larc.items()}

# ---- Louisville population denominators (Census PEP city class, vintage-2023/2024/2025) ----
# banked pop-bank route: populations_wide_v1 SUMLEV162 PEP. Louisville (Louisa/County balance)?
# Louisville Metro = consolidated gov; PEP publishes 'Louisville/Jefferson County metro government
# (balance)'. Use the CDE's own monthly population vector if it carries a Louisville-level pop.
j25 = getjson("https://cde.ucr.cjis.gov/LATEST/summarized/agency/KY0568000/HOM?from=01-2025&to=12-2025")
pops = (j25 or {}).get("populations", {}).get("population", {})
print("populations series:", list(pops))
denom = None
for k, v in pops.items():
    if k != "United States":
        print(k, {kk: v[kk] for kk in list(v)[:3]})
        denom = k
if denom:
    pv = pops[denom]
    lou_pop = {y: pv.get(f"07-{y}") or pv.get(f"01-{y}") for y in (2023, 2024, 2025) if pv.get(f"07-{y}") or pv.get(f"01-{y}")}
else:
    lou_pop = {}
print("Louisville pops from CDE:", lou_pop)

rates = {}
for y, c in annual.items():
    p = lou_pop.get(y)
    rates[y] = {"count": c, "pop": p, "rate_per_100k": round(c / p * 1e5, 2) if p else None}

# ---- ACS 1-yr keyless route (B08301 commute / B17001 poverty) for Louisville metro ( Jefferson KY ) ----
# the banked panel builder used www2.census.gov TableEngine/tablebrowser JSON by table ID; try the
# dataweb data.census.gov v3 keyless API? The proven keyless route in this project: www2.census.gov
# ACS detailed-table HTML/JSON. Try API.data.gov keyless ACS via https://api.census.gov/data/2023/acs/acs1?get=NAME,B17001_001E,B17001_002E&for=place:*&in=state:21
try:
    acs_pov = getjson("https://api.census.gov/data/2023/acs/acs1?get=NAME,B17001_001E,B17001_002E&for=place:45818&in=state:21")
except Exception as e:
    acs_pov = {"err": str(e)[:120]}
# Louisville metro government (balance) place code = 48066? verify via the response we got; try 45818 too
try:
    acs_pov2 = getjson("https://api.census.gov/data/2023/acs/acs1?get=NAME,B17001_001E,B17001_002E&for=place:48066&in=state:21")
except Exception as e:
    acs_pov2 = {"err": str(e)[:120]}
print("ACS poverty place:45818:", acs_pov)
print("ACS poverty place:48066:", acs_pov2)

out = {"annual_counts_cde": annual, "denominators": lou_pop, "rates": rates,
       "acs_poverty_2023_place_45818": acs_pov, "acs_poverty_2023_place_48066": acs_pov2}
with open(f"{BUILD}/civic_call_lou_inputs_v1.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print(json.dumps(rates, indent=1))
