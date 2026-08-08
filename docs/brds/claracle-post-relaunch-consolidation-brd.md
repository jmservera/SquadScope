---
title: Claracle Post-Relaunch Consolidation BRD
description: Consolidated business requirements for the remaining Data Observatory relaunch acceptance work plus a placeholder for the next set of requirements
author: SquadScope Squad
ms.date: 2026-08-08
ms.topic: reference
keywords:
  - business requirements
  - claracle
  - data observatory
  - post-relaunch
  - consolidation
estimated_reading_time: 8
---

<!-- markdownlint-disable-file -->

# Claracle Post-Relaunch Consolidation BRD

## Document Control

| Field | Value |
|-------|-------|
| BRD ID | BRD-CLARACLE-003 |
| Status | Draft; consolidates carried-over work, awaiting new requirements |
| Version | 0.1 |
| Author | SquadScope Squad |
| Sponsor | jmservera (also the human approval authority) |
| Last updated | 2026-08-08 |
| Related repositories | SquadScope, SquadScope-Podcaster, SquadScope-Coordinator |
| Supersedes (context) | [BRD-CLARACLE-002](claracle-data-observatory-relaunch-brd.md), [PRD relaunch](../prds/claracle-data-observatory-relaunch.md) |

### Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 0.1 | 2026-08-08 | SquadScope Squad | Initial consolidation of the remaining relaunch acceptance gates, rollout activations, and one engineering follow-up; placeholder for new requirements |

---

## 1. Purpose

The Claracle Data Observatory relaunch (BRD-CLARACLE-002 / the relaunch PRD) is **feature-complete
and its planning is closed**. All prior implementation plans under `.copilot-tracking/plans/` are
marked done or cancelled; any remaining items are carried into this document so the older plans can
be retired. This BRD is the single forward-looking backlog: it holds the small set of remaining
relaunch items and provides a placeholder for the **next requirements jmservera will add**.

## 2. Delivered Baseline (context, not in scope here)

Recorded as delivered in the [relaunch status of record](../review/data-observatory-relaunch/status-of-record.md):

- Discovery IA: topic hubs, data pages (monthly regen), 266 repository pages, internal linking.
- Technical SEO (FR-030..035) including the `author.url` structured-data completion (2026-08-08).
- Analytics and search: GA4/GSC connection, dated launch baseline (NFR-007) and consent behaviour
  (NFR-008), captured 2026-08-08.
- Security acceptance (NFR-004) approved 2026-08-06.
- CI timing budget approved and **enforced** (NFR-009) 2026-08-08 (Hugo 6,000 / Pagefind 5,500 /
  total 11,500 ms).
- Deploy/hydration parity and embed-reference guards (NFR-011/012).
- Linkable assets: MIT dataset, embeddable chart, Star Velocity Explorer tool, State-of page.
- External metadata validation (FR-032/033, NFR-006): home/article/repo pass (2026-08-08).

## 3. Carried-Over Requirements (remaining relaunch work)

> Priority: **Must** (blocks final release acceptance), **Should** (high value), **Could** (opportunistic).

### 3.1 Acceptance gates (human authority)

| ID | Requirement | Owner(s) | Priority | Acceptance |
|----|-------------|----------|----------|------------|
| CR-01 | Live accessibility pass (NFR-005): keyboard-only and screen-reader review of primary nav, consent, filters, charts, tools, and related links on production | Fry + named a11y reviewer | Must | Dated review record combining the automated axe/responsive coverage with keyboard and screen-reader conclusions; findings dispositioned |
| CR-02 | Final visual acceptance: named review of the produced 64-screenshot matrix plus the manual interaction-state captures (filter combinations, expanded detail, copy actions, visible keyboard focus) | Amy, Fry | Must | Disposition table accepted with the interaction captures retained; see [visual review handoff](../review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md) |
| CR-03 | Final relaunch GO/NO-GO release decision consolidating timing (done), security (done), and visual/accessibility acceptance | jmservera | Must | Dated release decision recorded in the status of record |

### 3.2 Rollout activations (staged, sponsor-gated)

| ID | Requirement | Owner(s) | Priority | Acceptance |
|----|-------------|----------|----------|------------|
| CR-04 | Dynamic-topic canary activation: approve the staged `allow_topics = ["local-first"]` revision, flip `enabled = true`, review the resulting transaction, then expand one reviewed slug at a time | Amy, Hermes, jmservera | Should | Hermes + sponsor approval of the exact revision; the promotion transaction reviewed (sanitization, YAML, evidence-backed assignments, taxonomy, logging, rendering, disabled rollback) |
| CR-05 | `repo_pages` rollout activation: content is already regenerated (#668); set `[repo_pages] enabled = true` in a reviewed transaction, inspect the committed diff, confirm production rendering/lifecycle/telemetry, retain rollback | jmservera, URL | Should | Sponsor-approved activation with URL workflow/secret review; both invariants preserved until execution |

### 3.3 Engineering follow-up

| ID | Requirement | Owner(s) | Priority | Acceptance |
|----|-------------|----------|----------|------------|
| CR-06 | Fix the cost-experiment harness so Q-01 can complete: the deploy/experiment hydration `rm -rf content/topics/ && git checkout publish -- content/topics/` collapses topic hubs to the single stale `ai-ml` hub carried on `publish`. Either publish the 5 seed-hub `_index.md` files to `publish`, or scope `content/topics/` out of the experiment's `topic_hubs` expected count. Production is unaffected (term pages are taxonomy-driven). | URL, Leela | Should | A clean `build-cost-experiment.yml` run on `main` with retained artifacts and a dated budget-owner conclusion (Q-01 / NFR-009 incremental cost) |

## 4. Out of Scope

- Re-delivery of anything in Section 2 (already shipped and accepted).
- Changing the deploy hydration semantics beyond the narrowly-scoped CR-06 fix without URL review.
- The retired implementation plans themselves (closed; see Section 6).

## 5. Success Criteria

- CR-01..CR-03 accepted, enabling the final relaunch GO decision.
- CR-04/CR-05 executed only under sponsor approval with both rollout flags controlled.
- CR-06 produces an admissible cost-experiment result.
- This BRD becomes the live backlog that the next requirements (Section 7) extend.

## 6. Retired Plans

All plans under `.copilot-tracking/plans/` are closed as of 2026-08-08. Fully-delivered plans are
marked **DONE**; plans whose only open items were human-gated are marked **CLOSED** with those items
migrated to Section 3 of this BRD. See each plan's status banner for its final state.

## 7. New Requirements (to be added)

> Placeholder. jmservera will add the next set of requirements here. Until then, this BRD tracks
> only the carried-over items in Section 3.

_(pending)_
