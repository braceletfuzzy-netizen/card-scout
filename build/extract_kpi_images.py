import pymupdf

PDF = "C:/Users/J/AppData/Local/Temp/memphis_fy26_adopted.pdf"
OUT = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/"
doc = pymupdf.open(PDF)

for pno in (349, 371):
    page = doc[pno]
    for im in page.get_images(full=True):
        xref, w, h = im[0], im[1], im[2]
        if w < 200:  # skip the 60x60 logo
            continue
        info = doc.extract_image(xref)
        path = f"{OUT}kpi_p{pno}_img.{info['ext']}"
        with open(path, "wb") as f:
            f.write(info["image"])
        print("WROTE", path, f"{w}x{h}")

# also render the full pages at 200dpi as backup/context (header rows sometimes
# live in page text, e.g. column headers rendered as text)
for pno in (349, 371):
    pix = doc[pno].get_pixmap(dpi=200)
    path = f"{OUT}kpi_p{pno}_page.png"
    pix.save(path)
    print("WROTE", path, pix.width, "x", pix.height)
