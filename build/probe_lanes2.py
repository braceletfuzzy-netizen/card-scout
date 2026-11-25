#!/usr/bin/env python3
# probe_lanes2.py — find the actual murder/homicide endpoints: Louisville (ArcGIS Hub on
# data.louisvilleky.gov) and Jacksonville (COJ hub). Also FBI CDE keyless route for both agencies.
import json, re, urllib.request, socket
socket.setdefaulttimeout(15)
UA = {"User-Agent": "Mozilla/5.0"}

def get(url, n=200000):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req) as r:
        return r.status, r.read(n).decode("utf-8", "replace")

out = {}
# 1) Louisville Hub: the page is an ArcGIS Hub; find its API
try:
    s, html = get("https://data.louisvilleky.gov/")
    hub = re.findall(r'https://[a-zA-Z0-9.\-]+\.arcgis\.com[^"\'\s]*', html)
    org = re.findall(r'data\.louisvilleky\.gov[^"\'\s]*', html)
    out["lou_hub_refs"] = {"status": s, "arcgis_refs": sorted(set(hub))[:6], "self_refs": sorted(set(org))[:8]}
except Exception as e:
    out["lou_hub_refs"] = {"err": str(e)}
# try the hub api v3 discovery on the domain itself (ArcGIS Hub sites host /api/search/v1 or /api/3/)
for api in ["https://data.louisvilleky.gov/api/search/v1?q=homicide",
            "https://data.louisvilleky.gov/api/3/catalog",
            "https://data.louisvilleky.gov/api/datasets?q=homicide"]:
    try:
        s, body = get(api, 6000)
        out.setdefault("lou_api_probes", []).append({"url": api, "status": s, "head": body[:300]})
    except Exception as e:
        out.setdefault("lou_api_probes", []).append({"url": api, "err": str(e)[:120]})

# 2) Jacksonville: try known COJ hub + arcgis domain guesses
for api in ["https://data-coj.opendata.arcgis.com/api/search/v1?q=homicide",
            "https://opendata.coj.net/",
            "https://cojgov.hub.arcgis.com/api/search/v1?q=homicide",
            "https://jax-fl.opendata.arcgis.com/api/search/v1?q=homicide",
            "https://www.jacksonville.gov/"]:
    try:
        s, body = get(api, 6000)
        out.setdefault("jax_api_probes", []).append({"url": api, "status": s, "head": body[:200]})
    except Exception as e:
        out.setdefault("jax_api_probes", []).append({"url": api, "err": str(e)[:120]})

# 3) FBI CDE keyless route for both agencies (the SAME route the banked wide-lane used)
# Louisville Metro PD ORI = KY0500300 ; Jacksonville Sheriff COI = FL0160000 (banked)
for ori in ["KY0500300", "FL0160000"]:
    for yr in (2024, 2025):
        url = f"https://api.usa.gov/crime/fbi/cde/summarized/agency/{ori}/HOM?from=01-{yr}&to=12-{yr}&API_KEY=IIu9Cu0SCc5S74BoTqIUtxq9iIOfY0f2EjjByDCY"
        try:
            s, body = get(url, 8000)
            out.setdefault("fbi_cde", []).append({"ori": ori, "year": yr, "status": s, "head": body[:500]})
        except Exception as e:
            out.setdefault("fbi_cde", []).append({"ori": ori, "year": yr, "err": str(e)[:120]})

with open("probe_lanes2_v1.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1)[:4000])
