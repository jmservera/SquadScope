---
title: Claracle Data Observatory Relaunch Remediation Phase 10 Validation
description: RPI validation of Phase 10 final repository and acceptance evidence
author: GitHub Copilot
ms.date: 2026-07-30
ms.topic: reference
---

## Validation Scope

Status: Partial

This validation compares Phase 10 of the remediation plan with the changes log,
planning log, primary research, and current repository evidence. Repository
implementation and external acceptance are assessed separately.

The plan marks Phase 10 and Steps 10.1 and 10.2 incomplete while marking only
blocker reporting complete
(`.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md:242-250`).
That status agrees with current evidence.

## Phase 10 Requirements

Phase 10 is the combined final gate
(`.copilot-tracking/plans/2026-07-29/claracle-data-observatory-relaunch-remediation-plan.instructions.md:258`).
It requires:

* Full Ruff lint and format checks, pytest, Hugo, Pagefind, internal links,
	Playwright, Lighthouse, Checkov, and Zizmor
	(`.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:480-494`)
* Two complete generator runs with no second-run diff, flags-off preservation,
	topic promotion, repository threshold creation, and rename, archive, delete,
	retention, and expiry acceptance
	(`.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:496-503`)
* Isolated correction of minor failures and explicit reporting of larger blockers
	(`.copilot-tracking/details/2026-07-29/claracle-data-observatory-relaunch-remediation-details.md:505-508`)

Research requires full validation before either rollout flag is enabled and treats
a successful exact-release Podcaster run as external evidence
(`.copilot-tracking/research/2026-07-29/claracle-data-observatory-relaunch-remediation-research.md:31,48-55`).

## Plan-to-Changes Comparison

| Plan item | Changes-log claim | Verified status |
|-----------|-------------------|-----------------|
| Step 10.1, full repository validation | Ruff, pytest, Hugo, Pagefind, links, and Checkov passed; browser gates were blocked; Zizmor reported findings | Partial |
| Step 10.2, idempotence and lifecycle acceptance | Focused idempotence and freshness contracts passed; literal two-run proof remains pending | Partial |
| Step 10.3, fixes and blockers | Browser, Zizmor, idempotence, timing, downstream, and external blockers are recorded without weakening checks | Complete |

The Phase 10 summary reports 1,362 pytest tests, Hugo in 6,128 ms, and Pagefind
in 1,534 ms
(`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:210-219`).
Those results are recorded evidence, but no retained raw Phase 10 command log or CI
run URL was found in the workspace. Attempts to refresh the focused tests during
this validation were interrupted or failed before test collection, so this review
does not represent those totals as independently reproduced.

## Verified Repository Evidence

### Final validation implementation

* CI installs pinned Playwright, axe, and Lighthouse packages and Chromium with
	host dependencies in `.github/workflows/ci.yml:60-121`
* CI builds Hugo and Pagefind, records report-only timing, runs rendered and
	internal-link contracts, starts the site, and executes Playwright and Lighthouse
	in `.github/workflows/ci.yml:123-185`
* The current local linker cache does not expose `libnspr4.so` or `libnss3.so`.
	This confirms the reported local browser blocker, but it does not establish a
	repository implementation defect because CI installs browser dependencies
* Both rollout flags remain disabled in `config/observatory.toml:1-2,12-21`

### Idempotence and lifecycle implementation

* Weekly topic backfill asserts a byte-identical second run in
	`tests/test_weekly_topic_backfill.py:53-80`
* Candidate discovery asserts byte stability and four-week eligibility in
	`tests/test_topic_hubs.py:145-165`
* Dynamic topic flags-off behavior preserves the hub, registry, and candidate
	bytes in `tests/test_topic_hubs.py:443-510`
* Repository generation compares complete generated page and taxonomy bytes
	across two runs in `tests/test_observatory_repos.py:194-221`
* Rename, archive, confirmed deletion, three-year retention, source absence,
	expiry, non-mutating check mode, and disabled generation are covered in
	`tests/test_observatory_repos.py:224-449`
* The publish workflow runs five freshness checks after generation in
	`.github/workflows/crawl-and-publish.yml:1204-1208`

These focused contracts support the implementation, but they do not satisfy the
plan's literal all-generator, clean-workspace, second-run diff acceptance record.

### Same-release and external evidence

Deploy invokes the reusable Podcaster smoke only after build and deployment, passing
the resolved week, URL, article path, byte hash, and promotion reference in
`.github/workflows/deploy-site.yml:197-213`. The reusable workflow checks out the
`publish` branch and validates the exact promoted bytes in
`.github/workflows/podcaster-handoff-smoke.yml:1-110`.

