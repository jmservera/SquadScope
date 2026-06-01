# Farnsworth hindsight validation decision

Date: 2026-06-01

## Decision
Use an optional `predictions` frontmatter registry on weekly analysis summaries with entries shaped as `{repo, direction, confidence}`.

## Why
The published markdown is already the durable editorial artifact, so embedding prediction intent there avoids a separate ledger drifting out of sync. Legacy summaries still need heuristic extraction from Signal/Noise/Gaps prose, but future summaries should register explicit repo-level calls for cleaner hindsight scoring.

## Operational note
The validator writes a human scorecard to `.squad/reskill/scorecards/YYYY-WNN.md` and a machine-readable companion to `data/metrics/scorecards/YYYY-WNN-scorecard.json` so the current reskill tooling can ingest the same run.
