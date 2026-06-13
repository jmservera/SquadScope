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

Date: 2026-06-01

## Context
Issue #217 showed the weekly analysis job can fail even when crawl data is healthy because Copilot sometimes returns a generic placeholder title or no output file at all after retries.

## Decision
Keep Copilot CLI as the primary analysis generator, but if its output still fails the quality gate after retries, immediately fall back to `scripts/analyze_fallback.py` via GitHub Models. Also render the prompt with concrete `week`, `year`, and title guidance so the model is less likely to echo placeholder frontmatter.

## Rationale
This keeps the higher-quality primary path, but removes CI flakiness from transient Copilot failures and from prompt placeholders leaking into the final markdown.

---

Date: 2026-06-01

## Context
Issue #217 showed the weekly analysis job can fail even when crawl data is healthy because Copilot sometimes returns a generic placeholder title or no output file at all after retries.

## Decision
Keep Copilot CLI as the primary analysis generator, but if its output still fails the quality gate after retries, immediately fall back to `scripts/analyze_fallback.py` via GitHub Models. Also render the prompt with concrete `week`, `year`, and title guidance so the model is less likely to echo placeholder frontmatter.

## Rationale
This keeps the higher-quality primary path, but removes CI flakiness from transient Copilot failures and from prompt placeholders leaking into the final markdown.

---

Date: 2026-06-01

## Context
Issue #220 showed the crawl-and-publish workflow could finish crawl and analysis successfully, then fail in the generate handoff because the generated weekly page path was absolute while the publish-branch restore logic assumed a repository-relative path. The same workflow also lacked a failure-to-issue bridge, so repeated pipeline failures did not automatically open or update a GitHub issue.

## Decision
Normalize `page_path` to a repo-relative `content/weekly/...` path inside the generate commit step before copying weekly output onto the publish branch. Add a dedicated `notify-failure` job that always evaluates after the pipeline jobs and creates or updates a GitHub issue whenever any crawl/analyze/generate/deploy/notify job fails.

## Rationale
The path normalization fixes the actual handoff bug without changing `scripts/generate_content.py`, which already returns an absolute file path used elsewhere in tests. A separate failure notifier makes regressions visible even when later jobs are skipped, which is the exact reliability gap that hid the recent failures.

---

Date: 2026-06-01

## Context
Issue #226 adds article-level sharing. PaperMod already ships a share-buttons partial, but SquadScope also needs mobile-native sharing through the Web Share API and token-aligned styling.

## Decision
Enable PaperMod share support through `hugo.toml` (`params.ShowShareButtons` plus an explicit `params.ShareButtons` allowlist), then override `layouts/partials/share_icons.html` in the project to add a mobile-only native share button while keeping desktop fallback links for X, LinkedIn, and Facebook. To keep the site buildable with the current PaperMod submodule layout, vendor the theme partials the site already relies on into `layouts/partials/` instead of editing the theme.

## Rationale
This keeps the third-party theme submodule untouched, reuses the existing article-footer insertion point, and scopes the share customization to a project-level partial plus tokenized footer styles. Vendoring the required PaperMod partials also makes the build deterministic for SquadScope without depending on theme-internal `_partials` resolution quirks.

---

Date: 2026-06-01

## Decision
Use an optional `predictions` frontmatter registry on weekly analysis summaries with entries shaped as `{repo, direction, confidence}`.

## Why
The published markdown is already the durable editorial artifact, so embedding prediction intent there avoids a separate ledger drifting out of sync. Legacy summaries still need heuristic extraction from Signal/Noise/Gaps prose, but future summaries should register explicit repo-level calls for cleaner hindsight scoring.

## Operational note
The validator writes a human scorecard to `.squad/reskill/scorecards/YYYY-WNN.md` and a machine-readable companion to `data/metrics/scorecards/YYYY-WNN-scorecard.json` so the current reskill tooling can ingest the same run.

---

Date: 2026-06-01

## Context
Issue #220 showed the crawl-and-publish workflow could finish crawl and analysis successfully, then fail in the generate handoff because the generated weekly page path was absolute while the publish-branch restore logic assumed a repository-relative path. The same workflow also lacked a failure-to-issue bridge, so repeated pipeline failures did not automatically open or update a GitHub issue.

## Decision
Normalize `page_path` to a repo-relative `content/weekly/...` path inside the generate commit step before copying weekly output onto the publish branch. Add a dedicated `notify-failure` job that always evaluates after the pipeline jobs and creates or updates a GitHub issue whenever any crawl/analyze/generate/deploy/notify job fails.

## Rationale
The path normalization fixes the actual handoff bug without changing `scripts/generate_content.py`, which already returns an absolute file path used elsewhere in tests. A separate failure notifier makes regressions visible even when later jobs are skipped, which is the exact reliability gap that hid the recent failures.

---

Date: 2026-06-01

## Decision
Use an optional `predictions` frontmatter registry on weekly analysis summaries with entries shaped as `{repo, direction, confidence}`.

## Why
The published markdown is already the durable editorial artifact, so embedding prediction intent there avoids a separate ledger drifting out of sync. Legacy summaries still need heuristic extraction from Signal/Noise/Gaps prose, but future summaries should register explicit repo-level calls for cleaner hindsight scoring.

## Operational note
The validator writes a human scorecard to `.squad/reskill/scorecards/YYYY-WNN.md` and a machine-readable companion to `data/metrics/scorecards/YYYY-WNN-scorecard.json` so the current reskill tooling can ingest the same run.

---

Date: 2026-06-05

## Decision

Keep external RSS/news in the existing crawl job with bounded in-process parallelism, but promote the handoff to a canonical `schema_version: 2` `data/raw/{week}-external-news.json` artifact. The artifact carries crawl window, source config checksum, requested/succeeded/failed sources, per-source status metrics, dedupe count, deterministic checksum, and partial-failure metadata.

## Rationale

The measured bottleneck remains the GitHub repository crawl, not the five-source RSS step. Source-aware telemetry and schema validation improve downstream reliability without adding Actions matrix startup overhead or splitting cache/API behavior.

## Operational notes

`correlate.py` and `render_press_context.py` now preserve article source/title/date/URL citations, label strong versus weak correlations, bound press context size to an ~8k token estimate, and keep legacy `*-techcrunch.json` and no-press fallbacks.

- PR #242 merged at 2026-06-05T17:24:14Z, closing issue #237.

---

Date: 2026-06-05T15:36:19.379+00:00

## Decision

The crawl-and-publish analysis stage should degrade to a data-only no-AI weekly summary when both Copilot output and GitHub Models output are unavailable or rejected by the quality gate.

## Rationale

A missing or unauthorized model is an operational dependency failure, but the pipeline still has verified crawl data. Publishing a clearly labeled data-only summary is more reliable than failing the entire weekly handoff after preserving no reader-facing output.

## Follow-up

If model access is restored, the AI analysis path remains preferred. The no-AI path is only a terminal fallback after Copilot and GitHub Models fail.

---

Date: 2026-06-05T15:36:19.379+00:00

**By:** Leela

## Decision

Issue #188 was closed as obsolete/unverifiable rather than reconstructed or rerouted. W23 draft files under `.squad/posts/`, the requested `.squad/metrics/2026/w23-distribution.md`, and platform posting evidence were absent from the working tree, git history, related issues, and PR context. PR #190 and `docs/growth/distribution-strategy.md` only provide the launch strategy/template, not the W23 execution artifacts.

## Rationale

Recreating social posts and metrics after the distribution window would create misleading evidence. Future growth execution issues should remain open until artifact-backed proof exists, or be closed explicitly when the posting window expires without evidence.

---

Date: 2026-06-05T15:36:19.379+00:00

PR #236 keeps RSS enrichment in the existing crawl job with bounded in-process parallel fetching instead of separate Actions jobs.

QA verified the diff covers config loading, multi-source crawl aggregation, metadata/errors, legacy `*-techcrunch.json` fallback, correlation handoff, press-context resolution, and rebuild hydration.

Validation run in an isolated PR worktree:
- `PYTHONPATH=. .venv/bin/python -m pytest tests -q` → 554 passed
- Live RSS smoke with `--max-workers 5` → 54 articles from 5 sources, no feed errors

Verdict: approve; no follow-up implementation owner required.

---

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

Date: 2026-06-05T15:36:19.379+00:00
Issue: #234

## Decision

