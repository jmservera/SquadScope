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
