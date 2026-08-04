# Research: observatory_repos.py repository lifecycle ledger duplicate-identity bug

## Topic / Questions

Investigate why running `scripts/observatory_repos.py` generate() twice in a row
(with `repo_pages.enabled = true`) grows the repository lifecycle ledger and the
qualified/page count (270 -> 487 pages, ledger 2242 -> 2637 entries), blocking the
repo_pages rollout. Determine exact root cause, whether it is a key-merge bug vs
field-population bug, which functions/lines need to change, whether existing tests
cover it, whether `seed_lifecycle()` shares the bug, and what else assumes key
stability.

## Method

Read-only investigation only, no repo files modified. To get concrete evidence
(rather than guessing), copied `scripts/`, `config/`, `data/raw`, `data/archive`,
`data/taxonomy`, `data/derived/observatory`, `content/repo` into an isolated `/tmp`
sandbox, flipped `repo_pages.enabled = true` in the sandbox copy only, and ran
`generate()` twice, inspecting the resulting ledger/derived JSON between runs.
This reproduced the reported 270 -> 487 / 2242 -> 2637 growth exactly.

## Root Cause

File: scripts/observatory_repos.py, function `load_repository_histories()`
(lines 437-528). The specific defective logic is lines 456-478:

```python
key = repository_key(observation.github_id, observation.full_name)          # 456
legacy_key = f"name:{normalize_full_name(observation.full_name)}"           # 457
if key != legacy_key and key not in histories and legacy_key in histories:  # 458
    history = histories.pop(legacy_key)                                    # 459
    history.key = key                                                      # 460
    history.github_id = observation.github_id                              # 461
    histories[key] = history                                               # 462
...
history = histories.get(key)                                               # 467
if history is None:                                                        # 468
    history = RepositoryHistory(                                           # 469
        ...
    )
    histories[key] = history
```

`repository_key()` (lines 130-133) returns the numeric `github_id` when present,
else falls back to `f"name:{normalize_full_name(full_name)}"`.

Empirically confirmed: raw crawl data only recently started carrying a numeric
`"id"` field. In the reproduction corpus, only the single most-recent week file
(`2026-W32.json`) has `id` populated for its records; every older week file
(`2026-W21.json` ... `2026-W31.json`, and the archived `recovered-W23-W29` weeks)
has no `id` field at all, so `observation.github_id` is `None` for those
observations on every run, forever (raw files are static, checked-in data).

Sequence that produces the bug:

1. **Run 1** (ledger starts as production's checked-in state: all 2242 entries
   `name:`-keyed). While iterating `raw_week_files(root)` in ascending week order,
   the older, id-less weeks are processed first: `key == legacy_key`, so the
   existing `name:`-keyed history from the ledger is found and observations are
   appended normally. When the loop reaches the newest week (`2026-W32.json`,
   which has `id`), `key` becomes the numeric id, `legacy_key` (`name:...`) is
   still present in `histories`, so the migration branch (line 458) fires: the
   `name:`-keyed entry is popped and reinserted under the numeric key, retaining
   all prior weeks' observations plus the new one. This is the *intended*
   correct behavior and is what the existing test
   `test_stable_id_absorbs_seeded_fallback_history` (line 589) verifies for a
   single pass.
2. **Ledger write**: `lifecycle_ledger_payload()` (line 752) persists `histories`
   as-is. The `name:`-keyed entry no longer exists in the dict at all — it was
   consumed by the pop/migrate — so the written ledger has the repo *only* under
   its numeric key.
3. **Run 2**: `load_repository_histories()` reloads the ledger, so `histories`
   starts containing the numeric-keyed entry only (no `name:` entry for that
   repo). The function then unconditionally reprocesses *all* raw week files
   from scratch (`raw_week_files(root)` at line 446, no incremental/short-circuit
   logic). For the older, id-less weeks, `key` is computed as `name:...` again
   (line 456) — same as always, since those raw records never carry `id`. The
   migration check (line 458) does NOT fire this time because its precondition
   `legacy_key in histories` is now false (the `name:` entry was removed from the
   ledger in step 2). Then `history = histories.get(key)` (line 467) returns
   `None` (the numeric-keyed entry is not indexed by the `name:` key at all), so
   a **brand-new, empty `RepositoryHistory` is minted under the stale `name:`
   key** (lines 468-478) and re-absorbs every id-less historical observation for
   that repo as if it were a never-before-seen repository.
