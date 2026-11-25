import json
import pymupdf as fitz

# POLYSCOUT #1 — THE NYC-AGENCY-LOOP v1: the BFA = the per-agency-parse via pymupdf
# THE BFA = the Budget-Function-Analysis-Adopted-FY2026 = the 1.4MB = the per-agency-summaries (the each = the
# "# {Agency-Name}" -head + the summary-table with-the FY2026-Plan-Total + the Funding-Summary).
PDF = 'C:/Users/J/AppData/Local/Temp/nyc_adopted_bfa.pdf'

doc = fitz.open(PDF)
print('pages:', len(doc))

# THE agency-heads = the font-size-class (the headings): the v1 = the text-scan (the "Budget Function Analysis Agency Summary" + the follow-line = the agency-name):
text_by_page = []
for page in doc:
    text_by_page.append(page.get_text())
full = '\n'.join(text_by_page)

# THE summary-tables = the pattern: "Agency Summary Adopted FY 2026 ($ in Thousands)" — the preceding-line = the agency-name
agencies = {}
import re
# PYMUPDF = the extraction-order-varies; the block-scan = the line-based:
lines = full.split('\n')
i = 0
while i < len(lines):
    line = lines[i].strip()
    if 'Agency Summary' in line and 'Adopted FY 2026' in line:
        # the agency-name = the nearest-preceding non-empty-line (the scan-back):
        j = i - 1
        name = None
        while j >= 0:
            cand = lines[j].strip()
            if cand and 'Agency Summary' not in cand and 'Adopted FY' not in cand and len(cand) > 2 and not cand.startswith('$'):
                name = cand
                break
            j -= 1
        # the FY2026-Plan-total = the scan-ahead-for-the "Total|$n,n,nnn" pattern (the 5-col-row = the 2022..2026):
        k = i
        total = None
        cnt = 0
        while k < min(i + 12, len(lines)) and total is None:
            cand2 = lines[k].strip()
            if cand2.startswith('Total') or cand2 == 'Total':
                # the next-non-empty = the 5-numbers-row:
                m = k + 1
                while m < min(k + 6, len(lines)):
                    nxt = lines[m].strip()
                    if nxt and nxt[0].isdigit() or (nxt.startswith('$')):
                        total = nxt
                        break
                    m += 1
            k += 1
        if name and total and name not in agencies:
            agencies[name] = total
        i += 1
    i += 1

print('agencies-captured:', len(agencies))
for name, total in list(agencies.items())[:40]:
    print(f' - {name[:52]:54s} {total[:34]}')

json.dump(agencies, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/nyc_agencies_bfa_v1.json', 'w', encoding='utf-8'), indent=1)
print('WROTE nyc_agencies_bfa_v1.json')
