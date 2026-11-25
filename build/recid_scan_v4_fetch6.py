import json, time, urllib.request, re, html

# Phase 6: pull specifics - RAND page (Davis figure), full Prison Journal abstract
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")

# 1) RAND RR-266 / RB-9728 landing page for the 13-pp figure
for url in ["https://www.rand.org/pubs/research_reports/RR266.html", "https://www.rand.org/pubs/research_briefs/RB9728.html"]:
    try:
        t = fetch(url)
        txt = re.sub(r"<[^>]+>", " ", t)
        txt = re.sub(r"\s+", " ", html.unescape(txt))
        # find snippet with "percentage point"
        hits = re.findall(r"[^.]{0,300}percentage point[^.]{0,120}\.", txt)
        print(f"--- {url} -> {len(t)} bytes")
        for h in hits[:3]:
            print("   *", h.strip()[:320])
        m = re.search(r"[^.]{0,250}(?:13\spercent|13 percentage)[^.]{0,150}", txt)
        if m: print("   MATCH:", m.group(0).strip()[:350])
    except Exception as e:
        print(f"--- {url} FAIL {e}")
    time.sleep(1.2)

# 2) full Prison Journal abstract from Crossref
import json as js
req = urllib.request.Request("https://api.crossref.org/works/10.1177/0032885514548009",
                             headers={"User-Agent": "PolyScout/1.0 (mailto:research-ops@example.org)"})
m = js.loads(urllib.request.urlopen(req, timeout=30).read())["message"]
ab = m.get("abstract", "")
print("\nPrisonJ2014 FULL abstract:", html.unescape(re.sub(r"<[^>]+>", "", ab))[:1200])

# 3) full Kim2026 abstract
req = urllib.request.Request("https://api.crossref.org/works/10.65150/ep-jsshrs/v2e7/2026-29",
                             headers={"User-Agent": "PolyScout/1.0 (mailto:research-ops@example.org)"})
m = js.loads(urllib.request.urlopen(req, timeout=30).read())["message"]
ab = m.get("abstract", "")
print("\nKim2026 FULL abstract:", html.unescape(re.sub(r"<[^>]+>", "", ab))[:1600])
