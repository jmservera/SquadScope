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
- 2026-06-01T12:16:50Z: W23's dominant noise pattern shifted from star-clustering (W22) to fork-inflation — polymarket bot repos landing with fork counts 10-20x their star count and keyword-stuffed descriptions. Same coordinated intent, new metric vector. Noise classification heuristics should track fork/star ratio as a manipulation signal alongside creation-timestamp clustering.
- 2026-06-01T12:16:50Z: Agent skills crossed a cultural boundary in W23 with the first major Chinese-platform design skills (Xiaohongshu, WeChat) achieving 1k-2k+ stars. Skills economy is now multilingual; editorial framing should treat geographic and linguistic expansion of skills as a trend signal distinct from English-developer workflow skills.
- 2026-06-01T12:16:50Z: GitHub Copilot token-billing backlash (TechCrunch, 2026-05-30) produced a clear same-week developer response in self-hosted AI workspace and alternative-routing repos — strongest press-developer convergence of W23. Monitoring for platform billing/policy changes as a leading indicator of self-hosting repo spikes is a reusable editorial pattern.
- 2026-06-01: Added hindsight validation that backfills Signal/Noise/Gaps repo calls from legacy summaries, writes a markdown scorecard for reskill, and treats frontmatter `predictions` as the forward-looking source of truth for cleaner future scoring.

- 2026-06-05T16:45:08+00:00: When press and developer layers converge on the same attack surface simultaneously — as happened this week with MIT Technology Review's Meta agent hack and three independent agent-safety repos arriving in the same crawl — that convergence is the week's editorial anchor, not just a correlation note. Name the convergence explicitly in the lede trend.
- 2026-06-05T16:45:08+00:00: Fork/star ratio is now a dual-purpose signal: high ratio (niubi_guard at 112fk/178★) signals genuine developer utility; zero forks despite high stars signals coordinated inflation. Make both directions explicit in Signal & Noise rather than treating fork analysis as only a noise-filter.
- 2026-06-05T16:45:08+00:00: The stars_tracked field remains a hand-estimated value (~17M for W23) because pipeline tooling does not inject it. Escalating this as a pipeline improvement: the analyzer should receive pre-computed stats in the prompt rather than estimating them.

## Round 2026-06-01T15:40

### Issue #38: Hindsight Validation
- PR #227 opened
- Implemented `predictions` frontmatter schema: `{repo, direction, confidence}`
- Validator generates scorecards: `.squad/reskill/scorecards/YYYY-WNN.md` (human) and `data/metrics/scorecards/YYYY-WNN-scorecard.json` (machine)
- 548 tests passing
- Ready for merge
