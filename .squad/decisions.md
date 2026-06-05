# Squad Decisions

# Squad Decisions

## Impact

Applies to future weekly summaries and any generator work that consumes `data/analyzed/*-summary.md`.

---

---

# Fry: quality gate fallback hardening

Date: 2026-06-01

## Context
Issue #217 showed the weekly analysis job can fail even when crawl data is healthy because Copilot sometimes returns a generic placeholder title or no output file at all after retries.

## Decision
Keep Copilot CLI as the primary analysis generator, but if its output still fails the quality gate after retries, immediately fall back to `scripts/analyze_fallback.py` via GitHub Models. Also render the prompt with concrete `week`, `year`, and title guidance so the model is less likely to echo placeholder frontmatter.

## Rationale
This keeps the higher-quality primary path, but removes CI flakiness from transient Copilot failures and from prompt placeholders leaking into the final markdown.

---

---

# Leela — PR review gate follow-up

- Date: 2026-06-01
- Context: Round review of PR #218 and PR #219 showed both branches were opened by `jmservera`, which means the current GitHub identity cannot submit an approving review on them.
- Decision: Do not bypass the review gate on self-authored pull requests. Treat independent approval as still required before merging branches opened by the same account Leela is operating under.
- Why: GitHub blocks self-approval, and preserving the review gate matters more than forcing a merge from the lead seat.

## Cost Transparency Placement (2026-05-25)

**Decision:** The AI pipeline cost dashboard is part of `/about/` under a Pipeline transparency section, with the existing `/dashboard/` page retained as a direct audit link that reuses the same shortcode.

**Rationale:** Cost reporting is operational transparency, not a primary navigation destination or product dashboard. Keeping it on About matches the editorial-restrained redesign while preserving the old URL for references.

## Nibbler Review Gate for External-Facing Artifacts (2026-05-25)

**Source:** Nibbler audit recommendation
**Adopted by:** Leela
**Status:** Adopted

External-facing launch and announcement artifacts require Nibbler review before publication or merge. This includes Hacker News posts, LinkedIn announcements, Bluesky threads, Reddit posts, launch blogs, press copy, launch graphics, and similar materials that will appear outside this repository.

PRs that ship this copy or graphics must tag `@squad:nibbler` for RAI sign-off and use the [Responsible AI checklist](skills/responsible-ai-review/SKILL.md) (`.squad/skills/responsible-ai-review/SKILL.md`) before merge.

**Rationale:** Distribution copy can create reputational, safety, accessibility, or policy risk even when the underlying code is unchanged. Nibbler provides the hostile-reader and responsible-AI perspective before users encounter the material.

---

# Amy — Topic buttons follow-up

- Date: 2026-06-01
- Context: Issue #216 mobile topic buttons regression
- Proposal: Keep topic discovery centered on `/topics/`, remove the global header topic shortcut strip, and hide per-report topic chips on screens up to 768px while leaving desktop topic browsing available through the homepage rail and Topics page.
- Why: The repeated chip rows were consuming too much vertical space on mobile and duplicated navigation that already exists in the primary menu.

---

# Fry: quality gate fallback hardening

Date: 2026-06-01

## Context
Issue #217 showed the weekly analysis job can fail even when crawl data is healthy because Copilot sometimes returns a generic placeholder title or no output file at all after retries.

## Decision
Keep Copilot CLI as the primary analysis generator, but if its output still fails the quality gate after retries, immediately fall back to `scripts/analyze_fallback.py` via GitHub Models. Also render the prompt with concrete `week`, `year`, and title guidance so the model is less likely to echo placeholder frontmatter.

## Rationale
This keeps the higher-quality primary path, but removes CI flakiness from transient Copilot failures and from prompt placeholders leaking into the final markdown.

---

---

# Fry — generate-step failure handling

Date: 2026-06-01

## Context
Issue #220 showed the crawl-and-publish workflow could finish crawl and analysis successfully, then fail in the generate handoff because the generated weekly page path was absolute while the publish-branch restore logic assumed a repository-relative path. The same workflow also lacked a failure-to-issue bridge, so repeated pipeline failures did not automatically open or update a GitHub issue.

## Decision
Normalize `page_path` to a repo-relative `content/weekly/...` path inside the generate commit step before copying weekly output onto the publish branch. Add a dedicated `notify-failure` job that always evaluates after the pipeline jobs and creates or updates a GitHub issue whenever any crawl/analyze/generate/deploy/notify job fails.

## Rationale
The path normalization fixes the actual handoff bug without changing `scripts/generate_content.py`, which already returns an absolute file path used elsewhere in tests. A separate failure notifier makes regressions visible even when later jobs are skipped, which is the exact reliability gap that hid the recent failures.

