# Leela — History

## Project Context
- **Project:** SquadScope — A GitHub Pages site that summarizes weekly tech news from GitHub
- **Stack:** TBD (GitHub Actions for automation, static site for GitHub Pages)
- **User:** jmservera
- **Goal:** Review new GitHub repos weekly, track trending repos by stars, summarize trends with critical thinking about what's important, what's trending, and what's missing. Future expansion to other tech news platforms.

## Learnings

### 2026-05-18T12:07:20.778+02:00 — Phase 2 PR Review

- **PR #27:** Not mergeable yet. The crawl workflow restores the `crawl-cache` artifact into repo root (`path: .`) while `scripts/crawl.py` reads cache from `data/cache/`, so the warm-cache handoff does not actually work yet.
- **PR #28:** Not mergeable yet. The spec/prompt require the stable H2 heading `## Trending This Week`, but the sample analyzed artifact still uses `## Trending This Week (Stars Gained)`, so the example does not satisfy its own contract.
- **GitHub constraint:** `gh pr review --request-changes` is blocked on self-authored PRs, so the blocking findings were recorded as PR comments instead.

### 2026-05-18 — PRD Authoring

- **PRD location:** `docs/PRD.md` — comprehensive PRD covering all requirements from jmservera
- **Architecture decisions made:**
  - Hugo recommended as static site generator (speed, simplicity, native RSS)
  - Pagefind for client-side search (static, no server dependency)
  - RSS + GitHub Releases for MVP notifications (zero external dependencies)
  - Plugin pattern for future data source extensibility
  - Reskill every 5 runs via simple counter in `.squad/run-counter.txt`
- **Key open questions flagged:**
  - How to invoke Copilot in GitHub Actions (OQ1, OQ3) — blocks Phase 2
  - Hugo vs Astro preference (OQ2) — awaiting stakeholder input
  - Star threshold for significance filtering (OQ4) — proposed 50 stars/week
- **User preferences noted:**
  - jmservera wants full automation with zero manual intervention
  - "Nap and reskill" metaphor is important — deliberate self-improvement built into the system
  - Free-only notification options
  - Ever-growing archive — nothing deleted
- **Content structure:** weekly (immutable) → monthly (append-only) → yearly (append-only)
- **Data paths:** `data/raw/` (JSON), `data/analyzed/` (Markdown), `content/` (Hugo pages)

### 2026-05-18T10:06:38.734+02:00 — PRD Decomposition

- **Decomposition approach:** Split the PRD into tightly scoped, single-session GitHub issues organized by delivery phase and explicit handoffs between crawl, analyze, generate, notify, and reskill stages.
- **Issue count:** 18 delivery issues + 6 governance/validation issues = 24 total issues.
- **Phase structure:** Added a new **Phase 0: Investigation** in front of Foundation so OQ1/OQ3 (Copilot CLI in Actions + auth path) are resolved before automation work proceeds.
- **Assignment pattern:** Mapped issues to roster strengths — Bender for Actions/crawler/integrations, Farnsworth for analysis/reskill logic, Amy for site/search/UX, Fry for validation, and Leela for architecture/docs.

### 2026-05-18T10:11:20Z — Decisions Merged

- **Copilot CLI:** Standalone CLI with fine-grained PAT (Copilot Requests) approved for Phase 0. Fallback: GitHub Models API.
- **MCP crawling:** Multi-site crawling authorized; remote calls require allowlist in GitHub Copilot agent settings.
- **Phase 0 gating:** OQ1/OQ3 investigation issues must close before Phase 2 analyzer work begins.
- **Next:** Issue creation from scripts/create-issues.sh is ready for execution.

### 2026-05-18T10:25:12.565+02:00 — CI Analysis Interface & Fallback Architecture (Issue #2)

- **Architecture decision published:** `.squad/decisions/inbox/leela-ci-architecture-decision.md`
- **Primary path:** Standalone `copilot` CLI with fine-grained PAT (`COPILOT_GH_TOKEN` secret → `COPILOT_GITHUB_TOKEN` env var). Programmatic mode with `--no-ask-user`, explicit `--allow-tool` flags.
- **Fallback path:** GitHub Models API (`models.github.ai`) with built-in `GITHUB_TOKEN` and `permissions: models: read`. Triggered on CLI auth failure, quota exhaustion, or repeated errors.
- **Pipeline contracts formalized:**
  - Crawl → Analyze: `data/raw/YYYY-WNN.json` (repo objects array)
  - Analyze → Generate: `data/analyzed/YYYY-WNN-summary.md` (Markdown + YAML frontmatter with `quality_score`)
  - Generate → Deploy: `public/` (Hugo build output)
