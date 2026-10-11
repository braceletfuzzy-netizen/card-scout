# Beta User Survey — Card Scout (Sept 2026)

## Goals (Jonathan, Sept 18)

Find out from beta users:
1. **Functionality** — is the alert system working for them?
2. **Ease of use** — how's the dashboard? Confusing anywhere?
3. **Features to add** — what's missing?
4. **Features to take away** — what feels noisy or unnecessary in Discord alerts?
5. **Updates → website dashboard** — what should be web-visible vs Discord-only?

## Why now

- Beta users have been on the platform for 2+ weeks
- Multiple alerts fired (varies by user)
- Per-grade alerts shipped Sept 18 — feedback window is ideal
- Pre-Pro-tier launch: validate what customers actually want

## Logistics (decided Sept 18)

- **Format**: Google Form, linked in Discord DM
- **Audience**: EVERYONE in beta at send time (dynamic — new signups get surveyed)
- **Anonymous**: Yes (no attribution, no follow-up by name)
- **First run**: ~Sept 25, 2026 (one week from Sept 18 framing)
- **Recurrence**: Weekly while in beta (or monthly — TBD with first results)
- **Length**: 5-7 questions max, mix of multiple-choice + open-ended
- **Reward**: TBD (could offer Pro trial as thank-you — wait for Sept 24 decision first)

## Re-run workflow (when sending weekly)

1. Query DB: `SELECT customer_id, discord_webhook FROM customers WHERE tier = 'beta_*' AND enabled = 1`
2. Generate Google Form (or reuse one with no per-user tracking)
3. Discord DM each customer: "Hey, quick survey (3 min). Anonymous. [link]"
4. Collect responses in Google Sheets (anonymous by default)
5. Tag responses by week, aggregate trends over time

## Questions to ask

### 1. Functionality check
- "Are the alerts you're receiving actionable?" (Yes / Sometimes / No)
- "When's the last time you bought a card because of a Card Scout alert?" (Past week / Past month / Past 3 months / Never)

### 2. Ease of use
- "How easy is it to add a new card?" (1-5)
- "How easy is it to remove a card?" (1-5)
- "Have you used the Browse tab yet?" (Yes, often / Yes, once / No, didn't know about it / No, prefer typing)

### 3. Features to add (open-ended)
- "What's the #1 thing you'd add to Card Scout if you could?"
- (Probes for: pop data? Trending list? Portfolio tracker? Sell-side alerts?)

### 4. Features to remove/refine (open-ended)
- "Is anything in the alerts noisy or unnecessary?"
- (Probes for: trend signals? Card Hedger FMV table? Sold data? Q bands?)

### 5. Updates → website dashboard (the key strategic question)
- "What's something you currently see in Discord alerts that you'd rather see on the website?"
- "What would make you check the dashboard more often?"
- (Probes for: portfolio view? Settings? History? Filters?)

### 6. Pricing validation
- "If Pro tier ($150/mo) had X, Y, Z, would you consider it?"
  - X = per-grade FMV at PSA 9, BGS 9.5, etc.
  - Y = population data
  - Z = trending list / hot 10
- "What's the max you'd pay per month for what you're getting today?"

### 7. Overall satisfaction
- "How likely are you to recommend Card Scout to a friend?" (1-10, NPS)
- "One sentence: what's the best part of Card Scout?"
- "One sentence: what's the worst part?"

## After each survey run

1. Aggregate responses into a sheet (rows = response, cols = question)
2. Tag responses: functionality / UX / feature_add / feature_remove / pricing
3. Update parking lot with new fires discovered
4. Brief Jonathan: top 3 takeaways + 3 priority items
5. Schedule next send (or pause if response rate is low)

## Trends over time (the real value)

- First survey: baseline
- Each subsequent survey: track trend on each question
- "How easy to add a card was 3.2 in Sept, 4.1 in Oct" = meaningful signal
- NPS over time = leading indicator of product-market fit

## Risks

- Survey fatigue: don't send more than weekly
- Leading questions: avoid "Would you like X?" → ask "What's missing?"
- Low response rate: 2-3 customers is a small sample. Aggregate carefully.
- Bias toward power users: Jim is engaged, others may not respond

## Open questions (resolved Sept 18)

1. Survey format: **Google Form via Discord DM**
2. Anonymous or attributed: **Anonymous**
3. Audience: **Everyone in beta that week** (dynamic)
4. When to send: **Start ~Sept 25**

