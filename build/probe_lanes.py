#!/usr/bin/env python3
# probe_lanes.py — verify keyless routes for Louisville vs Jacksonville civic call.
import json, urllib.request, socket
socket.setdefaulttimeout(12)

def probe(url, hdr=None):
    req = urllib.request.Request(url, headers=hdr or {"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read(3000)
            return {"url": url, "status": r.status, "head": body[:400].decode("utf-8", "replace")}
    except Exception as e:
        return {"url": url, "status": f"ERR {type(e).__name__}: {e}"}

targets = [
    # Louisville
    "https://data.louisvilleky.gov/",
    "https://data.louisvilleky.gov/api/3/catalog/v1?q=homicide",
    "https://opendata.louisvilleky.gov/",
    # Jacksonville (COJ) — known hosts
    "https://data.coj.net/",
    "https://opendata.jacksonville.gov/",
    "https://www.coj.net/",
    "https://jaxgis.coj.net/server/rest/services?f=json",
    # ArcGIS hub (Jacksonville published a homicide/hub layer class here)
    "https://services.arcgis.com/3NyIcTl9zGF7ETQc/arcgis/rest/services?f=json",
]
out = [probe(u) for u in targets]
for o in out:
    print("==", o["url"], "->", o["status"])
    if o["status"] == 200:
        print(o["head"][:300].replace("\n", " ")[:300])
with open("probe_lanes_v1.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
