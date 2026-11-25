import json
# BOARD-V5 = the v2-normalized-CARE+ = the re-render!
src = open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/board_v4.py', encoding='utf-8').read()
src = src.replace("crime_plus_care_plus_v1.json", "crime_plus_care_plus_v2.json")
src = src.replace("carep = f\"{round(cc*100,1)}\" if cc else '—'", "carep = str(r.get('care_plus_normalized')) if r.get('care_plus_normalized') else '—'")
src = src.replace("band_board_v4.html", "band_board_v5.html")
src = src.replace("Board v4", "Board v5")
src = src.replace("(direction inverts)", "(band-normalized v2 — founder-caught fix; direction inverts)")
open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/board_v5.py', 'w', encoding='utf-8').write(src)
print('v5-script = written')