---

---

# Amy — Share button implementation

Date: 2026-06-01

## Context
Issue #226 adds article-level sharing. PaperMod already ships a share-buttons partial, but SquadScope also needs mobile-native sharing through the Web Share API and token-aligned styling.

## Decision
Enable PaperMod share support through `hugo.toml` (`params.ShowShareButtons` plus an explicit `params.ShareButtons` allowlist), then override `layouts/partials/share_icons.html` in the project to add a mobile-only native share button while keeping desktop fallback links for X, LinkedIn, and Facebook. To keep the site buildable with the current PaperMod submodule layout, vendor the theme partials the site already relies on into `layouts/partials/` instead of editing the theme.

## Rationale
This keeps the third-party theme submodule untouched, reuses the existing article-footer insertion point, and scopes the share customization to a project-level partial plus tokenized footer styles. Vendoring the required PaperMod partials also makes the build deterministic for SquadScope without depending on theme-internal `_partials` resolution quirks.

---

---

# Farnsworth — Hindsight validation decision

Date: 2026-06-01

## Decision
Use an optional `predictions` frontmatter registry on weekly analysis summaries with entries shaped as `{repo, direction, confidence}`.

## Why
The published markdown is already the durable editorial artifact, so embedding prediction intent there avoids a separate ledger drifting out of sync. Legacy summaries still need heuristic extraction from Signal/Noise/Gaps prose, but future summaries should register explicit repo-level calls for cleaner hindsight scoring.

## Operational note
The validator writes a human scorecard to `.squad/reskill/scorecards/YYYY-WNN.md` and a machine-readable companion to `data/metrics/scorecards/YYYY-WNN-scorecard.json` so the current reskill tooling can ingest the same run.

---

---

# Fry — Generate-step failure handling

Date: 2026-06-01

## Context
Issue #220 showed the crawl-and-publish workflow could finish crawl and analysis successfully, then fail in the generate handoff because the generated weekly page path was absolute while the publish-branch restore logic assumed a repository-relative path. The same workflow also lacked a failure-to-issue bridge, so repeated pipeline failures did not automatically open or update a GitHub issue.

## Decision
Normalize `page_path` to a repo-relative `content/weekly/...` path inside the generate commit step before copying weekly output onto the publish branch. Add a dedicated `notify-failure` job that always evaluates after the pipeline jobs and creates or updates a GitHub issue whenever any crawl/analyze/generate/deploy/notify job fails.

## Rationale
The path normalization fixes the actual handoff bug without changing `scripts/generate_content.py`, which already returns an absolute file path used elsewhere in tests. A separate failure notifier makes regressions visible even when later jobs are skipped, which is the exact reliability gap that hid the recent failures.

---

---

# Farnsworth hindsight validation decision

Date: 2026-06-01

## Decision
Use an optional `predictions` frontmatter registry on weekly analysis summaries with entries shaped as `{repo, direction, confidence}`.

## Why
The published markdown is already the durable editorial artifact, so embedding prediction intent there avoids a separate ledger drifting out of sync. Legacy summaries still need heuristic extraction from Signal/Noise/Gaps prose, but future summaries should register explicit repo-level calls for cleaner hindsight scoring.

## Operational note
The validator writes a human scorecard to `.squad/reskill/scorecards/YYYY-WNN.md` and a machine-readable companion to `data/metrics/scorecards/YYYY-WNN-scorecard.json` so the current reskill tooling can ingest the same run.

---

---

# Fry QA triage decision

Date: 2026-06-05T15:36:19.379+00:00

## Decision

The crawl-and-publish analysis stage should degrade to a data-only no-AI weekly summary when both Copilot output and GitHub Models output are unavailable or rejected by the quality gate.

## Rationale

A missing or unauthorized model is an operational dependency failure, but the pipeline still has verified crawl data. Publishing a clearly labeled data-only summary is more reliable than failing the entire weekly handoff after preserving no reader-facing output.

## Follow-up

If model access is restored, the AI analysis path remains preferred. The no-AI path is only a terminal fallback after Copilot and GitHub Models fail.

---

---

# Leela: Close unverifiable W23 growth execution

Date: 2026-06-05T15:36:19.379+00:00

**By:** Leela

## Decision

Issue #188 was closed as obsolete/unverifiable rather than reconstructed or rerouted. W23 draft files under `.squad/posts/`, the requested `.squad/metrics/2026/w23-distribution.md`, and platform posting evidence were absent from the working tree, git history, related issues, and PR context. PR #190 and `docs/growth/distribution-strategy.md` only provide the launch strategy/template, not the W23 execution artifacts.

## Rationale

