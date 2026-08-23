---
title: Issue 722 Publication Hydration Evidence
description: Candidate-bound validation for preserving repository migration evidence during publication
author: SquadScope Squad
ms.date: 2026-08-23
ms.topic: reference
---

## Candidate Boundary

* Product candidate: `2088d44bfc9c716221ddbf2f7a8ed6bc89465270`
* Product-tree SHA-256:
  `5b2acbc43ee55f0e0a50afc7815ad2b70567956b668b3082d5cac323930010b5`
* Failed publication run: `32654911857`
* Failure issue: `jmservera/SquadScope#722`

The product-tree validator independently computes both the declared candidate
revision digest and the current product-tree digest.

## Root Cause and Correction

The weekly run generated an eligible article candidate, then the generate job
replaced the complete `data/derived/observatory/` directory with the narrower
publish-branch copy. That removed six reviewed migration-evidence files owned
by `main`, causing the freshness gate to fail before publication.

Both publication workflows now restore the exact six main-owned evidence files
after the publish overlay. Publish-owned `repositories.json` and
`repository-lifecycle.json` still come from the publish branch.

## Validation

* 63 focused pipeline, approved-disposition, and release-candidate tests passed.
* The workflow hydration shell was executed against a local Git repository with
  distinct `main` and `publish` branches; publish-owned generated data was
  overlaid and every main-owned evidence file survived.
* Ruff check and format passed repository-wide.
* Checkov reported 906 passed and zero failed checks.
* Zizmor reported no medium or high findings.
* The complete release diff passed `git apply --reverse --check` from candidate
  `2088d44` to the Phase 4 baseline.

The candidate changes only workflow hydration, workflow contract tests, and
release evidence. No rendered UI, browser behavior, or accessibility contract
changed, so the existing DRF browser evidence remains applicable.
