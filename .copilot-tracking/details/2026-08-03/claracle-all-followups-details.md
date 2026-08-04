<!-- markdownlint-disable-file -->
# Implementation Details: Claracle All Follow-Ups

## Context

* Plan: `.copilot-tracking/plans/2026-08-03/claracle-all-followups-plan.instructions.md`
* Research: `.copilot-tracking/research/2026-08-03/claracle-all-followups-research.md`

## Phase Boundaries

Phase 1 owns atomic proof scripts, tests, and its manual workflow. Phase 2 owns
Podcaster workflows, handoff outputs, workflow-contract tests, and operator docs.
Phase 3 owns build-cost tooling, tests, and workflow. Phase 4 owns frontend,
compressed serving, Lighthouse runner, visual tests, and quality documentation.
Phase 5 updates only acceptance handoffs after executable evidence exists.

## Validation Strategy

Each phase runs its focused test before another edit enters the same slice. Workflow
changes require Zizmor and Checkov. Python changes require Ruff and focused pytest.
Frontend changes require existing Node fixtures and CI-rendered browser/Lighthouse
validation when local Chromium or Hugo is unavailable.

## Safety

All proof and experiment workflows use `contents: read`, no secrets, no persisted
credentials, and no remote writes. The Podcaster real workflow is not dispatched.
Both rollout flags remain false throughout implementation.