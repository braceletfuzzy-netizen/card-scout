# _pit_lane_pull.py — PIT-HOMELESSNESS LANE (bob19 output-blind-spot P1)
# HUD CoC PopSub reports, keyless files.hudexchange.info/reports/published/CoC_PopSub_CoC_<coc>-<yr>_<st>_<yr>.pdf
# Grain: CoC (city-of-care). 2010-2025 annual. Static-stock law: a point-in-time count of a january night,
# NEVER read as a flow. City-key map: CoC number -> city; county companions noted per grain-law.
import urllib.request, pymupdf, re, json, math, time
from pathlib import Path
B = Path(r"C:\Users\J\Documents\LLM\cardscout-2.0\For You\PolyScout\build")
O = B/'_bob19_outputs'; O.mkdir(exist_ok=True)
R = O/'_pit_raw'; R.mkdir(exist_ok=True)

UA = {'User-Agent':'Mozilla/5.0'}
def fetch(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
            return r.read()
    except Exception:
        return None

# the-8-city-key map (6 founder-panel + Denver + Kingsport). County-companion grain noted.
COC_MAP = {
 'TN-501': {'city':'Memphis',   'state':'TN', 'coc_name':'Memphis/Shelby County CoC'},
 'MI-501': {'city':'Detroit',   'state':'MI', 'coc_name':'Detroit CoC'},
 'MO-501': {'city':'St. Louis', 'state':'MO', 'coc_name':'St. Louis City CoC'},
 'NY-600': {'city':'NYC',       'state':'NY', 'coc_name':'New York City CoC'},
 'TX-700': {'city':'Houston',   'state':'TX', 'coc_name':'Houston, Pasadena, Conroe/Harris, Fort Bend, Montgomery Counties CoC'},
 'OH-500': {'city':'Cincinnati','state':'OH', 'coc_name':'Cincinnati/Hamilton County CoC'},
 'CO-503': {'city':'Denver',    'state':'CO', 'coc_name':'Metropolitan Denver CoC'},
 'TN-509': {'city':'Kingsport','state':'TN', 'coc_name':'Appalachian Regional CoC (balance-of-state, includes Sullivan County)'},
}
YEARS = list(range(2010, 2026))

def parse_pit(b):
    d = pymupdf.open(stream=b, filetype='pdf')
    for page in d:
        w = page.get_text('words')
        rows = {}
        for x0,y0,x1,y1,txt,*rest in w:
            rows.setdefault(round(y0), []).append((x0, txt))
        out = {}; coc_id = None; coc_name = None; pit_date = None
        for y in sorted(rows.keys()):
            items = [t for x,t in sorted(rows[y])]
            s = ' '.join(items)
            m = re.match(r'^(\S+-\d{3,4})\s+(.+CoC)$', s)
            if m:
                coc_id, coc_name = m.group(1), m.group(2)
            ms2 = re.match(r'^CoC\s+Name:\s*(.+)$', s)
            if ms2 and coc_name is None: coc_name = ms2.group(1)
            if s.startswith('Point-in') and 'Date' in s:
                pit_date = s.split('Date:')[-1].strip()
            if s.startswith('Total Homeless Persons in Households'):
                nums = items[len('Total Homeless Persons in Households'.split()):]
                try:
                    vals = [float(n.replace(',','')) for n in nums[:4]]
                    if len(vals)==4 and not out:
                        es, th, uns, tot = vals
                        out = {'es':es,'th':th,'unsheltered':uns,'total':tot,'cols':'ES|TH|Unsheltered|Total (pre-2012 household-schema)'}
                except Exception:
                    pass
            if s.startswith('Total Homeless Persons'):
                nums = items[3:]
                try:
                    vals = [float(n.replace(',','')) if n not in ('—','–','-') else 0.0 for n in nums[:4]]
                    if len(vals)==4:
                        es, th, uns, tot = vals
                        out = {'es':es,'th':th,'unsheltered':uns,'total':tot,'cols':'ES|TH(SH folded)|Unsheltered|Total (dash=not-reported as 0 in-place)'}
                except Exception:
                    pass
        if out: return coc_id, coc_name, pit_date, out
    return None, None, None, {}

rows = []
errors = []
for coc, meta in COC_MAP.items():
    for yr in YEARS:
        st = meta['state']
        u = f"https://files.hudexchange.info/reports/published/CoC_PopSub_CoC_{coc}-{yr}_{st}_{yr}.pdf"
        cache = R/f"{coc.replace('-','')}_{yr}.pdf"
        if cache.exists():
            b = cache.read_bytes()
        else:
            b = fetch(u)
            if b and len(b) > 5000:
                cache.write_bytes(b)
            time.sleep(0.3)
        if not b:
            errors.append({'coc':coc,'year':yr,'status':'no-file'})  # honest-null: HUD published-nothing at this route (or year absent)
            continue
        cid, cname, pdate, out = parse_pit(b)
        if not out:
            errors.append({'coc':coc,'year':yr,'status':'parse-empty'})
            continue
        rows.append({
            'coc': cid or coc, 'coc_name_hud': cname if cname is None else cname, 'year': yr,
            'pit_date': pdate, 'city': meta['city'], 'grain': 'CoC',
            'pit_total_sheltered_es': out.get('es'), 'pit_total_sheltered_th': out.get('th'),
            'pit_total_unsheltered': out.get('unsheltered'), 'pit_total': out.get('total'),
            'col_note': out.get('cols'), 'route': u, 'stock_law_note': "STATIC-STOCK: a point-in-time count of one January night, never read as a flow"
        })
        print(coc, yr, rows[-1]['pit_total'], rows[-1]['pit_total_sheltered_es'], rows[-1]['pit_total_unsheltered'])

(O/'_pit_raw_rows.json').write_text(json.dumps({'rows':rows,'errors':errors}, indent=1), encoding='utf-8')
print('DONE rows', len(rows), 'errors', len(errors))
