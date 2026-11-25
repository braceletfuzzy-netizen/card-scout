#!/usr/bin/env python3
# gauntlet6_predict_v3.py — Louisville inputs, all keyless verified routes:
#  - pops: CDE per-year (done: 2013-2025)
#  - ACS 1-yr: the BANKED keyless route (www2.census.gov TableEngine JSON pulls, the same class the
#    panel builder used for _joint_panel_raw). Try the tablebrowser route for B17001 (poverty),
#    B08301 (commute), B25070 (rent burden), B15003 (education), S1901 via acs.
#  - Louisville Metro care-$ (budget): Louisville opens budget PDFs; verify quick reachability only,
#    mark honest-null if not routable in this pass.
import json, urllib.request, socket, time, re
socket.setdefaulttimeout(90)
out = {}

def fetch(url, tries=2, binary=False):
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}))
            b = r.read()
            return b if binary else b.decode("utf-8", "replace")
        except Exception as e:
            if i == tries-1:
                print("FAIL", url[:100], str(e)[:100]); return None
            time.sleep(2)

# The banked ACS route: check how the panel builder pulled TableEngine data
EOF = None
try:
    head = open("C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/maslow_joint_panel_build_v1.py").read()
    m = re.findall(r"https://[^\s\"']+census\.gov[^\s\"']*", head)
    print("banked census routes in panel builder:", m[:6])
    out["banked_census_routes"] = m[:6]
except Exception as e:
    print("read err", e)
# check any _joint_panel_raw fetch script
import glob
for f in glob.glob("C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/_joint_panel_raw/*"):
    print(" raw dir:", f)
