import requests, re, time

# THE BAND-RECRUITMENT-FACTS (the per-city = the budgets): the fixed-regex (the escaped-quotes = the fixed!)
tok = open('C:/Users/J/Documents/LLM/card-scout/config/bright-data-token.txt', encoding='utf-8').read().strip()

def sweep(q, kws):
    url = 'https://www.bing.com/search?q=' + requests.utils.quote(q)
    for a in range(2):
        r = requests.post('https://api.brightdata.com/request',
                          headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'},
                          json={'zone': 'web_unlocker1', 'url': url, 'format': 'raw'}, timeout=170)
        if len(r.text) > 80000:
            break
        time.sleep(8)
    t = re.sub('<[^>]+>', ' ', r.text)
    t = re.sub(r'\s+', ' ', t)
    hits = re.findall(r'[^.]{0,60}(?:' + '|'.join(kws) + r')[^.]{0,120}', t, re.I)
    seen = []
    for h in hits:
        h = h.strip()
        if h not in seen[:3]:
            seen.append(h)
    return seen[:6]

for q, kws in [
    ('Los Angeles city budget fiscal 2025 2026 adopted total billion', ['billion', 'budget of']),
    ('Boston city budget fiscal 2026 total adopted billion', ['billion', 'budget of']),
    ('New Orleans city budget 2026 adopted billion', ['billion', 'budget of']),
    ('Houston city budget fiscal 2026 adopted billion', ['billion', 'budget of']),
]:
    print('QUERY:', q[:50])
    for h in sweep(q, kws):
        print('  *', h[:220])
    print()
    time.sleep(4)
