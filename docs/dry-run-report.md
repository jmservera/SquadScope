# Dry Run Report — Issue #7

**Executed:** 2026-05-18T10:59:10.800+02:00  
**Scope:** Manual crawl → analyze → publish dry run using `data/raw/2026-W21.json`

## Inputs Checked

- `data/raw/2026-W21.json` exists.
- The crawler payload passes `scripts.crawl.validate_payload`.
- Top-level structure is present: `week`, `crawled_at`, `new_repos`, `trending_repos`, `signals`, `metadata`.
- Source counts: 209 new repositories, 215 trending repositories, 424 total entries.

## What Worked

1. **Manual analysis artifact created** at `data/analyzed/2026-W21-summary.md`.
2. **Weekly Hugo content updated** at `content/weekly/2026/W21.md` and linked back to both the raw and analyzed artifacts.
3. **Hugo build succeeded** when run with a compatible local binary (`v0.161.1`).
4. **Homepage validation passed**: the latest-week slot resolves to Week 21, 2026.
5. **Archive validation passed**: `/archive/` lists the weekly entry.
6. **RSS validation passed**: `public/index.xml` includes the Week 21 entry.
7. **Taxonomy validation passed**: generated tags and categories pages include the weekly entry.

## What Did Not Work Cleanly

1. **System Hugo is too old.** The machine default was `hugo v0.123.7`, but the PaperMod theme requires `v0.146.0+`, so the first build failed before validation could proceed.
2. **Trending is not truly trending yet.** Every `trending_repos` item for this week has `stars_gained = null`, which means the output is effectively “popular repos active this week” until a prior snapshot exists.
3. **Crawler noise is still high.** The new-repo dataset includes a noticeable amount of exploit, bypass, cheat, and game-mod content that would weaken fully automated publication.
4. **Automation gap remains.** The weekly page was assembled manually because the Analyze → Generate handoff is not implemented yet.

## Observations From the Data

- AI/agentic tooling is the dominant theme in both new and trending datasets.
- Security appears often, but much of that signal is exploit-oriented rather than defensive tooling.
- The strongest credible new-repo cluster is around agent workflows, reusable skills, and lightweight coding infrastructure.
- The strongest trending cluster is around established AI and developer-platform repositories (`n8n`, `ollama`, `transformers`, `dify`, `firecrawl`, `claude-code`).

## Missing Pieces Before Full Automation

- Seed and maintain historical snapshots so trending can calculate real weekly star deltas.
- Tighten crawler filtering or add a post-crawl quality gate for off-mission repositories.
- Implement the generator step that converts analyzed markdown into weekly/monthly/yearly Hugo content.
- Pin Hugo version in local/CI verification so validation does not depend on a too-old system package.
- Align the long-term analyzed markdown contract with the final weekly page schema and quality gate expectations.

## Dry Run Verdict

**Partial pass.** The publish side of the pipeline is structurally viable once given a valid analyzed markdown file, and the site surfaces the weekly entry in the expected places. Full end-to-end automation is still blocked by missing trend baselines, noisy crawl output, and the absent Analyze → Generate automation step.
