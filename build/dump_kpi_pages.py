import pymupdf

PDF = "C:/Users/J/AppData/Local/Temp/memphis_fy26_adopted.pdf"
doc = pymupdf.open(PDF)
for pno in (349, 371):
    print(f"\n{'='*70}\nFULL TEXT page {pno}\n{'='*70}")
    print(doc[pno].get_text("text"))
