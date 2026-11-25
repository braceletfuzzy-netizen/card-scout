# HEALTH-ACCESS LANE (bob19 blind-spot P1) extract step:
# ACS 5-YEAR table-based-SF (www2 keyless): B27001 (uninsured), B27010 detail, C27007 (Medicaid/means-tested by age x sex)
# City-place grain (6 lane-panel cities + Denver + Kingsport) + companion county grain (grain-law: separate).
import json, csv
from pathlib import Path
B = Path(__file__).parent
H = B/'_bob19_health'

CITIES = {
 '1600000US4748000': 'Memphis',   '1600000US3915000': 'Cincinnati',
 '1600000US2622000': 'Detroit',   '1600000US2965000': 'St. Louis',
 '1600000US3651000': 'NYC',       '1600000US4835000': 'Houston',
 '1600000US0820000': 'Denver',    '1600000US4739560': 'Kingsport',
}
COUNTIES = {
 '0500000US47157':'Shelby County TN (Memphis)','0500000US39061':'Hamilton County OH (Cincinnati)',
 '0500000US26163':'Wayne County MI (Detroit)','0500000US29510':'St. Louis city MO (county-equal)',
 '0500000US36061':'New York County NY','0500000US36047':'Kings County NY','0500000US36005':'Bronx County NY',
 '0500000US36081':'Queens County NY','0500000US36085':'Richmond County NY',
 '0500000US48201':'Harris County TX (Houston)','0500000US08031':'Denver County CO',
 '0500000US47163':'Sullivan County TN (Kingsport)',
}
GEOALL = dict(CITIES); GEOALL.update(COUNTIES)

TABLES = {'b27001':None,'b27010':None,'c27007':None}

def read_dat(path, geo):
    hdr=None; out=None
    with open(path, encoding='utf-8-sig', errors='replace') as fh:
        hdr=fh.readline().strip().split('|')
        for line in fh:
            if not out and line.split('|',1)[0]==geo:
                out=line.rstrip('\r\n').split('|')
                break
    if out is None: return None, hdr
    return dict(zip(hdr,out)), hdr

def E(d,tab,n):
    v=d.get(f'{tab}_E{n:03d}','')
    try: return float(v)
    except: return None

rows=[]
for yr in (2022,2023):
    for geo,name in GEOALL.items():
        r={'geo_id':geo,'name':name,'grain':'city-place' if geo.startswith('16') else 'county',
           'place_city':CITIES.get(geo),'acs_vintage':f'5yr{yr}','window':f'{yr-4}-{yr}'}
        for tab in TABLES:
            d,hdr=read_dat(H/f'acs5y{yr}_{tab}.dat', geo)
            if d is None:
                r[f'{tab}_err']='geo-absent'; continue
            tabU=tab.upper()
            if tab.lower()=='b27001':
                tot=E(d,tabU,1)
                un_m=[E(d,tabU,n) for n in (5,8,11,14,17,20,23,26,29)]
                un_f=[E(d,tabU,n) for n in (33,36,39,42,45,48,51,54,57)]
                ch_tot=E(d,tabU,3)+E(d,tabU,6)+E(d,tabU,31)+E(d,tabU,34)
                ch_un=(E(d,tabU,5) or 0)+(E(d,tabU,8) or 0)+(E(d,tabU,33) or 0)+(E(d,tabU,36) or 0)
                if tot and sum(v or 0 for v in un_m+un_f)>0 and not any(v is None for v in un_m+un_f):
                    r['pop_total']=tot
                    r['uninsured_share_pct']=round(100*sum(un_m+un_f)/tot,2)
                    r['uninsured_child_share_pct']=round(100*ch_un/ch_tot,2) if ch_tot else None
                    r['b27001_shell']='E001 total; uninsured = no-coverage cells E005/8/11/14/17/20/23/26/29 (M) + E033..E057 (F); verified via api.census.gov variables labels'
            elif tab.lower()=='c27007':
                tot=E(d,tabU,1)
                med=[E(d,tabU,n) for n in (4,7,10,14,17,20)]
                ch_tot=E(d,tabU,3)+E(d,tabU,13)
                ch_med=(E(d,tabU,4) or 0)+(E(d,tabU,14) or 0)
                ad_tot=E(d,tabU,6)+E(d,tabU,16)
                ad_med=(E(d,tabU,7) or 0)+(E(d,tabU,17) or 0)
                if tot and not any(v is None for v in med):
                    r['medicaid_share_pct']=round(100*sum(med)/tot,2)
                    r['medicaid_child_share_pct']=round(100*ch_med/ch_tot,2) if ch_tot else None
                    r['medicaid_adult19_64_share_pct']=round(100*ad_med/ad_tot,2) if ad_tot else None
                    r['c27007_shell']='E001 total; Medicaid/means-tested WITH-coverage = E004/7/10 (M) + E014/17/20 (F); verified via api.census.gov variables labels'
            elif tab.lower()=='b27010':
                tot=E(d,tabU,1)
                medonly=[E(d,tabU,n) for n in (7,23,39)]              # Medicaid/means-tested ONLY, one-type
                medcomb=[E(d,tabU,n) for n in (13,29,46,62)]          # Medicare+Medicaid combos
                if tot and not any(v is None for v in medonly+medcomb):
                    r['b27010_medicaid_any_share_pct']=round(100*(sum(medonly)+sum(medcomb))/tot,2)
                    r['b27010_shell']='Medicaid-involved = one-type-only E007/23/39 + Medicare+Medicaid combos E013/29/46/62 (partial combos E014/15/16-class other-combination cells NOT separable = lower-bound flag)'
        rows.append(r)
        print(yr, name, r.get('uninsured_share_pct'), r.get('medicaid_share_pct'), r.get('b27010_medicaid_any_share_pct'))

out={'_record':'bob19_health_access_acs5y_extract_v1','vintages':['acs5y2022','acs5y2023'],
     'table_shell_notes':{'B27001':' uninsured = sum of No-coverage cells','C27007':'Medicaid/means-tested public WITH = E004/7/10+E014/17/20 over E001','B27010':'Medicaid-involved partial (combos limited)'},
     'rows':rows}
(B/'_bob19_health/health_access_acs5y_extract_v1.json').write_text(json.dumps(out,indent=1),encoding='utf-8')
print('saved', len(rows),'rows')
