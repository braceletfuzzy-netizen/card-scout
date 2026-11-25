"""Memphis 311: year x type counts via per-year count queries (OpenedDateTime epoch range)."""
import requests, json, collections, time, datetime

base = "https://services.arcgis.com/g1fRTDLeMgspWrYp/arcgis/rest/services/311_All_Service_Calls/FeatureServer/0"
S = requests.Session(); S.headers["User-Agent"] = "lane-gray-safety/1.0"

yr_counts, type_by_year = {}, collections.defaultdict(collections.Counter)
for yr in range(2020, 2027):
    lo = int(datetime.datetime(yr, 1, 1).timestamp() * 1000)
    hi = int(datetime.datetime(yr + 1, 1, 1).timestamp() * 1000)
    where = f"OpenedDateTime >= timestamp '{datetime.datetime(yr,1,1).strftime('%Y-%m-%d %H:%M:%S')}' AND OpenedDateTime < timestamp '{datetime.datetime(yr+1,1,1).strftime('%Y-%m-%d %H:%M:%S')}'"
    q = {"where": where, "returnCountOnly": "true", "f": "json"}
    rr = S.get(base + "/query", params=q, timeout=120).json()
    if "count" in rr:
        yr_counts[yr] = rr["count"]
        print(yr, rr["count"], flush=True)
        # top types this year
        q2 = {"where": where, "groupByFieldsForStatistics": "TypeName",
              "outStatistics": json.dumps([{"statisticType": "count", "onStatisticField": "OBJECTID", "outStatisticFieldName": "n"}]),
              "returnGeometry": "false", "f": "json", "resultOffset": 0}
        rr2 = S.get(base + "/query", params=q2, timeout=120).json()
        for f in rr2.get("features", []):
            a = f["attributes"]
            type_by_year[yr][a.get("TypeName") or "unknown"] = a["n"]
    else:
        print(yr, "ERR", str(rr)[:150], flush=True)

json.dump({"year_counts": yr_counts, "types_by_year": {k: dict(v) for k, v in type_by_year.items()}},
          open("C:/Users/J/_lane13_gray_memphis_311_raw.json", "w"))
print("SAVED")
