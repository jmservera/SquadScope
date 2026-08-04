<!-- markdownlint-disable-file -->
# Implementation Details: Fix observatory_repos.py Lifecycle Ledger Duplicate-Identity Bug

## Context Reference

Sources: .copilot-tracking/research/2026-08-04/fix-observatory-repo-lifecycle-identity-bug-research.md,
.copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md

## Implementation Phase 1: Fix the Ledger Identity-Merge Bug

<!-- parallelizable: false -->

### Step 1.1: Add a `full_name -> current key` reverse index to `load_repository_histories()`

Build the index once, immediately after `histories` is populated from the loaded
ledger (right after the ledger-loading loop completes, after line 445 and before
line 446, before the raw-week iteration loop begins), mapping
`normalize_full_name(history.display_name)` (or the
existing `prior_full_names`/`current_full_name` tracking already used elsewhere in
the file) to the history's current dict key. When resolving an observation at lines
456-478, if neither `key` nor `legacy_key` is present in `histories`, consult the
reverse index for a match on the observation's normalized full name before minting a
new `RepositoryHistory`. If found, reuse that history (append the observation to it)
instead of creating a duplicate.

Files:
* scripts/observatory_repos.py - `load_repository_histories()`, lines 437-528

Discrepancy references:
* None (first fix step; establishes the core solution)

Success criteria:
* An id-less observation for a repo already migrated to a numeric key in a prior
  ledger reuses that same history instead of minting a `name:`-keyed duplicate
* No change to the existing single-pass migration behavior already covered by
  `test_stable_id_absorbs_seeded_fallback_history`

Context references:
* .copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md (Root Cause and Fix location sections) - exact defect lines and recommended index-based fix

Dependencies:
* None

### Step 1.2: Keep the reverse index current across migrations within one pass

When the migration branch (line 458) fires and a history's key changes during the
same `load_repository_histories()` invocation, update the reverse index entry for
that `full_name` to point at the new key so any later observation in the same pass
(for the same repo, still id-less) also finds the migrated history rather than the
now-stale key.

Files:
* scripts/observatory_repos.py - `load_repository_histories()`, lines 437-528 (same function as Step 1.1)

Success criteria:
* A repo whose identity migrates mid-pass never produces a duplicate within that
  same invocation, matching the existing single-pass test's expectations

Context references:
* .copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md (lines describing the migration branch at 456-462)

Dependencies:
* Step 1.1 completion (same reverse index)

### Step 1.3: Harden `write_repository_pages()` with a slug-collision guard

Add a defensive check in the `for history in eligible:` loop (lines 947-953)
that raises a clear `ValueError` if two different history keys resolve to the same
output slug/path, rather than silently last-writer-wins overwriting one derived
entry with another. This should be unreachable after Steps 1.1-1.2 but guards
against a future regression reaching production undetected.

Files:
* scripts/observatory_repos.py - `write_repository_pages()`, lines 922-996

Success criteria:
* A synthetic slug collision (constructed in a unit test) raises instead of
  silently producing duplicate/inconsistent derived data

Context references:
* .copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md (Secondary/consequential fix note)

Dependencies:
* None (independent hardening, can land alongside Steps 1.1-1.2)

## Implementation Phase 2: Add Regression Coverage and Restore Weakened Assertions

<!-- parallelizable: false -->

### Step 2.1: Add a two-pass duplicate-identity regression test

Add a new test to tests/test_observatory_repos.py with two raw week fixtures for the
same repository — one week with no `id` field, one later week with `id` set. Call
`load_repository_histories()` (or the equivalent generate/seed entry point used by
existing fixtures) once, persist the resulting ledger, then call it again using that
persisted ledger as input, reprocessing the same raw week files unchanged. Assert
that exactly one history exists for that repository's `full_name` after the second
call (not two), and that its `distinct_weeks`/observations reflect both weeks.

Files:
* tests/test_observatory_repos.py - new test near `test_stable_id_absorbs_seeded_fallback_history` (589-627)

Discrepancy references:
* Addresses the test-coverage gap identified in research: existing tests only cover
  a single migration pass, not a second pass against unchanged raw files

Success criteria:
* New test fails against the pre-fix code (reproduces the bug) and passes after
  Phase 1's fix

Context references:
* .copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md (Test coverage review section, "New fixture needed" paragraph)

Dependencies:
* Phase 1 fix implemented (test should be written to fail first if practical, then confirmed passing)

### Step 2.2: Restore strict assertions in `test_frozen_corpus_lifecycle_seed_has_expected_parity`

Remove the `TEMP (#652)` relaxation (tests/test_observatory_repos.py lines 573-577)
and restore exact-match assertions for corpus size, all-`name:`-key identity (where
still applicable), and ledger match, updated to reflect the current, post-fix
expected values against the real committed corpus.

Files:
* tests/test_observatory_repos.py - `test_frozen_corpus_lifecycle_seed_has_expected_parity`, lines 556-587

Discrepancy references:
* Directly resolves the condition the test's own comment says to restore on
  ("restore the strict assertions on #652")

Success criteria:
* Test passes with exact-match assertions against the real committed corpus, no
  `>=` relaxation remaining
