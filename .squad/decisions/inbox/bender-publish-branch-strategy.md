# Decision: Use `publish` branch for automated data commits

**Date:** 2026-05-19T19:37:45+02:00
**Author:** Bender (Crawler)
**Status:** Implemented (PR #129)
**Fixes:** Issue #128

## Context

The crawl-and-publish workflow failed because:
1. The repo setting "Allow GitHub Actions to create or approve pull requests" is disabled
2. `gh pr create` with `GITHUB_TOKEN` is blocked by this setting
3. Even if enabled, the `copilot_code_review` rule + `required_review_thread_resolution` on main could block auto-merge unpredictably

## Decision

Replace PR-based commits with direct push to an unprotected `publish` branch.

- The main branch ruleset only protects `refs/heads/main`
- The `publish` branch accepts direct pushes from workflow `GITHUB_TOKEN`
- Inter-job data flow uses artifacts (unchanged)
- Deploy job downloads all artifacts directly (no dependency on branch state)
- `reskill-check` reads `run-counter.txt` from `publish` branch with fallback to main

## Consequences

- Automated data no longer lands on `main` automatically — it accumulates on `publish`
- A separate manual or scheduled merge from `publish` → `main` can sync when desired
- Main branch protection remains fully intact (no bypasses)
- Pipeline reliability is decoupled from PR permission settings

## Alternatives Considered

1. Enable "Allow GitHub Actions to create PRs" — requires repo admin action, doesn't solve auto-merge reliability
2. Use a PAT/GitHub App token — adds secret management complexity
3. `--admin` flag on merge — bypasses protection, violates team decision
