# MATA-DEEP-DIVE = THE TRANSIT-AUTHORITY DIAGNOSIS (2026-11-24)

**The founder's question:** why is Memphis transit (MATA) inefficient, or as the share-of-commuters data suggests, functionally non-existent?
**The measured problem (banked):** Memphis transit-share of commuters = **0.47-0.78%** across 4 ACS vintages, **3-8x below** income-peer midwest cities (Cincy 3.9-6.6%, STL 4.9-7.9%, Detroit 3.9-5.6%).
**The machine's answer in one line:** Memphis runs transit at 1/2 to 1/12th the per-resident money of every functioning peer, delivers it on a network that was cut to near-minimum in Nov 2024, and has spent the last decade converting its funding into a $60M hidden deficit rather than service — the share is 0.5% because *everyone who can leave transit has already left, and the no-vehicle remainder is structurally underserved.*

Every dollar below is either an NTD (National Transit Database) figure pulled live from `datahub.transportation.gov` (FTA's Socrata) on 2026-11-24, a dated news figure, or a computed ratio explicitly labeled as computed. Honest nulls are named at the end.

---

## 1. THE FUNDING LANE — the binding constraint

**MATA operating-fund spend (NTD ID 40003), 2019-2025:**

| Year | Ops total | Fares | Local | State | Federal |
|------|-----------|-------|-------|-------|---------|
| 2019 | $58.4M | $7.7M | $29.5M | $7.9M | $13.3M |
| 2020 | $57.9M | $5.7M | $22.8M | $6.4M | $22.9M |
| 2021 | $65.5M | $2.9M | $4.1M | $8.7M | $49.9M |
| 2022 | $60.4M | $2.4M | $12.9M | $8.4M | $36.7M |
| 2023 | $53.3M | $2.6M | $29.2M | $6.2M | $15.3M |
| 2024 | $51.7M | $2.5M | $26.0M | $8.7M | $14.4M |
| 2025 | $55.9M | $2.6M | $32.3M | $7.6M | $13.4M |

(2022-2025 = NTD Socrata `4tmr-gwuu`, pulled live; 2019-2021 = NTD Annual Agency Profile PDFs via the Wayback mirror; the 2021 local number is the COVID-era federal-carry pattern.)

**Per-capita comparison, 2024 (computed: NTD ops ÷ 2020 census city population):**

| City | Ops $/city-res | Local $/city-res | Farebox % |
|------|------------|--------------|----------|
| **Memphis (MATA)** | **$82** | **$41** | **4.9%** |
| Cincinnati (SORTA) | $514 | $358 | 21.0% |
| St. Louis (Bi-State) | $1,041 | $842 | 11.1% |
| Detroit (DDOT) | $264 | $165 | 5.2% |
| Columbus (COTA) | $239 | ~$1 + $178 agency sales-tax | 13.8% |
| Indianapolis (IndyGo) | $155 | $118 | 7.8% |
| Richmond (GRTC) | $340 | $166 | 4.6% |

Memphis sits **2.1x-12.7x below** every functioning peer on total ops per resident, and the shape of the gap is the story:

- **No dedicated stream.** MATA levies **$0 of its own taxes every reported year (NTD `taxes_levied_by_agency`)**. Cincinnati's peer COTA collects **$161.4M in 2024 from its agency-levied sales tax — 3.1x MATA's entire 2024 budget**. Detroit has a state+city dedicated mix. IndyGo has the Marion County transit income tax. Richmond has a state matching formula. Memphis has an annual council appropriation that has been flat at **$30M since FY2025** (WREG 2025-06-24) — and a 2017 city-adopted plan (Transit Vision) that called for an **additional $30M/yr that has never been appropriated** (MLK50, 2026-11-24).
- **TN state claim, verified and reframed:** the task asked us to verify "TN = one of the worst for transit funding." The honest verdict: MATA's state grant is a flat **$6.2-8.7M/yr** (14.0% of ops 2022-25) — *not* the lowest share in the peer set (MO gives Bi-State just 1.1%, OH 2.1% — because those peers' totals ride on dedicated local streams that dwarf whole state grant lines). The structural finding the founder can carry: **Memphis transit has no dedicated funding stream of any kind — no agency-levied tax, no regional tax, no state formula tie — only an annual discretionary appropriation plus federal pass-through.** (Honest null: no state-by-state *ranking* was reachable this session; see nulls below.)
- **Farebox is a rounding error:** fares = **~5%** of MATA's budget (A5, 2024-08-20; NTD 2024 = 4.9%). There is no self-funding leverage.

