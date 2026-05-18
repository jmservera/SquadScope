# Bender Decision Inbox — Analyze Job

- **Date:** 2026-05-18T13:05:53.678+02:00
- **Author:** Bender
- **Issue:** #10 — Integrate Actions analyze job with Copilot path and reviewer gate

## Context

Phase 2 needs the weekly workflow to transform `data/raw/YYYY-WNN.json` into `data/analyzed/YYYY-WNN-summary.md` inside GitHub Actions, while preserving the approved fallback architecture and enforcing the analyzer contract before any downstream publish step runs.

## Decision

1. Extend `.github/workflows/crawl-and-publish.yml` with an `analyze` job that runs after `crawl`.
2. Standardize the stage handoff artifacts as:
   - `raw-data` for crawl → analyze
   - `analyzed-data` for analyze → generate
3. Use standalone Copilot CLI as the primary analysis path with:
   - `permissions.copilot-requests: write`
   - PAT secret `COPILOT_GH_TOKEN` exported as `COPILOT_GITHUB_TOKEN`
4. Add `scripts/analyze_fallback.py` as the GitHub Models fallback using `permissions.models: read` and `GITHUB_TOKEN`.
5. Enforce an automated `quality-check` gate in the workflow that blocks publish when the analysis contract is not met.

## Quality Gate Contract

The workflow gate should fail if any of the following are false:

- YAML frontmatter exists.
- The exact required frontmatter keys are present.
- `quality_score` is an integer and at least 60.
- Required H2/H3 sections appear in the documented order.
- Body word count is at least 200.
- Output does not leak raw JSON, traceback text, or placeholder/tool-log content.

## Implications

- Future generate jobs can safely consume `analyzed-data` without needing to inspect the raw crawl artifact.
- Copilot CLI failures do not block the pipeline immediately; the GitHub Models fallback preserves publishability.
- Reviewer-gate failures stay machine-detectable and stop low-quality summaries before they reach downstream stages.