4. This orphaned `name:` duplicate independently re-qualifies (it still has more
   than the `minimum_weeks` distinct weeks, just missing the one week that
   happened to carry an `id`), so `eligible_repositories()` (line 531) and
   `write_repository_pages()` (line 922) treat it as a second, distinct
   repository with the same `display_name`/`slug` as the canonical numeric
   entry.
5. Because `write_repository_pages()` builds `expected: dict[Path, str]` keyed by
   output path (line ~935), the physical `content/repo/<slug>/index.md` file is
   NOT actually duplicated on disk (last-writer-wins on the dict), but:
   - `written.append(output_path)` (inside the `for history in eligible` loop,
     around line 942-946) appends once per *history*, so the same path is
     appended twice, inflating `len(written)` / the "Generated N repository
     pages" console count (this is what showed 487 instead of 270-ish — the
     count is of eligible histories, not unique files).
   - `data/derived/observatory/repositories.json` (`derived.append(params)`,
     same loop) gets two entries with the same `repo_slug` — confirmed
     empirically: 487 entries, only 270 unique slugs, 217 duplicated slugs.
   - `repository-lifecycle.json` gets a genuine duplicate top-level key
     (`name:<repo>` alongside the numeric key) — confirmed: ledger grew from
     2242 to 2637 real distinct keys, with 217 of the 224 new numeric+existing
     qualified pairs being true duplicates of an already-numeric-keyed history
     (verified via matching `current_full_name` across two different keys).
   - This is a **permanent, ever-repeating** corruption: every subsequent run
     recreates the same orphaned `name:` duplicates, because raw week files are
     reprocessed from scratch every time and the ledger never retains a
     "this `full_name` now lives at key X" mapping once a `name:` entry is
     migrated away.

Correction to the manual reproduction notes: the `slug: None` observation in the
bug report does not match what the code actually produces. In the reproduction,
`current_slug` was populated for every entry (`RepositoryHistory.slug` is always
computed via `repo_slug()`, which never returns `None`, at every construction
site: line 372 `history_from_ledger`, line 425 `apply_configured_renames`, line
469 `load_repository_histories`, and inside `add_observation` line ~355). The
duplicate/orphan entries are actually the **`name:`-prefixed** ones (263 of them
after two runs, matching the exact pre-existing production qualified count), not
numeric ones; the numeric-keyed entries are the *correct*, fully-populated
canonical histories (224 qualified, 7 of which are legitimately new — 224 - 7 =
217 duplicate pairs, exactly matching the growth 487 - 270 = 217). This detail
should be verified again by whoever inspected the ledger manually, but it does
not change the diagnosis or the fix location.

## Is it a key-merge/migration bug or a field-population bug?

**Key-merge/migration bug.** The one-directional migration in
`load_repository_histories()` (lines 456-462) correctly moves a `name:`-keyed
history to a stable numeric key the *first* time it sees an `id`-carrying
observation, but it has no mechanism to prevent a *later* (or, on a repeat run,
*any*) id-less observation for the same `full_name` from re-minting a stale
`name:` identity, because:
- There is no reverse index from `full_name` to "current canonical key".
- The lookup at line 467 (`histories.get(key)`) only ever checks the key
  computed from the *current* observation's own `github_id` (or lack thereof);
  it never checks whether some *other* key in `histories` already has a matching
  `display_name`/`full_name`.
- The migration is not idempotent across the full observation set: it depends on
  which observation (id-carrying or not) is processed last for a given
  `full_name`, and — critically — the second and all subsequent invocations of
  `load_repository_histories()` never see the original `name:` entry again once
  the ledger has been rewritten, so the "recreate as new" branch always wins for
  the id-less observations from then on.

There is no field-population bug: slug/display_name are always correctly
computed for the freshly-minted duplicate; the duplicate is a structurally valid
but semantically wrong *second identity* for an already-known repository.

## Functions/line ranges that need to change

