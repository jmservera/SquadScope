# Squad Decisions Archive

## Archived Decisions (older than 7 days)

## Analysis Output Specification (2026-05-18)

**Issue:** #9 — Define weekly analysis contract between crawler output and site generator  
**Author:** Farnsworth (Analyst)  
**Status:** Approved for Phase 2 implementation  
**Date:** 2026-05-18T12:07:20.778+02:00

## Analyze Job Integration & Quality Gate (2026-05-18)

**Issue:** #10 — Integrate Actions analyze job with Copilot path and reviewer gate  
**Author:** Bender (Crawler agent)  
**Status:** Approved for Phase 2 implementation  
**Date:** 2026-05-18T13:05:53.678+02:00

## Architecture Decision: CI Analysis Interface & Fallback Architecture

**Date:** 2026-05-18T10:25:12.565+02:00  
**Author:** Leela (Lead/Architect)  
**Status:** Approved  
**Issue:** #2 — Decide CI analysis interface and fallback architecture  
**Depends on:** #1 (Copilot CLI investigation — completed by Bender)

## Crawler Cache & Artifact Handoff Decision (2026-05-18)

**Issue:** #8 — Create weekly Actions crawl job with artifact handoff  
**Author:** Bender (Crawler agent)  
**Status:** Approved for implementation  
**Date:** 2026-05-18T12:07:20.778+02:00

## Crawler Hardening Decision (2026-05-18)

**Issue:** #6 — Harden crawler for production readiness  
**Author:** Bender (Crawler agent)  
**Status:** Approved — implemented in crawler  
**Date:** 2026-05-18T10:59:10.800+02:00

## Dry-Run Validation Findings (2026-05-18)

**Issue:** #7 — Validate dry-run execution of full pipeline  
**Author:** Fry (Validator)  
**Status:** Findings archived for Phase 2 planning  
**Date:** 2026-05-18T10:59:10.800+02:00

## Generate & Deploy Workflow (2026-05-18)

**Issue:** #11 — Implement generate-and-deploy workflow for GitHub Pages  
**Author:** Amy (Generator agent)  
**Status:** Approved for Phase 2 implementation  
**Date:** 2026-05-18T13:20:07.067+02:00

## Reskill Retrospective & Learning State (2026-05-18)

**Issue:** #14 — Reskill retrospective, learned-state injection, and quality trend tracking  
**Author:** Farnsworth (Analyst)  
**Status:** Approved for Phase 2 implementation  
**Date:** 2026-05-18T15:22:25.067+02:00

## Run Counter & Reskill Trigger (2026-05-18)

**Issue:** #15 — Add run counter persistence and every-fifth-run reskill trigger  
**Author:** Bender (Crawler agent)  
**Status:** Approved for Phase 1B implementation  
**Date:** 2026-05-18T15:22:25.067+02:00

## Topic-Specific News Channels Architecture (2026-05-18)

**Issue:** #16 — Topic-specific news channels architecture  
**Author:** Leela (Lead/Architect)  
**Status:** Proposed  
**PRD:** docs/PRD-topic-channels.md  
**PR:** #39  
**Date:** 2026-05-18T13:20:07.067+02:00

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
- OQ8: Copilot usage limits in automation

## 2026-05-19: Milestone-based workflow adopted

- **Owner:** jmservera (via Copilot)
- **Date:** 2026-05-19
- **Decision:** All future work organized into versioned milestones (v0.5, v0.6, etc.). PRDs are decomposed into issues, assigned to milestones, then moved to docs/processed/. This enables progress tracking and versioning.
- **Why:** User directive — makes work easier to follow and enables versioning.

## 2026-05-19: Press Context Dual-Mode Rendering

- **Owner:** Farnsworth
- **Date:** 2026-05-19T20:50:22+02:00
- **Status:** Implemented
- **Decision:** Implement dual-mode rendering in `render_press_context.py` to serve AI prompts (full data + instructions) and reader-facing fallback (clean narrative) separately via `reader_mode` parameter and post-processing.
- **Why:** The press context serves two audiences. AI prompts need full data and model instructions; reader-facing pages should not expose AI directives or 100+ repo lists.
- **Changes:**
  - `render_press_context(reader_mode=False)` — new kwarg. When True, limits correlations to top 10, strips `### Instructions` block, and passes reader_mode to `format_divergences()`
  - `format_correlations_list(top_n=None)` — new kwarg. Truncates display and appends "…and N more repos"
  - `format_divergences(reader_mode=False)` — new kwarg. Replaces instruction bullets with reader-friendly narrative
  - `analyze_fallback._strip_ai_instructions(content)` — new helper. Applied in no-AI path to post-process rendered content
- **Consequences:** AI prompt path unchanged (full instructions + list continue to model); no-AI fallback now produces clean reader output. 16 new tests cover truncation, sorting, instruction stripping, narrative injection. All 498 tests passing. PR #135 merged.

## 2026-05-19: TechCrunch RSS as Enrichment Signal (PR #55)

- **Owner:** Bender
- **Date:** 2026-05-19
- **Decision:** TechCrunch RSS integration is an enrichment signal (not primary source) with explicit low-expectation framing (5–15% correlation hit rate). Feature degrades to zero noise when no correlations found.
- **Why:** Correlation between press articles and repos is inherently low. Value lies in the delta (hype vs traction), not article summarization. Enrichment positioning allows silent failure without degrading digest.
- **Implications:** All future `DataSource` plugins must declare "primary" or "enrichment" status. Enrichment sources require explicit failure/removal criteria. Farnsworth's analysis treats correlation data as optional context, never required input.

## Constraints Respected

- `reader_mode=False` output is unchanged — AI prompt consumers still receive full raw data.
- README fetching only happens in reader_mode=True paths (no side effects in CI pre-rendering).
- Article title lookup reuses the already-loaded `tc_data["articles"]` list — no new I/O for the article side.
- All new functions are covered by unit tests; 513 tests pass.

