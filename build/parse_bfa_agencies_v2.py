import json, re
import pymupdf as fitz

# THE v2-PARSER: the pymupdf-extract = the REVERSED-column-order (the newest-first: the 2026-Plan = the FIRST-number-row!)
# THE pattern (from-the page-3-sample): the agency-head = the "Agency Summary\nAdopted FY 2026\n($ in Thousands)\n{AGENCY}\n" then-the function-rows + the FUNDING-SUMMARY-block w/ the "Total".
# THE v2 = the per-page scan: every-page containing 'Agency Summary' = the one-agency-block; the agency-name = the 4th-line-class;
# the FY2026 = the FIRST-$-number after-'Budget Function' (the reversed-order!), the FUNDING-Total = the LAST-'Total'-block.

PDF = 'C:/Users/J/AppData/Local/Temp/nyc_adopted_bfa.pdf'
doc = fitz.open(PDF)

agencies = {}
for pno in range(len(doc)):
    text = doc[pno].get_text()
    if 'Agency Summary' not in text:
        continue
    lines = [l.strip() for l in text.split('\n')]
    # the agency-name = the line-after-'($ in Thousands)':
    try:
        idx = lines.index('($ in Thousands)')
        name = lines[idx + 1].strip()
    except (ValueError, IndexError):
        continue
    if not name or name in ('Budget Function Analysis',):
        continue
    # the FY2026-Plan total = the FIRST-$-row after-'Budget Function' ('Budget Function\n$758,531...'):
    fy26 = None
    for j, l in enumerate(lines):
        if l == 'Budget Function' and j + 1 < len(lines):
            nxt = lines[j + 1]
            m = re.match(r'\$([\d,]+)', nxt)
            if m:
                fy26 = int(m.group(1).replace(',', ''))
                break
    # the funding-summary-total = the LAST-'Total'-followed-by-$-row (the city-funds-class):
    fund_total = None
    tspots = [j for j, l in enumerate(lines) if l == 'Total']
    for j in tspots:
        m3 = None
        for k in range(j + 1, min(j + 3, len(lines))):
            m3 = re.match(r'\$([\d,]+)\s*$', lines[k].strip())
            if m3:
                fund_total = int(m3.group(1).replace(',', ''))
                break
    if name and fy26 and name not in agencies:
        agencies[name] = {'fy2026_thousands': fy26, 'funding_total_thousands': fund_total}

print('agencies:', len(agencies))
tot = 0
for name, v in sorted(agencies.items(), key=lambda x: -x[1]['fy2026_thousands']):
    tot += v['fy2026_thousands']
    print(f" - {name[:46]:48s} FY26: {v['fy2026_thousands']:>12,} K")
print()
print('sum-of-agencies (K):', f'{tot:,}')

json.dump(agencies, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/nyc_agencies_bfa_v2.json', 'w', encoding='utf-8'), indent=1)
print('WROTE nyc_agencies_bfa_v2.json')
