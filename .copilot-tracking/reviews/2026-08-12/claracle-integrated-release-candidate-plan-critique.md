# Plan Critique: Claracle Integrated Release Candidate

## Critique Metadata

| Field | Value |
|---|---|
| Execution status | Complete |
| Verdict | Revise |
| Date | 2026-08-12 |
| Plan | `.copilot-tracking/plans/2026-08-12/claracle-integrated-release-candidate-plan.md` |
| Details | `.copilot-tracking/details/2026-08-12/claracle-integrated-release-candidate-phase-details.md` |
| Research | `.copilot-tracking/research/2026-08-12/claracle-integrated-release-candidate-research.md` |

## Criterion Boundary

The critique assessed candidate identity, same-revision evidence, DRF-01 through
DRF-05 closure, severity policy, branch/PR boundaries, validation, sponsor GO,
rollback, deployment, and delayed outcomes. It treated the approved BRD, Phase 5
plan/details, finding map, repository workflow rules, and user continuation
direction as controlling.

## Coverage Assessment

The plan correctly treats Phase 5 as an evidence transaction, preserves the
live-AT blocker, separates future observations, and requires full PR/deployment
gates. Three planner-owned corrections are required before implementation.

## Findings

### PC-001 — Candidate identity is self-referential

* Severity: High
* Related IDs: FR-01, P01-T01, P03-T01
* Evidence: the plan requires the candidate record to contain the exact SHA and
  then commit that record as part of the candidate. A commit cannot contain its
  own final SHA.
* Impact: implementation could repeatedly invalidate the candidate or falsely
  claim that evidence belongs to the recorded revision.
* Smallest useful change: define a two-boundary model: an immutable product
  candidate commit/tree is frozen first; later evidence-only commits may refer
  to it but cannot modify product/runtime files. The validator must distinguish
  `candidate_sha` from evidence-record commit identity and reject product changes
  after the candidate boundary.
* Action owner: planner.
* Resolving evidence: revised FR-01, P03-T01, validator rules, and completion
  boundary.
* Decision class: direct planner correction.

### PC-002 — DRF-02 target is underspecified after repository-page retirement

* Severity: Medium
* Related IDs: P02-T02
* Evidence: the historical row names lifecycle/provenance detail, while the
  redesigned release retired individual repository pages and introduced
  repository/ranking/embed disclosures. The plan says "every redesigned
  disclosure state" but does not enumerate the current replacement states.
* Impact: tests could cover one tooltip and leave another current disclosure
  state unreviewed, while still claiming DRF-02 closure.
* Smallest useful change: inventory and lock the current disclosure set before
  implementation: repository explorer context/provenance, ranking row context,
  ranking visualization fallback, embed repository context, and any copy
  disclosure. Mark historical lifecycle-only UI not applicable with evidence
  rather than recreating retired product behavior.
* Action owner: planner.
* Resolving evidence: exact target list in P02-T02/details and named review
  matrix.
* Decision class: direct planner correction.

### PC-003 — Test ownership and addition bounds are incomplete

* Severity: Medium
* Related IDs: P02-T01 through P02-T05
* Evidence: the plan locks the runner but does not identify every owning test
  file or cap additions, despite the planning gate requiring exact test
  ownership and maximum additions before critique.
* Impact: Phase 5 could sprawl into a new test framework or duplicate existing
  matrices.
* Smallest useful change: lock semantic interaction work to
  `tests/visual/observatory-a11y.spec.mjs` and existing repository/ranking specs,
  visual captures to `tests/visual/observatory-visual-regression.spec.mjs`, and
  candidate validation to one new Python test file. Permit no new runner/config
  and at most one new visual spec only if no current owner exists.
* Action owner: planner.
* Resolving evidence: explicit ownership and addition bounds in plan/details.
* Decision class: direct planner correction.

## Residual Risks

* A named live screen-reader reviewer is not yet available. The plan correctly
  treats this as an implementation-time release blocker rather than a planning
  gap.
* Future outcome windows cannot close in the candidate PR. Scheduled ownership
  is the truthful current state.

## Closeout

* Highest-impact finding: PC-001.
* Action owner: planner.
* Smallest next action: revise the plan to use a frozen product candidate plus
  evidence-only commits, then apply PC-002 and PC-003 in the same batch.
* User response required: no.
