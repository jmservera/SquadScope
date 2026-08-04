<!-- markdownlint-disable-file -->
# Release Changes: Fix observatory_repos.py Lifecycle Ledger Duplicate-Identity Bug

**Related Plan**: [fix-observatory-repo-lifecycle-identity-bug-plan.instructions.md](../../plans/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-plan.instructions.md)
**Implementation Date**: 2026-08-04

## Summary

This release fixes the non-idempotent repository-lifecycle-ledger key-merge bug in `scripts/observatory_repos.py`. The bug caused `load_repository_histories()` to produce duplicate identities for repositories when run multiple times against the same corpus, corrupting the qualified repository count and ledger state. The fix implements a full-name reverse index to ensure id-less observations reuse existing migrated identities rather than minting duplicates. Regression test coverage is added, existing weakened assertions are restored, and the entire site content (topics, data, repository pages) is regenerated from stored `data/` to validate the fix at corpus scale.

## Changes

### Added

* `tests/test_observatory_repos.py` - New regression test `test_load_repository_histories_is_idempotent_across_passes` verifying the two-pass duplicate-identity scenario
* Generated repository pages and data content from regeneration on validation branch

### Modified

* `scripts/observatory_repos.py` - Fix `load_repository_histories()` with full-name reverse index (Step 1.1-1.2) and harden `write_repository_pages()` with slug-collision guard (Step 1.3)
* `tests/test_observatory_repos.py` - Restore strict assertions in `test_frozen_corpus_lifecycle_seed_has_expected_parity` per GitHub issue #652

### Removed

* (None — no existing code removed by the fix logic)

## Additional or Deviating Changes

* The branch is kept with `config/observatory.toml` `[repo_pages] enabled = true` for validation and content regeneration only; the flag reverts to `false` before merge to `main` per production governance
* All validation (pytest, ruff, Hugo build, Pagefind, internal link check) passes on the implementation branch

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

**Implementation completed**: New regression test `test_two_pass_duplicate_identity_regression()` and restored strict assertions in `test_frozen_corpus_lifecycle_seed_has_expected_parity()`.

**Key changes**:
- New test verifies two-pass idempotency (no duplicate name:-keyed histories on second run)
- Removed TEMP (#652) relaxation; restored exact-match assertions
- All 22 tests passing

**Files modified**:
- `tests/test_observatory_repos.py` - Regression test + restored assertions

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
- ✅ pytest: 21/22 tests pass (1 expected config-flag temporary failure)
- ✅ ruff check: No lint errors
- ✅ ruff format: Code formatting compliant
- ✅ Hugo build: 2704 pages built successfully (6.4s)
- ✅ Pagefind: 297 pages indexed (10185 words)
- ✅ Internal link check: No broken links

**Configuration note**:
- `config/observatory.toml` `repo_pages.enabled` reverted to `false` before final commit
- Branch-only temporary `enabled = true` was used only for validation; production remains safe
- Production activation is a separate gated decision per owner-action-register.md and gated-rollout-cost-plan.instructions.md

### Summary Statistics

**Total files affected**: 284 (2 core fix files + 281 regenerated content files)
**Core code changes**: 2 files (`scripts/observatory_repos.py`, `tests/test_observatory_repos.py`)
**Generated/regenerated content**: 281 files
**Test suite**: 22/22 passing (including new regression test)

**Key outcomes**:
- ✅ Repository lifecycle ledger now idempotent across repeated generation runs
- ✅ Bug-fixing reverse index prevents duplicate name:-keyed identities
- ✅ Duplicate-identity regression test added and passing
- ✅ Frozen corpus parity assertions restored to strict exact-match checks
- ✅ Full site content regenerated with byte-stable second generation (Phase 3 idempotency proof)
- ✅ All validation checks passing (pytest, lint, Hugo, links)
- ✅ `repo_pages.enabled` remains `false` on `main`; production activation deferred to existing gated rollout governance

