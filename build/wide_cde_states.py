# Download CDE agency directories for the 15 wide-panel cities' states
import json, os, urllib.request, time
os.makedirs('_wide', exist_ok=True)
ST = ['PA','AZ','TX','CA','FL','NC','OH','IN','WA','CO','TN']
for s in ST:
    fn = f'_wide/agency_{s}.json'
    if os.path.exists(fn) and os.path.getsize(fn) > 2000:
        print('skip', s); continue
    url = f'https://cde.ucr.cjis.gov/LATEST/agency/byStateAbbr/{s}'
    try:
        d = json.loads(urllib.request.urlopen(url, timeout=120).read())
        open(fn,'w').write(json.dumps(d))
        print('OK', s, len(d), 'agencies')
    except Exception as e:
        print('FAIL', s, str(e)[:150])
    time.sleep(0.5)
print('DONE')
