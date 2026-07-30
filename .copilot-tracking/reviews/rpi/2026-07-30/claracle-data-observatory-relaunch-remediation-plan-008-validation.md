---
title: Claracle Data Observatory Remediation Phase 8 Validation
description: RPI validation of the Phase 8 Podcaster release smoke implementation and external acceptance evidence
ms.date: 2026-07-30
---
<!-- markdownlint-disable-file -->

## Validation Scope

* Plan: `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md`
* Changes log: `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md`
* Research: `.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md`
* Phase: 8, Podcaster Release Smoke
* Validation date: 2026-07-30
* Status: Failed
* Current PR: Open, `Operationalize Claracle data observatory relaunch`, branch `feat/observatory-relaunch-remediation`

Phase 8 fails because the current PR does not guarantee that the downstream payload contains the exact promoted article bytes, and no successful protected downstream run is retained. Repository orchestration is present, but repository implementation and external acceptance are separate gates.

## Phase Requirements

### Step 8.1 Reusable Exact-Release Smoke

The plan marks Step 8.1 complete at `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md:224`. The implementation details require manual dispatch plus `workflow_call`, exact article path, URL, hash, and promotion reference inputs, no shared config or payload-contract changes, and validation of exact promoted bytes against the downstream dry-run endpoint at `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:377-388`.

The research independently requires the exact promoted release payload through a reusable workflow at `.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:31`.

### Step 8.2 Invocation and Retained Evidence

The plan leaves Step 8.2 open at `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md:226`. The caller must run after successful deployment, use the protected environment, retain an Actions run URL, and block relaunch acceptance on failure at `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:393-406`.

The successful downstream endpoint result is external evidence that repository analysis cannot manufacture, as stated at `.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:31` and `.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:52`.

## Plan-to-Changes Comparison

| Plan item | Changes log claim | Verified status |
|-----------|-------------------|-----------------|
| Step 8.1 reusable workflow | Implementation complete; 72 focused tests passed | Partial. Reusable inputs and exact-release source validation exist, but exact article bytes are not guaranteed in the emitted payload. |
| Step 8.1 unchanged shared contract | No `config/podcast.json` or `scripts/podcaster_handoff.py` contract change | Partial. The PR does not alter the shared contract for Phase 8, but existing payload truncation conflicts with the new exact-byte requirement. |
| Step 8.2 post-deploy caller | Deployment invokes the protected smoke | Implemented in repository source. |
| Step 8.2 retained downstream success | Protected run and URL pending deployment | Not complete. No external acceptance evidence exists. |

The changes log correctly identifies the missing protected run at `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:21` and `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:192-198`. Its statement that repository implementation is complete is contradicted by the exact-byte behavior below.

## Verified Repository Evidence

### Reusable Workflow

* Manual dispatch and `workflow_call` expose the five required inputs at `.github/workflows/podcaster-handoff-smoke.yml:4-51`.
* The workflow checks out `publish`, validates the promotion record, compares the retained article hash, and derives the source manifest and publish run at `.github/workflows/podcaster-handoff-smoke.yml:69-171`.
* The protected `podcaster-release-smoke` environment owns endpoint variables and secrets at `.github/workflows/podcaster-handoff-smoke.yml:59-65` and `.github/workflows/podcaster-handoff-smoke.yml:173-184`.
* The workflow records status, article path, hash, and Actions run URL in the job summary at `.github/workflows/podcaster-handoff-smoke.yml:237-251`.

### Caller

* Deployment resolves the latest retained promotion record and verifies the promoted file hash at `.github/workflows/deploy-site.yml:122-170`.
* The reusable smoke depends on both build and deploy and receives the resolved week, URL, path, hash, and promotion reference at `.github/workflows/deploy-site.yml:199-210`.
* Failure notification depends on the smoke job at `.github/workflows/deploy-site.yml:212-214`, so a failed smoke remains visible and prevents a fully successful deployment workflow.

### Tests

