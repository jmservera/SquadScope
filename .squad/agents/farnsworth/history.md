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
- 2026-05-21T11:21:08Z: W21 2026 — The "skills packaging" pattern is maturing from individual prompt files into a recognizable paradigm with provider-neutral conventions, install tooling, and institutional backing (anthropics/skills as anchor); this is now a trackable category, not a curiosity.
- 2026-05-21T11:21:08Z: W21 2026 — A coordinated noise campaign involving gaming-bypass repos (zero forks, hundreds of bought stars, keyword-stuffed descriptions) and bot-farm trading repos (2000–4500 forks on 150-star repos) is systematic enough to warrant a filter heuristic: zero-fork repos with >200 stars and SEO-dense descriptions should be flagged as suspicious before editorial consideration.
- 2026-05-21T11:21:08Z: W21 2026 — The press narrative (compute economics, model-provider deals) and developer activity (small-model efficiency, local inference, skills tooling) diverged significantly this week; the press-vs-reality section is most valuable when this gap is named explicitly with specific repos as counter-evidence.
- 2026-05-21T11:21:08Z: W21 2026 — No stars_gained data was available for trending_repos; the trending list behaves as a large-repo presence register rather than a momentum table; this caveat belongs in the analysis body, not just as a metadata note.
- 2026-05-21T11:21:08Z: W21 2026 — Agent observability (tracing, session replay, behavioral drift detection) is a concrete blind-spot category with near-zero representation; worth tracking as a leading indicator of ecosystem maturation in future weeks.
