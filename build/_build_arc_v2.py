
import json, re, csv, collections, os

P = r'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build'
TMP = r'C:/Users/J/AppData/Local/Temp'

CARE = {
 'Boston Public Schools':('Boston Public Schools',),
 'Charter School Tuition':('Charter School Tuition',),
 'Library Department':('Library Department',),
 'Parks and Recreation Department':('Parks & Recreation Department',),
 'BCYF - Community Centers':('Boston Center for Youth & Families',),
 'Office of Human Services':('Office of Human Services','Office of Health & Human Services'),
 'Elderly Commission':('Age Strong',),
 "Veterans Services Department":('Boston VETS',),
 'Health and Hospitals Department':('Public Health Commission',),
 'Commission For Persons W/Disabilities':('Commission For Persons W/Disabilities',),
 "Neighborhood/Housing (NHD, MOH)":('Neighborhood Development',"Mayor's Office of Housing"),
 'Office of Arts & Culture':('Office of Arts & Culture',),
 'Office for Immigrant Advancement':('Office for Immigrant Advancement',),
 'Office of Language & Communications Access':('Office of Language & Communications Access',),
 'Youth Fund':('Youth Engagement & Employment','Youth Employment and Opportunity'),
 'Office of Food Justice':('Office of Food Justice',),
 'Human Right Commission':('Human Right Commission',),
 'Office of Equity/Resiliency/Diversity':('Office of Equity','Office of Resiliency & Racial Equity','Office of Diversity'),
 'Black Male Advancement':('Black Male Advancement',),
 'LGBTQ+ Advancement':('LGBTQ+ Advancement','Office of LGBTQIA2S+ Advancement'),
 "Women's Advancement":("Women's Advancement",),
 'Fair Housing & Equity':('Fair Housing & Equity',),
 'Office of Historic Preservation':('Office of Historic Preservation',),
 'Environment Department (open space)':('Environment Department',),
}
CAGE = {
 'Police Department':('Police Department',),
 "Suffolk County Sheriff's Department":('Suffolk County Sheriff Dept',),
 'Execution of Courts':('Execution of Courts',),
 'Emergency Management':('Emergency Management',),
 'OPAT':('OPAT Cabinet','Office of Police Accountability & Transparency'),
}
FIRE = 'Fire Department'

def parse_file(f):
    rows=[r for r in list(csv.reader(open(f,encoding='utf-8')))[1:] if r[0] and r[0]!='Totals' and all(x!='' for x in r)]
    out=collections.defaultdict(lambda: collections.defaultdict(float))
    for dep,cat,y,a in rows:
        out[y][dep]+=float(a.replace(',',''))
    return dict(out)

vintages={f:parse_file(os.path.join(TMP,f'bos_{f}_dept.csv')) for f in ('fy22','fy23','fy24','fy25')}

def lane(y, mapping):
    for v in ('fy25','fy24','fy23','fy22'):
        d=vintages[v].get(y)
        if d:
            tot=0; det={}
            for label,names in mapping.items():
                s=sum(d.get(n,0.0) for n in names)
                if s: det[label]=round(s); tot+=s
            return round(tot), {k:v for k,v in det.items()}, v
    return None,None,None

ASSET_URL='https://patterns.boston.gov/assets/budget/{v}/spending_by_departments.csv (reached via boston.gov/departments/budget/{v}-operating-budget page config)'
def bos_row(FY):
    care,d_c,src_c=lane(FY,CARE)
    cage,d_g,src_g=lane(FY,CAGE)
    fire=round(vintages[src_g][FY].get(FIRE,0.0)) if src_g else None
    return {
      'city':'Boston','year':int(FY[2:]),
      'care_usd_total':care,'cage_usd_total':cage,'fire_flagged_usd':fire,
      'rows_care_top':d_c,'rows_cage_top':d_g,
      'source_refs':[ASSET_URL.format(v=src_g),'official City of Boston published chart data (cob_drupal patterns.boston.gov asset), retrieved 2026-11-22'],
      'data_quality':'Certain-as-published (city-hosted dept x category x FY CSV; dept sums recomputed)',
      'notes':'GF-style operating budget by dept as published on the FY budget pages. Basis: appropriations incl. BPS + Charter Tuition in care lane; Police+Sheriff+courts+EM+OPAT in cage lane; Fire flagged separately, excluded from cage (same convention as Boston care_arc v1 rows).',
      'honest_gaps':['Chart asset contains 4 FYs; earlier FYs restated in newer vintages (FY22 csv FY19-22 vs FY24 csv FY21-24 differ modestly: restatement). This row uses the NEWEST available vintage per year.',
                     'Care lane here includes BPS (school operating) because the Boston series 1993-2001 rows also counted Education-adjacent care in the flip analysis - the FY99/FY01 books were Volume II schools-complete. Noted, not reconciled to GF-only.'],
    }

