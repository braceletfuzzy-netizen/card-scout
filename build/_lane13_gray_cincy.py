"""Cincinnati 311 (gcej-gmiw Socrata): counts by year + by year x group_desc."""
import requests, json, collections

S = requests.Session(); S.headers["User-Agent"] = "lane-gray-safety/1.0"
FID = "gcej-gmiw"
BASE = f"https://data.cincinnati-oh.gov/resource/{FID}.json"

def yearly():
    q = {"$select": "date_extract_y(date_created) as yr, count(1) as n",
         "$group": "date_extract_y(date_created)", "$limit": 5000}
    rr = S.get(BASE, params=q, timeout=300)
    rr.raise_for_status()
    return {int(r["yr"]): int(r["n"]) for r in rr.json() if r.get("yr")}

def by_type():
    q = {"$select": "date_extract_y(date_created) as yr, group_desc, count(1) as n",
         "$group": "date_extract_y(date_created), group_desc", "$limit": 50000}
    rr = S.get(BASE, params=q, timeout=300)
    rr.raise_for_status()
    ty = collections.defaultdict(dict)
    for r in rr.json():
        if r.get("yr") is None or r.get("group_desc") is None:
            continue
        ty[int(r["yr"])][r["group_desc"]] = int(r["n"])
    return ty

if __name__ == "__main__":
    d = yearly()
    print("by year:", dict(sorted(d.items())), flush=True)
    ty = by_type()
    json.dump({"by_year": d, "types_by_year": {str(k): v for k, v in ty.items()}},
              open("C:/Users/J/_lane13_gray_cincinnati_raw.json", "w"))
    print("SAVED cincy; types/yr:", {k: len(v) for k, v in ty.items()})
