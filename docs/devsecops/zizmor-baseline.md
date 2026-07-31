---
title: Zizmor Baseline
description: Pinned repository-wide GitHub Actions security scan contract and finding disposition
author: SquadScope maintainers
ms.date: 2026-07-30
ms.topic: reference
keywords:
  - github actions
  - zizmor
  - workflow security
estimated_reading_time: 3
---

## Enforcement contract

[zizmor](https://github.com/zizmorcore/zizmor) audits GitHub Actions workflows
for supply-chain risks such as template injection, dangerous triggers,
unpinned actions, excessive permissions, and persisted checkout credentials.

The local and hosted enforcement contract is:

* Scanner version: `zizmor 1.27.0`
* Persona: `regular`
* Scope: `.github/workflows/`, including every `*.yml` and `*.yaml` workflow
* Blocking severity: `medium` and `high`
* Exclusions: none
* Repository configuration suppressions: none
* Hosted owner: `zizmor-scan` in `.github/workflows/security-scanning.yml`
* Hosted action: `zizmorcore/zizmor-action` v0.6.0 at commit
  `6599ee8b7a49aef6a770f63d261d214911a7ce02`

The hosted action receives `version: 1.27.0` and
`inputs: .github/workflows/`. It uses blocking console mode with
`min-severity: medium` because the action's Advanced Security mode intentionally
suppresses finding exit codes. The job therefore fails on medium or high
regular-persona findings instead of relying on stateful code-scanning merge
protection. Low findings remain visible in the separate full report and require
an explicit disposition.

Hosted online audits use the job's default GitHub token. Use an authenticated
token locally to match that behavior:

```bash
pipx install zizmor==1.27.0
GH_TOKEN="$(gh auth token)" zizmor --persona regular --min-severity medium .github/workflows/
```

For a full report that includes reviewed low-severity findings, omit the
threshold:

```bash
GH_TOKEN="$(gh auth token)" zizmor --persona regular .github/workflows/
```

## Remediation snapshot

The 2026-07-30 full-scope scan found one high-severity
`excessive-permissions` finding and 12 medium-severity `artipacked` findings
in Squad-managed workflows. Remediation made these changes:

* `contents: write` is job-scoped only in `squad-promote.yml`, whose two jobs
  can push promotion commits
* Promotion checkouts do not persist credentials; each push receives
  `github.token` only in that push step and uses an explicit authenticated URL
* Other Squad and label-sync checkouts set `persist-credentials: false`
* Placeholder release workflows use `contents: read` because they do not push
  commits or create releases in their current implementation

The resulting pinned full-scope scan reports no high or medium findings.
Existing inline ignores elsewhere in the workflow corpus predate this phase
and remain narrow to the annotated operation. This phase added no Zizmor ignore
or configuration suppression.

## Ad hoc package disposition

`crawl-and-publish.yml` requires the Copilot CLI during synthesis. The install
is pinned to `@github/copilot@1.0.76`, the published version verified on
2026-07-30. Pinning preserves the synthesis path while preventing an
unreviewed latest-package resolution. No scanner exclusion or broad
`adhoc-packages` suppression was added for this install.

## Validation

Run the workflow contract tests and both security scanners before changing the
baseline:

```bash
pytest -q tests/test_pipeline.py
zizmor --persona regular --min-severity medium .github/workflows/
checkov --directory . --framework github_actions --compact
```

Accepted future findings require a rule-specific inline disposition with a
narrow rationale. Do not exclude a workflow family or weaken scanner scope.
