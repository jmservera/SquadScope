<!-- markdownlint-disable-file -->
# Release Changes: Fix observatory_repos.py Lifecycle Ledger Duplicate-Identity Bug

**Related Plan**: [fix-observatory-repo-lifecycle-identity-bug-plan.instructions.md](../../plans/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-plan.instructions.md)
**Implementation Date**: 2026-08-04

## Summary

This release fixes the non-idempotent repository-lifecycle-ledger key-merge bug in `scripts/observatory_repos.py`. The bug caused `load_repository_histories()` to produce duplicate identities for repositories when run multiple times against the same corpus, corrupting the qualified repository count and ledger state. The fix implements a full-name reverse index to ensure id-less observations reuse existing migrated identities rather than minting duplicates. Regression test coverage is added, existing weakened assertions are restored, and the entire site content (topics, data, repository pages) is regenerated from stored `data/` to validate the fix at corpus scale.

## Changes

### Added

* `tests/test_observatory_repos.py` - New regression test `test_two_pass_duplicate_identity_regression()` verifying the two-pass duplicate-identity scenario
* `tests/test_observatory_repos.py` - New unit test `test_write_repository_pages_raises_on_slug_collision()` verifying the slug-collision guard in Phase 1 Step 1.3
* Generated repository pages and data content from regeneration on validation branch

### Modified

* `scripts/observatory_repos.py` - Fix `load_repository_histories()` with full-name reverse index (Step 1.1-1.2) and harden `write_repository_pages()` with slug-collision guard (Step 1.3)
* `tests/test_observatory_repos.py` - Correct the recurrence fixture, add slug-collision coverage, and retain strict frozen-corpus assertions
* `tests/test_page_css_bundles.py` - Accept quoted or unquoted minified stylesheet links and assert the current `.article-cover` module selector

### Removed

* (None — no existing code removed by the fix logic)

## Additional or Deviating Changes

* PR #663 temporarily enabled repository pages for corpus validation, then restored `repo_pages.enabled = false` before merge; the follow-on branch keeps it disabled
* The full suite exposed a stale CSS test that assumed quoted Hugo attributes and the removed `.article-visual` selector; Step 4.2 updated the test without changing production CSS
* The atomic publish proof failed intermittently twice, passed in isolation, and passed in the final full-suite run; no publish transaction code changed without a reproducible causal defect

## Release Summary

### Phase 1: Fix the Ledger Identity-Merge Bug ✅

**Implementation completed**: Reverse-index fix to `load_repository_histories()` and slug-collision guard to `write_repository_pages()`.

**Key changes**:
- Added `full_name_to_key` reverse index after ledger loading (lines 446-448)
- Updated reverse index during in-pass key migrations (line 468)
- Added defensive slug-collision guard in `write_repository_pages()` (lines 964-970)

**Files modified**:
- `scripts/observatory_repos.py` - Core bug fix

### Phase 2: Add Regression Coverage and Restore Assertions ✅

**Implementation completed**: Regression tests for two-pass duplicate-identity scenario and slug-collision guard, plus restored strict assertions in frozen corpus parity test.

**Key changes**:
- Corrected `test_two_pass_duplicate_identity_regression()` so both raw weeks exist before pass one and pass two reloads the persisted numeric ledger against unchanged files
- New test `test_write_repository_pages_raises_on_slug_collision()` verifies the defensive slug-collision guard catches identity collisions before corrupting derived data
- Removed TEMP (#652) relaxation; restored exact-match assertions in `test_frozen_corpus_lifecycle_seed_has_expected_parity()`
- All 23 focused observatory tests pass

**Files modified**:
- `tests/test_observatory_repos.py` - Corrected recurrence regression and added collision coverage

### Phase 3: Regenerate Site Content From Stored Data ✅

**Implementation completed**: Full regeneration of topics, data, and repository pages from checked-in `data/` with byte-stable idempotency verification.

**Key results**:
- 7 new repository pages created
- 263 existing repository pages updated with latest observations
- Taxonomy refreshed (topics.json, tags.json, topic-candidates.json)
- Dataset export regenerated (663 repositories)
- **Idempotency verification**: Run 1 = 270 pages, Run 2 = 270 pages (no growth) — confirms Phase 1 bug is fixed (previously showed 270→487)
- SHA256 checksums identical across runs

**Files modified**: 281 files total
- Generated content: `content/repo/`, `content/data/`, `data/derived/observatory/`, `data/taxonomy/`, `static/datasets/`

### Phase 4: Full Project Validation ✅

**Validation pipeline results**:
- pytest: 1,456 tests and 34 subtests pass; 2 expected sanitization warnings
- Targeted pytest: 23 observatory tests pass
- Ruff 0.15.7 lint and format checks pass across 150 Python files
- Hugo 0.146.0 builds 2,704 pages successfully
- Pagefind 1.5.2 indexes 297 pages and 10,185 words
- Internal link check passes with no broken links

**Configuration note**:
- `config/observatory.toml` `repo_pages.enabled` reverted to `false` before final commit
- Branch-only temporary `enabled = true` was used only for validation; production remains safe
- Production activation is a separate gated decision per owner-action-register.md and gated-rollout-cost-plan.instructions.md

### Summary Statistics

**Total files affected by the original implementation**: 284 (core fix, tests, tracking, and regenerated content)
**Follow-on branch changes**: Test coverage and tracking only; no production activation or generated-content changes
**Generated/regenerated content**: 281 files
**Test suite**: 1,456 tests and 34 subtests passing

**Key outcomes**:
- ✅ Repository lifecycle ledger now idempotent across repeated generation runs
- ✅ Bug-fixing reverse index prevents duplicate name:-keyed identities
- ✅ Two-pass duplicate-identity regression test added and passing
- ✅ Slug-collision guard defensive test added and passing
- ✅ Frozen corpus parity assertions restored to strict exact-match checks
- ✅ Full site content regenerated with byte-stable second generation (Phase 3 idempotency proof)
- ✅ All validation checks passing (pytest, lint, Hugo, links)
- ✅ `repo_pages.enabled` remains `false` on `main`; production activation deferred to existing gated rollout governance

