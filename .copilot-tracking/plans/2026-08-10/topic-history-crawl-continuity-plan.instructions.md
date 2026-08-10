<!-- markdownlint-disable-file -->
---
description: Repair historical topic frontmatter without breaking weekly crawl convergence
applyTo: '**'
---

# Topic History Crawl Continuity Plan

## User Requests

* Fix the historical topic regression associated with the PR #702 convergence
  path.
* Ensure the weekly crawl continues to work.

## Context Summary

Follow `.github/copilot-instructions.md`, `AGENTS.md`, `architecture.md`, and
`.squad/routing.md`. The root cause and selected approach are recorded in
`.copilot-tracking/research/2026-08-10/topic-history-crawl-continuity-research.md`.

## Implementation Checklist

### Phase 1: Regression Contract
<!-- parallelizable: false -->

* [x] Add workflow-order and hydration-preservation tests.
* [x] Add reconciliation coverage for missing historical topics plus a dynamic
  promoted topic.

### Phase 2: Crawl Repair
<!-- parallelizable: false -->

* [x] Reconcile weekly topic frontmatter after hub promotion.
* [x] Verify reconciliation during generated-content freshness checks.
* [x] Preserve durable topic hubs during publish hydration.

### Phase 3: Sync Repair
<!-- parallelizable: false -->

* [x] Carry dynamic topic hubs, taxonomy inputs, and topic-hub logs from publish.
* [x] Preserve seed hub pages while overlaying dynamic hubs.
* [x] Rebuild topics and candidates in dependency order after sync.

### Phase 4: Generated-State Restoration
<!-- parallelizable: false -->

* [x] Restore historical weekly topic assignments using the complete registry.
* [x] Keep generated-state repair isolated from source changes.

### Phase 5: Validation and Review
<!-- parallelizable: false -->

* [x] Run focused topic and pipeline tests.
* [x] Run Ruff, full pytest, Hugo, Checkov, and Zizmor gates.
* [x] Complete independent workflow and generated-state reviews.

## Dependencies

* Python foundational coding standards
* Repository Python, test, Markdown, and prompt-builder instructions
* Existing `backfill_weekly_topics.py` canonical derivation

## Success Criteria

The crawl publishes a byte-stable candidate registry, preserves canonical
historical topic assignments, carries dynamic topic state to main, and passes
all affected validation gates.