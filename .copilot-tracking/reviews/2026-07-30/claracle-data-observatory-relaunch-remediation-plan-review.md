<!-- markdownlint-disable-file -->
# Implementation Review: Claracle Data Observatory Relaunch Remediation

## Review Metadata

| Field | Value |
|---|---|
| Review date | 2026-07-30 |
| Related plan | `.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md` |
| Changes log | `.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md` |
| Research | `.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md` |
| Pull request | `jmservera/SquadScope#623` |
| Review scope | Full implementation against all ten plan phases |

## Overall Status

Needs Rework.

The remediation establishes most planned repository structure, but PR #623 is not
ready for merge or relaunch acceptance. Two correctness defects affect durable
retention and the protected Podcaster smoke, the production browser job is failing,
and required security and external acceptance gates remain open. Both rollout flags
correctly remain disabled.

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 7 |
| Major | 8 |
| Minor | 4 |

## Critical Findings

### CR-01 Deletion retention can violate the three-year minimum

`scripts/observatory_repos.py:738-746` starts retention from `last_seen_week` when
`deletion_confirmed_at` is omitted. A reviewed deletion can therefore expire less
than three years after confirmation. This violates FR-022 and invalidates Phase 3's
completed status.

### CR-02 The protected Podcaster smoke cannot prove exact promoted bytes

The payload-verifier heredoc in
`.github/workflows/podcaster-handoff-smoke.yml:222-225` fails compilation because of
inconsistent indentation. The shared payload also truncates content at 50,000
characters in `scripts/podcaster_handoff.py:524-555`. The exact-release contract is
not implemented for long articles, and no protected downstream success exists.

### CR-03 Production browser acceptance is failing

PR run `30502305707`, job `90744394455`, failed the axe and responsive browser gate
after 66 tests passed and 97 skipped. Lighthouse was skipped. Artifact `8744139176`
contains the reports. NFR-001 and NFR-005 have no passing evidence for this revision.

### CR-04 The required repository-wide Zizmor gate is not clean

The review scan reports one high, twelve medium, and one low finding, including
workflow-wide write permission in `.github/workflows/squad-promote.yml:14-15` and
retained checkout credentials across Squad workflows. Hosted Zizmor reports success,
so the scanner configuration and disposition also need reconciliation.

### CR-05 Security remediation and sign-off are incomplete

`docs/review/data-observatory-relaunch/security-review.md:140-169` leaves SEC-01
through SEC-06 open or conditional, including a high-severity candidate-title
sanitization gap. Hermes, URL, and owner sign-off are all pending. NFR-004 remains
blocked.

### CR-06 Required external launch evidence is absent

All GA4, GSC, social preview, structured-data, production feed, Podcaster, and
accessibility gates remain pending in
`docs/review/data-observatory-relaunch/README.md:48-63`. Repository tests cannot
substitute for these dated observations.

### CR-07 Sponsor approval is absent for both rollout controls

No dated approval exists for dynamic topic creation or repository page creation.
`config/observatory.toml:1-2,18-19` correctly keeps both controls off, but Phase 9 and
relaunch acceptance cannot complete without separate approvals.

## Major Findings

### MAJ-01 Dynamic-topic disablement returns without a decision

`scripts/manage_topic_hubs.py:393-394` silently returns instead of emitting the
required explicit disabled decision.

### MAJ-02 Existing repository histories are not seeded in the lifecycle ledger

`data/derived/observatory/repository-lifecycle.json:1-4` has an empty repositories
object despite existing generated repository pages. Current identity and alias state
is not durably seeded before the first enabled run.

### MAJ-03 Analytics privacy acceptance does not block CI

`.github/workflows/ci.yml:171-172` omits
`tests/visual/observatory-analytics.spec.mjs`. The spec also bypasses actual Cookie
Consent interaction and does not assert pre-consent GA script or cookie absence.

### MAJ-04 Atomic publication has no retained runtime proof

Phase 4 workflow-shape tests pass, but no Actions evidence proves failure rollback,
one lease-protected generated commit, deploy hydration from that commit, or a no-op
identical rerun.

### MAJ-05 The timing baseline has only one of three required CI reports

One `build-timing.json` artifact exists. Median, p95, proposed budgets, and owner
approval remain unavailable, so Step 7.3 is incomplete.

### MAJ-06 The literal all-generator two-run proof is missing

Focused idempotence tests and freshness checks pass, but no isolated workspace record
shows every generator run twice followed by a clean second-run diff.

### MAJ-07 Visual evidence does not satisfy the acceptance matrix

The retained screenshots are historical, some are obscured, and the topic capture is
empty. Mobile, dark-theme, populated, interaction, revision, and viewport evidence is
not accepted.

### MAJ-08 Traceability evidence is not consistently immutable or directly resolvable

Several changes-log cells use descriptions instead of exact paths or run identifiers.
Phase results also omit raw logs or current CI links, including the failed browser run
and artifact.

## Minor Findings

* `tests/test_pipeline.py:656-711` inspects workflow strings instead of executing
	embedded Python, allowing the invalid Podcaster verifier to pass.