Keep external news crawling in the existing crawl job and make the RSS source list config-driven via `config/external_news_sources.json`. Fetch the configured feeds concurrently inside `scripts/techcrunch_crawler.py` using a bounded thread pool, and write one weekly enrichment artifact: `data/raw/YYYY-WNN-external-news.json`.

## Rubberduck tradeoff

Separate GitHub Actions jobs would parallelize at the runner level, but every source would repeat checkout, Python setup, dependency install, artifact upload/download, and failure-handling boilerplate. For five RSS feeds, that overhead is larger than the network wait we are optimizing away, and it would fragment a single enrichment contract across multiple artifacts.

In-process threading matches the current architecture better: RSS fetching is I/O-bound, feedparser work is light, and the existing crawl job already owns raw data artifact handoff. A bounded pool preserves Actions compute, keeps one failure surface, and lets future sources be added by config without editing workflow topology.

## Scope boundary

This is a small architectural refactor around an existing RSS crawler, so Leela implemented directly rather than reassigning to Bender. Deeper crawler work, such as source-specific parsing, feed health dashboards, or correlation logic, should remain Bender-owned.

---

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

Date: 2026-06-05T17:11:29.929+00:00
Issue: https://github.com/jmservera/SquadScope/issues/238
Run: https://github.com/jmservera/SquadScope/actions/runs/27026348186

## Finding

The pipeline stages that produce and publish data succeeded. The only failed job was `notify`, where `gh release create week-2026-W23` returned HTTP 422 because the `week-2026-W23` release already existed.

## Decision

Treat this as a real QA-owned workflow idempotency bug, not a transient network or rate-limit failure. Weekly notify must be safe to rerun for an already-published week.

## Fix

Update the notify release step to check for the weekly release tag. If it exists, edit the existing release title/notes and mark it latest; otherwise create it as before.

## Validation

- `PYTHONPATH=. .venv/bin/python -m pytest tests/test_pipeline.py -q` — 9 passed.
- `PYTHONPATH=. .venv/bin/python -m pytest tests -q` — 563 passed after installing project requirements and pytest in a local venv.

---

Date: 2026-06-05T17:42:56Z
Requested by: jmservera
Scope: PRD-ready findings for Leela; no code or issue created.

## Recommendation

Keep the last implementation decision for now: GitHub crawl stays monolithic, and external RSS/news stays bounded in-process. The measured bottleneck is still the GitHub repository crawl, while RSS/news is already parallelized inside one job and completes in about one second for five feeds.

Introduce a matrix only behind measured gates, and prefer a staged fan-out/fan-in design over directly feeding matrix outputs to analysis. If the goal is smaller LLM context, solve that in the analysis handoff with deterministic map/reduce summaries rather than splitting API collection first.

## Why matrix was not used last time

The prior decision was evidence-based:

- Old crawler job `26753498571 / 78847225991`: crawl job ~6m23s; `Run crawler` ~5m58s.
- New crawler job `27026348186 / 79767247136`: crawl job ~5m08s; `Run crawler` ~4m47s; external RSS step ~1s.
- Current observed run `27030646485 / 79781846313`: crawl job ~4m50s; `Run crawler` ~4m30s; external RSS step ~1s.
- RSS fan-out would add repeated checkout/setup/artifact overhead that is larger than the current RSS work.
- GitHub crawl uses one shared cache, one shared token/rate-limit view, one star snapshot, and one deterministic output. Splitting it before measuring shard behavior risks API thrash and merge bugs.

This decision still holds unless the measured gates below fire.

## Parallelizable work

### GitHub repository crawl

Parallelizable in theory:

- Search query pages (`created:` new repos, `pushed:` trending repos, topic config primary/secondary queries).
- Candidate filtering and repository normalization.
- README existence checks.
- Star snapshot construction after shard outputs are merged.

Not safely parallelizable without coordination:

- GitHub search quota management. Search quota is much tighter than core quota; previous issue context observed search remaining near `24/30` while core stayed around `4450+/5000`.
- Secondary rate limit backoff and cooling. More jobs can make the aggregate request rate worse.
- Cache writes unless each shard has an isolated cache namespace and a deterministic post-merge cache artifact.
- Trending star-gain computation until all candidates and the prior snapshot are available.

### External RSS/news

Parallelizable today and already done in-process:

- Per-feed fetch and parse via `ThreadPoolExecutor`, capped at 8 workers.
- Per-source status telemetry, partial failures, and deterministic source ordering.

Good matrix candidate later:

- Per-source crawl jobs when source count grows, source p95 gets slow, or source-specific retries/credentials/network failures need isolation.

### Correlation / press context / analysis

Parallelizable for context reduction:

- Correlation can map over repo shards against the same bounded article set, then reduce ranked correlations and divergences.
- LLM analysis can map over normalized slices such as `new_repos`, `trending_repos`, `press_correlations`, and `divergences`, then reduce to the final weekly summary.

Requires strict contracts because final analysis must remain deterministic, citation-preserving, and bounded.

## Matrix design options

### Option A — RSS per-source matrix

Design:

1. A setup job computes `week`, `since`, `until`, and the source list from `config/external_news_sources.json`.
2. Matrix job runs one source per leg and emits `external-news-source-{source}.json`.
3. Fan-in job downloads all source artifacts, validates schema/checksums, dedupes articles, computes canonical `data/raw/{week}-external-news.json`, and uploads raw data for analyze.

Pros:

- Best failure isolation for flaky feeds.
- Easy per-source retries.
- Simple ownership and telemetry.

Cons:

- Slower than current state for five feeds because each leg pays Actions startup/setup overhead.
- More artifact merge code and missing-leg handling.
- Minimal end-to-end speed gain unless RSS p95 is high.

Use when: RSS/news p95 > 60s, source count > 10, or any source needs independent retry/credential/quota isolation.

### Option B — GitHub per-query/category matrix

Design:

1. Setup job restores previous cache and star snapshot, builds query shards.
2. Matrix legs run `scripts/crawl.py`-like shard mode for one query/category, writing candidate repo records, API metadata, errors, and shard cache.
3. Fan-in job validates shards, dedupes repos by `full_name`, applies significance filtering if not already done, checks README policy, merges API/cache metadata, computes star gains, builds snapshots, and emits canonical `data/raw/{week}.json`.

Pros:

- Potentially reduces wall-clock time if API wait and README checks dominate and rate limits permit concurrency.
- Isolates query failures.
- Enables targeted rerun of failed query shards.

Cons:

- Highest risk: search quota and secondary rate limits are shared across jobs but not centrally visible.
- Query shards can produce overlapping repos; merge must be deterministic.
- Cache artifacts can conflict or balloon.
- Fan-in must own star snapshot and trending delta semantics to avoid inconsistent star gains.

Use only after experiments prove aggregate API calls, secondary-limit events, and wall-clock improve versus monolith.

### Option C — Hybrid staged fan-out/fan-in

Design:

1. `crawl-github` remains monolithic initially.
2. `crawl-rss` remains in-process initially, or later becomes RSS matrix.
3. `merge-crawl-artifacts` is introduced as an explicit fan-in/validation job even before matrixing.
4. `correlate-map` optionally shards repository analysis and writes bounded correlation shards.
5. `reduce-analysis-context` emits compact deterministic context for the LLM.

Pros:

- Lowest risk migration path.
- Creates the artifact contract needed for any future matrix.
- Targets the user’s context-size concern without forcing risky GitHub API fan-out.

Cons:

- Does not materially speed crawl until matrix gates fire.
- Adds one fan-in job and contract tests.

Recommended path.

## Expected performance impact

Current baseline:

- GitHub crawler dominates: ~4.5–6 minutes.
- External RSS/news: ~1 second for five sources.
- Analyze stage dominates full workflow when LLM retries occur; example prior run analyze was ~36 minutes.

Expected impacts:

- RSS matrix: likely neutral or slower at current scale; improves retry isolation only.
- GitHub matrix: possible wall-clock improvement, but only if search/core rate limits and secondary limits do not force serialized backoff. Risk of slower runs from quota contention is real.
- Hybrid fan-in plus analysis map/reduce: biggest context-size benefit; may reduce LLM retries and latency by giving the analyzer smaller, purpose-built context.

Failure/retry behavior:

- RSS matrix can mark one source failed and still publish partial results if fan-in records `sources_failed` and caveats downstream output.
- GitHub matrix should fail closed if required query shards fail, unless a PRD explicitly allows partial GitHub data with visible `partial_failures`.
- Analyze map/reduce can retry failed map slices independently, but the reduce stage must fail if required slice summaries are missing or invalid.

