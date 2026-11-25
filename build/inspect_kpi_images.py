import pymupdf

PDF = "C:/Users/J/AppData/Local/Temp/memphis_fy26_adopted.pdf"
doc = pymupdf.open(PDF)

for pno in (349, 371):
    page = doc[pno]
    imgs = page.get_images(full=True)
    draws = page.get_drawings()
    print(f"page {pno}: images={len(imgs)} drawings={len(draws)} words={len(page.get_text('words'))}")
    for i, im in enumerate(imgs):
        xref = im[0]
        info = doc.extract_image(xref)
        print(f"  img{i}: {info['width']}x{info['height']} ext={info['ext']}")
    # where are the images placed?
    for i, im in enumerate(imgs):
        try:
            rects = page.get_image_rects(im[0])
            for r in rects:
                print(f"  img{i} rect: {r}")
        except Exception as e:
            print("  rect err", e)
