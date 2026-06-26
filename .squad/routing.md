# Work Routing

How to decide who handles what.

## Routing Table

| Work Type | Route To | Examples |
|-----------|----------|----------|
| Data crawling, GitHub API, Actions workflows | Bender | Build crawler, fix API pagination, add rate limiting |
| Trend analysis, content curation, critical thinking | Farnsworth | Analyze weekly data, identify trends, write summaries |
| Frontend, site design, GitHub Pages, templates | Amy | Build site layout, create report templates, fix styling |
| Visual design, brand assets, icons, design system | Calculon | Design tokens, icon, OG image, layout mockups, design review |
| Architecture, scope, priorities, editorial direction | Leela | Decide tech stack, review architecture, set priorities |
| Code review | Leela | Review PRs, check quality, approve/reject |
| Security review, threat analysis, vulnerability triage | Hermes | Review PRs for security, triage Dependabot/CodeQL alerts, threat modeling |
| DevSecOps pipeline, guardrail tooling, hooks, dependency/secret scanning | URL | Set up ruff/checkov/zizmor CI gates, install git hooks, wire SARIF, pin actions, phased rollout |
| Prompt injection, AI safety, harmful content, dark-pattern review | Nibbler | Prompt/input-output guardrails, untrusted-content fencing, canary checks, RAI review, accessibility/dark-pattern sweeps |
| SEO, titles, meta tags, structured data, search optimization | Zapp | Page title quality, meta descriptions, OpenGraph/JSON-LD, heading hierarchy, content discoverability |
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
| "take a nap and reskill" | Team-wide reskill cycle — follow `.squad/templates/skills/reskill/SKILL.md` |

## Rules

1. **Eager by default** — spawn all agents who could usefully start work, including anticipatory downstream work.
2. **Scribe always runs** after substantial work, always as `mode: "background"`. Never blocks.
3. **Quick facts → coordinator answers directly.** Don't spawn an agent for "what port does the server run on?"
4. **When two agents could handle it**, pick the one whose domain is the primary concern.
5. **"Team, ..." → fan-out.** Spawn all relevant agents in parallel as `mode: "background"`.
6. **Anticipate downstream work.** If a feature is being built, spawn the tester to write test cases from requirements simultaneously.
7. **Issue-labeled work** — when a `squad:{member}` label is applied to an issue, route to that member. The Lead handles all `squad` (base label) triage.
8. **AI-safety review** — work that changes prompts, imported external text, generated content, or user-facing AI output routes through Nibbler before merge.
9. **DevSecOps pipeline & guardrails** — changes to CI security/lint tooling (ruff, checkov, zizmor, Bandit, pip-audit), git hooks, or dependency/secret scanning route to URL. Infra, `Dockerfile`/`Containerfile`, and `.github/workflows/` changes get a URL (pipeline) review alongside Hermes (security).
