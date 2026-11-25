import pdfplumber, re

# THE ERC-PLUMBER-TEST: the small-agency-unit-page = the columns = the caught-or-not?
# THE test-subject = the MAYORALTY-summary-page (pdf-p-16) = the pymupdf = the dropped-the-cells:
with pdfplumber.open('C:/Users/J/AppData/Local/Temp/nyc_adopted_erc.pdf') as pdf:
    page = pdf.pages[16]
    # TEST-A: the raw-text-extract:
    t = page.extract_text() or ''
    print(f'raw-text = {len(t)} chars')
    print(t[:400])
    print()
    # TEST-B: the extract_table (the pdfplumber = the the structure-aware!):
    tables = page.extract_tables()
    print(f'tables = {len(tables)}')
    for i, tbl in enumerate(tables[:2]):
        print(f'--- table {i}: {len(tbl)} rows x {len(tbl[0]) if tbl else 0} cols')
        for row in (tbl or [])[:6]:
            print('   ', [str(c)[:14] if c else '' for c in (row or [])])
