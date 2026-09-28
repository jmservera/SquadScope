# RPI Plan: CKV_GHA_7 workflow_dispatch remediation

## Task Metadata

* Task ID: RPI-CKV-GHA-7-816
* Task slug: ckv-gha-7-workflow-dispatch
* Planning status: Ready
* Plan date: 2026-09-28
* Phase details: .copilot-tracking/details/2026-09-28/ckv-gha-7-workflow-dispatch-phase-details.md
* Plan critique: .copilot-tracking/reviews/plans/2026-09-28/ckv-gha-7-workflow-dispatch-plan-critique.md

## Executive Summary

This plan resolves jmservera/SquadScope#816 by addressing the actual reason CKV_GHA_7 alerts remain open: Checkov accepts the inline skips locally, but the CI job uploads suppressed Checkov SARIF `warning` results to GitHub Code Scanning. The implementation will preserve the blocking Checkov CLI gate, remove only in-source-suppressed SARIF results before upload, and harden the remaining operator inputs with allowlist validation before path/ref/script use.

### User Decisions and Requirements Highlights

* Keep all six manual workflows operational; justified CKV_GHA_7 skips are acceptable only for intentionally operator-controlled and validated inputs.
* Do not weaken Checkov or CodeQL configuration and do not dismiss alerts manually.
* Base work on `origin/main`; keep `build-cost-experiment.yml` changes minimal because jmservera/SquadScope#817 overlaps that workflow.
* Commit `.copilot-tracking` artifacts and open a PR closing jmservera/SquadScope#816.

### What You May Not Know

* Local Checkov already reports 0 CKV_GHA_7 failures and 7 skipped checks, so moving skip comments is not the main fix.
* GitHub Code Scanning alerts persist because uploaded SARIF still contains suppressed CKV_GHA_7 results.

### Unresolved Decisions or Blockers

* None.

