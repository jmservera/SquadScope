<!-- markdownlint-disable-file -->
# Release Changes: Claracle Gated Rollouts and Cost Measurement

**Related Plan**: claracle-gated-rollout-cost-plan.instructions.md
**Implementation Date**: 2026-08-05

## Summary

Reconciled Phase 1 (report-only build-cost experiment) as already delivered and merged
to `main` under a separate plan. Phases 2 through 5 remain blocked on pending sponsor
and Hermes rollout decisions and are not started.

## Changes

### Added

* None. No new code was required.

### Modified

* [.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md](.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md) - marked Phase 1 checklist items complete with a cross-reference note to the 2026-08-03 delivery.

### Removed

* None.

## Additional or Deviating Changes

* Phase 1 was not re-implemented. `.github/workflows/build-cost-experiment.yml`,
  `scripts/build_cost_experiment.py`, and `tests/test_build_cost_experiment.py` were
  delivered 2026-08-03 under
  `.copilot-tracking/plans/2026-08-03/claracle-all-followups-plan.instructions.md` and
  are already present on `main` as of 2026-08-05 (verified by file existence on this
  branch, cut from an up-to-date `main`).
  * Reason: implementing it again would duplicate an already-merged, tested experiment
    and diverge from the existing workflow contract.
* Phases 2 through 5 were not started.
  * Reason: each phase's success criteria require a sponsor (`jmservera`) rollout
    decision and, for Phase 2/4, additional Hermes lifecycle/identity dispositions.
    The [owner action register](../../../docs/review/data-observatory-relaunch/owner-action-register.md#sponsor-rollout-decision)
    records both `dynamic_topic_creation` and `repo_pages` sponsor decisions as
    **Pending** as of 2026-08-05. Proceeding would mean fabricating approvals or
    mutating production-shaped lifecycle/identity state without the required sign-off.

## Release Summary

One file affected: the implementation plan's Phase 1 checklist was marked complete with
a cross-reference to its actual 2026-08-03 delivery. No application code, tests, or
workflows changed in this branch. Phases 2 through 5 remain blocked pending sponsor and
Hermes decisions recorded in the owner action register.
