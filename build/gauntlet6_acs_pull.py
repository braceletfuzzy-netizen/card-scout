#!/usr/bin/env python3
# gauntlet6_acs_pull.py — Louisville ACS 1-yr inputs via the banked table-based-SF .dat route
# (www2.census.gov/programs-surveys/acs/summary_file/2023/table-based-SF/data/1YRData/).
# Geo row: Louisville/Jefferson County metro government (balance), GEO_ID suffix 21180 (place 48066
# labeled Louisville Metro in PEP). Also 2024 vintage where published.
import urllib.request, socket, io, csv
socket.setdefaulttimeout(120)
BASE = "https://www2.census.gov/programs-surveys/acs/summary_file/{yr}/table-based-SF/data/1YRData/"
TABLES = ["b17001", "b08301", "b15003", "b25070", "b25077", "b19013"]

def pull(yr, tab):
    url = BASE.format(yr=yr) + f"acsdt1y{yr}-{tab}.dat"
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()
    except Exception as e:
        print("FAIL", url[:110], str(e)[:80])
        return None
    txt = b.decode("utf-8", "replace").splitlines()
    hdr = txt[0].split("|")
    idx = {h: i for i, h in enumerate(hdr)}
    want = [l for l in txt if l.startswith("1600000US2148066") or l.startswith("1600000US21180")]
    return {"header_first": hdr[:4], "row_hits": want[:3], "n_lines": len(txt)}

res = {}
for yr in (2023, 2024):
    for t in TABLES:
        r = pull(yr, t)
        res[f"{yr}_{t}"] = r
        if r:
            print(yr, t, "lines", r["n_lines"], "hits", len(r["row_hits"]))
            for h in r["row_hits"]:
                print("   ", h[:150])
import json
json.dump(res, open("acs_lou_probe_v1.json", "w"), indent=1)