* `scripts/export_observatory_dataset.py:405-409` can raise `ValueError` while
	reporting stale files for an output directory outside the repository.
* The cross-origin embed consent limitation is recorded in the security review but
	not in `docs/data-observatory-runbook.md`.
* The changes log retains stale dataset-drift wording and does not record the current
	failed browser job, skipped Lighthouse state, or artifact ID.

## RPI Validation

| Phase | Status | Summary | Validation |
|---:|---|---|---|
| 1 | Partial | Safe defaults pass; disabled decision and traceability paths need repair | `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-001-validation.md` |
| 2 | Passed | Backfill, candidate discovery, guarded promotion, and continuity satisfy the plan | `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-002-validation.md` |
| 3 | Failed | Retention clock is unsafe; ledger seed and rendered acceptance are missing | `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-003-validation.md` |
| 4 | Partial | Workflow shape passes; runtime atomicity evidence is absent | `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-004-validation.md` |
| 5 | Passed | Page-class SEO, social dimensions, feeds, XML, and link contracts pass | `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-005-validation.md` |
| 6 | Partial | Bounded implementation exists; dedicated privacy tests do not block CI | `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-006-validation.md` |
| 7 | Partial | Source gates exist; browser CI fails and timing evidence is incomplete | `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-007-validation.md` |
| 8 | Failed | Exact-byte verifier is invalid, truncation conflicts with the contract, and no downstream run exists | `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-008-validation.md` |
| 9 | Partial | Runbook and ADR pass; security, platform, visual, and sponsor acceptance remain open | `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-009-validation.md` |
| 10 | Partial | Core gates pass; browser, Zizmor, all-generator proof, and external evidence remain open | `.copilot-tracking/reviews/rpi/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-010-validation.md` |

## Implementation Quality

The Implementation Validator was invoked twice but could not access execution or
workspace tools and issued no formal findings. Direct source verification is recorded
in
`.copilot-tracking/reviews/quality/2026-07-30/claracle-data-observatory-relaunch-remediation-plan-quality.md`.

Quality status: Needs Rework.

* Correctness: Critical retention and exact-byte workflow defects
* Security: Open SEC findings and non-clean local Zizmor scan
* Architecture: Atomic single-writer design is present; runtime evidence is missing
* Test quality: Broad Python coverage passes, but embedded workflow programs and real
	consent behavior are not executed
* Maintainability: Generated-state and traceability contracts need stronger seed and
	provenance records

## Validation Commands

| Validation | Result |
|---|---|
| `python3 -m ruff check .` | Passed |
| `python3 -m ruff format --check .` | Passed |
| `python3 -m pytest -q tests/` | Passed: 1362 tests, 2 warnings, 16 subtests |
| Focused lifecycle, pipeline, Podcaster, and topic tests | Passed: 91 tests, 8 subtests |
| `hugo --minify` with Hugo Extended 0.161.1 | Passed in 15.339 seconds |
| `npx pagefind@1.5.2 --site public/` | Passed in 1.631 seconds |
| Internal link checker | Passed |
| Checkov | Passed with one documented manual-dispatch skip |
| Podcaster payload-verifier compile | Failed: indentation error at extracted line 33 |
| Hosted Production site job | Failed: 66 passed, 97 skipped; Lighthouse skipped |
| Local `zizmor .github/workflows/` | Findings: 1 low, 12 medium, 1 high |
| `git diff --check` | Passed |

## Missing Work and Deviations

* Correct the deletion retention clock and seed the current lifecycle ledger.
* Repair and execute the exact-byte Podcaster verifier without truncation.
* Add the analytics privacy suite to CI and exercise real consent behavior.
* Diagnose artifact `8744139176`, fix browser failures, and obtain passing
	Lighthouse evidence on the same revision.
* Resolve or formally disposition repository-wide Zizmor findings.
* Execute the Phase 4 runtime scenarios and the isolated all-generator two-run proof.
* Complete security remediation and named reviewer sign-off.
* Complete platform, accessibility, visual, downstream, timing, and sponsor evidence.
* Update the plan and changes log after rework; completed Phase 3 and Phase 8 claims
	currently overstate verified behavior.

## Follow-Up Work

### Deferred From Scope

* Three-run Hugo and Pagefind baseline, statistics, and owner-approved budgets
* Protected downstream Podcaster run tied to the accepted promotion record
* GA4, GSC, social, schema, production feed, and accessibility observations
* Refreshed visual capture matrix and separate rollout approvals

### Discovered During Review

* Date-omitted deletion overrides can expire early
* The protected Podcaster payload verifier has invalid indentation
* Shared payload truncation conflicts with exact-release semantics
* The analytics browser contract is omitted from CI
* The lifecycle ledger is empty for the current corpus
* Workflow string assertions do not execute embedded programs
* Custom external dataset output paths can break stale-file reporting

## Reviewer Notes

PR #623 should remain open and both rollout flags should remain disabled. Rework the
critical repository defects first, rerun focused tests, then rerun Production site and
security gates. External acceptance can proceed only after a deployable revision has
passing repository gates and a designated promotion record.