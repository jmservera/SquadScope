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

