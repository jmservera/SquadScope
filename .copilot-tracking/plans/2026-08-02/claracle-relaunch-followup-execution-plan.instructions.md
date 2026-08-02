---
applyTo: '.copilot-tracking/changes/2026-08-02/claracle-relaunch-followup-execution-changes.md'
---
<!-- markdownlint-disable-file -->
# Implementation Plan: Claracle Relaunch Follow-Up Execution

## User Requests

* Publish review corrections: commit, push, and resolve PR threads
* Complete GA4/GSC setup
* Close security, accessibility, Podcaster, visual, and sponsor acceptance gates
* Plan repository-page, dynamic-topic, and generation-cost work

## Context Summary

Research shows that the repository implementation is ahead of the acceptance record. The remaining work mixes executable repository evidence with actions that require Google credentials, protected environment policy, downstream authorization, assistive technology, security review, visual review, and sponsor authority.

## Implementation Checklist

### [x] Phase 1: Publish Review Corrections

<!-- parallelizable: false -->

* [x] Commit the issue-state correction and RPI logs as `8fddceb`
* [x] Push the active PR branch
* [x] Resolve both addressed PR #647 review threads

### [ ] Phase 2: Reconcile GA4/GSC Evidence

<!-- parallelizable: true -->

* [x] Verify production GA configuration presence, GSC metadata absence, sitemap response, and secret names without exposing values
* [x] Correct the baseline and status of record to distinguish deployed wiring from external acceptance
* [x] Clarify that production GA configuration is injected through an Actions secret
* [x] Complete Google property verification, sitemap submission, Realtime confirmation, and product link (owner-confirmed by jmservera on 2026-08-02)
* [ ] Transcribe the supplied GSC performance export and retain production consent observations

### [x] Phase 3: Refresh Acceptance Evidence

<!-- parallelizable: true -->

* [x] Reconcile the security review with current SEC-01 and SEC-04 implementation evidence without granting sign-off
* [x] Record current CI, environment, Podcaster, accessibility, and visual evidence boundaries
* [x] Correct #622 to non-blocking polish and keep #626 as independent quality hardening
* [x] Provide owner-ready records for manual accessibility, protected Podcaster, visual, security, and sponsor decisions

### [x] Phase 4: Plan Gated Rollouts and Cost Measurement

<!-- parallelizable: true -->

* [x] Plan a report-only workload-variant experiment for Q-01/NFR-009
* [x] Plan repository-page activation with identity, lifecycle, diff, and rollback gates
* [x] Plan one reviewed dynamic-topic canary with explicit deferrals
* [x] Keep both production rollout flags disabled pending approval

### [x] Phase 5: Validate and Review

<!-- parallelizable: false -->

* [x] Run focused and full executable validation and inspect PR checks
* [x] Record completed work, owner-gated blockers, and final review disposition

## Dependencies

* Research documents under .copilot-tracking/research/2026-08-02/ and .copilot-tracking/research/subagents/2026-08-02/
* GitHub repository and Actions metadata access
* Google account access for FR-035 external acceptance
* Podcaster maintainer authorization and protected environment policy
* Hermes, URL, Amy, Fry, and jmservera review authority

## Success Criteria

* Review corrections are published and review threads resolved.
* Repository records accurately separate the completed GA4/GSC connection from pending baseline and production consent evidence.
* Every acceptance gate has current evidence, a concrete owner action, and no unsupported completion claim.
* Rollout and cost work is implementation-ready while both flags remain disabled.
