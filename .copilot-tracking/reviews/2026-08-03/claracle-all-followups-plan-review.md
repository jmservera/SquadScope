<!-- markdownlint-disable-file -->
# Review: Claracle All Follow-Ups

## Metadata

* Plan: `.copilot-tracking/plans/2026-08-03/claracle-all-followups-plan.instructions.md`
* Reviewer: RPI Agent
* Date: 2026-08-03
* Iterations: two implementation corrections during final integration, plus two CI-discovered
  fix rounds after PR #655 was opened (shallow-checkout git behavior, Bandit nosec parsing,
  Checkov skip-comment placement, and automated reviewer feedback)

## User Request Fulfillment

| Request | Status | Evidence |
| ------- | ------ | -------- |
| Complete human acceptance reviews | Complete for repository handoff | Exact owner actions and current evidence are reconciled; human dispositions remain pending and were not inferred |
| Prove atomic publishing | Complete for implementation | Isolated local-remote proof covers normal, rerun, failure, unchanged branch, accepted tree, and hydrated tree; retained manual artifact remains pending |
| Protect the real Podcaster run | Complete for implementation | Automatic real dispatch was removed; manual generation requires exact retained publish evidence and the `podcaster-real-generation` environment |
| Run the cost experiment | Complete for implementation | Report-only workflow and aggregation tooling are ready; no budget-consuming dispatch occurred |
| Resolve #622 and #626 | Complete for repository implementation | Star Velocity, consent geometry, CSS loading, compression, font behavior, Lighthouse concurrency, tests, and documentation were updated; PR CI and owner issue closure remain |

## Placement and Quality

* Publish-relative no-op detection occurs before immutable backup creation in the production workflow.
* Atomic proof executes the real commit-step shell against a temporary bare remote and cannot mutate production `publish`.
* Real Podcaster admission is manual, environment-bound, exact-run, merged-article validated, and records only bounded evidence outputs.
* Cost variants are cumulative, read-only, immutable-revision based, and report-only with no blocking threshold.
* UX changes preserve absolute observed-star semantics and stable scaling across filters.
* Lighthouse changes preserve thresholds and median-of-three sampling while bounding page concurrency.
* Human, sponsor, and private-platform conclusions remain explicitly pending.

## Validation

* Full Python suite: 1,434 passed, 20 skipped, 2 expected warnings, and 34 subtests
* Combined focused suite: 127 passed, 2 skipped, and 26 subtests
* Lighthouse Node suite: 2 passed
* Ruff check and format check: passed
* Diff whitespace check: passed
* Checkov: 843 passed, 0 failed, and 5 skipped
* Zizmor: 0 medium or high findings; one pre-existing low-severity finding in the Copilot package installation step
* Editor diagnostics: no errors in reviewed workflow, Python, or acceptance files

Hugo, Playwright, and full Lighthouse execution require PR CI because local Hugo and
browser runtime dependencies are unavailable.

## Safety Invariants

* No workflow was dispatched.
* No real Podcaster generation was triggered.
* Production `publish` was not mutated by the atomic proof.
* `config/podcast.json` was unchanged.
* `repo_pages.enabled` and `topic_hubs.dynamic_creation.enabled` remain false.
* Historical topic backfill was not promoted.

## Pull Request

* PR #655: <https://github.com/jmservera/SquadScope/pull/655>
* Branch: `feat/claracle-acceptance-followups` → `main`
* Opened to obtain Hugo, Playwright, Lighthouse, and workflow-security CI evidence
  unavailable in the local environment.
* All 16 status checks passing (Python, Ruff, Bandit, Checkov, CodeQL x3, Squad CI,
  Site Preview, Production site, Publish hydration parity, zizmor, plus informational
  Bandit/Checkov/CodeQL code-scanning summaries). No approvals required; no changes
  requested.

### CI-Discovered Fixes (after PR #655 opened)

* `scripts/atomic_publish_proof.py`: CI's shallow, single-ref `actions/checkout` left
  `origin/publish` unresolved and `HEAD` shallow. Fixed by fetching `origin publish`
  before the rev-parse, and by running `git fetch --unshallow origin` before seeding
  the isolated origin so `HEAD`'s full history can be pushed. Reproduced
  `actions/checkout`'s exact shallow-fetch approach locally against the real GitHub
  remote to verify both fixes end to end.
* `scripts/atomic_publish_proof.py` and `scripts/build_cost_experiment.py`: Bandit
  flagged 12 low-severity subprocess findings, suppressed with `# nosec` following the
  repo's existing convention. Discovered and worked around a Bandit 1.9.4 nosec parser
  bug where comma-separated codes (`# nosec B603,B607`) silently drop all but the last
  code.
* `.github/workflows/build-cost-experiment.yml`: moved the `CKV_GHA_7` Checkov skip
  comment inside `workflow_dispatch:` (matching `trigger-podcast.yml`'s placement) so it
  actually suppresses the finding instead of being ignored.
* `.github/workflows/trigger-podcast.yml`: added a job-level `if: github.ref ==
  'refs/heads/main'` guard per automated reviewer feedback, since the dispatched
  workflow YAML runs from the dispatched ref regardless of which branch is checked out.
* `tests/test_pipeline.py`: replaced fragile `workflow[True]` YAML-boolean-key indexing
  with the safer `workflow.get("on", workflow.get(True))` pattern already used elsewhere
  in the test suite, per automated reviewer feedback.

## Remaining Authority-Bound Work

* Merge PR #655 (all CI checks passing, no reviewer feedback outstanding).
* Configure and protect the `podcaster-real-generation` GitHub environment.
* Retain reviewed atomic proof and cost experiment workflow artifacts.
* Complete Hermes, URL, accessibility, analytics, metadata, visual, and sponsor reviews.
* Run one exact real Podcaster generation only after maintainer and environment approval.
* Use PR #655 CI evidence to close #622 and #626.

## Overall Status

Complete. All repository-executable scope is implemented and validated. External
acceptance remains pending with named owners and evidence requirements.