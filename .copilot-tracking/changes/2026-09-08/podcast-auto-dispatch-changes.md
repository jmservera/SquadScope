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
