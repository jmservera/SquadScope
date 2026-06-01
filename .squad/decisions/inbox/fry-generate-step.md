# Fry — generate-step failure handling

Date: 2026-06-01

## Context
Issue #220 showed the crawl-and-publish workflow could finish crawl and analysis successfully, then fail in the generate handoff because the generated weekly page path was absolute while the publish-branch restore logic assumed a repository-relative path. The same workflow also lacked a failure-to-issue bridge, so repeated pipeline failures did not automatically open or update a GitHub issue.

## Decision
Normalize `page_path` to a repo-relative `content/weekly/...` path inside the generate commit step before copying weekly output onto the publish branch. Add a dedicated `notify-failure` job that always evaluates after the pipeline jobs and creates or updates a GitHub issue whenever any crawl/analyze/generate/deploy/notify job fails.

## Rationale
The path normalization fixes the actual handoff bug without changing `scripts/generate_content.py`, which already returns an absolute file path used elsewhere in tests. A separate failure notifier makes regressions visible even when later jobs are skipped, which is the exact reliability gap that hid the recent failures.