## Required artifact contracts

### GitHub shard artifact, if implemented

Each shard must include:

- `schema_version`
- `week`, `crawl_window`, `shard_id`, `query`, `query_type`
- `repos` or raw candidates with `full_name`, stars, topics, timestamps, license, URL, fork/template flags as needed
- `api_calls_used`, `cache_hits`, `stale_cache_hits`
- `rate_limit_limit`, `rate_limit_remaining`, `rate_limit_reset`, `rate_limit_resource`
- `partial_failures`
- deterministic `artifact_checksum`

Fan-in must emit the existing canonical `data/raw/{week}.json` shape plus snapshot, preserving deterministic ordering and existing validation.

### RSS source artifact, if implemented

Each source shard must include:

- `schema_version`
- `week`, `source`, `source_config_checksum`, `crawl_window`
- `articles` with source provenance, URL, title, published date, categories, summary, GitHub links, entities, relevance score
- `source_status` with start/end/duration, attempts, timeout, success/error fields
- `artifact_checksum`

Fan-in must emit canonical `data/raw/{week}-external-news.json` with `sources_requested`, `sources_succeeded`, `sources_failed`, `source_status`, `sources_with_articles`, `dedupe_count`, `errors`, and stable checksum.

### Analysis map/reduce artifacts

Map outputs should be compact and machine-validatable:

- `schema_version`
- `week`, `slice_id`, `slice_type`, `source_artifacts`
- top ranked findings with citations and reason codes
- token/character estimate
- `required_context_omitted: false` or explicit omissions
- `artifact_checksum`

Reduce input should never be raw unbounded crawl JSON. It should consume validated map summaries plus bounded press context.

## Open questions / experiments

1. Measure per-step p50/p95 for `Run crawler`, RSS, correlation, press context, and analyze across at least 5–10 runs.
2. Run a no-merge experiment that replays GitHub query shards with isolated caches and records total API calls, search remaining, secondary-limit events, and wall-clock.
3. Measure checkout/setup/artifact overhead for a small RSS matrix versus current in-process RSS.
4. Determine whether GitHub Actions concurrency with one `GITHUB_TOKEN` worsens search quota or secondary rate limits.
5. Decide partial-data policy: RSS may degrade; GitHub likely should fail closed unless enough shards succeed by explicit threshold.
6. Define max shard count and naming to avoid artifact sprawl.
7. Decide whether map/reduce analysis runs in Actions jobs, Copilot sub-prompts, or a deterministic Python preprocessor plus one LLM reduce.
8. Validate that reduced context preserves all citations needed by quality gates and Copilot review.

## Acceptance criteria

A crawl matrix PRD should require:

- Baseline telemetry recorded for current monolith before implementation.
- Fan-in job validates every shard schema and checksum before analyze.
- Canonical output paths remain unchanged for downstream consumers.
- Deterministic merge: same inputs produce byte-stable canonical artifacts except timestamps explicitly excluded from checksum.
- Partial RSS failures are reflected in metadata and downstream caveats.
- GitHub shard failures either fail the workflow or are surfaced by an explicit accepted degradation policy.
- No increase in total GitHub API calls greater than 10% versus baseline without approval.
- No secondary-rate-limit regression versus baseline.
- End-to-end crawl p95 improves by at least 25% for GitHub matrix, or RSS isolation demonstrates successful partial publication with one failed source.
- Analysis context token estimate decreases by at least 30% for map/reduce without reducing required citations or quality-gate pass rate.
- Existing tests pass, plus new contract tests for shard validation, fan-in merge, deterministic ordering, duplicate handling, missing shard handling, and partial failure metadata.

## Metrics gates

Implement matrix only if at least one gate is met:

- RSS/news p95 > 60 seconds.
- RSS/news configured source count > 10.
- A source needs independent credentials, retry policy, or failure isolation.
- GitHub crawl p95 > 8 minutes and shard experiment shows at least 25% wall-clock improvement with <=10% API-call increase and no secondary-rate-limit increase.
- Analysis prompt/context p95 exceeds agreed token budget or LLM retry rate exceeds 20%, and map/reduce experiment reduces context by >=30% while preserving output quality.

## Key risks

- Matrixing GitHub search can trade wall-clock for rate-limit instability.
- Bad merge semantics can corrupt star-gain trends, duplicate repos, or lose source provenance.
- Matrix artifacts increase operational complexity and can make rebuild/hydration paths brittle.
- Map/reduce can lose nuance if slice summaries omit counterexamples or citations.
- Retry isolation can hide systemic failures unless fan-in produces clear status and gates.

---
# Leela — Issue hierarchy refresh for safe weekly analysis reruns

- Date: 2026-06-05T21:03:35.661+00:00
- Lead: Leela
- Parent epic: #248
- New child: #261

## Product north star

SquadScope's core product is high-quality AI trend analysis and article generation. Crawling and scrape artifacts are supporting evidence systems: they should improve freshness, provenance, and analysis reliability, but they are not the product focus.

## Immediate safety objective

Bad, failed, degraded, stale-evidence-backed, or no-AI fallback reruns must not overwrite a previously good weekly article. A good AI-authored weekly article remains the default last-known-good artifact unless an explicit, audited force/restore path is selected.

## Final hierarchy

- #248 — Parent epic: protect published weekly analysis from unsafe reruns and state the AI analysis/article-generation north star.
- #249 — Candidate staging and publish eligibility manifest, including AI provenance, source artifact provenance, freshness/reuse, and gate results.
- #250 — Preserve existing good weekly analysis on failed/degraded/no-AI/stale-evidence reruns.
- #251 — Block no-AI fallback from replacing AI-authored weekly summaries by default.
- #252 — Explicit safe rerun modes and restore controls; normal reruns reuse valid same-day source artifacts and process only missing/stale sources.
- #253 — Immutable backups and publish-branch concurrency safeguards with source provenance preserved.
- #254 — Atomic weekly promotion across analyzed artifacts, content, deploy, and notifications.
- #255 — Stronger analysis publish gate beyond structural validation, focused on editorial/evidence/provenance quality.
- #256 — Deterministic preflight compaction and fallback policy, aligned to future signal-type map/reduce slices.
- #257 — Overwrite-protection, safe-rerun idempotency, same-day reuse, and stale-evidence regression tests.
- #258 — Selected signal-type claim-ledger map/reduce dry-run: deterministic preflight; mappers for `new_repos`, `trending_repos`, `press_correlations`, and `prior_continuity`; reducer/editorial planner; one final writer; critic/QA gates.
- #259 — Safe rerun, force-replace, restore, no-AI, same-day reuse, and map/reduce dry-run operator docs.
- #261 — Reuse successful same-day source scrape artifacts on rerun, with per-source reuse, missing/stale detection, freshness/date guard, deterministic fan-in/dedupe, and artifact provenance.

## Rationale

The hierarchy now prioritizes analysis safety and generated article quality before crawl mechanics. The crawler-related work is framed as evidence freshness and provenance, especially avoiding redundant same-day source scrapes while still detecting missing or stale sources. The map/reduce work is no longer a broad exploration: it is explicitly the signal-type claim-ledger architecture from the PRD and remains dry-run until safety, publish, and QA gates are complete.

## GitHub changes made

- Edited #248-#259 to clarify priorities, dependencies, and acceptance criteria.
- Created #261 for same-day source scrape artifact reuse.
- Added parent comment on #248 linking #261 and summarizing the refreshed hierarchy.
- Added child comment on #261 linking it back to #248.

---

### 2026-06-05T21:01:05.160+00:00: User directive — Product focus

**By:** jmservera (via Copilot)
**What:** SquadScope is not a scraper; the core purpose is AI analytics and article generation. The product should prioritize trend analysis quality and generated articles over crawl mechanics.
**Why:** User request — captured for team memory

---

### 2026-06-05T21:02:36.076+00:00: User directive — Same-day source reuse

**By:** jmservera (via Copilot)
**What:** Do not repeat successful scraping jobs for the same source on the same day. If a source has already been scraped successfully today, reruns should reuse the latest same-day scrape for that source and continue with the next missing or stale source.
**Why:** User request — captured for team memory

---


# Leela — PR review gate follow-up

- Date: 2026-06-01
- Context: Round review of PR #218 and PR #219 showed both branches were opened by `jmservera`, which means the current GitHub identity cannot submit an approving review on them.
- Decision: Do not bypass the review gate on self-authored pull requests. Treat independent approval as still required before merging branches opened by the same account Leela is operating under.
- Why: GitHub blocks self-approval, and preserving the review gate matters more than forcing a merge from the lead seat.

