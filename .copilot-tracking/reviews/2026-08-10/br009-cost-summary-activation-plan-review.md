<!-- markdownlint-disable-file -->

# BR-009 Cost Summary Activation Review

## Metadata

* Plan: `.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md`
* Changes: `.copilot-tracking/changes/2026-08-10/br009-cost-summary-activation-changes.md`
* Branch: `feat/br009-cost-summary-activation`
* Base: `origin/main` at `45aeb2c`
* Date: 2026-08-10

## Request Fulfillment

* [x] Activate BR-009 cost-summary generation in the owning publish transaction
* [x] Preserve crawl continuity for an identified no-AI accepted run
* [x] Fail closed on missing, malformed, stale, or unreconciled ledger input
* [x] Carry the current summary through the same-run deployment artifact
* [x] Prevent the checked-in summary from satisfying current-run verification
* [x] Add automated regression coverage for activation boundaries

## Review Iterations

The first role review found that the summary was committed to `publish` but
omitted from the artifact consumed by the inline deployment. The workflow now
uploads only `data/metrics/cost-summary.json`, downloads it into the deployment
checkout, and verifies it before Hugo builds.

Hermes then found that the checked-in summary could satisfy the verification if
artifact transport regressed. The deployment now removes that copy before
download. The workflow contract enforces remove, download, and verify ordering.

Copilot's PR review found that the workflow contract grouped `data/metrics/`
with directories uploaded in full, even though the artifact intentionally
contains only the public `cost-summary.json`. The corrected contract checks the
metrics directory at hydration and commit boundaries, rejects a whole-directory
artifact upload, and requires the single public summary file.

## Final Dispositions

* URL: Accept
* Hermes: Accept
* Leela: Accept
* Fry: Accept with non-blocking follow-ups for subprocess and artifact
  round-trip integration coverage

## Validation

* Focused final transport contract: 1 passed
* Affected tests: 80 passed
* Full pytest suite: 1,588 passed with 2 expected URL-image warnings
* Ruff check and format: passed
* Workflow YAML parse and git diff check: passed
* Zizmor 1.27.0: no medium or high findings
* Checkov GitHub Actions scan: 894 passed, 0 failed
* Hugo 0.147.9: 2,707 pages and 8 aliases
* Initial PR head checks: 14 passed
* Copilot PR comments: 1 addressed, 0 remaining after thread resolution

## Completion

* User request fulfillment: 100%
* Code and test review: 100%
* Local validation: 100%
* Overall status: Follow-up fix validated locally; latest-head PR checks pending