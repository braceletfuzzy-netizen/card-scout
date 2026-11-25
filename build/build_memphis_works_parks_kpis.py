# THE MEMPHIS KPI DEEP-SCAN #3 — Public Works + Memphis Parks
# Per WALLE_BRIEF_memphis_kpi.md. Source: local PDF
# C:/Users/J/AppData/Local/Temp/memphis_fy26_adopted.pdf (27,333,848 bytes, 381 pages).
#
# METHOD (dual-record):
#  1. pymupdf text scan of pages 335-380 -> KPI tables are IMAGE-EMBEDDED
#     (no text layer; page 349 has 15 words, page 371 has 15 words = header only).
#  2. Embedded PNGs extracted: kpi_p349_table.png (1077x720),
#     kpi_p371_table.png (803x271).
#  3. Machine-vision transcription (2-pass: full read + digit-level verify,
#     4 vision passes total). Zero UNREADABLE cells. Digit verification
#     4/4 consistent across passes.
#  4. Provenance: every row carries its source pdf-page index.
#  5. NEVER fabricated: no value below is inferred; all read from the tables.
import json
from datetime import date

PW_PAGE = 371     # pdf-page index; book-page 372
PARKS_PAGE = 349  # pdf-page index; book-page 350

pw_rows = [
    {"metric": "Repaving cycle (years)", "fy24_actual": 25, "fy25_goal": 30,
     "fy25_actual": 30, "fy26_goal": 30, "category": "Neighborhoods"},
    {"metric": "Street repairs performed annually (#)", "fy24_actual": 6929,
     "fy25_goal": 7000, "fy25_actual": 8679, "fy26_goal": 8000,
     "category": "Neighborhoods"},
    {"metric": "Quantity of litter removed from right of way (yards)",
     "fy24_actual": 21500, "fy25_goal": 20000, "fy25_actual": 22688,
     "fy26_goal": 20000, "category": "Neighborhoods"},
    {"metric": "Average time to fill potholes in response to citizen request (days)",
     "fy24_actual": "3.0", "fy25_goal": "4.0", "fy25_actual": "2.7",
     "fy26_goal": "3.0", "category": "Neighborhoods"},
]

parks_rows = [
    {"section": "Community Centers",
     "goal_text": "Provide recreational programs that align with resident feedback and emerging trends",
     "metric": "Community Center Adult attendance", "fy24_actual": 202294,
     "fy25_goal": 208000, "fy25_actual": 271944, "fy26_goal": 285541},
    {"section": "Community Centers",
     "goal_text": "Provide recreational programs that align with resident feedback and emerging trends",
     "metric": "Community Center Youth attendance", "fy24_actual": 210968,
     "fy25_goal": 275000, "fy25_actual": 290536, "fy26_goal": 305063},
    {"section": "Community Centers",
     "goal_text": "Provide recreational programs that align with resident feedback and emerging trends",
     "metric": "Senior Center Attendance", "fy24_actual": 86659,
     "fy25_goal": 88000, "fy25_actual": 95328, "fy26_goal": 97711},
    {"section": "Community Centers",
     "goal_text": "Provide recreational programs that align with resident feedback and emerging trends",
     "metric": "Specialty Center Attendance", "fy24_actual": 5703,
     "fy25_goal": 6600, "fy25_actual": 13296, "fy26_goal": 13628},
    {"section": "Community Centers",
     "goal_text": "Provide recreational programs that align with resident feedback and emerging trends",
     "metric": "Summer Camp registrations", "fy24_actual": 2299,
     "fy25_goal": 2420, "fy25_actual": 2168, "fy26_goal": 2276},
    {"section": "Community Centers",
     "goal_text": "Provide recreational programs that align with resident feedback and emerging trends",
     "metric": "Meals served to youth", "fy24_actual": 282301,
     "fy25_goal": 302500, "fy25_actual": 290532, "fy26_goal": 297795},
    {"section": "Community Centers",
     "goal_text": "Provide recreational programs that align with resident feedback and emerging trends",
     "metric": "Meals served to seniors", "fy24_actual": 38080,
     "fy25_goal": 38500, "fy25_actual": 36996, "fy26_goal": 37921},
    {"section": "Recreation",
     "goal_text": "Provide recreational programs that align with resident feedback and emerging trends",
     "metric": "Golf rounds", "fy24_actual": 160184, "fy25_goal": 167200,
     "fy25_actual": 168052, "fy26_goal": 176455},
    {"section": "Recreation",
     "goal_text": "Provide recreational programs that align with resident feedback and emerging trends",
     "metric": "Youth golf rounds", "fy24_actual": 7469, "fy25_goal": 7700,
     "fy25_actual": 9370, "fy26_goal": 9839},
    {"section": "Recreation",
     "goal_text": "Provide recreational programs that align with resident feedback and emerging trends",
     "metric": "Youth Athletics participants", "fy24_actual": 36371,
     "fy25_goal": 36000, "fy25_actual": 42800, "fy26_goal": 44940},
    {"section": "Park Operations",
     "goal_text": "Ensure well-maintained park land, facilities, and public spaces",
     "metric": "Grass Cutting- % of mowing tasks complete within 17 days",
     "fy24_actual": "61.09%", "fy25_goal": "75%", "fy25_actual": "62.70%",
     "fy26_goal": "70%"},
    {"section": "Business Operations",
     "goal_text": "Ensure well-maintained parkland, facilities, and public spaces.",
     "metric": "Parks scheduled reservations", "fy24_actual": 458,
     "fy25_goal": 484, "fy25_actual": 477, "fy26_goal": 500},
    {"section": "Business Operations",
     "goal_text": "Ensure well-maintained parkland, facilities, and public spaces.",
     "metric": "Accounts Payable: % paid in 30 days", "fy24_actual": "82%",
     "fy25_goal": "90%", "fy25_actual": "80%", "fy26_goal": "90%"},
    {"section": "Business Operations",
     "goal_text": "Ensure well-maintained parkland, facilities, and public spaces.",
     "metric": "Grant dollars raised", "fy24_actual": "$943,752",
     "fy25_goal": "$550,000", "fy25_actual": "$469,631", "fy26_goal": "$495,000"},
    {"section": "Community Engagement",
     "goal_text": "Ensure park land facilities and public spaces are accessible by all Memphians",
     "metric": "New Social Media Followers", "fy24_actual": 2713,
     "fy25_goal": 3850, "fy25_actual": 4269, "fy26_goal": 4482},
]

