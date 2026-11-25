#!/usr/bin/env python3
# v19 round-2 targeted boosters: name the canonical anchors the round-1 ranked queries missed.
import json, time, urllib.parse, urllib.request, re, os
B = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(B, "peer_review_scan_v19_raw.jsonl")
UA = {"User-Agent": "bob-scan/20 (mailto:scan@example.org)"}

QUERIES = {
  "econ_growth_efficiency_band": [
    "Bartik state local economic development policies who benefits",
    "Bartik new evidence tax incentives local economic growth inequality",
    "Empreendimentos enterprise zones effectiveness review",
    "Hanson California enterprise zones tax credits employment",
  ],
  "infra_efficiency_band": [
    "deferred maintenance cost escalation infrastructure rehabilitation",
    "pavement condition index maintenance spending relationship",
    "water system reinvestment rate infrastructure gap",
    "life cycle cost infrastructure maintenance ratio",
  ],
  "housing_edu_efficiency_band": [
    "housing supply elasticity regulation United States",
    "zoning restrictiveness housing prices effects",
    "supply constraints housing expenditures Glaeser",
    "Jackson effects school finance reforms contemporary update",
    "lafortune school finance reforms achievement",
    "housing vouchers neighborhood effects experiment",
  ],
  "fiscal_efficiency_band": [
    "municipal bond credit ratings fiscal distress predictors",
    "pension funding status municipal distress effect",
    "optimal reserve fund size percent general fund revenue",
    "fiscal slack local government savings",
  ],
  "prism_two_tier_band": [
    "efficiency public spending OECD framework",
    "data envelopment analysis Charnes Cooper Rhodes",
    "municipal waste collection efficiency determinants",
    "government efficiency outcomes per dollar citizens",
    "public sector efficiency frontier nonparametric",
  ],
}

def jget(url, timeout=30):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            return json.load(r)
    except Exception as e:
        return {"error": str(e)}

def clean(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()

def q_crossref(q):
    d = jget("https://api.crossref.org/works?query=" + urllib.parse.quote(q) +
             "&rows=8&select=title,container-title,issued,is-referenced-by-count,DOI,author,abstract,type")
    if "error" in d: return None
    out = []
    for it in d.get("message", {}).get("items", []):
        if it.get("type") not in ("journal-article", "book-chapter", "report-component", "proceedings-article", None, ""):
            continue
        out.append({
            "authors": ", ".join(f"{a.get('given','')} {a.get('family','')}".strip()
                                 for a in (it.get("author") or [])[:4]) or None,
            "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "title": (it.get("title") or [""])[0],
            "venue": (it.get("container-title") or [""])[0],
            "abstract": clean(it.get("abstract") or ""),
            "cited": it.get("is-referenced-by-count", 0),
            "doi": it.get("DOI", ""),
            "url": "https://doi.org/" + it.get("DOI", ""),
        })
    return [h for h in out if h["title"]]

def q_epmc(q):
    d = jget("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=" + urllib.parse.quote(q) +
             "&format=json&pageSize=5&resultType=core")
    if "error" in d: return None
    out = []
    for it in d.get("resultList", {}).get("result", []):
        src, pid = it.get("source", ""), it.get("id", "")
        out.append({
            "authors": (it.get("authorString") or "")[:120] or None,
            "year": int(it["pubYear"]) if it.get("pubYear", "").isdigit() else None,
            "title": (it.get("title", "") or "").rstrip(". "),
            "venue": ((it.get("journalInfo") or {}).get("journal") or {}).get("title", ""),
            "abstract": clean(it.get("abstractText") or ""),
            "cited": (int(it["citedByCount"]) if str(it.get("citedByCount", "")).lstrip("-").isdigit() else None),
            "doi": it.get("doi") or "",
            "url": f"https://europepmc.org/article/{src}/{pid}" if src and pid else None,
        })
    return out

def dedup(hits):
    seen, out = set(), []
    for h in hits:
        if not h or not h.get("title"): continue
        k = re.sub(r"\W+", "", h["title"].lower())[:80]
        if k in seen: continue
        seen.add(k); out.append(h)
    return out[:8]

with open(RAW, "a", encoding="utf-8") as f:
    for band, qs in QUERIES.items():
        for q in qs:
            for route, fn in (("crossref", q_crossref), ("europepmc_search", q_epmc)):
                hits = fn(q); time.sleep(1.0)
                rec = (({"scan": "BOB-SCAN-20", "band": band, "query": q, "route": route + "_r2", "hits": dedup(hits)})
                       if hits is not None else
                       {"scan": "BOB-SCAN-20", "band": band, "query": q, "route": route + "_r2", "error": "api_error", "hits": []})
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            print(f"{band}: {q} done")
print("ROUND-2 BOOSTERS DONE")
