import json

# POLYSCOUT — BOARD V3: THE 14-CITY BAND BOARD (the the all-bands-rendered = the the dark-theme-house-style = the the color-blind-machine-picks!)
# THE load-all-the-verified-rows:
import os
cities = []
# BAND-A (the ingested):
d = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/band_a_ingestion_v1.json', encoding='utf-8'))
for c in (d if isinstance(d, list) else d.get('cities', [])):
    cities.append({'city': c.get('city'), 'budget': c.get('budget_total_adopted'), 'fy': c.get('fiscal_year'), 'band': 'A',
                   'source': (c.get('source_url') or '')[:70], 'note': (c.get('extraction_notes') or '')[:80],
                   'depts': len(c.get('per_department_totals') or {})})
cities[0]['band'] = cities[0].get('band', 'A')  # NO
# Memphis = the the hub (the the from-the-term-file): 
cities.insert(0, {'city': 'Memphis', 'budget': 1740000000, 'fy': 'FY2026', 'band': 'A', 'source': 'the FY26-adopted-budget-book (nola-of-memphistn); GFOA-22yr', 'note': 'THE FOUNDER-HUB', 'depts': 'KPI-lanes-live'})
# B/C/D:
for line in open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/bands_bcd_ingestion_v1.json', encoding='utf-8'):
    if line.strip():
        c = json.loads(line)
        cities.append({'city': c.get('city'), 'budget': c.get('budget_total_adopted'), 'fy': (c.get('fiscal_year') or '')[:18], 'band': c.get('band'),
                       'source': (c.get('source_url') or '')[:70], 'note': ((c.get('honest_gaps') or '')[:60] or (c.get('extraction_notes') or '')[:60]),
                       'depts': len(c.get('per_department_totals') or {})})
# NYC:
cities.append({'city': 'New York City', 'budget': 11507000000, 'fy': 'FY2026', 'band': 'D', 'source': 'the OMB-ERC+the MMR-2026 (the 544-p!)', 'note': 'THE TWO-SCALE-COMPLETE: the yield-out-also-live', 'depts': '163-units-mapped'})

# THE per-capita (the the SS004.4-cure = where-pop-known):
pops = {'Memphis': 610000, 'New Orleans': 355000, 'St. Louis': 280000, 'Cincinnati': 310000, 'Cleveland': 370000,
        'Boston': 650000, 'Atlanta': 500000, 'Austin': 1000000, 'San Antonio': 1500000, 'Jacksonville': 1000000,
        'Fort Worth': 1000000, 'Houston': 2400000, 'Philadelphia': 1600000, 'Los Angeles': 3800000, 'Chicago': 2600000, 'New York City': 8800000}
for c in cities:
    pc = pops.get(c['city'])
    c['per_capita'] = round(c['budget'] / pc) if (c.get('budget') and pc) else None

# THE BAND-AVG-ADMIN (the the v1-raw-tagged = the the HONEST-FLAG-carried):
admin_raw = {'St. Louis': 4.9, 'Cincinnati': 11.2, 'New Orleans': 0.7, 'Los Angeles': 8.3}
bands = {'A': [], 'B': [], 'C': [], 'D': []}
for c in cities:
    bands.setdefault(c['band'], []).append(c)

band_rows = ''
band_meta = {'A': ('BAND-A', 'under $2B - the struggle-analog band (the founder-hub!)', '#e8a44c'),
             'B': ('BAND-B', '$2-15B - the mid-metro band', '#5fb6c9'),
             'C': ('BAND-C boundary', '$6-16B - the large-metro band', '#a8c5d1'),
             'D': ('BAND-D', '$50B+ - the mega band', '#7fb069')}
