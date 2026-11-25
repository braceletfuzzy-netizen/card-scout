import pymupdf as fitz
import re as _re

# 1991/1994 dollar-line table scan (inline-quoted patterns to dodge shell-regex traps)
CARE = _re.compile(r'librar|park|recreation|school|health|human service|youth|elderly|child', _re.I)
CAGE = _re.compile(r'police|fire|court|sheriff|jail|correction', _re.I)
NAME = _re.compile(r'^[A-Za-z][A-Za-z ,\-/]{3,44}')
VAL = _re.compile(r'\$? ?([\d]{1,3},[\d]{3},[\d]{3}|[\d]{7,12})')

for y in (1991, 1994):
    doc = fitz.open(f'C:/Users/J/AppData/Local/Temp/boston_pb_{y}.pdf')
    hits = 0
    sample = []
    for pn in range(len(doc)):
        t = doc[pn].get_text()
        if len(t) < 300:
            continue
        for line in t.split('\n'):
            line = line.strip()
            if 5 < len(line) < 60 and NAME.match(line):
                vm = VAL.search(line)
                if vm:
                    val = int(vm.group(1).replace(',', ''))
                    if val > 500000:
                        hits += 1
                        if len(sample) < 6:
                            sample.append((pn, line[:70]))
    print(f'{y}: dept-dollar-lines={hits}')
    for s in sample:
        print('   *', s)
