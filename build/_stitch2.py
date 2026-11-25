import json
B = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/_outcomes/'
for f in ('nyc_grad_cohorts.json', 'bos_grad_raw.json', 'hisd_4yr_grad.json', 'orleans_grad.json', 'tax_base_est.json'):
    d = json.load(open(B + f, encoding='utf-8'))
    print(f, '| type:', type(d).__name__)
    if isinstance(d, dict):
        ks = list(d.keys())
        print('  keys:', ks[:5])
        v = d[ks[0]]
        print('  sample:', str(v)[:120])
    else:
        print('  head:', str(d[:2])[:150])
