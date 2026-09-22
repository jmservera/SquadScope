# Issue 779 lifecycle disposition plan

Date: 2026-09-22
Owner: Leela
Issue: https://github.com/jmservera/SquadScope/issues/779

## Objective

Correct the GPT-5.6-Sol PRD lifecycle state without changing production model
configuration. Preserve the distinction between shipped implementation,
qualified editorial acceptance, and blocked measurement acceptance.

## Plan

1. Review the PRD history, owner evidence, W37/W38/W39 gate and measurement
   evidence, editorial findings, and the implementation/archival PRs.
2. Restore the PRD from `docs/processed/` to `docs/prds/` with git history
   preserved.
3. Mark implementation as shipped while keeping post-upgrade validation
   incomplete/blocked.
4. Record:
   - passing W38/W39 gates and qualified editorial acceptance;
   - bounded prediction/reference weaknesses and the limits of score 100;
   - retained ledger deltas;
   - W37's incorrect `copilot-default` attribution;
   - the corrected GPT-5.5 pricing reconstruction and its analysis-only limits;
   - missing per-agent/runtime/cache/cost/provider-latency evidence.
5. Create one focused owner decision/rollback issue after checking for
   duplicates. Request either provisional retention with instrumented evidence
   collection or the documented rollback.
6. Preserve the Fry and Farnsworth research artifacts for the later focused
   docs PR because `.copilot-tracking/research/` is a tracked repository
   convention.
7. Stop before commit, push, PR creation, merge, or comments on issue #779.

## Acceptance

- PRD is active under `docs/prds/` and does not claim the cost criterion passed.
- Owner decision issue states exact missing evidence, triggers, and rollback
  scope.
- Change record identifies all worktree changes and the created issue.
- No model declaration, workflow, test, unrelated documentation, or mutable
  `.squad` state is modified.
