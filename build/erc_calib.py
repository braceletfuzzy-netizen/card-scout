import json, re
import pymupdf as fitz

# THE ERC-PER-AGENCY-TOTALS: the page-refs = the 70E-class = the printed-page-no = the pdf-index-offset (the printed-E-pages = the pdf-p+11-class from-the p10-index? THE detect: the p70E = the pdf-p~81): the calibrate-via-the sample:
doc = fitz.open('C:/Users/J/AppData/Local/Temp/nyc_adopted_erc.pdf')
# THE calibrate: find-'POLICE DEPARTMENT'-head-page:
police_page = None
for p in range(60, 95):
    t = doc[p].get_text()
    if 'POLICE DEPARTMENT' in t.upper()[:200]:
        police_page = p
        break
print('police-page (pdf-index):', police_page)
if police_page:
    t = doc[police_page].get_text()
    print(t[:600])
