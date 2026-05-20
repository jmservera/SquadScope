# Squad Decisions

## Active Decisions

### Architecture Decision: SquadScope Foundation

**Date:** 2026-05-18  
**Author:** Leela (Lead/Architect)  
**Status:** Proposed — awaiting stakeholder approval  
**Context:** PRD for greenfield SquadScope project

**Decisions Proposed:**

1. **Static Site Generator: Hugo (recommended)**
   - Why: Fastest builds (critical as archive grows to hundreds of pages), native RSS, single binary (no Node in CI), mature taxonomy support.
   - Alternative: Astro — better component model but heavier toolchain. Migrate later if interactive features needed.
   - Awaiting: jmservera preference confirmation.

2. **Search: Pagefind**
   - Why: Fully static (no server), tiny JS bundle, build-time indexing, free, supports metadata filters.
   - Trade-off: Index grows with content, but estimated 5+ years before any concern.

3. **Notifications MVP: RSS + GitHub Releases**
   - Why: Zero external dependencies, no accounts to manage, built into GitHub ecosystem.
   - Phase 2: Add GitHub Discussions, webhook support.
   - Not yet: Email newsletters (evaluate if demand exceeds RSS reach).

4. **Pipeline Architecture: Crawl → Analyze → Generate → Notify**
   - Why: Clean separation of concerns, each stage testable independently, artifacts stored between stages.
   - Key constraint: Copilot invocation in CI is an open question. May need fallback strategy.

5. **Reskill Cycle: Every 5th run**
   - Mechanism: Integer counter in `.squad/run-counter.txt`, modulo check.
   - Why simple counter: Avoids complex state management, easy to audit and reset.

6. **Content Immutability: Weekly pages never modified after publication**
   - Why: Historical integrity, reproducible archive, no merge conflicts on old content.

7. **Crawler Plugin Architecture (future-facing)**
   - Why: Design for extensibility now so adding HN/Reddit/etc. doesn't require pipeline rewrite.
   - Pattern: `DataSource` protocol with `crawl()`, `get_name()`, `get_rate_limits()` interface.

**Risks Acknowledged:**
- Copilot API availability in CI (Medium probability, High impact)
- Analysis quality without human review (mitigated by reviewer agent gate + reskill)
- GitHub API rate limits (mitigated by auth tokens + backoff)

**Open Questions Requiring Input:**
- OQ1/OQ3: Copilot in Actions — how? (blocks Phase 2)
- OQ2: Hugo vs Astro final call
- OQ4: Star threshold (50 proposed)
- OQ8: Copilot usage limits in automation## 

## PRD Decomposition into GitHub Issues (2026-05-18)

**Decision:** Decompose docs/PRD.md into 24 issues across Phase 0 (blocker investigations) + Phases 1-4.

**Phase 0 gating condition:** Resolves OQ1/OQ3 — Copilot invocation in GitHub Actions.

**Why:** Isolates largest delivery risk; ensures crawler, analyzer, and generator teams can work independently; makes reviewer gates explicit.

**Implications:**
- Phase 2 analyzer work blocked until Phase 0 closure
- Phase 1 (site foundation + crawler) can proceed in parallel
- QA and documentation are first-class issues## 

## Architecture Decision: CI Analysis Interface & Fallback Architecture

**Date:** 2026-05-18T10:25:12.565+02:00  
**Author:** Leela (Lead/Architect)  
**Status:** Approved  
**Issue:** #2 — Decide CI analysis interface and fallback architecture  
**Depends on:** #1 (Copilot CLI investigation — completed by Bender)

### Context

SquadScope's pipeline requires AI-powered analysis of crawled GitHub data inside GitHub Actions. Bender's investigation (docs/investigation-copilot-cli.md) confirmed that the standalone `copilot` CLI can run in CI with a fine-grained PAT, and identified GitHub Models API as a credible fallback. This decision formalizes the approved architecture.

### Decision 1: Primary Analysis Path — Standalone Copilot CLI

**Approved.** The primary CI analysis engine is the standalone `copilot` CLI (`@github/copilot`).

**Rationale:**
- Officially documented by GitHub for Actions automation
- Real-world precedent (microsoft/BCApps)
- Repo-aware agent behavior: can read/write files, use tools (grep, glob, read, write)
- Supports structured output (`--output-format=json`) and transcript export (`--share=PATH`)
- Programmatic mode (`-p`, `--no-ask-user`) is CI-safe

