<!-- markdownlint-disable-file -->
# Phase Details: W38 Delivery Reliability

## P01 - Safeguard Review and Incident Reproduction

Inspect `scripts/auto_dispatch_detect.py`,
`.github/workflows/auto-podcast-dispatch.yml`, related tests, and the supplied
run evidence. Completion requires a precise explanation of why the legacy run
was considered ambiguous and confirmation that it could not reach the protected
submission step.

## P02 - Identity-Scoped Compatibility Fix

Change only compatibility handling for legacy runs lacking canonical receipts.
Canonical exact-identity receipts remain authoritative. A legacy run may be
ignored when job/step evidence conclusively proves the protected dispatch never
submitted. Any legacy evidence that could represent a submission for the exact
requested identity remains fail-closed.

## P03 - Regression and Contract Tests

Use focused unit fixtures for the W38 identity and legacy run shape. Cover:

* different-publication no-anchor or detection-failed legacy run with protected
  generation skipped does not block;
* same-identity ambiguous legacy evidence still blocks;
* exact-identity canonical duplicate receipt still blocks;
* any workflow notification adjustment is actionable and does not duplicate
  notifications for the same workflow outcome.

## P04 - Documentation and Validation

Keep documentation changes limited to the compatibility rule and operator
evidence. Run the smallest tests covering duplicate detection and workflow
contracts, then Ruff lint/format checks for changed Python files. Verify the W38
article at its canonical lowercase URL without introducing flaky test
networking.

## P05 - Delivery

Review the diff for preserved safeguards, commit with the required trailers,
push `squad/w38-delivery-reliability`, and open an unmerged PR against `main`.
The PR must reference the W38 incident, list validation, document rollback with
`PODCAST_AUTO_DISPATCH_PAUSED=true`, and enumerate preserved safeguards.

## P06 - Independent Contract Revision

Revise the existing delivery without resetting validated work. The production
handoff must compute the SHA-256 of the exact authorized manifest bytes, include
it as `manifest_sha256`, and validate it in exact-release mode. Duplicate
detection must compare the ordered tuple `week`, `publish_run_id`,
`article_sha256`, `manifest_sha256`. Canonical evidence with the same first
three fields and a different manifest digest is conflicting, not a proven
duplicate or a safe clear result. Legacy evidence may omit the digest only
where existing job/step evidence conclusively proves no submission occurred;
otherwise it remains ambiguous and fail closed.

Canonical `duplicate_prevented` evidence retains its meaning that an earlier
exact-identity submission was proven. Unknown canonical receipt states,
same-base-identity receipts without a valid manifest digest, and successful
legacy handoffs whose manifest bytes cannot be reconstructed remain ambiguous.
Single-attempt skipped protected jobs may clear because they conclusively prove
no request left SquadScope; reruns may not.

Validation includes handoff payload tests, canonical receipt conflict tests,
legacy compatibility regressions, full relevant tests, Ruff, workflow checks,
diff integrity, commit/push, PR description reconciliation, and CI start.

## P07 - Reviewer-Lockout Correction

Close the two unresolved PR review findings without involving the locked-out
P06 author. Canonical identity validation, including the required requested
manifest digest, must happen before missing-credential and missing-repository
short-circuits in both duplicate-check entry points. Add credential-less and
repository-less regressions while preserving the existing clear result for a
complete valid identity when history cannot be queried.

Reconcile the P06 completed-work evidence to the actual final targeted and full
validation counts. Run targeted and full CI-equivalent Python tests, Ruff
lint/format, supported workflow and infrastructure checks, compile and diff
integrity checks, then commit, push, update PR evidence, resolve the current
threads, and leave the PR unmerged without production dispatch.
