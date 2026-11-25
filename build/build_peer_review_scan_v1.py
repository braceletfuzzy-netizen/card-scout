import json, time

# ============================================================
# peer_review_scan_v1.jsonl — BOB-lane peer-reviewed scan
# Only papers whose abstract/page was actually loaded this run
# (OpenAlex inverted-index deinvert, Crossref abstract, PubMed E-utilities,
#  or direct full-text HTML). Confidence tagged accordingly.
# ============================================================

def mk(pid, authors, year, title, venue, key_finding, relevance, cites, url,
       conf, aligned="aligned", note=""):
    return {
        "id": pid,
        "authors": authors,
        "year": year,
        "title": title,
        "venue": venue,
        "key_finding": key_finding,
        "relevance_to_our_pattern": relevance,   # list of pattern numbers 1-5 + label text
        "citation_count": cites,
        "url": url,
        "confidence": conf,                      # cited-in-abstract | cited-in-fulltext | secondhand
        "alignment": aligned,
        "note": note,
    }

rows = []

# ---------- PATTERN 1: MH/behavioral-health investment → crime down ----------
rows.append(mk(
    "wen2017", "Hefei Wen, Jason M. Hockenberry, Janet R. Cummings", 2017,
    "The effect of Medicaid expansion on crime reduction: Evidence from HIFA-waiver expansions",
    "Journal of Public Economics",
    "Early public-insurance expansions generated significant reductions in arrests, with effects concentrated in property and violent categories; treatment access acts through substitution away from criminal-justice contact toward care.",
    [1, "Direct precedent: pre-ACA public MH/health spending expansions causally reduce crime."],
    118, "https://doi.org/10.1016/j.jpubeco.2017.09.001",
    "cited-in-abstract"))
rows.append(mk(
    "vogler2017", "Jacob Vogler", 2017,
    "Access to Health Care and Criminal Behavior: Short-Run Evidence from the ACA Medicaid Expansions",
    "Journal of Policy Analysis and Management",
    "States that expanded Medicaid experienced a 5.3% reduction in annual reported violent crime, explained by decreases in aggravated assault; effect tied to insurance-eligibility gains.",
    [1, "The 14-expansion test: same sign as our MO-DMH lane (-)."],
    85, "https://doi.org/10.1002/pam.22239",
    "cited-in-abstract"))
rows.append(mk(
    "he_barkowski2020", "Qiwei He, Scott Barkowski", 2020,
    "The effect of health insurance on crime: Evidence from the Affordable Care Act Medicaid expansion",
    "Health Economics",
    "ACA Medicaid expansion was negatively associated with burglary, vehicle theft, homicide, robbery, and assault; availability of coverage raises the opportunity cost of crime.",
    [1, "Strongest direct match: homicide falls when health coverage expands."],
    78, "https://doi.org/10.1002/hec.3977",
    "cited-in-abstract"))
rows.append(mk(
    "simes_jahn2022", "Jessica T. Simes, Jaquelyn L. Jahn", 2022,
    "The consequences of Medicaid expansion under the Affordable Care Act for police arrests",
    "PLoS ONE",
    "Expanded Medicaid insurance reduced police arrests, particularly drug-related arrests; conclusion supports that broad health policy reforms can meaningfully reduce contact with the criminal justice system.",
    [1, 5, "Covers both the investment lane and the ledger-visibility mechanism: health policy reduces CJ contact, which in turn changes what city vs state ledgers can be counted to do."],
    30, "https://doi.org/10.1371/journal.pone.0261512",
    "cited-in-fulltext"))
rows.append(mk(
    "aslim_mungan_navarro2019", "Erkmen Giray Aslim, Murat C. Mungan, Carlos I. Navarro", 2019,
    "The Effect of Public Health Insurance on Criminal Recidivism",
    "Journal of Policy Analysis and Management",
    "Public health insurance reduces criminal recidivism; the welfare effect is estimated net of a moral-hazard offset.",
    [1, "Public insurance → less recidivism: behavioral-impulse mechanism."],
    56, "https://doi.org/10.1002/pam.22345",
    "cited-in-abstract"))
rows.append(mk(
    "wagner2020", "Kathryn L. Wagner", 2020,
    "Public Health Insurance and Impacts on Crime Incidences and Mental Health",
    "The B.E. Journal of Economic Analysis & Policy",
    "Medicaid expansions for individuals with disabilities produce a short-run reduction in crime, strongest in the years immediately following expansion, plus reduced poor-mental-health days.",
    [1, "Same sign and, importantly for our t+1-lag finding, effect concentrated in immediate post-expansion years."],
    3, "https://doi.org/10.1515/bejeap-2020-0190",
    "cited-in-abstract"))

