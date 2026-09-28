# RPI Changes: CKV_GHA_7 workflow_dispatch remediation

## Metadata

* Task ID: RPI-CKV-GHA-7-816
* Related plan: .copilot-tracking/plans/2026-09-28/ckv-gha-7-workflow-dispatch-plan.md
* Phase details: .copilot-tracking/details/2026-09-28/ckv-gha-7-workflow-dispatch-phase-details.md
* Implementation date: 2026-09-28

## Execution Status

* Status: Complete
* Declared invocation scope: full plan P01
* Completed scope markers: P01, P01-T01, P01-T02, P01-T03, P01-T04
* All remaining active-plan markers: none
* Status basis: implementation, focused tests, actionlint, Checkov CKV_GHA_7, pinned Zizmor, and SARIF proof completed locally; publication evidence is added after commit/PR creation.

## Execution Summary

Implemented a Checkov SARIF upload filter for accepted in-source suppressions, added missing workflow input allowlists, kept build-cost checkout pinned to the reviewed workflow commit, updated tests/docs, and completed local validation.

## Completed Work

### Checkov SARIF upload filtering

* Related phase or task: P01-T01
* Files: `.github/workflows/checkov.yml`, `scripts/filter_checkov_sarif.py`, `tests/test_filter_checkov_sarif.py`, `tests/test_checkov_workflow.py`
* What changed and why: added a post-processing step that removes only SARIF results Checkov already marked with `suppressions.kind == "inSource"` before upload to Code Scanning. This keeps the blocking CLI gate intact while preventing accepted CKV_GHA_7 skips from remaining open as alerts.
* Completion evidence: explicit SARIF proof removed 7 in-source-suppressed results and left 0 CKV_GHA_7 upload results.
* Validation: targeted pytest, Ruff, actionlint, Checkov CKV_GHA_7, and pinned Zizmor passed.

### Workflow input hardening

* Related phase or task: P01-T02
* Files: `.github/workflows/build-cost-experiment.yml`, `.github/workflows/podcaster-handoff-smoke.yml`, `.github/workflows/restore-publish-backup.yml`
* What changed and why: build-cost now checks out `${{ github.sha }}` before admitting `reviewed_main_sha`; restore backup validates the immutable backup manifest path before restore/commit; Podcaster smoke validates week, URL, article path, SHA-256, and promotion reference before publish-branch checkout or handoff scripts.
* Completion evidence: workflow tests assert the new guards and checkout behavior.
* Validation: targeted pytest and actionlint passed.

### Documentation and regression coverage

* Related phase or task: P01-T03
* Files: `docs/devsecops/checkov-baseline.md`, `tests/test_build_cost_experiment.py`, `tests/test_pipeline.py`, `tests/test_sync_publish_workflow.py`
* What changed and why: documented current enforced Checkov behavior, SARIF filtering, and 7 accepted CKV_GHA_7 skips; added tests for the hardened workflow contracts.
* Completion evidence: targeted pytest passed.
* Validation: targeted pytest passed.

## Implementation-Time Plan and Detail Updates

No material plan divergence identified. The implementation followed the plan; the only notable current-state update is the minimal `build-cost-experiment.yml` checkout change, which intentionally overlaps jmservera/SquadScope#817 and is required to validate `reviewed_main_sha` before using any operator-supplied ref.

## Validation Record

| Check | Scope | Status | Evidence or reason |
|---|---|---|---|
| Ruff | new Python script/tests | Passed | `python3 -m ruff check scripts/filter_checkov_sarif.py tests/test_filter_checkov_sarif.py tests/test_checkov_workflow.py` |
| pytest | targeted workflow/filter tests | Passed | `python3 -m pytest tests/test_filter_checkov_sarif.py tests/test_checkov_workflow.py tests/test_sync_publish_workflow.py tests/test_build_cost_experiment.py tests/test_pipeline.py -q` -> 77 passed |
| actionlint | changed workflows | Passed | `/tmp/actionlint-venv/bin/actionlint ...` over seven relevant workflows |
| checkov CKV_GHA_7 | `.github/workflows` | Passed | `checkov -d .github/workflows --check CKV_GHA_7 --quiet` -> 20 passed, 0 failed, 7 skipped |
| zizmor | `.github/workflows` | Passed | `zizmor==1.27.0 --persona regular --min-severity medium .github/workflows/` -> no findings |
| SARIF proof | full Checkov SARIF upload file | Passed | `scripts/filter_checkov_sarif.py` removed 7 in-source-suppressed results; 0 suppressed and 0 CKV_GHA_7 results remained |

## Pre-Review Reconciliation

* Plan markers and phase details: current.
* Completed-work evidence and handoff prose: current.
* Validation, blockers, remaining work, and follow-up items: current.
* Review readiness: ready for RPI review after commit/PR publication evidence is appended.

## Blockers

* None.

## Remaining Work

* None.

## Follow-Up Items

* Canonical plan list: .copilot-tracking/plans/2026-09-28/ckv-gha-7-workflow-dispatch-plan.md, `## Follow-Up Items`
* After merge, confirm main branch Checkov code-scanning run closes jmservera/SquadScope alerts #1175, #1178, #1179, #1194, #1195, and #1226.

## Return-to-Caller State

* Implementation execution status: Complete
* Declared scope and markers: full plan P01; P01 through P01-T04 complete
* Validation coverage: targeted pytest, Ruff, actionlint, Checkov CKV_GHA_7, pinned Zizmor, and SARIF proof passed
* Blockers: none
* Current plan and detail updates: markers reconciled complete
* Planning and critique state: ready / pass
* Follow-up items: hosted alert closure confirmation after merge
* Review readiness or no-handoff reason: ready for RPI review after PR publication evidence
* Continuation owner: confirmed automatic RPI Agent