Recreating social posts and metrics after the distribution window would create misleading evidence. Future growth execution issues should remain open until artifact-backed proof exists, or be closed explicitly when the posting window expires without evidence.

---

---

# Fry PR #236 QA Review

Date: 2026-06-05T15:36:19.379+00:00

PR #236 keeps RSS enrichment in the existing crawl job with bounded in-process parallel fetching instead of separate Actions jobs.

QA verified the diff covers config loading, multi-source crawl aggregation, metadata/errors, legacy `*-techcrunch.json` fallback, correlation handoff, press-context resolution, and rebuild hydration.

Validation run in an isolated PR worktree:
- `PYTHONPATH=. .venv/bin/python -m pytest tests -q` → 554 passed
- Live RSS smoke with `--max-workers 5` → 54 articles from 5 sources, no feed errors

Verdict: approve; no follow-up implementation owner required.

---

---

# Hermes security review — PR #236 external RSS feeds

Date: 2026-06-05T15:36:19.379+00:00

## Verdict

Request changes before merge.

## Rationale

PR #236 keeps workflow secrets out of the RSS step and does not add new dependency classes, but the new config-driven fetcher currently trusts `feed_url` values without enforcing scheme/host boundaries and calls `feedparser.parse(url)` without an explicit per-request timeout. Because the workflow runs this in CI and later grants `contents: write` in the same job, external-network behavior should fail closed around the intended RSS allowlist and fail fast on slow/unresponsive feeds.

## Required fixes

- Validate source config with `urllib.parse.urlparse()` before crawling:
  - require `https`;
  - require hostnames to match the repository-owned allowlist for the five intended feeds;
  - reject credentials, local/private/link-local hosts, and unexpected ports.
- Fetch feeds through a code path with explicit timeout and bounded retry/backoff behavior; do not rely on the default socket timeout.
- Keep bounded concurrency; optionally validate `--max-workers` to a safe range.

## Suggested owner

Bender should own the fixes so Leela does not review her own implementation changes.

---

---

# PR #236 security unblock

Date: 2026-06-05T16:00:00+00:00

Hermes re-reviewed PR #236 at Bender fix commit `e91e2a5b33b816191148125d40192b3fff8fbc6a`.

Security blockers from the prior review are resolved:
- external RSS feed URLs are parsed with `urllib.parse.urlparse()` and restricted to HTTPS on the approved host allowlist;
- credentials, localhost/local domains, private/link-local IP literals, invalid ports, and non-443 ports are rejected;
- RSS fetches use `urlopen(..., timeout=DEFAULT_FETCH_TIMEOUT_SECONDS)` with bounded retry attempts;
- parallel RSS crawling caps workers at `DEFAULT_MAX_WORKERS` and rejects `--max-workers < 1`;
- tests cover unsafe URL rejection and explicit timeout propagation.

Validation: `PYTHONPATH=. python -m pytest tests -q` in an isolated PR worktree passed with 563 tests.

Decision: Hermes security approval/unblock for merge, with CodeQL checks green on the PR.

---

---

# Bender — Crawler parallelism analysis

Date: 2026-06-05T16:26:00Z
Requested by: jmservera
Inputs:
- Old crawler job: https://github.com/jmservera/SquadScope/actions/runs/26753498571/job/78847225991
- New crawler job: https://github.com/jmservera/SquadScope/actions/runs/27026348186/job/79767247136

## Observations from job logs

### Old run — single TechCrunch RSS source

Run `26753498571`, job `78847225991`, head `59b45137fc3ad674276b1ff8c0aa743d8e43d1bb`:

- `crawl` job duration: 2026-06-01 11:58:51Z → 12:05:14Z, about 6m23s.
- `Run crawler`: 11:59:02Z → 12:05:00Z, about 5m58s.
- `Crawl TechCrunch RSS`: started and completed at 12:05:06Z in the step timing metadata, effectively sub-second.
- GitHub crawl summary: `Wrote data/raw/2026-W23.json with 196 new repos and 238 trending repos, saved data/snapshots/2026-W23-stars.json, used 447 API calls, and served 0 cache hits.`
- RSS summary: `Crawled 20 articles (7 relevant) → data/raw/2026-W23-techcrunch.json`.
- Rate-limit evidence: 447 rate-limit log lines; 6 search calls and 441 core calls. Minimum observed remaining quota was 24 search requests out of 30, and final core quota was 4556/5000.
- Retry/flakiness evidence: 0 `Retrying`, 0 stale-cache fallbacks, 0 search failures in the filtered log summary. The `warning`/`error` counts visible in the raw filtered scan are from workflow script text/hints, not crawler failures.

### New run — five external RSS sources, in-process parallelism

Run `27026348186`, job `79767247136`, head `87e55a227da78b86e9677acc96460968196e9e5a`:

