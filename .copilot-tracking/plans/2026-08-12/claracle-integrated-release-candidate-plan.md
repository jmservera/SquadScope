# Claracle Integrated Release Candidate Plan

## Task Metadata

| Field | Value |
|---|---|
| Task ID | BRD-CLARACLE-003 |
| Task slug | claracle-integrated-release-candidate |
| Date | 2026-08-12 |
| Status | Candidate |
| Mode | Automatic |
| Research | `.copilot-tracking/research/2026-08-12/claracle-integrated-release-candidate-research.md` |
| Details | `.copilot-tracking/details/2026-08-12/claracle-integrated-release-candidate-phase-details.md` |
| Critique | `.copilot-tracking/reviews/2026-08-12/claracle-integrated-release-candidate-plan-critique.md` |
| Changes record | `.copilot-tracking/changes/2026-08-12/claracle-integrated-release-candidate-changes.md` |

## Executive Summary

Phase 5 will create one immutable redesigned-release candidate and bind all
automated, named, sponsor, rollback, deployment, and outcome evidence to it.
Implementation first closes DRF-01 through DRF-04 with focused browser tests and
revision-tagged captures, then runs every affected repository gate. DRF-05
remains a hard human-review blocker: no automation or simulated accessibility
tree may substitute for a dated live screen-reader review. Release-day evidence
can be recorded in this delivery; seven-day, 28-day, three-month, and six-month
observations must be scheduled and recorded only when due.

## User Decisions and Requirements

* Continue automatically after Phase 4 is fully merged and deployed.
* Preserve all production, security, review, and severity gates.
* Every repository change must use a pushed pull request.
* Keep production on GitHub Pages.
* Phase 4 PR 712 was explicitly approved for merge on 2026-08-12.
* Review and fix repository explorer filters during Phase 5: topic selection
  can announce a reduced count while leaving all repositories visible, and
  observation-period filtering needs semantic verification.

## Sources

* `.copilot-tracking/research/2026-08-12/claracle-integrated-release-candidate-research.md`
* `.copilot-tracking/plans/2026-08-08/claracle-post-relaunch-consolidation-plan.instructions.md`
* `.copilot-tracking/details/2026-08-08/claracle-post-relaunch-consolidation-details.md`
* `docs/brds/claracle-post-relaunch-consolidation-brd.md`
* `docs/review/claracle-post-relaunch/redesigned-release-finding-map.md`

## Goals

* Produce one revision-addressed release-candidate evidence record.
* Close DRF-01 through DRF-04 with reproducible browser evidence.
* Obtain named Amy, Fry, Leela, Hermes, URL, Nibbler, Zapp, and sponsor
  dispositions where their ownership applies.
* Preserve DRF-05 as blocking until a real named live-AT review is recorded.
* Record release-day production evidence and assign all delayed outcome windows.

## Scope and Non-Goals

### In Scope

* Focused Playwright coverage and revision-tagged evidence for combined filters,
  disclosures, copy outcomes, visible focus, touch, zoom, and reduced motion.
* A Phase 5 candidate evidence document and finding-map reconciliation.
* Full affected repository gates, owner reviews, rollback evidence, PR, merge,
  deployment, and live probes.
* Explicit due dates and owners for delayed observations.

### Non-Goals

* No broad redesign or new product behavior beyond what closure evidence
  requires.
* No weakening or reclassification of a severity-2 finding without the BRD
  owner, rationale, due date, and sponsor process.
* No simulated or automated claim of live screen-reader acceptance.
* No claim that seven-day or later evidence exists before its due date.

## Functional Requirements

* FR-01: The candidate record identifies one frozen product commit SHA.
  Evidence-only commits may refer to that SHA but must not change runtime,
  workflow, content, generated-data, or test files after the freeze.
* FR-02: DRF-01 fixes and captures representative repository topic, language,
  status, observation-period, search, and combined-filter states; visible
  results must match the announced count, selected criteria, keyboard
  operation, reset behavior, and URL state.
* FR-03: DRF-02 captures expanded provenance/disclosure states and proves
  pointer and keyboard operation plus focus order.
* FR-04: DRF-03 proves copy success, failure, status announcement, and retained
  focus.
* FR-05: DRF-04 proves visible focus across homepage, article, repository,
  ranking, embed, and navigation links at desktop, mobile, and 200% zoom.
* FR-06: DRF-05 evidence records reviewer, browser, OS, AT/version, scenarios,
  findings, severity, disposition, and exact candidate revision.
* FR-07: Release-day evidence records PR/merge/deploy/run identifiers, rollback
  boundary, and live probes.
* FR-08: Outcome ownership records due dates relative to production deployment.

## Non-Functional Requirements

* NFR-01: Preserve useful no-JavaScript Hugo output.
* NFR-02: No severity-1 or severity-2 finding remains open at sponsor GO.
* NFR-03: Public data and external text remain sanitized and schema-valid.
* NFR-04: Workflow changes, if any, require URL and Hermes review.
* NFR-05: Generated-content or user-facing AI-output changes require Nibbler
  review.
* NFR-06: The branch remains one focused concern and reaches production only
  through a reviewed PR.

## Acceptance Criteria

* One immutable product candidate SHA is recorded in every Phase 5 evidence
  artifact; evidence commits remain a separate identity and contain no product
  or test changes after the freeze.
* DRF-01 through DRF-04 have passing automated evidence and named owner
  dispositions on that SHA.
* DRF-05 has genuine live-AT evidence on that SHA; until then status is Blocked.
* Python, Ruff, Hugo/Pagefind/link, schema/content, browser/accessibility,
  visual, performance, privacy, Bandit, Checkov, and Zizmor gates pass as
  applicable.
