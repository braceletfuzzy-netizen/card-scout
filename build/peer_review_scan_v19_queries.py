#!/usr/bin/env python3
# BOB-SCAN-20 — peer_review_scan_v19: THE LITERATURE PRISM FOR THE OUTPUT VECTOR.
# Five bands: fiscal-efficiency / econ-growth-efficiency / infra-efficiency / housing-edu-efficiency / the-prism (two-tier).
# Routes: keyless Crossref works API + PubMed eutils + EuropePMC (the bob19 proven routes).
# Laws: every row = a live probe result; honest-nulls logged; resume-safe (skip done query rows).
import json, time, urllib.parse, urllib.request, re, os
import xml.etree.ElementTree as ET

RAW = r"C:\Users\J\Documents\LLM\cardscout-2.0\For You\PolyScout\build\peer_review_scan_v19_raw.jsonl"
UA = {"User-Agent": "bob-scan/20 (mailto:scan@example.org)"}

QUERIES = {
  "fiscal_efficiency_band": [
    "pension funded ratio municipal fiscal distress",
    "rainy day fund budget stabilization recession outcomes state",
    "local government debt credit rating downgrade",
    "OPEB unfunded retiree health liability local government",
    "fiscal distress municipal bankruptcy determinants",
    "general fund reserves local government stability",
  ],
  "econ_growth_efficiency_band": [
    "tax incentives economic development job creation effectiveness Bartik",
    "enterprise zone employment effects",
    "business establishment birth local tax elasticity",
    "state business tax climate economic growth",
    "local economic development incentives firm location evidence",
    "job creation tax credit evaluation",
  ],
  "infra_efficiency_band": [
    "deferred maintenance road pavement rehabilitation cost",
    "infrastructure maintenance versus reconstruction cost multiplier",
    "water utility infrastructure investment efficiency",
    "bridge condition spending investment outcomes",
    "capital maintenance public infrastructure underinvestment",
    "municipal water system capital cost efficiency",
  ],
  "housing_edu_efficiency_band": [
    "zoning reform housing supply elasticity",
    "land use regulation housing production permits",
    "housing voucher versus supply side affordability",
    "school spending increases adult outcomes Jackson",
    "school finance reform long run earnings",
    "school district capital spending student achievement",
  ],
  "prism_two_tier_band": [
    "data envelopment analysis local government efficiency",
    "municipal efficiency DEA benchmarking public services",
    "administrative overhead ratio government expenditure",
    "public expenditure efficiency outcomes frontier",
    "public sector performance spending outcomes IMF",
    "local government service efficiency cost outcome",
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

def crossref_hit(it):
    return {
        "authors": ", ".join(f"{a.get('given','')} {a.get('family','')}".strip()
                             for a in (it.get("author") or [])[:4]) or None,
        "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
        "title": (it.get("title") or [""])[0],
        "venue": (it.get("container-title") or [""])[0],
        "abstract": clean(it.get("abstract") or ""),
        "cited": it.get("is-referenced-by-count", 0),
        "doi": it.get("DOI", ""),
        "url": "https://doi.org/" + it.get("DOI", ""),
    }

def q_crossref(q):
    d = jget("https://api.crossref.org/works?query=" + urllib.parse.quote(q) +
             "&rows=8&select=title,container-title,issued,is-referenced-by-count,DOI,author,abstract,type")
    if "error" in d: return None
    out = []
    for it in d.get("message", {}).get("items", []):
        if it.get("type") not in ("journal-article", "book-chapter", "report-component", "proceedings-article", None, ""):
            continue
        h = crossref_hit(it)
        if h["title"]: out.append(h)
    return out

def q_pm(q):
    s = jget("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=" +
             urllib.parse.quote(q) + "&retmax=5&retmode=json")
    if "error" in s: return None
    ids = s.get("esearchresult", {}).get("idlist", [])
    if not ids: return []
    f = jget("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=" +
             ",".join(ids) + "&retmode=xml") if False else None
    # use raw efetch (returns XML, not JSON)
    try:
        with urllib.request.urlopen(urllib.request.Request(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=" +
            ",".join(ids) + "&retmode=xml", headers=UA), timeout=40) as r:
            root = ET.fromstring(r.read())
    except Exception:
        return []
    out = []
    for art in root.iter("PubmedArticle"):
        auth = ", ".join(" ".join(x.text or "" for x in a if x.tag in ("ForeName", "LastName")).strip()
                         for a in list(art.iter("Author"))[:4])
        j = art.find(".//Journal")
        venue = (j.find("ISOAbbreviation").text if j is not None and j.find("ISOAbbreviation") is not None else "") or ""
        title = art.find(".//ArticleTitle")
        abst = art.find(".//Abstract")
        abst_txt = ("" .join(abst.itertext()) if abst is not None else "")
        year = None
        if j is not None:
            jd = j.find("JournalIssue/PubDate/Year") or j.find("JournalIssue/PubDate/MedlineDate")
            year = int(jd.text[:4]) if jd is not None and jd.text and jd.text[:4].isdigit() else None
        pmid = (art.find(".//PMID").text if art.find(".//PMID") is not None else "")
        out.append({
            "authors": auth or None, "year": year,
            "title": (title.text if title is not None and title.text else "".join(title.itertext()) if title is not None else ""),
            "venue": venue, "abstract": clean(abst_txt),
            "cited": None, "doi": next((a.text for a in art.iter("ArticleId") if a.get("IdType") == "doi"), ""),
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        })
    return out

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
        seen.add(k)
        out.append(h)
    return out[:8]

try:
    done = {json.loads(l)["query"] for l in open(RAW, encoding="utf-8") if l.strip()}
except FileNotFoundError:
    done = {}

with open(RAW, "a", encoding="utf-8") as f:
    for band, qs in QUERIES.items():
        for q in qs:
            if q in done:
                print("skip (done):", q); continue
            cr = q_crossref(q); time.sleep(1.0)
            pm = q_pm(q); time.sleep(1.0)
            ep = q_epmc(q); time.sleep(1.0)
            for route, hits in (("crossref", cr), ("pm_search", pm), ("europepmc_search", ep)):
                if hits is None:
                    rec = {"scan": "BOB-SCAN-20", "band": band, "query": q, "route": route,
                           "error": "api_error", "hits": []}
                else:
                    rec = {"scan": "BOB-SCAN-20", "band": band, "query": q, "route": route,
                           "hits": dedup(hits)}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            print(f"{band}: {q} -> xr={len(cr or [])} pm={len(pm or [])} ep={len(ep or [])}")

print("ALL V19 QUERIES DONE")