For current user input, see [User Decisions and Requirements](#user-decisions-and-requirements).

## User Decisions and Requirements

* Resolve Checkov CKV_GHA_7 alerts #1175, #1178, #1179, #1194, #1195, and #1226 for the six named workflows.
* Determine why alerts remain open despite existing CKV_GHA_7 skips and runtime validation.
* Ensure every `workflow_dispatch` input is strictly validated: choice/boolean where possible, regex allowlists for SHAs/IDs/paths before use, and env-passed into shell scripts rather than interpolated directly into `run:`.
* Preserve operational functionality.
* Keep justified skips only for intentionally operator-controlled, validated inputs.
* Do not weaken Checkov/CodeQL config or dismiss alerts.
* Coordinate overlap with jmservera/SquadScope#817 by minimizing `build-cost-experiment.yml` edits and noting overlap in the PR.
* Validate with actionlint, Checkov CKV_GHA_7, Zizmor, and relevant pytest.
* Push a branch and create a PR with `Closes jmservera/SquadScope#816`.
* Record decisions via Squad state at `decisions/inbox/basher-ckv-gha-7.md`.

## Goals

* Close the durable cause of CKV_GHA_7 code-scanning alerts without hiding unsuppressed Checkov findings.
* Harden all named workflow dispatch inputs before use.
* Keep recovery, promotion, experiment, and podcast dispatch workflows usable.
* Produce traceable RPI artifacts, validation evidence, and a reviewable PR.

## Scope and Non-Goals

### In Scope

* `.github/workflows/checkov.yml`
* `.github/workflows/auto-podcast-dispatch.yml`
* `.github/workflows/build-cost-experiment.yml`
* `.github/workflows/trigger-podcast.yml`
* `.github/workflows/podcaster-handoff-smoke.yml`
* `.github/workflows/squad-promote.yml`
* `.github/workflows/restore-publish-backup.yml`
* Direct tests and baseline docs for these changes.

### Non-Goals

* Manual alert dismissal.
* Broad scanner exclusions or weakened severity/gate behavior.
* Reworking jmservera/SquadScope#817 cache-poisoning changes.
* Redesigning the podcast or publish pipeline.

## Functional Requirements

* Filter Checkov SARIF before upload so in-source-suppressed results are removed while unsuppressed results remain.
  * Observable acceptance criteria: generated upload SARIF contains no CKV_GHA_7 results with in-source suppressions, and tests prove unsuppressed results are retained.
* Validate manual backup manifest paths before restore/push operations.
  * Observable acceptance criteria: `restore-publish-backup.yml` rejects paths outside `data/backups/<week>/<run>/content/manifest.json`.
* Validate Podcaster smoke manual inputs before `git checkout` or script invocation.
  * Observable acceptance criteria: workflow contains regex guards for week, article URL, article path, SHA-256, and promotion reference.
* Preserve typed `choice`/`boolean` input use where GitHub Actions supports it.
  * Observable acceptance criteria: `squad-promote.yml`, `auto-podcast-dispatch.yml`, and `build-cost-experiment.yml` retain constrained input types.
* Keep inputs passed through environment variables for shell scripts.
  * Observable acceptance criteria: shell scripts consume `$VARS`, not direct `${{ inputs.* }}` interpolation.

## Non-Functional Requirements

* Security scanner integrity.
  * Objective threshold or evaluation condition: no Checkov/CodeQL scope weakening; unsuppressed Checkov findings still fail the CLI gate.
  * Operating condition or verification approach: actionlint, Checkov CKV_GHA_7, full Checkov workflow scan as practical, Zizmor, and pytest.
  * Observable acceptance criteria: validation commands pass or any environment limitation is documented.
* Operational compatibility.
  * Objective threshold or evaluation condition: manual workflows keep their intended inputs and dispatch semantics.
  * Operating condition or verification approach: workflow text tests and actionlint.
  * Observable acceptance criteria: relevant pytest passes.

## Acceptance Criteria

* Root cause of open alerts is documented in RPI artifacts and PR description.
* Six named workflows either already have or receive strict input validation before use.
* Checkov SARIF upload no longer imports in-source-suppressed CKV_GHA_7 results.
* Local validation includes actionlint, Checkov CKV_GHA_7, Zizmor, and relevant pytest.
* Changes are committed, pushed, and opened as a PR closing jmservera/SquadScope#816.
* Squad state decision note is written.

## Implementation Context Record

| Context item | Current artifact or record |
|---|---|
| Plan | .copilot-tracking/plans/2026-09-28/ckv-gha-7-workflow-dispatch-plan.md |
| Phase details | .copilot-tracking/details/2026-09-28/ckv-gha-7-workflow-dispatch-phase-details.md |
| Latest critique | .copilot-tracking/reviews/plans/2026-09-28/ckv-gha-7-workflow-dispatch-plan-critique.md with Pass disposition |
| Relevant research | .copilot-tracking/research/2026-09-28/ckv-gha-7-workflow-dispatch-research.md |
| Changes-record role | .copilot-tracking/changes/2026-09-28/ckv-gha-7-workflow-dispatch-changes.md is created by implementation |
| Planning execution and readiness | Complete and ready |
| Continuation context | confirmed automatic RPI Agent continues to implementation |

## Sources

* .copilot-tracking/research/2026-09-28/ckv-gha-7-workflow-dispatch-research.md: root cause and workflow input evidence.
* `.github/copilot-instructions.md`: branch, PR, validation, and RPI discipline.
* jmservera/SquadScope#816: user acceptance criteria.

## Phase Checklist

<!-- rpi:phase id=P01 -->
### [x] P01: Implement CKV_GHA_7 remediation

* Intent: eliminate suppressed Checkov SARIF alert uploads and harden manual inputs.
* Dependencies: completed research and dedicated branch `squad/816-ckv-gha-7`.

<!-- rpi:task id=P01-T01 -->
#### [x] P01-T01: Add Checkov SARIF suppression filter

* Requirement and evidence: research C1-C3, C10.
* Expected result: Code Scanning upload receives only unsuppressed Checkov SARIF results while the CLI gate remains unchanged.
* Detail section: P01-T01 in .copilot-tracking/details/2026-09-28/ckv-gha-7-workflow-dispatch-phase-details.md.

<!-- rpi:task id=P01-T02 -->
#### [x] P01-T02: Harden workflow dispatch inputs

* Requirement and evidence: research C4-C9.
* Expected result: six workflows have typed/allowlisted inputs before shell/path/ref/script use.
* Detail section: P01-T02 in .copilot-tracking/details/2026-09-28/ckv-gha-7-workflow-dispatch-phase-details.md.

<!-- rpi:task id=P01-T03 -->
#### [x] P01-T03: Update tests and docs

* Requirement and evidence: user validation request and repository conventions.
* Expected result: tests cover SARIF filtering and workflow validation, baseline docs match current behavior.
* Detail section: P01-T03 in .copilot-tracking/details/2026-09-28/ckv-gha-7-workflow-dispatch-phase-details.md.

<!-- rpi:task id=P01-T04 -->
#### [x] P01-T04: Validate, commit, push, and open PR

* Requirement and evidence: user final output requirements and repository PR workflow.
* Expected result: branch is pushed and PR is opened with required issue closure, overlap note, and validation evidence.
* Detail section: P01-T04 in .copilot-tracking/details/2026-09-28/ckv-gha-7-workflow-dispatch-phase-details.md.

## Dependencies

* GitHub Code Scanning upload behavior: closure requires hosted Checkov run after PR merge to main.
* jmservera/SquadScope#817: overlapping `build-cost-experiment.yml`; avoid nonessential edits.

## Critique Disposition

| Critique run and finding | Disposition | Plan response or residual risk |
|---|---|---|
| self-critique: preserve scanner gate | resolved | Plan filters only suppressed SARIF upload results and keeps CLI gate unchanged. |
| self-critique: validate before first use | resolved | Plan explicitly adds validation before `git checkout`, restore, or script calls. |
| self-critique: PR #817 overlap | resolved | Plan limits build-cost workflow edits and requires PR note. |

## Follow-Up Items

* After merge, confirm main branch Checkov code-scanning run closes jmservera/SquadScope alerts #1175, #1178, #1179, #1194, #1195, and #1226.

## Handoff

* Implementation artifact: .copilot-tracking/changes/2026-09-28/ckv-gha-7-workflow-dispatch-changes.md
* Ready phase or task: review
* Remaining provisional question or blocker: none