**Invocation Contract:**

```bash
copilot -p "<prompt>" \
  -s \
  --no-ask-user \
  --allow-tool=read \
  --allow-tool=write \
  --allow-tool=glob \
  --allow-tool=grep \
  --output-format=json \
  --share=./copilot-session.md
```

**Token Strategy:**

| Item | Value |
|------|-------|
| Secret name | `COPILOT_GH_TOKEN` |
| Token type | Fine-grained PAT (`github_pat_...`) |
| Permission | Account → Copilot Requests |
| Env variable | `COPILOT_GITHUB_TOKEN` |
| Resource owner | Personal account (jmservera) |
| Classic PAT | **Not supported** — do not use `ghp_` tokens |

Wire in workflow:
```yaml
env:
  COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GH_TOKEN }}
```

### Decision 2: Fallback Path — GitHub Models API

**Approved.** If Copilot CLI is unavailable, rate-limited, or proves too brittle in CI, the fallback is the GitHub Models API.

**Rationale:**
- Works with built-in `GITHUB_TOKEN` (no PAT needed)
- Simple REST interface, easy to test and mock
- Supports structured JSON responses
- Less agentic, but sufficient for summarization tasks

**Invocation Contract:**

```yaml
permissions:
  models: read

steps:
  - name: Analyze via GitHub Models
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: |
      curl "https://models.github.ai/inference/chat/completions" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $GITHUB_TOKEN" \
        -d @data/prompts/analyze-week.json
```

**Trigger conditions for fallback:**
- Copilot CLI auth failure (token expired, permission revoked)
- Copilot CLI rate-limit / quota exhaustion
- Copilot CLI install failure (npm registry issue, Node version mismatch)
- Repeated non-deterministic failures (3+ retries fail)

### Decision 3: Pipeline Stage Contracts

**Stage boundaries and data flow:**

```
┌─────────┐    JSON     ┌──────────┐   Markdown   ┌──────────┐   HTML    ┌────────┐
│  Crawl  │ ──────────► │ Analyze  │ ───────────► │ Generate │ ────────► │ Deploy │
└─────────┘  data/raw/  └──────────┘ data/analyzed └──────────┘  public/  └────────┘
```

**Crawl → Analyze:**

| Property | Specification |
|----------|---------------|
| Location | `data/raw/` |
| Format | JSON (one file per crawl run) |
| Naming | `YYYY-WNN.json` (e.g., `2026-W21.json`) |
| Schema | Array of repo objects: `{name, url, description, stars, stars_gained, language, topics, created_at}` |
| Contract | Analyzer MUST NOT modify files in `data/raw/` |

**Analyze → Generate:**

| Property | Specification |
|----------|---------------|
| Location | `data/analyzed/` |
| Format | Markdown with YAML frontmatter |
| Naming | `YYYY-WNN-summary.md` |
| Frontmatter | `title`, `date`, `week`, `year`, `categories`, `quality_score` |
| Sections | Signal (important), Noise (overhyped), Gaps (missing from conversation) |
| Contract | Must include `quality_score` (0-100) for reviewer gate |

**Generate → Deploy:**

| Property | Specification |
|----------|---------------|
| Location | `public/` (Hugo build output) |
| Format | Static HTML/CSS/JS |
| Contract | Hugo builds from `content/` which is populated from `data/analyzed/` |

### Decision 4: Reviewer Gate

Analysis output in `data/analyzed/` MUST pass a quality check before the Generate stage runs.

**Gate criteria:**
- `quality_score` in frontmatter is ≥ 60
- All three required sections present (Signal, Noise, Gaps)
- Word count ≥ 200 (guards against empty/stub output)
- No raw JSON or error messages in body

**On failure:**
- Block publish
- Log failure reason to workflow summary
- Open an issue tagged `quality-gate-failure` for human review
- Do NOT retry analysis automatically (preserves Copilot request budget)

### Decision 5: MCP Tools Strategy

**Directive:** MCP tools are authorized for multi-site crawling extensibility.

**Constraints:**
- Remote MCP calls MUST be allowlisted in GitHub Copilot agent settings (repo-level)
- MCP tool definitions live in `.github/copilot/mcp.json`
- Only crawl-stage tools may make external HTTP calls
- Analysis-stage tools are local-only (read, write, glob, grep)