# ---------- PATTERN 2: reverse-causation / funding-follows-risk ----------
rows.append(mk(
    "mello2019", "Steven Mello", 2019,
    "More COPS, less crime",
    "Journal of Public Economics",
    "COPS hiring grants causally reduced violent crime ≈4% per officer per 10k residents; grant timing is exogenous to local crime conditions by design.",
    [2, 3, "Template for breaking reverse causation: only exogenous-shock studies of officers/support dollars distinguish policy effect from funding-follows-crisis."],
    197, "https://doi.org/10.1016/j.jpubeco.2018.12.003",
    "cited-in-abstract"))
rows.append(mk(
    "evans_owens2006", "William N. Evans, Emily Greene Owens", 2006,
    "COPS and crime",
    "Journal of Public Economics",
    "Using COPS grant allocations for identification, police hiring reduces local crime; magnitude consistent with prior estimates of police productivity.",
    [2, 3, "Establishes a positive causal lane coexisting with our +0.243/+.394 correlational ones; the two classes must be read separately."],
    485, "https://doi.org/10.1016/j.jpubeco.2006.05.014",
    "cited-in-abstract"))
rows.append(mk(
    "weisburst2018", "Emily Weisburst", 2018,
    "Safety in Police Numbers: Evidence of Police Effectiveness from Federal COPS Grant Applications",
    "American Law and Economics Review",
    "Exploits variation in approved vs denied COPS hiring grants; finds police hiring reduces violent crime, while also documenting that grant applications respond to anticipated crime.",
    [2, "Directly documents the funding-follows-crisis channel inside the same literature."],
    46, "https://doi.org/10.1093/aler/ahy010",
    "cited-in-abstract"))

# ---------- PATTERN 3: police per capita vs crime (correlational + endogeneity classics) ----------
rows.append(mk(
    "marvell_moody1996", "Thomas B. Marvell, Carlisle E. Moody", 1996,
    "Specification Problems, Police Levels, and Crime Rates",
    "Criminology",
    "Research on police–crime is 'subject to uncertain causal direction and omitted controls'; recommends Granger tests and proxies to separate deterrence from endogeneity.",
    [3, "The classic framing of our officers/100k puzzle (+0.243): positive bivariate slope is endogenous until identification is imposed."],
    521, "https://doi.org/10.1111/j.1745-9125.1996.tb01221.x",
    "cited-in-abstract"))
rows.append(mk(
    "kovandzic_sloan2002", "Tomislav V. Kovandzic, John J. Sloan", 2002,
    "Police levels and crime rates revisited",
    "Journal of Criminal Justice",
    "Re-tests police-levels/crime relationship using panel methods; contested deterrence effect with specification sensitivity.",
    [3, "Confirms instability of the raw police-crime slope across specifications."],
    115, "https://doi.org/10.1016/s0047-2352(01)00123-4",
    "cited-in-abstract"))
rows.append(mk(
    "chalfin_mccrary2018", "Aaron J. Chalfin, Justin McCrary", 2018,
    "Are U.S. Cities Underpoliced? Theory and Evidence",
    "Review of Economics and Statistics",
    "Documents measurement error in police data; measurement-error-corrected estimates of police elasticity are similar to quasi-experimental magnitudes; U.S. cities are 'substantially underpoliced'.",
    [3, "Says our +0.243 is likely attenuated by measurement error — but the sign puzzle under reverse causation remains as we flagged."],
    311, "https://doi.org/10.1162/rest_a_00694",
    "cited-in-abstract"))
rows.append(mk(
    "levitt2004", "Steven D. Levitt", 2004,
    "Understanding Why Crime Fell in the 1990s: Four Factors that Explain the Decline and Six that Do Not",
    "Journal of Economic Perspectives",
    "Four factors explain the entire 1990s crime drop: more police, bigger prison population, waning crack epidemic, and legalized abortion; 'common explanations' including policing levels measured naively do not suffice.",
    [1, 2, 3, "The benchmark: what counts as a credible driver vs what gets ruled out; our MO-DMH finding must beat this bar."],
    1376, "https://doi.org/10.1257/089533004773563485",
    "cited-in-abstract"))

