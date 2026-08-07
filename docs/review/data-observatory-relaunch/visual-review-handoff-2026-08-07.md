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
proceed while GitHub Actions is unavailable. It is a handoff, not an approval. Screenshots
alone are not acceptance; the gate closes only on a dated reviewer conclusion recorded in
the [status of record](status-of-record.md).

## Evidence under review

| Field | Value |
| ----- | ----- |
| Revision | `fix/phase-7-timing-and-visual-evidence` at the commit recorded in each `metadata.json` |
| Origin | Local capture; `workingTreeClean` recorded per project |
| Build | Hugo Extended 0.161.1, Pagefind 1.5.2, served by `scripts/serve_static.py` |
| Browser | Chromium via Playwright 1.54.2 |
| Location | `screenshots/visual-regression/` on the capturing workstation (gitignored) |
| Entry point | `screenshots/visual-regression/index.html` |
| Size | 64 screenshots plus 4 `metadata.json` files |

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

## Disposition

| Reviewer | Role | Decision | Date | Notes |
| -------- | ---- | -------- | ---- | ----- |
| Amy | Visual design | Pending | | |
| Fry | QA | Pending | | |

Recording a decision here also requires updating the Phase 7.3 rows in the
[status of record](status-of-record.md#phase-73-visual-regression-baseline-capture).
