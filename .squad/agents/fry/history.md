# Fry — History

## Core Context
- Owns pipeline validation across crawling, analysis, and publication.
- Uses test coverage to keep workflow changes honest.

## Learnings
- 2026-06-05T15:36:19.379+00:00: The weekly crawl pipeline needs a terminal data-only no-AI analysis fallback after Copilot and GitHub Models fail, because model-access errors such as `no_access` are real reliability bugs, not transient deploy noise.
- The PaperMod theme in this repo needs Hugo `v0.146.0+`, so build validation must use a sufficiently new Hugo binary.
- End-to-end checks matter more than isolated unit confidence when artifacts move across crawl, analyze, and publish stages.
- Raw crawl output can be publishable with curation, but trend filters still need skepticism about exploit noise and weak momentum data.
- 2026-06-01: Issue #217 came from the analysis stage: Copilot retries could fail the tightened gate with generic week-title output or missing files, so the prompt now injects concrete week/year values, the workflow falls back to GitHub Models after Copilot gate failures, and `scripts/analyze_fallback.py` now works when invoked exactly as CI runs it.
- 2026-06-01: Issue #220 came from the generate stage: `generate_content.py` emits an absolute `page_path`, but the publish-branch commit step treated it as `content/weekly/...`, so the restore `cp` doubled the path and failed. The crawl workflow also had no failure-issue job, so generate/deploy failures were silent unless someone checked Actions manually.

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

## Round 2026-06-01T15:40

### Issue #38: Anticipatory Tests
- Branch `squad/38-hindsight-tests` pushed
- Generated comprehensive test suite for hindsight validation
- Covers prediction registration, scorecard generation, metrics output
- Ready for integration with Farnsworth implementation

## Round 1 (2026-06-05)

- Triaged issues #232, #230, #188
- PR #235: quality-gate fallback hardening (Copilot → GitHub Models path)
- Decision: data-only fallback when all AI sources fail
- Reusable skill: notify-failure job for pipeline failure visibility
- Outcomes: #232 has PR ready, #230 closed as stale, #188 rerouted to Leela

## PR #236 QA (2026-06-05)

- Config-driven RSS expansion should be verified at the stage boundary: crawler output shape, correlation input resolution, press-context fallback, and rebuild hydration all need coverage.
- Bounded in-process RSS fan-out is acceptable for the current five-source enrichment set when full tests and a live smoke confirm stable artifact production.

## Round 2 (2026-06-05)

- QA review of PR #236 RSS enrichment feature complete
- 554 unit tests passed
- Live 5-source RSS smoke test: 54 articles, 5 sources, no feed errors
- QA verdict: **approve** (no follow-up QA work required)
- Formal approval blocked by GitHub own-PR rules (self-authored by Fry PR author)
- Posted QA rationale to PR #236
- Awaiting security review (Hermes) and lead approval (Leela) before merge

## PR #235 Copilot review follow-up (2026-06-05)

- Copilot fallback warnings should describe the observed pipeline state, not just retry exhaustion: the same branch can mean 0 Copilot attempts because the CLI is unavailable or failed attempts that never yielded a publishable summary.
