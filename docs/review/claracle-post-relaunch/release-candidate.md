---
title: Claracle Integrated Release Candidate Evidence
description: Revision-bound acceptance, review, deployment, and outcome record
author: SquadScope Squad
ms.date: 2026-08-12
ms.topic: reference
---

## Candidate

| Field | Value |
|---|---|
| Release | `claracle-v1-1` |
| Product candidate SHA | Pending freeze |
| Evidence record | `data/release/claracle-v1.1-release-candidate.json` |
| Schema | `data/schemas/release-candidate.schema.json` |
| Validator | `scripts/validate_release_candidate.py` |
| Baseline | Phase 4 merge `f9fb5d88fefde9b6143adda2d57e20d18f6b5e25` |
| Baseline deployment | GitHub Actions run `31645707266` |
| Release status | Preparing |

The product candidate is frozen only after all runtime, workflow, content, and
test changes pass local validation. Later evidence-only commits may update this
record and its machine-readable counterpart. Any later product or test change
invalidates the candidate and every revision-bound disposition.

## Automated Acceptance

| Finding | Automated evidence | Owner disposition | Status |
|---|---|---|---|
| DRF-01 | Repository topic, language, lifecycle, period, search, reset, URL, keyboard, combined-state, and visible-count Playwright assertions; four-project combined-state captures | Pending Amy/Fry review | Automated checks pass |
| DRF-02 | Repository, ranking, embed, provenance, fallback, copy-disclosure, pointer, keyboard, focus, touch, and Escape assertions | Pending Amy/Fry review | Automated checks pass |
| DRF-03 | Keyboard clipboard success/failure, polite status, manual-copy guidance, and retained-focus assertions | Pending Amy/Fry and live-AT review | Automated checks pass |
| DRF-04 | Focus-visible assertions and captures for homepage, article, repository, ranking, embed, and navigation links at desktop, mobile, and 200% equivalent viewport | Pending Fry review | Automated checks pass |
| DRF-05 | Genuine named live screen-reader review | Pending | Blocked |

Automation does not close DRF-05 and does not substitute for screen-reader
confirmation of the DRF-03 status message.

## Required Named Review

DRF-05 must record the reviewer name, date, exact candidate SHA, operating
system/version, browser/version, screen reader/version, keyboard-only and
screen-reader scenarios, findings, severity, disposition, and unresolved work.
Until that evidence exists, sponsor GO, merge, and deployment remain blocked.

## Rollback

The last known-good production boundary is Phase 4 merge
`f9fb5d88fefde9b6143adda2d57e20d18f6b5e25`. Rollback uses a protected fix
branch to revert the Phase 5 merge, deploys through the existing GitHub Pages
workflow, and repeats repository, ranking, public JSON, and retired-route
probes. The responsible owner is `jmservera`.

## Outcomes

Release-day evidence is recorded only after deployment. D+7, D+28, M+3, and
M+6 observations receive exact due dates from the production deployment
timestamp and remain scheduled until their windows arrive.
