#!/usr/bin/env python3
# backwards_test_v1 — OUTCOME-SERIES BUILDER v2 (priority-convention fix):
# a city-year's canonical outcome = PANEL cell (murders+population+murder_rate verbatim from maslow_joint_panel_v1, the FE frame's own convention)
# > murders_all_v1 count + _test2 pop bank (PEP/decennial-anchor, labeled) > murders_all count only (rate honest-null)
# > banked NYPD murdery-by-year wiki table for the NYC 1980-2018 interior (rate only at decennial anchors 1980/1990/2000).
# Priority prevents denominator-vintage mismatch between the scored actuals and the banked in-sample frames.
import json
from collections import Counter

BUILD = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build"
def jlines(p): return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]

rows = jlines(f"{BUILD}/maslow_joint_panel_v1.jsonl")
mur = json.load(open(f"{BUILD}/murders_all_v1.json", encoding="utf-8"))
mb = json.load(open(f"{BUILD}/_test2_merge_bank.json", encoding="utf-8"))
popb = {k: v["population"] for k, v in mb["pop"].items()}
popsrc = {k: v["pop_source"] for k, v in mb["pop"].items()}
ts = json.load(open(f"{BUILD}/triple_slider_v6d.json", encoding="utf-8"))
ts_pop = {(r["city"], int(r["year"])): r["population"] for r in ts if r.get("population")}
nyc_wiki = {1980:1814,1981:1826,1982:1668,1983:1622,1984:1450,1985:1384,1986:1582,1987:1672,1988:1896,1989:1905,1990:2245,1991:2154,1992:1995,1993:1946,1994:1561,1995:1177,1996:983,1997:770,1998:633,1999:671,2000:673,2001:649,2002:587,2003:597,2004:570,2005:539,2006:596,2007:496,2008:523,2009:471,2010:536,2011:515,2012:419,2013:335,2014:333,2015:352,2016:335,2017:292,2018:295,2019:319,2020:468,2021:488,2022:438,2023:391,2024:377,2025:303}  # NYPD CompStat basis; 2019-2024 fallback only (murders_all DCJS basis takes priority)
dec_pop = {("NYC", 1980): 7071639, ("NYC", 1990): 7322564, ("NYC", 2000): 8008288}
PARTIAL = {2026}

out = {}
def put(c, y, murders, murders_src, pop=None, pop_src=None, rate=None, rate_src=None, priority="panel"):
    e = out.setdefault((c, int(y)), {"city": c, "year": int(y), "priority": priority})
    e["murders"] = murders; e["murders_src"] = murders_src
    if pop is not None: e["population"] = pop; e["pop_src"] = pop_src
    if rate is not None:
        e["rate"] = round(rate, 2); e["rate_src"] = rate_src
        e.setdefault("priority", priority)

# 1) PANEL cells (canonical)
for r in rows:
    if r.get("murders") is not None:
        put(r["city"], r["year"], r["murders"], "panel maslow_joint_panel_v1 (banked murders)",
            r.get("population"), "panel denominator (banked)", r.get("murder_rate"),
            "panel murder_rate (the FE-frame convention)", priority="panel")

# 2) murders_all + pop banks
for k, v in mur.items():
    if not v: continue
    c, y = k.split("|"); y = int(y)
    e = out.setdefault((c, y), {"city": c, "year": y})
    if e.get("murders") is not None and e.get("priority") == "panel":
        continue
    e["murders"] = v; e["murders_src"] = "murders_all_v1 (banked)"
    e.setdefault("priority", "murders_all")
    p = popb.get(k) or ts_pop.get((c, y))
    if p:
        e["population"] = p
        e["pop_src"] = "pop-bank:" + (popsrc.get(k, "triple_slider_v6d")[:60])
        e["rate"] = round(v / p * 1e5, 2); e["rate_src"] = "murders_all / pop-bank"

# 3) NYC wiki interior
for y in range(1980, 2026):  # includes 2019-2025 NYPD-basis fallbacks (murders_all/panel take priority where banked)
    e = out.setdefault(("NYC", y), {"city": "NYC", "year": y})
    if "murders" not in e:
        e["murders"] = nyc_wiki[y]
        e["murders_src"] = "banked NYPD murdery-by-year wiki table (_wiki_Crime_in_New_York_City.txt)"
        e.setdefault("priority", "wiki_nyc")
    p = dec_pop.get(("NYC", y)) or popb.get(f"NYC|{y}") or ts_pop.get(("NYC", y))
    if p and "rate" not in e:
        _src = ("wiki NYC historical-population table (decennial census)" if ("NYC", y) in dec_pop
                else "pop-bank (PEP vintage-2025 SUMLEV 162)")
        e["population"] = p; e["pop_src"] = _src
        e["rate"] = round(e["murders"] / p * 1e5, 2)
        e["rate_src"] = "NYPD count / decennial census pop"
    e["nypd_dcjs_basis_note"] = "NYPD table may differ from the DCJS basis by plus/minus a few counts (e.g. 2019-2024); labeled, not reconciled"


# 4) post-pass: attach PEP/pop-bank denominators to remaining count-only cells (labeled; rate computed)
for k, v in mur.items():
    if not v: continue
    c, y = k.split("|"); y = int(y)
    e = out.get((c, y))
    if e and e.get("murders") is not None and "rate" not in e:
        p = popb.get(k) or ts_pop.get((c, y))
        if p:
            e["population"] = p; e["pop_src"] = "pop-bank attach:" + (popsrc.get(k, "triple_slider_v6d")[:50])
            e["rate"] = round(e["murders"] / p * 1e5, 2); e["rate_src"] = "count / pop-bank attach"

# flag 2026 partial cells
for (c, y), e in out.items():
    if y == 2026:
        e["partial_year_flag"] = "2026 YTD 9-11 months in the banked series — EXCLUDED from backwards scoring (honest partials, never annualized/fabricated)"

with open(f"{BUILD}/_backwards_outcome_series_v1.json", "w", encoding="utf-8") as f:
    json.dump({f"{c}|{y}": e for (c, y), e in out.items()}, f, indent=1, ensure_ascii=False)
print("outcome cells:", len(out))
print("priority distribution:", Counter(e.get("priority") for e in out.values()))
rate_rows = [(c, y, e["rate"]) for (c, y), e in out.items() if e.get("rate")]
print("rate cells:", len(rate_rows))
for c in ["Boston", "NYC", "St. Louis", "Memphis", "Detroit", "Cincinnati", "New Orleans", "Houston", "Oklahoma City", "Pittsburgh"]:
    ys = sorted(y for (cc, y), e in out.items() if cc == c and e.get("rate"))
    print(c, "rate-years:", ys)
