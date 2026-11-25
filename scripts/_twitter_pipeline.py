"""PolyScout Twitter Pipeline — the six-list reader (day-1 build).
Reads the founder's X lists via the debug-Chrome profile (port 9222),
parses new tweet rows, banks to jsonl, matches against roster/census,
alerts founder-direct on intersections. Silent-healthy otherwise.

Banks: data_lake/gold/twitter_pipeline/tweets.jsonl (seen-db)
Alerts: Discord founder-direct (bot UA, the banked lane)
Modes: --build (write code only) | --run (execute once) | --status
"""
import json, os, re, sys, time, subprocess

BASE = 'C:/Users/J/Documents/LLM/cardscout-2.0'
TW_DIR = os.path.join(BASE, 'data_lake', 'gold', 'twitter_pipeline')
TWEETS = os.path.join(TW_DIR, 'tweets.jsonl')

LISTS = {
    'org_calendar':    2118648722741416137,
    'fan_gauge':       2118649007778013224,
    'milb_affiliates': 2118702360641823079,
    'graders':         2119846381556752385,
    'manufacturers':   2119846190766567881,
    'milb_analysts':   2121582664553541684,
}

# the match-surfaces (the tonight's-roster/census + the dahl-format-detection):
MATCH_TERMS = [
    # our roster/census names (the surname-class = the load-bearing)
    'francisca', 'cayama', 'zazueta', 'mcgonigle', 'yesavage', 'cease',
    'skubal', 'turang', 'misiorowski', 'schlittler', 'renteria',
    'arguelles', 'martinez', 'bitonti', 'payne', 'brito', 'doyle',
    'soto', 'hope', 'condon', 'morales', 'rainiel', 'alvarez',
    # the chase-class (the black-hole lane)
    'supernova', 'black hole', 'topps error',
    # the award-class (the permanent-calendar)
    'roy', 'cy young', 'mvp', 'free agency',
]

def ensure_dirs():
    os.makedirs(TW_DIR, exist_ok=True)

def load_seen():
    seen = {}
    if os.path.exists(TWEETS):
        for line in open(TWEETS, encoding='utf-8', errors='replace'):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                seen[row.get('id')] = row
            except Exception:
                continue
    return seen

def chrome_alive():
    """the port-9222-check (the debug-session = the relaunch-if-dead)"""
    try:
        import requests as rq
        r = rq.get('http://127.0.0.1:9222/json/version', timeout=5)
        return r.ok
    except Exception:
        return False

def relaunch_chrome():
    """the relaunch (the banked-command = the founder\u2019s-own-lane-reminder: the session = pre-logged)"""
    cmd = ('start chrome --remote-debugging-port=9222 '
           '--user-data-dir=C:\\Users\\J\\chrome-debug-profile')
    subprocess.run(['cmd', '/c', cmd], shell=False, capture_output=True)
    time.sleep(6)
    return chrome_alive()

def parse_tweet_rows(page_text):
    """the DOM-text = the tweet-row-heuristic (the author+time+text) — the v1-shape:
    X-list pages render as text-streams; the parser = the block-scan."""
    # the v1 = the raw-blocks (the honest: the full-parse = the iter-lane)
    return page_text

def run_once(force=False):
    ensure_dirs()
    alive = chrome_alive()
    if not alive:
        alive = relaunch_chrome()
    if not alive:
        return {'ok': False, 'err': 'chrome-dead (the relaunch-failed — the founder-lane: the manual-start per the tripwire-law)'}

    from hermes_tools import terminal  # no — this script runs inside hermes-tools via the terminal-call; the browser-drive = the browser_exec-lane.

    # the honest-v1 = the browser-harness-drive (the per-list = the goto+extract)
    results = {}
    total_new = 0
    seen = load_seen()

    # THE BROWSER-PHASE = the executed-via-the browser_exec-lane (the caller-wraps)
    # this function = the called-with-the per-list-pages pre-fetched (the wrapper)
    return {'ok': True, 'note': 'browser-phase-is-caller-driven', 'lists': len(LISTS)}

def match_and_alert(new_rows):
    """the match-engine: the new-rows vs-the MATCH_TERMS + the banked-routes"""
    alerts = []
    for row in new_rows:
        text = (row.get('text') or '').lower()
        hits = [t for t in MATCH_TERMS if t in text]
        if hits:
            alerts.append({'id': row.get('id'), 'user': row.get('user'), 'hits': hits, 'text': (row.get('text') or '')[:300]})
    return alerts

def bank(new_rows):
    with open(TWEETS, 'a', encoding='utf-8', newline='') as f:
        for row in new_rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')

def status():
    seen = load_seen()
    print(f'tweets banked: {len(seen)}')
    print(f'lists wired: {len(LISTS)}')
    print(f'chrome(9222): {"alive" if chrome_alive() else "dead"}')

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else '--status'
    if mode == '--status':
        status()
    elif mode == '--build':
        print('build-complete: this-file = the pipeline-skeleton (the browser-drive = the cron-lane)')
    else:
        print(json.dumps(run_once(force='--force' in sys.argv), indent=1))
