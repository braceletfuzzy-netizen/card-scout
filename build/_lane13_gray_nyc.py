"""NYC 311 Socrata groupBy: counts by year. NYC host is slow — use long timeouts."""
import requests, json

S = requests.Session(); S.headers["User-Agent"] = "lane-gray-safety/1.0"

def pull(fid, label, out):
    q = {
        "$select": "date_extract_y(created_date) as yr, count(1) as n",
        "$group": "date_extract_y(created_date)",
        "$where": "1=1",
        "$limit": 5000,
    }
    rr = S.get(f"https://data.cityofnewyork.us/resource/{fid}.json", params=q, timeout=570)
    rr.raise_for_status()
    rows = rr.json()
    d = {int(r["yr"]): int(r["n"]) for r in rows if r.get("yr")}
    out[label] = d
    print(label, d, flush=True)

if __name__ == "__main__":
    out = {}
    for fid, label in [("erm2-nwe9", "2020_present"), ("76ig-c548", "2010_2019")]:
        try:
            pull(fid, label, out)
        except Exception as e:
            print(label, "ERR", str(e)[:200], flush=True)
    json.dump(out, open("C:/Users/J/_lane13_gray_nyc_year_counts.json", "w"))
    print("SAVED nyc")
