<!-- markdownlint-disable-file -->
# Research: Fix observatory_repos.py Lifecycle Ledger Duplicate-Identity Bug

## Scope

Enable the `repo_pages` rollout and rebuild topics/data/repo-page content from stored
`data/` by fixing a confirmed, reproduced bug in `scripts/observatory_repos.py` that
makes repeated repository-page generation non-idempotent, before attempting any
further preflight or production activation.

## Trigger

Manual preflight in a prior conversation turn: on a scratch branch with
`repo_pages.enabled = true`, running `python3 scripts/observatory_repos.py` (generate)
twice in a row produced 270 pages then 487 pages (should be byte-stable). The
lifecycle ledger grew from ~2242 to 2637 entries. This blocks the sponsor-gated
`repo_pages` rollout (`config/observatory.toml`) and is the same drift symptom
already tracked by GitHub issue #652 and a `TEMP (#652)` relaxed assertion in
`tests/test_observatory_repos.py`.

## Root Cause (see subagent research for full detail)

Key-merge/identity-migration bug in `load_repository_histories()`
(scripts/observatory_repos.py lines 437-528, defect at lines 456-478). Raw crawl
weeks only recently began carrying a numeric GitHub `id`. When an id-carrying
observation is processed, the migration branch (line 458) pops the repo's
`name:`-keyed history out of `histories` and reinserts it under the numeric key —
correct once. But the ledger is then persisted with the repo *only* under the
numeric key. On every subsequent run, the older, id-less raw weeks for that same
repo resolve `key == legacy_key` (the `name:` form) again; since `legacy_key` no
longer exists in the reloaded `histories`, the migration guard does not fire, and a
brand-new orphan `RepositoryHistory` is minted under the stale `name:` key,
re-absorbing the id-less historical weeks as a phantom duplicate. This repeats and
compounds forever. `write_repository_pages()` last-writer-wins on output path, so
`content/repo/*/index.md` file count does not double, but the console-printed page
count, `data/derived/observatory/repositories.json`, and
`data/derived/observatory/repository-lifecycle.json` all accumulate real duplicate
entries every run.

`seed_lifecycle()` shares the identical `load_repository_histories()` path and is
not structurally immune: its parity guard dedupes by `(display_name, slug)`, which
collapses a canonical/duplicate pair into one set element, so it can pass even when
`histories` (persisted in full, unconditionally, immediately after the check)
contains duplicate keys.

## Fix Direction

Build a `full_name -> current key` reverse index from the initially loaded ledger
histories, before iterating raw weeks, and consult it whenever the observation's own
computed `key`/`legacy_key` are both absent from `histories` — reuse/migrate the
matching history instead of minting a new one, updating the index on every
migration. This is the smaller, surgical fix consistent with the existing migration
pattern (vs. a more invasive redesign that skips reprocessing raw weeks already
reflected in the ledger).

## Test Coverage Gap

`test_stable_id_absorbs_seeded_fallback_history`
(tests/test_observatory_repos.py:589-627) only exercises a single migration pass; it
never re-invokes `load_repository_histories()` a second time against raw week files
still containing the original id-less observation, which is the real production
shape (historical weeks are static, checked-in files reprocessed every run). A new
fixture with two raw weeks for the same repo (one id-less, one id-bearing), loaded
twice in sequence using the first pass's persisted ledger as input to the second,
is needed to catch this regression.

`test_frozen_corpus_lifecycle_seed_has_expected_parity`
(tests/test_observatory_repos.py:556-587) already has a `TEMP (#652)` comment
(lines 573-577) that explicitly says to restore its strict assertions once the
ledger-refresh fix lands.

## References

* Subagent research (full detail, code citations):
  .copilot-tracking/research/subagents/2026-08-04/observatory-repos-ledger-duplicate-identity-bug.md
* Prior rollout research: .copilot-tracking/research/subagents/2026-08-02/claracle-rollout-cost-followup-research.md
* Gated rollout plan (Phase 2 identity precondition):
  .copilot-tracking/plans/2026-08-02/claracle-gated-rollout-cost-plan.instructions.md
* GitHub issue #652 (tracks the drift symptom in production terms)
* docs/review/data-observatory-relaunch/owner-action-register.md (sponsor/Hermes/URL
  gates for actual production activation — out of scope for this fix)

## Known Constraints

* Weekly crawl/analysis pipeline must not be modified.
* Podcaster handoff contract (`scripts/podcaster_handoff.py`, `config/podcast.json`)
  must not change.
* `repo_pages.enabled` stays `false` on `main` until Hermes/URL/jmservera sign-offs
  are separately recorded (existing governance, not part of this fix's scope).
* Hugo is now available locally (`sudo apt install hugo` succeeded in this session),
  so local `hugo --minify` validation is possible for this plan, unlike prior
  sessions where it had to be deferred to CI.
