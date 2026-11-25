#!/usr/bin/env python3
import json, os, re
from collections import defaultdict

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

def jl(p):
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]

# ---------- LOAD: crime+/care+ v2 (normalized) ----------
cc_rows = json.load(open(B + 'crime_plus_care_plus_v2.json', encoding='utf-8'))
# index by (city, normalized year string)
cc_index = {}
for r in cc_rows:
    key = (r['city'], str(r['year']))
    cc_index[key] = r

# ---------- EDU+ v1 ----------
edu_rows = json.load(open(B + 'edu_plus_v1_computed.json', encoding='utf-8'))

# ---------- ASSEMBLE THE MERGED TRIPLE TABLE ----------
edu_index = {}
for r in edu_rows:
    y_short = re.search(r'((19|20)\d\d)', str(r['year']))
    edu_index[(r['city'], y_short.group(0) if y_short else str(r['year']))] = r

merged = []
used = set()
for (city, y), r in cc_index.items():
    e = edu_index.get((city, y))
    eplus = r.get('eplus') or (e or {}).get('edu_plus')
    merged.append({
        'city': city, 'year': y,
        'crime_plus': r.get('crime_plus'),
        'care_plus_norm': r.get('care_plus_normalized'),
        'care_raw': r.get('care_cage_ratio'),
        'edu_plus': eplus,
        'edu_basis': (e or {}).get('basis'),
        'edu_per_capita': (e or {}).get('epc_est') or (e or {}).get('epc'),
    })
    used.add((city, y))

# add edu rows that didn't pair with a crime/care row
for key, e in edu_index.items():
    if key not in used:
        merged.append({'city': key[0], 'year': key[1], 'crime_plus': None,
                       'care_plus_norm': None, 'care_raw': None,
                       'edu_plus': e.get('edu_plus'), 'edu_basis': e.get('basis'),
                       'edu_per_capita': e.get('epc_est') or e.get('epc')})

merged.sort(key=lambda x: (x['city'], x['year']))

json.dump(merged, open(B + 'triple_slider_v1.json', 'w', encoding='utf-8'), indent=1)

# ---------- RENDER BOARD V6 ----------
# league rows
league_rows = ''
for r in merged:
    cp = r.get('crime_plus'); carep = r.get('care_plus_norm'); ep = r.get('edu_plus')
    basis = r.get('edu_basis') or '—'
    basis_tag = f"<span style='font-size:.72em;color:#5f6b7c'> {basis}</span>" if ep else ''
    cp_s = f"<span class='cp'>{cp}</span>" if cp else '—'
    carep_s = f"<span class='care'>{carep}</span>" if carep else '—'
    ep_s = f"<b>{ep}</b>{basis_tag}" if ep else '—'
    has_any = (cp or carep or ep)
    if not has_any:
        league_rows += f"<tr><td>{r['city']}</td><td>{r['year']}</td><td colspan='3' class='gapnote'>care-run pending — crime known, budget arc not yet backwards-run</td></tr>"
    else:
        league_rows += f"<tr><td>{r['city']}</td><td>{r['year']}</td><td>{cp_s}</td><td>{carep_s}</td><td>{ep_s}</td></tr>"

# quartet
quartet_rows = ''
band_a = {
    'New Orleans': ('1-PUBLIC-RESET', 'FLIP DURABLE 0.164->0.365 — falsifier survived GF-check'),
    'Memphis': ('5-EXTERNAL-CAGING', 'care GREW (normalized CARE+ 100.0) while state caged external'),
    'St. Louis': ('2-PRIVATE-INVISIBLE', 'No break, FLAT-TO-DOWN through Cortex/NGA; Prop-P lesson born here'),
    'Cincinnati': ('2-PRIVATE-INVISIBLE', 'Stable mild care-tilt; OTR ran via 3CDC = ledger-invisible; EDU+ leader 143.4'),
}
for city, (cl, v) in band_a.items():
    quartet_rows += f"<tr><td><b>{city}</b></td><td class='cl'>{cl}</td><td>{v}</td></tr>"

# classifier rows
classifier = json.load(open(B + 'flip_year_band_classifier_v1.json', encoding='utf-8'))
cls_rows = ''
for c in classifier['the_cities']:
    cls_rows += f"<tr><td><b>{c['city']}</b></td><td>{c['lane_class']}</td><td>{c['verdict'][:90]}</td></tr>"

# trails SVG (care-ratio per city, from series files)
care_series = {}
files = {'boston_care_cage_series_v1.jsonl':'Boston','neworleans_care_cage_series_v1.jsonl':'New Orleans',
         'stlouis_care_cage_series_v1.jsonl':'St. Louis','cincinnati_care_cage_series_v1.jsonl':'Cincinnati',
         'memphis_care_cage_series_v1.jsonl':'Memphis','detroit_care_cage_series_v1.jsonl':'Detroit',
         'okc_care_cage_series_v1.jsonl':'Oklahoma City','nyc_care_cage_series_v1.jsonl':'New York City'}
