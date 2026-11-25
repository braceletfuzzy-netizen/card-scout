# BOARD-2 GRAD-LANE: fetch ACS 1-yr state zips from ftp.census.gov for B14005 extraction
# 8 states x years 2010-2017 (2018/2019 already on disk). Resume-safe.
import ftplib, os, sys

BUILD = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
RAW = BUILD + '_edu_raw/'
STATES = {'Tennessee':'TN','Mississippi':'MS','Michigan':'MI','NewYork':'NY',
          'Ohio':'OH','Missouri':'MO','Colorado':'CO','Massachusetts':'MA'}
YEARS = [2017,2016,2015,2014,2013,2012,2011,2010]

f = ftplib.FTP('ftp.census.gov', timeout=300)
f.login()
ok=skip=err=0
for y in YEARS:
    for stn,ab in STATES.items():
        local = RAW + f'acs{y}_1yr_{ab}_allgeo.zip'
        if os.path.exists(local) and os.path.getsize(local) > 100000:
            skip += 1
            continue
        remote = f'/programs-surveys/acs/summary_file/{y}/data/1_year_by_state/{stn}_All_Geographies.zip'
        try:
            it = []
            f.retrlines('LIST ' + remote, lambda l: it.append(l))
            exp = int(it[0].split()[4])
            if os.path.exists(local) and os.path.getsize(local) == exp:
                skip += 1
                continue
            with open(local,'wb') as fh:
                f.retrbinary('RETR ' + remote, fh.write, blocksize=1<<20)
            ok += 1
            print('OK', y, ab, os.path.getsize(local), flush=True)
        except Exception as e:
            err += 1
            print('ERR', y, ab, str(e)[:100], flush=True)
            f = ftplib.FTP('ftp.census.gov', timeout=300)
            f.login()
f.quit()
print(f'DONE ok={ok} skip={skip} err={err}')
