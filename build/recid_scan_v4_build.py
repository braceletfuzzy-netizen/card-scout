import json, urllib.request, re, html

# Build peer_review_scan_v4.jsonl — BOB-THIRD recidivism scan (all rows abstract-verified this run)
UA = {"User-Agent": "PolyScout-peer-scan/1.0 (mailto:research-ops@example.org)"}
with open(r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/recid_v4_metadata.json", encoding="utf-8") as f:
    meta = json.load(f)

# authors for keys we never stored
AUTHORS = {}
for k in ["PrisonJ2014", "Kim2026_jsocsci"]:
    doi = meta[k]["crossref_doi"]
    req = urllib.request.Request(f"https://api.crossref.org/works/{doi}", headers=UA)
    m = json.loads(urllib.request.urlopen(req, timeout=30).read())["message"]
    AUTHORS[k] = ", ".join(f"{a.get('given','')} {a.get('family','')}".strip() for a in (m.get("author") or []))
print("PrisonJ2014 authors:", AUTHORS.get("PrisonJ2014"))
print("Kim2026 authors:", AUTHORS.get("Kim2026_jsocsci"))
print("PubMed row text head:", (meta.get("Mancino2023_ss_1", {}).get("pubmed_abstract") or "")[:120])

def mk(tid, authors, year, title, venue, key_finding, hypothesis, effect_size, design, n, cost, url, conf, note=""):
    return {"id": tid, "authors": authors, "year": year, "title": title, "venue": venue,
            "key_finding": key_finding, "hypothesis_addressed": hypothesis,
            "effect_size": effect_size, "design_class": design, "N": n,
            "cost_per_unit_where": cost, "url": url, "confidence": conf, "note": note}

rows = []
rows.append(mk("davis2013_rand_rr266", "Lois M. Davis, Robert Bozick, Jennifer L. Steele, Jessica Saunders, Jeremy N. V. Miles", 2013,
  "Evaluating the Effectiveness of Correctional Education: A Meta-Analysis of Programs That Provide Education to Incarcerated Adults",
  "RAND Corporation (RR-266)",
  "Comprehensive meta-analysis: correctional education while incarcerated reduces inmates' risk of recidivating and may improve post-release employment odds.",
  "education", "-13 percentage points recidivism risk vs non-participants (per rand.org RR-266/RB-9728 landing text)",
  "meta-analysis (comprehensive literature search)", "57 studies (recidivism), 21 (employment)",
  None, "https://www.rand.org/pubs/research_reports/RR266.html",
  "cited-in-abstract (OpenAlex abstract + RAND landing page verified)", "the founder's anchor study; 13pp figure verified on rand.org this run"))
rows.append(mk("bozick2018_jec", "Robert Bozick, Jennifer Steele, Lois Davis, Heather Turner", 2018,
  "Does providing inmates with education improve postrelease outcomes? A meta-analysis of correctional education in the United States",
  "Journal of Experimental Criminology",
  "In highest-caliber research designs, correctional-education participants were 28% less likely to recidivate than non-participants; but participants were AS likely to obtain post-release employment.",
  "education", "28% lower recidivism likelihood (highest-caliber designs); employment effect NULL",
  "meta-analysis, random-effects regression", "57 recidivism studies, 21 employment studies (1980-2017)",
  None, "https://doi.org/10.1007/s11292-018-9334-6",
  "cited-in-abstract (Springer page abstract loaded)", "education→recidivism YES, education→jobs NO: separates the two mechanisms"))
rows.append(mk("landenberger_lipsey2005", "Neal A. Landenberger, Mark W. Lipsey", 2005,
  "The positive effects of cognitive-behavioral programs for offenders: a meta-analysis of factors associated with effective treatment",
  "Journal of Experimental Criminology",
  "Meta-analysis of 58 experimental/quasi-experimental studies confirmed CBT reduces offender recidivism; larger effects with higher-risk offenders, high-quality implementation, and programs including anger control + interpersonal problem solving.",
  "other", "positive recidivism reductions confirmed (magnitude not stated in abstract)",
  "meta-analysis (58 experimental + quasi-experimental studies)", "58 studies", None,
  "https://doi.org/10.1007/s11292-005-3541-7",
  "cited-in-abstract (Springer page abstract loaded)", "CBT = the canonical class the founder didn't name: it outperforms all three of his arms in effect density"))
rows.append(mk("lipsey2007_campbell", "Mark W. Lipsey, Neal A. Landenberger, Suzanne J. Wilson", 2007,
  "Effects of Cognitive-Behavioral Programs for Criminal Offenders",
  "Campbell Systematic Reviews",
  "CBT prevents continuation of criminal careers; implementation quality and well-trained providers matter more than program type or setting (prison vs community made no difference).",
  "other", "significant recidivism reductions; no differences by program brand or setting",
  "Campbell systematic review / meta-analysis", "58 studies (per review family)", None,
  "https://doi.org/10.4073/csr.2007.6",
  "cited-in-abstract (Crossref abstract loaded)", ""))
rows.append(mk("kim2026_postsec_review", AUTHORS.get("Kim2026_jsocsci", ""), 2026,
  "Postsecondary Education Programs Among Incarcerated and Formerly Incarcerated Adults: A Systematic Review of Recidivism Outcomes",
  "Journal of Social Science and Human Research Studies",
  "PRISMA-2020 review of 15 studies: postsecondary education is associated with lower recidivism, but the association weakens as methodological rigor increases; strongest for credential completion.",
  "education", "positive association; strength diminishes with rigor",
  "systematic review (PRISMA 2020, narrative synthesis)", "15 studies", None,
  "https://doi.org/10.65150/ep-jsshrs/v2e7/2026-29",
  "cited-in-abstract (Crossref abstract loaded)", "2026 sanity-check on the education lane: direction survives, rigor gap flagged"))
rows.append(mk("prison_journal_2014", AUTHORS.get("PrisonJ2014", ""), 2014,
  "The Effects of Prison-Based Educational Programming on Recidivism and Employment",
  "The Prison Journal",
  "Among Minnesota releases 2007-2008: a secondary degree increased odds of post-release employment but had NO significant recidivism effect; a post-secondary degree was associated with more hours worked, higher wages, and less recidivism.",
  "education", "post-secondary: less recidivism + higher wages; secondary: employment only, recidivism null",
  "observational (administrative cohort)", "MN prison releases 2007-2008", None,
  "https://doi.org/10.1177/0032885514548009",
  "cited-in-abstract (Crossref abstract loaded)", "level-of-credential matters: splits education into effective vs ineffective variants"))
rows.append(mk("mcneeley2023_vocational", "Susanne McNeeley", 2023,
  "The Effects of Vocational Education on Recidivism and Employment Among Individuals Released Before and During the COVID-19 Pandemic",
  "International Journal of Offender Therapy and Comparative Criminology",
  "Propensity-score-matched evaluation: NO differences in any outcome between vocational-certificate participants and comparison group; prior positive findings attributed to selection bias.",
  "jobs", "NULL after matching (all outcomes)",
  "observational with propensity-score matching", "MN releases (pre/during COVID window)", None,
  "https://doi.org/10.1177/0306624X231159886",
  "cited-in-abstract (Crossref + PubMed abstracts loaded)", "the honest-null class: vocational ed effect collapses once selection is controlled"))
rows.append(mk("skardhamar_telle2012", "Torbjørn Skardhamar, Kjetil Telle", 2012,
  "Post-release Employment and Recidivism in Norway",
  "Journal of Quantitative Criminology",
  "All 2003 Norwegian prison releases followed monthly (N=7,476): employed ex-inmates show raw recidivism hazard 0.12x, but after adjusting for observable characteristics it is 0.50x — a large share of the employment-recidivism association is selection; residual association persists.",
  "jobs", "raw hazard ratio 0.12 → adjusted 0.50 (p<.001), employment months only",
  "registry cohort, discrete-time survival, time-varying covariates", "N=7,476", None,
  "https://doi.org/10.1007/s10940-012-9166-x",
  "cited-in-abstract (Springer page abstract loaded)", "the definitive honest partial-null for the jobs lane: ~2/3 of the raw effect is selection"))
rows.append(mk("berger_gross2022", "Andrew Berger-Gross", 2022,
  "The Impact of Post-Release Employment on Recidivism in North Carolina",
  "SSRN (working paper)",
  "2016 NC prison-exit cohort: early post-release employment is associated with lower 2-year reincarceration; top-quartile earners ~half as likely to be reincarcerated, effect varies sharply by earnings level.",
  "jobs", "top-quartile earnings ≈ 50% lower reincarceration; weaker at low earnings",
  "observational cohort, covariate-controlled", "2016 NC exit cohort", None,
  "https://doi.org/10.2139/ssrn.4083166",
  "cited-in-abstract (Crossref abstract loaded)", "conflict-of-interest flag: working paper, not peer-reviewed venue"))
rows.append(mk("bhuller2016_nber", "Manudeep Bhuller, Gordon B. Dahl, Katrine V. Loken, Magne Mogstad", 2016,
  "Incarceration, Recidivism and Employment",
  "NBER Working Paper No. 22648",
  "Judge-stringency IV, full Norwegian population panel: incarceration cuts 5-year reoffending by 29pp; the reduction is driven entirely by individuals who were NOT working before incarceration — prison raises program participation, employment, and earnings for them.",
  "other", "-29 percentage points reoffending within 5 years; -11 criminal charges; effect concentrated among the previously non-employed",
  "quasi-experimental IV (judge stringency)", "entire Norwegian population panel", None,
  "https://doi.org/10.3386/w22648",
  "cited-in-abstract (OpenAlex abstract loaded)", "the jobs mechanism works THROUGH prison programs, not post-release hiring schemes"))
rows.append(mk("duwe2011_mcorp_jq", "Grant Duwe", 2011,
  "Evaluating the Minnesota Comprehensive Offender Reentry Plan (MCORP): Results from a Randomized Experiment",
  "Justice Quarterly",
  "RCT of a reentry pilot increasing community-service access via improved prison-community case-management collaboration: significantly reduced rearrest, reconviction, and new-offense reincarceration; effects mediated by employment, community support programming (mentoring, restorative justice, faith-based), and social-support systems.",
  "community", "significant reductions in all three reoffending types (coefficients not in abstract)",
  "randomized controlled trial", "MCORP 2008 pilot sample", None,
  "https://doi.org/10.1080/07418825.2011.555414",
  "cited-in-abstract (OpenAlex abstract loaded)", "the community lane's best causal result: access-to-services + social support, not one service type"))
rows.append(mk("duwe2013_mcorp_cjs", "Grant Duwe", 2013,
  "A randomized experiment of a prisoner reentry program: updated results from an evaluation of the Minnesota Comprehensive Offender Reentry Plan",
  "Criminal Justice Studies",
  "Cox regressions from the same MCORP RCT: significant reductions on 4 of 5 recidivism measures, hazard-ratio reductions of 20-25%; cost-avoidance estimates not robust across assumptions.",
  "community", "20-25% hazard-ratio reductions on 4/5 measures",
  "randomized controlled trial (Cox regression)", "MCORP 2008 pilot sample", None,
  "https://doi.org/10.1080/1478601x.2013.850081",
  "cited-in-abstract (OpenAlex abstract loaded)", "supplies the quantified effect size the 2011 JQ paper left out"))
rows.append(mk("laub_sampson1990", "Robert J. Sampson, John H. Laub", 1990,
  "Crime and Deviance over the Life Course: The Salience of Adult Social Bonds",
  "American Sociological Review",
  "Glueck data reanalysis: despite childhood-delinquency continuity, job stability and strong marital attachment in adulthood inhibit adult criminal behavior — informal social control explains change over the life course.",
  "community", "directional (inhibiting); no single effect size in abstract",
  "longitudinal, natural-history reanalysis", "Glueck samples, ages 7-32", None,
  "https://doi.org/10.2307/2095859",
  "cited-in-abstract (OpenAlex abstract loaded)", "the theoretical base of the community/family lane: work AND marriage bonds, causal tone correlational"))
rows.append(mk("visher_travis2003", "Christy A. Visher, Jeremy Travis", 2003,
  "Transitions from Prison to Community: Understanding Individual Pathways",
  "Annual Review of Sociology",
  "600,000+ released from state/federal prisons in 2002 (4x the 1975 level); within 3 years almost 7 in 10 rearrested and half returned to prison; reentry pathways are shaped by community-level barriers and supports.",
  "other", "descriptive (68% rearrest within 3 years)",
  "narrative review / synthesis", "national reviews", None,
  "https://doi.org/10.1146/annurev.soc.29.010202.095931",
  "cited-in-abstract (Crossref abstract loaded)", "scale-setting: why recidivism is a policy target at all"))

with open(r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/peer_review_scan_v4.jsonl", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"\nWROTE {len(rows)} rows to peer_review_scan_v4.jsonl")
cnt = sum(1 for _ in open(r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/peer_review_scan_v4.jsonl", encoding="utf-8"))
print("JSONL line count verified:", cnt)
from collections import Counter
print("By hypothesis:", dict(Counter(r["hypothesis_addressed"] for r in rows)))
print("By confidence:", dict(Counter(r["confidence"].split()[0] for r in rows)))
