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
- 2026-05-21T12:33:16.507+02:00: Weekly analysis output must use a strong journalistic headline, explicitly state when no press data is available, and keep `Key References` complete so downstream publishing does not inherit placeholder artifacts.
- 2026-05-21T10:38:30Z: Scribe processed spawn manifest; decision on headline review appended to decisions.md and archived from inbox.
- 2026-05-21T12:25:08Z (2026-W21): A coordinated SEO/star-farming repo cohort (15+ repos, zero forks, 600-632 stars, created within 2 hours on May 17) appeared in new_repos — editorial call is to flag as noise and not feature any member. Trending repos again lacked `stars_gained` data; the trending set functions as a "large repos present in the crawl window" list, not a momentum leaderboard. Top durable signal: agent skills packaging is formalizing (claude-code 17 repos, mcp 15 repos, ai-agents 20 repos as top topics). The week's top new repo is vercel-labs/zerolang (4,076 stars, C implementation, "programming language for agents") — credible provenance, no press coverage, high editorial value as narrative anchor. Press divergence is significant: TechCrunch was all infrastructure/capital (Anthropic-xAI compute deal, NVIDIA earnings), while developers are building at the application/skills layer. Agent evaluation infrastructure remains a persistent blind spot — no repos this week address how to benchmark or verify agent skill quality at production scale.
