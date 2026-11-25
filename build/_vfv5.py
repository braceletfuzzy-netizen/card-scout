h = open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/band_board_v5.html', encoding='utf-8').read()
import re
vals = re.findall(r'100\.0|141\.3|139\.2|54\.4', h)
print('normalized-cells-found:', len(vals), vals[:8])
print('v2-mention:', 'v2' in h)
