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

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
