import json, re
import pymupdf as fitz

# THE v4-collector: the pymupdf-text = the CR-LF-lanes (the '\r\n') + the columns-run-together (the
# 'NET TOTAL DEPARTMENT            32,673,325,538        $34,029,029' = the single-line = the first-big-number = the dollars).
# THE DOPE: the '\n'-split = the breaks-the-row. THE fix = the whitespace-normalize-then-scan:
doc = fitz.open('C:/Users/J/AppData/Local/Temp/nyc_adopted_erc.pdf')
results = {}
current_name = None
for p in range(len(doc)):
    t = doc[p].get_text()
    if 'AGENCY EXPENSE BUDGET SUMMARY' not in t.upper():
        continue
    norm = re.sub(r'\s+', ' ', t)
    # the name = the text-between-the =====-rules and-the code:
    mname = re.search(r'={5,}\s+([A-Z][A-Z &,/\-\.\'#0-9]{6,70}?)\s+\d{3,4}\s', norm)
    if not mname:
        # fallback = the after-'ADOPTED BUDGET FOR FY 2026'-block:
        mname = re.search(r'={5,}\s+([A-Z][A-Z &,/\-\.\'#0-9]{6,70}?)\s{2,}', norm)
    name = mname.group(1).strip() if mname else None
    # the NET-TOTAL = the dollars-column:
    mtot = re.search(r'NET TOTAL DEPARTMENT\s+([\d,]{7,})', norm)
    total = int(mtot.group(1).replace(',', '')) if mtot else None
    if name:
        key = name.strip()
        if key not in results or (total or 0) > (results[key] or 0):
            results[key] = total

print('agencies:', len(results))
good = {k: v for k, v in results.items() if v}
tot = sum(good.values())
print('sum-of-nets:', f'{tot:,}')
for k, v in sorted(good.items(), key=lambda x: -(x[1] or 0))[:30]:
    print(f' - {k[:58]:60s} {v:>16,}')
nulls = [k for k, v in results.items() if not v]
print()
print('nulls:', len(nulls), nulls[:8])

json.dump(results, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/nyc_erc_net_totals_v4.json', 'w', encoding='utf-8'), indent=1)
print('WROTE nyc_erc_net_totals_v4.json')
