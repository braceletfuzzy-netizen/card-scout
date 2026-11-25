import json

# POLYSCOUT BUILD-2 — THE ONE-PILOT-BOARD: the two-statlines = the rendered-SIDE-BY-SIDE (the the-the-product!)
mam = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/mamdani_term_file_v2.json', encoding='utf-8'))
yng = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/paul_young_statline_v1.json', encoding='utf-8'))

def col(promises, fame, color, name, party_role, term):
    rows = ''
    for p in promises:
        src = p.get('claim_source_class') or '—'
        tag_cls = 'official' if 'OFFICIAL' in src or 'RGB' in src else ("own" if 'OWN' in src else 'platform')
        tag_label = {'official': 'official', 'own': 'mayor-own', 'platform': 'campaign'}[tag_cls]
        rows += f'''
    <div class="promise">
      <div class="p-head"><b>{p['id']}</b><span class="tag {tag_cls}">{tag_label}</span></div>
      <div class="ptext">{p['promise']}</div>
      <div class="p-clock">{p.get('clock') or p.get('delivery_deadline_stated') or ''}</div>
      <div class="p-status">{p.get('status','PENDING')}</div>
    </div>'''
    return f'''
  <div class="mayor" style="border-color:{color}">
    <h2 style="color:{color}">{name}</h2>
    <div class="meta">{party_role} · {term}</div>
    <div class="fame">fame-composite v0: <b>{fame}</b></div>
    {rows}
  </div>'''

# THE f-string-backslash-fix: the the unicode-escapes = the hoisted:
mam_own_lbl = 'helping public housing residents buy 91 properties (the homeownership-lane)'
yng_own_lbl = "the mayor\u0027s own numbers = NOT yet machine-verified"
html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>PolyScout — The Mayor Board v1</title>
<style>
body {{ background:#101418; color:#e8eaed; font-family:-apple-system,'Segoe UI',Roboto,sans-serif; margin:0; padding:24px; }}
h1 {{ color:#7fb069; font-size:1.45em; border-bottom:1px solid #2d3742; padding-bottom:10px; }}
.sub {{ color:#9aa7b4; margin-bottom:18px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
.mayor {{ border:1px solid #26303a; border-radius:8px; padding:16px; background:#131920; }}
.mayor h2 {{ margin:0 0 4px; font-size:1.15em; }}
.meta {{ color:#9aa7b4; font-size:.88em; margin-bottom:10px; }}
.fame {{ background:#1a2027; border-radius:6px; padding:8px 12px; margin-bottom:12px; font-size:.95em; }}
.promise {{ border-top:1px solid #232b34; padding:10px 2px; }}
.p-head display:flex; gap:8px; }}
.p-head b {{ color:#a8c5d1; }}
.tag {{ padding:1px 8px; border-radius:4px; font-size:.75em; }}
.tag.official {{ background:#1d2a1f; color:#7fb069; }}
.tag.own {{ background:#2a2416; color:#e8c46b; }}
.tag.platform {{ background:#1d2532; color:#a8c5d1; }}
.ptext {{ font-size:.95em; margin:4px 0; color:#dee4ea; }}
.p-clock {{ font-size:.8em; color:#9aa7b4; }}
.p-status {{ font-size:.85em; color:#e8c46b; font-weight:600; }}
.footer {{ color:#6a7580; font-size:.8em; margin-top:24px; border-top:1px solid #2a333d; padding-top:12px; line-height:1.5; }}
@media (max-width: 800px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style></head><body>
<h1>PolyScout — The Mayor Board v1</h1>
<div class="sub">Two mayors · one scale · the first political statlines in the ledger · built 2026-11-21</div>
<div class="grid">
{col(mam.get('campaign_promises', mam.get('promises', [])), '0.62', '#7fb069', 'Zohran Mamdani — NYC', 'the first major promise KEPT (RGB two-year freeze, one million apartments)', 'term: Jan 2026 → Dec 2029')}
{col(yng.get('campaign_promises', []), '0.38', '#e8a44c', 'Paul Young — Memphis', 'the yields pre-populated from the city KPI pages · mixed-honest', 'term: Jan 2024 → Dec 2027')}
</div>
<div class="footer">
<b>The laws:</b> every promise pre-registered at claim-date · claim-source tagged (campaign / official / mayor-own) · the unavailable = null, never fabricated · score = promise-vs-delivery, never the goodness (the voters) · deadline-slips logged as data.<br>
<b>Master classes:</b> Governance Yield · Transparency · Institution Building · Fiscal Discipline · Obfuscation Signature.<br>
PolyScout — agency infrastructure · informed choices, their judgment, their agency · study-phase to 2029.
</div>
</body></html>'''

out = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/pilot_board_v1.html'
open(out, 'w', encoding='utf-8').write(html)
import os
print('WROTE', out, os.path.getsize(out), 'bytes')
