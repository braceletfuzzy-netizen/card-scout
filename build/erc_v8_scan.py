import pdfplumber, re

# THE V8-SCAN: the PS-regex-discovery (the the PS-row-labels = the from-a-PS-detail-page): 
# THE sample = the p17 = the had-the 'GROSS OTPS' = the PS-page = the which? THE scan-p15-40 = the find-the PS-rows:
with pdfplumber.open('C:/Users/J/AppData/Local/Temp/nyc_adopted_erc.pdf') as pdf:
    for pno in range(15, 45):
        t = pdf.pages[pno].extract_text() or ''
        hits = re.findall(r'(?:TOTAL|GROSS|NET|LESS)[A-Z ]*PERSONAL[A-Z ]*(?:SERVICE|SERVICES)[A-Z ]*\$?\s*([\d,]{5,})', t)
        if hits:
            print(f'p{pno}: PERSONAL-SERVICE-rows = {hits[:4]}')
            # the context = the surrounding:
            norm = re.sub(r'\s+', ' ', t)
            for m in re.finditer(r'[A-Z ]{4,60}PERSONAL SERVICE[A-Z ]{0,20}\s*\$?\s*([\d,]{5,})', norm):
                print(f'   ctx: {m.group(0)[:80]}')
            break
    else:
        print('the no-PS-rows-p15-45 = the the scan-further:')
