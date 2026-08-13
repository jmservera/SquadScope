---
title: Phase 5 Automated Candidate Evidence
description: Exact-revision automated acceptance evidence for the Claracle integrated release candidate
author: SquadScope Squad
ms.date: 2026-08-13
ms.topic: reference
---

## Candidate Boundary

* Product candidate: `6ba13b501113201e69348d7c3c6042f8a9f96a8f`
* Product-tree SHA-256:
  `1215c36a94132f28833d51436fb62c8a11ce400b0bf0d30ad07869fe4b55bb54`
* Schema version: 1.1.0 (adds deferred/waiver finding state)
* Build tools: Hugo `0.161.1`, Pagefind `1.5.2`

The product-tree validator independently computes the declared candidate
revision and current product digests. Both must match the recorded digest.

## Gate Results

| Gate | Result |
|---|---|
| Python | 1,634 passed; 1 pre-existing unrelated failure |
| Candidate validator | 25 passed (16 original + 9 waiver tests); Git boundary passed |
| Ruff | 188 files linted and format-checked |
| Bandit | No findings |

Front-end, Node, Hugo, Playwright, Checkov, and Zizmor suites are unaffected by
this candidate's changes (schema/validator/test only) and will run via hosted CI.

## Finding Coverage

* DRF-01: topic, language, status, current/recent period, text, reset, URL,
  combined keyboard state, visible names, and announced count.
* DRF-02: expanded repository, ranking, embed, provenance, fallback,
  copy-disclosure, pointer, keyboard, focus-order, touch, and Escape states.
* DRF-03: race-safe copy success and failure feedback, visible manual guidance,
  polite status, retained keyboard focus, and restoration of the stable label.
* DRF-04: homepage, article, repository, ranking, embed, and navigation focus
  at desktop, mobile, and Chromium browser-engine 200% page scaling.

DRF-05 is intentionally absent. Automated evidence cannot replace a genuine
named live screen-reader review.

## Deferred Findings

DRF-03 and DRF-05 carry a sponsor-approved waiver (issue #714, expires
2026-11-11). The waiver is fail-closed: once expired, the validator fails CI
unconditionally until the finding is genuinely closed or the waiver is renewed.