- `scripts/observatory_repos.py` `load_repository_histories()`, lines 437-528,
  specifically the per-observation key resolution block at **lines 456-478**.
  The fix needs a `full_name -> key` (or `full_name -> history`) index built
  once from the initially-loaded ledger histories (before the raw-week loop, so
  right after line 444) so that when `key` (numeric) is not in `histories` and
  `legacy_key` (`name:`) is also not in `histories`, the code can still look up
  "does any known history already have `display_name == observation.full_name`
  (or `full_name` in `prior_full_names`)?" and reuse/migrate that entry instead
  of unconditionally creating a new one. Equivalently, the migration check at
  line 458 needs to run for *every* observation regardless of whether `key`
  happens to equal `legacy_key` for that particular observation — the current
  guard `key != legacy_key` only handles the exact moment an id first appears;
  it does not handle "this id was already adopted under a different, non-`name:`
  key that isn't `legacy_key`'s current form."
- Secondary/consequential fix: `write_repository_pages()`
  (scripts/observatory_repos.py lines 922-996), specifically the
  `for history in eligible:` loop (~lines 936-946) that does
  `written.append(output_path)` and `derived.append(params)` unconditionally per
  history. Even with the identity bug fixed, this loop has no defense against
  two different history *keys* resolving to the same `slug`/output path — worth
  hardening (e.g., detect/raise on slug collision) as a regression guard, though
  the root fix in `load_repository_histories()` should make this path
  unreachable in the intended flow.

## Test coverage review — tests/test_observatory_repos.py

- `test_stable_id_absorbs_seeded_fallback_history` (line 589-627): covers only a
  **single** call to `load_repository_histories()` where the *old* (id-less)
  observation exists solely inside the pre-supplied ledger (constructed directly
  in the test, not backed by any raw week file), and a *new* raw week file
  supplies the id-carrying observation. This exercises the migration succeeding
  once, but never exercises what happens when `load_repository_histories()` is
  called *again* afterward against raw week files that still contain the
  original id-less observation on disk (which is the real production shape:
  historical weeks are permanent, checked-in JSON files that get reprocessed
  every run, not one-time ledger seed data). It does not catch this bug.
- `test_seed_lifecycle_writes_only_ledger_and_is_byte_stable` (line 494-521) and
  `test_stable_id_rename_creates_alias_and_positive_archive_evidence` (line
  355-393) both call `generate()`/`seed_lifecycle()` twice and assert byte
  stability / absence of the old key — but in both cases *every* week's raw
  record consistently has a `github_id` (via `repo_record(..., github_id=...)`)
  or consistently lacks one; none of these fixtures mixes id-less historical
  weeks with an id-bearing later week across two full re-invocations of
  `load_repository_histories()` from raw files (as opposed to from a
  hand-built ledger). That specific combination — some raw week files with `id`,
  some without, for the *same* repo, reloaded from a ledger that has *already*
  migrated it once — is exactly the untested gap.
- **Already-known/tracked**: `test_frozen_corpus_lifecycle_seed_has_expected_parity`
  (line 556-587) contains an explicit acknowledgment of drift, with a `TEMP
  (#652)` comment (lines 573-577):
  > "while repo_pages is disabled, each crawl grows the corpus and adds
  > github_id-keyed histories, and the lifecycle ledger is not refreshed, so the
  > exact corpus size, the all-name-key identity assumption, and the exact
  > ledger match drift every crawl. They are relaxed to non-regressing checks
  > until the ledger-refresh fix lands; restore the strict assertions on #652."
  The assertion was weakened from an exact `len(histories) == 2242` to
  `len(histories) >= 2242` specifically because of this class of bug. This is
  strong corroborating evidence that the team already knows the corpus/ledger
  drifts on every load, tracked as issue/work item **#652**, though the test
  comment frames it as "the ledger is not refreshed" (a `seed_lifecycle`
  gap) rather than explicitly describing the duplicate-identity mechanism found
  here. Recommend cross-referencing #652 when filing/fixing this.
- **New fixture needed for a real regression test**: two raw week files for the
  same repo — one older week with no `id` field, one newer week with `id` set —
  fed through `load_repository_histories()` **twice in sequence, using the
  ledger persisted by the first call as the input to the second** (i.e.,
  `ledger = lifecycle_ledger_payload(load_repository_histories(root, ledger=ledger1))`
  then reload). Assert that after the second call there is still exactly one
  history for that `full_name`/key, not two. This is fundamentally different
  from `test_stable_id_absorbs_seeded_fallback_history`, which never performs a
  second, ledger-informed pass against the *same* raw files.

## Does `seed_lifecycle()` share the bug?

