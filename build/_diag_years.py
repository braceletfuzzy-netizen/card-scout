import json
# DIAG-3 = the year-formats = the the crime-file-years (the the '2024-25'-class):
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/'
for f in ('crime_series_wave1.jsonl', 'crime_series_wave1b.jsonl'):
    ys = [json.loads(l).get('year') for l in open(B + f, encoding='utf-8') if l.strip()]
    print(f, '->', sorted(set(str(y) for y in ys))[:12])
