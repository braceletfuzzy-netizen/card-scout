# _prepost_pass.py — the Raleigh Springs pre/post analysis pass
# THE TEST: corridor (MPD bbox, post-only) vs citywide TIBRS (pre+post),
# with the population/period honesty layer.
import json, os

B = os.path.dirname(os.path.abspath(__file__)) or '.'
d = json.load(open(os.path.join(B, 'raleigh_springs_site_v2.json'), encoding='utf-8'))
mem = d['lanes']['1a_tibrs_baseline_lane']['memphis_pd_series']
crime_lane = d['lanes']['1_crime_series']
corridor = crime_lane.get('corridor_series') or crime_lane.get('yearly_counts') or {}

print('=== 1. THE CITY-WIDE TIBRS ARC (pre + post) ===')
for y in mem:
    m = (y.get('murder') or {}).get('cases')
    agg = (y.get('agg_assault') or {}).get('cases')
    rob = (y.get('robbery') or {}).get('cases')
    mvt_key = 'mvt' if 'mvt' in y else ('motor_vehicle_theft' if 'motor_vehicle_theft' in y else None)
    mvt = (y.get(mvt_key) or {}).get('cases') if mvt_key else None
    yr = y.get('year'); period = y.get('period')
    print(yr, period, '| murder:', m, '| agg:', agg, '| rob:', rob, '| mvt:', mvt)

print()
print('=== 2. THE CORRIDOR-SERIES (MPD bbox, 2020-2026) ===')
if isinstance(corridor, dict):
    for k, v in sorted(corridor.items()):
        print(k, v if not isinstance(v, dict) else json.dumps(v)[:120])
print('corridor-lane-alt-keys:', [k for k in crime_lane if 'corridor' in k.lower() or 'bbox' in k.lower() or 'series' in k.lower()])
