---
title: Phase 5 Automated Candidate Evidence
description: Exact-revision automated acceptance evidence for the Claracle integrated release candidate
author: SquadScope Squad
ms.date: 2026-08-13
ms.topic: reference
---

## Candidate Boundary

* Product candidate: `31ab98c99c7175adf83d62321dd6f592ab54a5fd`
* Product-tree SHA-256:
  `25f9fcc8a8b8e41c4a073f3eb057ca0b55ada6c23b3901896d4838863ddb75cf`
* Production-test origin: `http://127.0.0.1:1313`
* Build tools: Hugo `0.161.1`, Pagefind `1.5.2`, Zizmor `1.27.0`

The product-tree validator independently computed the declared candidate
revision and current product digests. Both matched the recorded digest.

## Gate Results

| Gate | Result |
|---|---|
| Python | 1,670 passed; two expected URL-rejection warnings |
| Candidate validator | 16 passed; Git boundary passed |
| Ruff | 188 files linted and format-checked |
| Node | 2 passed |
| Hugo, Pagefind, rendered contracts, internal links | Passed |
| Repository, accessibility, and visual browser suites | 172 passed |
| Checkov | 906 passed, zero failed, six documented skips |
| Zizmor regular persona, medium/high | No findings |
| Bandit | No findings |

## Finding Coverage

* DRF-01: topic, language, status, current/recent period, text, reset, URL,
  combined keyboard state, visible names, and announced count.
* DRF-02: expanded repository, ranking, embed, provenance, fallback,
  copy-disclosure, pointer, keyboard, focus-order, touch, and Escape states.
* DRF-03: copy success, copy failure, visible manual guidance, polite status,
  and retained keyboard focus.
* DRF-04: homepage, article, repository, ranking, embed, and navigation focus
  at desktop, mobile, and Chromium browser-engine 200% page scaling.

DRF-05 is intentionally absent. Automated evidence cannot replace a genuine
named live screen-reader review.
