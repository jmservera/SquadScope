# Bender — History

## Core Context
- Owns crawl automation, raw data capture, and CI wiring for upstream collection.
- Produces structured artifacts for analysis rather than editorial output.

## Learnings
- Weekly crawl output should preserve both newly discovered repos and momentum candidates so downstream stages can reason about freshness and star gains.
- Star-gain estimates depend on comparing current search results against the most recent prior snapshot, so snapshot compatibility matters as much as the live crawl.
- Rate-limited integrations should follow the shared `exponential-backoff-with-jitter` skill instead of open-coding retry behavior.
- Analysis execution should prefer Copilot CLI first, then fall back to GitHub Models using the same rendered prompt so output contracts stay aligned.
- Reviewer gates should validate the analyzer contract, not just artifact existence.
- New pipeline stages should follow the `ci-data-source-integration-pattern` skill: wire the script into CI immediately, document the handoff, and test the producer/consumer schema at the boundary.
- Hugo's `ignoreFiles` config is overridden by explicit `[module.mounts]` declarations; use `excludeFiles` on the mount definition to exclude files from mounted directories (W21 rescue, PR #167).
- GitHub Actions schedule events do not have an `inputs` object; use `!inputs.X` instead of `github.event.inputs.X == ''` to safely check optional manual inputs without breaking cron triggers (critical fix, PR #164).
- Deploy pipeline should hydrate previous-week content/data from publish branch before Hugo build to prevent main/publish divergence and preserve existing data integrity (PR #164, W21 rescue architectural fix).
- Fork-safe deploy secrets should default to empty in Hugo config and be injected via `HUGO_PARAMS_*` environment overrides so forks render safe defaults without inherited maintainer secrets (GA4 PR #182/#191).

## Round 1 (2026-06-05)

- Resolved Copilot review thread PRRT_kwDOSgq4hM6HaRkn on PR #236
- Updated docs command to `python3 -m scripts.techcrunch_crawler ...`
- Validated command in clean venv: `python3 -m scripts.techcrunch_crawler --help` successful
- commit ba2787e pushed; thread resolved
- PR #236 awaiting post-commit CodeQL

- Comparing W23 crawler runs showed five in-process external RSS feeds added about 1s while the GitHub repo crawl remained the dominant 4m47s–5m58s step; keep RSS bounded in-process until source count/runtime justifies a matrix.

## 2026-06-05 Crawler parallelism analysis

- Analyzed old run (26753498571) vs. new run (27026348186) to assess topology options.
- Key finding: GitHub repo crawl is bottleneck (~5m58s old, ~4m47s new); RSS parallelism not a factor (~1s).
- Topology options: A (bounded in-process), B (matrix per-source), C (hybrid staged).
- Recommendation: Use Option C — keep in-process now, add per-source logs and schema versioning, add validation/merge step before analysis, defer matrix to when RSS p95 > 60s or source count > 10.
- Acceptance criteria documented: per-source logs, schema_version, sources_requested/succeeded/failed, deterministic merge.
- Decision recorded in .squad/decisions.md; GitHub issue #237 created for implementation.
- External RSS crawlers must validate config URLs against an HTTPS host allowlist and fetch through explicit per-request timeouts; config-driven source lists are not a security boundary by themselves (PR #236).
- Local validation docs for scripts importing `scripts.*` modules should use `python3 -m ...` or set `PYTHONPATH=.` so repo-root imports resolve reliably (PR #236).

## Issue #237 canonical external-news telemetry (2026-06-05)

- Multi-source RSS remains in-process, but downstream reliability depends on a versioned canonical artifact: include crawl window, source config checksum, per-source statuses, partial failures, dedupe count, and deterministic checksum in `*-external-news.json`.
- Press correlation must retain bounded source-aware citations and label category/fuzzy-only matches as weak so mirrored coverage or broad topics do not inflate strong press claims.
- PR #242 review follow-up: failed RSS fetch exceptions must stamp source-level attempt/timeout telemetry before re-raising, and scheduled external-news crawls should pass both `--since` and `--until` so canonical crawl windows are reproducible.

## 2026-06-05 Matrix crawl PRD input

- Current observed run 27030646485 confirmed the pattern from issue #237: crawl job ~4m50s, GitHub `Run crawler` ~4m30s, external RSS/news ~1s.
- Matrixing RSS is an isolation feature at current scale, not a speed feature; matrixing GitHub needs a shard experiment because search quota and secondary limits are shared across jobs.
- Recommended PRD path is hybrid staged fan-out/fan-in: establish validated artifact contracts first, then gate RSS matrix, GitHub query matrix, and analysis map/reduce on measured thresholds.
- Run 27030646485 also showed analysis, not crawling, is the critical-path risk: three Copilot attempts consumed ~28m41s, failed quality gates, GitHub Models had no `openai/gpt-4o` access, and the workflow shipped via no-AI fallback with ~112.9k estimated input tokens.
- Issue #249 implementation: weekly analysis now writes to `data/candidates/<week>/<run_id>/` first and emits a `publish_eligibility_v1` manifest before any `data/analyzed/<week>-summary.md` promotion; promotion must fail closed on no-AI, stale source evidence, missing checksums, or failed validation.
- Analysis preflight now emits raw and prompt-visible repository evidence inventories with byte/token/checksum metadata; analysis gate rejects final repo links outside current raw evidence when inventory is available.
