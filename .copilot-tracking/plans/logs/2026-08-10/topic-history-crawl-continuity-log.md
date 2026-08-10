<!-- markdownlint-disable-file -->
---
title: Topic History Crawl Continuity Planning Log
description: Decisions and deviations for the W33 topic-history repair
ms.date: 2026-08-10
ms.topic: reference
---

## Decisions

* Preserve PR #702 candidate convergence unchanged.
* Reuse canonical backfill rather than adding a second topic-mapping algorithm.
* Treat topic hubs as durable overlays and taxonomy registries as generated
  branch state.
* Keep generated corpus restoration separate from workflow source changes.
* Copy only explicit dynamic hubs instead of importing stale static publish hubs.
* Protect curated same-slug hubs from dynamic publish overlays.
* Refresh candidates after rebuilding topics during publish-to-main sync.

## Discrepancies

The initial sync design replaced the whole publish taxonomy and overlaid every
publish topic page. Validation exposed a stale static `ai-ml` hub and registry
term, so sync now carries taxonomy inputs, rebuilds the canonical topic registry,
and copies only explicit dynamic hubs. Independent review added collision
protection and a trailing candidate refresh.

## Validation

* Source affected tests: 34 passed, 19 subtests passed
* Generated topic tests: 46 passed
* Generated transaction: taxonomy, candidates, and weekly reconciliation stable
* Ruff check and format: passed
* Hugo builds: passed on both branches
* Checkov: passed
* Zizmor 1.27.0: no findings
* Full pytest: 1,579 passed; three unrelated generated baseline failures remain

## Suggested Follow-On Work

Add a branch-parity check that compares generated-path ownership contracts across
generate, deploy, and sync workflows.