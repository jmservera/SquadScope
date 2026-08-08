---
applyTo: '.copilot-tracking/changes/2026-08-03/claracle-all-followups-changes.md'
---
<!-- markdownlint-disable-file -->
# Implementation Plan: Claracle All Follow-Ups

> **STATUS — DONE / CLOSED 2026-08-08.** All items delivered. Retired per [BRD-CLARACLE-003](../../../docs/brds/claracle-post-relaunch-consolidation-brd.md).

## User Requests

* Continue all five suggested work items from the external acceptance review
* Complete executable work while preserving human and protected-environment boundaries

## Implementation Checklist

### [x] Phase 1: Add Isolated Atomic Publish Proof

<!-- parallelizable: true -->

* [x] Add a temporary-local-remote proof harness for normal, rerun, failure, tree, and hydration scenarios
* [x] Add focused unit and integration tests
* [x] Add a manual read-only artifact workflow
* [x] Retain local proof output without mutating `origin/publish`

### [x] Phase 2: Protect Real Podcaster Generation

<!-- parallelizable: false -->

* [x] Require an exact publish run and bind manual real generation to `podcaster-real-generation`
* [x] Require merged article identity and retain safe response outputs
* [x] Remove automatic real generation from publish sync
* [x] Update workflow contracts and operator documentation

### [x] Phase 3: Add Report-Only Cost Experiment

<!-- parallelizable: true -->

* [x] Add isolated workload materialization and aggregation tooling
* [x] Add a manual read-only experiment workflow with immutable reviewed SHAs
* [x] Add focused schema, statistics, isolation, and workflow tests
* [x] Keep thresholds null and rollout flags disabled

### [x] Phase 4: Resolve UX and Lighthouse Hardening

<!-- parallelizable: true -->

* [x] Replace the clipping Star Velocity scale and clarify visual semantics
* [x] Add mobile consent geometry coverage
* [x] Extend lean CSS bundles to search, about, methodology, and privacy
* [x] Add Brotli negotiation and response tests
* [x] Document current Lighthouse methodology and target font-swap CLS
* [x] Add bounded per-page Lighthouse concurrency without changing thresholds
* [x] Record topic aggregation as correct and retain publish-backfill as owner-controlled

### [x] Phase 5: Prepare Human Acceptance Handoffs

<!-- parallelizable: false -->

* [x] Link exact current evidence to security, accessibility, analytics, visual, and metadata actions
* [x] Record GitHub environment administration prerequisites
* [x] Preserve every pending human disposition

### [x] Phase 6: Validate and Review

<!-- parallelizable: false -->

* [x] Run focused tests after each implementation slice
* [x] Run full pytest, Ruff, workflow security scans, Hugo/build checks where available, and diff validation
* [x] Confirm no workflow was dispatched and both rollout flags remain disabled
* [x] Review all user requests and compile remaining authority-bound work

## Dependencies

* `.copilot-tracking/research/2026-08-03/claracle-all-followups-research.md`
* Four subagent research artifacts under `.copilot-tracking/research/subagents/2026-08-03/`
* Hugo Extended 0.161.1 and Pagefind 1.5.2 in CI
* GitHub environment administration for real Podcaster execution
* Hermes, URL, Fry, Amy, Podcaster maintainer, and sponsor authority

## Success Criteria

* All repository-executable follow-up work is implemented and validated.
* Atomic evidence uses only a temporary local remote.
* Real Podcaster generation cannot occur automatically and requires exact protected manual admission.
* Cost evidence remains report-only and non-blocking.
* UX and Lighthouse thresholds are not weakened.
* Human and sponsor decisions remain explicit and unforgeable by automation.