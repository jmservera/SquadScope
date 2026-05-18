# Farnsworth Analysis Spec Decisions

- **Date:** 2026-05-18T12:07:20.778+02:00
- **Issue:** #9
- **Scope:** Weekly analysis contract between crawler output and site generator

## Proposed decisions

1. **Analyzer output frontmatter is a superset contract.**
   - Required fields: `title`, `date`, `week`, `year`, `tags`, `categories`, `repos_featured`, `stars_tracked`, `top_repo`, `quality_score`, `summary`.
   - Why: this satisfies Amy’s weekly page needs and Leela’s reviewer gate in one artifact.

2. **Reader-facing structure stays in five stable H2 sections.**
   - Required order: `Notable New Repositories`, `Trending This Week (Stars Gained)`, `Trend Analysis`, `What's Missing`, `Conclusion`.
   - Why: matches the approved weekly page shape and keeps generator parsing simple.

3. **Signal / Noise / Gaps remain explicit as required subsections.**
   - `Trend Analysis` must include `### Signal` and `### Noise`.
   - `What's Missing` must include `### Gaps`.
   - Why: preserves the approved editorial lens without fighting the page-level section structure.

4. **Trending must degrade honestly when momentum data is incomplete.**
   - If `stars_gained` is absent or null, the summary must say the section is directional rather than a true weekly momentum leaderboard.
   - Why: avoids overstating popularity as trend movement.

5. **Analyzer input schema should be strict on core repo fields and tolerant on metadata.**
   - Required reads: week slug, crawl timestamp, new/trending repo arrays, and top topics.
   - Optional diagnostics: `partial_failures`, `filter_summary`, `snapshot_path`.
   - Why: supports current crawler output while leaving room for metadata evolution.
