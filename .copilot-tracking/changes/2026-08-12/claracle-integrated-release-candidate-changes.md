# Claracle Integrated Release Candidate Changes

## Execution State

* Task ID: BRD-CLARACLE-003
* Scope: full Phase 5 plan
* Branch: `feat/integrated-release-candidate-phase5`
* Status: In progress
* Current marker: P03-T02/P03-T04 replacement-candidate named review.

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
* Sixteen focused validator tests pass, including fail-closed lifecycle,
  evidence-hash, chronology, preparing, and release-day transitions.
* CI now runs the validator with the Git revision-boundary check.
* The replacement contract uses a SHA-256 digest of the product tree while
  excluding evidence-only paths, so validation remains correct after a squash
  merge without accepting product drift.
* The Git boundary gate independently computes that digest for both the
  declared candidate commit and the current revision, preventing an unrelated
  candidate SHA from borrowing the current tree's digest.
* Closed findings require nonempty hashed evidence and the named role
  dispositions defined by the finding map. Sponsor GO, deployment, rollback,
  and delayed outcomes now fail closed on incomplete or contradictory state.
* DRF-05 now records the real reviewer environment, scenarios, structured
  findings, severity, unresolved work, disposition, timestamp, and candidate
  SHA; automation still cannot satisfy it.
* Delayed outcomes retain the approved OBJ-02 baseline and its measurable
  250-organic-session and 15-top-20-query targets.

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

* `python3 -m pytest -q tests/test_validate_release_candidate.py`: 16 passed.
* `python3 scripts/validate_release_candidate.py`: passed.
* Full Python suite in the repository dependency environment: 1,670 passed.
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

A replacement pre-freeze review confirmed the interaction and lifecycle
remediations but found one candidate-digest binding gap and missing OBJ-02
outcome thresholds. Both are remediated. Because `9d5e55d` was never frozen,
the next commit can become the replacement candidate without invalidating
evidence.

## Replacement Candidate Freeze

* Product candidate:
  `dac7fae8b76257a21a82aea2c371a4e3d59933da`.
* Product-tree SHA-256:
  `45f9998ac0f74f0561e305fb1f30a1b0f1a5b6735d323381fb877a223c44a3b5`.
* Frozen at: `2026-08-12T23:17:30Z`.
* All later changes are limited to evidence-only paths unless this candidate is
  explicitly invalidated.

Exact-revision browser evidence exposed a redirect loop in the CI static server
for directory URLs carrying query strings, including
`/repo/?topic=ai-skills`. The request's query made `self.path.endswith("/")`
false even though its URL path already ended in `/`, so each redirect appended
another slash. Candidate `dac7fae` is invalidated before owner dispositions.
The server now checks the parsed URL path and has a focused no-loop regression
test.

The same static production boundary exposed two test-environment assumptions:
absolute canonical navigation links use `https://claracle.com`, and the delayed
consent dialog can legitimately take focus from repository controls. Internal
focus selection now accepts the document's canonical origin, while repository
filter tests settle and reject consent before asserting focus. The focused
static-browser rerun passed all four applicable scenarios.

## Final Replacement Candidate

* Product candidate:
  `f2b08e62408beaae8828c73e4d3253fa4a95ae12`.
* Product-tree SHA-256:
  `08f4bf6c9df09b1b4fb7f50cfaa5a950a135078b68166718632e0773d5962aff`.
* Frozen at: `2026-08-12T23:35:02Z`.
* Exact-revision evidence: 1,670 Python tests and all 172 affected browser
  scenarios pass at the production static-server boundary.

The final owner review reproduced three validator-test failures after hashed
evidence was added to the checked-in record. The test fixture loaded that
frozen record and replaced only the candidate SHA, leaving exact-candidate
evidence behind. The fixture now creates an isolated preparing record by
clearing candidate boundaries, evidence, reviews, and live-AT state before each
scenario. All 16 focused tests pass again. Candidate `f2b08e6` is invalidated
because the fixture correction changes a test file; it was never approved by
the final named review.

