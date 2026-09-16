# Card Scout Working Notes (Updated Sept 16, 2026)

## Time
Sept 16, 2026

## Session cadence
**Daily sessions** (confirmed Sept 16, founder preference)

## Timezone
CDT (UTC-05:00)

## Privacy rules
- NEVER share customer webhooks in plain text outside this repo
- NEVER share GCP SA key (use C:\Users\J\.secrets\<project>\)
- NEVER publish Card Scout's 3 actors to Apify Store

## Current state (Sept 16, 2026)

### Customers (3 total)
- `buddy_test_001` (Jim, beta #1) — 12 cards
- `hingle_mccringleberry_1789525909` (Hingle, beta #2) — 3 cards
- `cs_CZYAJYA00001` (test, DEAD webhook 404) — 1 card

### Latest pricing decision
**Casual $15 / Standard $30 / Dealer $75 / Pro $150**
(Margins 71-95%, pull frequency is the lever)

### Cost-cutting roadmap (5 stages)
- Stage 0 (0-10 customers): Apify
- Stage 1 (10+ customers): eBay Buy API (FREE) — sign-up done, awaiting verification
- Stage 2 (25+ customers): + Pricecharting API ($6/mo)
- Stage 3 (50+ customers): + Card Ladder ($20/mo)
- Stage 4 (500+ customers): DIY infrastructure
- Stage 5 (1000+ customers): Strategic partnerships

### Active blockers
1. PSA.com founder blocked (account/IP-level)
2. Card Hedge integration ON HOLD (x402 + sales call friction)
3. Pricing_bands has $0 spread (need sold history from Card Ladder)
4. eBay Developer Account sign-up DONE Sept 16, awaiting verification

### Open fires (priority order)
1. Paste eBay credentials when verified
2. Build eBay Browse API integration (~2-4 hours)
3. Subscribe to PC API (when 25+ customers)
4. Subscribe to Card Ladder (next month or 50+ customers)
5. Phase 1 PSA actor (October target)

### Today's deployed code
- deal_detector.py (z-score lower-third threshold)
- url_parser.py + url_orchestrator.py + url_resolver.py
- V3 alert layout (Jim + founder feedback)

### Lessons learned
- patch tool indents inconsistently in Python source
- "STOP AND READ" protocol — read docs in full before iterating fixes
- "one fire at a time" workflow
- Founder has shower-thoughts that change the game (PSA URL ownership, z-score)
- NEVER `git add -A` — leaked GCP SA key in 1f3e87a

## File system rules

### Project root
`C:\Users\J\Documents\LLM\card-scout\`

### "For You" folder
Personal artifacts (Reddit, Sourcing, Sales, Research, Plans, Personal Collection, Listings, Authenticity)

### Sessions
`.hermes/sessions/session-save-YYYY-MM-DD-{time}-{topic}.md`

### Plans
`For You/Plans/{topic}-{YYYY-MM-DD}.md` (markdown)
`For You/Plans/{topic}-NOTEPAD-{YYYY-MM-DD}.txt` (plain text for notepad)

## Founder preferences (CRITICAL — load first)

- **Distrusts flattery** → provide PROOF (billion-dollar examples, math)
- **NON-DEVELOPER PRODUCT FOUNDER** → plain English + decision tables + cost + risk
- **"STOP AND READ" PROTOCOL** → read full doc, then ONE clean solution
- **"ONE FIRE AT A TIME"** → serial, not parallel
- **Channel for pricing**: pull frequency (not card count)
- **Security**: founder never types passwords; you stay in control
- **PSA credentials**: in Apify secrets manager (not local)
- **Plaintext PSA.txt**: DELETED 2026-09-13

## Founder workflow

- Sketches design ideas on paper before typing into chat
- Shower = best product insights
- "When I come back from a break with an idea..." — capture it cleanly
- Lead with diagrams/tables, not raw SQL/Python
- Future-readiness pattern: "if this gains traction I want to be ready without a rewrite"

## Resume pattern

When founder returns:
1. session_search for most recent save
2. Read open fires section
3. Pick ONE fire (founder's "one at a time" rule)
4. Execute, save, move forward
