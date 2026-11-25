import json
from datetime import date

# THE MEMPHIS-PRIMARY-ISSUES TABLE (the machine-pulled, the founder-verify-next per the ask)
issues_table = {
    "generated": "2026-11-20",
    "city": "Memphis, TN",
    "method": "news-sweep (the Bing-via-BD + the DDG) — the local-press + the city's-own-SOTC framing; the founder-lane = the verify",
    "sources_key": ["the City's own State-of-the-City 2026 (the Mayor Paul Young)", "the local-press (the Commercial Appeal/Action-News-5/WREG/WATN-class)", "the 2026-State-of-Memphis-Housing-Report", "the federal-Task-Force-reporting"],
    "issues": [
        {
            "rank": 1,
            "issue": "PUBLIC SAFETY / CRIME",
            "evidence": [
                "the Memphis-Safe-Task-Force = the 1-year-mark: the 12,000+ arrests, the 2,100-guns-class (the federal-memorandum = the Jan-2026-launched)",
                "the Mayor-SOTC-2026: the 'historic progress on public safety' = the ~40%-crime-reduction-claim (the mayor's-own-number, the verify-lane)",
                "the MPD = the Q3-2026 public-safety-presentation (the city's-own-reporting-lane)"
            ],
            "budget_touchpoints": "the Police $308.3M (17.7%) + the Fire $246.7M (14.2%) = the 31.8%-of-the-operating = the largest-share",
            "verify_ask": "the founder: the does-the-40%-down = the match-the-lived-reality?"
        },
        {
            "rank": 2,
            "issue": "HOUSING (the affordability-crisis)",
            "evidence": [
                "the 2026-State-of-Memphis-Housing-Report: the city = the short-~28,000-units (the affordable-at-30%-AMI-class) — the official-report-figure",
                "the WATN-'Memphis-facing-possible-housing-crisis' (the 3-days-old)",
                "the WREG: the Mayor-Young = the outlined-the-housing-strategy (the SOTC = the Tuesday)",
                "the report's-own-headline: the 'more-homes-will-NOT-fix-Memphis-housing-problem' (the structural-frame = the displacement/the-income-classes)"
            ],
            "budget_touchpoints": "the Affordable-Housing-Fund = the $2.65M-adopted (the 0.15%-of-the-budget) + the HCD = the $6.29M — the crisis-vs-spend misfit = the founder's-flag = the CONFIRMED-by-the-scale-mismatch",
            "verify_ask": "the founder: the blight-vs-the-affordability = the which-hurts-first?"
        },
        {
            "rank": 3,
            "issue": "BLIGHT / DEMOLITION (the neighborhood-decay)",
            "evidence": [
                "the 100-Demo-campaign: the ~100-vacant-blighted-homes = the demolished-in-60-days (the Sep-2026)",
                "the press = the 'blight, illegal-dumping, abandoned-homes' = the what-Memphis-is-doing (the ongoing-coverage)"
            ],
            "budget_touchpoints": "the code-enforcement/the-public-works-lanes (the blight = the cross-cutting)",
            "verify_ask": "the founder: the 100-homes = the progress = the drop-in-the-bucket?"
        },
        {
            "rank": 4,
            "issue": "YOUTH OPPORTUNITY / EDUCATION-ADJACENT (the city-side)",
            "evidence": [
                "the SOTC-pillar-3 = the 'opening-doors-to-opportunity-for-the-young-people'",
                "the MSCS-district = the separate-$1.9B-body = the state-takeover-paused-in-court + the TVAAS-growth-collapse (the SS003.9 = the founder's-own-lived-lane)"
            ],
            "budget_touchpoints": "the city-Pre-K-fund $7.0M + the libraries $26.1M = the city-side-small; the district = the separate-budget-lane",
            "verify_ask": "the founder: the district-grain-row = the worth-the-add? (the $1.9B = the bigger-than-the-city-itself)"
        },
        {
            "rank": 5,
            "issue": "STREETS / INFRASTRUCTURE (the 911/EMS/potholes)",
            "evidence": [
                "the thin-sweep (the search-yield = the lower-density on-this-lane) — the honest-flag: the needs-the-second-pass (the MLK40/the-Commercial-Appeal-deep-dive)",
                "the Public-Works $203M (the 11.6%) + the City-Engineer $15.2M = the budget-touchpoints"
            ],
            "budget_touchpoints": "the infra-class = the ~18.5%-bucket",
            "verify_ask": "the founder: the potholes/the-response-times = the rank-where-vs-the-first-four?"
        }
    ],
    "meta_finding": "THE MAYOR'S-OWN-FRAME (the SOTC-2026) = the four-pillars: the public-safety-progress + the housing-growth + the youth-opportunity + the culture = THE city's-self-declared-scorecard = the PolyScout's ready-made-verify-list (the every-pillar = the scoreable-class).",
    "honest_flags": [
        "the 40%-crime-reduction = the mayor's-claim (the not-the-machine-verified — the verify = the founder's-lane or-the next-pass)",
        "the streets/911-lane = the thinnest-sweep (the needs-the-depth-pass)",
        "the housing-crisis-vs-the-$2.65M-scale = the misfit = the machine-confirmed; the fix-debate = the not-ours"
    ]
}

json.dump(issues_table, open('C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/memphis_primary_issues.json', 'w', encoding='utf-8'), indent=1)
print('WROTE memphis_primary_issues.json')
