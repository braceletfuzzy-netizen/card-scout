"""PolyScout mayor-row watch: monthly promise-clock check for mamdani_statline_v1.json.
Reads the statline, reports clock-status per promise (PENDING/due/overdue), banks state-deltas.
Founder-direct alert ONLY on: a promise flips PENDING->scored, or a deadline-slip appears. Silent otherwise (the watchdog law)."""
import json, os, urllib.request
from datetime import date

STAT = 'C:/Users/J/Documents/LLM/PolyScout/build/mamdani_statline_v1.json'
STATE = 'C:/Users/J/Documents/LLM/cardscout-2.0/data_lake/gold/mayor_row_state.json'
FD = '1567567851408072814'

TOK = None
for line in open('C:/Users/J/AppData/Local/hermes/.env', encoding='utf-8', errors='replace'):
    if line.startswith('DISCORD_BOT_TOKEN='):
        TOK = line.split('=', 1)[1].strip().strip('"').strip("'")
H = {'Authorization': 'Bot ' + TOK, 'User-Agent': 'DiscordBot (https://cardscout.pro, 1.0)', 'Content-Type': 'application/json'}

def main():
    row = json.load(open(STAT, encoding='utf-8'))
    today = date.today()
    prev = {}
    if os.path.exists(STATE):
        prev = json.load(open(STATE, encoding='utf-8'))
    lines = []
    changes = []
    state = {}
    for p in row['promises']:
        pid = p['id']
        ev = p.get('delivery_evidence')
        score = p.get('score') or 'PENDING'
        dl = p.get('delivery_deadline_stated')
        yrs_left = (dl - today.year) if dl else None
        lines.append(f"**{pid}** [{score}] deadline-{dl if dl else 'n/a'} ({yrs_left}y left) | evidence: {'present' if ev else 'null'}")
        state[pid] = score
        if prev.get(pid) != score:
            changes.append(f'{pid}: {prev.get(pid, "new")} -> {score}')
    # THE VERIFY-PASS (the build-3 v1): the reachable-checks = the fetch-lanes + the the verify-lines-appended:
    try:
        for vline in verify_pass():
            lines.append('· ' + vline)
    except Exception as _ex:
        lines.append('· verify-pass-error: ' + str(_ex)[:80])
    json.dump(state, open(STATE, 'w', encoding='utf-8'), indent=1)
    if changes and prev:
        msg = {'content': '**Mayor-row promise-clock update** (' + str(today) + '):\n' + '\n'.join('- ' + c for c in changes) + '\n\n' + '\n'.join(lines)}
        req = urllib.request.Request('https://discord.com/api/v10/channels/' + FD + '/messages', data=json.dumps(msg).encode(), headers=H, method='POST')
        urllib.request.urlopen(req, timeout=20)
        print('alerted:', len(changes), 'changes')
    else:
        print('silent-healthy:', len(row['promises']), 'promises tracked, no state-changes')

if __name__ == '__main__':
    main()


# === THE CLAIM-VERIFY-TICK (build-3 v1, the added-2026-11-22): ===
import re as _re, requests as _rq
VERIFY_LANES = [
    {'id': 'MMD-002', 'name': 'crime-40%', 'lane': 'NYPD-CompStat', 'url': 'https://www.nyc.gov/site/nypd/stats/crime-statistics/crime-statistics-landing.page'},
    {'id': 'YM-CRIME', 'name': 'crime-41%', 'lane': 'TN-TBI-UCR', 'url': 'https://www.tn.gov/tbi/crime-issues/crime-statistics.html'},
]
def verify_pass():
    out_lines = []
    for lane in VERIFY_LANES:
        try:
            r = _rq.get(lane['url'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
            out_lines.append(f"{lane['id']} [{lane['lane']}]: HTTP-{r.status_code}, {len(r.text)} chars — reachable-check")
        except Exception as ex:
            out_lines.append(f"{lane['id']} [{lane['lane']}]: FETCH-FAIL {str(ex)[:60]}")
    return out_lines
