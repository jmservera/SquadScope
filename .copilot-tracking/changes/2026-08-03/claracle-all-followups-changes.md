<!-- markdownlint-disable-file -->
# Changes Log: Claracle All Follow-Ups

## Related Plan

`.copilot-tracking/plans/2026-08-03/claracle-all-followups-plan.instructions.md`

## Implementation Date

2026-08-03

## Summary

Implemented all repository-executable follow-ups: isolated atomic publication proof,
protected exact-run Podcaster generation, report-only cost measurement, UX and Lighthouse
hardening, and explicit human acceptance handoffs.

## Added

* `.copilot-tracking/research/2026-08-03/claracle-all-followups-research.md`
* `.copilot-tracking/plans/2026-08-03/claracle-all-followups-plan.instructions.md`
* `.copilot-tracking/details/2026-08-03/claracle-all-followups-details.md`
* `.copilot-tracking/plans/logs/2026-08-03/claracle-all-followups-log.md`
* `.copilot-tracking/changes/2026-08-03/claracle-all-followups-changes.md`
* `.github/workflows/atomic-publish-proof.yml`
* `.github/workflows/build-cost-experiment.yml`
* `scripts/atomic_publish_proof.py`
* `scripts/build_cost_experiment.py`
* `tests/lighthouse-gates.test.mjs`
* `tests/test_atomic_publish_proof.py`
* `tests/test_build_cost_experiment.py`
* `tests/test_page_css_bundles.py`
* `tests/test_serve_static.py`

## Modified

* `.github/workflows/crawl-and-publish.yml`
* `.github/workflows/sync-publish-to-main.yml`
* `.github/workflows/trigger-podcast.yml`
* `architecture.md`
* `assets/css/extended/trend-explorer.css`
* `assets/js/star-velocity-explorer.js`
* `docs/design/visual-verification.md`
* `docs/devsecops/checkov-baseline.md`
* `docs/operator-guide.md`
* `docs/pipeline-validation.md`
* `docs/qa-gates.md`
* `docs/review/data-observatory-relaunch/owner-action-register.md`
* `docs/review/data-observatory-relaunch/status-of-record.md`
* `layouts/partials/head.html`
* `layouts/tools/single.html`
* `requirements.txt`
* `scripts/design/lighthouse-gates.mjs`
* `scripts/podcaster_handoff.py`
* `scripts/serve_static.py`
* `tests/test_pipeline.py`
* `tests/test_podcaster_handoff.py`
* `tests/test_sync_publish_workflow.py`
* `tests/test_trend_explorer_tool.py`
* `tests/visual/observatory-a11y.spec.mjs`

## Validation

* Combined focused Python suite: 127 passed, 2 skipped, 26 subtests passed
* Full Python suite: 1,434 passed, 20 skipped, 2 expected warnings, 34 subtests passed
* Protected Podcaster workflow contracts: 30 passed, 19 subtests passed
* Lighthouse Node suite: 2 passed
* Ruff check and format check: passed
* Diff whitespace check: passed
* Checkov: 843 passed, 0 failed, 5 skipped
* Zizmor: 0 medium or high findings; one unrelated existing low-severity finding

Full Hugo, Playwright, Lighthouse, and retained manual workflow evidence require CI because
the local environment lacks Hugo and browser runtime dependencies.