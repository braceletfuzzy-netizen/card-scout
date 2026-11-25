"""GRAY-LANE pull: Detroit Improve Detroit Issues — year x request_type counts (keyless AGOL)."""
import requests, json, collections, datetime

base = "https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/improve_detroit/FeatureServer/0"
S = requests.Session(); S.headers["User-Agent"] = "lane-gray-safety/1.0"

CNT = json.dumps([{"statisticType": "count", "onStatisticField": "ObjectId", "outStatisticFieldName": "n"}])

def year_group(out_group=None):
    q = {
        "where": "1=1",
        "groupByFieldsForStatistics": "YEAR(created_at)",
        "outStatistics": CNT,
        "returnGeometry": "false",
        "f": "json",
    }
    if out_group:
        q["groupByFieldsForStatistics"] = f"YEAR(created_at),{out_group}"
    rr = S.get(base + "/query", params=q, timeout=180)
    try:
        return rr.json()
    except Exception:
        return {"error": rr.text[:200]}

by_year = {}
for f in year_group().get("features", []):
    a = f["attributes"]; by_year[a.get("YEAR_created_at")] = a["n"]
print("by-year:", {k: v for k, v in sorted(by_year.items(), key=lambda x: (x[0] is None, x[0]))})

# request_type per year (grouping might choke on 1000 groups; limit via where on years with big volume)
ty = collections.defaultdict(collections.Counter)
for f in year_group("request_type").get("features", []):
    a = f["attributes"]
    ty[a.get("YEAR_created_at")][a.get("request_type") or "unknown"] = a["n"]

out = {"by_year": by_year, "types_by_year": {str(k): dict(v) for k, v in ty.items()}}
json.dump(out, open("C:/Users/J/_lane13_gray_detroit_raw.json", "w"))
print("n types per year:", {str(k): len(v) for k, v in ty.items()})
print("SAVED")