# Amy — Topic buttons follow-up

- Date: 2026-06-01
- Context: Issue #216 mobile topic buttons regression
- Proposal: Keep topic discovery centered on `/topics/`, remove the global header topic shortcut strip, and hide per-report topic chips on screens up to 768px while leaving desktop topic browsing available through the homepage rail and Topics page.
- Why: The repeated chip rows were consuming too much vertical space on mobile and duplicated navigation that already exists in the primary menu.

---


# Fry — generate-step failure handling


---

# Amy — Share button implementation


---

# Farnsworth — Hindsight validation decision


---

# Fry — Generate-step failure handling


---

# Farnsworth hindsight validation decision


---

# Fry QA triage decision


---

# Leela: Close unverifiable W23 growth execution


---

# Fry PR #236 QA Review


---

# Hermes security review — PR #236 external RSS feeds


---

# PR #236 security unblock


---

# Bender — Crawler parallelism analysis


---

# Farnsworth: LLM input strategy for multi-source news


---

# Fry QA: crawler reliability and performance next iteration


---

# Leela — crawler next-iteration issue


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


# Fry — Issue #238 notify triage


---

# Leela PR #241 Review — Idempotent Weekly Release Notify

- Date: 2026-06-05
- Context: Issue #238 showed a real rerun failure in `notify`: `gh release create week-2026-W23` returned HTTP 422 because the weekly release already existed.
- Decision: Keep weekly release notification idempotent by resolving the weekly tag first, editing an existing `week-*` release with `gh release edit`, and creating only when no release exists.
- Review result: Approved in substance. Formal GitHub approval was blocked because the authenticated account is the PR author, so Leela posted an explicit lead approval comment instead of bypassing the review gate.
- Validation: `tests/test_pipeline.py` passed locally (9 tests), full `tests` passed locally (563 tests), CodeQL checks were green, and Copilot PR review completed with no comments.
- Merge gate: Do not merge from this account until the repository's independent-review requirement for `jmservera`-authored PRs is satisfied.
- PR #241 merged at 2026-06-05T17:21:05Z, closing issue #238.

---

---

# Bender issue #237 implementation


---

# Bender PR #242 Copilot Review Fixes

- Keep category/project-name-only press matches weak even when temporally spiking or corroborated by multiple articles/sources.
- Pass both `--since` and `--until` from the crawl workflow to preserve deterministic canonical `crawl_window` metadata.
- Record bounded fetch attempts and timeout telemetry on `NewsFeedSource` even when `fetch_feed()` raises before returning a feed.
- Keep press-context article lookup comments aligned with the actual URL-to-title mapping.
- PR #243 merged at 2026-06-05T17:34:18Z.

---

---

# Leela PR #243 Review

- Verdict: approved in substance after independent lead review.
- Scope checked: issue #237 acceptance criteria follow-up, PR #242 Copilot comments, PR #243 diff, tests, CodeQL, Copilot review state.
- Local validation: clean PR worktree ran `pytest tests -q` with 574 passed.
- Formal GitHub approval blocked: the active account is the PR author and GitHub rejected own-PR approval.
- Merge gate: wait for an independent non-Bender reviewer/approval unless repository policy explicitly permits merge with the lead approval comment.

---

---

### 2026-06-05T17:06:31.753+00:00: User directive — Copilot Review Asynchronous Gate

**By:** jmservera (via Copilot)
**What:** Copilot Review is asynchronous. Before merging a PR, check whether Copilot is still reviewing and do not merge until the review has finished and any review comments are handled.
**Why:** User request — captured for team memory

---

# Bender input — crawl matrix and map/reduce PRD


# Farnsworth — PRD input: LLM analysis map/reduce

Date: 2026-06-05T17:42:56.819+00:00
Requested by: jmservera

## Recommendation

Adopt a staged map/reduce design for the **LLM analysis stage**, but do not start by splitting the raw crawl job into a GitHub Actions matrix for speed alone. Existing evidence says RSS collection is already fast and in-process parallelized, while the GitHub crawl dominates crawl runtime. The stronger reason for map/reduce is **analysis quality and reliability under context pressure**: smaller mapper calls can extract cited, typed claims from bounded evidence windows, and one reducer can preserve the weekly editorial voice and final `docs/analysis-spec.md` contract.

Initial PRD should target an experimental path behind a feature flag or dry-run workflow, with deterministic compaction and validation before any generated weekly summary becomes publishable.

## Current context pressure

Current weekly analysis input is already large before the model writes anything:

- GitHub raw crawl is the dominant payload. The W23 multi-source run recorded in `.squad/decisions.md` produced `213` new repos and `236` trending repos, roughly `296 KB` / `74k` token-estimate in raw GitHub JSON.
- External news expanded from one TechCrunch feed to five sources. W23 external news was `54` articles / `27` relevant articles, roughly `45.5 KB` / `11.4k` token-estimate.
- Rendered press context is intentionally capped by `scripts/render_press_context.py` at an `8k` token-estimate budget, but prompt-mode output can still include ranked articles, correlations, divergences, caveats, and telemetry.
- The weekly prompt itself injects raw JSON, previous summary, `.squad/identity/wisdom.md`, all `.squad/skills/**/*.md`, analysis instructions, security constraints, and optional press context. This overhead competes with repo evidence for attention.
- `analysis_gate.py` is structural: it enforces frontmatter, required headings, word count, placeholder/raw JSON bans, quality score, dates, and repo format. It does not yet validate intermediate faithfulness, mapper contradictions, or claim-level citation integrity.

The current failure mode is not only token overflow. It is attention dilution: long raw inputs encourage listing, citation drift, missed required headings, weak press/repo correlation claims, and generic summaries. A map/reduce design should reduce evidence windows and force explicit claim contracts before final prose.

## Why a matrix was not used for the crawl

The previous crawler analysis supports not using an Actions matrix yet for RSS/source crawling:

- New five-source RSS collection took about one second in the observed run; GitHub repo crawl remained about 4m47s.
- `scripts/techcrunch_crawler.py` already uses bounded in-process parallel source fetching in the newer pipeline.
- Matrix jobs would add checkout/setup/artifact/merge overhead and commit-race complexity without addressing the actual bottleneck.
- A matrix becomes justified when source count, source heterogeneity, source-specific credentials/quotas, or p95 external collection latency materially increases.

For the PRD, separate **crawl parallelism** from **analysis decomposition**. Matrix crawl is a future topology decision; map/reduce analysis is an editorial reliability strategy.

## Candidate map strategies

### 1. By editorial topic/category

Mappers receive repo slices clustered by topics, languages, descriptions, and prior-week continuity hints. They produce candidate trends, noise patterns, blind spots, and key repos.

Pros:
- Matches final article structure: macro trends and gaps.
- Good for discovering cross-repo patterns inside bounded themes.

Cons:
- Topic overlap can duplicate repos or split one trend across mappers.
- Requires deterministic cluster IDs and repo membership to avoid inconsistent claims.

Best use: primary mapper strategy after deterministic clustering.

### 2. By signal type: new, trending, news/correlation, prior continuity

Separate mappers handle:
- `new_repos`: novelty and launch quality.
- `trending_repos`: momentum and established anchors.
- press/correlation artifact: industry alignment/divergence.
- prior summary/history: continuity, reversals, and prediction follow-up.

Pros:
- Mirrors current input sources and reduces per-call context sharply.
- Easier citation provenance because each mapper owns one evidence type.

Cons:
- Final trends often require combining new + trending + press evidence.
- Reducer needs stronger dedupe and conflict logic.

Best use: strong baseline because it requires little new clustering machinery.

### 3. By source

Mappers summarize each external source or source family, preserving source name, URL, article title, date, relevance score, and correlation confidence.

Pros:
- Keeps source provenance clear.
- Prevents TechCrunch/GitHub/NVIDIA/MIT/HF from becoming one flattened press voice.

Cons:
- Risk of over-weighting press summaries in a GitHub-first analysis.
- More LLM calls for relatively small article volume.

Best use: only if relevant article volume exceeds the compact press-context budget or source mix becomes heterogeneous.

### 4. By repository clusters

Deterministically shard repos into clusters by embedding/topic/language/owner/fork-star anomaly patterns, then map each cluster.

