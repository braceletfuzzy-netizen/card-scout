"""Houston 311 Archives (5.8M rows) + Recent SR: year + year x CASE_TYPE counts, keyless AGOL/MapServer."""
import requests, json, collections, datetime

ARC = "https://mycity2.houstontx.gov/gisweb01/rest/services/311/Houston311_Archives/MapServer/0"
REC = "https://mycity2.houstontx.gov/gisweb01/rest/services/311/HOUSTON311_RECENT_SR_SNOW/FeatureServer/0"
S = requests.Session(); S.headers["User-Agent"] = "lane-gray-safety/1.0"

def where_for(base, yr):
    a = datetime.datetime(yr, 1, 1); b = datetime.datetime(yr + 1, 1, 1)
    return (f"CREATED_ON >= timestamp '{a.strftime('%Y-%m-%d %H:%M:%S')}' "
            f"AND CREATED_ON < timestamp '{b.strftime('%Y-%m-%d %H:%M:%S')}'")

def counts(base, years, label):
    by_year, ty = {}, collections.defaultdict(collections.Counter)
    for yr in years:
        w = where_for(base, yr)
        rr = S.get(base + "/query", params={"where": w, "returnCountOnly": "true", "f": "json"}, timeout=180).json()
        if "count" in rr:
            by_year[yr] = rr["count"]
            print(label, yr, rr["count"], flush=True)
            if rr["count"] > 0 and rr["count"] < 400000:
                rr2 = S.get(base + "/query", params={
                    "where": w, "groupByFieldsForStatistics": "CASE_TYPE",
                    "outStatistics": json.dumps([{"statisticType": "count", "onStatisticField": "OBJECTID", "outStatisticFieldName": "n"}]),
                    "returnGeometry": "false", "f": "json"}, timeout=180).json()
                for f in rr2.get("features", []):
                    att = f["attributes"]
                    ty[yr][str(att.get("CASE_TYPE") or "unknown")[:50]] = att["n"]
        else:
            print(label, yr, "ERR", str(rr)[:100], flush=True)
    return by_year, ty

if __name__ == "__main__":
    ay, aty = counts(ARC, list(range(2012, 2026)), "HOU-ARC")
    ry, rty = counts(REC, list(range(2025, 2027)), "HOU-REC")
    out = {
        "archives_by_year": ay, "archives_types_by_year": {str(k): dict(v) for k, v in aty.items()},
        "recent_by_year": ry, "recent_types_by_year": {str(k): dict(v) for k, v in rty.items()},
        "note": "archives MapServer capped at 1,000-row type groupings skipped for years >400k by CASE_TYPE volume guard",
    }
    json.dump(out, open("C:/Users/J/_lane13_gray_houston_raw.json", "w"))
    print("SAVED houston")
