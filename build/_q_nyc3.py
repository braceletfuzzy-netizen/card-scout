import json
rows = json.load(open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/triple_slider_v6c.json', encoding='utf-8'))
print('the cities-in-v6c:', sorted(set(r['city'] for r in rows)))
