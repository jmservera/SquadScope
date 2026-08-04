<!-- markdownlint-disable-file -->
# Planning Log: Claracle Gated Rollouts and Cost Measurement

**Related Plan**: claracle-gated-rollout-cost-plan.instructions.md

## Discrepancy Log

### Implementation Deviations

* DD-01: Phase 1 was reconciled rather than re-implemented.
  * Plan specifies: build a new report-only cost experiment (workflow, script, tests).
  * Implementation differs: the experiment was already built and merged to `main` on
    2026-08-03 under `.copilot-tracking/plans/2026-08-03/claracle-all-followups-plan.instructions.md`.
    This plan's Phase 1 checklist was marked complete with a cross-reference instead of
    duplicating that work.
  * Rationale: avoids a second, divergent implementation of the same workflow contract.

## Suggested Follow-On Work

* WI-01: Retain 3/5-run `build-cost-experiment.yml` artifacts and obtain an owner
  budget conclusion for Q-01/NFR-009 — medium priority.
  * Source: Phase 1 success criteria (report is implemented; retained comparable runs
    and an owner-reviewed budget are still open per
    [status-of-record.md](../../../../docs/review/data-observatory-relaunch/status-of-record.md)).
  * Dependency: none technical; needs an owner to dispatch and review the runs.
* WI-02: Resolve stable GitHub identity for the production repository corpus, or
  record an explicit accepted-risk disposition, before starting Phase 2 — high priority.
  * Source: Phase 2, Step 1.
  * Dependency: Hermes/sponsor decision.
* WI-03: Record the sponsor rollout decision for `dynamic_topic_creation` and
  `repo_pages` separately — high priority, blocks Phases 2 through 5.
  * Source: Phases 2 through 5 success criteria; Plan Dependencies.
  * Dependency: `jmservera` sponsor review of
    [owner-action-register.md#sponsor-rollout-decision](../../../../docs/review/data-observatory-relaunch/owner-action-register.md#sponsor-rollout-decision).

## User Decisions

* None recorded yet.