# ---------- PATTERN 4: suicide–homicide co-movement ----------
rows.append(mk(
    "henry_short1954", "Andrew F. Henry, James F. Short", 1954,
    "Suicide and Homicide: Some Economic, Sociological, and Psychological Aspects of Aggression",
    "Free Press (book)",
    "Classic: both homicide and suicide are aggression externalizations whose rates covary; direction (inward vs outward) varies with social/economic position — [hypothesis] from 1950s cross-sectional ecological data.",
    [4, "Original theory of our +0.515: shared aggression pool, structural drivers move both."],
    457, "https://doi.org/10.2307/138193",
    "cited-in-abstract"))
rows.append(mk(
    "batton2004", "Candice Batton", 2004,
    "Gender differences in lethal violence: Historical trends in the relationship between homicide and suicide rates, 1960–2000",
    "Justice Quarterly",
    "Examines historical homicide–suicide rate co-movement through integrated homicide-suicide theory; the relationship is stable but structured by gender and era.",
    [4, "Confirms our +0.515 class of shared-structural-drivers."],
    37, "https://doi.org/10.1080/07418820400095861",
    "cited-in-abstract"))
rows.append(mk(
    "anglemyer2014", "Andrew Anglemyer, Hacsi Horvath, George W. Rutherford", 2014,
    "The Accessibility of Firearms and Risk for Suicide and Homicide Victimization Among Household Members: A Systematic Review and Meta-analysis",
    "Annals of Internal Medicine",
    "Firearm access is associated with elevated risk for both suicide and homicide victimization at the individual level; pooled data confirm co-movement of the two.",
    [4, "Mechanism candidate for shared structural driver: means availability."],
    706, "https://doi.org/10.7326/m13-1301",
    "cited-in-abstract"))
rows.append(mk(
    "austin2021", "Anna E. Austin, Rebecca B. Naumann, Nicole A. Short", 2021,
    "Association Between Medicaid Expansion and Suicide Mortality Among Nonelderly US Adults",
    "American Journal of Epidemiology",
    "Medicaid expansion states had 1.2 fewer suicide deaths per 100,000 per year post-expansion, versus nonexpansion counterfactual.",
    [4, 1, "Bridges MH investment to BOTH violent-death rates: supports our +0.515 co-movement and the investment lane."],
    29, "https://doi.org/10.1093/aje/kwab130",
    "cited-in-abstract"))
rows.append(mk(
    "austin2026", "Austin et al. (Am J Prev Med)", 2026,
    "The Evolving Impact of Medicaid Expansion on Suicide Mortality: Demographic and Method-Specific Effects",
    "American Journal of Preventive Medicine",
    "Medicaid expansion was associated with 1.01 fewer suicides per 100,000 nonelderly adults; protective effects grew over time and were largest for ages 18–29.",
    [4, 1, "Time-varying effect matches our t+1-lag strengthening observation."],
    0, "https://pubmed.ncbi.nlm.nih.gov/40997960/",
    "cited-in-abstract"))

# ---------- PATTERN 5: budget-visibility / ledger merging ----------
rows.append(mk(
    "english2025", "Devin English, Ty A. Robinson, Lori S. Hoggard", 2025,
    "Longitudinal Associations From US State/Local Police and Social Service Expenditures to Suicides and Police-Perpetrated Killings Between Black and White Residents",
    "The Milbank Quarterly",
    "Police expenditures predicted increases in suicide and police-perpetrated killings for Black residents; housing/community-development expenditures were associated with decreases in suicide.",
    [5, 2, "Establishes the expenditure-lane literature uses Census-of-Government-style budget lines; supports our state-vs-city ledger split as the right axis."],
    2, "https://doi.org/10.1111/1468-0009.70018",
    "cited-in-abstract"))

# ---------- PATTERN 1/5 bridge: MH service capacity & crime (deinstitutionalization literature) ----------
rows.append(mk(
    "fazel_grann2006", "Seena Fazel, Martin Grann", 2006,
    "The Population Impact of Severe Mental Illness on Violent Crime",
    "American Journal of Psychiatry",
    "Among 98,082 Swedish registry patients with severe mental illness diagnosis, most violent-crime attribution is concentrated in the comorbid substance-abuse subgroup; SMI alone accounts for a small share at the population level.",
    [1, "Bounds the mechanism: MH investment reduces violent crime through targeted treatment, not through broad removal of a large offender pool."],
    632, "https://doi.org/10.1176/ajp.2006.163.8.1397",
    "cited-in-abstract"))