- **Reviewer gate:** quality_score ≥ 60, three required sections (Signal/Noise/Gaps), word count ≥ 200. Blocks publish on failure.
- **Token strategy:** Fine-grained PAT with Account → Copilot Requests permission. Classic PATs not supported. Future spike: `GITHUB_TOKEN` + `copilot-requests: write`.
- **MCP strategy:** Allowlist-gated remote calls, tool definitions in `.github/copilot/mcp.json`, crawl-stage only for external HTTP.
- **Nap & reskill interface:** Every 5th run, Copilot CLI reads squad state and writes improvement recommendations to `.squad/reskill/YYYY-WNN.md`.
- **Resolves:** OQ1 and OQ3 from PRD. Unblocks Phase 2 analyzer work.

### 2026-05-18T10:27:35Z — Phase 0 Completion (Scribe)

- **Status:** Phase 0 is complete. Architecture decision merged into `.squad/decisions.md`.
- **Secret configured:** `COPILOT_GH_TOKEN` repo secret established (coordinator action).
- **Issues closed:** #1 (completed by Bender) and #2 (Leela architecture).
- **Team notification:** All agents notified that Phase 0 is complete and architecture is published.
- **Next phase:** Phase 1 (crawlers and generators) can proceed independently. Phase 2 (analyzer) is unblocked.

### 2026-05-18T13:20:07.067+02:00 — Topic Channels PRD

- **Deliverable:** `docs/PRD-topic-channels.md` — feature PRD for topic-specific news channels
- **PR:** #39 (squad/topic-channels-prd → main)
- **Key decisions:**
  - Feature first, not separate platform — extends existing pipeline with topic namespace
  - v1 = single configurable topic per instance (fork per topic); v2 = multi-topic deferred
  - Per-topic learning isolation (wisdom, skills, predictions, scorecards)
  - New scoring pipeline between crawl and analyze (relevance score 0-100)
  - Prediction ledger (`predictions.jsonl`) with hindsight validation at week N+4
  - `squadscope.topic.yml` as the single config file controlling all topic behavior
  - Two example configs shipped: ai-ml and rust
- **Rubber-duck findings addressed:** All 7 findings incorporated (namespacing, multi-instance, learning isolation, scoring pipeline, prediction ledger, channel structure, quality criteria)
- **Learning audit gaps addressed:** G7 (prompt feedback), G8 (hindsight validation), G9 (prediction registry), G13 (enrichment signals as OQ5)
- **Implementation plan:** 15 issues with dependency graph, ~7-9 sessions estimated

### 2026-05-18T10:59:10.800+02:00 — Phase 1 PR Review Gate

- **PR #26 outcome:** Acceptable and merged after validation. The hardened crawler delivered the expected Phase 1 improvements: caching, star snapshots, stronger low-signal filtering, bounded retry/rate-limit behavior, partial-failure metadata, and regression tests for the new query and payload behavior.
- **PR #25 outcome:** I flagged a blocker against the dry-run artifact: the checked-in file under `data/analyzed/` does not match the approved Analyze → Generate contract in `.squad/decisions.md` (`Signal` / `Noise` / `Gaps`). By the time I verified final PR state, GitHub already showed PR #25 as merged, so the blocker was recorded as review commentary and follow-up guidance rather than an enforceable lockout.
- **Operational constraint:** Because the authenticated GitHub account is also the PR author, GitHub blocked formal approve/request-changes reviews. Outcome had to be recorded by comment, and only PR #26 could be actively merged during this pass.

### 2026-05-19T05:17:53.102+02:00 — Cost Estimation PRD

- **Deliverable:** `docs/PRD-cost-estimation.md` — comprehensive PRD for token-based Copilot billing cost estimation and optimization
- **Key findings:**
  - Weekly analysis cost: ~$0.30/run (Claude Sonnet 4, ~90K input tokens dominated by 301KB raw JSON)
  - Reskill cost: ~$0.036/run (GPT-4.1, much smaller context, runs every 5th week)
  - Annual all-in cost: ~$16/year for 52 weekly pages — $0.31/page
  - Context growth is modest (2-5%/year on weekly runs) because raw JSON dominates and is stable
  - Reskill grows faster (24-49%/year) due to accumulating history, but runs infrequently
- **Optimization levers identified (ordered by ROI):**
  1. Pre-process raw JSON to reduce tokens (40-60% savings on input)
  2. Model downgrade for routine analysis (GPT-4.1 or Haiku saves 33-67%)
  3. Prompt caching if available (77% savings on JSON portion)
  4. Token budget with tiered degradation
- **Pricing model hypothesis (pending OQ6 validation):** GitHub Models API and Copilot CLI are assumed to use the same per-token rates, with the difference being auth mechanism and agentic capabilities rather than cost per token. This assumption needs empirical validation — see PRD OQ6.
- **Open risk:** Whether Copilot CLI transcript exposes actual token usage (needed for monitoring)

