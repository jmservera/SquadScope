<!-- markdownlint-disable-file -->
---
title: Topic History Crawl Continuity Research
description: Root-cause analysis and repair contract for the W33 historical topic regression
ms.date: 2026-08-10
ms.topic: troubleshooting
---

## Scope

Repair historical weekly topic frontmatter corrupted during the W33 publish and
preserve crawl convergence introduced by PR #702.

## Evidence

* PR #702 added a trailing candidate-discovery pass after taxonomy mutation. The
  pass only rewrites `data/taxonomy/topic-candidates.json` and is required for a
  stable freshness check.
* The W33 publish transaction hydrated `content/weekly/` from `publish`, where
  older pages lacked canonical `topics` frontmatter.
* Dynamic hub promotion then created `Local First` and appended that topic to its
  evidence weeks. It did not remove existing topics.
* `scripts/backfill_weekly_topics.py` can reconstruct seed and dynamic topic
  assignments when the complete publish registry and hub set are present.
* The sync workflow copies weekly pages but not `content/topics/`,
  `data/taxonomy/`, or `data/topic-hubs/`. Main therefore loses the dynamic term
  while retaining weekly references to it.
* Generate hydration mirrors `content/topics/` destructively. Because publish
  lacks seed hub pages, a later crawl drops those pages from its working tree.

## Selected Approach

1. Reconcile all hydrated weekly pages after dynamic hub promotion and before
   taxonomy refresh. This restores missing canonical seed topics and retains
   newly promoted topics derived from tags.
2. Add weekly-topic reconciliation to the freshness gate.
3. Overlay durable topic hubs during generate hydration instead of deleting the
   main checkout first.
4. Sync topic hubs, taxonomy registries, and topic-hub logs from publish to main,
   overlaying durable hub pages while replacing generated registry state.
5. Restore the current generated corpus in a separate generated-data change.

## Rejected Alternatives

* Removing PR #702's trailing discovery pass would restore the stale-registry
  failure and would not repair historical weekly files.
* Limiting dynamic assignment to the current week would break the documented
  historical evidence behavior of newly promoted hubs.
* Replacing all topic hubs from publish would delete seed hub pages that remain
  authoritative on main.

## Success Criteria

* Historical seed topic assignments are restored.
* Legitimate `Local First` assignments remain on evidence weeks.
* A second reconciliation pass is byte-stable.
* Candidate discovery still reaches its fixed point.
* Topic hub, rendered weekly-link, pipeline, and full test gates pass.