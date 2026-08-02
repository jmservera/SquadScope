<!-- markdownlint-disable-file -->
# Implementation Details: Claracle Relaunch Readiness Reconciliation

## Context Reference

Sources: .copilot-tracking/research/2026-08-02/claracle-relaunch-readiness-reconciliation-research.md; conversation gap analysis (2026-08-02); repository inspection.

## Implementation Phase 1: Triage the Live Deploy Failure (#644)

<!-- parallelizable: false -->

### Step 1.1: Diagnose deploy run 30718600607 and classify the failure

Pull the failed step logs and classify: is it (a) the 2026-W31 restore interacting with the just-merged #646 preservation, (b) a dangling embed/source_page (the #627 class), (c) a publish/main hydration divergence, or (d) unrelated content.

Commands:
* `gh run view 30718600607 --log-failed | grep -iE "error|fail|does not exist|errorf|source_page|not found" | head -40`
* `gh issue view 644 --json body,createdAt`
* Compare timing against the restore run and #646 merge.

Files:
* .github/workflows/deploy-site.yml - hydration list
* layouts/embeds/single.html, layouts/shortcodes/observatory-chart.html - errorf sources

Success criteria:
* Root cause identified and classified against the known failure classes.

Dependencies:
* gh CLI access.

### Step 1.2: Apply or plan the fix and confirm a green deploy

If the fix is minor and reversible (e.g., a missing embed source_page, a hydration path), apply it via a PR to main. If it requires a larger change (e.g., restore-fix interaction), scope a dedicated fix plan instead of inline changes.

