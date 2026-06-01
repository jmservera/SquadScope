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
- 2026-05-25T11:56:08Z: W22 saw the most concentrated coordinated star-farming campaign in the crawl's history — a tight cluster of game-cheat, software-unlock, and AI-branded repos landing at 421–429 stars with zero forks in minutes. This is now a named pattern that should inform noise-filtering heuristics and lower editorial trust for new repos without fork activity.
- 2026-05-25T11:56:08Z: Press data was available this week (2026-W22-press-context.md) and surfaced a useful convergence: TechCrunch's article on inflated AI ARR metrics ran the same week GitHub new_repos was experiencing coordinated star inflation. Cross-referencing press themes against developer noise patterns can surface non-obvious editorial angles.
- 2026-05-25T11:56:08Z: The agent-skills ecosystem transition from hint (W21, chrisbanes/skills, vercel-labs/zero) to confirmed category (W22, multiple independent skill packaging repos alongside 140k+ ⭐ trending anchors) reinforces the wisdom pattern: clustered movement across independent teams is a stronger signal than any single repo launch.
- 2026-05-25T11:56:08Z: stars_tracked and repos_featured remain estimated due to lack of automated summation; these fields should be computed by the pipeline and injected into the prompt rather than hand-calculated each week — a recurring quality gap worth escalating as a skill or pipeline improvement candidate.
- **2026-06-01T10:57:24Z:** Platform billing dissatisfaction (GitHub Copilot token pricing) and self-hosted AI workspace launches are causally linked, not coincidental — when press covers developer billing friction and a high-fork self-hosted repo explodes in the same crawl window, the convergence is the story. Also: the W22 spam clusters (game cheats, polymarket bots, software unlocks) are now fully established as a recurring manipulation pattern identifiable by inverted fork-to-star ratios and keyword-stuffed descriptions; future weeks should apply this as a named filter heuristic rather than re-detecting from scratch.