rows=[]
rows.append(bos_row('FY19'))
rows.append(bos_row('FY20'))
rows.append(bos_row('FY21'))
rows.append(bos_row('FY22'))

# ---- HOUSTON: carry from nola_houston_pair_v1.jsonl verbatim (2004,2005,2006,2007,2022,2024,2026) ----
def ny(v):
    m=re.search(r'(19|20)\d\d', str(v)); return int(m.group(0)) if m else None
pair_path=os.path.join(P,'nola_houston_pair_v1.jsonl')
hou_carry=0
seen_hou = set()
for line in open(pair_path,encoding='utf-8'):
    if line.strip():
        r=json.loads(line)
        if r.get('city')=='Houston' and r.get('care_usd_total') is not None:
            y=ny(r.get('era_or_year'))
            if y is None or y in seen_hou: continue
            seen_hou.add(y)
            rows.append({
              'city':'Houston','year':y,
              'care_usd_total':r['care_usd_total'],'cage_usd_total':r['cage_usd_total'],
              'fire_flagged_usd':r.get('fire_flagged_usd'),
              'rows_care_top':r.get('rows_care_top',{'carry':'verbatim from pair run'}),
              'rows_cage_top':r.get('rows_cage_top',{'carry':'verbatim from pair run'}),
              'source_refs':list(r.get('source_refs') or ['nola_houston_pair_v1.jsonl']),
              'data_quality':r.get('data_quality','carried verbatim'),
              'notes':'CARRIED VERBATIM from nola_houston_pair_v1.jsonl (no re-fetch). '+str(r.get('notes',''))[:400],
              'honest_gaps':list(r.get('honest_gaps') or []),
            })
            hou_carry+=1

# ---- DETROIT 2012: carry from detroit_care_cage_series_v1.jsonl with verified live source ----
det_path=os.path.join(P,'detroit_care_cage_series_v1.jsonl')
for line in open(det_path,encoding='utf-8'):
    if line.strip():
        r=json.loads(line)
        if '2012' in str(r.get('era_or_year')):
            rows.append({
              'city':'Detroit','year':2012,
              'care_usd_total':r['care_usd_total'],'cage_usd_total':r['cage_usd_total'],
              'fire_flagged_usd':r.get('fire_flagged_usd'),
              'rows_care_top':{'carry':'see detroit_care_cage_series_v1.jsonl: '+str(r.get('rows_care_top'))[:300]},
              'rows_cage_top':{'carry':'see detroit_care_cage_series_v1.jsonl: '+str(r.get('rows_cage_top'))[:300]},
              'source_refs':list(r.get('source_refs') or []),
              'data_quality':r.get('data_quality'),
              'notes':'CARRIED from detroit_care_cage_series_v1.jsonl; source URL re-verified live (HTTP 200) on 2026-11-22. '+str(r.get('notes','')),
              'honest_gaps':list(r.get('honest_gaps') or []),
            })
            break

out_path=os.path.join(P,'care_arc_extension_v2.jsonl')
with open(out_path,'w',encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False)+'\n')
print('rows written:', len(rows), '| houston carries:', hou_carry)
for r in rows:
    print(r['city'], r['year'], 'care', r['care_usd_total'], 'cage', r['cage_usd_total'], 'fire', r['fire_flagged_usd'])