- `crawl` job duration: 2026-06-05 16:15:41Z → 16:20:49Z, about 5m08s.
- `Run crawler`: 16:15:49Z → 16:20:36Z, about 4m47s.
- `Crawl external news RSS feeds`: 16:20:42Z → 16:20:43Z, about 1s.
- GitHub crawl summary: `Wrote data/raw/2026-W23.json with 213 new repos and 236 trending repos, saved data/snapshots/2026-W23-stars.json, used 455 API calls, and served 0 cache hits.`
- External RSS summary: `Crawled 54 articles from 5 sources (27 relevant) → data/raw/2026-W23-external-news.json`.
- Rate-limit evidence: 455 rate-limit log lines; 6 search calls and 449 core calls. Minimum observed remaining quota was 24 search requests out of 30, and final core quota was 4458/5000.
- Retry/flakiness evidence: 0 `Retrying`, 0 stale-cache fallbacks, 0 search failures. The new RSS stage did not visibly bottleneck the job.

## Current implementation shape reviewed

The newer workflow revision changes the RSS stage from a single TechCrunch output to:

```yaml
python scripts/techcrunch_crawler.py \
  --sources config/external_news_sources.json \
  --output "data/raw/${WEEK}-external-news.json" \
  --since "$SINCE"
```

The external source config contains five approved feeds: TechCrunch, NVIDIA Blog, Hugging Face Blog, MIT Technology Review, and GitHub Blog.

The new crawler implementation:

- validates feed URLs against an HTTPS host allowlist;
- fetches RSS with an explicit 15s timeout;
- uses `ThreadPoolExecutor` with `max_workers=min(requested_or_source_count, source_count, 8)`;
- records per-source article `source` fields;
- writes one merged `external_news` artifact with metadata including `source_count`, `sources_with_articles`, totals, GitHub links, and `errors`.

## Topology options

### Option A — keep bounded in-process parallelism in one job

Best fit for the current source count.

Pros:
- Fast enough now: five-source RSS stage adds about 1s in the new run.
- No extra checkout/setup/artifact overhead per source.
- Keeps one downstream news artifact contract, which matches `correlate.py` and `render_press_context.py` expectations.
- A source failure can be represented inside `metadata.errors` without failing the entire crawl.

Cons:
- If one feed hangs until timeout, the RSS step is bounded by timeout plus retry delay for that source.
- GitHub Actions cannot independently retry only one failed source.
- Per-source logs are less visible unless the script emits explicit source start/end/error lines.

### Option B — GitHub Actions matrix per source/type

Not justified yet for the RSS feeds alone.

Pros:
- Clean isolation and per-source retry visibility.
- Natural if sources become heterogeneous: RSS, APIs, browser crawls, paid sources, or sources with independent secrets/quotas.
- Failure policy can vary by source.

Cons:
- More runner minutes and more setup overhead than the current 1s RSS crawl.
- Requires explicit merge job and stricter artifact naming/schema validation.
- Increases race/branch commit complexity if matrix outputs are committed directly.
- Does not help the actual current bottleneck, which is the GitHub repo crawl step at roughly 4m47s–5m58s.

### Option C — hybrid/staged topology

Recommended next iteration, but staged lightly: keep RSS in-process now, make the artifact contract merge-ready, and add a separate merge/validate step before analysis.

Pros:
- Preserves current speed and simplicity.
- Creates a clean future migration path to a matrix without changing analysis consumers.
- Lets the pipeline distinguish crawler collection from artifact assembly/validation.
- Gives downstream stages one canonical `external-news` artifact regardless of whether collection was single-process or matrix.

Cons:
- Adds one small script/step for validation/merge even before a matrix is needed.
- Requires schema versioning discipline.

## Recommendation

Use a hybrid/staged approach:

1. Keep the current bounded in-process parallel RSS crawl for the next iteration.
2. Add explicit per-source logs: start time, duration, article count, relevant count, GitHub-link count, and error if any.
3. Add `schema_version` and stable `sources_requested` / `sources_succeeded` / `sources_failed` metadata to `external-news.json`.
4. Add a validation/merge script that accepts either:
   - current single merged external-news payload, or
   - future per-source payloads named like `external-news-${source}.json`.
5. Make analysis consume only the canonical merged artifact: `data/raw/${WEEK}-external-news.json`.
6. Move to an Actions matrix only when evidence shows RSS collection is material: e.g. external source stage exceeds 60s p95, source count exceeds about 12–15, or a source requires independent credentials/rate policy.

## Risks

