import pymupdf, re

PDF = "C:/Users/J/AppData/Local/Temp/memphis_fy26_adopted.pdf"
doc = pymupdf.open(PDF)
print("total pages:", doc.page_count)

hits = []
for pno in range(335, min(385, doc.page_count)):
    text = doc[pno].get_text("text")
    has_kpi = ("Key Performance Indicator" in text) or ("Performance Indicators" in text)
    has_pw = "Public Works" in text
    has_parks = ("Memphis Parks" in text) or ("Parks and Neighborhood" in text) or ("Parks & Neighborhood" in text)
    if has_kpi or has_pw or has_parks:
        # first non-empty lines for a quick title read
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()][:12]
        hits.append((pno, has_kpi, has_pw, has_parks, lines))

for pno, k, pw, pk, lines in hits:
    print(f"\n=== page {pno} | KPI={k} PW={pw} PARKS={pk} ===")
    for ln in lines:
        print("   ", ln)
print("\nDONE scan")
