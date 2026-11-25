import json

# Summarize anchor candidates (Phase 2 output review)
with open(r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/recid_v4_anchors.json", "r", encoding="utf-8") as f:
    anchors = json.load(f)

for key, items in anchors.items():
    print(f"=== {key} ===")
    for it in items:
        doi = it.get("DOI", "")
        t = (it.get("title") or [""])[0]
        yr = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        ven = (it.get("container-title") or [""])[0]
        au = ", ".join(a.get("family", "") for a in (it.get("author") or [])[:4])
        print(f"  {doi} | {yr} | {ven[:40]} | {au[:40]} | {t[:95]} | abst={bool(it.get('abstract'))}")
    print()