Pros:
- Handles large GitHub raw payloads directly.
- Can isolate suspicious clusters such as fork inflation, star farming, exploit churn, or copycat agent repos.

Cons:
- Needs stable clustering and coverage accounting.
- Cluster labels may be misleading if generated by LLM without deterministic support.

Best use: second iteration once signal-type mapping proves useful.

### 5. Source-specific press summaries before main reduce

A deterministic or LLM-assisted press mapper compresses external news into source-aware press claims, then the main reducer joins those claims with repo claims.

Pros:
- Strong citation preservation if contract is strict.
- Keeps `Where Industry Meets Code` from becoming a news roundup.

Cons:
- Adds hallucination/citation drift risk if source summaries are LLM-generated.
- Current compact deterministic press-context path may be enough.

Best use: defer unless `*-external-news.json` regularly breaches press context budget.

## Recommended architecture

### Phase 0 — deterministic preflight

Inputs:
- sanitized weekly raw JSON,
- compact press context from `*-external-news.json` + `*-correlations.json`,
- previous summary,
- wisdom/skills bundle,
- analysis spec and gate constraints.

Preflight outputs:
- token estimates per input segment,
- repo coverage counts and star totals,
- source coverage counts/errors,
- deterministic clusters or slices,
- stable IDs for repos, articles, and candidate evidence groups.

### Phase 1 — mappers produce claim ledgers, not prose articles

Each mapper receives a bounded evidence slice and returns a strict JSON/markdown-ledger contract. Mappers should not write final publication prose or frontmatter. They should extract:

- candidate trend claims,
- signal/noise/gap judgments,
- evidence repo IDs and article IDs,
- confidence and uncertainty,
- citation URLs,
- contradiction flags,
- suggested `Key References` candidates,
- token usage/coverage telemetry.

### Phase 2 — reducer creates one coherent editorial plan

Reducer consumes only mapper ledgers plus compact global metadata. It:

- deduplicates candidate claims by normalized claim key/topic/repo/article URL,
- merges supporting evidence across mappers,
- rejects weak unsupported claims,
- resolves contradictions by evidence strength and citation quality,
- selects 3-5 macro trends, 2-4 correlations/divergences, 2-4 blind spots, 5-10 repo references, and 3-5 press references,
- chooses `title`, `top_repo`, `tags`, `quality_score`, and optional `predictions`,
- emits an editorial outline with citation bindings.

### Phase 3 — final writer/gate

Final writer converts the reducer plan into the exact `docs/analysis-spec.md` output shape:

```md
## This Week's Trends
## Where Industry Meets Code
## Signal & Noise
## Blind Spots
## The Week Ahead
## Key References
### Notable Projects
### Press & Industry
```

Then `scripts/analysis_gate.py` runs unchanged at first, with future enhancements for evidence/citation checks.

## Reducer responsibilities for global coherence

The reducer is the only stage allowed to create final reader-facing prose. It must:

- preserve one editorial voice and avoid mapper-by-mapper seams;
- maintain a single global thesis and title;
- avoid duplicate claims by normalizing repo full names, article URLs, topic labels, and claim keys;
- keep every repository mention renderable as `[owner/repo](https://github.com/owner/repo)`;
- keep every press claim backed by retained article citations;
- distinguish strong correlations from weak/category/fuzzy matches;
- retain source caveats from external-news metadata;
- keep `repos_featured` and `stars_tracked` tied to deterministic preflight totals rather than mapper estimates;
- satisfy `analysis_gate.py` frontmatter/headings/body constraints.

## Concrete mapper output contract

Suggested `analysis_map_v1` object:

```json
{
  "schema_version": "analysis_map_v1",
  "week": "YYYY-WNN",
  "slice": {
    "id": "signal-type:new-repos",
    "strategy": "signal_type|topic|source|repo_cluster",
    "input_token_estimate": 12000,
    "repo_count": 42,
    "article_count": 0
  },
  "coverage": {
    "repo_ids_seen": ["owner/repo"],
    "article_urls_seen": ["https://example.com/article"],
    "excluded_reason_counts": {"low_relevance": 3}
  },
  "claims": [
    {
      "claim_id": "stable-hash-or-slug",
      "claim_type": "trend|signal|noise|gap|press_correlation|press_divergence|continuity",
      "headline": "Short claim label",
      "summary": "One or two sentences, evidence-bound.",
      "evidence_repos": [
        {
          "full_name": "owner/repo",
          "url": "https://github.com/owner/repo",
          "role": "anchor|supporting|counterexample",
          "stars": 123,
          "stars_gained": null,
          "evidence_note": "Why this repo supports the claim"
        }
      ],
      "evidence_articles": [
        {
          "title": "Article title",
          "url": "https://example.com/article",
          "source": "TechCrunch",
          "published_at": "2026-06-01",
          "role": "corroborates|diverges|context",
          "correlation_strength": "strong|weak|none"
        }
      ],
      "confidence": 0.72,
      "uncertainties": ["stars_gained missing for most trending repos"],
      "quality_flags": ["possible_duplicate", "weak_citation", "needs_reducer_review"]
    }
  ],
  "reference_candidates": {
    "notable_projects": ["owner/repo"],
    "press_articles": ["https://example.com/article"]
  }
}
```

## Concrete reducer input/output contract

Reducer input:

```json
{
  "schema_version": "analysis_reduce_input_v1",
  "week": "YYYY-WNN",
  "run_datetime": "ISO-8601",
  "global_totals": {
    "repos_featured": 449,
    "stars_tracked": 123456,
    "new_repo_count": 213,
    "trending_repo_count": 236
  },
  "source_coverage": {
    "sources_requested": ["techcrunch", "github_blog"],
    "sources_succeeded": ["techcrunch"],
    "sources_failed": ["github_blog"]
  },
  "maps": ["analysis_map_v1 objects"]
}
```

Reducer output should be an editorial plan before prose:

```json
{
  "schema_version": "analysis_editorial_plan_v1",
  "title": "Punchy headline",
  "summary": "One-sentence thesis",
  "top_repo": "owner/repo",
  "tags": ["ai", "developer-tools", "security"],
  "selected_claims": [
    {
      "claim_id": "...",
      "section": "This Week's Trends|Where Industry Meets Code|Signal & Noise|Blind Spots|The Week Ahead",
      "merged_from": ["mapper-claim-id"],
      "citation_bindings": {
        "repos": ["owner/repo"],
        "articles": ["https://example.com/article"]
      }
    }
  ],
  "key_references": {
    "notable_projects": ["owner/repo"],
    "press_articles": ["https://example.com/article"]
  },
  "rejected_claims": [
    {"claim_id": "...", "reason": "duplicate|unsupported|contradicted|weak_citation"}
  ],
  "quality_notes": ["Caveat missing stars_gained in trend section"]
}
```

The final writer then emits only markdown conforming to the existing spec.

## Risks

- Mapper contradiction: two mappers may classify the same repo as signal and noise. Reducer needs explicit conflict resolution and rejected-claim logging.
- Citation drift: if mappers paraphrase article claims without preserving URLs/source/date, the final summary may cite the wrong article or overstate correlation.
- Duplicate claims: topic and signal-type mappers may independently discover the same pattern.
- Quality gate complexity: structural gate is simple today; claim-ledger validation, citation coverage, and contradiction checks add test and maintenance burden.
- Cost/token growth: multiple smaller LLM calls can exceed one large call if slices overlap or include repeated instructions/history.
- Runtime: parallel mapper calls help wall-clock time only if model/API concurrency is available and reliable.
- Editorial voice loss: mapper prose can create a patchwork article unless final prose is written by one reducer/writer pass.
- Over-pruning: small slices may miss weak cross-cluster patterns that only appear globally.
- Failure policy: partial mapper failure could bias coverage unless reducer sees missing-slice telemetry and either degrades explicitly or falls back.
- Prompt injection surface: every mapper still ingests untrusted repo/news text and must keep untrusted-content boundaries.

## Evaluation metrics

### Token and runtime metrics

- Total prompt token-estimate by stage: preflight, each mapper, reducer, final writer.
- Maximum per-call token-estimate and p95 per-call token-estimate.
- Total generated tokens and total model calls.
- End-to-end wall-clock time versus current single-call path.
- Cost per successful weekly analysis and cost per fallback/retry.

### Quality and faithfulness metrics

