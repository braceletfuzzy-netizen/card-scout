# LANE-2/3 CRIME PULL: Pittsburgh PD + Oklahoma City PD homicide series from keyless FBI CDE.
# Same conventions as crime_series_pull_v2.py / wide_b_runner.py (monthly Offenses sum, months_present guard).
# Output: crime_wide_c.jsonl (merge-safe "-c" suffix).
import urllib.request, urllib.error, json, time, re

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
BASE = "https://cde.ucr.cjis.gov/LATEST"
OUT = B + 'crime_wide_c.jsonl'

CITIES = [("Pittsburgh", "PA"), ("Oklahoma City", "OK")]

def cde(url, timeout=150, attempts=3):
    last = None
    for _ in range(attempts):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
            return json.loads(r.read().decode()), None
        except urllib.error.HTTPError as e:
            body = ''
            try: body = e.read().decode()[:250]
            except Exception: pass
            return None, f'{e.code} {body}'
        except Exception as e:
            last = str(e); time.sleep(1.5)
    return None, last

def ori_lookup(state, city):
    """Keyless byStateAbbr directory route (cached copies in _wide/agency_*.json)."""
    try:
        d = json.load(open(B + f'_wide/agency_{state}.json'))
        src = f'_wide/agency_{state}.json (cached byStateAbbr pull)'
    except FileNotFoundError:
        d_raw, e = cde(f'{BASE}/agency/byStateAbbr/{state}')
        if d_raw is None:
            return None, None, f'agency dir fail: {e}'
        d = {k: v for k, v in d_raw.items()}
        src = f'live {BASE}/agency/byStateAbbr/{state}'
    want = re.sub(r'[^A-Z ]', '', city.upper()).strip()
    for county, lst in d.items():
        for a in lst:
            nm = re.sub(r'[^A-Z ]', '', (a.get('agency_name') or '').upper()).strip()
            if nm in (want + ' POLICE DEPARTMENT', want + ' POLICE', want + ' BUREAU OF POLICE'):
                return a['ori'], a, src
    # fallback: any City-type agency containing city name + police
    for county, lst in d.items():
        for a in lst:
            nm = (a.get('agency_name') or '').upper()
            if want in nm and 'POLICE' in nm and (a.get('agency_type_name') == 'City'):
                return a['ori'], a, src
    return None, None, src + ' (no match)'

def hom_year(ori, y):
    data, err = cde(f"{BASE}/summarized/agency/{ori}/HOM?from=01-{y}&to=12-{y}&type=counts")
    if not data:
        return None, err
    act = data.get("offenses", {}).get("actuals", {})
    series, label = None, None
    for k, months in act.items():
        if "Clearances" in k:
            continue
        series, label = months, k
        break
    if series is None:
        return None, "no offense series"
    total = sum(v for v in series.values() if isinstance(v, (int, float)))
    present = sum(1 for v in series.values() if isinstance(v, (int, float)))
    return {"label": label, "total": int(total), "months_present": present,
            "raw_url": f"{BASE}/summarized/agency/{ori}/HOM?from=01-{y}&to=12-{y}&type=counts"}, None

def write_row(row):
    with open(OUT, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

rows_out = []
for city, st in CITIES:
    ori, meta, src = ori_lookup(st, city)
    print(f'{city} ({st}): ORI={ori} agency={meta and meta.get("agency_name")} nibrs_start={meta and meta.get("nibrs_start_date")} via {src}')
    if not ori:
        print('  -> NO ORI FOUND, skipping')
        continue
    for y in range(2019, 2026):
        r, e = hom_year(ori, y)
        if not r:
            print(f'  {y}: N/A ({e})')
            rows_out.append({"city": city, "state": st, "year": y, "murders": None, "ori": ori,
                             "source_refs": [f"FBI CDE summarized/agency HOM: no data ({e})"],
                             "data_quality": "official", "months_present": 0, "full_year": False,
                             "notes": f"CDE summarizer has no monthly homicide counts for {ori} in {y}.",
                             "honest_gaps": ["murders unknown"]})
            continue
        full_year = r['months_present'] == 12
        print(f'  {y}: murders={r["total"]} months={r["months_present"]}/12')
        rows_out.append({"city": city, "state": st, "year": y, "murders": r["total"], "ori": ori,
                         "source_refs": [r["raw_url"]], "data_quality": "official",
                         "months_present": r["months_present"], "full_year": full_year,
                         "notes": f"Sum of {r['months_present']}/12 monthly CDE 'Offenses' counts for {meta.get('agency_name')} ({ori}) via FBI CDE.",
                         "honest_gaps": [] if full_year else [f"partial-year: only {r['months_present']} months in CDE for {y}"]})
        time.sleep(0.1)
    # 2026 YTD (Jan-current)
    data, err = cde(f"{BASE}/summarized/agency/{ori}/HOM?from=01-2026&to=12-2026&type=counts")
    if data:
        act = data.get("offenses", {}).get("actuals", {})
        series = next((m for k, m in act.items() if "Clearances" not in k), None)
        if series is not None:
            total = sum(v for v in series.values() if isinstance(v, (int, float)))
            mp = sum(1 for v in series.values() if isinstance(v, (int, float)))
            print(f'  2026YTD: murders={int(total)} months={mp}')
            rows_out.append({"city": city, "state": st, "year": 2026, "murders": int(total), "ori": ori,
                             "source_refs": ["CDE 2026 partial-year pull"], "data_quality": "official",
                             "months_present": mp, "full_year": False,
                             "notes": f"2026 partial-year (Jan-current): {int(total)} through {mp} months. Not a full-year figure.",
                             "honest_gaps": ["partial-year YTD only"]})
    else:
        print(f'  2026YTD: N/A ({err})')
        rows_out.append({"city": city, "state": st, "year": 2026, "murders": None, "ori": ori,
                         "source_refs": [f"FBI CDE: no 2026 data ({err})"], "data_quality": "official",
                         "months_present": 0, "full_year": False,
                         "notes": "CDE has no 2026 homicide counts (year not closed).",
                         "honest_gaps": ["2026 unavailable until FBI release"]})

for r in rows_out:
    write_row(r)
print(f'wrote {len(rows_out)} rows to crime_wide_c.jsonl')
