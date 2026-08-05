<!-- markdownlint-disable-file -->
# Release Changes: Claracle Gated Rollouts and Cost Measurement

**Related Plan**: claracle-gated-rollout-cost-plan.instructions.md
**Implementation Date**: 2026-08-05

## Summary

Reconciled Phase 1 (report-only build-cost experiment) as already delivered and merged
to `main` under a separate plan. Implemented the sponsor-directed repository identity
backfill mechanism (Phase 2, Step 1) that resolves stable GitHub IDs for the production
corpus and treats confirmed-not-found repositories as reviewed deletion evidence. The
remainder of Phase 2 and all of Phases 3 through 5 remain blocked on pending sponsor and
Hermes rollout decisions and are not started.

## Changes

### Added

* [scripts/backfill_repo_identity.py](scripts/backfill_repo_identity.py) - new script
  that checks every repository history lacking a stable GitHub ID against
  `GET /repos/{full_name}`, recording `found` (github_id/node_id), `not_found` (a
  confirmed 404), or `error` (any ambiguous outcome, never treated as deletion)
  outcomes to `data/derived/observatory/repo-identity-backfill.json`. Reuses
  `scripts.crawl.GitHubClient` for caching/retry/rate-limit handling and
  `observatory_repos.write_json_atomically()` for checkpointed, resumable writes.
* [tests/test_backfill_repo_identity.py](tests/test_backfill_repo_identity.py) - unit
  tests covering pending-repo discovery, dry-run counting, found/not_found/error
  outcomes, resume-skips-already-checked behavior, and the missing-token failure mode.

### Modified

* [.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md](.copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md) - marked Phase 1 checklist items complete with a cross-reference note to the 2026-08-03 delivery.
* [scripts/observatory_repos.py](scripts/observatory_repos.py) - added
  `load_identity_backfill()` and `merge_identity_backfill_overrides()`; threaded an
  optional `identity_backfill` parameter through `load_repository_histories()` (fills
  `github_id`/`node_id` for observations the crawl never captured); `generate()` and
  `seed_lifecycle()` now load the backfill file and merge its `not_found` entries into
  the effective lifecycle overrides before validation, so a confirmed 404 resolves as
  `status: "deleted"` with `status_evidence: "github_api_404_identity_backfill"`
  unless a manual `[repo_pages.lifecycle]` override for the same repository takes
  precedence.
* [tests/test_observatory_repos.py](tests/test_observatory_repos.py) - added coverage
  for stable-ID resolution from the backfill file, not-found-as-deletion-evidence, and
  manual overrides winning over an automated not-found disposition.

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
* Phases 2 through 5 were not started, except for the identity backfill mechanism above.
  * Reason: each phase's success criteria require a sponsor (`jmservera`) rollout
    decision and, for Phase 2/4, additional Hermes lifecycle/identity dispositions.
    The [owner action register](../../../docs/review/data-observatory-relaunch/owner-action-register.md#sponsor-rollout-decision)
    records both `dynamic_topic_creation` and `repo_pages` sponsor decisions as
    **Pending** as of 2026-08-05. Proceeding would mean fabricating approvals or
    mutating production-shaped lifecycle/identity state without the required sign-off.
* Repository identity strategy (Phase 2, Step 1) was implemented as a sponsor-directed
  exception to the above.
  * Reason: `jmservera` gave an explicit sponsor decision (recorded as ID-01 in the
    Planning Log) to backfill stable GitHub IDs for the production corpus and to treat
    a confirmed not-found (HTTP 404) as deletion evidence, since deleted repositories
    are an expected risk independent of identity strategy. This resolves the sponsor
    half of Phase 2's identity/Hermes disposition item; the Hermes half remains open.
  * The live backfill run against the production corpus (`data/raw/*.json`, ~2,012
    repositories lacking a stable ID) is tracked separately; see the Release Summary
    for its outcome once complete.

## Release Summary

Updated after the live identity backfill run completes.
