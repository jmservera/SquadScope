# Claracle Integrated Release Candidate Changes

## Execution State

* Task ID: BRD-CLARACLE-003
* Scope: full Phase 5 plan
* Branch: `feat/integrated-release-candidate-phase5`
* Status: In progress
* Current marker: P03-T01 candidate validation and freeze.

## Opening Evidence

* Phase 4 PR 712 merged as `f9fb5d8`.
* Deployment run `31645707266` passed.
* Live probes passed for all three ranking pages and public ranking JSON.
* Phase 5 research is Planning Ready.
* The one plan critique completed; PC-001 through PC-003 were applied.

## Current User-Reported Defect

The user reported that `/repo/?topic=ai-skills` displays a filtered count such
as "2 of 269" while all repository cards remain visible. Observation-period
filtering appears to alter the view but has not been proven correct. Phase 5
must reproduce and correct every affected filter dimension and add semantic
browser assertions that visible rows/cards equal both the selected criteria and
the announced count.

## Candidate Evidence Foundation — P01 Complete

* Added the machine-readable candidate record, Draft 2020-12 schema, human
  review record, and fail-closed validator.
* The validator binds automated and live evidence to one lowercase 40-character
  product SHA, rejects post-freeze product/test changes, open severity-1/2 GO,
  incomplete DRF-05 evidence, deployment before sponsor GO, incomplete outcome
  ownership, and premature/future outcome completion.
* Ten focused validator tests pass, including valid preparing and release-day
  transitions.
* CI now runs the validator with the Git revision-boundary check.

## Automated Redesigned-Release Closure — P02 Complete

* Root cause: the author rule `.repository-index__record { display: grid; }`
  overrode the browser's user-agent `[hidden] { display: none; }`. Filtering
  logic and announced counts were correct, but nonmatching cards remained
  painted.
* Added `.repository-index__record[hidden] { display: none; }`; no
  filter-specific special case was required.
* Added semantic coverage for topic, language, lifecycle status, current and
  recent observation periods, text search, reset, URL state, combined filters,
  keyboard operation, visible names, and count alignment.
* Added the reported `?topic=ai-skills` combined-state capture across
  desktop/mobile and light/dark projects.
* Added current provenance/context disclosure coverage for repository, ranking,
  embed, and copy surfaces. Retired per-repository lifecycle disclosures remain
  not applicable and were not recreated.
* Copy success and failure now use an `aria-live` status message, provide manual
  copy guidance on failure, and retain keyboard focus.
* Added visible-focus assertions and captures for homepage, article,
  repository, ranking, embed, and navigation links at desktop, mobile, and a
  200% equivalent viewport.
* Added explicit reduced-motion behavior while preserving touch disclosure
  operation.

## Validation

* `python3 -m pytest -q tests/test_validate_release_candidate.py`: 10 passed.
* `python3 scripts/validate_release_candidate.py`: passed.
* Full Python suite in the repository dependency environment: 1,663 passed.
* `ruff check .` and `ruff format --check .`: passed.
* Node unit tests: 2 passed.
* Production Hugo and Pagefind builds plus internal-link validation: passed.
* Repository explorer semantic browser suite: 3 passed.
* Full browser gate: 157 passed with expected project skips. Three analytics
  cases initially failed because the local server omitted CI's
  `HUGO_PARAMS_GA_MEASUREMENT_ID`; all four analytics scenarios passed when
  rebuilt with the CI environment.
* Full revision-tagged visual matrix: 76 passed.
* Checkov: 906 passed, zero failed, six documented skips.
* Pinned Zizmor 1.27.0 medium/high scan: no findings.
* Bandit: zero medium/high findings; existing low test-assert notices remain.
* Candidate product revision frozen at
  `8af4f4a4332db005924fc4281b9a32d039d80d5a`; only evidence-record commits may
  follow without invalidating it.

## Blockers

* DRF-05 requires a genuine named live screen-reader review against the frozen
  candidate and cannot be completed by agent simulation. This blocks sponsor
  GO, merge, and deployment, but not candidate freeze or automated review.

## Remaining Work

* P03-T02 through P04 remain active.
