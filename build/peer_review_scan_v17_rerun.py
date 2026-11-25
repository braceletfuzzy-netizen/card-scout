#!/usr/bin/env python3
# BOARD-3 PART-A step-1: cooled-API-wall re-run of the v17 zero-hit sweep rows.
# Honest-null convention: routes re-tried, both original and rerun results carried.
import json, time, urllib.request, urllib.parse

RAW = [r"C:/Users/J/peer_review_scan_v17_raw.jsonl",
       r"C:/Users/J/peer_review_scan_v17_raw2.jsonl",
       r"C:/Users/J/peer_review_scan_v17_raw3.jsonl"]

def jlines(p): return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]

zero_rows = []
for f in RAW:
    for r in jlines(f):
        if not r.get("hits"):
            zero_rows.append(r)

# dedupe on (band, query)
seen, targets = set(), []
for r in zero_rows:
    k = (r["band"], r["query"])
    if k not in seen:
        seen.add(k); targets.append(r)
print(f"zero-hit rows: {len(zero_rows)}, unique (band,query) targets: {len(targets)}")

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Board3-scan-v17-rerun/1.0 (contact: local)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))

def crossref(q, n=8):
    u = "https://api.crossref.org/works?" + urllib.parse.urlencode({"query.bibliographic": q, "rows": n, "select": "DOI,title,container-title,issued,is-referenced-by-count,author"})
    d = fetch(u)
    hits = []
    for it in d.get("message", {}).get("items", []):
        t = (it.get("title") or [""])[0]
        if not t: continue
        yr = None
        for k in ("issued",):
            dp = it.get(k, {}).get("date-parts", [[None]])
            yr = dp[0][0] if dp and dp[0] else None
        au = it.get("author", [])
        hits.append({"authors": ", ".join(f"{a.get('family','')}" for a in au[:4]) or None,
                     "year": yr, "title": t,
                     "venue": (it.get("container-title") or [""])[0],
                     "cited": it.get("is-referenced-by-count", 0),
                     "url": it.get("DOI")})
    return hits

def epmc(q, n=8):
    u = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
        {"query": q, "format": "json", "pageSize": n})
    d = fetch(u)
    hits = []
    for it in d.get("resultList", {}).get("result", []):
        t = it.get("title", "")
        if not t: continue
        hits.append({"authors": it.get("authorString", "")[:120] or None,
                     "year": int(it["pubYear"]) if it.get("pubYear", "").isdigit() else None,
                     "title": t, "venue": it.get("journalTitle", ""),
                     "cited": int(it["citedByCount"]) if str(it.get("citedByCount", "")).isdigit() else 0,
                     "abstract": it.get("abstractText", ""), "url": it.get("doi", "")})
    return hits

def pubmed(q, n=8):
    u = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "term": q, "retmode": "json", "retmax": n})
    ids = fetch(u).get("esearchresult", {}).get("idlist", [])
    if not ids: return []
    u2 = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
    d = fetch(u2).get("result", {})
    hits = []
    for i in ids:
        it = d.get(i)
        if not it: continue
        hits.append({"authors": (it.get("authors") and ", ".join(a.get("name", "") for a in it["authors"][:4])) or None,
                     "year": it.get("pubdate", "")[:4] if it.get("pubdate") else None,
                     "title": it.get("title", ""), "venue": it.get("fulljournalname", ""),
                     "cited": None, "url": f"PMID:{i}"})
    return hits

ROUTE = {"crossref": crossref, "crossref_search": crossref, "pm_search": pubmed, "europepmc_search": epmc, "none": epmc}
out_f = open(r"C:/Users/J/peer_review_scan_v17_raw4.jsonl", "w", encoding="utf-8")
ok = 0
for r in targets:
    q, band = r["query"], r["band"]
    for rt, fn in [("crossref_rerun", crossref), ("europepmc_rerun", epmc)]:
        try:
            hits = fn(q)
        except Exception as e:
            hits = None
            err = str(e)[:80]
        else:
            err = None
        row = {"band": band, "query": q, "route": rt, "hits": hits or [],
               "rerun_error": err, "rerun_of": "zero-hit original row"}
        out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
        if hits: ok += 1
        time.sleep(0.4)
out_f.close()
print(f"re-ran {len(targets)*2} routes; non-empty captures: {ok}")