**Future extensibility:**
- Each new data source (HN, Reddit, etc.) is an MCP tool with a `crawl()` method
- Tools registered in allowlist before activation
- Rate limits per-source defined in tool config

### Decision 6: Nap & Reskill Interface

Every 5th pipeline run triggers a reskill cycle. The reskill workflow invokes Copilot CLI to review squad state and propose improvements.

**Mechanism:**

```bash
# Counter check
COUNTER=$(cat .squad/run-counter.txt)
if [ $((COUNTER % 5)) -eq 0 ]; then
  # Reskill invocation
  copilot -p "Read .squad/agents/*/history.md and .squad/decisions.md. \
    Assess: What patterns are working? What should change? \
    Write recommendations to .squad/reskill/YYYY-WNN.md" \
    --no-ask-user \
    --allow-tool=read \
    --allow-tool=write \
    --allow-tool=glob \
    --share=./reskill-session.md
fi
```

**Input context for reskill:**
- `.squad/agents/*/history.md` — all agent learnings
- `.squad/decisions.md` — current decision log
- `data/analyzed/` — recent analysis outputs (quality trend)
- `.squad/run-counter.txt` — run history

**Output:**
- `.squad/reskill/YYYY-WNN.md` — improvement recommendations
- Optional: PR with proposed changes to agent prompts or pipeline config

### Decision 7: Future Validation Spike — GITHUB_TOKEN + copilot-requests: write

**Status:** Noted for future spike (not yet approved for production use).

The community action `austenstone/copilot-cli` demonstrates that `GITHUB_TOKEN` with `permissions: copilot-requests: write` may eliminate the PAT requirement entirely. GitHub's official docs do not yet confirm this path.

**Spike criteria:**
- Create a test workflow with `copilot-requests: write`
- Validate auth succeeds without PAT
- Confirm quota/billing behaves identically
- If successful: migrate from PAT to workflow token (simpler, no secret rotation)

### Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Copilot CLI quota exhaustion | Medium | High | Coarse-grained prompts; fallback to Models API |
| PAT expiration in CI | Medium | Medium | GitHub secret expiry alerts; spike on workflow token |
| Analysis quality drift | Low | High | Reviewer gate + reskill cycle |
| MCP allowlist misconfiguration | Low | Medium | CI test that validates mcp.json against live config |
| Node 22 unavailability in runner | Very Low | Low | Pin `actions/setup-node@v4` with explicit version |

### Summary

The SquadScope CI analysis pipeline uses a two-tier approach: Copilot CLI (primary, agentic, repo-aware) with GitHub Models API (fallback, simpler, REST-based). Data flows through well-defined stage boundaries with JSON → Markdown → HTML transformations. A quality gate ensures no low-quality analysis reaches publication. The architecture is designed for extensibility via MCP tools and self-improvement via the reskill cycle.## 

## Crawler Hardening Decision (2026-05-18)

**Issue:** #6 — Harden crawler for production readiness  
**Author:** Bender (Crawler agent)  
**Status:** Approved — implemented in crawler  
**Date:** 2026-05-18T10:59:10.800+02:00

### Decision: Degradable README Signals & Bounded Retry Strategy

Treat README lookups as a degradable signal instead of a hard-stop path. The crawler now:
- Caches API responses to reduce repeated calls
- Saves weekly star snapshots under `data/snapshots/`
- Logs rate-limit state for observability
- Caps README retry delays to ensure partial failures don't block weekly crawls

**Rationale:**
- Search queries are cheap, but hundreds of README checks can trigger secondary GitHub API throttling
- Bounded retries plus persistent cache keep Phase 1 crawls finishable
- Partial failures recorded in metadata preserve data integrity even when GitHub responses are incomplete

**Outcomes:**
- Phase 1 crawls remain finishable even during GitHub API congestion
- Farnsworth (analyzer) receives usable JSON data even when README metadata is partial
- Better observability into rate-limit behavior across runs

---## 

## Analyze Job Integration & Quality Gate (2026-05-18)

**Issue:** #10 — Integrate Actions analyze job with Copilot path and reviewer gate  
**Author:** Bender (Crawler agent)  
**Status:** Approved for Phase 2 implementation  
**Date:** 2026-05-18T13:05:53.678+02:00

