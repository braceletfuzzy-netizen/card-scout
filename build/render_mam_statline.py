import json

# POLYSCOUT #A — THE MAYOR-ROW BOARD RENDER: the first-politician-statline = the visual-artifact
row = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/mamdani_statline_v1.json', encoding='utf-8'))

promises_html = ''
for p in row['promises']:
    evidence = p.get('delivery_evidence') or '<em>null \u2014 pending (honest-null law)</em>'
    score = p.get('score') or 'PENDING'
    tag = p.get('category_tag') or ''
    clock = p.get('clock') or ''
    deadline = p.get('delivery_deadline_stated') or ''
    deadline_note = p.get('deadline_note') or ''
    dn_html = f'<div class="risk">{deadline_note}</div>' if deadline_note else ''
    promises_html += f'''
    <div class="promise">
      <div class="p-head"><span class="pid">{p['id']}</span><span class="ptag">{tag}</span></div>
      <div class="ptext">{p['promise']}</div>
      <table class="ptable">
        <tr><th>Claimed</th><th>Deadline</th><th>Clock</th><th>Score</th></tr>
        <tr><td>{p['claim_date']}</td><td>{deadline}{dn_html}</td><td>{clock}</td><td class="pending">{score}</td></tr>
      </table>
      <div class="p-ev"><strong>Delivery evidence:</strong> {evidence}</div>
    </div>'''

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PolyScout Statline \u2014 Mayor Zohran Mamdani</title>
<style>
body {{ background: #101418; color: #e8eaed; font-family: -apple-system, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 24px; }}
.container {{ max-width: 950px; margin: 0 auto; }}
h1 {{ color: #7fb069; font-size: 1.5em; border-bottom: 1px solid #2d3742; padding-bottom: 10px; margin-bottom: 4px; }}
.sub {{ color: #9aa7b4; margin-bottom: 20px; font-size: 0.95em; }}
.legend {{ background: #141a20; border-left: 4px solid #7fb069; padding: 10px 14px; border-radius: 4px; font-size: 0.88em; margin: 14px 0 22px; }}
.legend b {{ color: #dee4ea; }}
.promise {{ border: 1px solid #26303a; border-radius: 8px; padding: 14px 16px; margin-bottom: 16px; background: #131920; }}
.p-head {{ display: flex; gap: 10px; align-items: center; margin-bottom: 6px; }}
.pid {{ background: #1d2a1f; color: #7fb069; padding: 2px 10px; border-radius: 4px; font-weight: 600; font-size: 0.9em; }}
.ptag {{ color: #a8c5d1; font-size: 0.85em; }}
.ptext {{ font-size: 1.02em; margin-bottom: 10px; color: #dee4ea; }}
.ptable {{ border-collapse: collapse; width: 100%; font-size: 0.9em; margin-bottom: 8px; }}
.ptable th {{ text-align: left; color: #a8c5d1; background: #1a2027; padding: 5px 10px; border-bottom: 1px solid #3a4552; font-weight: 600; }}
.ptable td {{ padding: 5px 10px; border-bottom: 1px solid #232b34; }}
.pending {{ color: #e8c46b; font-weight: 600; }}
.risk {{ color: #e8a44c; font-size: 0.85em; margin-top: 3px; }}
.p-ev {{ font-size: 0.88em; color: #9aa7b4; }}
.p-ev em {{ color: #e8c46b; font-style: normal; }}
.fame {{ background: #141a20; border: 1px solid #26303a; border-radius: 8px; padding: 12px 16px; margin: 18px 0; font-size: 0.95em; }}
.footer {{ color: #6a7580; font-size: 0.82em; margin-top: 26px; border-top: 1px solid #2a333d; padding-top: 12px; line-height: 1.5; }}
</style>
</head>
<body><div class="container">
<h1>PolyScout Statline \u2014 {row['statline']}</h1>
<div class="sub">Term: {row['term']['took_office']} \u2192 {row['term']['term_end']} \u00b7 Built {row['built']} \u00b7 The first career-statline in the ledger</div>

<div class="legend"><b>The laws:</b> every promise pre-registered at claim-date with its own falsifier-clock \u00b7 the unavailable = null, never fabricated \u00b7 the score = promise-vs-delivery (objective claims only) \u00b7 deadline-changes logged as data, never editorialized.</div>

{promises_html}

<div class="fame"><b>Fame-composite (hand-set v0):</b> {row['fame_composite']['value']} \u00b7 band {row['fame_composite']['band']} \u2014 the formal-fit lands with the calibration-lane.</div>

<div class="footer">PolyScout \u00b7 SPINOFF-005 career-statline v1 \u00b7 claims tracked, not judged \u00b7 deadline-slips logged as data (see MMD-001) \u00b7 pre-registered [FOUNDER-INTUITION] separate: the founder\u0027s \u201cawesome\u201d scores via these rows\u0029 outcomes by 2032 \u00b7 built 2026-11-21</div>
</div></body></html>'''

out = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/mamdani_statline_board.html'
open(out, 'w', encoding='utf-8').write(html)
import os
print('WROTE', out, os.path.getsize(out), 'bytes')