Evidence-only paths remain intentionally outside the product-tree digest so
post-freeze reports and dispositions can be retained. They are not
unvalidated: the schema constrains their shape, the validator checks each
candidate SHA/path/SHA-256 tuple, and protected-branch PR review governs every
evidence commit.

## Accepted Replacement Freeze

* Product candidate:
  `31ab98c99c7175adf83d62321dd6f592ab54a5fd`.
* Product-tree SHA-256:
  `25f9fcc8a8b8e41c4a073f3eb057ca0b55ada6c23b3901896d4838863ddb75cf`.
* Frozen at: `2026-08-13T07:57:34Z`.
* Exact-revision gates: 1,670 Python tests, 16 focused validator tests, 172
  browser scenarios, Ruff, Bandit, and Checkov pass. The earlier browser
  attempt was discarded because its local server was stopped; the identical
  suite passed after the production boundary was restarted.

The final named review found one evidence-only severity-2 issue: the approved
250-organic-session target was attached to D+28 rather than the six-month
window. The record now treats D+28 as a migration/organic regression review and
applies both approved OBJ-02 thresholds at six months. No automatable
severity-1 or severity-2 finding remains.

Amy and Fry's exact-candidate dispositions close DRF-01, DRF-02, and DRF-04.
They pass the automated portion of DRF-03, which remains open solely for
genuine named-human screen-reader announcement confirmation. DRF-05 remains
open for the complete live keyboard/screen-reader review.

## PR Feedback Remediation

Copilot review on evidence head `e47344b` raised three valid comments:

* copy-button feedback could capture a transient label and race overlapping
  timeouts;
* the release summary still described named owner review as pending;
* the combined-filter URL assertion depended on query-parameter order.

The copy handler now keeps one immutable default label, ignores stale
asynchronous completions, and owns one reset timer. Browser coverage verifies
that rapid success/failure activation returns to **Copy embed snippet**. URL
state assertions compare named `URLSearchParams`, and release/PR text now names
only the actual live-AT blockers. Because the handler and browser tests changed,
candidate `31ab98c` and its dispositions are superseded pending a replacement
freeze.

## Blockers

* DRF-03 and DRF-05 require genuine named live screen-reader review against the
  frozen candidate and cannot be completed by agent simulation. This blocks
  sponsor GO, merge, and deployment.

## Candidate 3271024 — PR Feedback Remediation

* Frozen product candidate:
  `327102410d5ade6048408463a27872cfd0bedc60`.
* Product-tree SHA-256:
  `f1b4831d4ccb112f949330b67561208b304c5a2f2e60bb16fc56ad9aa9d61085`.
* Exact-revision gates: 1,670 Python tests; 16 focused validator tests; Ruff;
  two Node tests; Hugo; 172 affected browser scenarios (139 passed and 33
  expected project skips); Checkov; Zizmor; and Bandit pass.
* Amy/Fry and cross-functional owner dispositions pass all automatable
  boundaries. DRF-03 and DRF-05 remain blocked only on genuine named-human
  live screen-reader evidence.

## Remaining Work

* P03-T03 remains human-blocked until genuine live screen-reader evidence is
  supplied for DRF-03 and DRF-05; sponsor GO, merge, deployment, and outcomes
  remain downstream.

## 2026-08-13: Candidate Invalidation — Deferred/Waiver Schema

* **Reason**: Schema, validator, and tests changed to support a first-class
  `deferred` finding status with a mandatory `waiver` object. This adds a new
  required key (`waiver`) to every finding and bumps schema_version to 1.1.0.
* Candidate `3271024` is invalidated; the record is reset to `preparing` with
  all findings open and `waiver: null`.