**Yes, it calls the identical `load_repository_histories()` path** (line
822-861, ledger load at line 834, histories built at line 835) and is subject to
the exact same duplicate-minting mechanism internally. However, `seed_lifecycle()`
has a built-in parity guard (lines 849-855):

```python
qualified_identities = {
    (history.display_name, history.slug) for history in histories.values() if history.qualified
}
page_identities, derived_identities = existing_repository_identities(root)
if qualified_identities != page_identities or qualified_identities != derived_identities:
    raise ValueError("Lifecycle seed parity mismatch: ...")
```

Empirically reproduced in the sandbox: calling `seed_lifecycle()` against the
current production ledger/raw corpus (with `enabled = false`, the real
production setting) raises `ValueError: Lifecycle seed parity mismatch:
qualified=270, pages=263, derived=263` and **does not write anything** — this
run only had 7 newly-qualifying repos (crossing the threshold via the
id-carrying week), no duplicates yet, so this particular failure is unrelated to
the duplicate-identity bug itself; it's the intended "don't seed a ledger that
doesn't match already-committed pages" guard doing its job.

Important caveat: `qualified_identities` is a **set of `(display_name, slug)`
tuples**, so if a `name:`-keyed orphan and its numeric-keyed canonical twin exist
simultaneously (both with qualified=True, both sharing `display_name`/`slug`),
they collapse into a single set element and the parity check would *not*
detect the duplication by count alone. This means: if `seed_lifecycle()` is ever
invoked against a ledger where the duplicate-identity bug has already occurred
(e.g., someone ran `generate()` with `enabled=true` twice, producing the
duplicates, then flips back to `enabled=false` and runs `--seed-lifecycle`), and
the deduplicated `(display_name, slug)` sets still happen to match existing
pages/derived data, the parity check can **pass** while
`lifecycle_ledger_payload(histories)` (called unconditionally at line 861,
after the check) serializes the **full**, non-deduplicated `histories` dict —
persisting the duplicate ledger keys to disk. So `seed_lifecycle()` is not
unconditionally safe against this bug; it only happens to fail loudly in the
specific scenario tested here because new qualifying repos changed the
deduplicated identity set's size, not because it structurally detects
duplicate keys.

## Other repo_pages-adjacent code/tests assuming key stability

- `apply_configured_renames()` (lines 395-434) matches renames by
  `normalize_full_name(history.display_name) == normalize_full_name(renamed_to)`
  across all histories — it would silently merge two independent duplicate
  identities together only if a manual rename override happens to reference
  them, which is not the general case; it does not protect against organic
  key duplication.
- `attach_related_repositories()` (lines 544-598) and `rename_aliases()`
  (lines 725-730) both iterate `histories.values()`/`histories.items()`
  unconditionally; if duplicate identities exist, a repo could show up related
  to itself under two different keys, or accumulate alias entries twice — not
  verified empirically here but structurally plausible given they have no
  slug-collision awareness either.
- `test_frozen_corpus_lifecycle_seed_has_expected_parity` (line 556) is the
  main safety net that would catch a *regenerated-and-committed* corrupted
  ledger reaching `main`, since it runs `load_repository_histories()` directly
  against the real, committed corpus and would need its now-relaxed assertions
  restored (per the `#652` comment) once a fix lands.
- `existing_repository_identities()` (lines 777-799) reads `content/repo/*/index.md`
  and the derived JSON to build `(full_name, slug)` identity sets — used by
  `seed_lifecycle()`'s parity check — and shares the same blind spot: it
  dedupes by `(full_name, slug)`, so it cannot distinguish "one page, one
  ledger entry" from "one page, two ledger entries for the same identity."

## Clarifying questions (not answerable from code alone)

- Whether GitHub work item/issue **#652** referenced in the test comment
  describes this exact duplicate-identity mechanism or a different framing
  ("ledger is not refreshed while repo_pages disabled") — worth checking issue
  #652 directly before scoping a fix, since the fix might already be partially
  designed there.
- Whether the intended design invariant is "one history per stable
  `full_name`, upgrade key in place" (my recommended fix direction) or "ledger
  keys should be frozen once written, and `load_repository_histories()` should
  never re-derive raw observations for weeks already reflected in the ledger"
  (a different, more invasive fix reducing recomputation entirely) — this
  affects which function boundary the fix belongs in.