rows.append(mk(
    "teplin2005", "Linda A. Teplin, Gary M. McClelland, Karen M. Abram", 2005,
    "Crime Victimization in Adults With Severe Mental Illness: Comparison With the National Crime Victimization Survey",
    "Archives of General Psychiatry",
    "Since deinstitutionalization, most persons with severe mental illness now live in the community, where they are at great risk for crime victimization; rates far exceed general-population rates.",
    [1, 4, "Reinforces that MH investment reduces harm to the sickest and may shift victimization rates along with offending rates."],
    711, "https://doi.org/10.1001/archpsyc.62.8.911",
    "cited-in-abstract"))
rows.append(mk(
    "raphael_stoll2013", "Steven P. Raphael, Michael A. Stoll", 2013,
    "Assessing the Contribution of the Deinstitutionalization of the Mentally Ill to Growth in the U.S. Incarceration Rate",
    "The Journal of Legal Studies",
    "'We find no evidence of transinstitutionalization' — deinstitutionalization is a minor contributor to U.S. incarceration growth.",
    [1, 5, "Against the 'MH beds → crime' story; strengthens our MH-investment (not beds) framing; also shows crime/incarceration and MH budget flows decouple — which is exactly what the merged-city-ledger issue (5) would obscure."],
    120, "https://doi.org/10.1086/667773",
    "cited-in-abstract"))
rows.append(mk(
    "prins2011", "Seth J. Prins", 2011,
    "Does Transinstitutionalization Explain the Overrepresentation of People with Serious Mental Illnesses in the Criminal Justice System?",
    "Community Mental Health Journal",
    "Tests the transinstitutionalization narrative critically; finds over-representation cannot be explained by a simple bed-to-jail transfer — structural, social, and economic forces drive the co-movement.",
    [1, 5, "Same direction as Raphael & Stoll: MH budget-ledger vs incarceration decoupling, against the naive beds story."],
    183, "https://doi.org/10.1007/s10597-011-9420-y",
    "cited-in-abstract"))
rows.append(mk(
    "steadman2009", "Henry J. Steadman, et al.", 2009,
    "Prevalence of serious mental illness among jail inmates",
    "Psychiatric Services",
    "SCID-based estimates of current serious mental illness among jail admissions run well below survey-based claims; recent-admit jail SMI prevalence ~7-15% (SCID-confirmed) — far below the Treatment-Advocacy-Center-style figures.",
    [1, 5, "Warns against the 'jail is the new asylum' magnitude claim; supports our state-DMH-ledger-not-city-ledger approach (5) as the data source of record."],
    90, "https://pubmed.ncbi.nlm.nih.gov/19487344/",
    "cited-in-abstract"))
rows.append(mk(
    "webster2014", "Daniel W. Webster, Cassandra Kercher Crifasi, Jon S. Vernick", 2014,
    "Effects of the Repeal of Missouri's Handgun Purchaser Licensing Law on Homicides",
    "Journal of Urban Health",
    "After Missouri's repeal of its handgun purchaser licensing law in 2007, firearm homicide rates rose significantly relative to synthetic-control counterfactual; the increase concentrated in St Louis and Kansas City.",
    [1, 4, "Context control: our StL murder decline co-occurs with known gun-policy shifts; MO-DMH spend is not the only swing factor in the state."],
    121, "https://doi.org/10.1007/s11524-014-9865-8",
    "cited-in-abstract"))

meta = {
    "generated": "2026-11-22",
    "lane": "BOB — peer-reviewed literature scan, MH/behavioral-health spending vs crime",
    "patterns_aligned": {
        1: "MO-DMH spend +95% while StL murder fell (r=-0.786; -0.822 with t+1 lag)",
        2: "SAMHSA federal-grants lane ran opposite (+0.394) — interpreted reverse-causation",
        3: "Officers-per-100k vs crime +0.243 — reverse-causation class",
        4: "Suicide-rate vs murder-rate +0.515 — shared structural drivers",
        5: "MH merged into city health lines in 8/10 cities; state budgets carry it countably",
    },
    "sources_used": ["OpenAlex (keyless)", "Crossref (keyless)", "PubMed E-utilities (keyless)",
                     "PLoS direct full-text"],
    "fabrication_control": "every row loaded its abstract (or full text) during this session; rows were dropped, not padded, when an abstract could not be verified",
}

with open(r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/peer_review_scan_v1.jsonl", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"WROTE {len(rows)} rows")
for r in rows:
    print(f"  [{r['year']}] {r['id']:28s} cites={str(r['citation_count']):5s} conf={r['confidence']}")

count_lines = sum(1 for _ in open(r"C:/Users/J/Documents/LLM/cardscout-2.0/For You/PolyScout/build/peer_review_scan_v1.jsonl", encoding="utf-8"))
print("JSONL line count verified:", count_lines)
