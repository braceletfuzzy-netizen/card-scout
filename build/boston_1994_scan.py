import pymupdf as fitz, re

# 1994-PROOF-SCAN (the caret-class-line-names = the ASCII-safe!):
doc = fitz.open('C:/Users/J/AppData/Local/Temp/boston_pb_1994.pdf')
CARE = re.compile(r'(libraries|parks|recreation|schools|health|human services|youth|elderly|child)', re.I)
CAGE = re.compile(r'(police|fire|court|sheriff|jail|correction)', re.I)
NAME = re.compile(r'^([A-Za-z][A-Za-z ,\-]{4,44})')
VAL = re.compile(r'\$?\s*([\d]{6,12})')
hits = []
for pn in range(min(100, len(doc))):
    t = doc[pn].get_text()
    for line in t.split('\n'):
        nm = NAME.match(line.strip())
        if nm:
            vm = VAL.search(line.strip())
            if vm:
                name = nm.group(1).strip()
                val = int(vm.group(1).replace(',', ''))
                if val > 200000:
                    nl = name.lower()
                    if CAGE.search(nl):
                        hits.append((pn, name, val, 'cage'))
                    elif CARE.search(nl):
                        hits.append((pn, name, val, 'care'))
for h in hits[:32]:
    print(' *', h)
