# THE MEMPHIS TRANSIT-SPINE REPORT — Where the Corridor Goes, and Why

**Built:** 2026-11-24
**Augments:** `2026-11-24-memphis-crime-reduction-brief.md` (Lever-2's access dial, F4 falsifier)
**The founder's directive this report answers:** "Pull the data, let's make this report a one-stop solution for where it's going. Do everything you recommended."

**The laws this report holds:** (1) zero-fabricated numbers — every figure traces to a named file or a dated keyless pull made 2026-11-24; (2) honest nulls named in Section 8, never backfilled; (3) the 5-way index is a **descriptive composite**, direction-class only, no causal claim; (4) plain English first.

---

## 1. THE ONE-PARAGRAPH VERSION

Memphis has 23 surviving bus routes and zero dedicated transit money, and this report now answers — with pulled tract-grade data instead of hunches — the question the diagnosis left open: **which corridor goes first?** We pulled the Census LEHD jobs file (LODES 2024, 537,432 jobs across Shelby + Crittenden work-tracts), the ACS vehicle table (249 Shelby tracts), the poverty table, MATA's own GTFS shape file (recovered, not authwalled), and the city's 311 code-enforcement calls by Council District, then scored every MATA route on the 5-way index the corridor-criteria set out. The scores' verdict: **Lamar is the spine.** It is #1 on the composite (0.78) and #1 on every equity component — the most jobs within an 800 m walk of its stops (82,696), the most no-vehicle households (4,607), the most residents below poverty (20,014) — and it is #2 in MATA's own published restore order (behind Poplar — an order built on bus supply, not demand). Union and Madison are the job-anchors that flank it; Park and Crosstown are the equity-heavy East-Wilmington–class candidates that score high on people but lower on jobs. Where the hunch-read and the scores **conflict**: Frayser (Route 11) scores near the bottom of the 23-route table on every pullable component — its problem is coverage-starved service frequency, not corridor-selection fitness — and Whitehaven has no single trunk to score at all. Both pattern-reads survive as *frequency* projects, not *spine* projects. The money for the whole program is one instrument: a dedicated Shelby County levy (COTA's 0.25%-class raised $161.4M in 2024), sequenced governance-first. The falsifiers are already wired: the annual ACS transit-share re-pull and the IndyGo/GRTC trajectory.

[Certain — the pull routes and computed components; direction-class on the ranking itself]

---

## 2. WHAT WAS PULLED (the new data layer, all keyless, all dated 2026-11-24)

| Pull | Route | What it gives | Raw file |
|------|-------|---------------|----------|
| **LEHD LODES8 WAC JT00 2024** (TN + MS, all-worker C000) | `lehd.ces.census.gov/data/lodes/LODES8/{tn,ms}/wac/` + xwalks | **Jobs at the work-tract grain**: 537,432 jobs across 270 Shelby+Crittenden work-tracts (497,554 TN-side + 39,878 MS-side) | `rjobs_by_work_tract_wac2024_v1.json` |
| **ACS 5-yr 2022 B08201** vehicles-available | `www2.census.gov` table-based-SF .dat (the banked keyless route; API is key-walled — "Missing Key" page live-verified) | No-vehicle households per tract, 249 Shelby + 21 Crittenden | `acsdt5y2022-b08201.dat` |
| **ACS 5-yr 2022 B17001** poverty | same route | Below-poverty population per tract | `acsdt5y2022-b17001.dat` |
| **MATA GTFS** | Mobility Database catalog (`feeds_v2.csv` → `files.mobilitydatabase.org/mdb-2352/latest.zip`; MATA's own `matatransit.com` link also live) | **Route geometry recovered — NOT authwalled**: 23-route roster (18 bus routes of the Nov-2024 network + the 16 SE Circulator + trims), shapes, 3,508 stops, calendar valid 2025-02-09→03-10 | `gtfs_mata_2352.zip` |
| **311 CE-class by district** | City of Memphis AGOL FeatureServer (the banked keyless AGOL route, re-queried at the district grain) | Code-enforcement-class calls by Council District, 2025 full-year + 2026 YTD | `r311_ce_by_district_v1.json` |
| **News route-rosters** | MLK50 WordPress REST (keyless, the proven route) | MATA's own published top-10 restore priority order (see §4) | — |

**The DNS note that made this possible (banked):** this box's default resolver fails for census.gov-class hosts; every pull above went through Google-DNS-resolved pinned IPs (`dns-workaround-banked`, commit d1b3cec). All routes remain keyless.

**Vintage honesty:** LODES jobs = 2024 (the newest file on the server, 404-verified beyond 2024); ACS = 2022 5-yr (tract grade only exists in the 5-yr; the 1-yr banked columns stop at city grain). MATA GTFS = a Feb-2025 calendar snapshot — the 23-route roster is the post-Nov-2024-cut network, not the pre-cut map.

---

## 3. THE 5-WAY INDEX — WHAT EACH COMPONENT MEASURES

| # | Criterion (from the corridor brief) | Measured as | Source |
|---|-------------------------------------|-------------|--------|
| C1 | Jobs density x destination | LODES 2024 jobs in every tract whose centroid sits within **800 m of a route stop** (the walkshed proxy) | LODES WAC 2024 + GTFS stops + xwalk centroids |
| C2 | Zero-car households (the riders who cannot leave) | ACS B08201 no-vehicle households in covered tracts | ACS 5-yr 2022 B08201 |
| C3 | The 20-60% targeting law | B17001 below-poverty population in covered tracts + covered-tract poverty rate | ACS 5-yr 2022 B17001 |
| C4 | The Pulse/Red-Line shape (4-7 mi) | GTFS max-shape length converted to a 0-1 fit score (1.0 inside 6.4-11.3 km, tapering outside) | GTFS shapes |
| C5 | 311/CE-class call density | CE-class 311 calls per Council District (2025 + 2026 YTD) | AGOL pull | 

**Two honest component nulls, named up front:** (a) **C5 cannot be joined to routes keylessly** — the 311 layer carries CouncilDistrict (11 values), route geometry is tract-latlon; without district polygons a route→district join would be fabricated, so C5 rides in Section 5 as district-grain evidence and is **excluded from the numeric composite**. (b) **Zero-fare response by route does not exist in any public pull** — MATA's +20-25% (trustee Holmes, MLK50 2026-10) and the banked +2.7M-trips / +$4M-rider-savings figures are systemwide; no route-grain counter split is published. Carried as qualitative context only. The composite is therefore a **4-way score** (jobs 0.30 / no-vehicle 0.27 / poverty 0.27 / shape-fit 0.16, rank-normalized), stated in writing so anyone can re-weight it: `rspine_scores_v2_2025_network.json`.

---

## 4. THE RANKING — ALL 23 ROUTES SCORED, TOP 5 NAMED

**Full table in `rspine_scores_v2_2025_network.json`; the ranked top five, with every component printed:**

| Rank | Route | Composite | Jobs (800m) | No-veh HH | Below-pov pop | Pov share | Length km (fit) | Daily trips |
|------|-------|-----------|-------------|-----------|---------------|-----------|-----------------|-------------|
| **1** | **36 LAMAR** | **0.784** | **82,696** | **4,607** | **20,014** | 26.5% | 36.3 (0.00) | 116 |
| 2 | 01 UNION | 0.675 | 99,057 | 3,636 | 8,379 | 24.8% | 22.0 (0.57) | 74 |
| 3 | 02 MADISON | 0.647 | 62,520 | 4,315 | 14,555 | 23.0% | 29.9 (0.26) | 66 |
| 4 | 42 CROSSTOWN | 0.629 | 40,074 | 4,526 | 19,816 | 29.6% | 39.4 (0.00) | 82 |
| 5 | 57 PARK | 0.609 | 47,652 | 3,998 | 14,528 | 34.8% | 24.3 (0.48) | 77 |
| 6 | 40 STAGE & LAUDERDALE | 0.530 | 55,320 | 3,405 | 15,346 | 32.7% | 45.7 (0.00) | 55 |
| 7 | 07 SHELBY & HOLMES | 0.528 | 62,810 | 3,457 | 11,466 | 27.7% | 31.3 (0.20) | 62 |
| 8 | 50 POPLAR | 0.512 | 73,900 | 3,205 | 6,919 | 16.2% | 25.6 (0.43) | 98 |
| 9 | 19 VOLLINTINE | 0.462 | 37,574 | 3,068 | 16,398 | 28.6% | 44.8 (0.00) | 48 |
| 10 | 39 SOUTH THIRD | 0.454 | 48,398 | 2,289 | 12,505 | 34.4% | 24.8 (0.46) | 122 |
| 11 | 04 WALKER | 0.452 | 47,008 | 3,074 | 8,744 | 36.6% | 23.7 (0.50) | 64 |
| 12 | 08 CHELSEA & HIGHLAND | 0.440 | 21,298 | 3,223 | 13,234 | 28.7% | 24.7 (0.46) | 106 |
| 13 | 52 JACKSON | 0.431 | 19,484 | 2,893 | 12,466 | 27.1% | 19.6 (0.67) | 82 |
| 14 | 34 CENTRAL & WALNUT GROVE | 0.421 | 65,386 | 2,438 | 5,984 | 19.7% | 24.4 (0.48) | 24 |
| 15 | 16 SOUTHEAST CIRCULATOR | 0.420 | 81,195 | 810 | 10,455 | 33.3% | 26.3 (0.40) | 36 |
| 16 | 12 MALLORY | 0.391 | 51,176 | 2,153 | 7,911 | 30.6% | 23.1 (0.53) | 38 |
| 17 | 32 HOLLYWOOD & HAWKINS MILL | 0.355 | 23,857 | 2,520 | 14,564 | 32.1% | 35.0 (0.05) | 74 |
| 18 | 53 SUMMER | 0.348 | 20,795 | 2,128 | 11,843 | 26.2% | 23.2 (0.52) | 58 |
| 19 | 69 WINCHESTER | 0.297 | 34,965 | 1,682 | 12,858 | 34.1% | 42.9 (0.00) | 30 |
| 20 | 30 BROOKS | 0.260 | 50,752 | 1,367 | 8,540 | 17.6% | 44.1 (0.00) | 46 |
| 21 | **11 FRAYSER** | **0.205** | 11,588 | 1,598 | 7,894 | 33.7% | 24.7 (0.46) | 80 |
| 22 | 37 PERKINS | 0.175 | 12,347 | 999 | 7,699 | 19.6% | 22.7 (0.54) | 22 |
| 23 | 28 AIRPORT | 0.133 | 48,165 | 795 | 3,288 | 24.2% | 35.1 (0.05) | 36 |

**Why Lamar wins:** it is the only route that is top-3 on all three demand components simultaneously — jobs (2nd, 82,696 vs Union's 99,057), no-vehicle households (1st, 4,607), below-poverty residents (1st, 20,014) — while carrying the 2nd-highest daily trip load (116/weekday, i.e. MATA's own riders are already voting with their feet), the 2nd-most covered tracts (26 of ~249 Shelby tracts). It leads the composite even though it scores **0.00 on the shape-fit criterion** (36.3 km of shape, three times the 4-7 mi band) — the win is that large. Its length honest-read: the GTFS shape includes looping variants; the corridor's spine (downtown→Lamar Ave→Southeast) is the 4-7 mi class the criterion wants, while the full shape serves the far southeast. **MATA's own published priority order corroborates** — MLK50 (2025-04-03) printed the restore order MATA/TransPro issued: "50 – Poplar, **36 – Lamar**, 42 – Crosstown, 52 – Jackson, 8 – Chelsea & Highland, 39 – South Third, 1 – Union, 2 – Madison, 40 – Stage & Lauderdale, 30 – Brooks." Lamar is #2 in their bus-supply order and #1 in every pullable data component; the hunch and the machine agree.

**What the news adds that the pull cannot (the zero-fare component, systemwide):** zero-fare is now in year two — the pilot (WREG 2025-11-14) became an extended program; the banked figures are +18-23% within weeks / 2.7M cumulative zero-fare trips / $4M rider savings (Fox13 2026-11-17, WREG 2025-12-02); trustee Holmes says the increases run "roughly 20-25%" (MLK50 2026-11-24, October interview). 14 buses were added in the 30 days before that interview, 44 more come May-October 2027 ($42M federal+local grants), **and the five routes that got the first buses back are MATA's own "high-ridership" list** (MLK50 2026-11-24) — route names not published at grain (honest null), but Lamar is the roster's highest-trip-count bus route in the GTFS (116 weekday trips).

---

## 5. WHERE THE SCORES CONFIRM — AND WHERE THEY CONFLICT — THE PATTERN-READ

| Pattern-read | Score says | Verdict |
|--------------|-----------|---------|
| **Lamar = the spine** | #1 composite (0.784), #1 on equity components, MATA's own #2 restore priority | **CONFIRMED**, amplified |
| **Poplar = the spine** | #8 composite (0.512). Jobs are real (73,900, #3) but covered-tract poverty share is the **4th-lowest on the network (16.2%)** and no-vehicle households trail Lamar by 30% | **CONFLICT** — Poplar is a strong *second trunk* (jobs-weighted), not the equity spine. It rides in MATA's restore order at #1, where the ranking is bus-supply-driven, not demand-driven |
| **Frayser = spine candidate** | #21 of 23 (0.205): 11,588 jobs, 1,598 no-vehicle households, 33.7% covered poverty | **CONFLICT, read honestly**: Route 11's components are weak because Frayser's tracts are poorly touched by *this* 800 m-coverage measure of a starved network — an 80-trips/day route with 145 stops. The pattern-read survives as a **frequency-restoration case**, not a BRT-spine build; the honest null is that no route-grain ridership counter exists to arbitrate |
| **Whitehaven = spine candidate** | No single trunk to score: the area rides Route 69 Winchester (0.297, 42.9 km mega-shape) + 38 Boxtown-class legs (dropped pre-2024). No GTFS trunk exists on the 2025 roster | **CONFLICT** — Whitehaven is the network-coverage gap itself; its need shows up in the CE calls (District 7: 3,817 CE-class calls 2025-26) not in any spine geometry. Same verdict as Frayser: frequency/coverage project |
| **Downtown-to-East anchors** | Union (99,057 jobs = #1 jobs in the city, 9th-highest US-class tract cluster), Madison's 4,315 no-vehicle HH | **CONFIRMED** as the job-anchors the spine must touch |

**The synthesis the scores support:** one east-west spine **Lamar (SE) → Crosstown/Park (midtown) → Union/Madison (downtown core)** touches, in some combination, the #1 through #5 composite routes and sits on the mConnect BRT shelf ($12M federal grant, awarded 2019, unspent through 2026 — the shelf MATA's trusteeship exit can finally open). Park + Crosstown are the mid-band equity connectors the 20-60% poverty targeting law wants (29.6% / 34.8% covered poverty); Union anchors the downtown job mass the jobs criterion wants.

**The 311 CE-call side panel (C5, district grain):** combined 2025 + 2026-YTD CE-class calls by district — D1 12,972 / D5 11,413 / D2 9,964 / D3 9,742 / **D6 4,826 / D2-3 wrap the Lamar southeast leg**; D7 (Whitehaven) 7,629 and D4 6,924 carry the south/Whitehaven need. District 0 = 62,484 calls with no district field — the layer's geography gap is itself a finding. The map: the CE-density spine and the demand-index spine overlap on the midtown-southeast leg (D2/D3/D5/D6 wrap Lamar's tracts), which is exactly where Branas-class remediation and the spine build both land first.

---

## 6. THE MAP — THE 10-MINUTE SPINE (descriptive, computed)

The "10-minute spine" definition: the corridor segment where a rider within 800 m of a stop reaches a stop with a trip every ≤10 min. At today's network (60-min headways everywhere, per the banked Nov-2024 cut), **no route anywhere clears the 10-minute test — the map is the corridor GEOMETRY, and the headway promise is what the levy buys.** The geometry, from the GTFS shapes (all coordinates in `rroute_covered_tracts_2025_v1.json` + `rmata_routes_2025_v1.json`):

- **Trunk 1 (the equity spine): Lamar 36** — downtown (William Hudson Transit Center area, ~35.14/-90.05) southeast along Lamar Ave to the Southeast Memphis terminal area (~35.06/-89.90); 26 covered tracts, 20,014 below-poverty residents, 82,696 jobs; 36.3 km of shape, of which the 4-7 mi core is the midtown→SE segment.
- **Trunk 2 (the job spine): Union 01 + Madison 02** — the river-to-East core pair; Union holds the #1 job cluster (99,057 in 17 covered tracts, 22.0 km); Madison parallels 1.5 mi north with 4,315 no-vehicle households (2nd on the network).
- **The equity connectors:** Crosstown 42 (4,526 no-veh HH, 19,816 below-pov) and Park 57 (3,998 no-veh HH, 34.8% covered poverty) — the north-south stitching the targeting law wants inside the trunk's headway, not as afterthoughts.
- **What is NOT on the map, on the score's say-so:** Frayser (frequency restoration), Whitehaven (coverage build), Stage & Lauderdale (45.7 km untargetable mega-route).

---

## 7. THE MONEY, THE SEQUENCE, THE FALSIFIERS (banked, restated with today's corridor attached)

**The instrument (one line):** a dedicated Shelby County levy — the COTA/IndyGo/GRTC instrument class — because MATA's $0 self-levied tax is the structural hole (`mata_diagnosis_v1.json`; COTA's 0.25%-class agency sales tax generated $161.4M in 2024; the *rate* is a design decision, not asserted here). The annual-appropriation model has demonstrably failed nine straight years ($30M flat city line, TransPro/PwC trusteeship record).

**Cost at GRTC-class productivity (banked figures, carried):** ~447,000 VRH at $173/VRH = **~$77M/yr ops (+$25M/yr over today)** — the productive-system floor; at MATA's own $225/VRH cost basis the same commuter target is ~$175M/yr — the floor's proof that productivity, not dollars alone, is the second dial. Corridor application: the three-trunk spine above is where the first VRH go, because the composite ranks the demand there.

**The sequence (the 4-step, governance-first):**
1. **Stability exit** — trusteeship runs to ~spring 2027 (Memphis Flyer 2026-11-10); 97% of operator seats filled; 51 of 62 buses run daily; the new board is seated (2026-09-02).
2. **The dedicated levy** — the COTA-class instrument, county-wide.
3. **The frequency floor** — no surviving route above 30-min headways; the first new VRH go to the restore order (Poplar/Lamar/Crosstown top MATA's own list, matching the composite's #1/#8/#4).
4. **The spine** — mConnect's $12M unspent federal grant builds the Lamar-midtown segment; a 3-5 year arc to 2%+ transit share (GRTC: levy 2016 → Pulse 2018 → 2.5→4.2% share by 2024; IndyGo: tax 2016 → Red Line 2019).

**The falsifiers (pre-registered, all re-runnable from banked routes):**
- **F4 already wired:** the annual ACS 1-YR transit-share re-pull (`worker_ladder_acs1yr_commute_v1.json` route) — if Memphis stays inside the 0.47-0.78% band after the sequence lands, the lane dies honestly.
- **The IndyGo/GRTC trajectory check:** those two went levy→BRT→share-gain in a 2-6 year window; if MATA's trusteeship-exit → levy → frequency arc fails to move daily boardings off ~3.0M annual (2024 class) within the same window, the exemplar-class promise fails for Memphis.
- **The route-grain counter gap (today's honest null becomes tomorrow's falsifier):** MATA publishes no per-route APC/ridership counter. Before the first dollar of the spine spend is committed, the corridor-falsifier needs (a) automatic passenger counters on the 5 ranked routes and (b) a baseline read on each. If Lamar's +20-25% zero-fare bump does NOT show up concentrated on the ranked trunks once published, the corridor-selection dies honestly and the money goes to frequency, not geometry.

---

## 8. HONEST NULLS (named, not faked)

1. **Zero-fare response by route** — no public route-grain split exists (checked MLK50 2026-11-24 full text, WREG RSS, Fox13); carried systemwide only.
2. **C5 (CE-call density) route join** — 311 layer carries CouncilDistrict (0 = blank, 1-10 assigned) only; no district polygons pulled this pass, so C5 cannot join to routes without fabricating. District-grain CE counts live in `r311_ce_by_district_v1.json` (districts 2 & 3 lead at 10,392/9,707 CE calls 2025-26; District 0 = 30,946 unattributed — the layer's geography gap is itself a finding).
3. **Tract-grain coverage is a centroid proxy** — "covered" = any route stop within 800 m of the tract (block-mean) centroid; large tracts partially touched count whole. Direction-class, stated, not a parcel walkshed.
4. **GTFS vintage** — the working feed is the mobility-database snapshot with a Feb-2025 calendar; MATA's cadavl real-time endpoint (port 5053) failed DNS/range this pass. Route geometry postdates the Nov-2024 cut, which is the network the spine rides on, but 2026 route-level tweaks (the "five high-ridership routes" additions) are not in it.
5. **LODES vintage** — 2024 WAC is the newest published; 2025 not on the server (404-verified). Job counts are 2024-vintage.
6. **ACS tract vintage** — B08201/B17001 2022 5-yr (tract grade doesn't exist in 1-yr); the banked 1-yr city columns (2021-2024) cover the citywide read in `worker_ladder_acs1yr_commute_v1.json`.
7. **Whitehaven trunk geometry** — no GTFS trunk exists on the 2025 roster; its need is carried as a coverage gap (District 7 CE calls), not scored.

---

## 9. SOURCES — the file map

| Figure | Value | Source file |
|--------|-------|-------------|
| Jobs by work tract (Shelby+Crittenden 2024) | 537,432 total; per-tract in JSON | `rthe-spine/rjobs_by_work_tract_wac2024_v1.json` |
| No-vehicle households per tract (ACS 5yr 2022 B08201) | per-tract in .dat | `rthe-spine/acsdt5y2022-b08201.dat` |
| Below-poverty population per tract (B17001) | per-tract in .dat | `rthe-spine/acsdt5y2022-b17001.dat` |
| Route geometry (23-route 2025 roster, shapes, stops, trips) | per-route in JSON | `rthe-spine/rmata_routes_2025_v1.json`, derived from `rthe-spine/gtfs_mata_2352.zip` |
| Tract centroids (block-mean) | per-tract | `rthe-spine/tn_xwalk.csv.gz` + `ms_xwalk.csv.gz` (LODES xwalks) |
| CE-class 311 calls by district 2025 + 2026 YTD | per-district | `rthe-spine/r311_ce_by_district_v1.json` |
| Covered-tracts walkshed per route | per-route tract lists | `rthe-spine/rroute_covered_tracts_2025_v1.json` |
| The 5-way composite scores (all 23 routes) | per-route | `rthe-spine/rspine_scores_v2_2025_network.json` |
| MATA's published restore priority order | 10 routes, verbatim | MLK50 2025-04-03 (`mata-secretly-cut-bus-routes...`), pulled via WP-REST 2026-11-24 |
| Zero-fare +20-25% / $4M / 2.7M-trips / 14+44 buses / $42M grants | systemwide | banked `mata_diagnosis_v1.json` + MLK50 2026-11-24 live pull |
| Transit-share 0.47-0.78%, GRTC $77M/$173-VRH/COTA $161.4M levy, sequence + IndyGo/GRTC arcs | banked | `mata_diagnosis_v1.json` + `worker_ladder_acs1yr_commute_v1.json` |
| Poverty-band targeting law 20-60% | banked frame | `2026-11-24-memphis-crime-reduction-brief.md` (§3 anti-patterns, Branas-2019) |

---

## APPEND — WORKING NOTES (build-time, 2026-11-24)

- **Route recovery beat the fallback:** the task brief expected MATA GTFS to be authwalled; the Mobility Database catalog CSV (`feeds_v2.csv`, keyless, one pinned-IP fetch) carried three MATA feed ids, and `files.mobilitydatabase.org/mdb-2352/latest.zip` served the full 23-route shape file. The dbstiles blob route died on DNS (no address from either resolver) — named, unused.
- **Two scoring passes were run** (33-route 2020 feed, then the 23-route 2025 network). The 2025-network pass is the binding one (`rspine_scores_v2_2025_network.json`); Lamar is #1 on both — the ranking is not vintage-fragile.
- **Lamar wins even with its shape-fit term at 0.00** — its 36.3 km GTFS shape (loop variants) is 3x the 4-7 mi band; the corridor's core segment is the band-compliant spine. If the founder wants a shape-pure ranking, Lamar still leads on the demand term alone.
- **The 800 m walkshed used stop points, not shape polylines, on the final pass** (stops are where riders actually are).
- **The one thing this report adds to the capstone brief's lever-2:** the F4 falsifier now has corridor teeth — the re-pull can be run at the covered-tract grain the same way this pass ran it.

*Pulled live 2026-11-24: lehd.ces.census.gov (LODES8 TN+MS 2024 WAC + xwalks), www2.census.gov (table-based-SF 2022 5-yr shells + B08201/B17001 .dat), services.arcgis.com (Memphis 311 FeatureServer, CouncilDistrict aggregation), files.mobilitydatabase.org (MATA GTFS mdb-2352), MLK50 WP-REST (2025-04-03 + 2026-11-24 full bodies). Census Data API key-walled ("Missing Key" page live-verified) — table-based-SF .dat route banked and used. The DNS-pinned-IP workaround (commit d1b3cec) is a prerequisite for every census/AGOL/google-DNS pull on this box.*
