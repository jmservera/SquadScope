---
applyTo: '.copilot-tracking/changes/2026-08-07/pending-plan-items-reconciliation-changes.md'
---
<!-- markdownlint-disable-file -->
# Implementation Plan: Pending Plan Items Reconciliation

## User Requests

* Review all pending tasks across every plan in `.copilot-tracking/plans/`
* Check off the items that are already delivered
* Implement all remaining items that repository work can complete

## Overview

Six plans carry unchecked items. Research shows three distinct classes:

1. Already delivered but never ticked (dynamic-topic preview, Hugo/Pagefind
   separate timing, idempotence proof, Phase 7.1/7.3 corrections from `#679`).
2. Executable repository work that is genuinely missing (bounded canary
   allowlist, stale cost-experiment page counts, stale PRD/BRD risk statuses).
3. Human-authority gates that automation must not forge (security signatures,
   sponsor approvals, GSC exports, screen-reader review, protected runs).

This plan closes classes 1 and 2 and records class 3 with named owners.

## Implementation Checklist

### [ ] Phase 1: Bound the Dynamic-Topic Canary

<!-- parallelizable: false -->

* [ ] Step 1.1: Add an `allow_topics` allowlist to `[topic_hubs.dynamic_creation]`
  that, when non-empty, restricts promotion to exactly those slugs
* [ ] Step 1.2: Apply the allowlist in both `preview_dynamic_hubs()` and
  `create_dynamic_hubs()` with a `not-in-allowlist` skip reason
* [ ] Step 1.3: Add tests proving the allowlist bounds promotion and that an
  empty allowlist preserves current behavior

### [ ] Phase 2: Unblock the Cost Experiment

<!-- parallelizable: true -->

* [ ] Step 2.1: Correct `EXPECTED_CLASS_COUNTS` and the `repository_pages`
  variant from the stale 263 to the regenerated corpus size
* [ ] Step 2.2: Confirm the guard still rejects a mismatched corpus

### [ ] Phase 3: Reconcile Product Documents

<!-- parallelizable: true -->

* [ ] Step 3.1: Correct the stale R-08, R-05, and R-03 risk statuses in the PRD
* [ ] Step 3.2: Record NFR-011/NFR-012 delivery status
* [ ] Step 3.3: Bump PRD and BRD versions with changelog entries

### [ ] Phase 4: Reconcile Plan Checkboxes

<!-- parallelizable: true -->

* [ ] Step 4.1: Tick delivered items across the 07-29, 07-30, 07-31, 08-02, and
  08-06 plans with reconciliation notes citing evidence
* [ ] Step 4.2: Leave human-authority items unticked with named owners

### [ ] Phase 5: Validation

<!-- parallelizable: false -->

* [ ] Step 5.1: Run `pytest tests/`, `ruff check .`, `ruff format --check .`
* [ ] Step 5.2: Run `hugo --minify` and `scripts/check_internal_links.py`
* [ ] Step 5.3: Report the remaining human-gated items

## Dependencies

* `.copilot-tracking/research/subagents/2026-08-07/pending-plan-items-research.md`
* Hermes, URL, Amy, Fry, and jmservera authority for the remaining gates

## Success Criteria

* No plan checkbox misrepresents delivered state.
* The dynamic-topic canary can be bounded to one reviewed slug.
* The cost experiment runs against the current corpus.
* PRD and BRD risk statuses match delivered reality.
* Both rollout flags remain disabled.
