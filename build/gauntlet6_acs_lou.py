#!/usr/bin/env python3
# gauntlet6_acs_lou.py — Louisville ACS 1-yr inputs via the SAME www2.census.gov route the panel
# uses (TableEngine .dat summary-file style). The panel's .dat files are TableEngine "get table"
# exports — the URL pattern for ACS 1-yr summary files:
#   https://www2.census.gov/programs-surveys/acs/summary_file/2023/table-data/…  (large zips)
# The proven light route used in this workspace is the TableEngine JSON API:
#   https://api.census.gov/...  requires key now
#   https://www2.census.gov/programs-surveys/acs/summary_file/2023/sequence-based/  zips ~10 MB per seq
# Cheapest keyless: TableBrowser 'TableEngine' JSON: https://www2.census.gov/…/tableengine/  — VERIFY:
import json, urllib.request, socket, time
socket.setdefaulttimeout(90)
def fetch(url, tries=2):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})).read()
        except Exception as e:
            if i == tries-1: print("FAIL", url[:100], str(e)[:100]); return None
            time.sleep(2)

# candidate routes for ACS 1yr 2023, table B17001 (poverty), place Louisville/Jefferson County metro govt (balance) FIPS 21-48066
routes = [
  # table shell json
  "https://www2.census.gov/programs-surveys/acs/summary_file/2023/table-based/B17001Albanian.json",
  # data profile tables via the ACS 'data profiles' API-free files:
  "https://www2.census.gov/programs-surveys/acs/data_profiles/2023/",
  # Socrata? no. The 'acs_summary_file' light route:
  "https://www2.census.gov/programs-surveys/acs/summary_file/2023/documentation/user_tools/",
]
for u in routes:
    b = fetch(u)
    print("==", u, "->", (len(b) if b else "FAIL"))
    if b and len(b) < 2000:
        print(b[:400])
