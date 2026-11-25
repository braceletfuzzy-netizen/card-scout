import pdfplumber, re, json

# THE ERC-SWEEP v6 (the pdfplumber = the raw-text-preserve = the regex-parse = the UNITS-DETAIL-route):
# THE STRATEGY-SHIFT: the unit-page-totals = the per-unit-of-appropriation (the 'NNN AGENCY-NAME-OTPS/PS' = the section-rows
# + the 'GROSS OTHER THAN PERSONAL SERVICES $n' + the 'TOTAL PERSONAL SERVICE' etc)... THE honest-v2 = the
# per-UNIT-totals = the the unit-code+name + the the adopted-FY26-total.
doc = pdfplumber.open('C:/Users/J/AppData/Local/Temp/nyc_adopted_erc.pdf')
# THE scan = the first-100-pages (the test-scope = the honest-v1):
units = {}
current_unit = None
text_all = {}
# PASS-1: the read-p1-100 = the collect-the text:
for pno in range(15, 120):
    t = doc.pages[pno].extract_text() or ''
    text_all[pno] = t
    norm = re.sub(r'\s+', ' ', t)
    # the unit-headers = 'NNN NAME-OTPS/PS/...' = the AGENCY OTPS DETAIL / AGENCY PS DETAIL = the unit-sections:
    m = re.findall(r'(\d{3,4}) ([A-Z][A-Z0-9 &,/\-\.#]{8,60}?) (?:OTPS|PS|DETAIL)', norm)
    for code, name in m:
        key = f'{code} {name.strip()}'
        if key not in units:
            units[key] = {'first_page': pno}
print('units-found-15-120:', len(units))
for k in list(units)[:30]:
    print(' -', k)
print()

# THE TOTALS-LANE (the v2 = the what-rows = the total-able?):
# 'TOTAL PERSONAL SERVICE', 'GROSS OTHER THAN PERSONAL SERVICES', 'LESS INTRA-CITY SALES', 'TOTAL EXPENDITURES':
sample = text_all.get(17, '') + text_all.get(18, '')
totals_pattern = re.findall(r'(TOTAL [A-Z ]{4,40}|GROSS [A-Z ]{8,50}|NET TOTAL [A-Z ]{4,40})\s*\$?\s*([\d,]{5,})', sample)
print('totals-pattern-sample:')
for name, val in totals_pattern[:12]:
    print(f' - {name[:44]:46s} {val}')
