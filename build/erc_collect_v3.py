import json, re
import pymupdf as fitz

# THE v3-COLLECTOR: the 'AGENCY EXPENSE BUDGET SUMMARY'-pages = the NET-TOTAL-DEPARTMENT = the FY26-adopted-total
# (the DOE-sample: the 'NET TOTAL DEPARTMENT  32,673,325,538  $34,029,029' = the first-big-number = the dollars!)
doc = fitz.open('C:/Users/J/AppData/Local/Temp/nyc_adopted_erc.pdf')
results = {}
for p in range(len(doc)):
    t = doc[p].get_text()
    if 'AGENCY EXPENSE BUDGET SUMMARY' not in t.upper():
        continue
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    name = None
    for i, l in enumerate(lines[:10]):
        if l.upper().startswith('AGENCY EXPENSE BUDGET SUMMARY'):
            # the name = the nearest-preceding non-rule-line:
            j = i - 1
            while j >= 0:
                cand = lines[j] if lines[j] != lines[i] else None
                if cand and '====' not in cand and not re.match(r'^\d{3,4}', cand) and len(cand) > 3:
                    name = cand
                    break
                j -= 1
            break
    if not name:
        continue
    # the NET-TOTAL = the scan:
    m = re.search(r'NET TOTAL DEPARTMENT\s+([\d,]{7,})', t)
    total = int(m.group(1).replace(',', '')) if m else None
    key = name.upper().strip(' -')
    if key not in results or (total or 0) > (results[key] or 0):
        results[key] = total

print('agencies:', len(results))
tot = sum(v for v in results.values() if v)
print('sum:', f'{tot:,}')
for k, v in sorted(results.items(), key=lambda x: -(x[1] or 0))[:25]:
    print(f' - {k[:56]:58s} {v if v else "null":>16}')

json.dump(results, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/nyc_erc_net_totals_v3.json', 'w', encoding='utf-8'), indent=1)
print('WROTE nyc_erc_net_totals_v3.json')
