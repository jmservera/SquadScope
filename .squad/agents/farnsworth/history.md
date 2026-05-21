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
- **2026-05-21T08:39:29Z:** The 2026-W21 crawl contained an exceptional volume of coordinated noise — game cheats, ROM emulator fronts, Windows activators, and trading bot spam clusters with replicated descriptions and inflated fork counts. The `hacktoberfest` topic appearing 24 times in May is a reliable marker of topic-stuffing; treat it as a noise signal in any non-October crawl.
- **2026-05-21T08:39:29Z:** A prior summary path of `None` means every momentum call must be explicitly caveated; no trend should be described as "accelerating" without `stars_gained` data or a baseline comparison. The trending set this week was entirely missing `stars_gained`, making it a popularity list, not a momentum list — said so explicitly in Signal & Noise.
- **2026-05-21T08:39:29Z:** The agent skill packaging pattern (repos explicitly formatted as distributable skill files for Claude Code / Codex / Opencode) reached threshold this week — multiple independent instances across diverse domains (Android testing, CUDA, legal, distributed systems, technical writing). This format may warrant a dedicated tracking tag in future crawls and is a candidate for a new skill in `.squad/skills/` covering how to identify and evaluate skill-packaging ecosystems.
