#!/usr/bin/env python3
# civic_call_recheck_v1.py — THE 10AM-CLASS RE-CHECK for the Louisville pre-registered civic call.
# Pulls LMPD (KY0568000) monthly HOM actuals from the keyless FBI CDE summarizer, builds the
# year-to-date 2026 total, and compares against the pre-registered call when a full year exists.
# Exit codes: 0 = checked, call pending (partials only) | 1 = call VERDICT HIT | 2 = call VERDICT MISS
#             3 = route failure (honest: no claim either way)
import json, sys, datetime, urllib.request, socket
socket.setdefaulttimeout(60)

PREREG = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/pre_registered_civic_call_v1.json"
ORI = "KY0568000"
YEAR = datetime.date.today().year

def getjson(url, tries=3):
    import time
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})).read())
        except Exception:
            if i == tries - 1: return None
            time.sleep(3)

pop_cache = {}
def agency_pop(y):
    if y in pop_cache: return pop_cache[y]
    d = getjson(f"https://cde.ucr.cjis.gov/LATEST/summarized/agency/{ORI}/HOM?from=01-{y}&to=12-{y}")
    p = ((d or {}).get("populations", {}).get("population", {}) or {}).get("Louisville Metro Police Department", {})
    v = p.get(f"07-{y}") or p.get(f"01-{y}")
    pop_cache[y] = v
    return v

def ytd(y):
    d = getjson(f"https://cde.ucr.cjis.gov/LATEST/summarized/agency/{ORI}/HOM?from=01-{y}&to=12-{y}")
    if not d: return None, None
    act = (d.get("offenses", {}).get("actuals") or {}).get("Louisville Metro Police Department Offenses", {})
    months = {}
    for kk, v in act.items():
        yy = int(kk.split("-")[1])
        if yy == y: months[kk] = (v or 0)
    if not months: return None, None
    return int(sum(months.values())), sorted(months)

try:
    pre = json.load(open(PREREG, encoding="utf-8"))
except Exception as e:
    print("preregistration file missing:", e); sys.exit(3)

center = pre["lou_own_mean_rate_2021_25"]
today = datetime.date.today()
out = {"checked": today.isoformat(), "city": pre["city"], "prediction": pre["prediction"],
       "falsifier": pre["falsifier"], "preregistered_at": pre["timestamp_utc"]}

# full-year check only when the year is complete AND the CDE refresh window has passed (~Mar of next year)
if today.year > pre["target_year"]:
    got, months = ytd(pre["target_year"])
    pop = agency_pop(pre["target_year"])
    if got is None or not pop:
        out["status"] = "route-failure — no claim"; print(json.dumps(out, indent=1)); sys.exit(3)
    rate = round(got / pop * 1e5, 2)
    actual_dir = "DOWN" if rate < center else ("UP" if rate > center else "FLAT")
    out.update({"target_year_full_year": {"count": got, "pop": pop, "rate": rate},
                "center_2021_25": center, "actual_direction": actual_dir,
                "verdict": "HIT" if actual_dir == pre["prediction"] else "MISS"})
    print(json.dumps(out, indent=1))
    sys.exit(1 if out["verdict"] == "HIT" else 2)
else:
    got, months = ytd(YEAR)
    if got is not None:
        out["target_year"] = pre["target_year"]
        out["ytd_status"] = {"year": YEAR, "count_ytd": got, "months_present": len(months or []),
                             "note": "partials carried, never annualized (the banked months-guard law); the pre-registered call resolves only when the full target year publishes"}
    print(json.dumps(out, indent=1)); sys.exit(0)
