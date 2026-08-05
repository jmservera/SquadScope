<!-- markdownlint-disable-file -->
# Planning Log: Claracle Gated Rollouts and Cost Measurement

**Related Plan**: claracle-gated-rollout-cost-plan.instructions.md

## Discrepancy Log

### Implementation Deviations

* DD-01: Phase 1 was reconciled rather than re-implemented.
  * Plan specifies: build a new report-only cost experiment (workflow, script, tests).
  * Implementation differs: the experiment was already built and merged to `main` on
    2026-08-03 under `.copilot-tracking/plans/2026-08-03/claracle-all-followups-plan.instructions.md`.
    This plan's Phase 1 checklist was marked complete with a cross-reference instead of
    duplicating that work.
  * Rationale: avoids a second, divergent implementation of the same workflow contract.
* DD-02: The frozen-corpus qualified count in this plan's Phase 2 success criteria
  (263) is stale.
  * Plan specifies: 263 qualified histories, pages, and derived identities.
  * Implementation differs: `tests/test_observatory_repos.py`'s
    `test_frozen_corpus_lifecycle_seed_has_expected_parity` currently asserts 270,
    reflecting 7 pages added after the plan was written.
  * Rationale: not corrected in this pass; flagged here so Phase 2 execution reconciles
    against the live test assertion rather than the stale plan figure.

## Suggested Follow-On Work

* WI-01: Retain 3/5-run `build-cost-experiment.yml` artifacts and obtain an owner
  budget conclusion for Q-01/NFR-009 — medium priority.
  * Source: Phase 1 success criteria (report is implemented; retained comparable runs
    and an owner-reviewed budget are still open per
    [status-of-record.md](../../../../docs/review/data-observatory-relaunch/status-of-record.md)).
  * Dependency: none technical; needs an owner to dispatch and review the runs.
* WI-02: Resolve stable GitHub identity for the production repository corpus, or
  record an explicit accepted-risk disposition, before starting Phase 2 — high priority.
  * Source: Phase 2, Step 1.
  * Dependency: Hermes/sponsor decision. **Sponsor half resolved by ID-01** (backfill
    mechanism implemented in `scripts/backfill_repo_identity.py` and
    `scripts/observatory_repos.py`; live corpus run tracked in the Changes Log). Hermes
    disposition on corpus-level evidence remains outstanding.
* WI-03: Record the sponsor rollout decision for `dynamic_topic_creation` and
  `repo_pages` separately — high priority, blocks Phases 2 through 5.
  * Source: Phases 2 through 5 success criteria; Plan Dependencies.
  * Dependency: `jmservera` sponsor review of
    [owner-action-register.md#sponsor-rollout-decision](../../../../docs/review/data-observatory-relaunch/owner-action-register.md#sponsor-rollout-decision).

## User Decisions

* ID-01: Repository identity backfill strategy — backfill stable GitHub IDs for the
  production corpus via live GitHub REST API lookups (`GET /repos/{full_name}`) for
  every history currently keyed by the `name:` fallback.
  * Not-found policy: any repository returning HTTP 404 is recorded with
    `status: "not_found"` and folded into lifecycle resolution as reviewed deletion
    evidence (`status: "deleted"`, `status_evidence: "github_api_404_identity_backfill"`),
    equivalent to a manual `[repo_pages.lifecycle]` override. Manual overrides still take
    precedence when both exist for the same repository.
  * Rationale (from sponsor): deleted repositories are an expected, independent risk that
    occurs regardless of identity strategy, so a confirmed 404 should resolve the identity
    question rather than remain an open risk.
  * Decision by: jmservera (sponsor), recorded 2026-08-05.
  * Implementation: `scripts/backfill_repo_identity.py` (new), `load_identity_backfill()`
    and `merge_identity_backfill_overrides()` in `scripts/observatory_repos.py`, threaded
    through `generate()` and `seed_lifecycle()`. See the Changes Log for the live corpus
    run outcome.
