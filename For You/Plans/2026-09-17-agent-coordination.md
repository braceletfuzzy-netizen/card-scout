---
type: agent-coordination
created: 2026-09-17
purpose: Tell every AI agent (Hermes, Claude Code, Codex, OpenCode, future
  Hermes sessions, etc.) how to read Card Scout state and how to write back
  to it. Lives in git history as the durable reference.
audience: AI agents AND the founder
---

# Card Scout — Agent Coordination Note

**If you're an AI agent working on the Card Scout project: read this first.**

This file tells you where to find the current state of the project, where to
write updates when you do work, and the conventions to follow so other agents
(future you, the next agent, the founder) can pick up where you left off.

## TL;DR

1. **Read first**: `Sessions/README.md` and `Sessions/handoff.md` (gitignored)
2. **Read second**: `.hermes/memory/working-notes.md` (canonical current state)
3. **Read third** (only if relevant): `For You/Plans/data-provider-comparison-2026-09-16.md`
4. **When you finish**: update `Sessions/handoff.md` with what you did + what's
   next, even if you only changed one line. Future agents need that breadcrumb.

## Why this exists

Multiple AI agents may work on this project (Hermes for ongoing work,
Claude Code / Codex / OpenCode for delegated coding tasks). Without a shared
context, each agent re-discovers the same facts, contradicts previous
decisions, or loses track of pending fires. This file is the agreement on
how we avoid that.

## Read order (every agent, every session, every task)

### 1. `Sessions/README.md`
- Agent-agnostic contract: explains the Sessions/ folder layout
- ~5 min read
- Tells you what's in `Sessions/`, what's gitignored, what the YAML
  frontmatter means, how topic pages are organized

### 2. `Sessions/handoff.md`
- Current state snapshot: what's done, what's next, what's blocked
- ~2 min read
- Has the TL;DR at top, then "What was done this session," "What is OPEN
  (active fires)," "Parking lot," "Next agent's first action"

### 3. `.hermes/memory/working-notes.md`
- Canonical current state, longer-form
- ~3 min skim (sections marked with timestamps)
- Has founder preferences, customer list, cost ledger, resume pattern
- **NOTE**: This is Hermes-flavored (references `.hermes/sessions/` paths)
  but other agents should still skim it — the *facts* are agent-agnostic

### 4. Plan docs in `For You/Plans/` (only if relevant)
- `data-provider-comparison-2026-09-16.md` — current data stack strategy
  (eBay Browse API + GemRate + SCPro; Card Ladder cancelled; PSA actor
  likely obsolete)
- `cost-cutting-roadmap-2026-09-16.md` — 5-stage scaling roadmap
- `z-score-framework-2026-09-16.md` — deal detection math
- Other plans in this folder are session-personal notes; check `type` in
  frontmatter before reading deeply

### 5. Session topic pages (only if relevant)
- `Sessions/2026-09-17-card-ladder-trial.md` — research on Card Ladder
- `Sessions/2026-09-17-inline-card-search.md` — PL-008 UX spec
- `Sessions/2026-09-17-gemrate-discovery.md` — GemRate research
- `Sessions/2026-09-17-gemrate-inquiry-draft.md` — vendor outreach draft
- `Sessions/parking_lot.md` — all deferred items (PL-001 through PL-010+)

## Write conventions (when YOU do work)

### When you complete or modify work

Update `Sessions/handoff.md` — append or modify the relevant section:

```markdown
### Fire X: <name>
- **Status**: <new status>
- **NEW**: <what you just did>
- **Next agent's action**: <what comes next>
```

If you discover a new fire, add it. If you resolve a fire, mark it
`RESOLVED` and move the summary to `parking_lot.md` "Resolved items" history.

### When you defer work

Add a `PL-NNN` entry to `Sessions/parking_lot.md`. Use the existing format:

```markdown
### PL-NNN — <short name>
- **Deferred**: YYYY-MM-DD
- **Context**: <why it's not done now>
- **Action when picked up**: <what to do>
- **Why deferred**: <what's blocking>
```

### When you discover something durable

If you find a fact that future sessions will need, decide:

