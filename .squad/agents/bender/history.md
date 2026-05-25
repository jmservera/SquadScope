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
