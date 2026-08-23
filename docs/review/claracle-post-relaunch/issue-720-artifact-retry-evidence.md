---
title: Issue 720 Artifact Retry Evidence
description: Candidate-bound evidence for resilient weekly workflow artifact handoffs
author: SquadScope Squad
ms.date: 2026-08-23
ms.topic: reference
---

## Incident

Scheduled workflow run `31985981109` successfully uploaded the `raw-data`
artifact, then the analyze job failed when the artifact service returned a
transient intermediary `403 Forbidden` during its one-shot download. The
crawler and analysis inputs were not defective.

## Candidate

| Field | Value |
|---|---|
| Candidate SHA | `8895304313aa145e02072b9a1109ba93c28bfe70` |
| Product-tree digest | `fcb3cf50d21a60b6b234d2d4cbc1847ad9de995f11def98b441b8198cab5230e` |
| Issue | jmservera/SquadScope#720 |
| Pull request | jmservera/SquadScope#721 |

## Change

Critical same-run artifact handoffs now use the authenticated GitHub CLI
artifact transport with five bounded attempts and exponential delays. Each
attempt stages extraction in a temporary directory; destination files are
overlaid only after `gh run download` succeeds. The helper constrains repository
identifiers, run IDs, artifact names, and workspace destinations, resolves the
CLI to an absolute path, and never invokes a shell.

## Validation

* Ruff check and format passed.
* `tests/test_download_run_artifact.py` and `tests/test_pipeline.py` passed.
* Bandit found no issue in the helper.
* Checkov reported 0 failed GitHub Actions checks.
* Zizmor reported no medium or high workflow finding.
* The helper successfully downloaded `raw-data` from failed run `31985981109`.
* URL, Hermes, Fry, and Leela review found no release blocker after the workflow
  token and permission contracts were added to tests.

## Release disposition

The operational change does not modify the user-facing accessibility surfaces.
Existing DRF-03/DRF-05 waivers remain time-bounded to `2026-11-11T16:50:19Z`
and are rebound to this exact candidate without extending their expiry.
Deployment evidence and deployment-relative outcomes return to pending until
the merged workflow completes successfully.
