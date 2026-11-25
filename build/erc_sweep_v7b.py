import pdfplumber, re, json
from collections import defaultdict

# THE ERC-SWEEP v7-B (the timeout = the 838-pages = the pdfplumber = the slow!): THE CHUNKED-RUN:
# THE chunk-mechanism: the page-range = the args (the chunks = the 0-1-per-run = the the jsonl-append!)
import sys
START, END = int(sys.argv[1]), int(sys.argv[2])
OUT = 'C:/Users/J/Documents/LLM/cardscout-2.0/data_lake/gold/nyc_erc_units.jsonl'
doc = pdfplumber.open('C:/Users/J/AppData/Local/Temp/nyc_adopted_erc.pdf')
units = {}
current = None
for pno in range(START, min(END, len(doc.pages))):
    t = doc.pages[pno].extract_text() or ''
    norm = re.sub(r'\s+', ' ', t)
    m = re.search(r'(\d{3,4}) ([A-Z][A-Z0-9 &,/\-\.#\u2019]{8,60}?) (OTPS|PS) AGENCY', norm)
    if m:
        code, name, kind = m.group(1), m.group(2).strip(), m.group(3)
        current = f'{code} {name}'
        units.setdefault(current, {'otps': None, 'ps': None, 'kind': kind})
    if current:
        mg = re.search(r'GROSS OTHER THAN PERSONAL SERVICES\s+\$?\s*([\d,]{4,})', norm)
        if mg and units[current].get('otps') is None:
            units[current]['otps'] = int(mg.group(1).replace(',', ''))
        mps = re.search(r'TOTAL PERSONAL SERVICE\s+\$?\s*([\d,]{4,})', norm)
        if mps and units[current].get('ps') is None:
            units[current]['ps'] = int(mps.group(1).replace(',', ''))
with open(OUT, 'a', encoding='utf-8') as f:
    f.write(json.dumps({'chunk': [START, END], 'units': units}) + '\n')
n_tot = sum(1 for v in units.values() if v['otps'] or v['ps'])
print(f'chunk-{START}-{END}: units={len(units)} with-totals={n_tot}')
