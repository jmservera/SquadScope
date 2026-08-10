<!-- markdownlint-disable-file -->
---
title: Topic History Crawl Continuity Details
description: Phase-by-phase execution details for the W33 topic-history repair
ms.date: 2026-08-10
ms.topic: reference
---

## Context

* Plan: `.copilot-tracking/plans/2026-08-10/topic-history-crawl-continuity-plan.instructions.md`
* Research: `.copilot-tracking/research/2026-08-10/topic-history-crawl-continuity-research.md`

## Phase Details

### Regression Contract

Update focused tests to require weekly reconciliation between promotion and
rehashing, a freshness check for weekly topics, non-destructive topic-hub
hydration, and complete sync path coverage.

### Crawl Repair

Use the existing backfill script after `manage_topic_hubs.py`. At this point the
hydrated weekly corpus, dynamic hub page, and promoted registry term are all
available. Rehashing then records the reconciled current page in the publish
manifest.

### Sync Repair

Copy taxonomy inputs and topic-hub logs from publish. Overlay only pages whose
frontmatter marks them as dynamic, and do not replace an existing curated page
with a dynamic page of the same slug. Rebuild `topics.json`, then refresh
`topic-candidates.json` to preserve the candidate fixed point.

### Generated-State Restoration

Apply the same complete-registry backfill to the checked-in corpus in a separate
generated-data branch so the source PR does not mix generated output with code.

### Validation

Run focused tests immediately after each edit, then all repository gates affected
by Python and workflow changes.

Focused source tests passed with 34 tests and 19 subtests. Topic repair tests
passed with 46 tests. Ruff, Hugo, Checkov, and Zizmor 1.27.0 passed. Full pytest
reached 1,579 passing tests on the generated branch; three unrelated baseline
failures remain in data-page freshness, lifecycle corpus size, and trend export
freshness.