for fname, city in files.items():
    try:
        pts = []
        for r in jl(B + fname):
            era = str(r.get('era_or_year') or r.get('era') or '')
            c = r.get('care_usd_total'); g = r.get('cage_usd_total')
            if c and g:
                ym = re.search(r'(19|20)\d\d', era)
                if ym: pts.append((int(ym.group(0)), round(c/g,3)))
        pts = sorted({y: r for y,r in reversed(pts)}.items())
        care_series[city] = pts
    except FileNotFoundError:
        pass

trail_svg = ''
for city, pts in care_series.items():
    if len(pts) < 2: continue
    ys = [p[0] for p in pts]; rs = [p[1] for p in pts]
    x0, x1 = min(ys), max(ys); y0, y1 = min(rs), max(rs)
    span_x, span_y = (x1-x0) or 1, (y1-y0) or 1
    def xp(y): return 40 + (y-x0)/span_x*260
    def yp(r): return 70 - (r-y0)/span_y*54
    poly = ' '.join(f"{xp(y):.0f},{yp(r):.0f}" for y, r in pts)
    trail_svg += f"<polyline points='{poly}' fill='none' stroke-width='1.5' class='tr'/><text x='{xp(ys[0]):.0f}' y='82' font-size='6.5' fill='#7f8ea3'>{city[:10]} {ys[0]}</text><circle cx='{xp(ys[-1]):.0f}' cy='{yp(rs[-1]):.0f}' r='2.2' fill='#7fb069'/>"

html = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><title>PolyScout Board v7 — The Three-Slider League</title>
<style>
body {{ background:#0d1117; color:#d8dee6; font-family:Segoe UI,-apple-system,sans-serif; margin:0; padding:22px }}
h1 {{ color:#7fb069; font-size:1.35em; border-bottom:1px solid #2a333d; padding-bottom:8px }}
h2 {{ color:#a8c5d1; font-size:1.05em; margin:22px 0 6px; border-left:3px solid #7fb069; padding-left:9px }}
table {{ border-collapse:collapse; width:100%; font-size:.86em; margin-bottom:14px }}
th {{ text-align:left; color:#a8c5d1; background:#161d24; padding:4px 9px; border-bottom:1px solid #3a4552 }}
td {{ padding:4px 9px; border-bottom:1px solid #1f2933 }}
.cp {{ color:#e8a44c; font-weight:700 }}
.care {{ color:#7fb069; font-weight:700 }}
.legend {{ background:#131a21; border-left:3px solid #7fb069; padding:8px 12px; font-size:.82em; margin:10px 0; color:#a9b6c2 }}
.foot {{ color:#5f6b7c; font-size:.78em; border-top:1px solid #2a333d; margin-top:18px; padding-top:10px }}
svg {{ background:#12181f; border-radius:6px }}
.tr {{ stroke:#6b8ea4; opacity:.75 }}
</style></head><body>
<h1>PolyScout Board v7 — The Three-Slider League: CRIME+ / CARE+ / EDU+</h1>
<div class="legend"><b>The ruler (founder design):</b> field-normalized, 100 = in-line with the year's cohort band. CRIME+ <i>higher = more trouble</i>; CARE+ <i>higher = more care</i> (band-normalized v2, founder-caught fix); EDU+ <i>higher = more education spending/resident</i> (basis-flagged: city-run vs district — Boston the only city-run case). All three same formula, same 100-anchor. Built 2026-11-22.</div>

<h2>The Triple League — CRIME+ / CARE+ / EDU+</h2>
<table><tr><th>City</th><th>Year</th><th>CRIME+</th><th>CARE+</th><th>EDU+</th></tr>
{league_rows}</table>

<h2>The Band-A Quartet — four cities, four mechanisms</h2>
<table><tr><th>City</th><th>Class</th><th>Verdict</th></tr>
{quartet_rows}</table>

<h2>The Care-Ratio Trails — every city's line, backwards-run</h2>
<svg width="340" height="90" viewBox="0 0 340 90" style="margin:6px 0">{trail_svg}
<text x="40" y="12" font-size="7" fill="#5f6b7c">care/cage ratio (trails per city, first→last)</text></svg>

<h2>The Six-Class Fingerprint Classifier</h2>
<table><tr><th>City</th><th>Lane Class</th><th>Verdict</th></tr>
{cls_rows}</table>

<div class="foot">
<b>The three-slider model:</b> CARE+/EDU+ = the two input sliders (the budget pie — near-zero-sum trade-offs); CRIME+ = the outcome dial (tests at t+2/3/5 — never instant). Interactions observed, never guaranteed: the pie-constraint, the lead-lag, the twin-control (NO flipped, HOUSTON absorbed — the same shock; the flip is a CHOICE), the Goodhart-guard.<br>
<b>The family:</b> CRIME+ / CARE+ / EDU+ — same formula, same anchor, direction + maturity tagged. EDU+ = own line (the basin-structure lesson: MSCS $1.85B standalone vs city contribution $1.33M settlement [the $514-614M columnar-artifact trap excluded]).<br>
<b>Honesty:</b> association-not-causation; Y+n effects named (planting-trees-for-shade); falsifier-carried in every source JSON; the interpretive layer backed to polyscout-internal (private, snapshot-1 pushed).
</div></body></html>'''

out = B + 'band_board_v7.html'
open(out, 'w', encoding='utf-8').write(html)
print('WROTE', out, os.path.getsize(out))
