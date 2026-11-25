"""LANE-GRAY-SAFETY pull 1: Memphis 311 All Service Calls AGOL FeatureServer (keyless)."""
import requests, json, collections, time

base = "https://services.arcgis.com/g1fRTDLeMgspWrYp/arcgis/rest/services/311_All_Service_Calls/FeatureServer/0"
S = requests.Session()
S.headers["User-Agent"] = "lane-gray-safety/1.0"

def stat(field, st):
    stat_json = json.dumps([{"statisticType": st, "onStatisticField": field, "outStatisticFieldName": "v"}])
    q = {"where": "1=1", "returnCountOnly": "false", "f": "json", "outStatistics": stat_json}
    return S.get(base + "/query", params=q, timeout=90).json()

print("min/max OpenedDateTime:", stat("OpenedDateTime", "min"), stat("OpenedDateTime", "max"))

# year counts via groupBy
q = {
    "where": "1=1",
    "groupByFieldsForStatistics": "YEAR(OpenedDateTime)",
    "outStatistics": json.dumps([{"statisticType": "count", "onStatisticField": "OBJECTID", "outStatisticFieldName": "n"}]),
    "orderByFields": "YEAR(OpenedDateTime)",
    "f": "json",
}
rr = S.get(base + "/query", params=q, timeout=120).json()
rows = rr.get("features", [])
year_counts = {f["attributes"].get("YEAR(OpenedDateTime)") or f["attributes"].get("YEAR_OpenedDateTime"): f["attributes"]["n"] for f in rows}
print("total-rows:", len(rows), "grand:", sum(v for v in year_counts.values() if v))
print(sorted((int(k), v) for k, v in year_counts.items() if k is not None)[:30])

# top types (TypeName x total) — calls-by-type
q2 = dict(q)
q2["groupByFieldsForStatistics"] = "TypeName"
q2["outStatistics"] = json.dumps([{"statisticType": "count", "onStatisticField": "OBJECTID", "outStatisticFieldName": "n"}])
q2.pop("orderByFields", None)
rr2 = S.get(base + "/query", params=q2, timeout=120).json()
type_rows = rr2.get("features", [])
print("n_types:", len(type_rows))
top = sorted(((f["attributes"]["TypeName"], f["attributes"]["n"]) for f in type_rows), key=lambda x: -x[1])[:25]
for t, n in top:
    print(f"  {n:>8}  {t}")
json.dump({"year_counts": year_counts, "n_total": sum(year_counts.values()), "top_types": top},
          open("C:/Users/J/_lane13_gray_memphis_311_year_counts.json", "w"))
