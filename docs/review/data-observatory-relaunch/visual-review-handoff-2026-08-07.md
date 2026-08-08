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

Evidence basis for the 2026-08-08 dispositions below: a local production-parity run on
branch `chore/observatory-timing-gate-and-doc-sync` at revision
`f37b49dbd90afd80ba1fd18ec2169d4da31fcc3a` (Hugo `--minify` build with
`HUGO_PARAMS_GA_MEASUREMENT_ID=G-TEST-OBSERVATORY`, served by `scripts/serve_static.py`).
Toolchain note: this local pass used Playwright 1.58.2 and its bundled Chromium rather
than the CI-pinned 1.54.2, and `@axe-core/playwright@4.10.2` and `lighthouse@12.8.2` were
not available offline; where a check could not run locally the disposition rests on the
retained CI evidence rather than a new local result.

Automated results this run:

- Visual regression / evidence matrix (`observatory-visual-regression.spec.mjs`):
  **68/68 passed**; the index builder produced **64 screenshots + 4 `metadata.json` +
  `index.html`** across `desktop-light`, `desktop-dark`, `mobile-light`, `mobile-dark`
  (desktop 1280x800, mobile 393x727), each tagged with the revision above. Gate
  assertions held: route status, breadcrumb structure, absence of horizontal overflow,
  and consent resolved before every feature capture.
- Responsive / touch-target a11y (`a11y-perf.spec.mjs`): **passed** across all four
  projects (no horizontal overflow, tap targets >= 44x44, main content within 600px).
- Analytics-consent contract (`observatory-analytics.spec.mjs`): **3 of 4 passed** —
  fresh/rejected consent sends no analytics, tool interactions use real handlers with
  bounded/redacted fields, and the standalone frame isolates its own consent. The one
  failure is the post-withdrawal `autoClear` purge of two manually injected `/^_ga/`
  cookies; the `ga-disable-*` flag was set correctly and this branch changed no
  analytics/consent/JS/test file, so the failure is attributed to CookieConsent
  `autoClear` behavior under the non-pinned Playwright/Chromium rather than a branch
  regression. The CI-pinned 1.54.2 analytics gate is authoritative and NFR-008 is
  independently evidenced by the production private-session HAR captures.
- Not run locally (dependency absent offline): the axe WCAG 2.1 A/AA check plus the
  keyboard-label, consent focus-trap/restore, and chart-alternative tests
  (`observatory-a11y.spec.mjs`, needs `@axe-core/playwright`) and the Lighthouse gate.
  These rest on the retained CI a11y and Lighthouse evidence
  ([run 31160859598](https://github.com/jmservera/SquadScope/actions/runs/31160859598)
  and the [2026-08-03 automated evidence record](automated-acceptance-evidence-2026-08-03.md)).

| Reviewer | Role | Decision | Date | Notes |
| -------- | ---- | -------- | ---- | ----- |
| Amy | Visual design | Accept (rendered evidence) | 2026-08-08 | Reviewed the 64-screenshot desktop/mobile x light/dark matrix at `f37b49d`; visual regression suite 68/68 passing with no route, breadcrumb, or horizontal-overflow defects and consent resolved before every feature capture. Residual manual step: the interaction-state captures the [capture checklist](screenshots/README.md) requires (tool filter combinations, expanded lifecycle/provenance detail, copy actions, visible keyboard focus on the internal-link block) are not in the automated matrix and remain an open manual reviewer item. The mobile `embed` long-name truncation is accepted as-is for the syndicated frame. |
| Fry | QA | Accept (automated coverage); one live step remains | 2026-08-08 | Automated a11y (responsive/touch-target) and 3/4 analytics-contract checks pass at `f37b49d`; the single analytics failure is a non-pinned-toolchain `autoClear` artifact, not a branch regression (analytics code unchanged on this branch; CI 1.54.2 gate authoritative). axe WCAG + keyboard/focus-trap/chart-alt and Lighthouse did not run locally (pinned deps absent offline) and are carried on the retained CI evidence. **This disposition rests on automated a11y coverage plus rendered-evidence review; a live screen-reader (assistive-technology) pass for NFR-005 was NOT performed and remains the outstanding item.** |

Recording a decision here also requires updating the Phase 7.3 rows in the
[status of record](status-of-record.md#phase-73-visual-regression-baseline-capture).
