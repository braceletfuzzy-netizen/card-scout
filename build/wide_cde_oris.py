# Resolve ORIs for the 15 wide-panel cities from the downloaded state directories
# (state dir = {ST:[...]} keyed by county; agencies have ori/agency_name/agency_type_name)
import json, re

def norm2(s):
    s = (s or '').lower()
    s = re.sub(r'[^a-z0-9]+', '', s)      # drop ALL non-alnum
    if s.startswith('saint'):
        s = 'st' + s[5:]                  # THE law: St./Saint/New-variants merge
    # 'new' variants: 'newyorkcity' handled per-city below if needed
    return s

CITIES = [('PA','Philadelphia','philadelphia'),
          ('AZ','Phoenix','phoenix'),
          ('TX','San Antonio','sanantonio'),
          ('TX','Dallas','dallas'),
          ('CA','San Diego','sandiego'),
          ('FL','Jacksonville','jacksonville'),
          ('TX','Fort Worth','fortworth'),
          ('TX','Austin','austin'),
          ('NC','Charlotte','charlotte'),
          ('OH','Columbus','columbus'),
          ('IN','Indianapolis','indianapolis'),
          ('CA','San Francisco','sanfrancisco'),
          ('WA','Seattle','seattle'),
          ('CO','Denver','denver'),
          ('TN','Nashville','nashville')]

res = {}
for st, city, token in CITIES:
    st_dir = json.load(open(f'_wide/agency_{st}.json'))
    hits = []
    for county, ags in st_dir.items():
        for a in ags:
            nm = a.get('agency_name') or ''
            n = norm2(nm)
            t = token
            ncity = norm2(nm.replace('Police Department', ''))
            if n.startswith(t) or ncity.startswith(t) or t in n.replace('policedepartment','').replace('cityof',''):
                hits.append(a)
    # eyeball list
    res[city] = hits
    print(f'== {city} ({st}): {len(hits)} hits')
    for h in hits[:12]:
        print('   ', h.get('ori'), '|', h.get('agency_type_name'), '|', h.get('agency_name')[:60])
json.dump(res, open('_wide/ori_hits.json','w'), indent=1)