# ---- verify: every row carries all four fields, no nulls sneaked in ----
fields = ("fy24_actual", "fy25_goal", "fy25_actual", "fy26_goal")
honest_nulls = 0
for r in pw_rows + parks_rows:
    for f in fields:
        if r[f] is None or r[f] == "":
            raise SystemExit(f"NULL CELL in {r['metric']}.{f} — fix or null+note")

out = {
    "city": "Memphis",
    "source": "FY26 Adopted Budget Book w/ CIP (local PDF) — KPI tables image-embedded; machine-vision transcribed",
    "url": "https://www.memphistn.gov/wp-content/uploads/2025/10/FY26-Adopted-Budget-Book.pdf",
    "local_pdf": "C:/Users/J/AppData/Local/Temp/memphis_fy26_adopted.pdf",
    "built": str(date.today()),
    "method": "pymupdf text-scan (tables had NO text layer, Fire-division class) -> embedded PNG extracted -> vision transcribe -> 4-pass digit-level verification (all consistent, zero unreadable cells)",
    "kpis_by_division": [
        {
            "division": "Public Works",
            "table_found": True,
            "format": "image-embedded table",
            "source_pdf_page_index": PW_PAGE,
            "source_page_ranges": f"pdf-page {PW_PAGE} (book-page 372)",
            "table_section": "Street Maintenance",
            "rows_extracted": len(pw_rows),
            "rows": pw_rows,
            "cross_reads": [
                "the FY25-vs-goal = the BEATS-class: repairs 8,679 vs 7,000-goal + potholes 2.7d vs 4.0-goal (BETTER than FY24 too) + litter 22,688 vs 20,000-goal — the streets-lane (rank-5 thin-sweep in memphis_primary_issues.json) now has machine-readable countables",
                "THE repaving-cycle = 30-years constant (FY24 25 -> goals 30/30/30) = the honest-infrastructure-signal: the city resurfaces a street every 30 years — the slow-rotation = the structural-frame",
                "the pothole-response = the founder's lived-experience lane now scoreable (2.7-day-mean = the official number; the lived-check = the verify-ask)"
            ]
        },
        {
            "division": "Memphis Parks",
            "table_found": True,
            "format": "image-embedded table",
            "source_pdf_page_index": PARKS_PAGE,
            "source_page_ranges": f"pdf-page {PARKS_PAGE} (book-page 350)",
            "table_section": "5 sections: Community Centers / Recreation / Park Operations / Business Operations / Community Engagement (each carries its own Goal line; rows carry section+goal_text instead of a Category column)",
            "rows_extracted": len(parks_rows),
            "rows": parks_rows,
            "cross_reads": [
                "the attendance-surge-class: adult 202,294->271,944 (+34%), youth 210,968->290,536 (+38%), golf 160,184->168,052, youth-athletics 36,371->42,800 — the post-Lester-center-opening growth-frame ($19.8M facility opened May-2025, performance-highlights p.348)",
                "THE MISSES-class: grass-cutting 62.70% vs 75%-goal (12.3-pt miss, the lived-mowed-lane), accounts-payable-30d 80% vs 90%-goal, summer-camp 2,168 vs 2,420-goal",
                "THE goal-cut-after-miss signal: grant-dollars raised $469,631 vs $550,000-goal (85%) -> FY26 goal CUT to $495,000 (below the old goal) = the honesty-class — while FY24 was $943,752 = the 2-year-collapse (the ~50%-of-FY24 frame)"
            ]
        }
    ],
    "honest_flags": [
        "zero cells unavailable — no nulls, no fabrication needed; both tables read fully",
        "tables are image-embedded in the PDF (the Fire-division-class found WITH tables this time, unlike Fire which had none)",
        "public-works 'Category' column = 'Neighborhoods' on every row (the city's own category label)",
        "parks format differs: no Category column — section headers + Goal lines instead (recorded as section/goal_text)",
    ]
}

path = "C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/memphis_works_parks_kpis_v1.json"
json.dump(out, open(path, "w", encoding="utf-8"), indent=1)
print("WROTE", path)
print(f"rows-per-division: Public Works={len(pw_rows)}, Memphis Parks={len(parks_rows)}")
print(f"honest-nulls-found: {honest_nulls} (all cells read; none needed)")
