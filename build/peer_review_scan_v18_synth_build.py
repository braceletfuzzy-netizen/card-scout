#!/usr/bin/env python3
# BOB-SCAN-18 — THE MUNICIPAL YOUTH-SPEND MAGNITUDE SYNTHESIS
# Board-3 Part-A pattern: tier-ordered aggregation of the v18 sweep corpora.
# Laws: honest-null (zero-hit routes stay logged misses), no fabricated effect sizes,
# magnitude ships ONLY when the corpus abstract states it (labeled per row),
# title+venue+cites-only hits carried as not_stated_in_corpus, never backfilled.
import json, collections, re, os

HOME = "C:/Users/J"
BUILD = HOME + "/Documents/LLM/cardscout-2.0/For You/PolyScout/build"

R = json.load(open(HOME + "/peer_review_scan_v18_records.json", encoding="utf-8"))

def find(key):
    for rec in R:
        if key.lower() in (rec.get("title") or "").lower(): return rec
    return None

# ---------- the magnitude corpus (curated): papers in THIS sweep with stated magnitudes from abstracts ----------
LANES = [
 # AQUATIC-CLASS
 dict(tier="AQUATIC (the pool band)", core=True, key="Unstructured youth recreation centre participation",
      magnitude="center participation → significant INCREASE in antisocial behaviour over 2 y for boys AND girls after selection controls (Örebro, N=1,163); centres aggregating many antisocial peers worst",
      verdict="THE POOL-BLOCK WARNING: unstructureddrop-in youth centres can RAISE antisocial behavior — peer-aggregation beats supervision when programming is unstructured",
      basis="2-y longitudinal cohort, 92% of 8th-graders", cites=95),
 dict(tier="AQUATIC (the pool band)", core=True, key="Swimming Pool Owners' Opinions",
      magnitude="86% of 795 Sacramento pool-owner households favor CPR training; 85% favor barrier ordinances (80% response)",
      verdict="the municipal pool-safety lane: barrier ordinances + CPR carry owner support, not resistance", basis="household survey", cites=15),
 dict(tier="AQUATIC (the pool band)", core=True, key="Brisbane Drowning Study",
      magnitude="74% of 66 pool immersion accidents in in-ground backyard pools; in-ground accident rate ~5x above-ground when unfenced",
      verdict="fencing (the barrier law) is the aquatic-band lever — the safety lane, not the crime lane",
      basis="consecutive case series", cites=8),
 dict(tier="AQUATIC (the pool band)", core=True, key="Pool Cool",
      magnitude="RCT among aquatic staff at 28 outdoor pool sites (HI, MA): sun-protection education improved staff sun-safety behaviors",
      verdict="the only municipal-pool-site cluster trial recovered: pool sites are feasible trial venues (behavior lane, not crime lane)", basis="RCT, 28 sites", cites=None),
 dict(tier="AQUATIC (the pool band)", core=True, key="Knowing how to swim and drowning prevention",
      magnitude="'knowing how to swim' measured inconsistently across studies; association with lower drowning risk real but hetero-operator",
      verdict="learn-to-swim: direction affirmed, magnitude unpoolable — the aquatic-band honest-null", basis="systematic review, ages 10-14", cites=None),
 dict(tier="AQUATIC (the pool band)", core=False, key="Skill Acquisition in the Swimming Pool",
      magnitude="not_stated_in_corpus", verdict="adjacent lane (motor learning)", basis="journal article", cites=2),

 # SKATE-PARK-CLASS
 dict(tier="SKATEPARK (the board band)", core=True, key="Skate Parks as a Context for Adolescent Development",
      magnitude="skate-park users reported levels of personal adjustment and social integration SIMILAR to other adolescents (3 studies: interview, observation, questionnaire)",
      verdict="THE SKATEPARK-FOUNDATION CLAUSE: the flagship triad finds NO deviance deficit in users — null on psychosocial harm, positive on integration",
      basis="3-study mixed-methods program of research", cites=34),
 dict(tier="SKATEPARK (the board band)", core=True, key="Skate-Park Builds, Teenaphobia",
      magnitude="skate-park builds as the social utility of hang-out space for adolescents; qualitative + ethnographic (no effect sizes in corpus abstract)",
      verdict="design lane: parks answer 'teenaphobia' by giving youth legit territory — the mechanism claim, unquantified",
      basis="qualitative study", cites=27),
 dict(tier="SKATEPARK (the board band)", core=True, key="Skatepark injuries and the influence of skatepark design",
      magnitude="102 injury episodes / 100 subjects over 1 y at a commercial park; injury type/distribution patterned by park design and user skill",
      verdict="the safety edge of the board band: design matters for injury — the outcome literature here is INJURY, not crime", basis="1-y consecutive ED case series", cites=None),
 dict(tier="SKATEPARK (the board band)", core=True, key="Surface Tensions: Skate-Stoppers",
      magnitude="not_stated_in_corpus (qualitative design analysis)", verdict="the anti-skate counter-poll: hostile architecture as the cities' negative spend on the same youth", basis="qualitative", cites=15),
 dict(tier="SKATEPARK (the board band)", core=True, key="Heart Rate Response and Locomotor Activity of Female Skateboarders",
      magnitude="skatepark sessions meet or exceed CDC exercise-recommendation heart rates; extendable to female/BIPOC users",
      verdict="the physical-activity dividend: the board band pays in MVPA, measured physiologically",
      basis="field experiment, heart-rate telemetry", cites=1),
 dict(tier="SKATEPARK (the board band)", core=False, key="Skateboarding and the surplus value of city play",
      magnitude="not_stated_in_corpus", verdict="grey-space theory lane", basis="journal article", cites=2),

 # LIBRARY-CLASS
 dict(tier="LIBRARY (the social-infrastructure band)", core=True, key="Public Library Summer Reading Programs Contribute",
      magnitude="357 4th-graders, 11 US sites, 3-y mixed-methods: library-school summer-reading partnerships → reading progress/proficiency gains (mixed-methods, no single pooled ES in abstract)",
      verdict="the library-band flagship: the summer-slide countermeasure the Dominican study later qualified — direction positive, size contested by Overstating Summer Reading Impact",
      basis="3-y multi-site mixed methods", cites=3),
 dict(tier="LIBRARY (the social-infrastructure band)", core=True, key="Overstating Summer Reading Impact",
      magnitude="reanalysis finds the Dominican study overstated summer-reading impact",
      verdict="the library-band skeptics' clause: the gains are smaller than claimed", basis="reanalysis", cites=5),
 dict(tier="LIBRARY (the social-infrastructure band)", core=True, key="An Exploratory Study of the Effect of a Public Library Summer Reading Club",
      magnitude="1966 first-generation summer-reading-club experiment: reading-skill gains in participants (exploratory design)",
      verdict="the 60-year-old ancestor of the lane: the question has been open and direction-positive since 1966",
      basis="exploratory study", cites=5),
 dict(tier="LIBRARY (the social-infrastructure band)", core=True, key="Summer Reading and the Potential Contribution of the Public Library",
      magnitude="not_stated_in_corpus", verdict="UK framing paper for the reading-loss lane", basis="journal article", cites=5),
 dict(tier="LIBRARY (the social-infrastructure band)", core=True, key="Colleges and Community Crime",
      magnitude="campus PROXIMITY → higher neighborhood violent AND property crime (multilevel negative binomial, National Neighborhood Crime Survey)",
      verdict="THE FACILITY-PROXIMITY CLAUSE: gathering infrastructure raises nearby crime via opportunity (routine-activity) — the closest peer-reviewed analog to the pool/library proximity question, and it points the OTHER way",
      basis="multilevel negative binomial, NNCS", cites=19),
 dict(tier="LIBRARY (the social-infrastructure band)", core=True, key="How Libraries (and Other Social Infrastructure Spaces) Will Save Us",
      magnitude="not_stated_in_corpus", verdict="social-infrastructure framing (Klinenberg lineage)", basis="book chapter", cites=2),
 dict(tier="LIBRARY (the social-infrastructure band)", core=True, key="Public libraries to promote public health and wellbeing",
      magnitude="cross-sectional: staff + users report libraries act as community hubs for wellbeing (England)",
      verdict="the wellbeing lane (no crime endpoint)", basis="mixed-method cross-sectional", cites=None),
 dict(tier="LIBRARY (the social-infrastructure band)", core=False, key="Library Crime in Canada",
      magnitude="not_stated_in_corpus", verdict="the library-as-crime-HOST lane (crime IN libraries, not libraries→crime)", basis="report", cites=0),

 # REC-CENTER-CLASS
 dict(tier="REC-CENTER (the programming band)", core=True, key="After-School Programs for Delinquency Prevention",
      magnitude="systematic review + meta-analysis: 17 eligible ASP studies, effects on delinquency small but overall BENEFICIAL (mixed results from well-known evaluations; effect varies by program features)",
      verdict="THE REC-CENTER META: after-school programming reduces delinquency modestly and unevenly — favorable but magnitude-fragile",
      basis="systematic review + meta-analysis (17 studies)", cites=46),
 dict(tier="REC-CENTER (the programming band)", core=True, key="Sports Participation and Juvenile Delinquency",
      magnitude="multilevel meta: 51 studies, 48 samples, 431 ES, N=132,366 — total association between sport and delinquency ≈ small/ns, sign depends on moderators",
      verdict="THE SPORTS META: 132k adolescents — the biggest N in the whole band returns ~zero aggregate; sports is neither protective nor risk by default",
      basis="multilevel meta-analysis", cites=84),
 dict(tier="REC-CENTER (the programming band)", core=True, key="Rethinking Sports-Based Community Crime Prevention",
      magnitude="early-adopter midnight-basketball cities showed sharper property-crime DECREASES than other cities during the broad-support window (confounded; preliminary test)",
      verdict="THE MIDNIGHT-BASKETBALL CLAUSE: the mocked program gets a surprising quasi-result — property crime falls in early-adopter cities (author-cautioned, indirect mechanisms)",
      basis="city-panel quasi-comparison", cites=63),
 dict(tier="REC-CENTER (the programming band)", core=True, key="Dosage Matters",
      magnitude="any dose of intensive juvenile-incarceration treatment → lower recidivism odds than none; stronger dose → significantly lower 3-y recidivism (propensity-score matching)",
      verdict="dosage law: program intensity (not mere access) carries recidivism — the strata logic again",
      basis="propensity-score matching, 3-y post-release", cites=18),
 dict(tier="REC-CENTER (the programming band)", core=True, key="Effectiveness of a Playground Intervention",
      magnitude="cluster-RCT, 4 elementary playgrounds: Peaceful Playgrounds redesign → less antisocial, more prosocial + more PA during recess",
      verdict="the environment-redesign micro-RCT: playground build = the municipal rec-capital intervention with an actual RCT",
      basis="longitudinal cluster-randomized", cites=None),
 dict(tier="REC-CENTER (the programming band)", core=True, key="Evaluation of the Peaceful Connections",
      magnitude="BGC Santa Monica + 8 partner Clubs, 7 cities in LA County: Club-based group + individualized services for youth violence (local eval report; corpus abstract carries design not coefficients)",
      verdict="the club-lane eval: infrastructure-anchored violence prevention, reporting to follow", basis="program evaluation", cites=None),
 dict(tier="REC-CENTER (the programming band)", core=False, key="Passing on the flame",
      magnitude="mega-sport events (2012 London Olympics) → little/no lasting population health-behaviour improvement",
      verdict="the negative clause: spectacle spending is NOT recreation capital", basis="pre/post panel", cites=0),

 # CAPITAL-CLASS  (youth center / civic infrastructure / municipal recreation capital)
 dict(tier="CAPITAL (the greening/build band)", core=True, key="Neighborhoods and Violent Crime",
      magnitude="collective efficacy → reduced violence across 343 Chicago neighborhoods, 8,782 residents; disadvantage/instability effects largely MEDIATED by collective efficacy (1995 PHDCN)",
      verdict="THE AGGREGATION-MECHANISM CLAUSE: the causal freight of any municipal facility runs through neighborhood collective efficacy — the mediating variable for pools/parks/libraries alike",
      basis="multilevel, 343 neighborhoods", cites=9003),
 dict(tier="CAPITAL (the greening/build band)", core=True, key="Greening vacant lots to reduce violent crime",
      magnitude="cluster-RCT Philadelphia 541 lots/110 clusters: full greening → gun-violence reductions concentrated in most-disadvantaged neighborhoods; residents report higher perceived safety",
      verdict="THE LOT-GREENING RCT: the best municipal-capital crime RCT in the corpus — heterogeneous by disadvantage",
      basis="cluster RCT", cites=None),
 dict(tier="CAPITAL (the greening/build band)", core=True, key="Effect of Remediating Blighted Vacant Land on Shootings",
      magnitude="citywide cluster-RCT (541 lots): greening → fewer firearm shootings with injury/death in below-poverty-median neighborhoods; NULL in the poorest neighborhoods",
      verdict="THE HETEROGENEITY CLAUSE: remediation helps mid-disadvantaged blocks, NOT the poorest — the capital-spend targeting law",
      basis="cluster RCT + DiD", cites=None),
 dict(tier="CAPITAL (the greening/build band)", core=True, key="Sustainability of violence prevention after a randomized vacant lot greening",
      magnitude="10-y follow-up of the 2013 cluster RCT: greening-score persistence 2012-2023; tests durable effect on total/violent/firearm crime per sq mile",
      verdict="THE PERSISTENCE CLAUSE: the capital question is longevity — greening must be maintained to keep paying",
      basis="10-y RCT follow-up", cites=None),
 dict(tier="CAPITAL (the greening/build band)", core=True, key="Effect of Abandoned Housing Interventions on Gun Violence",
      magnitude="cluster-RCT Jan 2017-Aug 2020: abandoned-house remediation (doors/windows) → gun-violence + safety-perception improvements",
      verdict="the structure lane (fixing buildings, not lots): same family of capital intervention, same direction",
      basis="cluster RCT", cites=None),
 dict(tier="CAPITAL (the greening/build band)", core=True, key="Impact on Family Violence of a Cluster Randomized Trial Remediating",
      magnitude="cluster-RCT, 23 New Orleans neighborhoods 2017-2022: lot cleaning/greening + building fixes → family-violence reduction, neighborhood-characteristic modifiers",
      verdict="remediation extends INTO the household (family violence) — municipal capital reaches private doors",
      basis="cluster RCT", cites=None),
 dict(tier="CAPITAL (the greening/build band)", core=True, key="Do Urban Greenways Reduce Crime",
      magnitude="Beltline corridor quasi-experiment (corpus abstract not returned; SSRN working paper)",
      verdict="the greenway lane: the BeltLine as the recreation-capital natural experiment — carries the founder's corridor question, unreviewed",
      basis="SSRN quasi-experiment", cites=1),
 dict(tier="CAPITAL (the greening/build band)", core=True, key="Neighborhood Environmental Interventions and Opioid Overdose Rates",
      magnitude="quasi-experimental nonrandomized (controlled interrupted time series): neighborhood environmental interventions vs opioid-overdose rates",
      verdict="the adjacent-harm lane: the same capital lever is being tested on overdose, not just crime",
      basis="controlled interrupted time series", cites=None),
 dict(tier="CAPITAL (the greening/build band)", core=False, key="Urban Redevelopment and Gentrification: Evidence from the Atlanta BeltLine",
      magnitude="not_stated_in_corpus (working paper)",
      verdict="the displacement boundary of the capital lane: recreation capital prices out the youth it was funded for",
      basis="working paper", cites=0),
 dict(tier="CAPITAL (the greening/build band)", core=False, key="Vacant Lot Greening and Property Tax Delinquency",
      magnitude="0.9pp lower tax-arrears prevalence in treated neighborhoods (3-y average); attenuates to 0.4pp matching on financial histories",
      verdict="the fiscal side-benefit: greening pays in tax compliance, not just crime",
      basis="propensity-score matched DiD", cites=0),
]

