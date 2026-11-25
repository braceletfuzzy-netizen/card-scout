import json, urllib.request, re

# peer-review-scan runner — keyless Semantic Scholar first (the BOB-lane pattern)
# Usage: python peer_review_scan.py "search terms" [limit]
# Writes rows to build/peer_review_scan_v1.jsonl (append); prints title/venue/year/citations.
# NEVER fabricate: only rows returned by the API are written. Secondhand-tag anything relayed.
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'For You', 'PolyScout', 'build')
os.makedirs(B, exist_ok=True)
OUT = os.path.join(B, 'peer_review_scan_v1.jsonl')

BASE = 'https://api.semanticscholar.org/graph/v1/paper/search'
FIELDS = 'title,abstract,year,venue,citationCount,externalIds'

def scan(thread, limit=10):
    params = f'?query={urllib.parse.quote(thread)}&fields={FIELDS}&limit={limit}'
    req = urllib.request.Request(BASE + params, headers={'User-Agent': 'PolyScoutResearch/1.0 (civic study; contact: cardscout.pro)'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        d = json.loads(resp.read())
    papers = d.get('data', [])
    out = []
    for p in papers:
        if not p.get('abstract'):
            continue  # never fabricate: skip papers without a loadable abstract
        row = {'thread': thread, 'title': p.get('title'), 'year': p.get('year'),
               'venue': p.get('venue'), 'citation_count': p.get('citationCount'),
               'abstract_excerpt': p['abstract'][:600], 'confidence': 'cited-in-abstract',
               'paperId': p.get('paperId')}
        out.append(row)
    with open(OUT, 'a', encoding='utf-8') as f:
        for r in out:
            f.write(json.dumps(r) + '\n')
    print(f'[{thread}] {len(out)} rows appended to {OUT}')
    for r in out:
        print(f"  - ({r.get('year')}) {r['title']} | cites={r['citation_count']} | {r['venue']}")
    return out

if __name__ == '__main__':
    import os, urllib.parse
    threads = sys.argv[1] if len(sys.argv) > 1 else (
        'mental health spending crime rates state budget',
        'deinstitutionalization crime Levitt',
        'Medicaid expansion crime rates difference in differences',
        'police staffing crime reverse causation ',
        'suicide homicide rates correlation structural',
    )
    if isinstance(threads, str):
        threads = [threads]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    for t in threads:
        try:
            scan(t, limit)
        except Exception as e:
            print(f'[{t}] ERROR: {e}')
