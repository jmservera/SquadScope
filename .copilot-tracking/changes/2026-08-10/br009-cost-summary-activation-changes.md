<!-- markdownlint-disable-file -->

# Changes: BR-009 Cost Summary Activation

## Related Plan

`.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md`

## Implementation Date

2026-08-10

## Summary

Activates the reconciled public cost projection in the owning crawl-and-publish
transaction. The generate job now requires the current run's token ledger
artifact, projects `data/metrics/cost-summary.json` after publish hydration and
ledger overlay, and commits that artifact with the rest of generated state.

## Modified

* `.github/workflows/crawl-and-publish.yml`
  * Fails the analyze job when the token ledger artifact has no source file
  * Fails the generate job when the required ledger artifact cannot be downloaded
  * Runs `scripts/generate_cost_summary.py` before content promotion
  * Uses the canonical analysis timestamp and sponsor-approved
    `--legacy-policy exclude-unidentified`
  * Carries only the public `cost-summary.json` through the generated-content
    artifact, removes the checked-in copy, and verifies the artifact-restored
    file exists before the same-run Hugo deployment
* `scripts/generate_cost_summary.py`
  * Allows an identified accepted `model: none` record to produce an honest
    reconciled zero-cost projection
  * Fails with an explicit reconciliation error when legacy exclusion leaves no
    identified accepted record
* `tests/test_generate_cost_summary.py`
  * Covers valid no-AI zero-cost projection, the first legacy-plus-no-AI run,
    malformed ledger CLI failure, and empty identified-set rejection
* `tests/test_pipeline.py`
  * Enforces fail-closed artifact transport, activation arguments, and
    hydration, overlay, projection, and commit ordering
* `.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md`
  * Marks BR-009 activation complete and records its operational boundaries

## Crawl Continuity

The checked-in ledger contains only legacy rows, but every publishing analysis
path appends an identified record before artifact upload. A synthetic first-run
test combining the historical ledger with an identified `model: none` W33 row
produced a reconciled artifact with one accepted record, one excluded no-AI
billing record, six excluded legacy rows, and zero cost. The pipeline therefore
continues when no-AI is the accepted attempt while still failing if transport
loses the current identified row.

## Validation

* Focused final transport contract: 1 passed
* Affected workflow, generator, renderer, and schema tests: 80 passed
* Cost generator boundary tests: 11 passed
* Full pytest suite: 1,588 passed with 2 expected URL-image warnings
* Ruff check and format: passed
* Workflow YAML parse: passed
* Git diff check: passed
* Synthetic first activated no-AI crawl projection: passed
* Zizmor 1.27.0 blocking medium/high scan: no findings
* Checkov GitHub Actions scan: 894 passed, 0 failed
* Hugo 0.147.9 production build: 2,707 pages, 8 aliases
* URL final review: accepted
* Hermes final security review: accepted
* Leela final architecture review: accepted
* Fry final test review: accepted with non-blocking follow-ups

## Completion

* Implementation: 100%
* Automated validation: 100%
* Required role review: 100%
* Branch publication: pending commit, push, pull request, and remote checks

## Deviations

The initial activation design retained warning-only ledger download behavior.
Reviewing the owning transaction showed that this would permit a stale summary
that omitted the current run. Activation therefore makes ledger upload and
download required. The generator also needed one crawl-continuity correction:
the BRD excludes `model: none` billing but does not prohibit a valid no-AI run,
so an identified no-AI accepted attempt now emits a reconciled zero instead of
blocking publication. Independent URL, Leela, and Fry reviews then found that
the first implementation committed the summary to `publish` but omitted it from
the same-run deployment artifact. The final implementation transports that one
public file explicitly and blocks the inline deployment if it is absent.
Hermes then identified that the checked-in summary could satisfy the existence
check if artifact transport regressed. The deploy now removes that copy before
download, so only the current run's artifact can satisfy verification.