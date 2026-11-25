import json, re
import pymupdf as fitz

# THE v2-collector: the total = the 'TOTAL EXPENSES'-row per-agency-section + the ALL-FUNDS-column (the FY26-total). THE honest-v2:
# the sample = the DOE = the null-v1 → the read-the-DOE-section = the format-check:
doc = fitz.open('C:/Users/J/AppData/Local/Temp/nyc_adopted_erc.pdf')
t68 = doc[68].get_text()
lines = t68.split('\n')
print('==p68-lines==')
i_tot = [i for i, l in enumerate(lines) if 'TOTAL' in l.upper()]
for i in i_tot[:6]:
    print(f' {i}: {lines[i][:70]!r}' + (f' | next: {lines[i+1][:60]!r}' if i + 1 < len(lines) else ''))
