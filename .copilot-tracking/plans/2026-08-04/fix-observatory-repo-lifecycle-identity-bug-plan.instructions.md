---
applyTo: '.copilot-tracking/changes/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-changes.md'
---
<!-- markdownlint-disable-file -->
# Implementation Plan: Fix observatory_repos.py Lifecycle Ledger Duplicate-Identity Bug

## Overview

Fix the non-idempotent repository-lifecycle-ledger key-merge bug in
`scripts/observatory_repos.py` and use the fixed script to regenerate topics/data/
repo-page content from stored `data/` on a reviewed branch, closing the technical
blocker on the `repo_pages` rollout without changing the production flag itself.

## Objectives

### User Requirements

* Enable `repo_pages` and rebuild the whole site (topics, data) with stored
  information — Source: user request, prior conversation turn
* Fix the ledger reload bug before `repo_pages` can be safely enabled — Source:
  prior agent turn's recommendation, confirmed by the user proceeding to plan it

### Derived Objectives

* Fix the `load_repository_histories()` key-merge bug so repeated generation runs
  are idempotent — Derived from: root-cause research showing every run
  re-duplicates ledger entries, corrupting production if shipped
* Add regression test coverage for the exact two-pass duplicate scenario — Derived
  from: existing tests (`test_stable_id_absorbs_seeded_fallback_history`) do not
  cover a second, ledger-informed pass against unchanged raw week files
* Restore the strict assertions in `test_frozen_corpus_lifecycle_seed_has_expected_parity`
  per its own `TEMP (#652)` comment — Derived from: the comment explicitly says to
  restore once the ledger-refresh fix lands
* Regenerate topics/data/repo-page content end-to-end on a branch to validate the
  fix at full corpus scale and produce reviewable output — Derived from: the
  original "rebuild the whole site" request
* Defer flipping `repo_pages.enabled = true` on `main` and the associated Hermes/
  URL/sponsor sign-offs to a separate follow-on decision — Derived from: existing
  repo governance (gated rollout plan, owner-action-register.md) requires explicit
  sponsor approval independent of this technical fix

## Context Summary

### Project Files

* scripts/observatory_repos.py - contains the defective `load_repository_histories()`
  (lines 437-528, defect at 456-478) and `write_repository_pages()` (lines 922-996)
* tests/test_observatory_repos.py - existing migration test (589-627) and the
  relaxed frozen-corpus parity test (556-587) with the `TEMP (#652)` comment
  (573-577)
* config/observatory.toml - `[repo_pages] enabled = false` (stays false on `main`
  through this plan)
* docs/review/data-observatory-relaunch/owner-action-register.md - sponsor/Hermes/
  URL gates for actual production activation (out of scope, referenced only)

### References

* .copilot-tracking/research/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-research.md - synthesized research
* .copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md - full root-cause detail with code citations
* .copilot-tracking/research/subagents/2026-08-02/claracle-rollout-cost-followup-research.md - prior rollout-safety research
* .copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md - Phase 2 identity precondition this fix closes
* GitHub issue #652 - tracks the drift symptom in production terms

### Standards References

* docs/qa-gates.md - repository validation command conventions

## Implementation Checklist

### [x] Implementation Phase 1: Fix the Ledger Identity-Merge Bug

<!-- parallelizable: false -->

* [x] Step 1.1: Add a `full_name -> current key` reverse index to `load_repository_histories()`
  * Details: .copilot-tracking/details/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-details.md (Lines 15-45)
* [x] Step 1.2: Keep the reverse index current across migrations within one pass
  * Details: .copilot-tracking/details/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-details.md (Lines 47-60)
* [x] Step 1.3: Harden `write_repository_pages()` with a slug-collision guard
  * Details: .copilot-tracking/details/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-details.md (Lines 62-78)

### [x] Implementation Phase 2: Add Regression Coverage and Restore Weakened Assertions

<!-- parallelizable: false -->

* [x] Step 2.1: Add a two-pass duplicate-identity regression test
  * Details: .copilot-tracking/details/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-details.md (Lines 82-104)
* [x] Step 2.2: Restore strict assertions in `test_frozen_corpus_lifecycle_seed_has_expected_parity`
  * Details: .copilot-tracking/details/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-details.md (Lines 106-120)
* [x] Step 2.3: Run targeted tests for this phase
  * Details: .copilot-tracking/details/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-details.md (Lines 122-130)

### [ ] Implementation Phase 3: Regenerate Site Content From Stored Data on a Branch

<!-- parallelizable: false -->

* [ ] Step 3.1: Create the working branch and enable `repo_pages` locally for validation only
  * Details: .copilot-tracking/details/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-details.md (Lines 134-146)
* [ ] Step 3.2: Refresh taxonomy, topic candidates, data pages, and dataset export
  * Details: .copilot-tracking/details/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-details.md (Lines 148-160)
* [ ] Step 3.3: Run repository-page generation twice and confirm byte-identical output
  * Details: .copilot-tracking/details/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-details.md (Lines 162-178)
* [ ] Step 3.4: Review the full generated-content diff before any commit decision
  * Details: .copilot-tracking/details/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-details.md (Lines 180-190)

### [ ] Implementation Phase 4: Validation

<!-- parallelizable: false -->

* [ ] Step 4.1: Run full project validation
  * Execute `python -m pytest tests/`, `ruff check .`, `ruff format --check .`
  * Execute `hugo --minify` and `npx "pagefind@1.5.2" --site public/`
  * Execute `python scripts/check_internal_links.py public --base-url "https://claracle.com/"`
* [ ] Step 4.2: Fix minor validation issues
  * Iterate on any lint/test failures surfaced by the fix or regenerated content
* [ ] Step 4.3: Report the remaining sponsor-gated rollout decision
  * Document that flipping `repo_pages.enabled = true` on `main` and recording
    Hermes/URL/jmservera sign-off remain a separate, already-tracked decision
    (owner-action-register.md, gated rollout plan Phases 4-5); this plan closes
    only the technical blocker

## Planning Log

See .copilot-tracking/plans/logs/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-log.md
for discrepancy tracking, implementation paths considered, and suggested follow-on work.

## Dependencies

* Python 3, pytest, ruff (existing repo tooling)
* Hugo (now installed locally via `sudo apt install hugo`)
* `npx "pagefind@1.5.2"` (Node.js, already available)
* No new services or dependencies

## Success Criteria

* `load_repository_histories()` produces byte-identical output across repeated
  invocations against the same corpus — Traces to: root-cause research
* New regression test reproduces and catches the exact two-pass duplicate scenario — Traces to: test coverage gap finding
* `test_frozen_corpus_lifecycle_seed_has_expected_parity` strict assertions restored
  per its own `TEMP (#652)` comment — Traces to: issue #652
* Repository pages, topics, and data content regenerated from stored `data/` on a
  branch with a reviewable diff and byte-stable second generation — Traces to: user's
  "rebuild the whole site" request
* `repo_pages.enabled` remains `false` on `main`; production activation explicitly
  deferred to the existing sponsor-gated process — Traces to: repo governance
