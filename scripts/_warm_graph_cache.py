#!/usr/bin/env python3
"""WARMER: pre-build the CH player-index-history cache so prod graphs render
without any inline page-load CH call.
Reads the distinct players from the shipped tp_pulls corpus + the published
lane registry, calls band_graph.index_history(player) once per player (the
function itself caches to AGG_DIR indexhist_*.json with the 24h TTL).
Run as a cron nightly (or after deploys). Never raises; logs to stdout.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'scripts'))

# import after path insert
from dashboard import band_graph as bg  # noqa: E402  (uses the shipped fallback paths)

CACHED_SHIPS = []

def main():
    players = set()

    # 1. the shipped tp_pulls corpus (our known watch-players)
    tp = REPO / 'data' / 'tp_pulls.jsonl'
    if tp.exists():
        KNOWN = ['turang','chourio','mcgonigle','ohtani','yamamoto','misiorowski',
                 'messick','schlittler','tolle','sasaki','skubal','judge','witt',
                 'wood','caminero','arroyo','rice','neto','detmers','harper',
                 'tatis','verlander','schwarber','arraez','scherzer','harris',
                 'alonso','sale']
        for line in tp.read_text(encoding='utf-8', errors='ignore').splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            t = (row.get('title') or '').lower()
            for n in KNOWN:
                if n in t:
                    players.add(n.title())
                    break

    # 2. registry players (prod lane store)
    reg_path = REPO / 'dashboard' / 'registry' / 'card_page_registry.json'
    try:
        reg = json.loads(reg_path.read_text(encoding='utf-8'))
        for key in (reg if isinstance(reg, dict) else {}):
            slug = str(key)
            players.add(slug.split('-')[0].title())
    except Exception as ex:
        print('registry read skipped:', ex)

    players = sorted(p for p in players if p)
    print(f'warming {len(players)} players:', ', '.join(players[:12]),
          ('...' if len(players) > 12 else ''))
    ok = fail = 0
    for p in players:
        try:
            pts = bg.index_history(p, days=90)
            n = len(pts)
            print(f'  {p:14s} -> {n} pts '
                  f'{"(cached)" if n else "(no series)"}')
            ok += 1 if n else 0
        except Exception as ex:
            print(f'  {p:14s} -> ERROR {str(ex)[:60]}')
            fail += 1
    print(f'done: {ok} series cached, {fail} errors, cache at {bg.AGG_DIR}')
    return 0 if fail == 0 else 0  # never fails the job

if __name__ == '__main__':
    raise SystemExit(main())
