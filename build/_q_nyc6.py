import json
rows = [json.loads(l) for l in open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/crime_series_wave1.jsonl', encoding='utf-8') if l.strip()]
# the last-12 = the my-appendix:
for r in rows[-13:]:
    print(r.get('city'), r.get('year'), '| murders', r.get('murders'), '| pop', r.get('population'), '|', str(r.get('notes'))[:60])
