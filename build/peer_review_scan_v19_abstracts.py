#!/usr/bin/env python3
# Print full abstracts for the v19 magnitude-candidate set (extract countable numbers).
import json, os, re, textwrap
B = os.path.dirname(os.path.abspath(__file__))
corpus = json.load(open(os.path.join(B, "peer_review_scan_v19_corpus.json"), encoding="utf-8"))
recs = corpus["records"]

KEYS = [
 # fiscal
 "State Rainy Day Funds and Fiscal Crises",
 "State Rainy Day Funds and Government General Fund",
 "Saving for a rainy day",
 "Is There an Optimal Size of Fiscal Reserves",
 "City Revenue Structure and Unfunded Pension",
 "CREDIT RISK, CREDIT RATINGS, AND MUNICIPAL BOND YIELDS",
 "Municipal pension funding: A theory",
 "fiscal slack in a political-budgetary-managerial",
 "general fund balances of major American",
 "Will Public Sector Retiree Health Benefit Plans Survive",
 # econ
 "The Effect of State Tax Incentives on Economic Growth and Firm Location",
 "The Impact of Enterprise Zones on Resident Employment",
 "Tax Costs and Employment Benefits of Enterprise Zones",
 "Simulating the Effects of the Tax Credit Program of the Michigan",
 "Does the Job Creation Tax Credit Program in Maryland",
 "Job Creation Tax Credits, Fiscal Foresight",
 "Do Tax Incentives Affect Business Location and Economic Development",
 "Who Benefits From State and Local Economic Development",
 # infra
 "Preventive and corrective maintenance",
 "Pavement Preventive Maintenance: Description, Effectiveness",
 "Using Simulation to Understand the Impact of Deferred Maintenance",
 "marginal cost of pavement damage",
 "participatory assessment technique for infrastructure",
 "Life cycle cost analysis for managing rail",
 # housing/edu
 "The Effects of School Spending on Educational and Economic Outcomes",
 "School Finance Reform and the Distribution of Student Achievement",
 "Long-Run Price Elasticity of Supply of New Residential Construction",
 "Housing affordability and family well",
 "Long-term effects of public low-income housing vouchers",
 "Density zoning and class segregation",
 "Do Strict Land Use Regulations Make Metropolitan Areas More Segregated",
 "Housing supply and housing affordability",
 # prism
 "Evaluating Program and Managerial Efficiency",
 "Determinants of efficiency in the provision of municipal street-cleaning",
 "The efficiency of municipal solid waste collection in Mexico",
 "Measuring efficiency in the public sector using nonparametric frontier",
 "The Efficiency Frontier as a Method for Gauging",
 "Cost Efficiency of Macedonian Municipalities",
 "Fiscal Decentralization and Efficiency of Regional Government in Croatia",
 "efficiency of China",
 "efficiency of municipal solid waste management efficiency in EU",
 "Local Government Service Efficiency: Public Participation",
 "willingness to adopt process innovations",
 "efficiency of water service in Brazilian",
 "Cost Efficiency of Public Procurement at Local Level",
]

for k in KEYS:
    match = next((r for r in recs if k.lower() in (r.get("title") or "").lower()), None)
    print("=" * 100)
    if not match:
        print(f"!! NO MATCH: {k}"); continue
    ab = re.sub(r"<[^>]+>", "", match.get("abstract") or "").strip()
    print(f"[{match.get('cited')}] {match.get('year')} | {match['title']}")
    print(f"   {match.get('venue')} | {match.get('url')}")
    if ab:
        print(textwrap.fill(ab, 115, initial_indent="   ", subsequent_indent="   ")[:1400])
    else:
        print("   (no abstract in corpus)")
