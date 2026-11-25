import json, re
import pymupdf as fitz

# THE ERC-AGENCY-SUMMARY-COLLECTOR: the format = the 'AGENCY EXPENSE BUDGET SUMMARY' =
# the agency-name-head + the unit-code + the 'CURRENT MODIFIED...'-columns = the TOTALS-row.
# THE collect: every 'AGENCY EXPENSE BUDGET SUMMARY'-page = the agency + the adopted-FY26-total-class.
doc = fitz.open('C:/Users/J/AppData/Local/Temp/nyc_adopted_erc.pdf')
results = {}
current = None
for p in range(len(doc)):
    t = doc[p].get_text()
    if 'AGENCY EXPENSE BUDGET SUMMARY' in t.upper():
        lines = [l.strip() for l in t.split('\n') if l.strip()]
        # the agency-name = the line-before-the code-line (the '040 (CONT.)'-class) or-the uppercase-center-line:
        name = None
        code = None
        for i, l in enumerate(lines[:8]):
            if re.match(r'^\d{3,4}\s', l) or re.match(r'^\d{3,4}$', l):
                code = l.split()[0] if l.split() else None
                name = lines[i - 1] if i > 0 else None
                break
        # the fallback = the uppercase-line-2:
        if not name and len(lines) > 2:
            name = lines[2] if lines[1].isdigit() is False else lines[2]
        current = {'pdf_page': p, 'name': name, 'code': code}
        # THE total = the 'TOTAL'-line = the scan (the 'TOTAL EXPENSE...' / 'TOTAL' + the $-row):
        joined = t
        m = re.search(r'TOTAL[^\n]*?\n?,?\s*\(?\$?([0-9][\d,]{6,})', joined)
        if m:
            current['total_candidates'] = [int(m.group(1).replace(',', ''))]
        if name:
            results.setdefault(name, []).append(current)

print('agency-summary-pages:', len(results))
for k, v in list(results.items())[:20]:
    vv = v[0].get('total_candidates') or [None]
    print(f" - {k[:52]:54s} total?{vv[0] if vv[0] else 'null'}")

json.dump(results, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/nyc_erc_agency_summaries_v1.json', 'w', encoding='utf-8'), indent=1)
print('WROTE nyc_erc_agency_summaries_v1.json')
