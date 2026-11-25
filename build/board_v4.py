#!/usr/bin/env python3
import json, os, re
from collections import defaultdict

B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

def jl(p):
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]

# ---------- LEAGUE (CRIME+/CARE+) ----------
league = json.load(open(B + 'crime_plus_care_plus_v1.json', encoding='utf-8'))

# ---------- QUARTET + CLASSIFIER ----------
classifier = json.load(open(B + 'flip_year_band_classifier_v1.json', encoding='utf-8'))
cities_cls = classifier['the_cities']

# ---------- CARE-RATIO SERIES PER CITY (trail data) ----------
care_series = {}
for fname, city in [('boston_care_cage_series_v1.jsonl','Boston'),
                    ('neworleans_care_cage_series_v1.jsonl','New Orleans'),
                    ('stlouis_care_cage_series_v1.jsonl','St. Louis'),
                    ('cincinnati_care_cage_series_v1.jsonl','Cincinnati'),
                    ('memphis_care_cage_series_v1.jsonl','Memphis'),
                    ('detroit_care_cage_series_v1.jsonl','Detroit'),
                    ('okc_care_cage_series_v1.jsonl','Oklahoma City'),
                    ('nyc_care_cage_series_v1.jsonl','New York City')]:
    pts = []
    for r in jl(B + fname):
        era = str(r.get('era_or_year') or r.get('era') or '')
        c = r.get('care_usd_total'); g = r.get('cage_usd_total')
        if c and g:
            ym = re.search(r'(19|20)\d\d', era)
            if ym:
                pts.append((int(ym.group(0)), round(c/g, 3)))
    # sort + dedupe by year keeping first
    pts = sorted({y: r for y, r in reversed(pts)}.items())
    care_series[city] = pts

# ---------- BAND-A QUARTET ----------
band_a = {
    'New Orleans': {'class': '1-PUBLIC-RESET', 'verdict': 'FLIP DURABLE 0.164->0.365', 'evidence': 'Katrina rebuild doubled care share; falsifier survived GF-check'},
    'Memphis': {'class': '5-EXTERNAL-CAGING', 'verdict': 'care GREW (care+ 51.5, largest reading) while state caged external', 'evidence': 'founder-lens confirmed: zero MSTF line-items; $100M state fund external'},
    'St. Louis': {'class': '2-PRIVATE-INVISIBLE', 'verdict': 'No break 0.190->0.118, flatter-to-down through Cortex/NGA', 'evidence': 'Cortex 501(c)(3) + NGA federal = revival outside ledger; Prop-P special-funds lesson'},
    'Cincinnati': {'class': '2-PRIVATE-INVISIBLE', 'verdict': 'Stable 0.637-0.728, mild care-tilt, no break', 'evidence': 'OTR ran via 3CDC corporate capital = ledger-invisible'},
}

# ---------- RENDER ----------
cls_rows = ''
for c in cities_cls:
    lane = c['lane_class']; v = c['verdict']
    cls_rows += f"<tr><td><b>{c['city']}</b></td><td>{lane}</td><td>{v[:90]}</td></tr>"

league_rows = ''
for r in sorted([x for x in league if x.get('crime_plus')], key=lambda x: -x['crime_plus']):
    cp = r['crime_plus']; cc = r.get('care_cage_ratio'); carep = f"{round(cc*100,1)}" if cc else '—'
    league_rows += f"<tr><td>{r['city']}</td><td>{r['year']}</td><td>{r['murders']}</td><td>{r['rate']}</td><td class='cp'>{cp}</td><td>{cc if cc else '—'}</td><td>{carep}</td></tr>"

quartet_rows = ''
for city, d in band_a.items():
    quartet_rows += f"<tr><td><b>{city}</b></td><td class='cl'>{d['class']}</td><td>{d['verdict']}</td><td class='ev'>{d['evidence'][:110]}</td></tr>"

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

edu_rows = "<tr><td>EDU+ v0</td><td>Designed — own line item (basin-structure: schools usually NOT in city ledger; Boston/OKC exceptions violate like-to-like; size-drowns other lanes)</td><td>EDU+ = 100 x (city edu per capita / band median). Family: CRIME+ / CARE+ / EDU+</td></tr>"

html = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><title>PolyScout Board v4 — Care+/Crime+ League</title>
<style>
body {{ background:#0d1117; color:#d8dee6; font-family:Segoe UI,-apple-system,sans-serif; margin:0; padding:22px }}
h1 {{ color:#7fb069; font-size:1.35em; border-bottom:1px solid #2a333d; padding-bottom:8px }}
h2 {{ color:#a8c5d1; font-size:1.05em; margin:22px 0 6px; border-left:3px solid #7fb069; padding-left:9px }}
table {{ border-collapse:collapse; width:100%; font-size:.86em; margin-bottom:14px }}
th {{ text-align:left; color:#a8c5d1; background:#161d24; padding:4px 9px; border-bottom:1px solid #3a4552 }}
td {{ padding:4px 9px; border-bottom:1px solid #1f2933 }}
.cp {{ color:#e8a44c; font-weight:700 }}
.cl {{ color:#7fb069 }}
.ev {{ color:#8b9cac; font-size:.83em }}
.legend {{ background:#131a21; border-left:3px solid #7fb069; padding:8px 12px; font-size:.82em; margin:10px 0; color:#a9b6c2 }}
.foot {{ color:#5f6b7c; font-size:.78em; border-top:1px solid #2a333d; margin-top:18px; padding-top:10px }}
svg {{ background:#12181f; border-radius:6px }}
.tr {{ stroke:#6b8ea4; opacity:.75 }}
</style></head><body>
<h1>PolyScout Board v4 — The Care+/Crime+ League & the Fingerprint Band</h1>
<div class="legend"><b>The ruler (founder design):</b> field-normalized, 100 = in-line with the cohort band. CRIME+ <i>higher = more trouble</i>; CARE+ <i>higher = more care</i> (direction inverts). Care+ is v0-roughest (fund-aware v2 maturing). Built 2026-11-22 — every figure source-cited in the underlying JSONLs.</div>

<h2>The League — murders, CRIME+, care-side, CARE+</h2>
<table><tr><th>City</th><th>Year</th><th>Murders</th><th>Rate/100k</th><th>CRIME+</th><th>care/cage</th><th>CARE+</th></tr>
{league_rows}</table>

<h2>The Band-A Quartet — four cities, four mechanisms</h2>
<table><tr><th>City</th><th>Class</th><th>Verdict</th><th>Evidence</th></tr>
{quartet_rows}</table>

<h2>The Care-Ratio Trails — every city's line, backwards-run</h2>
<svg width="340" height="90" viewBox="0 0 340 90" style="margin:6px 0">{trail_svg}
<text x="40" y="12" font-size="7" fill="#5f6b7c">care/cage ratio (trails per city, first→last point)</text></svg>

<h2>The Six-Class Fingerprint Classifier</h2>
<table><tr><th>City</th><th>Lane Class</th><th>Verdict</th></tr>
{cls_rows}</table>

<h2>The Third Slider — EDU+ v0 (designed)</h2>
<table>{edu_rows}</table>

<div class="foot">
<b>Stacked lineage:</b> budget ingestion (8 cities, dept-grain, delta-0 reconciles) → care/cage fingerprint runs (8 cities backwards-run) → the flip-year band classifier (six-taxonomy) → the twin-city control (NO vs Houston = the split verdict = the flip is a CHOICE) → CRIME+/CARE+ field-normalized league (this board).<br>
<b>Family:</b> CRIME+ / CARE+ / EDU+ — same formula (100 × city / band-field), directions named, v0-honesty tagged. EDU+ designed as its own line (basin-structure). Fund-aware v2 live (the Prop-P lesson +16.6% invisible care).<br>
<b>Honesty:</b> association-not-causation; Y+n effects named (planting-trees-for-shade); every claim falsifier-carried in source JSONs; interpretive layer backed to polyscout-internal (private).
</div></body></html>'''

out = B + 'band_board_v4.html'
open(out, 'w', encoding='utf-8').write(html)
print('WROTE', out, os.path.getsize(out), 'bytes')