### Decision

Extend `.github/workflows/crawl-and-publish.yml` with an `analyze` job that runs after `crawl` and enforces an automated quality gate before downstream publish steps.

**Stage handoff artifacts:**
- `raw-data` for crawl → analyze
- `analyzed-data` for analyze → generate

**Analysis paths:**
1. Primary: Standalone Copilot CLI with `permissions.copilot-requests: write` and `COPILOT_GH_TOKEN`
2. Fallback: `scripts/analyze_fallback.py` using GitHub Models API with `permissions.models: read`

**Quality Gate Contract** — workflow must fail if any of the following are false:
- YAML frontmatter exists with exact required keys
- `quality_score` is an integer ≥ 60
- Required H2/H3 sections appear in documented order
- Body word count ≥ 200
- Output does not leak raw JSON, traceback, or placeholder content

**Implications:**
- Generate jobs can safely consume `analyzed-data` without inspecting raw crawl artifacts
- Copilot failures do not block immediately; GitHub Models fallback preserves publishability
- Reviewer-gate failures stop low-quality summaries before downstream stages

---## 

## Generate & Deploy Workflow (2026-05-18)

**Issue:** #11 — Implement generate-and-deploy workflow for GitHub Pages  
**Author:** Amy (Generator agent)  
**Status:** Approved for Phase 2 implementation  
**Date:** 2026-05-18T13:20:07.067+02:00

### Decision

Keep `.github/workflows/deploy-site.yml` for push-to-main deployments. Weekly automation lives in `.github/workflows/crawl-and-publish.yml` end-to-end (crawl → analyze → generate → deploy).

**Generate stage:**
1. Read `data/analyzed/YYYY-WNN-summary.md`
2. Write Hugo page to `content/weekly/YYYY/WNN.md` with archetype-compatible frontmatter
3. Commit back to default branch before Pages build so future archive builds retain previously published content

**Deploy:**
- Build with Hugo 0.161.1 + Pagefind
- Deploy with `actions/deploy-pages@v4` under `github-pages` environment

---## 

## Reskill Retrospective & Learning State (2026-05-18)

**Issue:** #14 — Reskill retrospective, learned-state injection, and quality trend tracking  
**Author:** Farnsworth (Analyst)  
**Status:** Approved for Phase 2 implementation  
**Date:** 2026-05-18T15:22:25.067+02:00

### Decisions

1. **Reskill context** from latest analyzer evidence, not generic squad history:
   - Inputs: last ~5 `data/analyzed/*-summary.md` files, `data/snapshots/` hindsight, `wisdom.md`, learned skills, quality trend report
   - Why: gives retrospective concrete calibration points and closes gap findings

2. **Learned state flows back** into weekly analyzer prompt:
   - Inject `.squad/identity/wisdom.md` into `{{WISDOM}}` placeholder
   - Inject concatenated markdown from `.squad/skills/` into `{{SKILLS}}` placeholder
   - Why: without prompt injection, learning artifacts exist but never influence future analysis

3. **Quality trend tracking** is first-class reskill input:
   - `scripts/track_quality.py` reads `quality_score` from analyzed summaries, produces markdown trend report
   - Why: squad needs lightweight longitudinal measure of editorial quality improvement

4. **Reskill outputs in persistent squad state:**
   - `.squad/reskill/` for weekly retrospective reports
   - `.squad/skills/` for extracted reusable patterns
   - Both committed to git (not ephemeral workflow output)

---## 

## Topic-Specific News Channels Architecture (2026-05-18)

**Issue:** #16 — Topic-specific news channels architecture  
**Author:** Leela (Lead/Architect)  
**Status:** Proposed  
**PRD:** docs/PRD-topic-channels.md  
**PR:** #39  
**Date:** 2026-05-18T13:20:07.067+02:00

### Key Architectural Decisions

**Feature First, Not Platform:** Generalize SquadScope into topic channels by adding topic namespace to existing pipeline. No new platform, no new repo structure. Same codebase, configured differently.

**Multi-Instance Single-Topic (v1):** One fork/config per topic with isolated learning, own `squadscope.topic.yml`, own Actions schedule, own GitHub Pages site. Multi-topic single-instance is v2.

**Topic Config as Single Source of Truth:** `squadscope.topic.yml` controls:
- Crawler queries
- Scoring weights and thresholds
- Analysis tone and audience
- Learning state paths
- Quality criteria

