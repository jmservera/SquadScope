# Leela — History

## Core Context
- Owns architecture decisions, review gates, and cross-team coordination.
- Keeps interface contracts stable enough for specialists to work independently.

## Learnings
- 2026-06-05T15:36:19.379+00:00 issue #234: for small RSS enrichment sets in the weekly crawl, prefer a config-driven source list plus bounded in-process parallel fetches over separate Actions jobs; runner setup/artifact overhead outweighs per-feed job parallelism.
- Branch protection must never be bypassed; automated write paths should follow the shared `branch-protection-pr-workflow` skill instead.
- The learning loop only works when agent identity is loaded before execution, outcomes are persisted after execution, and that state is injected into the next run.
- Copilot CLI agent selection uses the registered agent name, not the path to the agent file.
- Documentation and orchestration updates should land in the permanent record quickly so the rest of the squad sees the current operating model.
- Cleanup pattern: distinguish team-member agent directories (`agents/{squad-member}/`) from orphaned agent definitions (`.github/agents/*.agent.md`). Archive before deleting if historical value is uncertain; delete confidently once verified dead (unused in workflows).
- 2026-06-01 review note: PR #218 looked structurally sound and its targeted analysis tests passed locally after dependency setup; the fix closes prompt placeholder leakage and restores the GitHub Models fallback path.
- 2026-06-01 review note: PR #219 stayed within presentation scope and diff-check was clean, but local Hugo validation remained blocked by the repo's existing toolchain baseline rather than the PR itself.
- 2026-06-01 governance note: GitHub will not let this account approve its own PRs, so branches opened as `jmservera` still need an independent reviewer before Leela can treat approval gating as satisfied.
- 2026-06-05T15:36:19.379+00:00 growth governance note: time-boxed distribution work needs repository artifacts, metrics files, or linked platform evidence before acceptance is considered verifiable; do not reconstruct stale social copy after the posting window just to satisfy checked boxes.
- 2026-06-05 PR #235 review note: a terminal no-AI publishing fallback is acceptable when it is deterministic, explicitly attributed (`source=no-ai`, `model=none`), and still passes the same analysis quality gate; self-approval remains blocked for `jmservera`-authored PRs.
- 2026-06-05 crawler topology note: keep GitHub repo crawl monolithic/cached and RSS in-process until measured triggers justify matrix isolation; improve source-aware press correlation/rendering rather than creating a new compact press artifact path.

## Round 1 (2026-06-05)

- Implemented issue #234: config-driven RSS sources + bounded parallel fetching
- PR #236: 554 tests pass, 5-feed live smoke crawl green, CodeQL clean
- Updated docs/decision (source-selection methodology, BaseURL strategy)
- Updated docs/history with architecture notes
- Issue #188 assigned for round 2 (missing-artifact findings from Fry)

## Round 2 (2026-06-05)

- PR #235 code review: approved in substance (terminal no-AI publishing fallback)
- Formal approval blocked by GitHub own-PR rules (self-authored `jmservera` PR)
- Posted lead review comment to PR #235
- Awaiting independent reviewer approval before merge
- Note: self-approval remains impossible for `jmservera`-authored PRs regardless of review gate satisfaction

## Round 3 (2026-06-05T16:26:00Z)

- Crawler improvement analysis completed: squad findings synthesized into GitHub issue #237
- Issue title: "Improve multi-source crawler telemetry and source-aware press correlation"
- Lead decision: keep GitHub crawl monolithic, keep RSS in-process bounded parallelism, defer matrix fan-out to triggered conditions (RSS p95 > 60s, source count > 10, per-source retry/quota needed)
- Scope: per-source metrics, schema versioning, deterministic merge before analysis, cross-source dedupe, press-context bounds and telemetry, tests for partial failures/fallback/reproducibility
- Non-goals: LLM staged analysis, GitHub raw compaction, matrix unless triggered, core GitHub crawler changes
- Routing: Bender (implementation), Fry (reliability gates), Farnsworth (press-context quality)
- Labels: `squad`, `squad:leela`, `squad:bender`, `go:yes`
- Decisions recorded in .squad/decisions.md under four entries (Bender, Farnsworth, Fry, Leela)
- 2026-06-05T17:42:56.819+00:00 matrix/map-reduce PRD note: treat crawl matrix and analysis decomposition as separate decisions; keep crawl fan-out measurement-gated, while map/reduce is a citation-preserving LLM context/quality experiment with mapper claim ledgers and reducer-owned editorial coherence.
