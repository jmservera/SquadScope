---
title: Visual Review Handoff for 2026-08-07
description: Named-reviewer handoff for the Data Observatory relaunch visual evidence capture, including coverage against the capture checklist and open observations
author: SquadScope Squad
ms.date: 2026-08-07
ms.topic: reference
keywords:
  - visual acceptance
  - review handoff
  - data observatory
  - screenshots
estimated_reading_time: 5
---

## Purpose

This hands the captured visual evidence to Amy and Fry so the visual acceptance gate can
proceed. It is a handoff, not an approval. Screenshots alone are not acceptance; the gate
closes only on a dated reviewer conclusion recorded in the
[status of record](status-of-record.md).

## Evidence under review

GitHub Actions recovered on 2026-08-07 and now produces this evidence itself. Prefer the
CI artifact; the local capture is the fallback for another outage.

| Field | CI capture (preferred) | Local capture (fallback) |
| ----- | ---------------------- | ------------------------ |
| Source | `production-quality-reports` artifact, [run 31160859598](https://github.com/jmservera/SquadScope/actions/runs/31160859598) | `screenshots/visual-regression/` on the capturing workstation |
| Revision | `93ffa62e3359d49bcabc65423087fa54add11455` | Commit recorded in each `metadata.json` |
| Branch field | `679/merge` | `fix/phase-7-timing-and-visual-evidence` |
| Origin | `ci` | `local` |
| Entry point | `screenshots/visual-regression/index.html` | Same |
| Size | 64 screenshots plus 4 `metadata.json` files | Same |

Build and browser for both: Hugo Extended 0.161.1, Pagefind 1.5.2, served by
`scripts/serve_static.py`, Chromium via Playwright 1.54.2.

On a `pull_request` run the recorded revision is GitHub's merge commit rather than a
branch commit, which is why the branch field reads `679/merge`. Final acceptance should
cite a `main` run so the revision is one that actually ships.

Open `index.html`. It groups each route with its desktop and mobile, light and dark
variants side by side, and it warns when a capture mixes revisions or came from a dirty
working tree. Regenerate it at any time with
`python scripts/design/build_visual_evidence_index.py`.

## What changed since the rejected 2026-07-30 set

The [capture checklist](screenshots/README.md) rejected the previous set because captures
were obscured by the consent banner, lacked mobile and dark variants, and carried no
revision, viewport, or theme identity. This capture addresses all three:

- Every route except `home-consent` rejects the consent decision before the screenshot,
  so no feature capture is obscured. `home-consent` is the banner-specific capture the
  checklist separately requires.
- Four projects cover desktop and mobile at light and dark.
- Each project records revision, branch, origin, working-tree cleanliness, timestamp,
  viewport, and Playwright version.

## Coverage against the capture checklist

| Required surface | Captured as | Status |
| ---------------- | ----------- | ------ |
| Home and consent | `home`, `home-consent` | Covered |
| Topics index | `topics-index` | Covered |
| Topic hub | `topic` | Covered |
| Repository page | `repo-detail`, with `repo-index` | Covered |
| Data ranking | `data-detail` | Covered |
| State-of page | `state-of` | Covered |
| Embeddable chart | `embed` | Covered; standalone frame renders without site chrome |
| Star Velocity Explorer | `tool` | Default state only |
| Weekly article | `weekly`, with `monthly` | Covered |
| Internal-link block | Within `weekly` | Default state only |

Not covered by the automated capture: interaction states. The checklist asks for tool
filter combinations, expanded lifecycle or provenance detail, copy actions, and visible
keyboard focus on the internal-link block. Those remain a manual reviewer step and must
be recorded separately before the gate closes.

## Reviewer checklist

Follow the checklist in the
[visual regression execution guide](visual-regression-execution-guide.md#visual-acceptance-checklist),
then record the outcome below.

## Observations for the reviewers

These were noticed while capturing and are offered as starting points, not findings.

- On the mobile `embed` capture, long repository names are truncated where the bar
  overlay begins, for example `NousResearch/hermes-a…` and `harry0703/MoneyPrinte…`.
  Confirm whether that truncation is acceptable for a syndicated embed, where the label
  is the only identification of the ranked repository.
- Lighthouse on the same run scores the `weekly` page at exactly the 0.90 performance
  threshold and 0.96 accessibility, the tightest margins in the matrix. Every other page
  scores 0.93 or better on performance and 1.00 on accessibility.

## Disposition

| Reviewer | Role | Decision | Date | Notes |
| -------- | ---- | -------- | ---- | ----- |
| Amy | Visual design | Pending | | |
| Fry | QA | Pending | | |

Recording a decision here also requires updating the Phase 7.3 rows in the
[status of record](status-of-record.md#phase-73-visual-regression-baseline-capture).
