# Claracle Integrated Release Candidate Changes

## Execution State

* Task ID: BRD-CLARACLE-003
* Scope: full Phase 5 plan
* Branch: `feat/integrated-release-candidate-phase5`
* Status: In progress
* Current marker: P03-T01 replacement-candidate freeze.

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
* Fifteen focused validator tests pass, including fail-closed lifecycle,
  evidence-hash, chronology, preparing, and release-day transitions.
* CI now runs the validator with the Git revision-boundary check.
* The replacement contract uses a SHA-256 digest of the product tree while
  excluding evidence-only paths, so validation remains correct after a squash
  merge without accepting product drift.
* Closed findings require nonempty hashed evidence and the named role
  dispositions defined by the finding map. Sponsor GO, deployment, rollback,
  and delayed outcomes now fail closed on incomplete or contradictory state.
* DRF-05 now records the real reviewer environment, scenarios, structured
  findings, severity, unresolved work, disposition, timestamp, and candidate
  SHA; automation still cannot satisfy it.

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
  repository, ranking, embed, and navigation links at desktop, mobile, and
  Chromium browser-engine 200% page scaling.
* Added explicit reduced-motion behavior while preserving touch disclosure
  operation.
* Expanded ranking and embed context captures now retain keyboard focus, and
  Escape dismisses the tooltip without moving focus.

## Validation

* `python3 -m pytest -q tests/test_validate_release_candidate.py`: 15 passed.
* `python3 scripts/validate_release_candidate.py`: passed.
* Full Python suite in the repository dependency environment: 1,668 passed.
* `ruff check .` and `ruff format --check .`: passed.
* Node unit tests: 2 passed.
* Production Hugo and Pagefind builds plus internal-link validation: passed.
* The affected repository, accessibility, and revision-tagged visual browser
  suites passed all 172 scenarios with expected project skips.
* Checkov: 906 passed, zero failed, six documented skips.
* Zizmor regular-persona medium/high scan: no findings.
* Bandit: no findings.
* Candidate product revision
  `8af4f4a4332db005924fc4281b9a32d039d80d5a` was frozen and then invalidated by
  the named owner review. The review found fail-open evidence/lifecycle
  semantics and incomplete interaction proof that require product and test
  changes.

## Named Owner Review — Blocked

Amy, Fry, Leela, Hermes, URL, Nibbler, Zapp, and Farnsworth returned Block.
The candidate must add mandatory named dispositions and hashed evidence,
complete the DRF-05 data model, survive squash merges, enforce lifecycle
chronology, capture expanded disclosures, expose visible copy-failure guidance,
and exercise actual 200% page zoom. The complete disposition is retained at
`.copilot-tracking/reviews/2026-08-12/claracle-integrated-release-candidate-owner-review.md`.

## Blockers

* DRF-05 requires a genuine named live screen-reader review against the frozen
  candidate and cannot be completed by agent simulation. This blocks sponsor
  GO, merge, and deployment, but not candidate freeze or automated review.

## Remaining Work

* Freeze and push the replacement candidate, bind hashed evidence and named
  dispositions to it, and repeat owner review.
* P03-T03 remains human-blocked until genuine live screen-reader evidence is
  supplied; sponsor GO, merge, deployment, and outcomes remain downstream.
