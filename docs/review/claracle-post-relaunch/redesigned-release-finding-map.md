---
title: Claracle Redesigned-Release Finding Map
description: Successor acceptance gates for unresolved historical interaction and accessibility findings
author: SquadScope Squad
ms.date: 2026-08-08
ms.topic: reference
keywords:
  - accessibility
  - acceptance
  - claracle
  - visual review
estimated_reading_time: 4
---

## Purpose

This map carries unresolved interaction and accessibility findings from the
superseded relaunch into the redesigned-release acceptance plan. It does not
alter, close, or reinterpret the frozen historical evidence.

Severity follows BRD-CLARACLE-003 section 8. Every row is severity 2 until its
successor evidence passes against one immutable redesigned-release candidate.
An unresolved row blocks release.

## Frozen Evidence

| Historical record | SHA-256 |
|-------------------|---------|
| `docs/review/data-observatory-relaunch/visual-review-handoff-2026-08-07.md` | `85f3bf597a3f5802b87074c2280d1266e19f5cbe7a01ac16736c9f22eb175a82` |
| `docs/review/data-observatory-relaunch/owner-action-register.md` | `8c821873f6d450ee87c4f4295db8a9a5dc6a9c8c85ce3fb67e870e7460e9b0d0` |
| `docs/review/data-observatory-relaunch/screenshots/README.md` | `fa2ef1554383887836f2758b5612f4e6a0151f533a52c79fe9378fbf412a9eb8` |

## Successor Gates

| ID | Historical finding | Severity | Accountable owner | Redesigned-release gate | Required closure evidence | Status |
|----|--------------------|----------|-------------------|--------------------------|---------------------------|--------|
| DRF-01 | Filter combinations were not represented in the frozen screenshot matrix | 2 | Amy | Add representative combined-filter states to `tests/visual/observatory-visual-regression.spec.mjs` and keyboard operation to `tests/visual/observatory-a11y.spec.mjs` | Passing screenshots and keyboard assertions from the immutable candidate, reviewed by Fry | Open |
| DRF-02 | Expanded lifecycle and provenance detail was not represented | 2 | Amy | Exercise every redesigned disclosure state with pointer and keyboard input in visual and accessibility tests | Passing expanded-state screenshots, focus-order assertions, and Fry review | Open |
| DRF-03 | Copy actions lacked captured success, failure, and focus behavior | 2 | Amy | Test copy activation by keyboard, visible status announcement, failure fallback, and retained focus | Passing Playwright assertions plus live screen-reader confirmation of the status message | Deferred — sponsor risk-accepted waiver (issue #714, expires 2026-11-11) |
| DRF-04 | Internal-link visible focus was not captured across representative pages | 2 | Fry | Extend the visible-focus gate to representative homepage, article, repository, ranking, embed, and navigation links | Passing focus-visible assertions and reviewed screenshots at desktop, mobile, and 200% zoom | Open |
| DRF-05 | Live assistive-technology review remained incomplete | 2 | Fry plus named accessibility reviewer | Run the redesigned release through keyboard-only and live screen-reader paths, including dynamic state, errors, disclosures, and embeds | Dated reviewer, browser, operating system, assistive technology and version, scenarios, findings, severity, disposition, and candidate revision | Deferred — sponsor risk-accepted waiver (issue #714, expires 2026-11-11) |

## Closure Rules

* Automated evidence supplements but does not replace DRF-05 live review.
* Evidence from different candidate revisions cannot be combined into one release
  claim.
* A lower-severity reclassification requires the reviewer, rationale, owner, and
  due date required by the BRD release policy.
* A blocking exception requires sponsor rationale, compensating control, and an
  expiry date.
* Closure updates belong in redesigned-release evidence. The frozen records and
  hashes above remain unchanged.
