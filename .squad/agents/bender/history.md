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
- External RSS crawlers must validate config URLs against an HTTPS host allowlist and fetch through explicit per-request timeouts; config-driven source lists are not a security boundary by themselves (PR #236).