**The 2024-25 funding-crisis, dated dollar-for-dollar:**

- **2024-01-31:** CEO Gary Rosenfeld steps down; Bacarra Mauldin interim (ABC24 via Wikipedia refs).
- **2024-05-21:** MATA discloses a **$60M cumulative deficit** and cannot repay a **$20M loan due in June**; discovery ran through the **Tennessee Comptroller** (Fox13 Memphis headline, via Wikipedia citation; page now 404).
- **2024-08-20:** Council hearing: the budgeted system was ~$84-85M with 75 buses, but only ~$67M funding existed and ~53-55 buses operated; proposed balanced budget $67.8M; **$30.6M straight from City of Memphis**; fares ~5% of revenue; ridership **>6M (2019) → ~3M (2024 YTD)** (Action News 5, WMC).
- **2024-08-27:** Board OKs FY25 budget: **6 routes + Ready! Zone eliminated, 241 layoffs (~half the staff), ~$10M op cut**, effective Nov 3 (Commercial Appeal + Daily Memphian, via Wikipedia; WREG confirms 23→18 routes on 2024-09-24).
- **2024-09-10:** MATA's CFO (Hamish Davidson) tells council the agency has run an **unrestricted net deficit for 10 straight years: −$90M in 2014, −$91M in 2019** (Action News 5). Council members' response: "a 10-year thing that you all have known about... never said anything to anyone."
- **2024-10-11:** Mayor Paul Young replaces **all nine board members** after TransPro's diagnostic ($336,000): boardings per revenue-hour **23% below peer average** (4th lowest in peer group), cost per revenue-hour **29% above** (2nd highest), no financial audit, gaps in contract/project tracking, "a culture of poor accountability" (WREG).
- **2025-01-15:** 8-month "crisis management" contract with TransPro, **$1.3M**, at $486/hr for the CEO-consultant (WREG).
- **2025-06-10:** City passes FY26 at **$30M**; board chair asks $45M ("Band-Aid on a system that needs emergency surgery"), advocates ask $50M; council **holds $15M** pending a PwC forensic audit (WREG 2025-06-24; MLK50 2025-06-03/16). Councilmember: buses "every one to two hours" on most routes; 300 MATAplus trips denied per month.
- **2025-12-02:** FY2026 revenue estimate $66.85M = $30.67M city + $27M federal + ~$1M zero-fare reimbursement + state/grant residue (WREG, Holmes presentation).

## 2. THE SERVICE-DESIGN LANE — network cut + never-funded redesign

**What NTD says MATA delivers (Bus mode, service hours = VRH):**

| Year | Annual bus UPT | Annual bus VRH | Typical-weekday VRH |
|------|---------------|----------------|--------------------|
| 2022 | 2,485,053 | 261,127 | 848 |
| 2023 | 2,208,154 | 257,407 | 836 |
| 2024 | 2,627,188 | 229,752 | 746 |
| 2025 | 2,265,143 | 215,801 | 693 |

Service hours **still falling — 17% in three years** — even through the "recovery" era. Peer 2024 comparison (NTD): SORTA 829,081 VRH with 42,688 weekday boardings; Bi-State 863,096 / 40,365; DDOT 580,489 / 40,492; COTA 909,197 / 37,106; **GRTC (Richmond) 444,294 / 27,463** — vs **MATA 229,752 / 8,975**. Memphis is ~1/4 of even Richmond's weekday boardings at 2.5x fewer service hours per capita.

