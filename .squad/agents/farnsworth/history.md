# Farnsworth — History

## Project Context
- **Project:** SquadScope — A GitHub Pages site that summarizes weekly tech news from GitHub
- **Stack:** Data analysis, content generation, markdown output
- **User:** jmservera
- **Goal:** Critical analysis of GitHub trends — identify what's important, what's trending, what's missing. Feed insights to Amy for the GitHub Pages site.

## Team Updates

**2026-05-18:** PRD now available at `docs/PRD.md`. Review for analysis requirements and success criteria.

**2026-05-18T10:27:35Z:** Phase 0 is complete. Architecture decision published in `.squad/decisions.md`. CI analysis pipeline uses Copilot CLI (primary) with GitHub Models fallback. Reviewer gate requires quality_score ≥ 60. Phase 2 analyzer work is unblocked.

## Learnings

- **2026-05-18T10:50:21Z:** PR #28 (Issue #9 analysis spec) review complete. All 4 Copilot findings addressed (bc823a3). Analyzer contract formalized: markdown + YAML frontmatter with `quality_score` field, three labeled sections (Signal, Noise, Gaps), machine-checkable structure. Quality gate criteria: score ≥ 60, all sections present, word count ≥ 200. Reuses crawler JSON input schema. Ready for merge. Phase 2 generator can now design Hugo templates against stable contract.
- **2026-05-18T12:07:20.778+02:00:** The analyzer contract should be a superset of Amy's weekly page frontmatter plus Leela's `quality_score` gate, so one analyzed artifact can satisfy both editorial review and generator input.
- **2026-05-18T12:07:20.778+02:00:** The analyzer contract should be a superset of Amy’s weekly page frontmatter plus Leela’s `quality_score` gate, so one analyzed artifact can satisfy both editorial review and generator input.
- **2026-05-18T12:07:20.778+02:00:** Keep the reader-facing weekly summary in five stable H2 sections, but require labeled `Signal`, `Noise`, and `Gaps` subsections so the editorial lens remains explicit and machine-checkable.
- **2026-05-18T13:20:07.067+02:00:** Weekly analysis prose should render repo mentions as explicit GitHub markdown links, and the current raw crawl artifact exposes those repo page URLs under `url` rather than `html_url`, so analyzer/generator prompts should require link formatting without assuming a different field name.
