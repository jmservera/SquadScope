# Review: CKV_GHA_7 workflow_dispatch remediation

## Scope and Evidence

* Task ID: RPI-CKV-GHA-7-816
* Review date: 2026-09-28
* Review scope: full task P01
* Assessed boundary: jmservera/SquadScope#816 requirements, six named workflows, Checkov SARIF upload path, input validation, tests, docs, and RPI artifacts.
* Plan: .copilot-tracking/plans/2026-09-28/ckv-gha-7-workflow-dispatch-plan.md
* Phase details: .copilot-tracking/details/2026-09-28/ckv-gha-7-workflow-dispatch-phase-details.md
* Plan critique: .copilot-tracking/reviews/plans/2026-09-28/ckv-gha-7-workflow-dispatch-plan-critique.md
* Changes: .copilot-tracking/changes/2026-09-28/ckv-gha-7-workflow-dispatch-changes.md
* Other evidence considered: .copilot-tracking/research/2026-09-28/ckv-gha-7-workflow-dispatch-research.md, local validation command outputs, and current git diff.

## Opening Review State

* Interpreted review goal: determine whether implementation satisfies the approved plan and jmservera/SquadScope#816 without weakening scanner gates or breaking operator workflows.
* Review scope: full task P01.
* Evidence readiness: plan, details, critique, research, changes record, implementation diff, and validation evidence are available.
* Acceptance basis: user requirements, plan acceptance criteria, and critique findings PC-001 through PC-003.
* First comparison boundary: Checkov SARIF behavior, workflow input validation before first use, tests/docs, and PR-readiness state.
* Active read-only boundaries: review creates only this review record.
* Initial blockers: none.

## Execution Status

* Execution status: Complete
* Review execution evidence: reviewed current artifacts and diff on 2026-09-28 after local validation passed.

## Plan-to-Change Reconciliation

| Current plan scope | Descriptive changes-record summary | Current-state reconciliation | Gap or rationale |
|---|---|---|---|
| P01-T01 | Checkov SARIF upload filtering | Reconciled | `scripts/filter_checkov_sarif.py` removes in-source suppressions; `.github/workflows/checkov.yml` runs it before upload; tests cover retained unsuppressed findings. |
| P01-T02 | Workflow input hardening | Reconciled | Restore manifest and Podcaster smoke inputs are allowlisted before use; build-cost checkout uses `github.sha` before admitting user SHA. |
| P01-T03 | Documentation and regression coverage | Reconciled | Tests and Checkov baseline docs updated. |
| P01-T04 | Validate, commit, push, PR | Reconciled for local validation; publication proceeds after review record | Local validation is complete; commit/PR evidence is operationally recorded after this read-only review stage. |
| Follow-Up Items | Hosted alert closure confirmation after merge | Reconciled | Correctly distinct from active implementation because GitHub closes default-branch alerts after hosted SARIF upload. |

## Completed Work Assessment

| Related marker | Files | What changed and why | Completion evidence | Validation | Assessment |
|---|---|---|---|---|---|
| P01-T01 | `.github/workflows/checkov.yml`, `scripts/filter_checkov_sarif.py`, `tests/test_filter_checkov_sarif.py`, `tests/test_checkov_workflow.py` | Added in-source-suppressed SARIF result filtering before Code Scanning upload while retaining blocking Checkov CLI. | SARIF proof removed 7 suppressed results and left 0 CKV_GHA_7 upload results. | Passed targeted pytest, Ruff, actionlint, Checkov CKV_GHA_7, pinned Zizmor. | Reconciled. |
| P01-T02 | `.github/workflows/build-cost-experiment.yml`, `.github/workflows/podcaster-handoff-smoke.yml`, `.github/workflows/restore-publish-backup.yml` | Added/retained validation before operator inputs influence checkout, restore, or script execution. | Workflow tests assert guard text and checkout behavior. | Passed targeted pytest and actionlint. | Reconciled. |
| P01-T03 | `docs/devsecops/checkov-baseline.md`, workflow tests | Documented current Checkov enforcement and SARIF filtering; added regression coverage. | Tests and docs match implementation behavior. | Passed targeted pytest. | Reconciled. |
| P01-T04 | validation state and PR-ready branch | Completed local validation and artifact reconciliation. | Validation record in changes log. | Passed all requested local validations available in the environment. | Reconciled; publication is next operational step. |

