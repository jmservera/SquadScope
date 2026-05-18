# Farnsworth Reskill Workflow Decisions

- **Date:** 2026-05-18T15:22:25.067+02:00
- **Issue:** #14
- **Scope:** Reskill retrospective, learned-state injection, and quality trend tracking

## Proposed decisions

1. **Reskill context should be assembled from the latest analyzer evidence, not generic squad history alone.**
   - Inputs: last up to five `data/analyzed/*-summary.md` files, matching `data/snapshots/` hindsight when available, current `wisdom.md`, learned skills, and a quality trend report.
   - Why: this gives the retrospective something concrete to calibrate against and closes gaps G3-G7, G11, and G12.

2. **Learned state must flow back into the weekly analyzer prompt.**
   - The analyze job should inject `.squad/identity/wisdom.md` into `{{WISDOM}}` and concatenated markdown from `.squad/skills/` into `{{SKILLS}}` before calling Copilot CLI or the GitHub Models fallback.
   - Why: without prompt injection, learning artifacts exist but never influence future analysis.

3. **Quality trend tracking should be a first-class reskill input.**
   - `scripts/track_quality.py` should read `quality_score` from analyzed summaries and produce a markdown trend report for retrospective review.
   - Why: the squad needs a lightweight longitudinal measure of whether editorial quality is improving.

4. **Reskill outputs belong in persistent squad state.**
   - Keep `.squad/reskill/` for weekly retrospective reports and `.squad/skills/` for extracted reusable patterns, both committed to git.
   - Why: durable learning needs durable storage, not ephemeral workflow output.