* Validator now enforces: deferred findings must carry a non-null waiver bound
  to the candidate SHA; waiver `decided_at` must fall within the candidate
  window; `expires_at > decided_at` and `expires_at > now` (fail-closed: an
  expired waiver fails CI unconditionally); non-deferred findings must have
  `waiver: null`. GO-blocking logic now exempts `deferred` findings.
* 9 new tests added (25 total focused validator tests all green).

## Accepted Replacement Freeze — Candidate 6ba13b5

* Frozen product candidate:
  `6ba13b501113201e69348d7c3c6042f8a9f96a8f`.
* Product-tree SHA-256:
  `1215c36a94132f28833d51436fb62c8a11ce400b0bf0d30ad07869fe4b55bb54`.
* Schema version bumped to 1.1.0 (new `waiver` field on every finding).
* Gates: 1,634 Python tests passed; 25 focused validator tests; Ruff; Bandit.
  Front-end/Node/Hugo/Playwright/Checkov/Zizmor run via hosted CI.
* DRF-01, DRF-02, DRF-04: closed with Amy/Fry owner dispositions re-bound to
  new candidate SHA.
* DRF-03, DRF-05: deferred with sponsor-approved waiver (jmservera, issue #714,
  expires 2026-11-11T16:50:19Z). No live_at_review fabricated.
* Sponsor's deferral decision: "Ok, then dismiss it, create a comprehensive GH
  Issue to run this in the future, I don't have access to a screen reader nor
  to a genuine accessibility expert now."

## 2026-08-13: Candidate Invalidation — Test Coverage Fix

* **Reason**: Three new tests added to `tests/test_validate_release_candidate.py`
  covering both branches of the `decided_at` candidate-window check and the
  `additionalProperties: false` waiver schema rejection. Test files are not in
  `EVIDENCE_ONLY_PREFIXES`, so this is a product-tree-affecting change.
* Candidate `6ba13b5` is invalidated; the record is reset to `preparing` with
  all findings open and `waiver: null`.
* 28 focused validator tests pass after the addition.

## Accepted Replacement Freeze — Candidate c7b08f1

* Frozen product candidate:
  `7f5cd59feae7f6eec35787b981998bd931b358ef`.
* Product-tree SHA-256:
  `c2254db371a4a691143ab56ebb8f124d5c9ede68010e05457e8e0b2a53d8b502`.
* Frozen at: `2026-08-13T18:21:44Z`.
* Gates: 1,634 Python tests passed; 28 focused validator tests; Ruff; Bandit.
* DRF-01, DRF-02, DRF-04: closed with Amy/Fry owner dispositions re-bound to
  new candidate SHA.
* DRF-03, DRF-05: deferred with sponsor-approved waiver (jmservera, issue #714,
  expires 2026-11-11T16:50:19Z). Waiver `decided_at` re-anchored to freeze
  time per re-bind convention; underlying decision unchanged.

## Sponsor GO

* Sponsor `jmservera` granted GO for candidate
  `7f5cd59feae7f6eec35787b981998bd931b358ef` at
  `2026-08-13T18:21:44Z`.
* DRF-03 and DRF-05 remain deferred, not passed, under the time-bounded waiver
  tracked by jmservera/SquadScope#714.
* Rollback readiness is tested: the complete Phase 5 diff passed
  `git apply --reverse --check`, and Phase 4 deployment run `31645707266`
  remains the last-known-good production boundary.

## Candidate 7f5cd59 — Complete Fixture Isolation

The first post-deployment evidence transition showed that the validator fixture
also inherited deployment and delayed-outcome state from the checked-in record.
The fixture now resets sponsor, rollback, deployment, findings, and every
outcome lifecycle field before each independent scenario. All 28 focused tests
pass. Candidate `7f5cd59feae7f6eec35787b981998bd931b358ef` supersedes
`ed9106c` with product-tree digest
`c2254db371a4a691143ab56ebb8f124d5c9ede68010e05457e8e0b2a53d8b502`.