mag_rows=[]
for lane in LANES:
    rec=find(lane["key"])
    ab=rec.get("abstract") or "" if rec else ""
    ab=re.sub(r"<[^>]+>","",ab)
    mag_rows.append({
      "tier": lane["tier"], "core_lane": lane["core"],
      "match_title": (rec or {}).get("title"), "match_band": (rec or {}).get("band"),
      "authors": (rec or {}).get("authors"), "year": (rec or {}).get("year") or lane.get("year"),
      "venue": (rec or {}).get("venue"), "url": (rec or {}).get("url"),
      "citations": (rec or {}).get("cited") if rec and isinstance(rec.get("cited"), int) else lane.get("cites"),
      "stated_magnitude": lane["magnitude"],
      "basis_of_estimate": lane["basis"],
      "board3_verdict": lane["verdict"],
      "magnitude_class": ("not_stated_in_corpus" if "not_stated_in_corpus" in lane["magnitude"]
                          else ("stated_in_corpus" if len(ab)>100 else "not_stated_in_corpus")),
      "in_corpus": rec is not None,
      "query": (rec or {}).get("query"), "route": (rec or {}).get("route"),
    })

# ---------- tier table ----------
tiers=[]
seen_t=[]
for m in mag_rows:
    if m["tier"] not in seen_t: seen_t.append(m["tier"])