### 2026-05-19T11:48:44.543Z — PR #54 Merged (Cost Estimation)

- **Status:** All 4 review comments resolved and PR squash-merged to main
- **Outcome:** Cost estimation framework approved for Phase A implementation
- **Integration:** Cost tracking issues will be added to Phase A backlog
- **Team note:** Cost analysis findings established sustainability baseline; no immediate budget action required but monitoring framework is essential for future growth planning

### 2026-05-19T11:55:46.116Z — PR #55 Review (TechCrunch RSS PRD)

- **Verdict:** REJECTED (request-changes, recorded as comment due to self-author constraint)
- **Reason:** PR title/description promises a TechCrunch RSS integration PRD but the branch contains zero TechCrunch-related content. Actual diff is stale cost-estimation work already merged via PR #54. Branch has merge conflicts against main.
- **Architectural observation:** The PR description's editorial framing (cross-source correlation to distinguish press hype from organic momentum) is sound and aligned with Decision #7's plugin architecture. When the actual PRD arrives, key review criteria will be: plugin interface compliance, overlap with topic-channels PRD, and incremental cost impact.
- **Recurring pattern:** This is another instance of a PR being opened before the deliverable is committed — need team discipline on "commit first, then open PR."

### 2026-05-19T11:59:28Z — PR #55 Resolved by Bender (TechCrunch RSS PRD Revision)

- **Handoff:** Rejected PR #55 passed to Bender for revision (Farnsworth locked out per protocol)
- **Outcome:** Bender rewrote PRD, rebased branch, committed deliverable, updated PR description
- **Key decision captured:** TechCrunch as enrichment signal (5–15% correlation hit rate), not primary source
- **Status:** PR #55 ready for next review cycle
- **Team learning:** Rollback/rejection-to-revision cycle worked as designed — rejector (Leela) transitioned ownership cleanly, locked reviewer enabled handoff without conflicts

### 2026-05-19T14:51:48.593+02:00 — PR #55 Re-review (TechCrunch RSS PRD)

- **Verdict:** APPROVED (recorded as comment due to GitHub self-author constraint)
- **Revision quality:** Excellent. Bender delivered a complete 443-line PRD that addresses all original rejection reasons.
- **Key strengths:** Honest 5–15% correlation rate, graceful zero-noise degradation, Decision #7 plugin compliance, explicit failure criteria with removal triggers, phased rollout with exit gates.
- **Minor suggestions (non-blocking):** Spike OQ1 (RSS content depth) before Phase 1; consider `correlate.py` placement at `scripts/` root since it's a cross-source concern; add URL-based dedup for mid-week article republishes.
- **Pattern confirmed:** The reject → reassign → revise cycle works. Bender's revision was materially better than a "fix the branch" patch — it was a ground-up rewrite with proper editorial framing.
- **Operational note:** GitHub still blocks formal approve/request-changes on self-authored PRs. Approval recorded via PR comment.

### 2026-05-19T14:59:57+02:00 — PRD Decomposition into Milestones

- **Milestone structure adopted:** v0.5 (Cost Visibility, 3 issues), v0.6 (Topic Channels Foundation, 6 issues), v0.7 (Learning & Predictions, 9 issues), v0.8 (Cross-Source Intelligence, 7 issues), v0.9 (Cost Optimization & Polish, 9 issues)
- **Total issues created:** 34 issues across 5 milestones (issues #56–#89)
- **PRDs processed:** 3 PRDs moved to docs/processed/ (cost-estimation, topic-channels, techcrunch-integration)
- **Workflow change:** Milestone-based versioning adopted per user directive. PRDs → issues → milestones → docs/processed/
- **Dependencies respected:** TechCrunch (v0.8) follows topic-channels foundation (v0.6); cost optimization (v0.9) follows cost visibility (v0.5)
- **Label convention:** All issues carry `squad` + `squad:{agent}` labels for routing

### 2026-05-19T18:05:10+02:00 — CI Workflow: PR-based commits, ruleset bypass reverted

- **Ruleset fix:** Removed RepositoryRole:5 bypass actor from the `main` ruleset (id 16532660). Branch protection must never be bypassed.
- **Workflow refactor:** All commit steps in `crawl-and-publish.yml` now create a timestamped branch, open a PR via `gh pr create`, and auto-merge with `--squash --auto` instead of pushing directly to main.
- **Steps renamed:** "Commit crawl data" → "Commit crawl data via PR", "Commit analysis" → "Commit analysis via PR", "Commit generated content" → "Commit generated content via PR", reskill step also converted.
- **No more `continue-on-error: true`** on commit steps — they succeed properly now via the PR path.
- **Tests updated:** Adjusted step name references in `tests/test_pipeline.py` to match new naming.
- **Decision recorded:** `.squad/decisions/inbox/leela-no-ruleset-bypass.md`