## Implementation-Time Plan and Detail Update Assessment

| Affected area or marker | What changed and why | Triggering evidence and user decision | Reconciliation performed | Planning and critique state | Assessment |
|---|---|---|---|---|---|
| P01-T02 | Minimal `build-cost-experiment.yml` checkout changed to `github.sha` before user SHA admission. | User warned about jmservera/SquadScope#817 overlap; implementation evidence showed validation should happen before using operator SHA as checkout ref. | Plan/details/changes record note overlap and rationale. | PC-003 remains satisfied because edit is minimal and PR body must mention overlap. | Reconciled. |

## Critique and Material Revision Assessment

* Latest critique dispositions: PC-001, PC-002, and PC-003 are addressed by tests, workflow guards, and minimal build-cost overlap.
* Material revisions: none requiring replanning; `build-cost-experiment.yml` change preserves user intent and issue acceptance criteria.
* Dependent-work pause assessment: no dependent work resumed early after a material decision gap.
* Justification assessment: supported by research evidence and validation.

## Plan Follow-Up Assessment

| Follow-up item | Why outside immediate scope | Owner or next action | Assessment and route |
|---|---|---|---|
| After merge, confirm main branch Checkov code-scanning run closes alerts #1175, #1178, #1179, #1194, #1195, and #1226. | GitHub Code Scanning alert state changes after hosted default-branch SARIF ingestion. | PR/merge operator or follow-up automation. | Distinct follow-up; not an implementation defect. |

## Findings

* None.

## Defects

* None.

## Routed Findings

| Finding | Destination | Owner or next action | Reason for route |
|---|---|---|---|
| none | none | none | no defects, decision gaps, or evidence gaps found |

Later implementation of a routed finding does not require another Review.

## Residual Work

* Hosted alert closure confirmation after merge remains distinct follow-up work.

## Blockers and Remaining Work

* Blockers: none.
* Remaining active work: none.

## Validation Evidence

| Command | Scope | Status | Summary |
|---|---|---|---|
| `python3 -m ruff check scripts/filter_checkov_sarif.py tests/test_filter_checkov_sarif.py tests/test_checkov_workflow.py` | new Python script/tests | Passed | All checks passed. |
| `python3 -m ruff format --check scripts/filter_checkov_sarif.py tests/test_filter_checkov_sarif.py tests/test_checkov_workflow.py` | new Python script/tests | Passed | Files formatted after one test file was reformatted. |
| `python3 -m pytest tests/test_filter_checkov_sarif.py tests/test_checkov_workflow.py tests/test_sync_publish_workflow.py tests/test_build_cost_experiment.py tests/test_pipeline.py -q` | workflow/filter regression tests | Passed | 77 passed. |
| `/tmp/actionlint-venv/bin/actionlint ...` | seven relevant workflows | Passed | No output; exit 0. |
| `checkov -d .github/workflows --check CKV_GHA_7 --quiet` | GitHub Actions workflows | Passed | 20 passed, 0 failed, 7 skipped. |
| `zizmor==1.27.0 --persona regular --min-severity medium .github/workflows/` | all workflows | Passed | No findings to report. |
| Checkov SARIF proof with `scripts/filter_checkov_sarif.py` | full Checkov SARIF upload file | Passed | Removed 7 in-source-suppressed results; 0 suppressed and 0 CKV_GHA_7 results remained. |

## Outcome

* Outcome: Conformant
* Outcome rationale: implementation satisfies the approved plan and user acceptance criteria. It addresses the evidenced SARIF upload root cause, adds missing input allowlists, preserves scanner enforcement and operational workflows, and passes relevant local validation.

## Closeout Routing Record

| Finding class | Destination | Owner or next action |
|---|---|---|
| Implementation defect | none | none |
| Decision gap or invalid assumption | none | none |
| Material evidence gap | none | none |
| Non-blocking residual work | follow-up | confirm GitHub code-scanning alerts close after default-branch SARIF upload |

* Execution status: Complete
* Outcome: Conformant
* Validation coverage: targeted pytest, Ruff, actionlint, Checkov CKV_GHA_7, pinned Zizmor, and SARIF proof passed.
* Blockers: none.
