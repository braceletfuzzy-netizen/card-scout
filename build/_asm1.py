import json, re
from collections import defaultdict
SOC = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/_soc/'
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'

# === 1. ACS 2021-2025 = the acs_pov_bch.json (already-extracted-by-the-child!) ===
acs = json.load(open(SOC + 'acs_pov_bch.json', encoding='utf-8'))
print('ACS-structure-keys:', list(acs.keys())[:5])
sample = acs[list(acs.keys())[0]]
print('acs-sample:', str(sample)[:200])
