#!/usr/bin/env python3
# pull_lou_v3.py — THE LOUISVILLE FRESH PULL, done right:
#  1) resolve the Lousville agency ORI from the CDE agency directory ( Kentucky state list )
#  2) pull monthly HOM actuals per year 2011-2025 (same route/shape as the banked wide-lane cache),
#  3) build the murder ARC (annual counts + own-population denominator from CDE? no — counts first),
#  4) same for Jacksonville FL0160000 (already cached 2011-2025 banked; pull only 2024/2025 fresh).
# Also pull Louisville-Jefferson County ACS 1-yr inputs via the keyless www2.census.gov route used
# by the panel builder (B17001 poverty / B08301 commute / B25070-class) — check the _joint_panel_raw route.
import json, urllib.request, socket, time
socket.setdefaulttimeout(60)

def getjson(url, tries=3):
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(url).read())
        except Exception as e:
            if i == tries-1:
                print("FAIL", url[:90], str(e)[:120]); return None
            time.sleep(3)

OUT = {}
# --- 1) Kentucky agency directory -> Louisville ORI ---
ky = getjson("https://cde.ucr.cjis.gov/LATEST/agency/byStateAbbr/KY")
if ky:
    OUT["ky_agencies_n"] = len(ky) if isinstance(ky, list) else "dict:" + str(list(ky)[:5])
    hits = []
    items = ky if isinstance(ky, list) else ky.get("agencies") or ky.get("data") or []
    for a in (items if isinstance(items, list) else []):
        s = json.dumps(a).lower()
        if "louisville" in s or "jefferson" in s:
            hits.append({k: a.get(k) for k in ("ori", "agencyName", "agency_name", "name", "oriName", "county") if k in a})
    OUT["louisville_ori_hits"] = hits[:12]
print(json.dumps({k: v for k, v in OUT.items()}, indent=1)[:1800])
json.dump(OUT, open("_pull_lou_dir.json", "w"), indent=1)
