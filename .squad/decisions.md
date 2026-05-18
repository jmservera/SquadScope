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
- OQ8: Copilot usage limits in automation

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

The SquadScope CI analysis pipeline uses a two-tier approach: Copilot CLI (primary, agentic, repo-aware) with GitHub Models API (fallback, simpler, REST-based). Data flows through well-defined stage boundaries with JSON → Markdown → HTML transformations. A quality gate ensures no low-quality analysis reaches publication. The architecture is designed for extensibility via MCP tools and self-improvement via the reskill cycle.

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
