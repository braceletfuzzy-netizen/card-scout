import json, re
import pymupdf as fitz

# THE v5-collector: the agency-blocks = the multi-page (the name = the on-the-start-page; the NET-TOTAL = the on-the-tail-page). THE two-pass:
# PASS-1: the walk-pages = the track-the current-agency (the header-page = the agency-start) — the pages-between = the same-agency-until-the-next-header.
# PASS-2: the NET-TOTAL-scan-per-page = the assign-to-the current-agency (the max-wins = the not-the sum [the blocks re-print]).
doc = fitz.open('C:/Users/J/AppData/Local/Temp/nyc_adopted_erc.pdf')
results = {}
current = None
for p in range(len(doc)):
    t = doc[p].get_text()
    norm = re.sub(r'\s+', ' ', t)
    if 'AGENCY EXPENSE BUDGET SUMMARY' in norm:
        mname = re.search(r'={5,}\s+([A-Z][A-Z &,/\-\.\'#0-9]{6,70}?)\s+\d{3,4}\s', norm)
        if mname:
            current = mname.group(1).strip()
            if current not in results:
                results[current] = None
    if current:
        mtot = re.search(r'NET TOTAL DEPARTMENT\s+([\d,]{7,})', norm)
        if mtot:
            total = int(mtot.group(1).replace(',', ''))
            if (results[current] or 0) < total:
                results[current] = total

good = {k: v for k, v in results.items() if v}
print('agencies:', len(results), '| with-totals:', len(good))
tot = sum(good.values())
print('sum-of-nets:', f'{tot:,}')
for k, v in sorted(good.items(), key=lambda x: -(x[1] or 0))[:30]:
    print(f' - {k[:58]:60s} {v:>16,}')
nulls = [k for k, v in results.items() if not v]
print()
print('nulls:', len(nulls), nulls[:10])

json.dump(results, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/nyc_erc_net_totals_v5.json', 'w', encoding='utf-8'), indent=1)
print('WROTE nyc_erc_net_totals_v5.json')
