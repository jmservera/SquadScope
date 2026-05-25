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
- 2026-05-25T09:51:17Z: Sybil-style repo farming (coordinated polymarket bot clusters with ~2000+ identical fork counts) is qualitatively different noise than individual exploit/crack repos and deserves a named pattern — call it "coordinated engagement manufacturing." Filtering heuristic: repos created within the same hour, with identical fork counts and spam-repeated descriptions, are sybil artifacts regardless of star count.
- 2026-05-25T09:51:17Z: "Fake brand" repos imitating AI product names (Claude Design Studio, Mythos Claude, Gemini app clones) are a new noise category: brand parasitism for SEO/discovery manipulation. They show up as real stars but contain no code and should be treated as noise unless a legitimate organization is confirmed.
- 2026-05-25T09:51:17Z: The skills-as-distribution-format pattern is now a confirmed category, not a curiosity. W21 had one hint (chrisbanes/skills); W22 had five independent skills repos across visualization, trading knowledge, context engineering, and prompt methodology. Worth tracking as its own trend dimension going forward.
- 2026-05-25T09:51:17Z: When stars_gained is missing for a second consecutive week, the trending section should be explicitly described as a large-repository census rather than a momentum leaderboard, and the caveat should appear once in Trends not dominate Signal & Noise. Avoid repeating the caveat more than twice per report.