**Scoring Pipeline (New Stage):** GitHub topic search is noisy. New `scripts/score_repos.py` between crawl and analyze, scoring repos 0-100 on relevance/momentum/language/noise/recency. Only repos ≥40 reach analysis.

**Per-Topic Learning Isolation:**
- `topics/{id}/wisdom.md` — domain-specific heuristics
- `topics/{id}/skills/` — extracted patterns
- `topics/{id}/predictions.jsonl` — prediction ledger
- `topics/{id}/scorecards/` — hindsight validation results
- No cross-topic contamination

**Prediction Ledger with Hindsight Validation:** Every analysis appends machine-readable predictions to `predictions.jsonl`. Four weeks later, `scripts/validate_predictions.py` scores them against actual outcomes (star deltas, fork growth). Scorecards feed into reskill.

**Topic Quality Criteria:**
- Minimum N repos/week passing filters
- Maximum false positive rate
- Minimum genuinely significant repos per issue

### Implications

- Crawler must read config instead of hardcoded queries
- Analysis prompt becomes a template with injection points
- Hugo gains topic taxonomy and per-topic RSS
- All data paths gain `{topic_id}/` prefix
- Reskill reads per-topic state

### Open for Discussion

- Should enrichment signals (forks, contributors) be in v1 scorer or deferred?
- Prediction confidence: fixed initial values or prompt-generated?
- Topic config in root vs `topics/` directory?

---## 

## Decision: Use `publish` branch for automated data commits (2026-05-19)

