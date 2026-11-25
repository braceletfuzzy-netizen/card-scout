"""GRAY-LANE: AGOL FeatureServer year x type counts via per-year where clauses (epoch millis)."""
import requests, json, collections, datetime, sys

CNT = json.dumps([{"statisticType": "count", "onStatisticField": "ObjectId", "outStatisticFieldName": "n"}])

def pull(base, date_field, year_lo, year_hi, type_field, out_json, label):
    S = requests.Session(); S.headers["User-Agent"] = "lane-gray-safety/1.0"
    by_year, ty = {}, collections.defaultdict(collections.Counter)
    for yr in range(year_lo, year_hi):
        a = datetime.datetime(yr, 1, 1); b = datetime.datetime(yr + 1, 1, 1)
        where = (
            f"{date_field} >= timestamp '{a.strftime('%Y-%m-%d %H:%M:%S')}' "
            f"AND {date_field} < timestamp '{b.strftime('%Y-%m-%d %H:%M:%S')}'"
        )
        q = {"where": where, "returnCountOnly": "true", "f": "json"}
        rr = S.get(base + "/query", params=q, timeout=120).json()
        if "count" in rr:
            by_year[yr] = rr["count"]
            if rr["count"] and type_field:
                q2 = {"where": where, "groupByFieldsForStatistics": type_field, "outStatistics": CNT,
                      "returnGeometry": "false", "f": "json"}
                rr2 = S.get(base + "/query", params=q2, timeout=120).json()
                for f in rr2.get("features", []):
                    att = f["attributes"]
                    ty[yr][str(att.get(type_field) or "unknown")[:60]] = att["n"]
            print(label, yr, by_year[yr], flush=True)
        else:
            print(label, yr, "ERR", str(rr)[:120], flush=True)
    json.dump({"by_year": by_year, "types_by_year": {str(k): dict(v) for k, v in ty.items()}},
              open(out_json, "w"))
    print(label, "SAVED", out_json)

if __name__ == "__main__":
    which = sys.argv[1]
    if which == "detroit":
        pull("https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/improve_detroit/FeatureServer/0",
             "created_at", 2014, 2027, "request_type",
             "C:/Users/J/_lane13_gray_detroit_raw.json", "DETROIT")
