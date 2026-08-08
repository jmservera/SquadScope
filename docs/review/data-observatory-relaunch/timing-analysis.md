---
title: CI Timing Analysis and Budget Approval
description: Performance baseline, median/p95 calculations, and timing budget approval for Data Observatory relaunch
author: SquadScope Squad
ms.date: 2026-08-08
ms.topic: reference
keywords:
  - timing
  - performance
  - ci budget
  - baseline
estimated_reading_time: 5
---

<!-- markdownlint-disable-file -->

## Overview

This document consolidates CI timing data for the production site build (Hugo + Pagefind), establishes baseline metrics, and tracks timing budget approval. All times are measured in milliseconds on `ubuntu-latest` runners.

## Timing Measurements Collection

### Phase 6.3 Evidence Requirement

Step 6.3 of the remediation plan requires:

- Three comparable successful Production site timing artifacts (commit, Hugo duration, Pagefind duration)
- Median and p95 calculations for Hugo and Pagefind independently
- Approved budget thresholds before enforcement
- Named approver sign-off

### CI Timing Report Format

Each `reports/build-timing.json` captured by `.github/workflows/ci.yml` contains:

```json
{
  "commit": "<SHA>",
  "mode": "report-only",
  "hugo": {
    "version": "0.161.1",
    "duration_ms": <milliseconds>
  },
  "pagefind": {
    "version": "1.5.2",
    "duration_ms": <milliseconds>
  },
  "blocking_threshold_ms": null
}
```

## Baseline Data Collection

### Run 1: Exact-main Production CI (2026-08-05)

**Run ID**: `31039618366`
**Commit**: `211f0974ce375e427591803cc3f3dfd39e169ead`
**Branch**: `main`
**Date**: 2026-08-05
**Status**: ✅ Passed

Captured timing (transcribed from `reports/build-timing.json`):

- Hugo: `2,822` ms (0.161.1)
- Pagefind: `2,707` ms (1.5.2)
- **Total build**: `5,529` ms