- **Add to memory** (preferences, environment facts, corrections) — survives
  across sessions
- **Add to working notes** (`.hermes/memory/working-notes.md`) — durable
  current state
- **Add to topic page in Sessions/** (per-fire research, scratch work)
- **Add to plan doc in For You/Plans/** (strategic decisions)

When in doubt: working notes > Sessions/ topic page > memory. The Sessions/
files are gitignored and won't survive if the folder is wiped.

### When you commit code

- **NEVER `git add -A`** (per the founder's security rule from a previous leak)
- Stage files explicitly: `git add file1 file2 file3`
- **Untracked files in `For You/Plans/` are personal** — leave them alone
- Run `git status` first, every time

## Founder preferences (CRITICAL — all agents must follow)

- **"One fire at a time"** — serial, not parallel. Don't dump 5 follow-up
  ideas; pick one and execute.
- **"Full picture before commit"** — proactively flag setup time, config
  decisions, ongoing costs, risks. Never bare-minimum pricing.
- **Distrusts flattery** — provide PROOF (math, examples), not reassurance.
- **Non-developer product founder** — plain English + decision tables +
  cost + risk BEFORE code. Lead with diagrams/tables, not raw SQL/Python.
- **"Stop and read" protocol** — when founder says "stop and read this,"
  HARD STOP all fixes, read the docs they paste in FULL, then propose ONE
  clean solution.
- **Future-readiness pattern** — translate architecture into scale ladders
  ("works to N customers → breaks → add X engine"). Show trigger points +
  cost trajectory + migration plan.
- **"No slippage" UX principle** — minimize redirects that pull customers
  off cardscout.pro.
- **Channel for pricing**: pull frequency (not card count)
- **Security**: founder never types passwords; agent stays in control

## Founder identity (for any service signups or outreach)

- **First name**: Jonathan (use for founder-to-founder outreach)
- **Brand**: Fuzzy Bracelet (use for service signups — Card Ladder trial,
  GitHub profile, Porkbun domain, etc.)
- **Email**: braceletfuzzy@gmail.com (Google login across services)
- **Jim** = beta tester (Discord webhook + form submissions). **NOT the
  founder.** Never address the founder as "Jim."

## What NOT to do

- Don't subscribe to anything without pricing response + decision criteria
  check
- Don't scrape Card Ladder internal API (kills B2B partnership path)
- Don't `git add -A`
- Don't start parallel fires
- Don't build Phase 1 PSA actor (likely obsolete; wait for GemRate decision)
- Don't volunteer competitor intel to vendors (e.g., "Card Ladder uses
  GemRate" — even if true, don't say it to GemRate)
- Don't write code without checking `Sessions/handoff.md` first

## Active fires (Sept 17 evening snapshot — likely stale by next session)

1. ⏳ **GemRate partner response** (1-3 business days) — pricing + API key
2. ⏳ **eBay Developer verification** (Day 2 of ~2 since Sept 16)
3. 🎯 **Next fire** — pending founder's call

Always check `Sessions/handoff.md` for the most current list. This section
here is for orientation only — the live answer is in handoff.md.

## For the founder

You don't have to read this file every session. It's a contract for the
agents. But:

- **When you start a new agent session** (new chat, new agent), tell it:
  *"Read `Sessions/README.md` and `Sessions/handoff.md` in my card-scout
  project at `C:\Users\J\Documents\LLM\card-scout\`."*
- **When you delegate coding work** (Claude Code, Codex, OpenCode), include
  the same instruction in the task prompt.
- **If an agent doesn't follow the read-first convention**, point them at
  this file.

## For future agents (reading this for the first time)

If you're new to Card Scout:

1. Read `Sessions/README.md` (5 min) — sets the conventions
2. Read `Sessions/handoff.md` (2 min) — sets the current state
3. Read `.hermes/memory/working-notes.md` (3 min skim) — sets the context
4. If the founder gave you a specific task, do THAT — don't try to fix
   every fire you see in handoff.md. "One fire at a time."
5. When you're done with your task, update `Sessions/handoff.md` so the
   next agent knows what you did and what's next.

Welcome to Card Scout. Let's build something good.
