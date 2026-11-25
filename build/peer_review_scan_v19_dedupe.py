#!/usr/bin/env python3
# Dedup v19 raw -> canonical corpus with per-rec metadata.
import json, re, os
B = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(B, "peer_review_scan_v19_raw.jsonl")
OUT = os.path.join(B, "peer_review_scan_v19_corpus.json")
recs = []
queries = {}
routes = {}
errors = []
for line in open(RAW, encoding="utf-8"):
    r = json.loads(line)
    if not r.get("band"): continue
    q = r["query"]
    queries.setdefault(q, set()).add(r["band"])
    routes[r["route"]] = routes.get(r["route"], 0) + 1
    if r.get("error"): errors.append((q, r["route"]))
    for h in r.get("hits", []):
        h2 = dict(h); h2["band"] = r["band"]; h2["query"] = q; h2["route"] = r["route"]
        recs.append(h2)

# dedupe by normalized title (keep the richest abstract version)
seen = {}
for h in recs:
    k = re.sub(r"\W+", "", (h.get("title") or "").lower())[:90]
    if not k: continue
    if k in seen:
        old = seen[k]
        if len(h.get("abstract") or "") > len(old.get("abstract") or ""):
            old["abstract"] = h["abstract"]
            old["cited"] = old.get("cited") or h.get("cited")
        old["query"] = old["query"] if old["query"] == h["query"] else old["query"] + " | " + h["query"]
        old["route"] = old["route"] if old["route"] == h["route"] else old["route"] + "/" + h["route"]
    else:
        seen[k] = h
corpus = list(seen.values())

years = [c["year"] for c in corpus if isinstance(c.get("year"), int)]
cits = [c["cited"] for c in corpus if isinstance(c.get("cited"), int)]
withab = [c for c in corpus if len(re.sub(r"<[^>]+>", "", c.get("abstract") or "")) > 100]
bands = {}
for c in corpus: bands[c["band"]] = bands.get(c["band"], 0) + 1

out = {
    "_record": "peer_review_scan_v19 corpus — BOB-SCAN-20 THE LITERATURE PRISM FOR THE OUTPUT VECTOR",
    "built": "2026-11-25",
    "deduped_records": len(corpus),
    "raw_hit_rows": len(recs),
    "unique_queries": len(queries),
    "route_distribution": routes,
    "api_error_rows": errors,
    "records_with_abstract_gt_100": len(withab),
    "abstract_share_pct": round(100 * len(withab) / max(1, len(corpus)), 1),
    "year_span": [min(years), max(years)] if years else None,
    "median_cites": sorted(cits)[len(cits) // 2] if cits else None,
    "max_cites": max(cits) if cits else None,
    "band_distribution": bands,
    "records": sorted(corpus, key=lambda c: -(c.get("cited") or 0)),
}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)

# print top-cited per band for magnitude extraction
for band in sorted(set(c["band"] for c in corpus)):
    rows = [c for c in corpus if c["band"] == band]
    rows.sort(key=lambda c: -(c.get("cited") or 0))
    print(f"\n=== {band} ({len(rows)} recs) ===")
    for c in rows[:12]:
        ab = "YES" if len(re.sub(r'<[^>]+>', '', c.get("abstract") or "")) > 100 else "no"
        print(f"  [{c.get('cited')}] {c.get('year')} | {c['title'][:95]} | {(c.get('venue') or '')[:40]} | abst={ab} | {c['route']}")
print(f"\nCORPUS: {len(corpus)} deduped, {len(withab)} w/abstracts, errors={len(errors)}")
