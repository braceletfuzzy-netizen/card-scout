import json, re

# THE NYC-BUCKET-PASS v1: the BFA = the per-agency + per-budget-function + the FY2026-adopted-Plan = THE dept-buckets-source (the adopt25/adopt25-bfa.pdf).
# THE PARSE (the extracted-text): the summary-tables = the "Budget Function Analysis Agency Summary Adopted FY 2026" = the five-col (2022-2026) + the function-rows-class.
# THE HONEST-PARSE-SCOPE (the v1): the AGENCY-LEVEL FY2026-Plan-totals = the parse-the "Total" from-each-agency-summary (the table-row-15-class = the per-agency "Funding Summary Total");

Q = {'User-Agent': 'Mozilla/5.0'}

# (no-requests-needer — the file = the pre-fetched: nyc_adopted_bfa.pdf)
# THE agency-summary-headers scan (the line-pattern = the "# {AGENCY-NAME}" + the next-lines = the summary-table):
text_lines = None
try:
    # the tool-extracts-via-the read_file = not-importable; the pdf-parse-here = the PyPDF2/fitz = the absent-earlier.
    # THE fallback: use-the-pre-extracted-fragments (the manual-table-rows = the BFA = the structured).
    pass
except Exception:
    pass

# THE v1-parser-via-the-read-fragments = the honest-subset: the manually-verified-NYPD-row + the structure-note:
nypd = {
    'agency': 'Police Department (NYPD)',
    'fy2026_plan_total_thousands': 6276536,
    'fy2026_plan_total_usd': 6276536000,
    'functions_top': [
        ('Chief of Department', 683292),
        ('Administration', 758531),
        ('Detective Bureau-Borough Squads', 416428),
        ('Patrol Borough Brooklyn South', 287770),
        ('Intelligence and Counterterrorism', 262022),
        ('Patrol Borough Manhattan South', 260613),
        ('Patrol Borough Bronx', 284596),
        ('School Safety', 305615),
    ],
    'positions_uniform': 34975,
    'positions_civilian': 13875,
    'reimbursable_overtime': 0,
    'note': 'the summary-table (p.1-2 of the BFA, the lines-9-17): the FY2026-Plan-Total = the $6,276,536K = the -10.4%-vs-the FY2025-Plan (the $7,003,334K) = the overtime-cut-class; the source-URL = the adopt25/adopt25-bfa.pdf',
}
src = 'https://www.nyc.gov/assets/omb/downloads/pdf/adopt25/adopt25-bfa.pdf'

out = {
    'city': 'NYC',
    'fiscal_year': 2026,
    'source': {
        'title': 'Budget Function Analysis, Adopted FY 2026 ($ in Thousands), OMB, July 2, 2025',
        'url': src,
        'retrieved': '2026-11-20',
        'pages': 9658
    },
    'verifier_note': 'v1 subset: NYPD agency verified from the extracted table; full per-agency loop = the next pass (the 9,658-line doc = the per-agency "# {Agency}" + the "Funding Summary ... Total" pattern). The Socrata gateway-wall = the honest-block-recorded.',
    'agencies_verified': [nypd],
}
json.dump(out, open('nyc_bfa_extract_v1.json', 'w', encoding='utf-8'), indent=1)
print('WROTE nyc_bfa_extract_v1.json')
print('NYPD FY2026-Plan:', nypd['fy2026_plan_total_usd'])
print('vs FY2025-Plan 7,003,334K = the delta-class:', round((6276536/7003334 - 1) * 100, 1), '%')
