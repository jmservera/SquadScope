---
applyTo: '.copilot-tracking/changes/2026-08-02/claracle-gated-rollout-cost-changes.md'
---
<!-- markdownlint-disable-file -->
# Implementation Plan: Claracle Gated Rollouts and Cost Measurement

> **STATUS — CLOSED 2026-08-08.** Delivered items complete; the remaining sponsor-gated rollout
> and cost items are migrated to [BRD-CLARACLE-003 §3](../../../docs/brds/claracle-post-relaunch-consolidation-brd.md#3-carried-over-requirements-remaining-relaunch-work) (CR-04 dynamic-topic canary, CR-05 repo_pages activation, CR-06 cost-experiment fix). The `ignore_topics` blocklist step is superseded by the `allow_topics` allowlist. Do not resume here.

## User Requests

* Plan the `repo_pages` rollout
* Plan the `dynamic_topic_creation` rollout
* Plan the incremental generation cost spike for Q-01/NFR-009

## Preconditions

* Keep `repo_pages.enabled = false` and `topic_hubs.dynamic_creation.enabled = false` during planning and preflight.
* Use one reviewed main SHA and one hydrated publish SHA for comparable experiments.
* Preserve Lighthouse thresholds and keep new cost thresholds report-only until approved.
* Require separate sponsor decisions for each rollout flag.

## Implementation Checklist

### [x] Phase 1: Build a Report-Only Cost Experiment

<!-- parallelizable: false -->

* [x] Add a manually dispatchable experiment that creates clean, isolated workload variants from the same main and publish revisions
* [x] Measure baseline, topic hubs, data pages, repository pages, and an optional approved dynamic canary
* [x] Record Hugo and Pagefind versions, durations, page counts, indexed counts, output bytes, variant, runner, and both SHAs
* [x] Retain at least three comparable runs, preferably five
* [x] Aggregate median, nearest-rank p95, absolute delta, percent delta, and marginal milliseconds per added source page
* [x] Publish the report without a blocking threshold

Success: Q-01 has reproducible page-class attribution and an owner-reviewable report.

> Delivered 2026-08-03 under `.copilot-tracking/plans/2026-08-03/claracle-all-followups-plan.instructions.md`
> as `.github/workflows/build-cost-experiment.yml`, `scripts/build_cost_experiment.py`, and
> `tests/test_build_cost_experiment.py`. Verified present on `main` as of 2026-08-05; retained
> 3/5-run artifacts and owner budget conclusion remain pending per
> [status-of-record.md](../../../docs/review/data-observatory-relaunch/status-of-record.md).


### [x] Phase 2: Close Repository Identity and Lifecycle Preconditions

<!-- parallelizable: true -->

* [x] Obtain stable GitHub IDs for the production corpus or record an explicit accepted-risk disposition for fallback name identity
* [x] Hydrate the target publish revision and seed lifecycle parity twice while production generation remains disabled
* [x] Require 263 qualified histories, pages, and derived identities, with byte-identical second output
* [x] Exercise and review one rename, archive, confirmed deletion, retention, and expiry transition against production-shaped data
* [x] Record Hermes and sponsor dispositions for identity and deletion policy

Success: FR-020 through FR-022 have corpus-level identity and lifecycle evidence rather than fixture-only proof.

> Identity backfill completed 2026-08-05 via `scripts/backfill_repo_identity.py`
> (sponsor decision ID-01): 2,012/2,012 pending repositories checked, 1,241 found,
> 768 not_found (reviewed deletion evidence), 3 access-blocked (deferred by sponsor
> decision, see WI-05/ID-02). Applying it surfaced a real rename/consolidation
> transition, resolved by [PR #666](https://github.com/jmservera/SquadScope/pull/666)
> (duplicate-identity bug fix) and [PR #668](https://github.com/jmservera/SquadScope/pull/668)
> (corpus regeneration): 266 qualified histories/pages/derived identities (down from
> 270), byte-identical two-run `generate()` output, 0 `--seed-lifecycle` mismatches.
> Sponsor dispositions recorded as ID-02 (2026-08-05): `repo_pages` approved,
> `dynamic_topic_creation` approved in principle pending Phase 3. PR #668 was merged
> on the strength of automated validation evidence; the sponsor explicitly waived a
> separate formal Hermes review pass for this merge (see ID-02).

### [ ] Phase 3: Add a Safe Dynamic-Topic Preview and Canary

<!-- parallelizable: true -->

* [x] Change `--dry-run` from an early exit into a non-mutating proposed-change report, or add an equivalent preview command — delivered in `e3a00a6` (`#670`): `scripts/manage_topic_hubs.py::preview_dynamic_hubs` reports proposed promotions as JSON and runs while `enabled = false`
* [x] Test that preview reads candidates but writes no hub, registry, weekly frontmatter, taxonomy, or log changes — delivered: `tests/test_topic_hubs.py` snapshots every file before/after and asserts byte equality plus that `data/topic-hubs/` is never created (`test_preview_dynamic_hubs_reports_without_mutating_and_works_while_disabled`, `test_preview_dynamic_hubs_tolerates_malformed_registry_terms`)
* [ ] Review the five currently eligible candidates and choose one unambiguous canary — human-authority (owners: Amy, Hermes, jmservera); the evidence window now yields ~1,051 eligible candidates, so a naive activation is unsafe. Selecting the canary slug is a human decision recorded via the `allow_topics` allowlist
* [ ] Add all non-canary candidates to `ignore_topics` as explicit temporary deferrals — superseded by the `allow_topics` allowlist (added 2026-08-07): a non-empty allowlist restricts promotion to exactly the reviewed slugs, so blocklisting ~1,050 candidates is no longer required; the remaining action is the human populating `allow_topics`
* [ ] Generate and review the exact canary transaction in an isolated checkout — human-authority (owner: Amy)
* [ ] Validate sanitization, structured YAML, evidence-backed assignments, taxonomy, logging, rendering, and disabled rollback — human-authority (owners: Amy, Hermes)
* [ ] Obtain Hermes and sponsor approval for the exact canary revision — human-authority (owners: Hermes, jmservera)

Success: one bounded candidate can be promoted without exposing all eligible candidates to the same transaction.

### [ ] Phase 4: Preflight Repository Regeneration

<!-- parallelizable: false -->

* [x] Enable the existing repository config only in an isolated checkout at the unchanged recurrence threshold
* [x] Run enabled `--check`, then two full generations
* [x] Review every created, rewritten, obsolete, and expired path
* [x] Require byte-stable second generation and no unapproved removals
* [ ] Run Hugo, pinned Pagefind, rendered metadata, internal links, axe, Lighthouse, and the cost experiment — partial: Hugo and internal links run clean; the cost experiment is now unblocked (its corpus guard was corrected to 266 on 2026-08-07) but produces admissible evidence only via the `build-cost-experiment.yml` `workflow_dispatch` on `main` with reviewed SHAs; axe/Lighthouse for this specific content remain a dispatched-run step (owner: URL)
* [ ] Obtain Hermes, URL, and sponsor approval for the exact activation revision — human-authority (owners: Hermes, URL, jmservera)

Success: the first production run is a reviewed 263-page regeneration transaction with known cost and rollback.

> The isolated-checkout preflight (items 1-4) was substantially completed by
> [PR #668](https://github.com/jmservera/SquadScope/pull/668) (WI-04): enabled
> `[repo_pages]` in an isolated branch at the unchanged threshold, ran two full
> `generate()` passes (byte-identical), and reviewed every created/removed path
> (4 confirmed prior-name removals, all merged into an already-existing
> identity). `hugo --minify` and `scripts/check_internal_links.py` both ran
> clean; Pagefind, axe, Lighthouse, and the cost experiment were not run
> locally (no browser tooling in that environment) - CI covers Hugo/lint/tests
> but not axe/Lighthouse for this specific content, so those remain open.
> Sponsor approved `repo_pages` (ID-02) and explicitly waived a separate
> Hermes pass for that merge; URL (workflow/secret-scope) approval has not
> been sought. `config/observatory.toml [repo_pages] enabled` is still `false`
> in `main` - #668 only regenerated content to match what the flag *would*
> produce, matching the #663 precedent, deliberately not flipping the flag.
> Flipping it for real is Phase 5's job.

### [ ] Phase 5: Execute and Observe Rollouts

<!-- parallelizable: false -->

* [ ] Enable only the separately approved flag and run one publish transaction — human-authority (owner: jmservera); both rollout flags remain `false`
* [ ] Inspect the committed generated-state diff before deployment — human-authority (owner: URL)
* [ ] Confirm production rendering, lifecycle, telemetry, and downstream smoke — human-authority (owners: Amy, URL)
* [ ] For rollback, disable the flag and revert the generated transaction; disabling alone does not undo durable mutations — human-authority (owner: URL)
* [ ] Expand dynamic candidates one reviewed item at a time — human-authority (owner: Amy); bounded by the `allow_topics` allowlist
* [ ] Add blocking budgets only after the report-only observation window and explicit owner approval — human-authority (owners: timing-budget owner, jmservera)

Success: each rollout is independently approved, observable, and reversible.

## Validation Commands

* `python -m pytest tests/test_observatory_repos.py tests/test_topic_hubs.py tests/test_taxonomy_registry.py`
* `python scripts/discover_topic_candidates.py --check`
* `python scripts/generate_data_pages.py --check`
* `python scripts/export_observatory_dataset.py --check`
* `python scripts/export_trend_explorer_data.py --check`
* `hugo --minify`
* `npx "pagefind@1.5.2" --site public/`
* `python scripts/check_internal_links.py public --base-url "https://claracle.com/"`
* `python -m pytest tests/`
* `ruff check .`
* `ruff format --check .`

Workflow changes also require Zizmor and Checkov. Browser and Lighthouse validation may run in GitHub CI when local system dependencies are unavailable.

## Dependencies

* .copilot-tracking/research/subagents/2026-08-02/claracle-rollout-cost-followup-research.md
* docs/review/data-observatory-relaunch/owner-action-register.md
* Stable identity decision
* Hermes security disposition
* URL workflow review
* Separate jmservera sponsor decisions
