import json, re
import pymupdf as fitz

# POLYSCOUT #C — THE NYC-BUCKETS-COMPLETE: the ERC = the per-agency-adopted-budgets (the 839-pages = the index = the agencies-with-page-refs [the 'NNNE'-class = the expense-encoding])
# THE v1-scope: the MAJOR-buckets-agencies = the index-pull (the Fire-80E, the Police, the Sanitation, the Parks, the Dep-of-Ed-52E, the HPD, the Aging-139E, the DOT, the DEP-332E, the Health...) = the major-agency-heads = the parse-the per-agency-'Total-Expenses'-line.

doc = fitz.open('C:/Users/J/AppData/Local/Temp/nyc_adopted_erc.pdf')

# THE index = the p10-14 (the expense-page-refs [the 'E'-suffix]):
index_text = ''
for p in range(9, 16):
    index_text += doc[p].get_text()

# THE parse-the index-rows: "Agency-Name....... PAGE-E" pattern
refs = re.findall(r'([A-Z][A-Za-z&,/ \-\.#0-9]{4,60}?)\.{3,}\s*([\d]+)E\s*$', index_text, re.M)
print('index-refs:', len(refs))
majors = [
    ('Police Department', None), ('Fire Department', None),
    ('Sanitation', None), ('Parks', None), ('Education, Department of', None),
    ('Housing Preservation', None), ('Aging, Department for the', None),
    ('Transportation, Department of', None),
    ('Environmental Protection, Department of', None),
    ('Health and Mental Hygiene', None), ('Correction, Department of', None),
    ('Homeless Services', None), ('Social Services', None),
    ('Youth and Community Development', None),
]
picked = {}
for name, (agency_pat, _) in [(n, (n, None)) for n, _ in majors]:
    for ref_name, page in refs:
        if agency_pat.lower().split(',')[0] in ref_name.lower().split(',')[0] or agency_pat.lower().split(' ')[0] in ref_name.lower():
            picked[name] = int(page)
            break

print('picked:', len(picked))
for k, v in picked.items():
    print(f' - {k:44s} -> p{v}E')

json.dump(picked, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/nyc_erc_index_refs_v1.json', 'w', encoding='utf-8'), indent=1)
print('WROTE nyc_erc_index_refs_v1.json')
