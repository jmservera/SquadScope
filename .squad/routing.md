# Work Routing

How to decide who handles what.

## Routing Table

| Work Type | Route To | Examples |
|-----------|----------|----------|
| Data crawling, GitHub API, Actions workflows | Bender | Build crawler, fix API pagination, add rate limiting |
| Trend analysis, content curation, critical thinking | Farnsworth | Analyze weekly data, identify trends, write summaries |
| Frontend, site design, GitHub Pages, templates | Amy | Build site layout, create report templates, fix styling |
| Architecture, scope, priorities, editorial direction | Leela | Decide tech stack, review architecture, set priorities |
| Code review | Leela | Review PRs, check quality, approve/reject |
| Security review, threat analysis, vulnerability triage | Hermes | Review PRs for security, triage Dependabot/CodeQL alerts, threat modeling |
| Testing, QA, validation | Fry | Write tests, validate pipeline, find edge cases |
| Scope & priorities | Leela | What to build next, trade-offs, decisions |
| Session logging | Scribe | Automatic — never needs routing |

## Issue Routing

| Label | Action | Who |
|-------|--------|-----|
| `squad` | Triage: analyze issue, assign `squad:{member}` label | Lead |
| `squad:{name}` | Pick up issue and complete the work | Named member |

### How Issue Assignment Works

1. When a GitHub issue gets the `squad` label, the **Lead** triages it — analyzing content, assigning the right `squad:{member}` label, and commenting with triage notes.
2. When a `squad:{member}` label is applied, that member picks up the issue in their next session.
3. Members can reassign by removing their label and adding another member's label.
4. The `squad` label is the "inbox" — untriaged issues waiting for Lead review.

## Trigger Phrases

| Phrase | Action |
|--------|--------|
| "take a nap and reskill" | Farnsworth reads `.squad/reskill/current-prompt.md` and follows the instructions inside |

## Rules

1. **Eager by default** — spawn all agents who could usefully start work, including anticipatory downstream work.
2. **Scribe always runs** after substantial work, always as `mode: "background"`. Never blocks.
3. **Quick facts → coordinator answers directly.** Don't spawn an agent for "what port does the server run on?"
4. **When two agents could handle it**, pick the one whose domain is the primary concern.
5. **"Team, ..." → fan-out.** Spawn all relevant agents in parallel as `mode: "background"`.
6. **Anticipate downstream work.** If a feature is being built, spawn the tester to write test cases from requirements simultaneously.
7. **Issue-labeled work** — when a `squad:{member}` label is applied to an issue, route to that member. The Lead handles all `squad` (base label) triage.