**Author:** Bender (Crawler)
**Status:** Implemented (PR #129)
**Fixes:** Issue #128

### Context

The crawl-and-publish workflow failed because:
1. The repo setting "Allow GitHub Actions to create or approve pull requests" is disabled
2. `gh pr create` with `GITHUB_TOKEN` is blocked by this setting
3. Even if enabled, the `copilot_code_review` rule + `required_review_thread_resolution` on main could block auto-merge unpredictably

### Decision

Replace PR-based commits with direct push to an unprotected `publish` branch.

- The main branch ruleset only protects `refs/heads/main`
- The `publish` branch accepts direct pushes from workflow `GITHUB_TOKEN`
- Inter-job data flow uses artifacts (unchanged)
- Deploy job downloads all artifacts directly (no dependency on branch state)
- `reskill-check` reads `run-counter.txt` from `publish` branch with fallback to main

### Consequences

- Automated data no longer lands on `main` automatically — it accumulates on `publish`
- A separate manual or scheduled merge from `publish` → `main` can sync when desired
- Main branch protection remains fully intact (no bypasses)
- Pipeline reliability is decoupled from PR permission settings

### Alternatives Considered

1. Enable "Allow GitHub Actions to create PRs" — requires repo admin action, doesn't solve auto-merge reliability
2. Use a PAT/GitHub App token — adds secret management complexity
3. `--admin` flag on merge — bypasses protection, violates team decision

---## 

## Directive: Always test the whole publishing cycle before considering work done (2026-05-19)

**By:** jmservera (via Copilot)
**Date:** 2026-05-19T19:37:45+02:00

User directive — captured for team memory. Always test the whole publishing cycle before considering work done.

---## 

## Directive: Never bypass branch protection rulesets (2026-05-19)

**By:** jmservera (via Squad)
**Date:** 2026-05-19T18:05:10Z

CI workflows must not push directly to protected branches. Use PR-based commits instead. Never add bypass actors to rulesets to work around branch protection.

**Why:** Branch protection exists to ensure code review on every change. Bypassing it for convenience undermines the safety net.

---


# Decision: Divergence Section Uses Narrative Prose in Reader Mode

**Date:** 2026-05-19T21:24:54+02:00  
**Author:** Farnsworth (Analyst)  
**Status:** Implemented  
**Affects:** `scripts/render_press_context.py`, `tests/test_render_press_context.py`## 

## Rationale

Raw topic-and-repo bullet lists communicate data but not meaning. Readers gain more from a paragraph that groups activity, links to repos by short name, and closes with an interpretive sentence. The AI model still needs the full structured data — so the dual-mode architecture cleanly separates the two use cases.## 

## Implications

- Any future changes to reader-mode divergence prose go into the two helper functions.
- If the data schema adds new fields (e.g., `growth_rate`), the helpers can incorporate them without touching AI-mode output.
- Tests updated: `test_reader_mode_has_narrative` and `test_reader_mode_has_repo_links` replace the old phrase-matching assertions. 499 tests pass.

---

# Decision: No-AI Fallback Must Re-render from Raw Data for Reader Mode

**Date:** 2026-05-19T21:54:14+02:00  
**Author:** Farnsworth  
**Status:** Implemented (PR #137, merged)## 

## Decision

**Re-render from raw JSON data in the no-AI path.** Specifically:

1. Extract the week identifier from the `press_context_path` filename stem.
2. Load `data/raw/{WEEK}-techcrunch.json` and `data/analyzed/{WEEK}-correlations.json`.
3. Call `render_press_context(tc_data, corr_data, week, reader_mode=True)`.
4. If raw files are absent, fall back to the existing strip-based approach.## 

## Impact

- The no-AI CI path now uses identical rendering logic to the AI path's fallback output.
- Any future changes to `render_press_context(..., reader_mode=True)` automatically apply to the no-AI path without further changes.
- The W21 page will show the correct narrative format on the next pipeline run.## 

## Context

The Correlation Summary section was showing a raw bullet list of repo names, confidence scores, and match types — useful for AI prompt consumption but meaningless to human readers. The Divergence section had already been upgraded to narrative prose (PR #131). This decision extends that pattern to correlations.## 

## Alternative Considered

**No README fetching — use only repo names**: simpler and fully deterministic, but produces flat prose with no editorial context about what the repos actually do. The README fetch adds signal at low cost (max 6 network requests, fails gracefully).## 

## Context

The CI pipeline runs AI analysis (Copilot CLI) and reskill (GitHub Models API) but neither job leverages the squad agent system. The analysis agent has no identity, cannot read its own history/skills, and has no mechanism to write learnings back. The reskill job bypasses Copilot CLI entirely and uses a model (`openai/gpt-4.1`) that returns 403.## 

## Risks

| Risk | Mitigation |
|------|-----------|
| Agent writes bad content to `.squad/` files | Quality gate still runs on analysis output; .squad changes are append-only learnings |
| Copilot CLI doesn't support `--agent` as expected | Fallback path (GitHub Models via reskill.py) still works without agent identity |
| Learning state diverges between publish branch and main | Periodic sync PRs already exist; learnings on publish are forward-compatible |## 

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction

## Weekly Analysis Article Restructure

**Date:** 2026-05-20T19:15:53.942+02:00  
**Author:** Leela (Lead/Architect) — Proposed; Farnsworth (Analyst) — Implemented  
**Status:** Implemented  
**Requested by:** jmservera

### Context

The weekly analysis output was structured like a repo-listing document (Notable New Repositories, Trending This Week, etc.). User requested a restructure to read like a Gartner/McKinsey-style trend insight brief.

### Decision

Replace the six-section repo-listing structure with a six-section editorial structure:

| Old Section | New Section |
|---|---|
| `## Notable New Repositories` | (moved to `### Notable Projects` under Key References) |
| `## Trending This Week` | (rolled into `## This Week's Trends`) |
| `## Industry & Press Correlation` | `## Where Industry Meets Code` |
| `## Trend Analysis` / `### Signal` / `### Noise` | `## Signal & Noise` (integrated prose, no sub-headings) |
| `## What's Missing` / `### Gaps` | `## Blind Spots` |
| `## Conclusion` | `## The Week Ahead` |
| _(new)_ | `## Key References` / `### Notable Projects` / `### Press & Industry` |

### Rationale

1. Lead with synthesis, not inventory.
2. Comparative press analysis gets its own section.
3. Signal & Noise integrated (no mandatory sub-headings).
4. Key References at the end (scannable).
5. Forward-looking close ("The Week Ahead").

### Implementation

**Files Changed:** `prompts/analyze-weekly.md`, `docs/analysis-spec.md`, `scripts/analysis_gate.py`, `scripts/analyze_fallback.py`, `scripts/generate_rollups.py`, 5 test files.

**Backward Compatibility:** `generate_rollups.py` tries new heading names first and falls back to old names. All frontmatter fields, repo link format, quality_score gate, and body word count rules unchanged.

**Outcome:** All 519 tests pass with new structure.