---

# Decision: CI Self-Learning Pipeline Architecture

**Date:** 2026-05-19T22:57:55+02:00
**Author:** Leela (Lead/Architect)
**Status:** Proposed
**Scope:** Analysis and reskill CI jobs — self-learning loop

## Cost Estimation & Budget Controls (2026-05-19)

**Issue:** #17 — Cost estimation framework for SquadScope  
**Author:** Leela (Lead/Architect)  
**Status:** Proposed  
**PRD:** docs/PRD-cost-estimation.md  
**Date:** 2026-05-19T05:17:53.102+02:00

## Directive: Always test the whole publishing cycle before considering work done (2026-05-19)

**By:** jmservera (via Copilot)
**Date:** 2026-05-19T19:37:45+02:00

User directive — captured for team memory. Always test the whole publishing cycle before considering work done.

---

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
**Affects:** `scripts/render_press_context.py`, `tests/test_render_press_context.py`

## Files Changed

- `scripts/analyze_fallback.py` — `_render_press_section_no_ai()` (lines 346–370)

---

# Decision: Correlation Summary — Narrative Prose in reader_mode

**Date:** 2026-05-19T22:34:57+02:00  
**Author:** Farnsworth (Analyst)  
**PR:** #138  
**Status:** Merged

## Implications

- Any future changes to reader-mode divergence prose go into the two helper functions.
- If the data schema adds new fields (e.g., `growth_rate`), the helpers can incorporate them without touching AI-mode output.
- Tests updated: `test_reader_mode_has_narrative` and `test_reader_mode_has_repo_links` replace the old phrase-matching assertions. 499 tests pass.

---

# Decision: No-AI Fallback Must Re-render from Raw Data for Reader Mode

