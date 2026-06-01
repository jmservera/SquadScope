# Fry — History

## Core Context
- Owns pipeline validation across crawling, analysis, and publication.
- Uses test coverage to keep workflow changes honest.

## Learnings
- The PaperMod theme in this repo needs Hugo `v0.146.0+`, so build validation must use a sufficiently new Hugo binary.
- End-to-end checks matter more than isolated unit confidence when artifacts move across crawl, analyze, and publish stages.
- Raw crawl output can be publishable with curation, but trend filters still need skepticism about exploit noise and weak momentum data.
- 2026-06-01: Issue #217 came from the analysis stage: Copilot retries could fail the tightened gate with generic week-title output or missing files, so the prompt now injects concrete week/year values, the workflow falls back to GitHub Models after Copilot gate failures, and `scripts/analyze_fallback.py` now works when invoked exactly as CI runs it.

## Round 2026-06-01T12:19

### Issue #217: Quality Gates
- PR #218 opened with all tests passing
- Fallback mechanism now includes GitHub Models support
- Copilot prompt validation hardened

## Round 2026-06-01T12:41

### PR #218 Merged
- Review comment resolved: removed outer quotes from YAML title hint
- Added regression test
- 542 tests passing
- Commit 9d15b18
- Merged (squash)
- Issue #217 closed
