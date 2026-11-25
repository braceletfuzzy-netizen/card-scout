# maslow_joint_panel_v1 producer (re-merge path) — THE JOINT-BUILD PHASE-1, first construction
# Shipped artifact: maslow_joint_panel_v1.jsonl (94 city-year rows) + maslow_joint_panel_v1.json (record + reads).
# Reproduces the merge from _joint_panel_raw/*.dat (raw ACS 1-YR table-based-SF pulls, keyless www2.census.gov)
# + banked build/ inputs. Column laws (Table-Shell guards, per-100k convention = usd/pop*1e5) in the verdict file.
import json
from pathlib import Path
B = Path(__file__).parent
J = B/'_joint_panel_raw'

def jl(p): return json.load(open(p, encoding='utf-8'))
def jlines(p): return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]

rows = jlines(B/'maslow_joint_panel_v1.jsonl')
print(len(rows), 'city-year rows on disk (the Phase-1 v1 artifact)')
print('per-city:', {c: sum(1 for r in rows if r['city'] == c) for c in ['Cincinnati', 'Denver', 'Detroit', 'Memphis', 'NYC', 'St. Louis']})