- `analysis_gate.py` pass rate.
- Required section/headings/frontmatter pass rate.
- Citation coverage: percentage of repo/article claims with retained citations.
- Claim support: percentage of final claims traceable to mapper evidence IDs.
- Hallucination/unsupported-claim count from automated or human review.
- Duplicate claim count before/after reduce.
- Contradiction count and reducer resolution rate.
- Press correlation accuracy: strong vs weak labels preserved correctly.
- Editorial quality score from Farnsworth/Leela rubric: synthesis, specificity, skepticism, blind spots, and voice.

### Stability metrics

- Rerun stability: overlap in selected top trends/repos/press references across repeated runs with same inputs.
- Title/top_repo stability across repeated runs.
- Sensitivity to mapper ordering.
- Missing-slice degradation behavior.

## Non-goals for initial PRD

- Do not replace the weekly `docs/analysis-spec.md` output contract.
- Do not make each mapper produce publishable prose.
- Do not split the crawl into an Actions matrix as part of the analysis map/reduce MVP unless separate performance evidence justifies it.
- Do not include raw article dumps or raw correlation dumps in final analysis prompts.
- Do not let weak/category-only correlations become strong claims without corroboration.
- Do not optimize for maximum recall at the expense of citation integrity and editorial judgment.
- Do not require new paid services, embeddings infrastructure, or vector databases for MVP.
- Do not publish map/reduce output until it passes the existing gate and a new evidence-contract validator.

## Guardrails for MVP

- Feature flag the map/reduce path; preserve the current single-call/fallback path.
- Keep deterministic preflight totals authoritative for `repos_featured`, `stars_tracked`, source status, and citation inventories.
- Wrap all repo/news evidence as untrusted data in every mapper prompt.
- Limit mapper output to structured claims with evidence IDs, not final prose.
- Run final `analysis_gate.py` unchanged initially, then add a separate mapper/reducer contract validator.
- Require a human review comparison against the single-call output for the first several weeks.
- Treat no-AI/data-only fallback as the terminal reliability fallback if mapper/reducer calls fail.

## Acceptance criteria

1. Given the same weekly raw GitHub JSON and compact press context, the map/reduce experiment produces a final markdown summary that passes `scripts/analysis_gate.py`.
2. Every final repo mention resolves to a repo seen in preflight or mapper coverage and is rendered as a proper GitHub markdown link.
3. Every final press claim cites an article URL retained in source coverage or press context.
4. The reducer emits a rejected-claims/conflicts ledger for audit, even if not published.
5. The final article contains 3-5 coherent macro trends, explicit signal/noise judgment, useful blind spots, and a single editorial voice.
6. The map/reduce path demonstrates lower max per-call token-estimate than the current single-call prompt, with measured total cost/runtime reported.
7. Reruns on identical input are stable enough for publication: same top_repo or documented reason for change, and at least 70% overlap in selected key references.
8. Partial mapper failure either retries that slice or marks the final output as degraded; it must not silently omit a source/category.
9. Existing single-call and no-AI fallback paths remain available until map/reduce beats them on gate pass rate, citation coverage, and human editorial review.

---

# Fry QA input — matrix crawl + map/reduce analysis PRD

Date: 2026-06-05T18:15:23Z
Requested by: jmservera
Owner: Fry / QA

## QA position

A matrix is not automatically faster for the current crawl. Prior evidence shows the external RSS stage is about one second, while GitHub search/repo crawling dominates and already approaches the tighter Search API budget. The PRD should treat matrix crawl as a measured experiment: first make artifacts merge-ready and deterministic, then fan out only workloads with independent latency, retry, and quota profiles.

Map/reduce analysis is worth ideating because it can shrink per-model context and isolate failures, but it must not weaken the existing analysis contract. The reducer's final markdown must still pass `scripts/analysis_gate.py`, preserve repo/news citations, produce the current frontmatter shape, and keep the existing Copilot -> GitHub Models -> no-AI fallback path viable.

## PRD-ready QA gates

### 1. Matrix crawl fan-out/fan-in

Required gates before default-on:

- **Deterministic run context:** every leg receives the same `week`, `since`, `until`, source config revision, topic config revision, and run id. No leg may compute its own week window from local wall clock except via a shared generated context artifact.
- **Per-leg artifact contract:** each leg writes exactly one JSON artifact with `{schema_version, run_id, week, since, until, leg_id, source_type, started_at, finished_at, duration_seconds, status, payload, errors, metrics, checksum}`.
- **Fan-in determinism:** merge output must be byte-stable for the same inputs: canonical ordering, deterministic dedupe keys, stable error ordering, and a checksum recorded in metadata.
- **Partial failure semantics:** required legs fail the workflow; optional legs degrade with explicit `status=failed` artifacts and a minimum-source-success gate.
- **Retry behavior:** retry only failed optional legs when possible; fan-in must distinguish first-attempt failure, retry success, and terminal failure. A rerun must not double-count articles/repos.
- **Cache consistency:** cache keys include query/source config, week window, and schema version. Stale cache use must be marked in metadata and never silently mix different windows.
- **Rate-limit safety:** GitHub-query fan-out must be capped by search quota remaining and secondary-rate-limit backoff. RSS/API legs need per-host concurrency limits and timeout/retry ceilings.
- **Artifact compatibility:** downstream analysis consumes one canonical raw payload and one canonical external-news payload regardless of matrix vs single-process collection.

### 2. Map/reduce analysis

Required gates before default-on:

- **Mapper schema validation:** each mapper emits structured JSON, not prose-only markdown: `{schema_version, run_id, week, shard_id, input_refs, findings[], citations[], token_estimate, model, status, errors}`.
- **Finding shape:** each finding includes `claim`, `evidence_refs`, `confidence`, `category`, `source_type`, `repo_full_name?`, `news_url?`, and `contra_refs[]`.
- **Citation preservation:** reducer must be able to trace every final claim to repo URLs, raw payload paths, and news URLs. Missing or malformed citations fail reducer validation.
- **Reducer behavior:** reducer must dedupe equivalent findings, surface contradictions instead of hiding them, prefer higher-confidence/evidence-backed findings, and record rejected/merged finding IDs in a sidecar.
- **Contradiction tests:** contradictory mapper outputs must either resolve with documented rationale or appear in the final analysis as uncertainty/blind spot; they must not disappear silently.
- **Duplicate tests:** duplicate repo/news claims across shards must collapse to one final claim without losing all citations.
- **Gate compatibility:** final markdown must pass `analysis_gate.py` unchanged unless the PRD explicitly extends the gate. Frontmatter, headings, week/date, predictions, and no-placeholder rules still apply.
- **Fallback compatibility:** if any map/reduce stage cannot produce a valid final summary, the pipeline must still try the current single-pass/GitHub Models/no-AI fallback path.

## Test matrix

| Area | Scenario | Expected QA outcome |
| --- | --- | --- |
| Crawl context | All legs receive shared generated week window | Artifacts have identical `week/since/until/run_id`; mismatch fails fan-in |
| Crawl determinism | Same fixture artifacts merged twice | Identical merged JSON bytes/checksum |
| Crawl optional failure | One RSS/source leg times out | Workflow continues if minimum source threshold met; error recorded; analysis sees canonical artifact |
| Crawl required failure | GitHub raw repo leg fails | Analyze does not run; notify-failure path catches pipeline failure |
| Crawl retry | Failed optional leg succeeds on retry | Final metadata records retry count and no duplicate payload entries |
| Crawl cache | Stale cache restored for wrong week/config | Fan-in rejects or marks unusable; no silent mixed-window output |
| Crawl rate limit | Search quota near floor | GitHub fan-out throttles or skips risky fan-out; no uncontrolled parallel search bursts |
| No news data | External-news artifact absent or empty | Press context says no press data; analysis gate can still pass |
| Mapper schema | Mapper emits malformed JSON/prose | Reducer rejects mapper artifact and records mapper failure |
| Mapper failure | One mapper exits non-zero | Required shard fails workflow or optional shard degrades by configured policy; reducer cannot silently omit |
| Duplicate findings | Same repo trend in two shards | Reducer emits one finding with combined citations |
| Contradictions | One mapper says trend is signal, another says noise | Reducer records rationale or uncertainty; contradiction sidecar includes both sources |
| Citation loss | Reducer final claim lacks source refs | Reducer validation fails before `analysis_gate.py` |
| Over-budget context | Single reducer input exceeds token budget | Reducer switches to hierarchical reduce or fails to fallback before spending unbounded tokens |
| Week mismatch | Mapper output `week` differs from raw payload | Reducer rejects artifact |
| Token spike | Mapper/reducer token estimate exceeds budget threshold | Dry-run blocks default path; metrics identify model/stage/shard |
| Gate regression | Final summary missing heading or generic title | Existing `analysis_gate.py` fails and fallback path is exercised |

