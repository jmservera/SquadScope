---
title: Claracle Integrated Release Candidate Evidence
description: Revision-bound acceptance, review, deployment, and outcome record
author: SquadScope Squad
ms.date: 2026-08-23
ms.topic: reference
---

## Candidate

| Field | Value |
|---|---|
| Release | `claracle-v1-1` |
| Product candidate SHA | `bab613c016c1aedc4f291e87f213206d8bf55f0c` |
| Evidence record | `data/release/claracle-v1.1-release-candidate.json` |
| Schema | `data/schemas/release-candidate.schema.json` |
| Validator | `scripts/validate_release_candidate.py` |
| Baseline | Phase 4 merge `f9fb5d88fefde9b6143adda2d57e20d18f6b5e25` |
| Baseline deployment | GitHub Actions run `31645707266` |
| Release status | GO; deployment verification pending for issue #722 publication hydration fix; DRF-03/DRF-05 remain deferred under issue #714 |

The product candidate is frozen only after all runtime, workflow, content, and
test changes pass local validation. Later evidence-only commits may update this
record and its machine-readable counterpart. Any later product or test change
invalidates the candidate and every revision-bound disposition.

## Automated Acceptance

| Finding | Automated evidence | Owner disposition | Status |
|---|---|---|---|
| DRF-01 | Repository topic, language, lifecycle, period, search, reset, URL, keyboard, combined-state, and visible-count Playwright assertions; four-project combined-state captures | Amy/Fry pass | Closed |
| DRF-02 | Repository, ranking, embed, provenance, fallback, copy-disclosure, pointer, keyboard, focus, touch, and Escape assertions | Amy/Fry pass | Closed |
| DRF-03 | Keyboard clipboard success/failure, polite status, manual-copy guidance, and retained-focus assertions | Amy/Fry automated pass; live-AT pending | Deferred — risk-accepted (issue #714) |
| DRF-04 | Focus-visible assertions and captures for homepage, article, repository, ranking, embed, and navigation links at desktop, mobile, and Chromium browser-engine 200% page scaling | Fry pass | Closed |
| DRF-05 | Genuine named live screen-reader review | Pending | Deferred — risk-accepted (issue #714) |

Automation does not close DRF-05 and does not substitute for screen-reader
confirmation of the DRF-03 status message.

## Required Named Review

DRF-03 and DRF-05 must record the reviewer name, date, exact candidate SHA, operating
system/version, browser/version, screen reader/version, keyboard-only and
screen-reader scenarios, findings, severity, disposition, and unresolved work.
Sponsor `jmservera` explicitly deferred this evidence under the time-bounded
waiver tracked by issue #714. The deferral is not a passing live-AT result and
must be replaced by genuine evidence before the waiver expires.

## Rollback

The last known-good production boundary is Phase 4 merge
`f9fb5d88fefde9b6143adda2d57e20d18f6b5e25`. Rollback uses a protected fix
branch to revert the Phase 5 merge, deploys through the existing GitHub Pages
workflow, and repeats repository, ranking, public JSON, and retired-route
probes. The complete Phase 5 diff passed a reverse-apply check before sponsor
GO. The responsible owner is `jmservera`.

## Outcomes

The prior candidate was invalidated when run `32654911857` showed that publish
hydration removed main-owned repository migration evidence before freshness
validation. Candidate `bab613c` preserves those inputs while retaining
publish-owned generated state. Focused tests, Ruff, Checkov, and Zizmor pass.
Deployment and all deployment-relative outcome windows remain pending until
the merged candidate completes the weekly workflow.

| Window | Due at |
|---|---|
| Release day | Pending deployment |
| D+7 | Pending deployment-relative scheduling |
| D+28 | Pending deployment-relative scheduling |
| M+3 | Pending deployment-relative scheduling |
| M+6 | Pending deployment-relative scheduling |

The approved organic baseline is 0 organic sessions, 149 impressions, 0 clicks,
and 17 impression-bearing queries. The approved targets are at least 250
organic sessions per complete 28-day month and at least 15 queries in the top
20 by six months.
