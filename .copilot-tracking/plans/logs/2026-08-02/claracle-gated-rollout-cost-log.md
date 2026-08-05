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
* DD-03: Applying the completed identity backfill to `seed_lifecycle()` fails the
  existing byte-for-byte parity check (Phase 2, checklist item 2) by design, not by bug.
  * Plan specifies: hydrate and seed lifecycle parity twice while production generation
    remains disabled.
  * Implementation differs: `python -m scripts.observatory_repos --seed-lifecycle` now
    raises `Lifecycle seed parity mismatch: qualified=266, pages=270, derived=270` once
    the completed backfill (`data/derived/observatory/repo-identity-backfill.json`) is
    merged in. Root cause confirmed via direct inspection (not a defect in
    `merge_identity_backfill_overrides()`/`load_repository_histories()`): the backfill
    resolved `github_id`s for repositories previously split across a stale fallback
    identity and their real, already-tracked numeric-id identity, consolidating each
    pair into one history under the corrected current `full_name`. This surfaces 7
    existing pages as stale/duplicate and 3 new identities needing a page:
    * `react/react` (`react-react`) and `react/react-native` no longer independently
      qualify; their observations merged into already-existing, already-paged
      identities (no new page needed for these two).
    * `Egonex-AI/Understand-Anything` -> `Lum1104/Understand-Anything`
      (`lum1104-understand-anything`)
    * `affaan-m/ECC` -> `affaan-m/everything-claude-code`
      (`affaan-m-everything-claude-code`)
    * `openinterpreter/openinterpreter` -> `openinterpreter/open-interpreter`
      (`openinterpreter-open-interpreter`)
    * `Graphify-Labs/graphify` and `odysseus-dev/odysseus` also merged into other
      already-qualified identities; no new page needed.
  * Rationale: not corrected in this pass. Regenerating/renaming/removing
    `content/repo/*` pages is exactly the reviewed rename/consolidation transition
    Phase 2's checklist requires exercising, and doing so was intentionally deferred
    for explicit confirmation rather than mixed into a docs-only PR. `seed_lifecycle()`
    correctly fails closed (writes nothing) until this is reviewed and the pages are
    regenerated to match.
* DD-04: Attempting DD-03's remediation surfaced a genuine, pre-existing bug
    (independent of the identity backfill feature itself): `write_repository_pages()`
    raised `Slug collision detected: both history key '1255180606' and
    'name:pewdiepie-archdaemon/odysseus' produce slug 'pewdiepie-archdaemon-odysseus'`.
  * Root cause: a `name:`-keyed ledger entry recorded before a repository's `github_id`
    was known can coexist with a stable-ID ledger entry for the same repository under
    an earlier name. The reverse-index migration in `load_repository_histories()` only
    reconciles this during raw-week processing when the stable key isn't already
    present in `histories`; it was never applied to ledger-preloaded duplicates whose
    display names only converge after raw-week observations settle.
  * Fix: `consolidate_ledger_duplicate_identities()`, added and merged as
    [PR #666](https://github.com/jmservera/SquadScope/pull/666) (based on this branch,
    since it depends on the identity backfill mechanism). Regression test
    `test_consolidates_ledger_preloaded_duplicate_after_rename_settles_display_name`
    reproduces the scenario.
  * With the fix, `--check` succeeds (no collision) but reports **110 files** would
    change (page renames/removals plus `related_repos` recalculation across the
    corpus) — this is Phase 4-scale regeneration, not a single reviewed example.
    Deliberately not written; `config/observatory.toml` was reverted to
    `enabled = false` before committing the fix. See WI-04.

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
* WI-04: Review and regenerate the repository pages affected once the completed
  identity backfill is applied, so `seed_lifecycle()` parity (Phase 2, checklist item
  2) can pass — high priority, blocks the remainder of Phase 2.
  * Source: DD-03, DD-04.
  * Status: the blocking duplicate-identity bug is fixed and open as
    [PR #666](https://github.com/jmservera/SquadScope/pull/666) (retargeted to `main`
    after #665 merged; CI green). `--check` on top of it shows **110 files** would
    change corpus-wide (not just the original 7). This is full Phase 4-scale
    regeneration (page creation/removal, ledger, derived JSON, `related_repos`
    recalculation across the corpus) and needs its own reviewed PR following the
    Repository Activation Contract rather than being treated as a quick follow-up.
  * Dependency: PR #666 merged first; reviewer time to disposition ~110 file changes.
  * Scoping (not yet started, pending PR #666 merge):
    1. New isolated branch off `main` once #666 merges.
    2. Temporarily set `config/observatory.toml` `[repo_pages] enabled = true`
       (matching the precedent in #663).
    3. Run `python -m scripts.observatory_repos` (write mode); capture the full diff
       for review — expect renames/removals for the identities in DD-03 plus any
       additional consolidations the corpus-scale fix surfaces beyond the original 7.
    4. Reviewer dispositions every obsolete/removed path per the Repository Activation
       Contract ("No removal is accepted from mere crawl absence").
    5. Run generation a second time; require byte-identical output (idempotence).
    6. Run `python -m scripts.observatory_repos --seed-lifecycle` to confirm parity.
    7. Run `hugo --minify`, Pagefind, `scripts/check_internal_links.py`, and the
       existing Python/ruff validation commands from the plan's Validation Commands
       section.
    8. Revert `enabled` back to `false` before merging (keep the generated content
       and ledger changes, matching the #663 precedent).
    9. Update `test_frozen_corpus_lifecycle_seed_has_expected_parity`'s qualified/page
       counts to the new totals.
    10. Obtain Hermes and sponsor sign-off per the Approval Contract before this can
        be considered a closed Phase 2 precondition.
* WI-05: Obtain an accepted-risk disposition or broader-scoped token for the 3
  repositories the backfill could not resolve (access-blocked, not confirmed deleted)
  — medium priority.
  * Source: Changes Log Release Summary (`asz798838958/abaiautoplus` HTTP 403 privacy
    block, `openysmdev/openysm` HTTP 451 DMCA takedown, `powershell/powershell` HTTP 403
    SAML enforcement). None are deletions; the SAML-blocked one specifically requires
    `jmservera` to authorize the OAuth token against the PowerShell org, not something
    resolvable headlessly.
  * Dependency: sponsor/Hermes disposition, or manual SSO authorization for the one
    SAML case.

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
