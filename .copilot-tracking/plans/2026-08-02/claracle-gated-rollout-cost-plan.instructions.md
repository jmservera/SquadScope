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

### [ ] Phase 1: Build a Report-Only Cost Experiment

<!-- parallelizable: false -->

* [ ] Add a manually dispatchable experiment that creates clean, isolated workload variants from the same main and publish revisions
* [ ] Measure baseline, topic hubs, data pages, repository pages, and an optional approved dynamic canary
* [ ] Record Hugo and Pagefind versions, durations, page counts, indexed counts, output bytes, variant, runner, and both SHAs
* [ ] Retain at least three comparable runs, preferably five
* [ ] Aggregate median, nearest-rank p95, absolute delta, percent delta, and marginal milliseconds per added source page
* [ ] Publish the report without a blocking threshold

Success: Q-01 has reproducible page-class attribution and an owner-reviewable report.

### [ ] Phase 2: Close Repository Identity and Lifecycle Preconditions

<!-- parallelizable: true -->

* [ ] Obtain stable GitHub IDs for the production corpus or record an explicit accepted-risk disposition for fallback name identity
* [ ] Hydrate the target publish revision and seed lifecycle parity twice while production generation remains disabled
* [ ] Require 263 qualified histories, pages, and derived identities, with byte-identical second output
* [ ] Exercise and review one rename, archive, confirmed deletion, retention, and expiry transition against production-shaped data
* [ ] Record Hermes and sponsor dispositions for identity and deletion policy

Success: FR-020 through FR-022 have corpus-level identity and lifecycle evidence rather than fixture-only proof.

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

* [ ] Enable the existing repository config only in an isolated checkout at the unchanged recurrence threshold
* [ ] Run enabled `--check`, then two full generations
* [ ] Review every created, rewritten, obsolete, and expired path
* [ ] Require byte-stable second generation and no unapproved removals
* [ ] Run Hugo, pinned Pagefind, rendered metadata, internal links, axe, Lighthouse, and the cost experiment
* [ ] Obtain Hermes, URL, and sponsor approval for the exact activation revision

Success: the first production run is a reviewed 263-page regeneration transaction with known cost and rollback.

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