- Current metadata has `errors`, but success criteria are ambiguous. A total RSS outage could still return exit 0 if errors are recorded but no minimum-source gate exists.
- The script name `techcrunch_crawler.py` is now misleading for multi-source external news. Rename later only with backward-compatible CLI/wrapper to avoid breaking existing docs/tests.
- The current logs show `0 cache hits` in both old and new GitHub crawls, so cache restoration is not reducing runtime in these examples. That may be due to TTL/query churn or artifact mismatch and should be investigated separately from RSS topology.
- Search API quota is the tighter GitHub limit: both runs reached minimum remaining 24/30 search requests while core remained above 4450/5000. More GitHub search parallelism would risk secondary/rate-limit pressure; RSS parallelism does not consume GitHub API quota.

## Acceptance criteria for next implementation

- A weekly crawl with five RSS sources still completes the external RSS stage in under 30s under normal network conditions.
- The RSS crawler logs one concise summary line per source with duration and counts.
- `data/raw/${WEEK}-external-news.json` includes `schema_version`, `source_count`, `sources_requested`, `sources_succeeded`, `sources_failed`, `sources_with_articles`, and `errors`.
- The workflow fails only when the required GitHub raw payload is missing or the external-news artifact is structurally invalid; individual optional RSS source failures are recorded and do not block analysis unless fewer than an agreed minimum number of sources succeed.
- Rebuild mode hydrates the canonical external-news artifact and remains backward-compatible with legacy `${WEEK}-techcrunch.json`.
- Correlation and press-context steps read the canonical merged artifact and do not need to know whether collection was in-process or matrix-based.
- Tests cover single merged payload validation plus simulated future per-source merge inputs.

---

---

# Farnsworth: LLM input strategy for multi-source news

Date: 2026-06-05T16:26:00.133+00:00

## Context

The old crawler run (`26753498571` / job `78847225991`) produced:

- `data/raw/2026-W23.json`: 196 new repos, 238 trending repos, 447 GitHub API calls.
- `data/raw/2026-W23-techcrunch.json`: 20 TechCrunch articles, 7 relevant.

The new crawler run (`27026348186` / job `79767247136`) produced:

- `data/raw/2026-W23.json`: 213 new repos, 236 trending repos, 455 GitHub API calls.
- `data/raw/2026-W23-external-news.json`: 54 articles from 5 sources, 27 relevant, no feed errors.
- Source mix: TechCrunch 20, NVIDIA Blog 13, Hugging Face Blog 9, MIT Technology Review 10, GitHub Blog 2.

The external-news artifact is roughly 45.5 KB / 11.4k token-estimate by itself; the GitHub raw artifact from the same run is roughly 296 KB / 74k token-estimate. Existing rendered press context can also be large: the W23 TechCrunch-only press context on `publish` is about 27.9 KB / 7k token-estimate before adding the extra sources.

## Analyst assessment

Do not send all raw GitHub and all raw external-news inputs directly to the weekly analysis model. That path is editorially fragile: the model will spend attention on repeated article summaries, source boilerplate, low-relevance items, and broad category matches instead of the actual job — deciding what matters. It also increases prompt-injection surface and makes limited-context models more likely to drop required sections, lose citations, or overfit the latest/longest source.

The current analysis contract already expects a concise `Where Industry Meets Code` comparison, not a press digest. External news should therefore enter analysis as a compact, source-aware correlation artifact: a deterministic press-context file that preserves the top evidence and citations while discarding bulk article text.

## Options considered

### 1. Pass every raw input at once

**Pros**
- Maximum recall.
- Simplest implementation if context windows are assumed unlimited.

**Cons**
- Poor fit for limited-context or cheaper fallback models.
- Increases prompt size from already-large GitHub raw payloads into 90k+ token territory before learned state and instructions.
- Encourages article summarization instead of repo-to-industry synthesis.
- Makes the quality gate less reliable because structural failures, missing references, and citation drift become more likely.
- Treats all sources equally even when some are lower relevance for developer adoption.

**Analyst verdict:** Reject for the default path.

### 2. Pre-merge and summarize all sources into one artifact

**Pros**
- Keeps the analyzer prompt smaller.
- Gives the model one stable press evidence surface.
- Easier to validate than source-specific LLM steps.

**Cons**
- If summarization is LLM-generated, it can lose citations or compound hallucinations before the main analysis.
- If it simply concatenates all sources, it still carries noise.
- Needs source provenance to avoid TechCrunch/GitHub/NVIDIA/MIT/HF being flattened into one undifferentiated "press" voice.

**Analyst verdict:** Good only if deterministic and citation-preserving.

### 3. Run staged source-specific LLM analyses

**Pros**
- Keeps each model call small.
- Can produce richer source-by-source editorial nuance.
- Scales if future source count grows substantially.