This is repository implementation evidence. It is not external acceptance. The
successful protected Podcaster run and Actions URL remain pending, as do GA4, GSC,
production response, social/schema debugger, accessibility, visual, security, URL,
and sponsor evidence
(`docs/review/data-observatory-relaunch/README.md:42-62`).

### Current Zizmor evidence

A fresh read-only `zizmor .github/workflows/` scan on 2026-07-30 returned exit code
zero but still emitted 14 findings: one help/low, twelve warning/medium, and one
error/high. Exit code zero does not make the required security gate clean.

* The low `adhoc-packages` finding is at
	`.github/workflows/crawl-and-publish.yml:511`
* The high `excessive-permissions` finding is the workflow-wide
	`contents: write` grant at `.github/workflows/squad-promote.yml:14-15`
* The twelve medium `artipacked` findings are checkout steps without
	`persist-credentials: false`, including `.github/workflows/squad-ci.yml:18`,
	`.github/workflows/squad-docs.yml:21`, `.github/workflows/squad-release.yml:15`,
	both checkout jobs in `.github/workflows/squad-promote.yml:22,74`, and related
	Squad workflows named by the scan

The refreshed count agrees with the changes log
(`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:221`).
The log characterizes the high and medium findings as pre-existing. Regardless of
origin, the plan requires a clean repository-wide scan, so they remain Phase 10
repository blockers.

## Findings

### Critical

1. The required repository-wide Zizmor gate is not clean. Current evidence contains
	 one high and twelve medium findings. The high workflow-wide write permission and
	 retained checkout credentials affect repository automation security and block
	 Step 10.1. The findings were neither suppressed nor falsely reported as passing,
	 which correctly preserves the gate.
2. Required browser acceptance has not executed successfully. Playwright and
	 Lighthouse are implemented in CI, but the only local Phase 10 attempt is blocked
	 by missing Chromium host libraries and no retained successful CI artifact is
	 cited. Repository implementation exists; execution acceptance remains missing.

### Major

1. The literal all-generator two-run proof required by Step 10.2 is absent. Focused
	 byte-stability tests and freshness modes reduce implementation risk, but they do
	 not prove that every generated path is stable together in one isolated release
	 workspace. The planning log records this deviation at
	 `.copilot-tracking/plans/logs/2026-07-29/claracle-data-observatory-relaunch-remediation-log.md:70-74`.
2. Same-release Podcaster orchestration is implemented and locally contract-tested,
	 but no protected downstream success URL exists. This is an external acceptance
	 gap, not missing repository functionality.
3. Phase 10 passing command output is summarized only in the changes log. Without a
	 retained raw report, CI URL, commit identifier, and environment record, the Ruff,
	 pytest, Hugo, Pagefind, link, and Checkov claims cannot be independently audited
	 beyond the checked-in summary.

### Minor

No additional Phase 10 style or documentation defects were identified. The changes
log and planning log accurately disclose the known blockers and do not overstate
release acceptance.

## Coverage Assessment

Overall Phase 10 coverage is partial.

* Step 10.1 has reported passing evidence for seven gate groups, two locally blocked
	browser groups, and one repository security scan with unresolved findings
* Step 10.2 has strong focused implementation coverage, but its literal second-run
	workspace proof and protected same-release downstream acceptance are incomplete
* Step 10.3 is complete because blockers are explicitly recorded and checks were not
	weakened
* Repository implementation is substantially present, with rollout flags safely off
* External relaunch acceptance remains pending and must not be inferred from source,
	unit tests, workflow definitions, or screenshots

The relaunch is not accepted, consistent with
`.copilot-tracking/changes/2026-07-29/claracle-data-observatory-relaunch-remediation-changes.md:230`.

## Clarifying Questions

* Which clean revision or isolated worktree should be used for the literal two-run
	generator diff so unrelated workspace changes cannot contaminate the result?
* Which retained GitHub Actions run should serve as the successful Playwright,
	Lighthouse, timing, and exact-release Podcaster acceptance record?
* Who owns remediation or explicit reviewed disposition of the Squad workflow
	Zizmor findings before the final gate is rerun?

## Recommended Next Validations

* [ ] Run every generator twice in a clean isolated worktree and retain the second-run
	`git diff --exit-code` output with the commit SHA
* [ ] Run Playwright and Lighthouse on a compatible host or CI runner and retain the
	report artifacts and run URL
* [ ] Remediate the Zizmor high and medium findings, then require a finding-free scan
* [ ] Retain a successful protected exact-release Podcaster smoke URL tied to the same
	promotion reference used by deploy
* [ ] Collect three comparable Hugo and Pagefind CI timing artifacts and obtain owner
	approval before introducing a blocking budget
* [ ] Complete the external security, GA4, GSC, production, debugger, accessibility,
	visual, URL, and sponsor acceptance matrix before either rollout flag changes