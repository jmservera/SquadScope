<!-- markdownlint-disable-file -->
---
title: Topic History Crawl Continuity Changes
description: Implemented source and generated-state repairs for W33 topic history
ms.date: 2026-08-10
ms.topic: reference
---

## Related Plan

`.copilot-tracking/plans/2026-08-10/topic-history-crawl-continuity-plan.instructions.md`

## Summary

The crawl now reconciles weekly topics after dynamic promotion, preserves curated
seed hubs, transports only explicit dynamic hubs, and rebuilds taxonomy before
refreshing candidates during publish-to-main sync. A separate generated-data
branch restores W21-W33 topic frontmatter and the valid Local First hub state.

## Modified Source

* `.github/workflows/crawl-and-publish.yml`
* `.github/workflows/sync-publish-to-main.yml`
* `tests/test_pipeline.py`
* `tests/test_weekly_topic_backfill.py`

## Generated-State Repair

* Added `content/topics/local-first/_index.md`
* Restored canonical topics in `content/weekly/2026/W21.md` through `W31.md`
* Refreshed topic, tag, candidate, and dynamic-hub evidence state
* Updated coupled topic derivation and hub tests

## Validation

* Source affected tests: 34 passed, 19 subtests passed
* Generated topic tests: 46 passed
* Ruff, Hugo, Checkov, and Zizmor 1.27.0 passed
* Full pytest: 1,579 passed with three unrelated baseline failures