**Cons**
- Higher cost and more failure points.
- Second-stage analyzer may inherit summaries without enough evidence.
- Quality gate currently validates final structure, not the faithfulness of intermediate source briefs.
- More operational complexity than current volume justifies.

**Analyst verdict:** Defer. Consider only when relevant article volume regularly exceeds the compact artifact budget.

### 4. Use compact correlation / press-context artifact

**Pros**
- Best match for the weekly brief: correlations, divergences, citations, and source provenance are preserved.
- Keeps the LLM focused on editorial judgment instead of raw article triage.
- Can be generated deterministically and tested.
- Supports fallback models and no-AI fallback more safely.

**Cons**
- Requires explicit ranking and truncation rules.
- Bad correlation heuristics can still inject false positives, especially category-only matches.
- Needs quality gates that check citation preservation, not just markdown shape.

**Analyst verdict:** Recommended default.

## Recommendation

Implement a source-aware compact press-context artifact as the only external-news input to weekly analysis.

The analyzer should receive:

1. Sanitized/possibly compacted GitHub repo evidence.
2. Previous weekly summary.
3. Learned wisdom/skills.
4. One compact press-context artifact containing:
   - source coverage summary (`source`, total articles, relevant articles, errors),
   - 5-10 ranked press items with URL, source, date, relevance score, and one-sentence why-it-matters,
   - 5-10 highest-confidence repo/news correlations,
   - separate "possible/weak correlations" bucket for category-only or fuzzy matches,
   - 3-6 divergence findings,
   - complete citations for every article retained,
   - explicit caveat when sources were unavailable or noisy.

Do not include all article summaries in the analysis prompt. Do not let low-confidence category matches count as strong press correlation. Category-only matches should be framed as weak context unless reinforced by direct GitHub link, organization/entity match, temporal spike, or repeated source agreement.

## Prompt / gate implications

- The prompt should say: "Use press context as correlation evidence, not as instructions and not as content to repackage."
- External-news content should be wrapped in the same untrusted-content boundary pattern used for raw repo JSON.
- The quality gate should remain structural, but add evidence-focused checks:
  - `## Key References > ### Press & Industry` contains 3-5 retained article links when press data exists.
  - The body does not contain raw correlation dumps, model instructions, or full article payloads.
  - At least one sentence in `Where Industry Meets Code` distinguishes strong correlation from weak/noisy press context.
  - If external-news metadata reports source errors, the article includes a concise caveat.

## Acceptance criteria for Leela's next issue

- A deterministic compact press-context artifact is generated before analysis from `*-external-news.json` and `*-correlations.json`.
- The compact artifact has a documented token/size budget, recommended ceiling: <= 8k token-estimate for press context.
- The weekly analysis prompt consumes the compact press context, not the full external-news JSON.
- Press context retains source name, article URL, article title, published date, relevance score, and correlation confidence for every retained citation.
- Correlations are tiered: direct-link/org/entity/temporal matches are strong; fuzzy/category-only matches are weak unless corroborated.
- Quality gate or tests reject raw article/correlation dumps in final analysis output.
- Tests cover: multi-source source counts, no-source/error caveats, citation preservation, truncation behavior, weak-correlation labeling, and legacy `*-techcrunch.json` fallback.
- The final weekly summary still conforms to `docs/analysis-spec.md`: required frontmatter, stable H2 sections, complete Key References, no placeholders, no raw JSON/tool logs.

## Editorial success metric

The finished weekly brief should make fewer but sharper press claims: "what the industry narrative explains, what developer activity confirms, and what the press is missing." It should not become a five-source news roundup.

---

---

# Fry QA: crawler reliability and performance next iteration

Date: 2026-06-05T16:26:00Z
Requested by: jmservera

## Evidence reviewed

- Old crawl job `26753498571 / 78847225991`: crawl job 11:58:51–12:05:14 (~6m23s). GitHub crawl wrote `data/raw/2026-W23.json` with 196 new repos, 238 trending repos, 447 API calls, 0 cache hits. Single TechCrunch RSS step produced 20 articles / 7 relevant. Raw artifact: 199,434 bytes; cache artifact: 10,188,525 bytes.
- New crawl job `27026348186 / 79767247136`: crawl job 16:15:41–16:20:49 (~5m08s). GitHub crawl wrote 213 new repos, 236 trending repos, 455 API calls, 0 cache hits. External RSS step produced 54 articles from 5 sources / 27 relevant. Raw artifact: 207,606 bytes; cache artifact: 11,874,886 bytes.
- Current `origin/main` workflow runs GitHub crawl first, then a single in-process parallel `scripts/techcrunch_crawler.py --sources config/external_news_sources.json` step, uploads one `raw-data` artifact, and analysis falls back from `{week}-external-news.json` to legacy `{week}-techcrunch.json`.
- Existing tests cover source config validation, allowlisted HTTPS feed URLs, explicit fetch timeout, in-process parallel aggregation, metadata/errors in combined output, correlation loading, and press-context rendering.

