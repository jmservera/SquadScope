# Podcast Auto-Dispatch Changes — 2026-09-08

## P03 — Tests (Fry)

**Author:** Fry (QA/Tester)  
**Date:** 2026-09-08  
**Branch:** feat/podcast-auto-dispatch  

### Files created

- `tests/test_auto_dispatch_detect.py` — 22 tests across 4 test classes
- `tests/fixtures/auto_dispatch/valid_manifest.json` — W37 manifest with known SHA256
- `tests/fixtures/auto_dispatch/ineligible_manifest.json` — publish_eligible=false
- `tests/fixtures/auto_dispatch/malformed_manifest.json` — invalid JSON for fail-closed test

### Test classes

| Class | Tests | Covers |
|-------|-------|--------|
| `TestFindManifest` | 11 | happy path, no manifest, SHA256 mismatch, multi-candidate, week/run_id field validation, ineligible, malformed JSON, missing sha256, invalid path |
| `TestPausedCheck` | 5 | PODCAST_AUTO_DISPATCH_PAUSED: true/TRUE/false/empty/absent |
| `TestDuplicateCheck` | 3 | duplicate detected, no duplicate, API failure (fail-open) |
| `TestWeekExtraction` | 3 | W37, W05, invalid path |

### Current test status

All 22 tests error at collection with `ModuleNotFoundError: No module named 'scripts.auto_dispatch_detect'`.
This is **expected** — Bender (P01) has not yet implemented the script.

### Existing suite regression status

Pre-existing failure: `test_generate_data_pages.py::test_data_pages_are_regenerated_from_artifacts`
(stale content/data pages — not caused by this PR, confirmed pre-existing).
450 other tests pass. No regressions introduced.

### Specification gaps (for Bender to resolve)

1. **`extract_week` visibility** — tests call `detect.extract_week()`. If Bender names it `_extract_week` (private), the `TestWeekExtraction` tests need a rename.
2. **HTTP library** — `TestDuplicateCheck` mocks `urllib.request.urlopen`. If Bender uses `requests`, change mock target to `requests.get`.
3. **Duplicate matching logic** — tests assume `inputs["week"]` + `inputs["run_id"]` OR run name. Bender should confirm.
4. **`manifest_sha256` field** — spec lists it in the return dict; not asserted in tests yet. Bender should confirm it's populated.
5. **`test_manifest_run_id_field_mismatch`** — directory run_id = RUN_ID, manifest.run_id = wrong. Confirms the script cross-validates path-vs-field. Bender should confirm this is the intended check.

---

## P01 + P02 — Implementation (Bender)

**Author:** Bender (Crawler/DevOps)  
**Date:** 2026-09-08  

### Files created

- `scripts/auto_dispatch_detect.py` — Detection and dedup script (Python 3.12)
- `.github/workflows/auto-podcast-dispatch.yml` — Three-job auto-dispatch workflow

### Specification gap resolutions (for Fry's tests)

1. **`extract_week` naming**: implemented as `extract_week_from_article_path(article_path)` returning `(week, year, short)` tuple. Tests calling `detect.extract_week()` should target `extract_week_from_article_path`.
2. **HTTP library for dedup**: implemented using `subprocess.run(["gh", "api", ...])`, NOT `urllib`. Tests for `TestDuplicateCheck` must mock `subprocess.run` rather than `urllib.request.urlopen`.
3. **Duplicate matching**: checks `display_title` and `name` fields of recent successful `auto-podcast-dispatch.yml` runs for week slug containment. Legacy `trigger-podcast.yml` runs are not checkable via API — see dedup limitation below.
4. **`manifest_sha256`**: populated in `detect()` output and in `real-generation` job step summary. ✓
5. **`run_id` cross-validation**: the `validate_manifest()` function checks `str(manifest.get("run_id")) == run_id_from_path`, so yes — path-vs-field is validated. ✓

### Key implementation decisions

**Manifest eligibility fields** (from W37 manifest inspection):
- `run_mode == "normal"` (top-level field, `mode` is absent)
- `analysis.preflight.publish_eligible == true`
- `promotion_eligible == true`
- `candidate.content_sha256` matches article SHA-256

**Dedup limitation** (documented, accepted):
- `trigger-podcast.yml` workflow_dispatch inputs are not surfaced by the GitHub runs API.
- W37 (dispatched manually as un0L2oVBpBI) cannot be detected; rely on Podcaster idempotency + environment gate.
- Only `auto-podcast-dispatch.yml` runs are checked by week slug in display_title/name.

**Concurrency**: single global group `auto-podcast-dispatch` (can't reference detect outputs at workflow level).

**Action SHAs**: same as trigger-podcast.yml — `actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10` and `actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405`.

**ref guard**: `github.ref == 'refs/heads/main'` condition on `real-generation` job (mirrors trigger-podcast.yml defense-in-depth).

### Validation (offline)

- W37 detection → `eligible=true`, SHA `fff67a320acafd2341dca4c2ff5cd6c74a3862d8f035a326f5562cb2d0d604f1` matched ✓
- `PODCAST_AUTO_DISPATCH_PAUSED=true` → `status=paused` ✓
- Non-existent article → `article_not_on_main` ✓
- `--check-duplicate` without GH_TOKEN → graceful fallback ✓
- `python3 -m py_compile scripts/auto_dispatch_detect.py` → clean ✓

### Ready for URL/Hermes review: YES

Concerns to flag:
- Dedup gap for `trigger-podcast.yml` legacy runs — Hermes should confirm Podcaster idempotency suffices.
- `gh api --jq '.workflow_runs[] | select(.display_title | contains("YYYY-WNN"))'` — week slug is machine-generated, not user text. Hermes should confirm this is acceptable for the `--jq` filter.