**Date:** 2026-05-19T21:54:14+02:00  
**Author:** Farnsworth  
**Status:** Implemented (PR #137, merged)

## TechCrunch RSS as First Non-GitHub Data Source (2026-05-19)

**Issue:** TechCrunch integration as first non-GitHub crawler plugin  
**Author:** Farnsworth (Analyst)  
**Status:** Proposed  
**PRD:** docs/PRD-techcrunch-integration.md  
**Date:** 2026-05-19T11:48:44.543Z

## Implementation

- Removed `--model claude-sonnet-4` from Copilot CLI invocations
- Removed workflow pinned preflight model, switched to generic `copilot-default` rate profile
- Promoted `GITHUB_MODELS_MODEL` to workflow-level env with `openai/gpt-4o` default

**Files:** `.github/workflows/crawl-and-publish.yml`, `scripts/preflight_cost_check.py`, `scripts/track_token_usage.py`

---

# Decision: Prevent Copilot stdout from Leaking into Published Markdown

**Date:** 2026-05-20T22:14:02+02:00  
**Owner:** Farnsworth  
**Status:** Proposed

## Weekly Analysis Article Restructure

**Date:** 2026-05-20T19:15:53.942+02:00  
**Author:** Leela (Lead/Architect) — Proposed; Farnsworth (Analyst) — Implemented  
**Status:** Implemented  
**Requested by:** jmservera

### Implementation

**Files Changed:** `prompts/analyze-weekly.md`, `docs/analysis-spec.md`, `scripts/analysis_gate.py`, `scripts/analyze_fallback.py`, `scripts/generate_rollups.py`, 5 test files.

**Backward Compatibility:** `generate_rollups.py` tries new heading names first and falls back to old names. All frontmatter fields, repo link format, quality_score gate, and body word count rules unchanged.

**Outcome:** All 519 tests pass with new structure.

---

# Decision: Model Resilience for Weekly CI

**Date:** 2026-05-20T20:09:26+02:00  
**Owner:** Farnsworth  
**Status:** Proposed

## Impact

- All charters now under 1.5 KB target
- Oversized histories condensed
- 3 new skills extracted (minimal-agent-charter, agent-history-hygiene, weekly-learning-loop)
- 1 existing skill upgraded (branch-protection-pr-workflow)
- **Net savings: 68.4% reduction** (39,568 → 12,521 bytes)

---

# Decision: Farnsworth Weekly Headline Review

**Date:** 2026-05-21T12:33:16.507+02:00
**Author:** Farnsworth (Analyst)
**Status:** Implemented

## Implementation

- Changed Copilot CLI redirects from output markdown to `/dev/null`
- Added `scripts/sanitize_agent_output.py` to strip leaked lines (`✅ Farnsworth is done`, `Editorial thesis:`, etc.)
- Reinforced `prompts/analyze-weekly.md` so agent writes only publication-ready markdown

**Files:** `.github/workflows/crawl-and-publish.yml`, `prompts/analyze-weekly.md`, `scripts/sanitize_agent_output.py`, `tests/test_sanitize_agent_output.py`

---

# Decision: Squad Agent Documentation Restructure

**Date:** 2026-05-21T09:23:40+02:00  
**Author:** Farnsworth (Analyst)  
**Status:** Implemented


## Archived from 2026-06-01 sweep (entries older than 7 days)

## Copilot CLI in GitHub Actions (2026-05-18)

**Requestor:** jmservera  
**Source:** Bender investigation  
**Status:** Approved for implementation

- **Action:** Use standalone **GitHub Copilot CLI** (not deprecated `gh copilot` extension)
- **Auth:** Fine-grained PAT with **Account → Copilot Requests** permission, passed as `COPILOT_GITHUB_TOKEN`
- **Invocation:** Programmatic via `copilot -p "..." -s --no-ask-user --allow-tool=...`
- **Output:** JSON (--output-format=json, JSONL) or markdown (--share=PATH)
- **Fallback:** GitHub Models API with `GITHUB_TOKEN` (permissions: models: read)
- **Next spike:** Test whether `copilot-requests: write` on workflow token replaces PAT (community action shows promise)

## PRD Decomposition into GitHub Issues (2026-05-18)

**Decision:** Decompose docs/PRD.md into 24 issues across Phase 0 (blocker investigations) + Phases 1-4.

**Phase 0 gating condition:** Resolves OQ1/OQ3 — Copilot invocation in GitHub Actions.

**Why:** Isolates largest delivery risk; ensures crawler, analyzer, and generator teams can work independently; makes reviewer gates explicit.

**Implications:**
- Phase 2 analyzer work blocked until Phase 0 closure
- Phase 1 (site foundation + crawler) can proceed in parallel
- QA and documentation are first-class issues

## MCP Tools for Multi-Site Crawling (2026-05-18)

**Directive:** MCP tools may crawl sites beyond GitHub; remote calls require allowlist in Copilot agent settings (GitHub repo settings).

**Impact:** Affects crawler extensibility design (HackerNews, Reddit, etc.) and GitHub Actions Copilot token model.

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

### Decision 7: Weekly Analysis Fail-Fast Policy

Weekly article generation must only publish Copilot-authored analysis. The workflow now fails immediately if Copilot CLI is unavailable or the analysis call fails; it does not fall back to GitHub Models or no-AI summaries.

**Enforcement:**
- `scripts/analysis_gate.py` rejects any analysis source other than `copilot-cli`
- The article title must be a journalistic headline, not the generic `Week NN, YYYY Analysis` template
- If Copilot cannot run, the workflow is expected to be rerun later rather than publishing stale content

**Goal:** prevent generic or stale weekly articles from being published when the preferred analysis agent is unavailable.

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

The SquadScope CI analysis pipeline uses a two-tier approach: Copilot CLI (primary, agentic, repo-aware) with GitHub Models API (fallback, simpler, REST-based). Data flows through well-defined stage boundaries with JSON → Markdown → HTML transformations. A quality gate ensures no low-quality analysis reaches publication. The architecture is designed for extensibility via MCP tools and self-improvement via the reskill cycle.

### Decision: Cache Restoration from Prior Workflow Runs

The weekly crawl workflow (`crawl-and-publish.yml`) MUST restore `data/cache/` from the latest successful run before executing `scripts/crawl.py`.

**Rationale:**
- Reuses the crawler's on-disk GitHub API cache across weekly runs
- Lowers repeated README/search calls on warm runs
- Keeps the crawl stage self-contained until downstream jobs arrive in later issues

**Implementation Details:**
- Workflow needs `actions: read` permission to discover prior successful runs
- Download the `crawl-cache` artifact before running the crawler
- Upload new cache artifact after successful crawl
- Preserve crawler state through GitHub Actions artifact storage

**Implications:**
- Reduces GitHub API rate limit consumption across runs
- Enables faster weekly crawls as cache grows
- Supports Phase 1 crawl-only deliverables

---

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

---

### Key Findings

1. **Hugo Version Pinning Required**
   - Local environment defaulted to `hugo v0.123.7`
   - Repository theme requires `v0.146.0+`
   - Dry-run only succeeded with `hugo v0.161.1`
   - **Action:** Pin Hugo version in CI/validation workflows

2. **Trending Analysis Requires Historical Data**
   - `data/raw/2026-W21.json` contains no usable `stars_gained` values in `trending_repos`
   - Current output is popularity-biased rather than momentum-based
   - **Action:** Implement multi-week aggregation in analyzer for trend detection

3. **Content Filtering Needs Refinement**
   - Sample week contains exploit, bypass, cheat, and game-mod repositories in "new" ranking
   - Current filtering logic insufficient for curated editorial quality
   - **Action:** Implement stricter content filtering or human quality gate in Phase 2

4. **Analyzer-Generator Contract Needs Specification**
   - PRD weekly page shape and approved analyzer contract are close but not identical
   - Generator step needs explicit mapping from analyzed markdown to publishable Hugo content
   - **Action:** Formalize analyzer output schema and generator input contract (Phase 2)

---

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

---

### Decisions

1. **Analyzer output frontmatter is a superset contract.**
   - Required fields: `title`, `date`, `week`, `year`, `tags`, `categories`, `repos_featured`, `stars_tracked`, `top_repo`, `quality_score`, `summary`

2. **Reader-facing structure: five stable H2 sections** (in order):
   - `Notable New Repositories`
   - `Trending This Week (Stars Gained)`
   - `Trend Analysis` (with required `### Signal` and `### Noise` subsections)
   - `What's Missing` (with required `### Gaps` subsection)
   - `Conclusion`

3. **Trending must degrade honestly when momentum data is incomplete.**
   - If `stars_gained` is absent or null, summary must say the section is directional, not a true momentum leaderboard

4. **Analyzer input schema: strict on core fields, tolerant on metadata.**
   - Required: week slug, crawl timestamp, new/trending repo arrays, top topics
   - Optional: `partial_failures`, `filter_summary`, `snapshot_path`

---

### Decision

Keep `.github/workflows/deploy-site.yml` for push-to-main deployments. Weekly automation lives in `.github/workflows/crawl-and-publish.yml` end-to-end (crawl → analyze → generate → deploy).

**Generate stage:**
1. Read `data/analyzed/YYYY-WNN-summary.md`
2. Write Hugo page to `content/weekly/YYYY/WNN.md` with archetype-compatible frontmatter
3. Commit back to default branch before Pages build so future archive builds retain previously published content

**Deploy:**
- Build with Hugo 0.161.1 + Pagefind
- Deploy with `actions/deploy-pages@v4` under `github-pages` environment

---

### Decisions

1. **Create `.squad/run-counter.txt`** initialized to `0`
2. **Increment counter** in `crawl` job's git commit step after syncing default branch, then commit `.squad/run-counter.txt` with `data/raw/` and `data/snapshots/`
3. **Add `reskill-check` job** that reads persisted counter and exposes `should_reskill` for downstream jobs
4. **Add placeholder `reskill` job** that logs the trigger and scaffolds `.squad/skills/` and `.squad/reskill/` until Issue #14 adds full retrospective implementation

**Why:** Reading the counter only after syncing `origin/main` keeps the increment tied to latest persisted state. Committing together ensures survival between weekly runs. Splitting `reskill-check` from `reskill` keeps trigger logic auditable.

---

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

---

### Summary

Current SquadScope cost under token-based billing: ~$0.30/week (~$16/year), well within Copilot Pro's 300 credits/month allowance. However, proactive monitoring and budget controls needed before context growth or model upgrades change the picture.

### Decisions

1. **Accept current cost profile as sustainable** — $16/year is economically trivial; no immediate model downgrade required
2. **Implement token usage tracking (Phase A)** — Add `scripts/track_token_usage.py` and `data/metrics/token-usage.jsonl` to establish baselines before optimizing
3. **Set budget alert thresholds:**
   - Warn at $0.50/run
   - Fail at $1.00/run
   - Email alert at $5/month cumulative
   - Auto-switch to cheaper model at $10/month cumulative
4. **Defer raw JSON pre-processing** — 40-60% savings significant but adds pipeline complexity; implement only if costs grow beyond $30/year
5. **Wisdom.md cap at 5 KB** — Reskill should retire obsolete heuristics, not only append

**Rationale:** Dominant cost driver (raw JSON at 86K tokens) is stable and bounded by crawl scope. Growth comes from wisdom/skills/history accumulation, which is slow. Premature optimization would add complexity without meaningful savings at current scale.

**Risks:**
- OQ5/OQ6: Billing mechanics for Copilot CLI vs Models API may differ in ways not yet visible
- Credit exhaustion mid-month would disrupt weekly pipeline if no degradation path exists

---

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

---

### Decision

Add TechCrunch RSS (`https://techcrunch.com/feed/`) as SquadScope's first non-GitHub data source, implementing Decision #7's crawler plugin architecture.

**Rationale:**
1. Cross-source correlation enables hype detection (press-driven vs. organic growth)
2. Near-zero cost and complexity (public RSS, no auth, no rate limits)
3. Directly implements the `DataSource` plugin pattern already approved
4. Enriches editorial judgment without changing SquadScope's voice or pipeline structure

**Impact:**
- **Bender:** Implements `TechCrunchSource` crawler plugin
- **Farnsworth:** Analyzer prompt gains press-context block; labels repos as press-correlated or organic
- **Amy:** Optional correlation badge in Hugo templates
- **Leela:** No architectural changes needed; plugin arch already designed for this

### Open for Team Input

- Should we start with full feed or category-specific feeds?
- Correlation annotations: reader-visible or internal-only?

---

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

---

## Decision: Manual W21 content regeneration (2026-05-19)

**Author:** Bender
**Status:** Executed

### Context

The crawl-and-publish workflow (run #26109935234) generated W21 analysis but failed to commit it because the commit step tried to push directly to `main`, which requires PRs (branch protection). PR #123 fixed the workflow to use PR-based commits, but it merged after the failed run.

### Decision

Regenerated W21 content manually and created PR #125 to update the page. No workflow code changes needed — the root cause (direct push) was already fixed by PR #123.

### Impact

- `content/weekly/2026/W21.md` updated from stale manual dry-run to full analysis
- Monthly/yearly rollups refreshed
- Once PR #125 merges, deploy-site will publish the updated page
- Future scheduled runs will use the PR-based approach and should not hit this again

---

## Decision: PR #126 Security Review — Clear (2026-05-19)

**Author:** Hermes (Security)
**PR:** #126 — "feat: wire TechCrunch RSS into CI pipeline and add API retry backoff"

### Decision

PR #126 is **security-clear**. No blocking vulnerabilities found.

### Key Findings

- No SSRF risk (hardcoded feed URL)
- Retry logic properly bounded (3 retries, exponential backoff + jitter)
- No secrets leaked in logs
- feedparser dependency is well-maintained, no CVEs
- Workflow permissions unchanged

### Non-blocking Recommendation

RSS content fed into AI prompts has a theoretical indirect prompt injection surface. Mitigated by HTML stripping and content truncation. Recommend adding control character sanitization in a future PR for defense-in-depth.

### Impact

Team can merge PR #126 without security holds.

---

## Decision

The divergence section in `format_divergences()` now renders as narrative prose when `reader_mode=True`, replacing the prior bullet list format. AI-prompt mode (`reader_mode=False`) is unchanged.

## Rationale

Raw topic-and-repo bullet lists communicate data but not meaning. Readers gain more from a paragraph that groups activity, links to repos by short name, and closes with an interpretive sentence. The AI model still needs the full structured data — so the dual-mode architecture cleanly separates the two use cases.

## Format Decisions

1. **Repo links:** `[repo-name](https://github.com/owner/repo-name)` — repo name only (after `/`), never `owner/repo (⭐N)`.
2. **Article links:** `[title](url)` — standard markdown.
3. **Topic capping:** Top 6 topics by aggregate star count for "Dev Activity Without Press Coverage"; top 5 for "Tech Trends Without Dev Activity".
4. **Structure:** Two named helpers — `_format_unpublicized_narrative()` and `_format_uncovered_narrative()` — keep the logic isolated and independently testable.

## Context

The CI pipeline falls to the no-AI path when the AI API is unavailable. In that path, `_render_press_section_no_ai()` was reading the pre-rendered `data/analyzed/{WEEK}-press-context.md` and stripping AI instructions to produce reader output.

The problem: that file is generated in AI-prompt mode (`reader_mode=False`). The narrative divergence format introduced in PR #136 is only produced when `reader_mode=True`. So the no-AI path always showed the old bullet-list format regardless of code changes in the reader-mode rendering path.

## Decision

**Re-render from raw JSON data in the no-AI path.** Specifically:

1. Extract the week identifier from the `press_context_path` filename stem.
2. Load `data/raw/{WEEK}-techcrunch.json` and `data/analyzed/{WEEK}-correlations.json`.
3. Call `render_press_context(tc_data, corr_data, week, reader_mode=True)`.
4. If raw files are absent, fall back to the existing strip-based approach.

## Rationale

- The pre-rendered press-context.md is an AI prompt artifact, not a reader artifact. It must not be the source of truth for reader-facing output.
- Raw JSON files are always present when the CI pipeline runs (they are produced earlier in the same pipeline run).
- The fallback ensures backward compatibility for edge cases (manual script invocations against older data).

## Impact

- The no-AI CI path now uses identical rendering logic to the AI path's fallback output.
- Any future changes to `render_press_context(..., reader_mode=True)` automatically apply to the no-AI path without further changes.
- The W21 page will show the correct narrative format on the next pipeline run.

## Context

The Correlation Summary section was showing a raw bullet list of repo names, confidence scores, and match types — useful for AI prompt consumption but meaningless to human readers. The Divergence section had already been upgraded to narrative prose (PR #131). This decision extends that pattern to correlations.

## Decision

When `reader_mode=True`, `format_correlations_list()` delegates to `_format_correlations_narrative()` which:

1. **Groups correlations by org** (first path segment of owner/repo). This is the natural unit of press coverage — TechCrunch writes about organizations, not individual repos.
2. **Ranks groups by aggregate confidence score** (sum of correlation_confidence across all repos in the group).
3. **Fetches README snippets** (first 500 chars) for the top 2 repos per group, up to 6 total, using `urllib.request` with a 5-second timeout and graceful failure. This enables project descriptions in the narrative (e.g., "Guava is a set of core Java libraries from Google").
4. **Produces 1–3 paragraphs** with inline links to repos (short name, e.g., `[codex](https://github.com/openai/codex)`) and matched TechCrunch articles (full title as link text).

## Alternative Considered

**No README fetching — use only repo names**: simpler and fully deterministic, but produces flat prose with no editorial context about what the repos actually do. The README fetch adds signal at low cost (max 6 network requests, fails gracefully).

## Context

The CI pipeline runs AI analysis (Copilot CLI) and reskill (GitHub Models API) but neither job leverages the squad agent system. The analysis agent has no identity, cannot read its own history/skills, and has no mechanism to write learnings back. The reskill job bypasses Copilot CLI entirely and uses a model (`openai/gpt-4.1`) that returns 403.

## Decisions

### 1. Dedicated Farnsworth Agent File (`.github/agents/farnsworth.agent.md`)

A standalone agent file gives the Copilot CLI the full Farnsworth identity — charter, history reading instructions, post-analysis learning format, and write permissions to `.squad/`.

**Rationale:** The `--agent` flag loads an agent markdown file with YAML frontmatter and instructions. A dedicated file allows CI-specific directives (learning output format, file write permissions) without polluting the interactive Squad coordinator agent.

### 2. `--agent` Flag in Copilot CLI Invocations

Both the analysis and reskill jobs now use:
```bash
copilot --agent .github/agents/farnsworth.agent.md ...
```

**Rationale:** This loads Farnsworth's identity, making the CLI aware of the agent's history, wisdom, skills, and learning expectations.

### 3. Learning Commit Strategy: Same Branch, Same Job

After analysis, `.squad/` changes (history, skills) are committed alongside `data/analyzed/` to the `publish` data branch in a single atomic commit.

**Rationale:** No additional branch/PR overhead. The data branch is unprotected and already receives CI commits. Learnings are part of the analysis artifact — they should be co-located temporally. The reskill job already commits `.squad/` state via the same pattern.

### 4. Model Fallback: `openai/gpt-4o` Replaces `openai/gpt-4.1`

The default model for GitHub Models API fallback is changed from `openai/gpt-4.1` (which returns 403) to `openai/gpt-4o` (widely accessible).

**Rationale:** `gpt-4.1` is not accessible via the GitHub Models API for this repository's token. `gpt-4o` is the current generally available model. The env var `GITHUB_MODELS_MODEL` still allows override.

### 5. Reskill Primary Path: Copilot CLI with Agent

The reskill job now tries Copilot CLI first (with agent identity), falling back to GitHub Models API if CLI is unavailable. This gives reskill the same agent-aware capabilities as analysis: read wisdom/skills/history, write updated wisdom and learnings back.

**Rationale:** The reskill cycle is the primary mechanism for reinforcing the learning loop. With agent identity, it can directly update `wisdom.md` and `history.md` based on retrospective findings — the core of self-improvement.

### 6. Prompt Template Unchanged

The existing prompt templates (`prompts/analyze-weekly.md`, `prompts/reskill.md`) already inject wisdom and skills via `{{WISDOM}}` and `{{SKILLS}}` placeholders. The agent file complements this by providing identity context and learning output instructions that the templates alone cannot express.

## Risks

| Risk | Mitigation |
|------|-----------|
| Agent writes bad content to `.squad/` files | Quality gate still runs on analysis output; .squad changes are append-only learnings |
| Copilot CLI doesn't support `--agent` as expected | Fallback path (GitHub Models via reskill.py) still works without agent identity |
| Learning state diverges between publish branch and main | Periodic sync PRs already exist; learnings on publish are forward-compatible |

## Implementation

- [x] `.github/agents/farnsworth.agent.md` — agent identity file
- [x] `.github/workflows/crawl-and-publish.yml` — `--agent` flag, learning commits, model fix
- [x] `scripts/reskill.py` — model default updated to `openai/gpt-4o`
- [x] `scripts/analyze_fallback.py` — model default updated to `openai/gpt-4o`

---

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction

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

## Context

Copilot CLI model IDs can disappear from the platform, causing silent degradation to fallback paths.

## Decision

The `crawl-and-publish.yml` workflow should never pass a version-pinned `--model` flag. Analysis and reskill rely on the CLI's platform default, while GitHub Models fallback uses `openai/gpt-4o` (configurable via `GITHUB_MODELS_MODEL`).

## Rationale

Pinned model IDs can silently disappear; letting the CLI choose its default keeps the primary path available without manual model churn.

## Context

Published week 21 article leaked agent status text because shell appended Copilot CLI stdout to the markdown file after Farnsworth had already written the real article.

## Decision

In `crawl-and-publish.yml`, Copilot CLI stdout must never redirect to the same markdown file the agent writes. Analysis and reskill invocations send stdout to `/dev/null`, rely on `--share` or workflow logs for transcripts, and run a post-write sanitizer for defense in depth.

## Rationale

Separates channels (fixes root cause) and reduces blast radius if CLI emits metadata again.

## Context

Audit found repeated charter scaffolding, duplicated rollout updates in histories, and mature workflow knowledge scattered across multiple agent files.

## Decision

Squad agent docs follow a shared minimal-charter and history-hygiene model. Shared operating patterns move into `.squad/skills/`, while charters keep only: identity, ownership, working style, boundaries, and model preference.

## Rationale

- Eliminates redundant documentation
- Preserves workflow knowledge as reusable skills
- Reduces agent charter bloat

## Context

Week 21 analysis requires both editorial quality and automation compliance. The title and press-fallback handling must satisfy both reader expectations and the analyzer contract.

## Decision

Week 21 analysis should use a journalistic title, not a generic week label, and must keep the no-press fallback explicit when press data is absent.

## Rationale

The published analysis needs to read like an editorial artifact and satisfy the analyzer contract at the same time. A headline plus explicit press fallback keeps the page useful to readers and safe for automation.

## Context

When rebuilding data for a previous week, the workflow must NOT re-run the crawl. Re-crawling pollutes prior weeks' data (overwrites the high-quality version with a fresh, possibly worse snapshot). User repeatedly lost high-quality W21 analysis because re-runs re-crawled and re-analyzed, regenerating inferior versions.

## Directive

For previous-week rebuilds:
1. Hydrate from `publish` (canonical source for analyzed content)
2. Re-run analysis/generation only as needed
3. **Never crawl again** for previous weeks

This restores/regenerates from existing data without polluting the archive.

## Implementation Status

- Captured in PR #164 (bender-3): deploy-site.yml now hydrates content/data from publish before hugo build
- Schedule event guard fixed: `!inputs.rebuild_week` instead of `== ''` ensures cron doesn't skip
- Format validation added for YYYY-WNN rebuild_week parameter
- Architectural fix prevents main/publish divergence

**Files affected:** `.github/workflows/deploy-site.yml`, `.github/workflows/crawl-and-publish.yml`

### 2026-05-18T16:22:40Z: User directive
**By:** jmservera (via Copilot)
**What:** When the Hugo deployment fails, automatically create a GitHub issue so the squad can decide to fix it or dismiss it as transient. The squad should think thoroughly about whether an issue truly needs a human before escalating.
**Why:** User request — ensures deploy failures don't go unnoticed and the team self-triages problems.

### 2026-05-18T12:57:06Z: User directive
**By:** jmservera (via Copilot)
**What:** To merge a PR, all review conversations must be fixed AND resolved first. Agents must resolve each conversation thread (not just push fixes) before a PR can be merged.
**Why:** User request — reinforcement of PR review workflow. GitHub blocks merge when conversations are unresolved.
# Decision Inbox: Learning System Audit Findings

**Author:** Leela (Lead/Architect)  
**Date:** 2026-05-18T13:20:07.067+02:00  
**Type:** Audit findings requiring team action  
**Related:** Issues #14, #15; docs/learning-audit.md

## Summary

Comprehensive audit of the learning system reveals that SquadScope's main differentiator — learning over time — is currently design-only. Zero implementation exists. The full gap analysis is in `docs/learning-audit.md`.

## Decisions Needed

### 1. Prompt Feedback Loop (New Issue Required)

**Problem:** `prompts/analyze-weekly.md` has no mechanism to inject learned wisdom or skills. Even if reskill produces insights, they never reach the analyzer.

**Proposed fix:** Add `{{WISDOM_CONTENT}}` and `{{SKILLS_CONTENT}}` template variables; update `scripts/analyze_fallback.py` to read and inject `.squad/identity/wisdom.md` and `.squad/skills/` content.

**Impact:** Without this, learning has literally no effect on analysis quality.

### 2. Reskill Output Governance

**Question:** Should reskill commit directly to main, or produce a PR for human review?

**Leela's recommendation:** PR-based for prompt/spec changes; direct commit for `.squad/reskill/` reports and `run-counter.txt`.

### 3. New Issues to Create

Three gaps require issues beyond #14 and #15:
- Prompt feedback loop (G7)
- Hindsight validation script (G8)
- Prediction registry format (G9)

**Assignee recommendation:** Farnsworth for all three (owns analysis and reskill domain).

## Action Items for Existing Issues

- **Issue #15 (Bender):** Must include counter initialization, increment in commit step, and `.squad/run-counter.txt` in git add paths.
- **Issue #14 (Farnsworth):** Must create `.squad/skills/`, `.squad/reskill/`, seed `wisdom.md`, write structured `prompts/reskill.md`, and add `.squad/` commit step to workflow.

---

# Directive: Prevent Recrawl on Previous-Week Rebuilds

**Date:** 2026-05-25T15:55:00+02:00  
**Source:** User directive (jmservera via Copilot)  
**Status:** Active

## Active Decisions

---

# AI Disclosure Pattern

**Date:** 2026-05-25  
**Author:** Amy  
**Status:** Proposed  

Every page renders an AI-disclosure footer partial; article pages additionally show a prominent AI-generated badge in the meta block. Single partial = single source of truth.

---

# Amy — Cookie Consent vendoring

Date: 2026-05-25

Decision: vendor Cookie Consent v3 directly in `static/vendor/cookieconsent/` and pin it to upstream version `v3.0.1`.

Rationale:
- Cookie consent must run before optional analytics scripts are activated.
- Vendoring avoids relying on the jsDelivr CDN at runtime.
- The pinned files are the published `dist` CSS and UMD bundle from `orestbida/cookieconsent@v3.0.1`.

Checksums:
- `cookieconsent.css`: `sha256 ca046b8b1b1094107205988e7096a687b241c8ef5f3fefe5e543ed28d26646c1`
- `cookieconsent.umd.js`: `sha256 1267fd33fcf3ab4043a7cc62cc9259a2c66f839f695216f7737ed37b7b3e62e6`

---

# Article errata schema

**Date:** 2026-05-25  
**Author:** Amy  
**Status:** Proposed

## Decision

Articles declare corrections in front-matter using `errata: [{date, note}]`; the article footer renders those entries at the end of the article.

## Schema example

```yaml
errata:
  - date: 2026-05-26
    note: "Corrected the company name in the EU AI Act section (was 'Mistral.ai', now 'Mistral AI')."
```

## Rationale

Keeping corrections in front-matter makes the article-level errata path data-driven, reviewable in Git, and visible to readers without requiring silent edits to published analysis.

---

# Home hero restructure

**Date:** 2026-05-25  
**Author:** Amy (Frontend Engineer)  
**Status:** Proposed

## Decision

Home page is a publication front page — the latest weekly analysis IS the hero. Explainer lives at `/about/`.

---

# Amy Phase 1 Design Foundation Implementation

**Date:** 2026-05-25  
**Author:** Amy (Frontend Developer)  
**Status:** Implemented

## Decision

Phase 1 tokens and typography are implemented as a Hugo asset-pipeline foundation without changing page layouts.

## File locations

- `assets/css/tokens.css` is the design-system entry point for color, type, spacing, radius, shadow, and line-height tokens.
- `layouts/partials/head.html` loads Inter and JetBrains Mono from Google Fonts using preload + stylesheet links, then includes `tokens.css` before the PaperMod-compatible CSS bundle.
- `assets/css/core/theme-vars.css` maps PaperMod legacy variables to SquadScope tokens so existing templates continue to render.
- `assets/css/core/reset.css` applies the base reset, body typography, heading scale, and monospace stack.
- `assets/css/common/*.css`, `assets/css/extended/squadscope.css`, and `assets/css/badges.css` consume the token aliases while preserving existing layouts.

## How to extend

Future phases should add new tokens to `assets/css/tokens.css` first, then consume them through component or layout CSS. Keep semantic tokens stable (`--color-*`, `--text-*`, `--space-*`) and add component-specific variables only when a pattern repeats across multiple publishing surfaces.

## Gotchas

PaperMod lives as a submodule, so theme CSS changes should be copied into root-level `assets/css/` overrides rather than editing `themes/PaperMod` directly. Hugo resolves these project assets through the existing asset pipeline while leaving the third-party theme clean.

---

# Amy Phase 2 Implementation Notes

Date: 2026-05-25
Author: Amy
Status: Implemented in PR branch

## Decisions

- Override PaperMod chrome at the project layer (`layouts/partials/header.html`, `layouts/partials/footer.html`) rather than editing the theme submodule.
- Add `layouts/_default/baseof.html` solely to place the skip-to-content link before the cached header and give the main landmark `id="main-content"`.
- Keep the primary nav intentionally scoped to Weekly, Monthly, Yearly, and About for Phase 2; archive/search/taxonomy links remain in the page body and footer where already present.
- Use a native `<details>` disclosure for mobile navigation so the collapsed menu remains keyboard reachable without adding new JavaScript.

## Implications

Future chrome work should continue to extend root layouts and tokenized CSS. If PaperMod changes its base template, compare against this override before upgrading the theme.

---

# Decision: GA4 fork-safe secret injection

**Date:** 2026-05-25T22:30:00+02:00  
**Author:** Bender (Crawler/CI)  
**Status:** Proposed

## Context

SquadScope needs GA4 analytics for the upstream site, but forks must not silently report traffic to the maintainer's GA property. Repository secrets are not inherited by forks, so analytics must depend on an explicitly provided secret and render nothing when absent.

## Decision

Use a secret-default-empty pattern: Hugo config defines `params.ga_measurement_id = ""`, while the Pages deploy workflow injects `${{ secrets.GA_MEASUREMENT_ID }}` through `HUGO_PARAMS_GA_MEASUREMENT_ID`. Hugo maps that environment key to `params.ga.measurement.id`, and the analytics partial renders GA4 only when either config path is non-empty. The rendered scripts are marked with `data-cc-category="analytics"` so Cookie Consent v3 can load them only after analytics consent.

## Rationale

The empty config default is safe for forks and local builds. The environment override keeps the maintainer measurement ID out of source control while still enabling analytics in the upstream deployment. Consent-category script tagging keeps analytics dormant until the consent integration activates the analytics category.

## Impact

- Upstream deploys can enable GA4 by setting `GA_MEASUREMENT_ID`.
- Forks build without analytics by default.
- Maintainers can opt out by deleting the secret.
- Cookie consent integration can activate the tagged scripts without changing the GA4 partial.

---

# Decision: Journalistic shell baseline

**Date:** 2026-05-25T23:31:03+02:00  
**Owner:** Calculon  
**Status:** Proposed

## Decision

The journalistic shell is a non-negotiable baseline for SquadScope. Navigation density, search, weekly archive access, and topic shortcuts must remain present in future home-page cleanups.

## Rationale

jmservera rejected the PR #205 revision because it over-pruned the publication shell. Future cleanups may relocate explanatory body content, but they must not remove the publication affordances that make the site feel like an editorial front page.

## Implications

- Keep top-level access to all weeks, topics, and search.
- Keep a home-page rail or equivalent surfacing active topics and recent issues.
- Preserve `/about/` as the home for the explainer and transparency dashboard.

---

# Design Direction: Editorial Trend Report

**Date:** 2026-05-25  
**Author:** Calculon (Designer)  
**Status:** Proposed

## Decision

**Visual Direction:** Editorial Trend Report — Dense but Quiet

This positions SquadScope as a credible, opinionated weekly briefing rather than a generic blog or SaaS dashboard. Typography carries the design; images and color accents are supporting actors.

## Rationale

After studying GitHub Pulse, TechCrunch, Wired, and The Verge:
- GitHub Pulse is too dashboard-like for editorial content
- TechCrunch provides good headline hierarchy but is too news-feed
- Wired is too image-dependent for text-first analysis
- The Verge shows density can work if hierarchy is clear

SquadScope is closer to a weekly briefing document than any of these. The design borrows TechCrunch's reading rhythm, GitHub Pulse's monochrome discipline, and The Verge's willingness to be dense — while avoiding their weaknesses.

## Token Summary

**Palette:** Monochrome foundation with single accent (#0066CC light, #4DA3FF dark). All combinations WCAG AA verified.

**Typography:** Inter system stack for headlines and body. JetBrains Mono for code. Type scale from 0.75rem (tiny) to 2.25rem (h1). Optimal prose measure 68ch.

## Phase Plan

1. Tokens + Typography Foundation
2. Header + Footer + Navigation
3. Home Page Layout
4. Article Layout + Components
5. Cost Dashboard Refresh
6. Icon + Favicon + Social Images

Each phase ships independently. Tokens must land first; other phases have light dependencies.

## Icon

Radar sweep concept — concentric circles with sweep line and signal blip. Represents continuous scanning. Hand-coded SVG, no external fonts, under 2KB. Uses currentColor for automatic mode adaptation.

## References

- `docs/design/redesign-proposal-2026-05.md`
- `docs/design/icon-spec.md`
- Issues #170-#177

---

# Source-selection methodology disclosure

- **Date:** 2026-05-25
- **Owner:** Farnsworth
- **Status:** Proposed for merge

## Decision

Source-selection biases are publicly disclosed at `/methodology/`; updates to scoring, source ingestion, crawl thresholds, or press coverage should be reflected there.

## Context

Nibbler's second responsible-AI sweep identified source-selection bias disclosure as a high-severity fairness and transparency gap. The methodology page gives readers a plain-English explanation of source inputs, ranking logic, and interpretation limits.

## Consequences

- Pipeline changes that alter source mix or scoring should include a reader-facing methodology update.
- Future bias metrics can link back to `/methodology/` as the stable disclosure surface.

---

# BaseURL-aware links in data files

Date: 2026-05-25
Owner: Hermes

## Decision

Links inside `data/*.json` files must use `__TOKEN__` placeholders substituted by partials with Hugo URL helpers; never hardcode `/path/` prefixes inside data files.

## Rationale

SquadScope is currently deployed on GitHub project Pages under `/SquadScope/`, so root-relative links such as `/privacy/` resolve outside the site and can 404. If the site later moves to an apex/custom domain, Hugo URL helpers will render the same logical route correctly without changing legal-copy JSON.

## Implementation note

For cookie-consent copy, `data/cookieconsent.json` uses `__PRIVACY_URL__`, and `layouts/partials/cookie-consent.html` replaces it with `"privacy/" | relURL` before initializing Cookie Consent.

---

# Hermes Privacy Policy v1

Date: 2026-05-25
Author: Hermes (Security & Legal)
Status: Proposed

## Decision

GA4 is our ONLY analytics; no first-party tracking.

## Context

SquadScope is a static editorial trend-analysis site with no accounts, signup, comments, contact form, or newsletter. The site is hosted on GitHub Pages and uses a cookie consent banner before analytics can run.

## Consequences

- SquadScope must not add first-party visitor profiling, server-side personal-data storage, or additional analytics tools without a new privacy review.
- GA4 must remain consent-gated behind the analytics cookie category.
- Privacy disclosures should continue to identify GitHub Pages hosting logs, GA4, Google Fonts if used, and the essential consent cookie.

---

# Prompt Injection Hardening for Analysis Prompts

**Date:** 2026-05-25
**Author:** Hermes
**Status:** Proposed

## Context

Nibbler's RAI audit identified user-controlled GitHub repository descriptions entering the weekly analysis prompt through `{{RAW_JSON_CONTENT}}`. A malicious repo description can contain prompt-injection text that attempts to override Farnsworth's editorial instructions.

## Decision

Apply a layered OWASP LLM01 defense for analyzer prompt rendering:

1. Mark raw crawl JSON as untrusted data with explicit `<untrusted-content>` boundaries.
2. Sanitize repository descriptions before prompt rendering by stripping leading whitespace, escaping boundary-closing tags, truncating long text, and warning on common prompt-injection phrases.
3. Add output guardrails telling the analyst to stop on unsupported claims and avoid verbatim descriptions containing meta-instructions.
4. Repeat the editorial mission after the untrusted content so late prompt text reinforces trusted instructions.

## Consequences

The analyzer keeps using the same editorial structure, but prompt provenance is clearer and repository descriptions have bounded influence. Suspicious descriptions are logged and truncated rather than blocked to avoid false positives disrupting publication.

---