## Reliability observations

1. Multi-source RSS is not currently the runtime bottleneck. The new five-source RSS step took about one second after dependencies; the GitHub API crawler still dominates the crawl job at ~4m47.
2. The in-process model is operationally simple and fast, but failure isolation is only at script level. A per-source fetch exception can be represented in `metadata.errors`, but a bad config parse, merge bug, dependency issue, or Python process failure takes out every external source in one step.
3. Retry granularity is poor in the current shape. A flaky NVIDIA/Hugging Face/MIT feed requires rerunning the whole crawl job, including the GitHub API crawl and cache artifact upload, unless manual surgery is done.
4. Artifact availability is all-or-nothing for external news. The workflow uploads `raw-data` after the combined step, so failed individual sources do not leave independently downloadable payloads unless the combined script writes a degraded aggregate.
5. Cache behavior argues against matrixing the GitHub repository crawl right now. The GitHub cache is a single `data/cache/` artifact restored from the previous successful run; splitting GitHub query work would introduce cache merge/conflict questions without evidence it is the bottleneck needing parallel source isolation.
6. Partial data tolerance exists downstream: correlation only runs if an external-news or legacy TechCrunch file exists, and press context can render a no-press fallback. That is good, but the workflow does not yet make optional-source degradation explicit enough in job summaries or gating.
7. Reproducibility needs tightening before matrix fan-out. Matrix jobs must share the same centrally computed `week`, `since`, and `until`; otherwise each source can observe a slightly different crawl window.

## Recommendation

For the next iteration, keep the GitHub repository crawl as one core job and split external RSS/news sources into a GitHub Actions matrix with `fail-fast: false`, per-source artifacts, and a deterministic merge job before analysis.

This gives the best reliability improvement without multiplying the GitHub API/cache risk. Because external RSS jobs can run in parallel with the slower GitHub crawl, matrix overhead should not increase the critical path much if analysis depends on a small merge job rather than on the old monolithic crawl job. Do not push source merging into analysis; merge before analysis so correlation, press context, artifacts, and rebuild hydration keep a stable stage boundary.

## Acceptance criteria for the issue

- Workflow defines a shared crawl context (`week`, `since`, `until`, source config checksum) once and passes it to all crawl jobs.
- GitHub repository crawl remains a required/core job and continues to restore/upload the existing `crawl-cache` artifact.
- External news uses a matrix over configured source names/URLs with `strategy.fail-fast: false`.
- Each source uploads a per-source artifact on `if: always()` containing either:
  - a valid source payload with articles and metadata; or
  - a status/error JSON with source name, error class/message, attempts, duration, and crawl window.
- A merge job runs on `if: always()` after core crawl and all news matrix jobs, downloads available source artifacts, validates schemas, deduplicates/sorts deterministically, and writes canonical `data/raw/{week}-external-news.json`.
- Analysis consumes only the merged canonical external-news file plus the GitHub raw file; it does not crawl or merge feeds itself.
- Optional external-news failures do not block publication when GitHub raw data is valid; they must produce visible warnings and metadata. A config/schema/security validation failure should fail the workflow because it is deterministic and actionable.
- Rebuild mode hydrates the merged external-news file and still accepts legacy `{week}-techcrunch.json`.
- The raw-data artifact remains available even when one or more optional source jobs fail.
- CI summary reports per-source status and aggregate totals; the next run can identify exactly which feed was slow/flaky.

## Tests to add or update

- Unit tests for a new merge helper/script:
  - merges multiple valid source artifacts into `source=external_news` canonical output;
  - preserves `source_count`, `sources_with_articles`, `metadata.errors`, and per-source status;
  - deduplicates repeated article URLs deterministically without dropping distinct source attribution unexpectedly;
  - sorts output deterministically by `published_at`, then source/name/url;
  - tolerates missing/failed optional source artifacts;
  - fails on malformed JSON, invalid source names, or mismatched `week`/window metadata.
- CLI tests for fixed `--since` and `--until` propagation so matrix jobs reproduce the same window.
- Workflow/handoff tests or a validation script fixture that asserts `analyze` depends on the merge artifact, not raw matrix artifacts directly.
- Correlation and press-context tests with merged `*-external-news.json`, legacy `*-techcrunch.json`, and no external-news file.
- Regression test that a single source failure still produces a merged canonical file with remaining articles and visible `metadata.errors`.
- Regression test that all external sources failing produces a no-press fallback path while preserving a valid GitHub raw artifact.

