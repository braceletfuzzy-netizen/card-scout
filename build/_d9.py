import json
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
murders = json.load(open(B + 'murders_all_v1.json', encoding='utf-8'))
for c in ('Austin', 'Dallas', 'Philadelphia', 'Seattle', 'San Diego'):
    for y in (2012,):
        k = f'{c}|{y}'
        print(k, '->', murders.get(k))
