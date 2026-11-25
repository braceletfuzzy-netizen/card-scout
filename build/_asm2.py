import json
SOC = 'C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/_soc/'
acs = json.load(open(SOC + 'acs_pov_bch.json', encoding='utf-8'))
print('count:', len(acs))
print('sample[0]:', acs[0])
print('sample[-1]:', acs[-1])
# the FRED = the sample:
fred = open(SOC + 'fred_LAUCN295100000000003A.csv', encoding='utf-8').read()
print()
print('FRED-STL-head:', fred[:400])