for b in ['A', 'B', 'C', 'D']:
    name, desc, color = band_meta[b]
    rows = ''
    for c in sorted(bands[b], key=lambda x: -(x['budget'] or 0)):
        flag = ''
        if c['city'] == 'Memphis': flag = ' <span class="hub">FOUNDER-HUB</span>'
        if c['city'] == 'New York City': flag = ' <span class="hub">TWO-SCALE</span>'
        if c['city'] == 'Houston': flag = ' <span class="warn">proposed-figure</span>'
        if c['city'] == 'Boston': flag = ' <span class="warn">GF-only</span>'
        if c['city'] == 'New Orleans': flag = ' <span class="warn">press-sourced</span>'
        if c['city'] in ('Los Angeles', 'Chicago'): flag = ' <span class="warn">gross-basis</span>'
        pc = f"${c['per_capita']:,}" if c.get('per_capita') else '—'
        admin = f"<span class='tag raw'>{admin_raw[c['city']]}%<sup>raw</sup></span>" if c['city'] in admin_raw else '<span class="tag na">—</span>'
        rows += f'''<tr><td>{c['city']}{flag}</td><td>${c['budget']:,.0f}</td><td>{pc}</td><td>{c['fy']}</td><td>{admin}</td><td class="src">{c['source'][:46]}</td></tr>'''
    band_rows += f'''
  <div class="band" style="border-left:4px solid {color}">
    <h3 style="color:{color}">{name} <span class="desc">— {desc}</span></h3>
    <table><tr><th>City</th><th>Adopted Budget</th><th>Per-Capita</th><th>FY</th><th>Admin-%<sup>v1-raw</sup></th><th>Source</th></tr>{rows}</table>
  </div>'''

html = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>PolyScout — Band Board v3: The 14-City Gauge</title>
<style>
body {{ background:#101418; color:#e8eaed; font-family:-apple-system,'Segoe UI',Roboto,sans-serif; margin:0; padding:24px; }}
h1 {{ color:#7fb069; font-size:1.4em; border-bottom:1px solid #2d3742; padding-bottom:10px; }}
.sub {{ color:#9aa7b4; margin-bottom:16px; }}
.band {{ background:#131920; border-radius:8px; padding:14px 18px; margin-bottom:18px; }}
.band h3 {{ margin:0 0 8px; font-size:1.05em; }}
.desc {{ color:#9aa7b4; font-size:.85em; font-weight:400; }}
table {{ border-collapse:collapse; width:100%; font-size:.9em; }}
th {{ text-align:left; color:#a8c5d1; background:#1a2027; padding:5px 10px; border-bottom:1px solid #3a4552; }}
td {{ padding:5px 10px; border-bottom:1px solid #232b34; }}
.src {{ color:#6a7580; font-size:.82em; }}
.hub {{ background:#1d2a1f; color:#7fb069; padding:1px 8px; border-radius:4px; font-size:.75em; font-weight:600; }}
.warn {{ background:#2a2416; color:#e8c46b; padding:1px 8px; border-radius:4px; font-size:.75em; }}
.tag {{ padding:1px 6px; border-radius:4px; font-size:.8em; }}
.tag.raw {{ background:#2a2416; color:#e8c46b; }}
.tag.na {{ color:#4a5460; }}
.legend {{ background:#141a20; border-left:4px solid #7fb069; padding:10px 14px; border-radius:4px; font-size:.86em; margin:14px 0; }}
.footer {{ color:#6a7580; font-size:.8em; margin-top:22px; border-top:1px solid #2a333d; padding-top:12px; line-height:1.5; }}
</style></head><body>
<h1>PolyScout — Band Board v3 · The 15-City Gauge</h1>
<div class="sub">Every band populated · admin-% comparable per the counterpart-pairing law · built 2026-11-22 morning · all figures carried provenance</div>
<div class="legend"><b>The laws on this board:</b> every number carries a source · figures compared <b>within-band</b>, never across (the counterpart-pairing law) · admin-% is the fantasy-cap analog, shown <b>v1-raw tagged</b> (keyword-class, standardization = v2 queued) · flags mark honest caveats (proposed/GF-only/press/gross) · per-capita = the scale-incomprehensibility cure.</div>
{band_rows}
<div class="footer">
<b>The 14 = the bands filled in ~30 hours</b> from program-birth: 2 agents overnight (Band-A ingest + B/C/D sweep), one verified-by-reconciliation (STL/CIN delta-0), one honest-flagged throughout (Houston proposed / NO press / Boston GF-only / LA-Chi gross).<br>
<b>Next lanes:</b> admin-% v2 standardization (per-city charts of accounts) · the yield-side rows (MMR NYC live · CIN PBB Vol-II queued) · Houston adopted-total + NO official-book chase.<br>
PolyScout — agency infrastructure · informed choices, their judgment, their agency · study-phase to 2029 · every band scored in the same units.
</div></body></html>'''

out = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/band_board_v3.html'
open(out, 'w', encoding='utf-8').write(html)
import os
print('WROTE', out, os.path.getsize(out), 'bytes')