Files:
* .github/workflows/deploy-site.yml or content/embeds/* or content/data/* depending on cause

Success criteria:
* A deploy run completes successfully, or a scoped fix plan is handed off.

Dependencies:
* Step 1.1 classification.

### Step 1.3: Close #644 with the root-cause note

Comment the root cause and resolution on #644 and close it once the deploy is green.

Success criteria:
* #644 closed with a documented root cause, or explicitly kept open with a linked fix plan.

## Implementation Phase 2: Reconcile Plan Checklists to Delivered State

<!-- parallelizable: true -->

### Step 2.1: Update the 2026-07-31 deploy-hydration plan checkboxes to match shipped PRs

Mark Phase 3 (deploy hydration restored via #637) and Phase 4 Step 1 (embed source_page guard shipped as check_embed_sources.py in #641) complete; annotate Phase 5 with #627 closed. Keep genuinely open items unchecked.

Files:
* .copilot-tracking/plans/2026-07-31/claracle-deploy-hydration-remediation-plan.instructions.md

Success criteria:
* Checkboxes match the merged PRs (#628/#632/#634/#637/#641) with PR references.

Dependencies:
* None (documentation only).

### Step 2.2: Update the 2026-07-29 and 2026-07-30 plan checkboxes for completed work

Reflect Podcaster smoke reusability + release evidence (#636/#639/#643), and restore-consistency (#640/#646) against the relevant phases (2026-07-29 Phase 8; 2026-07-30 Phases 6-8 where satisfied). Do not mark human/external gates that remain pending.

Files:
* .copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md
* .copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md

Success criteria:
* Only items with merged evidence are checked; each carries a PR/issue reference.

Dependencies:
* None.

### Step 2.3: Create one status-of-record reconciling delivered vs pending

Author a single status-of-record (under docs/review/data-observatory-relaunch/ or .copilot-tracking) that maps every relaunch requirement/phase to Done/Pending with evidence, superseding the fragmented view across three plans and covering the final dispositions of epic issues #644/#626/#622/#599/#594.

Files:
* docs/review/data-observatory-relaunch/status-of-record.md (new) or an agreed location

Success criteria:
* A reader can determine relaunch readiness from one document.

Dependencies:
* Steps 2.1-2.2.

## Implementation Phase 3: Reconcile Product Documents

<!-- parallelizable: true -->

### Step 3.1: Fix BRD version drift

Reconcile the BRD Document Control version (v1.1) with the Acceptance section and the PRD REF-1 reference (both cite v1.0). Choose the authoritative version, update cross-references, and add a BRD changelog row if missing.

Files:
* docs/brds/claracle-data-observatory-relaunch-brd.md
* docs/prds/claracle-data-observatory-relaunch.md (REF-1)

Success criteria:
* BRD version and all cross-references agree.

Dependencies:
* None.

### Step 3.2: Add PRD v1.3 changelog + restore-consistency behavior

Add a v1.3 changelog entry covering #627-#646 (deploy/hydration cascade, Podcaster smoke hardening, restore-consistency). Extend NFR-002 or add a new NFR capturing that restore preserves the published weekly transaction (article, summary, promotion record, rollups) and does not corrupt provenance.

Files:
* docs/prds/claracle-data-observatory-relaunch.md (sections 7, 15)

Success criteria:
* PRD reflects the delivered restore/Podcaster behavior with a dated changelog row, and FR-041's partial status (test-level link check only, no CI link tool) is recorded.

Dependencies:
* None.

### Step 3.3: Add a sponsor-approval + launch-gate register

Add (or link) an artifact that records sponsor approval status and the launch-gate register so the rollout flags have a traceable approval path.

Files:
* docs/review/data-observatory-relaunch/ (approval + gate register)
* docs/prds/claracle-data-observatory-relaunch.md (link from Acceptance Status / section 13)

Success criteria:
* Approval status and gate ownership are recorded and linked from the PRD.

Dependencies:
* None.

## Implementation Phase 4: Sequence Remaining Launch Gates

<!-- parallelizable: false -->

### Step 4.1: Consolidate pending gates into the register

For each pending gate, record owner, dependency, and evidence path:
* GA4/GSC connection - FR-035 and the human actions recorded on closed #599 (jmservera) - blocks OBJ-2/4 baselines
* NFR-004 security sign-off - Hermes
* NFR-005 accessibility evidence - Amy/Fry
* Podcaster downstream run - URL (NFR-002/R-04)
* Refreshed visual acceptance
* Q-01/NFR-009 incremental generation cost
* #626 Lighthouse quality-gate follow-ups (disposition: readiness scope or explicit out-of-scope)
* #622 post-review UX polish (disposition: readiness scope or explicit out-of-scope)

Files:
* the launch-gate register from Step 3.3

Success criteria:
* Every pending gate has owner + dependency + evidence path.

Dependencies:
* Step 3.3.

### Step 4.2: Record deferred scope requiring its own plan

Capture as follow-on planning items: GA4/GSC implementation (#599), repo_pages rollout, dynamic topic-creation rollout, incremental-generation-cost design spike (Q-01). Note each needs its own plan and (for rollout) sponsor approval.

Files:
* .copilot-tracking/plans/logs/2026-08-02/claracle-relaunch-readiness-reconciliation-log.md (Suggested Follow-On Work)

Success criteria:
* Deferred workstreams are enumerated with dependencies.

Dependencies:
* None.

## Implementation Phase 5: Validation and Re-Review

<!-- parallelizable: false -->

### Step 5.1: Validate all edited docs

Run markdown lint and verify internal references, version numbers, and changelog consistency across the edited docs and plans.

Validation commands:
* markdown lint per .mega-linter.yml on changed .md files
* grep for stale version/reference strings (BRD v1.0 vs v1.1; PRD version)

Success criteria:
* No lint errors; version/reference consistency verified.

### Step 5.2: Fix minor validation issues

Apply straightforward lint/reference fixes directly.

### Step 5.3: Report blocking issues and hand off deferred plans

Summarize residual blockers and hand off the deferred planning items. The final review
must record addressed findings, resolved PR threads, the merged PR commit, and distinguish
completed GA4/GSC connection work from pending baseline and consent evidence.

## Dependencies

* gh CLI, repository write access, markdown lint tooling, sponsor input.

## Success Criteria

* Docs and plans are consistent, current, and validated; pending gates and deferred workstreams are enumerated with owners and dependencies.
