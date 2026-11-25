import pymupdf as fitz, re

# THE CINCINNATI-TOTAL-HUNT (the regex-fixed = the the no-quantifier-bugs!):
doc = fitz.open('C:/Users/J/AppData/Local/Temp/cincinnati_fy26_brief.pdf')
found = False
for pno in range(len(doc)):
    t = re.sub(r'\s+', ' ', doc[pno].get_text())
    # the all-funds-total-class = the "$1,4xx,xxx,xxx"-pattern:
    for m in re.finditer(r'\$1,[3-5][0-9]{2},[0-9]{3},[0-9]{3}', t):
        ctx = t[max(0, m.start()-70):m.start()+30]
        print(f'p{pno}: {m.group(0)} | ctx: {ctx[-90:]}')
        found = True
if not found:
    print('the no-$1.4B-pattern-in-the-brief; the biennial-vol = the deeper')