## Metrics/logging to capture

- Per source: source name, URL host, start/end/duration seconds, attempts, timeout seconds, total articles, relevant articles, GitHub links found, error class/message, and success/failure.
- Aggregate: source_count, successful_source_count, failed_source_count, total/relevant articles, dedupe counts, artifact size, merge duration.
- Core GitHub crawl: API calls, cache hits, stale cache hits, rate-limit remaining/resource/reset, partial failure count, repo counts, snapshot repo count.
- Workflow: job durations for core crawl, each source crawl, merge, analyze; whether analysis used full press data, partial press data, or no-press fallback.
- Reproducibility: source config checksum, code commit SHA, crawl window, and canonical merged file checksum.

## Risks / gates

- Matrix jobs add workflow complexity and more artifacts; keep merge logic small and heavily tested.
- Matrix setup overhead is only acceptable if source jobs run in parallel with the GitHub crawl. If they remain sequential after core crawl, in-process fan-out is faster for five feeds.
- Do not treat article volume alone as success. Gate on valid schemas, explicit source statuses, deterministic merge, and downstream correlation/press-context success.
- Keep optional-source degradation visible. Silent partial data is worse than a failed optional feed.

---

---

# Leela — crawler next-iteration issue

Date: 2026-06-05T16:26:00Z
Requested by: jmservera
Issue: https://github.com/jmservera/SquadScope/issues/237

## Decision

Created issue #237, "Improve multi-source crawler telemetry and source-aware press correlation."

The lead decision is:

- Keep GitHub repository crawl monolithic and cached.
- Keep external RSS/news crawl in-process with bounded parallelism for now.
- Defer Actions matrix fan-out until evidence triggers it: RSS/news p95 > 60s, source count > 10, or a source needs independent retry, credentials, quota, or network isolation.
- Treat merge-before-analyze as deterministic data fan-in, not staged LLM map-reduce.

## Scope captured

The issue asks the next iteration to improve:

- per-source external-news status and metrics;
- schema/versioned deterministic canonical `*-external-news.json`;
- source-aware and bounded `correlate.py` / `render_press_context.py`;
- cross-source dedupe to avoid correlation inflation;
- press-context token/article bounds and telemetry;
- tests for partial failures, fallback paths, reproducibility, dedupe, and citation preservation.

## Non-goals captured

- Multi-pass/staged LLM analysis.
- GitHub raw compaction.
- Matrix split unless the trigger threshold is met.
- Core GitHub crawler topology changes.

## Routing

Labels applied: `squad`, `squad:leela`, `squad:bender`, `go:yes`.

Bender is the likely implementation owner; Fry should validate reliability gates; Farnsworth should review press-context quality.

---

---

# Bender PR #236 Security Fix

## Context
Hermes blocked PR #236 because config-driven external RSS sources were fetched directly without egress URL validation or explicit per-request timeouts.

## Decision
External news RSS source configs now require HTTPS URLs whose host is in the approved feed allowlist, with credentials, local/private/link-local targets, and unexpected ports rejected before crawl. Fetching now goes through `urllib.request.urlopen` with an explicit bounded timeout before handing bytes to `feedparser`, while retaining the existing config-driven source list and bounded in-process worker pool.

## Validation
Added tests for invalid/unapproved URL rejection and explicit fetch timeout propagation. Ran `PYTHONPATH=. .venv/bin/python -m pytest tests -q` with 563 passing tests.

---

---

# Leela — Issue 234 external news source architecture

Date: 2026-06-05T15:36:19.379+00:00
Issue: #234

## Decision

Keep external news crawling in the existing crawl job and make the RSS source list config-driven via `config/external_news_sources.json`. Fetch the configured feeds concurrently inside `scripts/techcrunch_crawler.py` using a bounded thread pool, and write one weekly enrichment artifact: `data/raw/YYYY-WNN-external-news.json`.

## Rubberduck tradeoff

Separate GitHub Actions jobs would parallelize at the runner level, but every source would repeat checkout, Python setup, dependency install, artifact upload/download, and failure-handling boilerplate. For five RSS feeds, that overhead is larger than the network wait we are optimizing away, and it would fragment a single enrichment contract across multiple artifacts.

In-process threading matches the current architecture better: RSS fetching is I/O-bound, feedparser work is light, and the existing crawl job already owns raw data artifact handoff. A bounded pool preserves Actions compute, keeps one failure surface, and lets future sources be added by config without editing workflow topology.

## Scope boundary

This is a small architectural refactor around an existing RSS crawler, so Leela implemented directly rather than reassigning to Bender. Deeper crawler work, such as source-specific parsing, feed health dashboards, or correlation logic, should remain Bender-owned.
