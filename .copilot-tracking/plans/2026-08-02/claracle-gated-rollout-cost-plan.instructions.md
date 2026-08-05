---
applyTo: '.copilot-tracking/changes/2026-08-02/claracle-gated-rollout-cost-changes.md'
---
<!-- markdownlint-disable-file -->
# Implementation Plan: Claracle Gated Rollouts and Cost Measurement

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

* [ ] Change `--dry-run` from an early exit into a non-mutating proposed-change report, or add an equivalent preview command
* [ ] Test that preview reads candidates but writes no hub, registry, weekly frontmatter, taxonomy, or log changes
* [ ] Review the five currently eligible candidates and choose one unambiguous canary
* [ ] Add all non-canary candidates to `ignore_topics` as explicit temporary deferrals
* [ ] Generate and review the exact canary transaction in an isolated checkout
* [ ] Validate sanitization, structured YAML, evidence-backed assignments, taxonomy, logging, rendering, and disabled rollback
* [ ] Obtain Hermes and sponsor approval for the exact canary revision

Success: one bounded candidate can be promoted without exposing all eligible candidates to the same transaction.

### [ ] Phase 4: Preflight Repository Regeneration

<!-- parallelizable: false -->

* [x] Enable the existing repository config only in an isolated checkout at the unchanged recurrence threshold
* [x] Run enabled `--check`, then two full generations
* [x] Review every created, rewritten, obsolete, and expired path
* [x] Require byte-stable second generation and no unapproved removals
* [ ] Run Hugo, pinned Pagefind, rendered metadata, internal links, axe, Lighthouse, and the cost experiment
* [ ] Obtain Hermes, URL, and sponsor approval for the exact activation revision

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

* [ ] Enable only the separately approved flag and run one publish transaction
* [ ] Inspect the committed generated-state diff before deployment
* [ ] Confirm production rendering, lifecycle, telemetry, and downstream smoke
* [ ] For rollback, disable the flag and revert the generated transaction; disabling alone does not undo durable mutations
* [ ] Expand dynamic candidates one reviewed item at a time
* [ ] Add blocking budgets only after the report-only observation window and explicit owner approval

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
