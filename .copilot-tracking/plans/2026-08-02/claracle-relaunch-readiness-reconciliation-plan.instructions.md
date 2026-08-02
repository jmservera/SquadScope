---
applyTo: '.copilot-tracking/changes/2026-08-02/claracle-relaunch-readiness-reconciliation-changes.md'
---
<!-- markdownlint-disable-file -->
# Implementation Plan: Claracle Relaunch Readiness Reconciliation

## Overview

Triage the live deploy failure, reconcile the three relaunch plans and the PRD/BRD with the delivered repository state, and produce a single sequenced launch-gate register so the relaunch decision is grounded in accurate, current evidence.

## Objectives

### User Requirements

* Review the plans, PRD, and BRD and address what is missing - Source: user request, 2026-08-02
* Produce implementation-ready planning artifacts from the gap analysis - Source: task-plan prompt, 2026-08-02

### Derived Objectives

* Resolve the live deploy failure before reconciling status so the record reflects a green pipeline - Derived from: open issue #644
* Bring the three overlapping plan checklists to the true delivered state and collapse them into one status-of-record - Derived from: stale checkboxes across the 2026-07-29/30/31 plans
* Make the PRD and BRD internally consistent and current with the #627-#646 workstream - Derived from: BRD version drift and PRD changelog lag
* Consolidate the remaining launch gates into one owner/evidence register rather than leaving them scattered - Derived from: pending NFR-004/005/007, Podcaster run, visuals, and sponsor approval

## Context Summary

### Project Files

* docs/prds/claracle-data-observatory-relaunch.md - PRD v1.2; changelog, NFRs, rollout flags, open questions
* docs/brds/claracle-data-observatory-relaunch-brd.md - BRD v1.1 with v1.0 cross-references (drift)
* .copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md - Phases 7-10 partial
* .copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md - Phases 6-8 open
* .copilot-tracking/plans/2026-07-31/claracle-deploy-hydration-remediation-plan.instructions.md - Phases 2-5 open; Phase 4 shipped but unmarked
* config/observatory.toml - repo_pages flag disabled (confirmed)
* hugo.toml - fork-safe GA4/GSC defaults are empty; production configuration and platform acceptance require separate evidence
* docs/review/data-observatory-relaunch/ - bounded acceptance evidence and pending gates

### References

* .copilot-tracking/research/2026-08-02/claracle-relaunch-readiness-reconciliation-research.md - gap analysis and verified findings
* Issue #644 - live deploy failure (run 30718600607)
* Issue #599 - Connect GA4 + Google Search Console (FR-035)
* Issue #594 - Epic: Claracle Data Observatory Relaunch

### Standards References

* .github/copilot-instructions.md - testing, workflow security, cross-repository conventions
* .github/instructions/hve-core/markdown.instructions.md - Markdown requirements
* .github/instructions/hve-core/writing-style.instructions.md - documentation voice and style

## Implementation Checklist

### [x] Implementation Phase 1: Triage the Live Deploy Failure (#644)

<!-- parallelizable: false -->

* [x] Step 1.1: Diagnose deploy run 30718600607 and classify the failure — dangling `source_manifest.path` (`data/candidates/2026-W31/30669054860/publish-manifest.json`) broke the Podcaster smoke gate (class b/dangling reference)
  * Details: .copilot-tracking/details/2026-08-02/claracle-relaunch-readiness-reconciliation-details.md (Lines 12-30)
* [x] Step 1.2: Apply or plan the fix and confirm a green deploy — resolved by already-merged `#645`/`#646`; deploy-site green since 2026-08-01 (runs 30720064394, 30721575540)
  * Details: .copilot-tracking/details/2026-08-02/claracle-relaunch-readiness-reconciliation-details.md (Lines 31-43)
* [x] Step 1.3: Close #644 with the root-cause note — #644 already CLOSED (COMPLETED)

### [x] Implementation Phase 2: Reconcile Plan Checklists to Delivered State

<!-- parallelizable: true -->

