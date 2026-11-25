"""4H SYSTEMS WATCHDOG (CardScout fleet). Silent-healthy; self-heals gateway; alerts only on failure/unhealed.
Runs via cron in no_agent mode every 4h. STDOUT = the alert (delivered verbatim); empty stdout = silent.

CONVENTION NOTE (fleet stall-exit pattern, adopted Nov-23 — agent-loop course item #3):
  Stand-exit rule = "2 rounds without fewer failures => structured stop". Module:
  For You/PolyScout/build/fleet_stall_exit.py (AppData hermes/scripts/ mirror per the
  two-place law) — import-ready NOW, call-site NOT yet wired (convention-first; do not
  rewire the watchdog cycle without a test run):
      import sys as _sys
      _sys.path.insert(0, "C:/Users/J/Documents/LLM/PolyScout/build")
      from fleet_stall_exit import check_stall, stall_exit_note
      # call-site (keep a persistent failure-count file across 4h cycles, e.g.
      # _watchdog_failures.json — append round count of failed checks; >=3 points
      # = 2 consecutive non-improving rounds):
      #   stop, reason = check_stall(failure_history)
      #   if stop:
      #       print(stall_exit_note(what_tried="gateway heal + site check + cron sanity",
      #                             why_failing=reason,
      #                             what_next="inspect hermes gateway logs + cron a67286951773 last runs; escalate to founder"))
      #       sys.exit(0)
"""
import subprocess, requests, time, os, sys

def alive_gateway():
    try:
        r = subprocess.run(['hermes', 'gateway', 'status'], capture_output=True, text=True, timeout=60)
        ok = ('running' in r.stdout.lower() and 'No gateway' not in r.stdout) or '✓' in r.stdout
        return ok, r.stdout.strip()[-120:]
    except Exception as e:
        return False, str(e)[:120]

def heal_gateway():
    try:
        subprocess.run(['hermes', 'gateway', 'start'], capture_output=True, text=True, timeout=120)
        time.sleep(5)
        return alive_gateway()
    except Exception as e:
        return False, str(e)[:120]

def site_ok():
    try:
        r = requests.get('https://cardscout.pro/bands', headers={'User-Agent': 'Mozilla/5.0 Chrome/120.0'}, timeout=25)
        return r.status_code == 200 and len(r.text) > 5000, f'HTTP {r.status_code} len {len(r.text)}'
    except Exception as e:
        return False, str(e)[:120]

def crons_sane():
    try:
        r = subprocess.run(['hermes', 'cron', 'list'], capture_output=True, text=True, timeout=90)
        t = r.stdout
        ok = t.count('Last run:') > 5
        gw_down = 'gateway is not running' in t.lower()
        return (ok and not gw_down), ('cron list fine' if ok else 'cron list thin') + ('; GATEWAY-DOWN flagged' if gw_down else '')
    except Exception as e:
        return False, str(e)[:120]

def bd_token():
    try:
        p = r'C:\Users\J\Documents\LLM\card-scout\config\bright-data-token.txt'
        ok = os.path.exists(p) and len(open(p, encoding='utf-8').read().strip()) > 10
        return ok, ('token ok' if ok else 'token missing/short')
    except Exception as e:
        return False, str(e)[:120]