Artifact location: [GitHub Actions run 31039618366](https://github.com/jmservera/SquadScope/actions/runs/31039618366)

### Run 2: Production `main` CI (2026-08-06)

**Run ID**: `31079871801`
**Event**: `push` to `main`
**Commit**: `f5c2be46fa598c1593c91c9dba6c39d98b0e347c`
**Branch**: `main`
**Date**: 2026-08-06 (07:09:54 UTC)
**Status**: ✅ Passed

Captured timing (transcribed from `reports/build-timing.json`):

- Hugo: `2,456` ms (0.161.1)
- Pagefind: `2,255` ms (1.5.2)
- **Total build**: `4,711` ms

Artifact location: [GitHub Actions run 31079871801](https://github.com/jmservera/SquadScope/actions/runs/31079871801)

### Run 3: Production `main` CI (2026-08-06)

**Run ID**: `31081291997`
**Event**: `push` to `main`
**Commit**: `353b147ec1e8e0c9572a1d1d2ab4da2a94923b9d`
**Branch**: `main`
**Date**: 2026-08-06 (07:32:06 UTC)
**Status**: ✅ Passed

Captured timing (transcribed from `reports/build-timing.json`):

- Hugo: `3,058` ms (0.161.1)
- Pagefind: `2,316` ms (1.5.2)
- **Total build**: `5,374` ms

Artifact location: [GitHub Actions run 31081291997](https://github.com/jmservera/SquadScope/actions/runs/31081291997)

### Correction Notice (2026-08-06)

An earlier revision of this document recorded Run 1 as Hugo `15,339` ms and Pagefind `1,631` ms, and recorded a PR-branch build as Run 2. Both entries were wrong:

- The Run 1 figures did not match the retained `build-timing.json` artifact for run `31039618366`, which reports Hugo `2,822` ms and Pagefind `2,707` ms.
- The former Run 2 was a `pull_request` build on the PR #677 branch, which is not comparable to a production `main` build.

All three runs above are now `push`-to-`main` production builds, each transcribed directly from its retained artifact. The "Run 2 anomaly" previously flagged does not exist: Hugo durations across the three production runs fall within a 602 ms spread.

## Statistical Analysis

### Three Production `main` Measurements

| Component | Run 1 (211f0974) | Run 2 (f5c2be46) | Run 3 (353b147e) | Median | p95 (nearest-rank) |
|---------------|------------------|------------------|------------------|--------|--------------------|
| Hugo 0.161.1  | 2,822 ms         | 2,456 ms         | 3,058 ms         | 2,822 ms | 3,058 ms         |
| Pagefind 1.5.2 | 2,707 ms        | 2,255 ms         | 2,316 ms         | 2,316 ms | 2,707 ms         |

With three samples, the nearest-rank p95 (`ceil(0.95 x 3) = 3`) resolves to the maximum observed value for each component. Treat these percentiles as an upper bound from a small sample rather than a stable long-run estimate.

### Proposed Budget Thresholds (Pending Approval)

The previously proposed thresholds (Hugo 20,000 ms, Pagefind 2,500 ms) are superseded because they were derived from the incorrect Run 1 baseline. The Pagefind threshold in particular would already have been breached by the corrected Run 1 value of 2,707 ms.

Revised proposal, sized at approximately twice the observed p95 to absorb GitHub-hosted runner variance:

| Component | Observed p95 | Proposed Threshold | Headroom over p95 | Status |
|-----------|--------------|--------------------|-------------------|--------|
| Hugo build | 3,058 ms | 6,000 ms | ~96% | Proposed |
| Pagefind index | 2,707 ms | 5,500 ms | ~103% | Proposed |
| Total build | 5,529 ms | 11,500 ms | ~108% | Proposed |

**Note**: Thresholds require review by the timing-budget owner before enforcement. Current measurements remain report-only (`blocking_threshold_ms: null`); no blocking gate is active.

## Collection Workflow

1. **Run Passing CI** → Captures `reports/build-timing.json`
2. **Download Artifact** → Extract timing report from Actions artifacts
3. **Record Run Data** → Add commit, date, duration to this document
4. **Calculate Stats** → Once 3 runs collected, compute median and p95
5. **Owner Review** → Timing budget owner approves thresholds
6. **Enforcement** → Update `.github/workflows/ci.yml` to fail on exceeded budgets

## Approval Chain

### Timing Budget Owner

- **Role**: Review and approve timing threshold recommendations
- **Responsibility**: Confirm budgets align with acceptable user experience and CI capacity
- **Sign-off Required**: Yes
- **Status**: ✅ Approved 2026-08-08 (jmservera)

### Infrastructure Owner (URL)

- **Role**: Validate CI timing data collection methodology
- **Responsibility**: Confirm measurements are reproducible and artifact retention is durable
- **Sign-off Required**: Yes
- **Status**: ✅ Approved 2026-08-08 (accepted by jmservera as production authority; collection method documented and reproducible)

### Production Owner (jmservera)

- **Role**: Final acceptance of timing budget as production control
- **Responsibility**: Confirm enforcement mechanism and rollback plan
- **Sign-off Required**: Yes
- **Status**: ✅ Approved 2026-08-08 (jmservera); enforcement applied to `ci.yml`, rollback = revert the step to report-only

### Data Collection Status

**Status Date**: 2026-08-08
**Collection**: ✅ **COMPLETE** — three comparable production `main` runs transcribed from retained artifacts
**Approval**: ✅ **APPROVED 2026-08-08** — jmservera accepted the revised thresholds (Hugo 6,000 ms, Pagefind 5,500 ms, Total 11,500 ms); enforcement applied to `ci.yml`

The prior provisional approval is withdrawn. It relied on the incorrect Run 1 baseline and on a non-comparable PR-branch measurement, so its margin calculations were invalid. No provisional or implied approval carries forward; the revised thresholds require a fresh decision.

**What the owner is asked to decide**:

1. Accept or adjust the proposed thresholds (Hugo 6,000 ms, Pagefind 5,500 ms).
2. Confirm whether three samples are sufficient, or require a larger collection window before enforcement.
3. Confirm the report-only posture remains in place until enforcement is separately approved.

## Approval Request (approved 2026-08-08)

> Decision: jmservera accepted the proposed budgets on 2026-08-08; the enforcement step is
> now applied in `ci.yml` (see Enforcement below). The request below is retained as the
> historical record of what was asked.

To: timing-budget owner, URL, jmservera. Subject: Data Observatory timing budget sign-off.

Three comparable production `main` CI runs were collected and transcribed:

| Component | Median | p95 (nearest-rank) | Proposed budget | Headroom over p95 |
| --------- | ------ | ------------------ | --------------- | ----------------- |
| Hugo 0.161.1 | 2,822 ms | 3,058 ms | 6,000 ms | ~96% |
| Pagefind 1.5.2 | 2,316 ms | 2,707 ms | 5,500 ms | ~103% |
| Total | 5,138 ms | 5,529 ms | 11,500 ms | ~108% |

Requested decision:

1. Accept or adjust the proposed budgets (sized at ~2x observed p95 for runner variance).
2. Confirm three samples suffice, or require a larger window before enforcement.
3. Confirm the report-only posture holds until enforcement is separately approved.

Applied 2026-08-08: jmservera accepted the budgets and the enforcement step is now live in
`ci.yml` (see Enforcement below), replacing the earlier report-only posture.

## Enforcement (applied 2026-08-08 after owner approval)

The following step is now live in `.github/workflows/ci.yml`, replacing the previous
report-only step. `blocking_threshold_ms` is set and the build fails if any budget is
exceeded. Rollback: revert this step to the report-only version.

```yaml
      - name: Write build timing and enforce budgets
        env:
          COMMIT_SHA: ${{ github.sha }}
          HUGO_DURATION_MS: ${{ steps.hugo-build.outputs.duration_ms }}
          PAGEFIND_DURATION_MS: ${{ steps.pagefind-build.outputs.duration_ms }}
          HUGO_BUDGET_MS: '6000'
          PAGEFIND_BUDGET_MS: '5500'
          TOTAL_BUDGET_MS: '11500'
        run: |
          set -euo pipefail
          mkdir -p reports
          total_ms=$(( HUGO_DURATION_MS + PAGEFIND_DURATION_MS ))
          printf '{\n  "commit": "%s",\n  "mode": "blocking",\n  "hugo": {"version": "%s", "duration_ms": %s, "budget_ms": %s},\n  "pagefind": {"version": "%s", "duration_ms": %s, "budget_ms": %s},\n  "total_ms": %s,\n  "blocking_threshold_ms": %s\n}\n' \
            "${COMMIT_SHA}" "${HUGO_VERSION}" "${HUGO_DURATION_MS}" "${HUGO_BUDGET_MS}" \
            "${PAGEFIND_VERSION}" "${PAGEFIND_DURATION_MS}" "${PAGEFIND_BUDGET_MS}" \
            "${total_ms}" "${TOTAL_BUDGET_MS}" > reports/build-timing.json
          fail=0
          if [ "${HUGO_DURATION_MS}" -gt "${HUGO_BUDGET_MS}" ]; then
            echo "::error::Hugo build ${HUGO_DURATION_MS}ms exceeds budget ${HUGO_BUDGET_MS}ms"; fail=1
          fi
          if [ "${PAGEFIND_DURATION_MS}" -gt "${PAGEFIND_BUDGET_MS}" ]; then
            echo "::error::Pagefind ${PAGEFIND_DURATION_MS}ms exceeds budget ${PAGEFIND_BUDGET_MS}ms"; fail=1
          fi
          if [ "${total_ms}" -gt "${TOTAL_BUDGET_MS}" ]; then
            echo "::error::Total build ${total_ms}ms exceeds budget ${TOTAL_BUDGET_MS}ms"; fail=1
          fi
          [ "${fail}" -eq 0 ] || exit 1
```

Activation checklist: (1) timing-budget owner accepts or adjusts the budgets above;
(2) URL confirms methodology and artifact durability; (3) jmservera confirms the
enforcement mechanism and rollback (revert this step to the report-only version).

## Implementation Notes

### Measurement Integrity

- Measurements use system `date +%s%N` (nanosecond precision) on GitHub-hosted runners
- Conversion to milliseconds: `(finished_ns - started_ns) / 1,000,000`
- No external network calls or downloads are timed (tool installation precedes timing)
- Page volume (site size) is noted for statistical grouping

### Page Volume at Baseline

**Measured on the 2026-08-06 `main` working tree after a full `hugo --minify` build**:

- Content source files: 313 Markdown files under `content/`
- Hugo page count reported by the build: 2,700
- Rendered output: 1,503 HTML files, 49 MB total under `public/`

An earlier revision recorded ~18,000+ Markdown files and ~850+ MB of output. Those figures did not match the repository and are corrected above. Re-measure with `find content -name '*.md' | wc -l`, `find public -name '*.html' | wc -l`, and `du -sh public` when refreshing this section.

Budget adjustments may be needed if page volume changes materially (>20% growth).

### Durable Artifact Retention

- CI artifacts retained for 30 days (Actions setting)
- Evidence links point to specific run IDs and jobs
- Run data must be recorded in this document before artifact expiration
- Long-term record: This markdown file (versioned in git)

## Pending Deliverables

- [x] Collection of Run 2 timing data (production `main` run `31079871801`)
- [x] Collection of Run 3 timing data (production `main` run `31081291997`)
- [x] Median and p95 calculation
- [x] Timing budget owner review and approval of the revised thresholds
- [x] Infrastructure owner (URL) sign-off
- [x] Production owner (jmservera) acceptance
- [x] Enforcement gate activation in CI workflow

## Cross-References

- Plan: [`.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md`](../../../.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md) (Step 6.3)
- Evidence index: [`docs/review/data-observatory-relaunch/README.md`](./README.md)
- CI workflow: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)