* The caller test verifies post-deploy dependencies and exact-release input mapping at `tests/test_pipeline.py:211-247`.
* The reusable-workflow test verifies workflow shape and searches the shell source for expected assertions at `tests/test_pipeline.py:656-711`.
* The payload test proves exact bytes only for a short fixture at `tests/test_podcaster_handoff.py:288-318`.
* The changes log records 72 focused tests and eight subtests as passed at `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:192-196`. A fresh test result could not be obtained in this validation session because the terminal integration replayed stale output; the recorded result is not represented as re-executed evidence.

## External Acceptance Evidence

No protected Podcaster Actions run URL or downstream response artifact is present. The changes log explicitly records the execution and URL as pending at `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:198`. The planning log likewise states that local workflow tests cannot substitute for the downstream endpoint at `.copilot-tracking/plans/logs/2026-07-29/claracle-data-observatory-relaunch-remediation-log.md:58-61`.

Repository implementation status: Partial.

External acceptance status: Not started or not evidenced.

## Findings

### Critical Findings

#### RPI-008-C01 Exact Promoted Bytes Are Not Guaranteed

The payload builder truncates article content to 50,000 characters at `scripts/podcaster_handoff.py:20` and `scripts/podcaster_handoff.py:524-555`, while retaining the manifest hash for the complete article at `scripts/podcaster_handoff.py:686-703`. The reusable workflow attempts to compare payload content and hash to the complete article, but both comparisons are indented inside the `if not payload["source_artifacts"]` branch after an unconditional `raise`, making them unreachable at `.github/workflows/podcaster-handoff-smoke.yml:219-225`.

An article longer than 50,000 characters therefore cannot be sent as the exact promoted bytes required by Step 8.1. The repository explicitly tests and preserves truncation at `tests/test_podcaster_handoff.py:1072-1092`. This contradicts the exact-release requirement and invalidates the plan's completed status for Step 8.1.

Required correction: define an exact-release payload path that does not truncate the promoted article, move the content and hash comparisons outside the missing-field branch, and execute the inline verifier in a focused test.

#### RPI-008-C02 Protected Downstream Acceptance Is Missing

No successful protected smoke run or Actions URL is retained. Step 8.2 requires both at `.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:393-403`, and the changes log confirms they remain pending at `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:198`.

This is an external acceptance gap, not evidence that the caller source is absent. Relaunch acceptance remains blocked until a corrected workflow succeeds against the downstream dry-run endpoint for the exact relaunch state.

### Major Findings

#### RPI-008-M01 Workflow Tests Do Not Execute the Inline Verifier

The reusable-workflow test checks only for source strings at `tests/test_pipeline.py:682-711`. It neither compiles nor executes the two embedded Python programs, so the unreachable exact-byte checks pass review unnoticed. The short-article payload test at `tests/test_podcaster_handoff.py:288-318` does not exercise the documented 50,000-character boundary.

Required correction: extract and execute the workflow verifier against valid, invalid, and over-limit fixtures, including a payload-content mismatch that must fail before the network request.

### Minor Findings

No minor Phase 8 findings were identified.

## Coverage Assessment

* Step 8.1: Partial. Reusable triggers, inputs, protected environment use, promotion verification, downstream invocation, and summary evidence are implemented. Exact promoted payload bytes are not guaranteed.
* Step 8.2 repository implementation: Implemented. The deployment caller waits for build and deploy and passes exact release identifiers.
* Step 8.2 external acceptance: Missing. No successful protected run or retained URL exists.
* Overall Phase 8 coverage: Partial by checklist count, but validation status is Failed because both the exact-byte contract and required external acceptance gate are critical.

## Clarifying Questions

* Must Podcaster continue enforcing the general 50,000-character article limit, or may the protected release-smoke path transmit the complete promoted article independently of the normal payload limit?
* Which deployed promotion record should be designated as the relaunch acceptance state for the protected run?

## Recommended Next Validations

* Correct and test exact-byte handling for articles above 50,000 characters.
* Add executable coverage for both workflow Python heredocs rather than source-string assertions.
* Re-run the focused pipeline and Podcaster handoff tests after correction.
* Run the protected `podcaster-release-smoke` job after deployment with the designated relaunch promotion record.
* Retain the successful Actions run URL and downstream dry-run response evidence in the changes log.
* Revalidate Phase 8 before relaunch acceptance.