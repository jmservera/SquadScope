<!-- markdownlint-disable-file -->
# Changes Log: Claracle Relaunch Follow-Up Execution

## Related Plans

* .copilot-tracking/plans/2026-08-02/claracle-relaunch-followup-execution-plan.instructions.md
* .copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md

## Implementation Date

2026-08-02

## Summary

Published the PR review correction, reconciled production GA4/GSC observations, refreshed acceptance evidence, created one owner-action register, and produced implementation-ready rollout and cost plans. External account actions and human approvals remain owner-gated.

## Added

* .copilot-tracking/research/subagents/2026-08-02/claracle-ga4-gsc-followup-research.md
* .copilot-tracking/research/subagents/2026-08-02/claracle-acceptance-gates-followup-research.md
* .copilot-tracking/research/subagents/2026-08-02/claracle-rollout-cost-followup-research.md
* .copilot-tracking/research/2026-08-02/claracle-relaunch-followup-execution-research.md
* .copilot-tracking/plans/2026-08-02/claracle-relaunch-followup-execution-plan.instructions.md
* .copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md
* .copilot-tracking/details/2026-08-02/claracle-relaunch-followup-execution-details.md
* .copilot-tracking/details/2026-08-02/claracle-gated-rollout-cost-details.md
* .copilot-tracking/plans/logs/2026-08-02/claracle-relaunch-followup-execution-log.md
* docs/review/data-observatory-relaunch/owner-action-register.md

## Modified

* hugo.toml
* docs/growth/ga4-gsc-baseline-2026-07-29.md
* docs/prds/claracle-data-observatory-relaunch.md
* docs/review/data-observatory-relaunch/README.md
* docs/review/data-observatory-relaunch/security-review.md
* docs/review/data-observatory-relaunch/status-of-record.md
* .copilot-tracking/research/2026-08-02/claracle-relaunch-readiness-reconciliation-research.md
* .copilot-tracking/plans/2026-08-02/claracle-relaunch-readiness-reconciliation-plan.instructions.md
* .copilot-tracking/changes/2026-08-02/claracle-relaunch-readiness-reconciliation-changes.md

## Completed Work

* Pushed correction commit `8fddceb` and resolved both PR #647 review threads
* Confirmed production GA configuration presence, GSC metadata absence, sitemap health, and protected secret names without exposing values
* Corrected FR-035 from disconnected to partial external acceptance
* Reconciled SEC-01 and SEC-04 with current sanitization and lifecycle tests
* Classified #622 as non-blocking polish and #626 as independent hardening
* Added exact owner actions for analytics, security, accessibility, protected Podcaster, visual, and sponsor evidence
* Planned report-only cost attribution, one dynamic-topic canary, and repository-page activation with rollback

## Validation

* Full pytest: 1,389 passed, 19 skipped, 34 subtests passed
* Focused acceptance suite: 45 passed, 4 skipped
* Ruff lint and format: passed
* Data-page, public dataset, and trend-export checks: passed
* PR #647 at `8fddceb`: 13 successful checks, including Production site
* Editor diagnostics and `git diff --check`: passed

## Known Inherited Discrepancy

`discover_topic_candidates.py --check` reports the candidate registry stale at the inherited commit. Temporary regeneration preserves 2,173 total candidates and the same five eligible candidates while rotating four sanitized keys. The owning publish workflow should refresh this generated state.