## Failure modes to require in PRD

- One matrix leg fails: fan-in runs with `if: always()` for diagnostics, but publish/analyze only continue if required artifacts exist and optional-source thresholds pass.
- One mapper fails: reducer must not hide it; either fail the map/reduce path or explicitly degrade based on shard criticality, then fallback to single-pass/no-AI if final gate fails.
- No news data: treated as valid degraded input, not a crash; final summary uses existing "No press data" behavior.
- Over-budget context: preflight estimates for each mapper, reducer, and aggregate final prompt; hard fail or hierarchical reduce before model invocation.
- Stale cache: cache metadata includes created_at, week window, source config checksum, and schema version; stale use is observable and bounded.
- Inconsistent week windows: fan-in/reducer reject mixed `week/since/until` artifacts.
- Token/cost spikes: per-shard and total token ledger records estimates/actuals; alert if p95 or per-run cost exceeds threshold.

## Observability requirements

Minimum notices/metrics per run:

- Per crawl leg: `leg_id`, source name/type, status, start/end/duration, item count, relevant count, dedupe count, artifact size, checksum, cache hit/stale hit, API calls, retry count, error class.
- Aggregate crawl: required/optional leg counts, failed leg counts, merged artifact size/checksum, total API calls, rate-limit remaining/reset/resource, cache hit ratio.
- Per mapper: shard id, input artifact refs/checksums, prompt size, token estimate/actual, model/source, duration, output size, finding count, citation count, quality/schema validation result.
- Reducer: input shard count, failed/skipped shard count, duplicate count, contradiction count, final prompt/output tokens, duration, model/source, final quality gate result.
- Pipeline path: selected path (`single-pass`, `map-reduce`, `github-models`, `no-ai`), fallback reason, and final `analysis_gate` outcome.

## Rollout plan and acceptance thresholds

1. **Design-only contract:** define artifact schemas and validators; do not change default workflow path.
2. **Local fixture dry-run:** run fan-in and map/reduce reducer on deterministic fixtures with no network/model calls.
3. **CI dry-run mode:** add non-publishing matrix/map-reduce jobs that upload artifacts and metrics but keep single-pass analysis as source of truth.
4. **A/B comparison:** for at least 4 weekly runs, compare current single-pass vs map/reduce outputs for gate pass rate, citation preservation, token use, cost, duration, and human review quality.
5. **Default switch only if thresholds pass:**
   - 100% final `analysis_gate.py` pass rate in dry-run comparison.
   - 0 missing required citations in reducer validation.
   - No increase in failed weekly publishes.
   - >=25% reduction in analysis prompt tokens or >=20% reduction in analysis wall time, without quality regression.
   - Crawl matrix only enabled if measured crawl stage p95 improves by >=20% or it materially improves retry isolation for sources with real failure/latency.
   - Token/cost per run stays within agreed budget and has alerts before hard overrun.
6. **Guarded rollout:** workflow_dispatch flag first, then scheduled dry-run, then default-on with single-pass fallback retained for at least one release cycle.

## Local and CI validation needed

Local validation:

- Unit tests for artifact schemas, fan-in merge determinism, dedupe ordering, cache metadata rejection, and failure classification.
- Unit tests for mapper schema validator, reducer dedupe/contradiction handling, citation preservation, week-window rejection, and token-budget preflight.
- Existing focused tests should remain green: `tests/test_crawl.py`, `tests/test_techcrunch_crawler.py`, `tests/test_pipeline.py`, `tests/test_analysis_gate.py`, `tests/test_analyze_fallback.py`, `tests/test_track_token_usage.py`, `tests/test_preflight_cost_check.py`, `tests/test_render_press_context.py`, `tests/test_correlate.py`.

CI validation:

- Matrix dry-run job with fixture legs and one forced optional failure.
- Fan-in job using `if: always()` that publishes diagnostics artifacts even on failed legs.
- Map/reduce dry-run job that compares reducer output to single-pass output but does not publish.
- Quality gate runs on final reducer markdown and fallback markdown.
- Token/cost ledger checks include mapper/reducer stages and enforce budget alerts.
- Rebuild mode validation hydrates canonical merged artifacts and does not depend on per-leg artifacts being present forever.

---

# Leela decision input — matrix crawl + map/reduce analysis PRD

Date: 2026-06-05T17:42:56.819+00:00
Owner: Leela / Lead
Artifact: `docs/PRD-matrix-crawl-map-reduce-analysis.md`

## Decision recommendation

Do not enable a crawl matrix by default. The recent implementation correctly avoided it because five-source RSS collection is about one second and already uses bounded in-process parallelism, while GitHub crawling is dominated by API/cache/rate-limit behavior that matrix fan-out could make worse.

Make crawl artifacts matrix-ready through shared run context, schema validation, checksums, deterministic fan-in, and observability. Gate RSS matrix on source count/runtime/isolation triggers. Gate GitHub matrix on a no-publish shard experiment that proves >=25% crawl speedup with <=10% API-call growth and no secondary-rate-limit regression.

Adopt map/reduce only as an analysis experiment for LLM context and quality. Mappers should emit structured claim ledgers with citations, confidence, contradictions, and coverage. The reducer should own dedupe, citation preservation, contradiction handling, editorial coherence, and final `analysis_gate.py` compliance.

## Follow-up needed

- Baseline crawl/analyze p50/p95 and token/cost metrics across multiple runs.
- Define artifact and mapper/reducer JSON schemas plus validators.
- Run map/reduce in dry-run A/B mode before publication eligibility.
- Keep single-pass/GitHub Models/no-AI fallback until map/reduce beats current quality and reliability gates.

---

# Bender run 27030646485 log review

Date: 2026-06-05T17:42:56Z
Run: https://github.com/jmservera/SquadScope/actions/runs/27030646485

## Findings

- Workflow completed successfully, but success came through the no-AI fallback path.
- Crawl job was healthy: `Run crawler` took ~4m30s, used 455 GitHub API calls, found 213 new repos and 236 trending repos, with 0 cache hits.
- External news behaved correctly at current scale: 5/5 sources succeeded in ~1s total, 39 articles, 23 relevant, 0 deduped, checksum `ebe382a11c0b...`.
- Per-source external news telemetry was present in logs and artifact metadata: source names, hosts, attempts, durations, article counts, relevant counts, GitHub-link counts, errors, config checksum, and artifact checksum.
- Correlation/press-context generation succeeded before analysis: 50 correlations from 449 repos; 9 strong and 41 weak; press context 32,765 bytes / ~7,991 token estimate.
- Analysis was the runtime and reliability concern: three Copilot attempts took ~28m41s and failed quality gates; the fallback GitHub Models request failed with `no_access` for `openai/gpt-4o`; data-only no-AI output passed the gate.
- Quality-gate failures were actionable:
  - attempts 1 and 2: `date must match the current run timestamp`;
  - attempt 3: invalid `predictions[*].claim_type` values plus the date mismatch.
- Token telemetry showed the analysis path estimated 112,911 input tokens / 119,620 total tokens, while the pre-flight check estimated 74,318 input tokens before full rendered prompt accounting.
- Non-blocking platform warning: GitHub Actions reported Node.js 20 actions deprecation for checkout/download/upload/setup/deploy actions.

## Directional read

This run supports the current PRD direction to keep external RSS in-process until scale/isolation thresholds are met. RSS is still not the speed bottleneck; the critical path is now analysis duration, prompt size, and retry waste. It also supports deterministic merge/press-context fan-in over LLM map-reduce for now: compact press context worked, but the full analysis prompt is still too large and brittle.

## Recommendations

1. Treat analysis compaction/retry control as higher priority than crawler matrixing.
2. Add or refine telemetry so pre-flight token estimates match the final prompt/token ledger, including press context and rendered instructions.
3. Consider failing faster on repeated deterministic gate failures such as timestamp mismatch and invalid enum values, or patch/sanitize those fields before retrying.
4. Gate Copilot retry count or switch earlier to no-AI/data-only when attempts exceed a duration budget.
5. Resolve the `openai/gpt-4o` GitHub Models access/config mismatch, or configure an accessible fallback model.
6. Track the Node.js 20 Actions deprecation, but it is not run-specific or urgent compared with analysis reliability.

## Issue recommendation

