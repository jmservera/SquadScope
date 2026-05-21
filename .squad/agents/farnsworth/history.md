# Farnsworth — History

## Core Context
- Owns editorial analysis of GitHub and adjacent press signals for the published weekly brief.
- Analysis output must stay useful to readers and structured enough for downstream automation.

## Learnings
- The analyzer contract should remain a superset of the published weekly frontmatter plus the quality gate so one artifact serves editorial and pipeline needs.
- Weekly briefs work best as named macro trends supported by repo evidence, with repo links rendered from the crawl artifact's `url` field.
- Press and industry coverage are correlation signals, not material to repackage; the value is in explaining the gap between narrative and developer traction.
- Reader-facing renders need a cleanup pass that strips AI-only scaffolding before publication.
- The learning loop only matters when lessons are persisted and injected back into the next prompt through shared wisdom and skills.
- The squad reskill audit showed repeated charter and history scaffolding across agents; that boilerplate now lives in `minimal-agent-charter`, `agent-history-hygiene`, and `weekly-learning-loop`.
- The reskill pass also cut squad agent-doc footprint from 39568 to 12521 bytes, with every charter at or below the 1.5 KB target and the largest histories back under maintenance limits.
- **2026-05-21T10:11:07Z:** Agent-skills as a packaging category emerged this week as a distinct, countable signal (10+ repos in a single crawl week) — watch for a canonical registry or package manager in coming weeks as the obvious next step in this pattern.
- **2026-05-21T10:11:07Z:** The fork-to-star inversion ratio (2000–4500 forks on repos with <200 stars) is a reliable primary noise filter for SEO-spam and crypto-bot farm repos; consider proposing it as a named filter rule in the crawler's filter_summary.
- **2026-05-21T10:11:07Z:** When `api_calls_used: 0` and `stars_gained` is universally absent from trending_repos, all trend statements must be directional only; the momentum caveat is not a footnote but a first-class editorial constraint that should appear in the Blind Spots section explicitly.
- **2026-05-21T10:11:07Z:** The prior file at `data/analyzed/2026-W21-summary.md` used non-spec H2 sections and referenced repos not in the raw payload; the analysis-spec.md output contract (six exact H2 headings, no `### Signal`/`### Noise` sub-headings in Signal & Noise) must be enforced on every run regardless of what a pre-existing file contains.