* [x] Step 2.1: Update the 2026-07-31 deploy-hydration plan checkboxes to match shipped PRs (#628/#632/#634/#637/#641)
  * Details: .copilot-tracking/details/2026-08-02/claracle-relaunch-readiness-reconciliation-details.md (Lines 55-67)
* [x] Step 2.2: Update the 2026-07-29 and 2026-07-30 plan checkboxes for completed Podcaster/smoke/restore work (#639/#643/#640/#646)
  * Details: .copilot-tracking/details/2026-08-02/claracle-relaunch-readiness-reconciliation-details.md (Lines 68-81)
* [x] Step 2.3: Create one status-of-record reconciling delivered vs pending across all three plans, including the final dispositions of epic issues #644/#626/#622/#599/#594 — docs/review/data-observatory-relaunch/status-of-record.md
  * Details: .copilot-tracking/details/2026-08-02/claracle-relaunch-readiness-reconciliation-details.md (Lines 82-94)

### [x] Implementation Phase 3: Reconcile Product Documents

<!-- parallelizable: true -->

* [x] Step 3.1: Fix BRD version drift (Document Control vs Acceptance/PRD v1.0 references) — BRD bumped to v1.2 with a Change History; PRD cross-reference aligned to v1.2
  * Details: .copilot-tracking/details/2026-08-02/claracle-relaunch-readiness-reconciliation-details.md (Lines 99-112)
* [x] Step 3.2: Add PRD v1.3 changelog + restore-consistency behavior for the #627-#646 workstream, and record the FR-041 link-check partial status (test-level only, no CI link tool)
  * Details: .copilot-tracking/details/2026-08-02/claracle-relaunch-readiness-reconciliation-details.md (Lines 113-125)
* [x] Step 3.3: Add a sponsor-approval + launch-gate register with owners and evidence links — register in the status-of-record, linked from PRD Acceptance Status, section 13, and REF-10
  * Details: .copilot-tracking/details/2026-08-02/claracle-relaunch-readiness-reconciliation-details.md (Lines 126-139)

### [x] Implementation Phase 4: Sequence Remaining Launch Gates

<!-- parallelizable: false -->

* [x] Step 4.1: Consolidate pending gates (GA4/GSC baseline and consent, external metadata and feed validation, NFR-004 security, NFR-005 a11y, Podcaster run, visuals, Q-01 cost) plus epic issues #626 (Lighthouse) and #622 (UX polish) into the register with owner, dependency, and evidence path — status-of-record launch-gate register
  * Details: .copilot-tracking/details/2026-08-02/claracle-relaunch-readiness-reconciliation-details.md (Lines 144-164)
* [x] Step 4.2: Record deferred scope requiring its own plan (GA4/GSC baseline and consent evidence, repo_pages rollout, dynamic topic rollout, cost spike) — planning log Suggested Follow-On Work (WI-01/03/04/05)
  * Details: .copilot-tracking/details/2026-08-02/claracle-relaunch-readiness-reconciliation-details.md (Lines 165-181)

### [x] Implementation Phase 5: Validation and Re-Review

<!-- parallelizable: false -->

* [x] Step 5.1: Validate all edited docs (markdown lint, internal link/reference integrity, changelog/version consistency) — `test_internal_link_checker`/`test_embed_sources` green; referenced files verified; no stale version strings
  * Details: .copilot-tracking/details/2026-08-02/claracle-relaunch-readiness-reconciliation-details.md (Lines 182-192)
* [x] Step 5.2: Fix minor validation issues — none required
* [x] Step 5.3: Report blocking issues and hand off deferred plans — no blockers; #644 resolved; deferred plans in the log (WI-01/03/04/05)

## Planning Log

See .copilot-tracking/plans/logs/2026-08-02/claracle-relaunch-readiness-reconciliation-log.md for discrepancy tracking, implementation paths considered, and suggested follow-on work.

## Dependencies

* gh CLI access for #644 diagnosis and issue updates
* Repository write access for docs/ and .copilot-tracking/ edits
* Markdown lint tooling per .mega-linter.yml
* Sponsor (jmservera) input for the approval artifact and gate ownership

## Success Criteria

* Issue #644 is diagnosed and either fixed with a green deploy or handed off with a scoped fix plan - Traces to: open issue #644
* All three relaunch plans reflect true delivered state and a single status-of-record exists - Traces to: stale checkbox findings
* PRD and BRD are internally consistent, version-correct, and current through the #627-#646 workstream - Traces to: BRD version drift and PRD changelog lag
* A single launch-gate register lists every pending gate with owner, dependency, and evidence path - Traces to: pending NFR-004/005/007, Podcaster, visuals, sponsor approval
* Deferred implementation workstreams are captured for separate planning - Traces to: #599, repo_pages/dynamic rollout, Q-01