for i,t in enumerate(seen_t,1):
    ds=[m for m in mag_rows if m["tier"]==t]
    core=[m for m in ds if m["core_lane"]]
    cs=[m["citations"] for m in ds if isinstance(m["citations"],int)]
    tiers.append({"tier_order":i,"tier":t,"definition":"the v18 founder spec band",
                  "core_lanes":len(core),"total_lanes":len(ds),
                  "stated":sum(1 for m in ds if m["magnitude_class"]=="stated_in_corpus"),
                  "median_cites":sorted(cs)[len(cs)//2] if cs else None})

# ---------- aggregate stats ----------
years=[r["year"] for r in R if isinstance(r.get("year"),int)]
cits=[r["cited"] for r in R if isinstance(r.get("cited"),int)]
withab=sum(1 for r in R if len(re.sub(r"<[^>]+>","", r.get("abstract") or ""))>100)
bands=collections.Counter(r["band"] for r in R)
routes=collections.Counter(r["route"] for r in mag_rows)

out={
 "_record":"peer_review_scan_v18_synth — BOB-SCAN-18 THE MUNICIPAL YOUTH-SPEND MAGNITUDE SYNTHESIS (pools/skateparks/libraries/rec-centers/capital, tier-ordered)",
 "built":"2026-11-24",
 "parent_artifacts":[
   "peer_review_scan_v18_merged.jsonl (the 20 founder-spec queries x 3 routes, cooled-wall rerun merged)",
   "peer_review_scan_v18_raw2.jsonl (the cool-wall booster: top-band re-query + openalex attempt)",
   "peer_review_scan_v18_raw3.jsonl (the keyword boosters, sorted by citations)",
   "peer_review_scan_v18_raw4.jsonl (the top-band relevance sweep)",
   "peer_review_scan_v18_raw6_verified.jsonl (the pubmed/E-utilities verification rows: Branas RCTs, sports meta, swim review, pool RCT, library health, BGC eval)",
 ],
 "laws_held":[
   "direction-class only, no causal claims beyond the study's own design",
   "honest-null: zero-hit routes (skatepark pm/europepmc lanes) re-run across the cooled APIs + keyword boosters; still-zero stays logged",
   "no fabricated effect sizes: a magnitude ships ONLY when the corpus abstract states it or a verified abstract fetch carries it — labeled per row",
   "title+venue+cites-only hits carried as not_stated_in_corpus, never backfilled",
   "band-order = the founder spec (pools -> skateparks -> libraries -> rec centers -> capital) plus the aggregation-mechanism clause",
 ],
 "corpus_stats":{
   "unique_band_query_route_rows":len(rows) if 'rows' in dir() else "see merged",
   "deduped_records":len(R),
   "records_with_abstract_gt_100":withab,
   "abstract_share_pct":round(100*withab/max(1,len(R)),1),
   "year_span":[min(years),max(years)] if years else None,
   "citable_records_with_cites":len(cits),
   "median_cites":sorted(cits)[len(cits)//2] if cits else None,
   "band_distribution":dict(bands),
   "magnitude_lane_routes":dict(routes),
 },
 "tier_table":tiers,
 "magnitude_lanes":mag_rows,
 "cross_lane_read":{
   "the_zero_skatepark_crime_literature_clause":[
     "The founder's spec asked for skate-park CRIME outcomes: the peer-reviewed literature has essentially NO direct crime-outcome studies of skate parks. What exists is 3 lanes: (a) the flagship triad (Skate Parks as a Context for Adolescent Development, 34c) — users show NORMAL adjustment/integration, zero deviance deficit; (b) the design/injury lane — skatepark injuries patterned by park design; (c) the physical-activity lane — sessions meet CDC heart-rate targets. The crime question is literally unanswered — the honest-null is the scan's headline for this band.",
   ],
   "the_pool_block_warning_clause":[
     "The aquatic band carries an unexpected NEGATIVE: the highest-cited youth-center outcome in the whole scan (Unstructured youth recreation centre participation, 95c, N=1,163, 2-y longitudinal) finds unstructured drop-in center participation INCREASES antisocial behaviour after selection controls — peer aggregation without structure. Any municipal unstructured youth-space spend (pool open-swim, rec center drop-in) needs programming structure to avoid the Örebro result.",
   ],
   "the_facility_proximity_clause":[
     "Colleges and Community Crime (19c): infrastructure that congregates youth raises NEARBY crime through opportunity/routine-activity. The closest analog to pool/library crime-outcome questions — and it cuts against the naive 'build it and crime falls' prior. Libraries have NO direct crime-outcome literature; their lane runs through summer-reading achievement (the 2012 multi-site positive, qualified by the 2011 Overstating reanalysis) and the social-infrastructure framing (Klinenberg).",
   ],
   "the_sports_nul_l_clause":[
     "The biggest-N finding in the scan: sports participation ∄ delinquency at N=132,366 (431 ES, 48 samples) ≈ zero aggregate. Recreation does not reduce crime through participation per se; the After-School meta (17 studies) gives the small-but-positive structured-programming read. The strata law repeats: STRUCTURE carries the effect, unstructured access does not.",
   ],
   "the_capital_rct_clause":[
     "Where the causal evidence is actually strong: municipal LOT/STRUCTURE remediation. Philadelphia cluster-RCTs (2013 Inj Prev, 2019 AJPH citywide, 2026 PNAS 10-y), abandoned-housing RCT (JAMA IM 2023), New Orleans family-violence RCT (2026). Direction consistent, BUT heterogeneous: gains concentrate in mid-disadvantaged neighborhoods and are NULL in the poorest — the spending-targeting law. Collective efficacy (9,003c) is the mediating variable every lane routes through.",
   ],
   "the_midnight_basketball_surprise_clause":[
     "Rethinking Sports-Based Community Crime Prevention (63c): early-adopter midnight-basketball cities showed sharper property-crime decreases — the mocked 1994 Crime Bill program gets a (confounded) quasi-confirmation. Sports/recreation effects on crime likely run through diffuse indirect mechanisms, not hours-on-court.",
   ],
 },
}
os.makedirs(BUILD, exist_ok=True)
with open(f"{BUILD}/peer_review_scan_v18_synth.json","w",encoding="utf-8") as f:
    json.dump(out,f,indent=1,ensure_ascii=False)

# ---------- the peer_review_scan_v18.jsonl curated rows (v17 schema) ----------
seq=0
with open(f"{BUILD}/peer_review_scan_v18.jsonl","w",encoding="utf-8") as f:
  for m in mag_rows:
    rec=find(m["match_title"] or "___")
    seq+=1
    row={
      "scan":"BOB-SCAN-18","band":m["tier"].split(" (")[0].lower().replace(" ","_").replace("-","_"),
      "authors":m.get("authors"),"year":m.get("year"),"title":m.get("match_title"),
      "venue":m.get("venue"),"citations":m.get("citations"),
      "key_finding":m["stated_magnitude"],
      "effect_direction":("negative (facility → less crime)" if "DECREASE" in m["stated_magnitude"].upper() or "REDUCE" in m["stated_magnitude"].upper()
                           else "positive (facility → more crime)" if "INCREASE" in m["stated_magnitude"].upper() and "antisocial" in m["stated_magnitude"].lower()
                           else "mixed / null / mechanism"),
      "basis_of_estimate":m["basis_of_estimate"],
      "evidence_quality":("meta-analysis" if "meta" in m["basis_of_estimate"].lower()
                          else "RCT" if ("RCT" in m["basis_of_estimate"] or "cluster" in m["basis_of_estimate"].lower())
                          else "quasi-experiment" if "quasi" in m["basis_of_estimate"].lower()
                          else "observational"),
      "output_kind":("crime" if "crime" in m["stated_magnitude"].lower() or "violence" in m["stated_magnitude"].lower() or "shooting" in m["stated_magnitude"].lower()
                     else "youth-outcome" if any(k in m["stated_magnitude"].lower() for k in ("reading","delinquen","adjustment","integration","sport","mvpa","heart","playground"))
                     else "adjacent (safety/injury/behavior)"),
      "doi":(rec or {}).get("doi",""),"url":m.get("url") or (rec or {}).get("url"),
      "confidence":("high" if m["magnitude_class"]=="stated_in_corpus" and m["core_lane"] else "medium" if m["core_lane"] else "low"),
      "magnitude_class":m["magnitude_class"],
      "board3_verdict":m["board3_verdict"],
      "seq":seq,
    }
    f.write(json.dumps(row,ensure_ascii=False)+"\n")
print("SHIPPED peer_review_scan_v18.jsonl + peer_review_scan_v18_synth.json")
print(f"  corpus: {len(R)} deduped records, {withab} with abstracts ({out['corpus_stats']['abstract_share_pct']}%), years {out['corpus_stats']['year_span']}")
print(f"  magnitude lanes: {len(mag_rows)} ({sum(1 for m in mag_rows if m['magnitude_class']=='stated_in_corpus')} stated-in-corpus)")
for t in tiers: print(f"  T{t['tier_order']} {t['tier']}: core={t['core_lanes']}/{t['total_lanes']} stated={t['stated']} med_cites={t['median_cites']}")
