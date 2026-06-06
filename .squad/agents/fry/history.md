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

## PR #235 Copilot review resolution (2026-06-05)

- Resolved Copilot review thread PRRT_kwDOSgq4hM6HaPhr
- Updated fallback warning: "No publishable Copilot summary was produced; falling back to GitHub Models API."
- Added pipeline test assertion to prevent regression
- 9 tests passing
- commit 7409b05 pushed; thread resolved


## Crawler reliability analysis (2026-06-05)

- Multi-source RSS is not yet the crawl bottleneck; GitHub API crawl still dominates wall time, while five external RSS sources completed in about one second after dependency setup.
- Next reliability iteration should keep GitHub crawl/cache as one core job and matrix only optional external news sources, merging per-source artifacts before analysis for isolation, retry granularity, and reproducible handoff.

## Crawler reliability architecture assessment (2026-06-05T16:26:00Z)

- Reviewed old (26753498571) vs. new (27026348186) crawl jobs; GitHub repo crawl is the actual bottleneck (~4m47s–5m58s).
- In-process model is operationally simple/fast but offers poor per-source failure isolation; retry requires full crawl rerun.
- Recommendation: hybrid staged topology — keep GitHub crawl monolithic; add matrix for external RSS with fail-fast: false, per-source artifacts, and deterministic merge before analysis.
- Acceptance criteria: shared crawl context (week, since, until, source config), per-source artifacts (success or error JSON), merge job on `if: always()`, explicit optional-source degradation, backward-compatible rebuild mode.
- Tests to add: merge helper validation (schema, dedupe, sorting, error handling), per-source failure handling, fallback paths, reproducibility gates, citation preservation.
- Metrics: per-source (name, host, duration, article counts, errors) and aggregate (source_count, failed_source_count, total articles, artifact size).
- Decision recorded in .squad/decisions.md.

## Issue #238 notify triage (2026-06-05)

- Run 27026348186 completed crawl, analyze, generate, and deploy successfully; only `notify` failed.
- Root cause: `gh release create week-2026-W23` is not idempotent when the weekly release tag already exists, so rerunning/publishing the same week produced HTTP 422 `Release.tag_name already exists`.
- QA fix: make notify update an existing weekly release with `gh release edit` instead of failing, while preserving release creation for new weeks.

## Matrix + map/reduce PRD QA input (2026-06-05T18:15:23Z)

- Matrix crawl should be gated by deterministic shared run context, per-leg artifacts, fan-in checksums, optional-vs-required failure policy, and explicit rate-limit budgets; GitHub search fan-out is riskier than RSS fan-out because search quota is already the tight limit.
- Map/reduce analysis is promising for context reduction only if mapper outputs are schema-validated, reducer output preserves citations and contradictions, and the final markdown still passes the existing analysis gate with current fallback paths retained.

## Analysis decomposition QA recommendation (2026-06-05T20:57:09Z)

- Signal-type hierarchical map/reduce is the lowest-risk analysis decomposition MVP because it matches current raw payload boundaries, is fixture-testable, and can run sidecar-first without overwriting the existing Copilot -> GitHub Models -> no-AI publish path.
- Map/reduce must not become publishable until mapper/reducer schemas, citation bindings, rejected-claim/contradiction sidecars, final `analysis_gate.py` compliance, fallback preservation, and A/B quality metrics pass.

## Issue #257 overwrite-protection test groundwork (2026-06-05T21:16:49Z)

- Added deterministic no-network regression coverage around publish eligibility manifests and promotion guard behavior.
- Good canonical weekly summary/content must remain unchanged when candidates are failed, degraded, no-AI, stale, missing-manifest, or malformed-manifest.
- Safe rerun promotion is copy-stable and must not append or duplicate article body content; ineligible candidates should remain in staging with promotion diagnostics for debugging.