Do not open a separate crawler/RSS matrix issue from this run. The existing PRD/issue direction is enough for external-news telemetry and fan-in. If a new issue is opened, make it about analysis critical-path reduction and fallback model access, not crawler parallelism.

---

## Scribe: 2026-06-05T18:27:00Z — Merged PRD/run-review decision inputs

**Action:** Merged 5 decision inbox files into decisions.md:
- bender-matrix-crawl-prd-input.md (Bender: matrix crawl and fan-in/fan-out design options)
- farnsworth-map-reduce-analysis-prd-input.md (Farnsworth: analysis map/reduce architecture)
- fry-matrix-mapreduce-qa-prd-input.md (Fry QA: PRD-ready gates and test matrix)
- leela-matrix-mapreduce-prd.md (Leela: decision recommendation summary)
- bender-run-27030646485-log-review.md (Bender: run analysis and directional findings)

**Outcome:** decisions.md grew from 45948 → 91562 bytes. Inbox purged. No duplicates found in merge. Added 5 decision dividers. Content addresses crawl matrix topology, analysis map/reduce experiment design, QA gates/tests, run diagnostics, and fallback strategy.

**No archiving trigger:** decisions.md is still within typical document lifecycle size; existing PRD scope is fresh and actionable.

---

## Leela: Analysis rerun safety issue plan

Created: 2026-06-05T20:46:00.582+00:00

### Parent epic

- #248 — [Protect published weekly analysis from unsafe reruns](https://github.com/jmservera/SquadScope/issues/248)

### Immediate objective

Stop failed, degraded, low-quality, or no-AI analysis reruns from overwriting a good published weekly article. This protection should land before map/reduce implementation changes can affect publication.

### Child issues hierarchy

**P0 Safety Layer (11 issues):**
- #249 — Add candidate staging and publish eligibility manifest for analysis outputs | Bender | type:feature, priority:p0
- #250 — Preserve existing good weekly analysis on failed/degraded reruns | Bender | type:feature, priority:p0
- #251 — Block no-AI fallback from replacing AI-authored weekly summaries by default | Farnsworth | type:feature, priority:p0, rai
- #252 — Add explicit safe rerun modes and restore workflow controls | Leela | type:feature, priority:p0
- #253 — Add immutable backups and publish-branch concurrency safeguards | Bender | type:feature, priority:p0
- #254 — Make weekly promotion atomic across analyzed/content/deploy/notify | Bender | type:feature, priority:p0
- #255 — Strengthen analysis publish gate beyond structural validation | Farnsworth | type:feature, priority:p0, rai
- #257 — Add overwrite-protection and rerun idempotency regression tests | Fry | type:feature, priority:p0

**P1 Quality/Run Readiness (2 issues):**
- #256 — Add preflight compaction and fallback policy for next analysis run | Farnsworth | type:feature, priority:p1
- #259 — Document safe rerun, force-replace, and restore operations | Leela | type:docs, priority:p1

**P2 Future Analysis Architecture (1 issue):**
- #258 — Add map/reduce dry-run with claim-ledger contracts and QA comparison gates | Farnsworth with Fry QA support | type:feature, priority:p2, rai

### Summary

Safety-first protection layer for analysis reruns across staging/publish workflow. Prevents silent overwrite of good weekly articles on transient failures, low-quality output, or no-AI fallback misuse. Prioritizes atomic promotion, eligibility gates, and immutable backups before rolling out map/reduce.

### Notes

GitHub issue hierarchy represented via parent #248 with linked child issues and inline comments. All issues labeled `squad` with per-owner tracking.
### 2026-06-09T15-55-26: PRD triage disposition and move block
**By:** Leela
**What:** PRD triage disposition and move block
**References:** #327, #328, #329, #330, #331, #332, #333, #302, #307
**Why:** Reviewed PRD/planning docs and GitHub issues/PRs on 2026-06-09. Completed or superseded docs should not be moved in the current worktree because unrelated dirty Squad upgrade files are present. Remaining work is tracked by existing issues: #327 mobile density/scannability, #328 generated visuals and cover/frontmatter support, #329 copyright-safe image policy/registry, #330 accessibility/performance gates, #331 map/reduce promotion, #333 crawl matrix readiness, #302 Podcaster handoff, #307 external podcast link, and #332 archive-after-clean-worktree. No duplicate feature issues are needed.

# Podcaster handoff boundary for issue #302

Date: 2026-06-07T21:42:28.011+00:00

Decision: SquadScope emits the Podcaster handoff only after a successful normal weekly article deploy. The handoff job depends on `analyze`, `generate`, and `deploy`, gates on `run_mode == 'normal'`, and is non-blocking so Podcaster errors cannot fail, roll back, or delay article publication.

Rationale: Podcaster is a sister project. SquadScope should provide a trusted post-publish contract, not own podcast generation or Azure podcast resources. Dry-run, candidate-only, restore, force-replace, no-AI, and failed paths are excluded to avoid downstream generation from unpromoted, replacement, or fallback content.

Implementation notes: `scripts/podcaster_handoff.py` reads `PODCASTER_ENDPOINT` from Actions variables and `PODCASTER_API_KEY` from Actions secrets, sends the key only in the `x-podcaster-api-key` header, and never logs the key. The payload includes `week`, `article_url`, `article_path`, `article_sha256` when available, `publish_run_id`, `publish_mode`, and source artifact references.

# Fry Podcaster validation recommendation

Date: 2026-06-07T21:42:28.011+00:00

## Recommendation

Do not use a normal `crawl-and-publish.yml` dispatch as the first Podcaster dry-run path. The safe first live validation path should be a dedicated non-publishing Podcaster dry-run workflow/job that uses the configured Actions `PODCASTER_ENDPOINT` variable and `PODCASTER_API_KEY` secret, sends `dry_run: true`, and cannot publish, restore, force-replace, or mutate production content.

## Rationale

Local mocks validate the SquadScope handoff client and redaction behavior, but local live validation is blocked because the Podcaster secret is only available in Actions. The existing `crawl-and-publish.yml` dry-run and candidate-only modes explicitly skip `podcaster-handoff`, while normal/force-replace modes can touch production content.

### 2026-06-10T10:27:49.647+00:00: Tick / Checklist
**By:** squadscope (automated)
**What:**
- Confirm and document the Podcaster HTTP API contract (request fields plus the response schema, e.g. the proposed Podcaster-side `job_id`, `status`, and `errors` fields) once Podcaster attaches it
- Confirm the authentication header name and the canonical secret name used to store the Podcaster API key (Podcaster-side proposal: `PODCASTER_API_KEY`)
- Document accepted status values and retry semantics for non-2xx responses
- Confirm and document the canonical publish manifest field names (e.g. reconcile freshness status and artifact URL fields; proposed Podcaster-side names `freshness_status` vs `freshness`, `artifact_url` vs `url`)
- Provide example request/response JSON and canonical endpoint URL(s)
- Confirm dry-run semantics and non-blocking handoff behavior

**Next steps:**
1. Author or attach a concise API contract doc (e.g. `docs/integration-contract.md`) with request/response schemas and examples; treat the field names above as Podcaster-side proposals until the contract is attached.
2. Update pipeline docs to reference the API contract and confirm/document the canonical Actions secret names (Podcaster-side proposal: `PODCASTER_ENDPOINT`, `PODCASTER_API_KEY`).
3. Add integration smoke test instructions and an operator checklist for manual runs.

### 2026-06-10T10:27:49.647+00:00: Tick / Checklist
**By:** squadscope (automated)
**What:**
- Listed open PRs and inspected PR #314
- Ran full test suite on main (696 passed)
- Checked out PR #314 and ran its tests (9 passed)
- Created Podcaster submission checklist and opened PR #363
- Verified ralph loop activity via ralph_squadscope.log

**Next steps:**
1. Monitor PR #314 review threads and surface unresolved threads.
2. Request API contract doc from Podcaster (if missing) and attach to checklist PR.
3. Run periodic ticks every 20 minutes and append summary.

### 2026-06-13T15:54:00Z: NEVER disable or bypass branch rulesets

**By:** jmservera (operator directive)

**What:** Never disable, bypass, or work around branch protection rulesets. All changes MUST go through a branch + PR workflow. Pushing directly to main is forbidden, even for cleanup, docs, or trivial changes. Agents must always create a feature branch and open a PR.

**Why:** Operator found that a dispatched agent bypassed the ruleset to push directly to main. This must never happen again.

