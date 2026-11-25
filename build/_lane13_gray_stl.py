"""St. Louis CSB (311) per-year counts + top GROUP breakdown from the downloaded per-year CSVs."""
import csv, json, collections, os

DIR = "C:/Users/J/_stl_csb"
out = {"by_year": {}, "groups_by_year": {}}
for yr in range(2008, 2027):
    p = os.path.join(DIR, f"{yr}.csv")
    if not os.path.exists(p):
        continue
    n = 0
    groups = collections.Counter()
    with open(p, encoding="utf-8", errors="replace", newline="") as fh:
        rd = csv.reader(fh)
        header = next(rd, None)
        if header is None or "GROUP" not in header:
            print(yr, "EMPTY/BROKEN HEADER — skipped", flush=True)
            continue
        gi = header.index("GROUP")
        for row in rd:
            n += 1
            if len(row) > gi:
                groups[row[gi] or "unknown"] += 1
    out["by_year"][str(yr)] = n
    out["groups_by_year"][str(yr)] = dict(groups)
    print(yr, n, "groups:", len(groups), flush=True)

json.dump(out, open("C:/Users/J/_lane13_gray_stlouis_raw.json", "w"))
print("SAVED stl")
