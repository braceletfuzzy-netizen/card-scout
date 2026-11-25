import json, re, statistics
from collections import defaultdict
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

def norm(c):
    c = (c or '').strip()
    c = c.replace('St. Louis', 'STLOUIS')
    c = c.replace('St Louis', 'STLOUIS')
    c = {'NYC': 'NYC', 'New York City': 'NYC', 'New York': 'NYC'}.get(c, c)
    return c.title().replace('Stlouis', 'St. Louis').replace('Kansas City', 'Kansas City')

# THE the crimes = the merge-all-3:
murders = {}
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl', 'crime_series_wave2_holefill.jsonl', 'crime_wide.jsonl', 'crime_wide_b.jsonl', 'crime_wide_c.jsonl'):
    try:
        for l in open(B + f, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l)
            c = r.get('city')
            if not c:
                continue
            c = c.strip()
            cc = {'New York City': 'NYC'}.get(c, c)
            y = r.get('year')
            if not y:
                m = re.search(r'((19|20)\d\d)', str(r.get('era_or_year') or r.get('era') or ''))
                y = int(m.group(0)) if m else None
            if not y or r.get('murders') is None:
                continue
            mur = (cc.title() if cc not in ('NYC',) else 'NYC', int(y))
            # the take = the max (the the dedupe = the same-double-annual-class):
            if mur not in murders or murders[mur] < r['murders']:
                murders[mur] = r['murders']
    except FileNotFoundError:
        pass
print('the murders-cities:', sorted(set(c for c, y in murders.keys())))
print('the murders-count:', len(murders))
json.dump({f'{c}|{y}': m for (c, y), m in murders.items()}, open(B + 'murders_all_v1.json', 'w', encoding='utf-8'), indent=1)