* No unresolved severity-1/2 finding or PR thread remains.
* Sponsor GO and rollback readiness are recorded before merge/deployment.
* Release-day live evidence passes.
* Delayed observations have owners and exact due dates and are not marked
  complete early.

## Phase Checklist

<!-- phase-id: P01 -->
### [x] P01 — Candidate Evidence Foundation

* [x] P01-T01 Create the revision-bound Phase 5 evidence schema/document.
* [x] P01-T02 Add deterministic validation that rejects mixed revisions,
  premature outcome completion, missing owner/due-date fields, and open blocking
  findings in a GO candidate.
* [x] P01-T03 Add focused unit tests for the evidence validator.

<!-- phase-id: P02 -->
### [x] P02 — Automated Redesigned-Release Closure

* [x] P02-T01 Reproduce and fix repository explorer filter rendering, verify
  every filter dimension semantically, and add combined-filter visual and
  keyboard evidence.
* [x] P02-T02 Add DRF-02 expanded disclosure/provenance pointer, keyboard, and
  focus-order evidence for the repository explorer, ranking rows/visual
  fallback, embed repository context, and copy disclosure. Record retired
  lifecycle-only UI as not applicable rather than recreating it.
* [x] P02-T03 Add DRF-03 copy success/failure/announcement/focus evidence.
* [x] P02-T04 Add DRF-04 representative visible-focus evidence at desktop,
  mobile, and 200% zoom.
* [x] P02-T05 Capture reduced-motion and touch equivalence needed by Phase 5.

<!-- phase-id: P03 -->
### [ ] P03 — Candidate Validation And Named Review

* [x] P03-T01 Freeze the product candidate SHA, capture all automated reports
  against that exact revision, and allow only evidence-record commits afterward.
* [ ] P03-T02 Obtain Amy/Fry visual, keyboard, touch, zoom, reduced-motion, and
  evidence dispositions.
* [ ] P03-T03 Obtain the real named DRF-05 live screen-reader disposition.
* [ ] P03-T04 Obtain Leela, Hermes, URL, Nibbler, Zapp, editorial/data-integrity,
  and sponsor dispositions as applicable.
* [ ] P03-T05 Reconcile every finding under the BRD severity policy.

<!-- phase-id: P04 -->
### [ ] P04 — Release And Outcome Ownership

* [ ] P04-T01 Record sponsor GO and tested rollback readiness.
* [ ] P04-T02 Push, open the Phase 5 PR, complete hosted checks/Copilot review,
  resolve threads, request merge authorization, merge, and verify deployment.
* [ ] P04-T03 Record release-day probes and the deployed revision.
* [ ] P04-T04 Record owners and due dates for seven-day, 28-day, three-month,
  and six-month observations.

## Dependencies and Ordering

* P02 depends on P01's evidence contract.
* P03 depends on P01-P02 and one frozen candidate revision.
* P04 sponsor GO depends on every severity-1/2 finding being closed, including
  DRF-05.
* Delayed outcome observations depend on the actual deployment timestamp.

## Validation Strategy

* Focused Python tests for candidate validation.
* Focused Playwright scenarios while developing P02.
* Full repository Python/Ruff/Hugo/Pagefind/link/browser/visual/Node/security
  gates before push.
* Hosted checks and Copilot review on every substantive pushed head.
* Live HTTP and JSON probes after deployment.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Evidence mixes revisions | validator fails closed on any SHA mismatch |
| Automated evidence is mistaken for live AT | DRF-05 requires named environment metadata and remains manual-only |
| Candidate changes after manual review | invalidate dispositions and refreeze/review the new SHA |
| Future outcomes are marked complete early | validator compares status/due date and permits only scheduled state before due |
| Phase 5 expands into redesign | limit production edits to evidence-required defects/tests |

## Test Ownership and Addition Bounds

* Candidate validator semantics:
  `tests/test_validate_release_candidate.py` (one new Python test file).
* Repository interaction semantics: existing repository explorer browser spec.
* Ranking semantics: `tests/visual/ranking-explorer.spec.mjs`.
* Embed/copy/disclosure/focus semantics:
  `tests/visual/observatory-a11y.spec.mjs`.
* Revision-tagged captures:
  `tests/visual/observatory-visual-regression.spec.mjs`.
* No new Playwright runner or config. At most one new visual spec is permitted
  only if no existing owner can express a required candidate-state capture.
* Exact removals: none planned.

## Critique Disposition

* PC-001: Applied. Candidate product SHA and later evidence-commit identity are
  now distinct; post-freeze product/test changes invalidate the candidate.
* PC-002: Applied. DRF-02 targets the current repository, ranking, embed, and
  copy disclosure surfaces; retired lifecycle-only UI is not recreated.
* PC-003: Applied. Test ownership, one-new-Python-test maximum, no-new-runner
  rule, and visual-spec bound are locked.
* Final critique execution: Complete.
* Final critique verdict after direct dispositions: Pass.

## Follow-Up Items

* Seven-day production smoke: due seven calendar days after deployment.
* 28-day migration and organic evidence: due 28 calendar days after deployment.
* Three-month migration and organic evidence: due three calendar months after
  deployment.
* Six-month SEO outcome evidence: due six calendar months after deployment.

## Handoff

Implementation starts at P01 on
`feat/integrated-release-candidate-phase5`. The changes record is
`.copilot-tracking/changes/2026-08-12/claracle-integrated-release-candidate-changes.md`.
The implementation must stop at the named-human blocker rather than infer or
simulate DRF-05 completion.
