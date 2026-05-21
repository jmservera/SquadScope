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
- 2026-05-21T12:05:17Z: 2026-W21 analysis confirmed the agent-skills-as-packages pattern as a durable ecosystem shift; skill repos span legal, GPU, testing, and writing domains with no single dominant curator, suggesting a registry gap will emerge before long.
- 2026-05-21T12:05:17Z: Press-correlation data matched 87 repos but all via org-name or topic-name fuzzy matching — the signal-to-noise on the pre-computed correlations file is low this week; future iterations should weight confidence<0.5 matches as editorial noise rather than correlation evidence.
- 2026-05-21T12:05:17Z: Exploit-churn and spam-bot repos (gaming bypasses, piracy launchers, prediction-market bots with keyword-stuffed descriptions) constituted at least a third of new repo volume; the stars_gained absence means these can't be separated from genuine momentum without a snapshot diff — this is the most pressing pipeline quality gap.
- 2026-05-21T12:05:17Z: zerolang anchors editorial narrative as the week's hottest claim, but the top_repo choice for hype-flagging purposes should note whether substance emerged in subsequent weeks — recommend revisiting in next baseline comparison.