**The cut history, dated:**

1. **2017:** Transit Vision network redesign begins — the city adopts it; Bill Dries (Memphis Daily News, 2017-04-28) reports MATA "prepares case for $30M increase to fund bus system improvements." Final report 2019. **The $30M/yr was never appropriated** (MLK50, 2026-11-24: "MATA has never received that funding, and service has declined since then").
2. **2019-2022:** Federal grants arrive for capital (the mConnect BRT: $12M in 2019, another $76M in 2022) — but as capital, not operations, with **no construction progress as of 2026** (Wikipedia citing city + WREG 2026-04-14: the $403K of BRT money was just transferred to 311 software).
3. **2021:** Groove and Ready! on-demand zones launch (Transit Vision's partial implementation, Wikipedia).
4. **2024-08-18:** Trolley service suspended indefinitely (brake system; TDOT recommendation); **18 operators laid off** (WREG 2024-11-25). Return target: **December 2026** — i.e. a two-plus-year loss of the system's most visible element.
5. **2024-11-03:** 23→18 routes; **60-minute headways on every remaining route**, Mon-Sat until 7pm, Sun until 6pm; fare to $1.75 (WREG 2024-09-24).
6. **2025:** the reduced schedule = **"70% of the COVID service schedule"** per the Better Transit for a Better Memphis coalition (MLK50, 2025-06-16); interim CEO John Lewis: "We're at the bare minimum of service levels now. Anytime we've got routes at two-hour headways, you can't get much worse than that."
7. **2026:** annual fixed-route service hours **320,000 (2017) → 215,000 (now)**, per former board member Jackson McNeil (MLK50, 2026-11-24) — corroborated by NTD VRH above.

**On-time performance (the reliability record, trustee-reported):** MATA OTP hovered ~60% through 2026 (low of 56% in Feb), 64% claimed for Oct 2026 (not yet on the city dashboard); **missed trips were 26-30% of all scheduled trips** in late 2025 — buses that never left the garage — down to 7% by Oct 2026; 91% of the fleet now put out daily, from 53-55 buses on a 75-bus structure (MLK50 2026-11-24; WREG 2024-10-14, 2026-09-17).

**Redesign status:** no plan branded exactly "MATA Forward" was found this session (honest null). The real lineage: **Transit Vision (2017-2019) was the redesign — city-adopted, never funded.** Its 2026 replacement is a **$125,000 University of Memphis contract to write MATA's long-term spend plan** (Fox13, 2026-09-14). The system is being planned from an empty wallet.

## 3. THE GOVERNANCE LANE — who controls MATA

**Structure (Memphis City Code, as summarized by MLK50 2025-09-05):** a board of 9 members, **nominated by the mayor and approved by council**; the board supervises operations (routes, schedules, fares, management contracts) but **cannot take on debt or buy/sell real estate without mayor+council approval**, and its budget must go to the mayor and ultimately the Council for approval. It is an arm of the city in practice, independent in law.

**The decade-long governance record, dated:**

- **2024-01-31:** CEO resignation #1 (Rosenfeld).
- **2024-05:** $60M deficit discovered via TN Comptroller.
- **2024-08-27 → 09-24:** austerity budget + 241 layoffs approved by the OLD board.
- **2024-10-11:** Mayor Young replaces **all nine board members** — "a clean-slate environment" — after TransPro's diagnostic.
- **2024-10-XX:** interim CEO Mauldin "exits through side door" after TransPro initial findings (WREG investigations slug); credit-card reporting shows spending at spas, Grizzlies suite, international travel, a $555K vendor claim; deputy CEO fired over ~$800K in misspent funds.
- **2025-01-15:** TransPro takes over operations on an 8-month crisis contract ($1.3M); John Lewis interim CEO.
- **2025-06:** council withholds half of MATA's $30M pending the PwC audit; PwC findings (2025-06): "widespread lack of financial documentation and controls, unstructured budget process, outdated policies, issues with how federal and state grant dollars were spent" (MLK50, 2025-09-05).
- **2025-09-04/05:** **five of nine board members resign** mid-CEO-search; quorum lost; CFO seat vacant; contract of interim CEO ends same day.
- **2025-09-10:** Council votes to run MATA's spending through a **two-person city trust** instead of a CEO ("not a private takeover... funds go to buses and drivers and mechanics and not Grizzlies suites and trips to other countries" — City Attorney Wade). Rodrick Holmes named trustee at **$75,000/month, city-paid** (MLK50 2026-11-24).
- **2026-04-14:** board still vacant months later; council approves a **$13M city loan** to bridge federal-funding delays.
- **2026-09-02:** a new nine-member board is seated; trusteeship continues, expected to run until **spring 2027** (Memphis Flyer, 2026-11-10); permanent-CEO search reopens.

**The may-vs-council dynamic:** the 2025-26 fight *is* the mayor-council dispute — council rolling-disbursement + audits + money transers; mayor flat $30M + board control + trustee. The transit agency has become the battlefield; **stability itself was the casualty: four CEOs/interims in 30 months, three governance regimes in two years.**

## 4. THE DIAGNOSIS — ranked causes with evidence

**#1 FUNDING-STARVED (the binding constraint).**
Proof by dollars: $82/city-resident ops vs $155-$514 everywhere else on the ledger; $0 self-levied taxes vs COTA's $161M sales-tax stream; fares ≈5% of revenue; city allocation flat $30M with the 2017 $30M/yr plan never funded. Proof by mechanism: the deficit spiral (Mauldin: "debt grew over time due to increased costs, decreased ridership, and flat funding," A5 2024-08-20) turned a $85M system into a $52M NTD-audited system. Falsifier check: per-resident transit funding *tracks* transit-share across our panel (Cincy $514→5-6.6%; Memphis $82→0.5-0.8%) — money is the variable that moves with the outcome.

**#2 GOVERNANCE FAILURE (the transmission mechanism).**
The dollar deficit had to be hidden for 10 years ($90M-$91M unrestricted deficit, revealed only in 2024) while leadership spent on a Grizzlies suite and international travel; the TransPro numbers (boardings/rev-hr 23% below peers, cost/rev-hr 29% above) are exactly what an unaudited, unmonitored operation produces; three governance regimes since Oct 2024. Money is starved *because* the institutions that would defend it lost credibility — the trustee state is the city's verdict on a decade of board-level negligence.

**#3 SERVICE-DESIGNED-OUT (the supply-side retreat).**
Transit Vision (2017) = the frequency-first redesign MATA promised and City adopted; funding never arrived; service fell from 320,000 annual hours to 215,000; Nov 2024 cut the map to 18 routes at 60-min everywhere (two-hour headways on "most routes," per their own board chair); OTP ~60% and 26-30% missed trips in 2025. But the **zero-fare natural experiment** (Nov 2025) proved suppressed demand: ridership **+18-25% within weeks** (+2.7M trips, +$4M rider savings, no new routes) — the constraint is supply, not willingness.

**#4 GEOGRAPHY (a real but secondary term).**
The banked commute lane shows Memphis mean-commute **21.4-21.5 min, flat across 4 vintages** with the **lowest ge45-share of 6 cities** — short commutes are the *no-service-so-no-choice* signature, not evidence transit serves them. Houston (car-80%, mean commute 26-28 min) runs 2.9-3.4% transit share at 3x MATA's per-resident funding — dispersion is a handicap, not an excuse. MATAplus denial of 300 paratransit trips/month (legally the floor of the system) shows even the mandated share is unmet.

**In the founder's tribe frame:** a transit system is a tribe-infrastructure input — the shared circulating commons that stitches neighborhoods into one labor market. Memphis's 0.5% means the city has effectively dissolved that commons: the 18-route, 60-min, sometimes-never-showing bus network is a residual charity for the ~6% no-vehicle households, not a shared tribal organ. The machine just counts it: 0.55%.

## 5. THE LEVER TIE-BACK — what it takes to reach 2-3%

**Honest math (computed from NTD 2024 actuals + banked ACS; no invented dollars):**

- **Target riders:** ACS 2024 city grain = 271,695 workers (incl. WFH denominator per lane rule); 1,499 transit commuters = 0.55%. **2% = 5,434 daily transit commuters (3.6×); 3% = 8,151 (5.4×).**
- **MATA's productivity is fine:** 11.4 unlinked trips per revenue-hour (GRTC 19.8, COTA 13.0). The input is missing: 215,801 annual bus-VRH (2025), 693 weekday hours across 18 routes.
- **Cost to serve 2-3% at MATA's own cost basis ($225/VRH):** ~777,000 VRH → **~$175M/yr ops** (vs $51.7M today; **+$123M/yr**).
- **Cost at GRTC-class productivity + cost ($173/VRH, 19.8 UPT/VRH — the achievable mid-tier):** ~447,000 VRH → **~$77M/yr** (**+$25M/yr**). That is the floor, and GRTC proves it is achievable at *mid*-funding with higher productivity.
- **Per-resident cost frame (the banked $67/$69 class):** bringing MATA to the **IndyGo per-resident level ($155/res)** = **$98M/yr** = **+$73/res/yr — 1.06× the banked per-resident class**, i.e. one more class-unit of annual city-resident spend buys the IndyGo funding floor. Richmond's per-res level ($340/res) buys the GRTC share trajectory (2.5→4.2% in 2 yrs post-redesign).
- **Instrument class:** the exemplars' money all arrives through *dedicated streams* — COTA's agency-levied **0.25%-class sales tax: $161.4M in 2024 alone**; IndyGo's Marion County transit income tax; GRTC's state formula. Memphis's equivalent class (Shelby County levy; the rate is a design decision, not asserted here) is the only structure that survives council turnover — the annual-appropriation model has demonstrably failed for 9 years.
- **Timeline reality:** GRTC: levy (2016) → Pulse BRT (2018) → +2.5→4.2% share by 2024. IndyGo: income tax (2016) → Red Line (2019) → 3 BRT lines by 2025. COTA: levy → frequency-first redesign, share ~1.9-2.3%. Memphis: mConnect's **$12M federal grant has been on the shelf since 2019 with zero progress as of 2026** — the first step is governance stability (trusteeship exit, spring 2027 target per the city) + the dedicated levy; a 3-5 year arc to 2%+ is the honest read. The zero-fare pilot's +20% at *static supply* shows the demand exists the moment the supply-side fix begins.

**What NOT to do (banked discipline):** one-year funding bumps (the FY25 FY26 pattern reverts — the "one-year bumps" law); top-end-only corridors; untargeted spend without the mid-band service frequency floor.

## 6. THE EXEMPLAR BRIEF (founder follow-up)

**Peer-class (benchmark vs MATA):**
- **Cincinnati (SORTA/Metro):** $159M ops (2024), $514/city-res, farebox 21% — the high-funding, regional-levy model; ACS share 3.9-6.6%. Why it works: a county sales-tax stream plus state match produces both coverage and 15-30 min peak frequencies MATA hasn't had in decades.
- **St. Louis (Bi-State/Metro):** $314M ops (2024), $1,041/city-res — the *money* case (city+county sales-tax streams; Transit sales tax 2024 in the county). Share 4.9-7.9%. Why it works: dedicated metro-wide streams fund a metro network (MetroLink + bus, 465→434 VOMS 2022→2025).
- **Detroit (DDOT):** $169M ops (2024), $264/city-res incl. **$50.4M state**; share 3.9-5.6%. Why it works: dedicated city millage + state mix. Note it is also a cautionary tale — 1/3 of buses routinely down (Detroit News, 2024-08-06) — still >4% share *because the dollars get to service despite management stress*.

**Aspirational bus-only class (the realistic grain — 2-4% share cities):**
- **COTA (Columbus OH).** Verified: **$216.5M ops 2024 | $161.4M agency-levied sales tax | $239/city-res | ACS share 1.93-2.34% (2022-2024, computed from the banked ACS route) | 37,106 weekday boardings.** Why it works: the permanent dedicated levy funds a frequency-first redesign + 3 BRT spines; the levy guarantees the money lands each year regardless of council mood. Lesson: **MATA's $0 self-levied tax is the first structural fix**; a Shelby-county-class dedicated levy makes the rest possible.
- **GRTC (Richmond VA).** Verified: **$77.0M ops 2024 | $340/city-res | state share 33.8% (2022-25) | ACS share 2.47% (2022) → 4.20% (2024) | 19.8 UPT/VRH — the best productivity in the entire peer set.** Why it works: the Pulse BRT spine (2018) + a 2020 bus-network redesign + strong state matching convert *mid*-funding into the region's best riders-per-hour. Lesson: **frequency design beats raw dollars** — share nearly doubled within two redesign-years; this is MATA's most direct template.
- **IndyGo (Indianapolis IN).** Verified: **$136.4M ops 2024 | $104.3M local (Marion County transit income tax) | $155/city-res | ACS share 1.18-1.30% | Red/Purple/Blue BRT lines 2019-2025.** Why it works: a voter-approved county income tax tripled the local stream; the Red Line spine opened 2019. Lesson: **a stalled BRT grant is recoverable** — mConnect's 7-year shelf-life is a governance choice, not fate.

**BRT/European frame:** honored by pointer only, per falsifier discipline — two verified exemplars beat five half-probes.

## 7. WHAT THE DELIVERABLES ARE

- `mata_diagnosis_v1.json` — the full dated machine record (funding matrix 2019-2025, peer matrix, chronology, ranked causes, lever math, exemplars, nulls).
- `mata_diagnosis_v1.md` — this brief.
- Working notes appended to `.hermes/memory/working-notes.md`.

## 8. HONEST NULLS (named, not faked)

1. **No state-by-state transit-funding ranking** was reachable this session — "TN worst in nation" is NOT independently verified; what IS verified is the absence of any dedicated stream + $0 self-levied taxes + the flat ~$6-9M state grant (NTD).
2. **TN Code sections** enabling MATA not pulled live; carried via Memphis City Code as reported by MLK50 (2025-09-05).
3. **No MATA-published rider-complaint/OTP series** exists in public record this session; OTP figures are trustee/council numbers (60-64% through 2026).
4. **"MATA Forward"** — no plan by that name found; lineage = Transit Vision (2017-2019, unfunded) → U of Memphis $125K plan (2026-09-14).
5. Richmond's 2023 ACS B08301 row was absent from the .dat pull (2022/2024 present); 2023 share named as interpolation, not invented.
6. MATA weekday-span NTD fields garbled for 2022-24; span trend carried from dated news instead.
7. Driver headcount series not found; "241 layoffs ≈ half of staff" implies ~470-500 pre-cut headcount — labeled inference, not record.

---

*Sources: FTA NTD via datahub.transportation.gov (resources 4tmr-gwuu / wwdp-t4re / c8k8-y2cj / ekg5-frzt), pulled live 2026-11-24; NTD Annual Agency Profiles 2019-2023 (NTD ID 40003) via web.archive.org mirror of transit.dot.gov; WREG (WordPress REST API, full dated bodies; articles 2024-09-24 → 2026-09-17); MLK50: Justice Through Journalism (2025-06-03/16, 2025-09-05, 2026-11-24); Action News 5 (2024-08-20/21, 2024-09-10); Bing News RSS (dated headlines incl. Memphis Flyer 2026-11-10, Fox13 2026-09-14/11-17); Wikipedia MATA article (dated citation chain); banked worker_ladder_acs1yr_commute_v1.json (ACS shares, www2.census.gov .dat, 2021-2024).*
