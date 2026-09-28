# RPI Phase Details: CKV_GHA_7 workflow_dispatch remediation

## Metadata

* Task ID: RPI-CKV-GHA-7-816
* Task slug: ckv-gha-7-workflow-dispatch
* Related plan: .copilot-tracking/plans/2026-09-28/ckv-gha-7-workflow-dispatch-plan.md
* Evidence sources: .copilot-tracking/research/2026-09-28/ckv-gha-7-workflow-dispatch-research.md

## Phase Index

| Phase ID | Name | Status | Detail sections |
|---|---|---|---|
| P01 | Implement CKV_GHA_7 remediation | Complete | P01, P01-T01 through P01-T04 |

<!-- rpi:phase id=P01 -->
## P01: Implement CKV_GHA_7 remediation

### Context

The six target workflows already carry CKV_GHA_7 skip comments that Checkov accepts locally. The open GitHub alerts remain because Checkov SARIF includes suppressed `warning` results and `.github/workflows/checkov.yml` uploads the raw SARIF. Some workflows also need clearer pre-use validation for operator inputs.

### Intent

Implement a minimal, auditable fix that removes accepted suppressed Checkov findings from SARIF upload, validates workflow inputs before use, and preserves operator functionality.

### Boundaries

* Included: scanner upload post-processing, workflow validation guards, direct tests/docs/RPI artifacts.
* Excluded: scanner scope weakening, manual alert dismissal, broad workflow redesign, PR #817 cache-poisoning work.

### Likely Targets

* `.github/workflows/checkov.yml`: add SARIF post-filter step before upload.
* A script under `scripts/`: implement reusable SARIF filtering logic.
* `tests/`: add unit/workflow tests.
* `.github/workflows/restore-publish-backup.yml`: add backup manifest allowlist.
* `.github/workflows/podcaster-handoff-smoke.yml`: add manual input allowlists before checkout.
* `docs/devsecops/checkov-baseline.md`: document current SARIF filtering behavior and skip count.

### Dependencies

* Research artifact complete.
* Branch `squad/816-ckv-gha-7` exists in `/home/azureuser/source/SquadScope-wt-816`.

### Validation Expectations

* `pytest -q` for new SARIF filter tests and relevant workflow tests.
* `actionlint` over changed workflows.
* `checkov -d .github/workflows --check CKV_GHA_7`.
* `zizmor --persona regular --min-severity medium .github/workflows/`.

### Completion Evidence

* Passing validation commands.
* Git commit, pushed branch, and PR URL.
* Squad decision note written.

### Unresolved Items

* None.

<!-- rpi:task id=P01-T01 -->
### P01-T01: Add Checkov SARIF suppression filter

#### Context

Local SARIF shows CKV_GHA_7 results with `suppressions.kind == "inSource"` and `level == "warning"`. Uploading those results keeps accepted findings visible as open code-scanning alerts.

#### Intent

Remove only in-source-suppressed results from the SARIF file uploaded to GitHub Code Scanning, while preserving unsuppressed findings and the raw CLI gate.

#### Boundaries

* Included: script and tests; Checkov workflow post-processing step.
* Excluded: changing Checkov command scope, `--soft-fail`, CodeQL upload action, or skip reasons.

#### Likely Targets

* `scripts/filter_checkov_sarif.py`
* `tests/test_filter_checkov_sarif.py`
* `.github/workflows/checkov.yml`

#### Dependencies

* None beyond research evidence.

#### Validation Expectations

* Unit tests prove suppressed results are removed and unsuppressed results remain.
* Checkov workflow still generates CLI and SARIF outputs.

#### Completion Evidence

* Tests pass and local filtered SARIF has no suppressed CKV_GHA_7 result uploads. Completed by `scripts/filter_checkov_sarif.py`, Checkov workflow wiring, unit tests, and explicit SARIF proof showing 7 removed suppressed results and 0 remaining CKV_GHA_7 upload results.

#### Unresolved Items

* None.

<!-- rpi:task id=P01-T02 -->
### P01-T02: Harden workflow dispatch inputs

#### Context

The workflows already env-pass most inputs, but `restore-publish-backup.yml` and `podcaster-handoff-smoke.yml` need explicit allowlists before first path/ref use. Other named workflows need preservation of existing constraints and minor documentation/test coverage.

#### Intent

Ensure every manual input is choice/boolean where possible or regex validated before use.

#### Boundaries

* Included: shell validation guards and test assertions.
* Excluded: replacing operator inputs with different workflow contracts.

#### Likely Targets

* `.github/workflows/restore-publish-backup.yml`
* `.github/workflows/podcaster-handoff-smoke.yml`
* `.github/workflows/build-cost-experiment.yml` only if a minimal validation/test-aligned clarification is required.
* `.github/workflows/trigger-podcast.yml`, `.github/workflows/auto-podcast-dispatch.yml`, `.github/workflows/squad-promote.yml` only for minimal validation/test/doc alignment.

#### Dependencies

* Preserve PR #817 overlap constraints.

#### Validation Expectations

* actionlint passes.
* Related pytest workflow assertions pass.

#### Completion Evidence

* Validation guards appear before `git checkout`/restore/script calls and tests assert them. Completed for restore backup manifests, Podcaster smoke inputs, and build-cost checkout admission via `github.sha`.

#### Unresolved Items

* None.

<!-- rpi:task id=P01-T03 -->
### P01-T03: Update tests and docs

#### Context

Repository convention uses direct pytest workflow text tests and devsecops baseline docs.

#### Intent

Capture regression coverage for SARIF filtering and input validation, and update docs so future maintainers know why upload SARIF is filtered.

#### Boundaries

* Included: focused tests and devsecops docs.
* Excluded: broad test rewrites.

#### Likely Targets

* `tests/test_filter_checkov_sarif.py`
* `tests/test_sync_publish_workflow.py`
* possibly existing podcaster/build-cost workflow tests.
* `docs/devsecops/checkov-baseline.md`

#### Dependencies

* Implementation changes exist.

#### Validation Expectations

* Focused pytest passes.

#### Completion Evidence

* Tests fail on missing guard/filter behavior and pass after implementation. Completed with `tests/test_filter_checkov_sarif.py`, `tests/test_checkov_workflow.py`, and workflow test updates.

#### Unresolved Items

* None.

<!-- rpi:task id=P01-T04 -->
### P01-T04: Validate, commit, push, and open PR

#### Context

User requested validation, commit trailer, push, PR creation, CI watch, and final concise output.

#### Intent

Deliver the change through the repository PR workflow.

#### Boundaries

* Included: local validation, commit, push, PR creation, initial CI watch/fix cycle where possible.
* Excluded: merging PR without explicit human approval.

#### Likely Targets

* Git branch `squad/816-ckv-gha-7`
* PR body
* Squad state key `decisions/inbox/basher-ckv-gha-7.md`

#### Dependencies

* P01-T01 through P01-T03 complete.

#### Validation Expectations

* Required local commands have recorded outcomes.
* CI status reported from GitHub.

#### Completion Evidence

* Commit hash, PR URL, CI status, and Squad state write. Commit/PR/CI status are recorded by P01-T04 closeout after publication.

#### Unresolved Items

* Hosted code-scanning alert closure can only be fully observed after main branch SARIF upload post-merge.
