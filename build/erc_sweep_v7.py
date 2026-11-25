import pdfplumber, re, json
from collections import defaultdict

# THE ERC-SWEEP v7 = THE FINAL-COLLECTOR (the unit-rows + the GROSS-OTPS-totals = the per-unit-dollar):
# THE structure-discovered: 'NNN NAME-OTPS' → the section = the
# 'GROSS OTHER THAN PERSONAL SERVICES $n' = the unit-total-OTPS-class.
# ALSO = the PS-side ('TOTAL PERSONAL SERVICE' [Likely]).
doc = pdfplumber.open('C:/Users/J/AppData/Local/Temp/nyc_adopted_erc.pdf')
units = {}
current = None
for pno in range(15, 838):
    t = doc.pages[pno].extract_text() or ''
    norm = re.sub(r'\s+', ' ', t)
    m = re.search(r'(\d{3,4}) ([A-Z][A-Z0-9 &,/\-\.#\u2019]{8,60}?) (OTPS|PS) AGENCY', norm)
    if m:
        code, name, kind = m.group(1), m.group(2).strip(), m.group(3)
        current = f'{code} {name}'
        units.setdefault(current, {'otps': None, 'ps': None, 'pages': []})
        units[current]['pages'].append(pno)
        units[current]['kind'] = kind
    if current:
        mg = re.search(r'GROSS OTHER THAN PERSONAL SERVICES\s+\$?\s*([\d,]{4,})', norm)
        if mg and units[current]['otps'] is None:
            units[current]['otps'] = int(mg.group(1).replace(',', ''))
        mps = re.search(r'TOTAL PERSONAL SERVICE\s+\$?\s*([\d,]{4,})', norm)
        if mps and units[current]['ps'] is None:
            units[current]['ps'] = int(mps.group(1).replace(',', ''))

# THE summary (the v7):
with_tot = {k: v for k, v in units.items() if v['otps'] or v['ps']}
print('units-total:', len(units), '| with-dollar-totals:', len(with_tot))
otps_sum = sum(v['otps'] or 0 for v in with_tot.values())
ps_sum = sum(v['ps'] or 0 for v in with_tot.values())
print(f'OTPS-sum: {otps_sum:,}')
print(f'PS-sum: {ps_sum:,}')
top = sorted(with_tot.items(), key=lambda x: -((x[1]['otps'] or 0) + (x[1]['ps'] or 0)))
for k, v in top[:25]:
    print(f" - {k[:52]:54s} OTPS:{str(v['otps'] or '-'):>12} PS:{str(v['ps'] or '-'):>14}")

json.dump(units, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/nyc_erc_units_v7.json', 'w', encoding='utf-8'), indent=1)
print('WROTE nyc_erc_units_v7.json')
