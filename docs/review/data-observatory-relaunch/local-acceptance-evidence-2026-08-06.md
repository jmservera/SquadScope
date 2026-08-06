---
title: Data Observatory Local Acceptance Evidence for 2026-08-06
description: Dated local production-equivalent validation and visual evidence capture for Claracle relaunch gates, recorded while GitHub Actions was unavailable
author: SquadScope Squad
ms.date: 2026-08-06
ms.topic: reference
keywords:
  - acceptance evidence
  - visual regression
  - accessibility
  - lighthouse
  - local validation
estimated_reading_time: 6
---

## Evidence boundary

This record retains local, production-equivalent validation for branch
`fix/phase-7-timing-and-visual-evidence` at revision
`16923f6cbeb9d59a6963a5c68173e0172fc9095a`. It exists because GitHub Actions was
unavailable on 2026-08-06, so the usual CI artifact path could not produce evidence.

It does not grant security, accessibility, visual, Podcaster, analytics, or sponsor
acceptance, and it does not replace a `main` CI run. Local timing numbers are not
comparable to the runner measurements in [timing-analysis.md](./timing-analysis.md)
and must not be used for budget approval.

## Environment

| Component | Version or setting | Parity with CI |
| --------- | ------------------ | -------------- |
| Hugo Extended | 0.161.1 (downloaded and checksum-verified) | Matches `ci.yml` |
| Pagefind | 1.5.2 | Matches `ci.yml` |
| Playwright | 1.54.2, Chromium only | Matches `ci.yml` |
| `@axe-core/playwright` | 4.10.2 | Matches `ci.yml` |
| Lighthouse | 12.8.2 | Matches `ci.yml` |
| Python | 3.12.3 | Matches `ci.yml` |
| Ruff | 0.16.1 | CI pins 0.15.7 |
| Base URL | `http://127.0.0.1:1313` served by `scripts/serve_static.py` | Matches `ci.yml` |
| `HUGO_PARAMS_GA_MEASUREMENT_ID` | `G-TEST-OBSERVATORY` | Matches `ci.yml` |
| Host | WSL2 developer workstation | Differs from `ubuntu-latest` |

## Automated control evidence

| Check | Result |
| ----- | ------ |
| `ruff check .` | Passed |
| `ruff format --check .` | 858 files formatted; one `.copilot-tracking` research note differs under local Ruff 0.16 only |
| `python -m pytest tests/` | 1,471 passed, 34 subtests passed, 2 expected warnings |
| `python scripts/check_embed_sources.py` | All embed `source_page` references resolve |
| Rendered SEO, weekly link, internal link, and topic-hub suites | 39 passed |
| `python scripts/check_internal_links.py public --base-url https://claracle.com/` | Passed |
| Axe, responsive, and analytics browser gates | 147 passed, 0 failed, 305 skipped by project scoping |
| Visual regression evidence capture | 44 passed |

## Visual regression evidence

Captured with `tests/visual/observatory-visual-regression.spec.mjs` against the served
production build. Output is gitignored and lives at `screenshots/visual-regression/`
on the capturing workstation.

- 10 routes resolved from the built `sitemap.xml`: `home`, `about`, `dashboard`,
  `search`, `charts`, `repo-index`, `repo-detail`, `topic`, `weekly`, `monthly`
- 4 projects: `desktop-light`, `desktop-dark`, `mobile-light`, `mobile-dark`
- 40 screenshots plus 4 `metadata.json` files, each recording revision
  `16923f6cbeb9d59a6963a5c68173e0172fc9095a`, branch, `origin: local`,
  `workingTreeClean: true`, timestamp, viewport, and Playwright version
- Every non-home route asserted a real `nav.breadcrumbs` construct with a marker-free
  flex or grid list and a terminal `aria-current="page"` label
- No route overflowed horizontally at any viewport in the matrix

Conclusion: the evidence matrix is complete and revision-tagged. Named visual review by
Amy and Fry remains outstanding; see the
[visual regression execution guide](visual-regression-execution-guide.md).

## Lighthouse observations

Thresholds are unchanged: performance 0.90, accessibility 0.95, best practices 0.95.
Two runs were taken, at the CI default concurrency of 3 and again serially, because
page-level concurrency competes for CPU on a workstation.

| Page | Performance (serial) | Accessibility | Best practices | CLS |
| ---- | -------------------- | ------------- | -------------- | --- |
| home | 92% | 100% | 100% | 0.000 |
| weekly | 88% | 96% | 100% | 0.000 |
| monthly | 90% | 100% | 100% | 0.000 |
| yearly | 93% | 100% | 100% | 0.000 |
| topic | 93% | 100% | 100% | 0.000 |
| data | 71% | 100% | 100% | 0.000 |
| repository | 93% | 100% | 100% | 0.000 |
| chart | 100% | 100% | 100% | 0.000 |
| tool | 93% | 100% | 100% | 0.000 |

Accessibility, best practices, and CLS pass on every page. Performance scores moved by
up to 30 points between the concurrent and serial runs on the same build, so the local
performance column is not a gate result. The CI Lighthouse job remains the authority
for the performance threshold, and `data` is the page to watch when it next runs.

## Local build timing (informational only)

Measured on the workstation, not on a runner: Hugo 6,338 ms and Pagefind 2,778 ms.
These values are recorded to show the build completed, not to inform the timing budget.
The three comparable production `main` measurements in
[timing-analysis.md](./timing-analysis.md) remain the only figures eligible for
budget-owner approval.

## Defect found and corrected

The blocking analytics gate contained a latent flake that CI masked. In
`tests/visual/observatory-analytics.spec.mjs`, `waitForFunction` was used to wait for
consent bootstrap inside the cross-origin embed iframe. Playwright bound the predicate
to the frame's pre-navigation execution context, so it never resolved even though
`frame.evaluate` confirmed `window.CookieConsent` and `window.ObservatoryAnalytics`
were already present at the moment of timeout.

The failure reproduced whenever the standalone-frame test ran after another test in the
same file, and did not reproduce when that test ran alone. CI never surfaced it because
`tests/visual/playwright.config.mjs` sets `retries: 1` when `CI` is set.

The helpers now poll `evaluate`, which re-resolves the frame's current execution context
on each attempt. The previously failing sequences pass 6 of 6 with `--repeat-each 3`, and
the full three-spec gate set passes with no failures.

## Still blocked

| Gate | Reason it cannot close locally |
| ---- | ------------------------------ |
| Timing budget approval (Phase 7.1) | Needs runner-comparable artifacts and the timing-budget owner's decision |
| Visual acceptance (Phase 7.3) | Needs named review and disposition by Amy and Fry |
| Accessibility acceptance (NFR-005) | Needs keyboard-only and screen-reader review by a named reviewer |
| Incremental generation cost (Q-01 / NFR-009) | Needs the dispatched experiment with immutable reviewed SHAs and runner metadata |
| GA4 and GSC baseline and consent evidence (FR-035) | Needs Google property access and production observation |
| External metadata and feed validation | Needs external debuggers and named reviewer conclusions |

Both rollout flags remain disabled: `repo_pages.enabled` and
`topic_hubs.dynamic_creation.enabled` are unchanged.
