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

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