def ingest_founder_direct():
    """New-tweet digest: fetch last 25 founder-direct msgs, resolve unseen tweet links via fxtwitter, bank + announce."""
    import re, json as _json
    BAKED = r'C:\Users\J\Documents\LLM\cardscout-2.0\data_lake\gold\founder_direct_tweets.jsonl'
    seen_ids = set()
    try:
        for line in open(BAKED, encoding='utf-8'):
            try: seen_ids.add(_json.loads(line).get('id'))
            except Exception: pass
    except Exception: pass
    try:
        tok_line = [l for l in open(r'C:\Users\J\AppData\Local\hermes\.env', encoding='utf-8', errors='replace') if l.strip().startswith('DISCORD_BOT_TOKEN')]
        tok = tok_line[0].strip().split('=',1)[1].strip().strip('"')
        H = {'Authorization': 'Bot ' + tok, 'User-Agent': 'DiscordBot (https://cardscout.pro, 1.0)'}
        r = requests.get('https://discord.com/api/v10/channels/1567567851408072814/messages?limit=25', headers=H, timeout=20)
        msgs = r.json() if r.status_code == 200 else []
    except Exception:
        return []
    new_tweets = []
    for m in msgs:
        for user, tid in re.findall(r'https://x\.com/(\w+)/status/(\d+)', m.get('content','') or ''):
            if tid not in seen_ids:
                new_tweets.append((user, tid))
    if not new_tweets:
        return []
    out = []
    for user, tid in new_tweets[:12]:
        try:
            rr = requests.get(f'https://api.fxtwitter.com/{user}/status/{tid}', headers={'User-Agent':'Mozilla/5.0 Chrome/120.0'}, timeout=15)
            if rr.status_code == 200:
                t = (rr.json() or {}).get('tweet') or {}
                rec = {'id': tid, 'user': user, 'handle': (t.get('author') or {}).get('name'),
                       'text': (t.get('text') or '')[:400], 'ts': t.get('created_timestamp')}
                out.append(rec)
        except Exception:
            pass
        time.sleep(1.2)
    try:
        with open(BAKED, 'a', encoding='utf-8') as f:
            for rec in out:
                f.write(_json.dumps(rec) + chr(10))
    except Exception: pass
    return out

checks = []
gw_ok, gw_msg = alive_gateway()
healed = False
if not gw_ok:
    gw_ok2, gw_msg2 = heal_gateway()
    if gw_ok2:
        gw_ok, gw_msg, healed = True, str(gw_msg2) + ' [SELF-HEALED]', True
    else:
        gw_ok, gw_msg, healed = gw_ok2, str(gw_msg2) + ' [HEAL-FAILED]', False
checks.append(('gateway', gw_ok, gw_msg))
s_ok, s_msg = site_ok();    checks.append(('site', s_ok, s_msg))
c_ok, c_msg = crons_sane(); checks.append(('crons', c_ok, c_msg))
b_ok, b_msg = bd_token();   checks.append(('bd-token', b_ok, b_msg))


# founder-direct ingest (the twitter-repo lane)
try:
    tw = ingest_founder_direct()
except Exception:
    tw = []

fails = [c for c in checks if not c[1]]

def post_discord(msg):
    try:
        tok_line = [l for l in open(r'C:\Users\J\AppData\Local\hermes\.env', encoding='utf-8', errors='replace') if l.strip().startswith('DISCORD_BOT_TOKEN')]
        tok = tok_line[0].strip().split('=',1)[1].strip().strip('"')
        H = {'Authorization': 'Bot ' + tok, 'User-Agent': 'DiscordBot (https://cardscout.pro, 1.0)'}
        requests.post('https://discord.com/api/v10/channels/1567567851408072814/messages',
                      headers=H, json={'content': msg[:1900]}, timeout=20)
    except Exception as e:
        pass
lines = ['[SYSTEMS WATCHDOG - ' + time.strftime('%Y-%m-%d %H:%M') + ']']
if healed:
    lines.append('+ gateway SELF-HEALED automatically (was dead; restarted clean). FYI only.')
for n, ok, msg in fails:
    lines.append(f'- {n}: FAIL - {msg}')
if fails:
    post_discord('\n'.join(lines))
    print('\n'.join(lines))
elif tw:
    ds = ['[TWITTER-REPO INGEST - ' + time.strftime('%Y-%m-%d %H:%M') + f'] {len(tw)} new tweet(s):']
    for t in tw[:6]:
        ds.append(f"@{(t['user'])}: {((t['text'] or '').replace(chr(10),' '))[:180]}")
    msg = chr(10).join(ds)
    post_discord(msg)
    print(msg)
else:
    sys.exit(0)