* GitHub issue #652 can be closed or updated to reference this fix

Context references:
* .copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md (Test coverage review section, "Already-known/tracked" paragraph)

Dependencies:
* Phase 1 fix implemented

### Step 2.3: Run targeted tests for this phase

Files:
* tests/test_observatory_repos.py

Validation commands:
* `python -m pytest tests/test_observatory_repos.py -q` - confirms new and restored tests pass

## Implementation Phase 3: Regenerate Site Content From Stored Data on a Branch

<!-- parallelizable: false -->

### Step 3.1: Create the working branch and enable `repo_pages` locally for validation only

Create a new branch from `main`. Set `config/observatory.toml` `[repo_pages]
enabled = true` on this branch only, for the purpose of validating the fix and
producing reviewable regenerated content — not for merging to `main` with the flag
enabled.

Files:
* config/observatory.toml - `[repo_pages] enabled` set to `true` on this branch

Success criteria:
* Branch created; flag flipped only in the working branch

Dependencies:
* Phase 1 and Phase 2 completion

### Step 3.2: Refresh taxonomy, topic candidates, data pages, and dataset export

Run, in order, from the repository root:

```bash
python scripts/taxonomy_registry.py
python scripts/discover_topic_candidates.py
python scripts/generate_data_pages.py
python scripts/export_observatory_dataset.py
```

These regenerate topics/data content from checked-in `data/` with no recrawl,
matching the "rebuild the whole site (topics, data)" part of the request.

Files:
* data/taxonomy/topics.json, data/taxonomy/tags.json
* data/topic-candidates.json
* content/data/_index.md and content/data/*/index.md
* static/datasets/open-source-ai-github-projects-2026 (or current dataset path)

Success criteria:
* Each script completes without error; `discover_topic_candidates.py`'s existing
  prompt-injection-phrase warnings (if any) are reviewed, not silently ignored,
  consistent with SEC-01 sanitization behavior

Dependencies:
* Step 3.1 completion

### Step 3.3: Run repository-page generation twice and confirm byte-identical output

Run `python3 scripts/observatory_repos.py` (generate) twice in immediate succession.
Compare `sha256sum data/derived/observatory/repositories.json
data/derived/observatory/repository-lifecycle.json` between the two runs and confirm
they are identical. Also confirm the printed page count and `git status --short
content/repo/ data/derived/observatory/` show no changes between run 1 and run 2.

Files:
* content/repo/*/index.md
* data/derived/observatory/repositories.json
* data/derived/observatory/repository-lifecycle.json

Discrepancy references:
* This step is the direct regression check for the bug this plan fixes; it must
  reproduce the previously-broken 270→487 growth as now stable (no growth)

Success criteria:
* Second generation run produces byte-identical `repositories.json` and
  `repository-lifecycle.json`, and no file changes are reported by `git status`
  after the second run

Context references:
* .copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md (Root Cause reproduction steps)

Dependencies:
* Step 3.2 completion

### Step 3.4: Review the full generated-content diff before any commit decision

Review every created, modified, and removed path under `content/repo/`,
`content/data/`, `content/topics/`, `data/derived/`, `data/taxonomy/`, and
`static/datasets/` for correctness (expected new repository pages, no unexpected
removals of durable pages, no unreviewed dynamic topic promotions since
`topic_hubs.dynamic_creation.enabled` stays `false`).

Files:
* All paths touched by Steps 3.2-3.3

Success criteria:
* Diff reviewed and summarized; no unexpected removals of durable content; no
  dynamic-topic-creation side effects since that flag remains disabled

Dependencies:
* Step 3.3 completion

## Implementation Phase 4: Validation

<!-- parallelizable: false -->

### Step 4.1: Run full project validation

```bash
python -m pytest tests/
ruff check .
ruff format --check .
hugo --minify
npx "pagefind@1.5.2" --site public/
python scripts/check_internal_links.py public --base-url "https://claracle.com/"
```

### Step 4.2: Fix minor validation issues

Iterate on any lint, test, or link-check failures surfaced by the fix or the
regenerated content. Apply direct fixes when corrections are straightforward and
isolated to this change.

### Step 4.3: Report the remaining sponsor-gated rollout decision

Document explicitly, in the PR/commit and in `.copilot-tracking/plans/logs/`, that:

* `repo_pages.enabled` remains `false` on `main` after this plan
* Flipping it to `true` in production and recording Hermes/URL/jmservera sign-off
  remain a separate, already-tracked decision per
  docs/review/data-observatory-relaunch/owner-action-register.md and
  .copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md
  Phases 4-5
* This plan's scope is limited to fixing the technical blocker and producing a
  reviewable regenerated-content branch

## Dependencies

* Python 3, pytest, ruff
* Hugo (locally installed this session)
* Node.js / npx for Pagefind
* No new services or third-party dependencies

## Success Criteria

* Ledger identity-merge bug fixed and covered by a regression test
* `test_frozen_corpus_lifecycle_seed_has_expected_parity` strict assertions restored
* Full site content (repo pages, topics, data) regenerated from stored data with a
  byte-stable second generation and a reviewed diff
* Production `repo_pages.enabled` stays `false`; rollout decision explicitly
  deferred to existing governance
