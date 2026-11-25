import json
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
murders = json.load(open(B + 'murders_all_v1.json', encoding='utf-8'))
# the 2012 + 2013-class = the the wide-cities:
for c in ('Austin', 'Dallas', 'Philadelphia', 'Seattle'):
    got = [(k.split('|')[1], v) for k, v in murders.items() if k.startswith(c + '|') and k.split('|')[1] in ('1992', '2012', '2013')]
    print(c, got)
