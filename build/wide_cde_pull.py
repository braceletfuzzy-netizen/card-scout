# Pull HOM (murder) monthly counts 2011-2025 for all 15 city ORIs via keyless CDE summarizer
# + PE (officers male+female) 2011-2025. Cache per ORI in _wide/hom_<ORI>.json / pe_<ORI>.json
import json, os, time, urllib.request

ORI = json.load(open('_wide/ori_primary.json'))
W = '_wide'
os.makedirs(W, exist_ok=True)

def fetch(url, tries=3):
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(url, timeout=90).read())
        except Exception as e:
            if i == tries-1:
                print('FAIL', url[:80], str(e)[:120])
                return None
            time.sleep(3)

for city, ori in ORI.items():
    # HOM per year 2011..2025
    hom_cache = f'{W}/hom_{ori}.json'
    if os.path.exists(hom_cache):
        print('skip hom', ori); hom = json.load(open(hom_cache))
    else:
        hom = {}
        for y in range(2011, 2026):
            url = f'https://cde.ucr.cjis.gov/LATEST/summarized/agency/{ori}/HOM?from=01-{y}&to=12-{y}'
            d = fetch(url)
            hom[y] = d
            time.sleep(0.25)
        json.dump(hom, open(hom_cache, 'w'))
        print('saved hom', city, ori)
    pe_cache = f'{W}/pe_{ori}.json'
    if os.path.exists(pe_cache):
        print('skip pe', ori)
    else:
        url = f'https://cde.ucr.cjis.gov/LATEST/pe/agency/{ori}?from=2011&to=2025'
        d = fetch(url)
        json.dump(d if d else {}, open(pe_cache, 'w'))
        print('saved pe', city, ori, 'ok' if d else 'EMPTY')
    time.sleep(0.2)
print('ALL DONE')
