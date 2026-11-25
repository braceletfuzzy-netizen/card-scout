import urllib.request, urllib.error, json, time, os
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
BASE = "https://cde.ucr.cjis.gov/LATEST"
B = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
OUT = B + "/oh_county_crime_raw.jsonl"

def cde(url, timeout=150, attempts=3):
    last = None
    for _ in range(attempts):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
            return json.loads(r.read().decode()), None
        except urllib.error.HTTPError as e:
            try: body = e.read().decode()[:200]
            except Exception: body = chr(32)
            return None, f"{e.code} {body}"
        except Exception as e:
            last = str(e); time.sleep(2)
    return None, last

dirf = json.load(open("C:/Users/J/_ori_dir_oh.json"))
agencies = [(cty, a) for cty, lst in sorted(dirf.items()) for a in lst if a.get("is_nibrs")]
done = set()
if os.path.exists(OUT):
    for line in open(OUT, encoding="utf-8"):
        try:
            r = json.loads(line); done.add(r["ori"])
        except Exception: pass
todo = [(c, a) for c, a in agencies if a["ori"] not in done]
print(f"{len(agencies)} nibrs agencies; {len(done)} done; {len(todo)} todo", flush=True)
n = 0
for cty, a in todo:
    ori = a["ori"]
    url = f"{BASE}/summarized/agency/{ori}/HOM?from=01-2019&to=12-2025&type=counts"
    d, e = cde(url)
    if not d:
        rec = {"ori": ori, "county": cty, "agency_name": a["agency_name"], "agency_type": a.get("agency_type_name"), "error": str(e), "data": None}
    else:
        act = d.get("offenses", {}).get("actuals", {})
        off = {k: v for k, v in act.items() if "Clearances" not in k}
        rec = {"ori": ori, "county": cty, "agency_name": a["agency_name"], "agency_type": a.get("agency_type_name"),
               "offense_series": off, "part_pop_raw": d.get("populations", {}).get("participated_population", {}), "raw_url": url}
    with open(OUT, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + chr(10))
    n += 1
    if n % 100 == 0: print(f"{n} pulled", flush=True)
    time.sleep(0.05)
print("DONE", flush=True)
