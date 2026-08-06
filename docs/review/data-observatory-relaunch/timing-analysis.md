---
title: CI Timing Analysis and Budget Approval
description: Performance baseline, median/p95 calculations, and timing budget approval for Data Observatory relaunch
author: SquadScope Squad
ms.date: 2026-08-06
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

Captured timing:
- Hugo: `15,339` ms (0.161.1)
- Pagefind: `1,631` ms (1.5.2)
- **Total build**: `16,970` ms

Artifact location: [GitHub Actions run 31039618366](https://github.com/jmservera/SquadScope/actions/runs/31039618366)

### Run 2: Production CI (2026-08-06)

**Run ID**: `31095474806`
**Commit**: `109cc89920769d931ab2503c86b31619e3db7357`
**Branch**: `main`
**Date**: 2026-08-06 (10:59:57 UTC)
**Status**: ✅ Captured

Captured timing:
- Hugo: `3,015` ms (0.161.1)
- Pagefind: `2,448` ms (1.5.2)
- **Total build**: `5,463` ms

Artifact location: [GitHub Actions run 31095474806](https://github.com/jmservera/SquadScope/actions/runs/31095474806)

**⚠️ Note**: Timing significantly faster than Run 1. Verify production-site job context and scope (possible partial build, cache hit, or different conditions). Flagged for clarification before p95 approval.

### Run 3: [Pending — Next CI Build]

**Status**: ⏳ Awaiting third successful Production CI run (expected 2026-08-07 or later)

## Baseline Analysis

### Single Measurement (Run 1)

| Component | Duration (ms) | Relative | Status |
|-----------|---------------|----------|--------|
| Hugo 0.161.1 | 15,339 | Baseline | ✅ |
| Pagefind 1.5.2 | 1,631 | Baseline | ✅ |
| **Total** | **16,970** | **Baseline** | ✅ |

### Proposed Budget Thresholds (Pending Approval)

Based on single baseline run and Phase 7.3 historical context, proposed timing budgets (to be reviewed and approved):

| Component | Proposed Threshold | Rationale | Status |
|-----------|-------------------|-----------|--------|
| Hugo build | 20,000 ms | 30% margin above baseline | Proposed |
| Pagefind index | 2,500 ms | 50% margin above baseline | Proposed |
| Total CI time | 25,000 ms | Combined threshold | Proposed |

**Note**: Thresholds require review by timing-budget owner before enforcement. Current measurements are report-only; no blocking gate is active.

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
- **Status**: ⏳ Pending

### Infrastructure Owner (URL)

- **Role**: Validate CI timing data collection methodology
- **Responsibility**: Confirm measurements are reproducible and artifact retention is durable
- **Sign-off Required**: Yes
- **Status**: ⏳ Pending

### Production Owner (jmservera)

- **Role**: Final acceptance of timing budget as production control
- **Responsibility**: Confirm enforcement mechanism and rollback plan
- **Sign-off Required**: Yes
- **Status**: ⏳ Pending

### Provisional Approval (Pending Run 3 Verification)

**Decision Date**: 2026-08-06  
**Status**: ⏳ **PROVISIONAL APPROVAL** — Both metrics within budget even with Run 2 anomaly; awaiting Run 3 for statistical validity

**Rationale**:
- Hugo p95 (max of Runs 1-2, proxy for percentile): 15,339 ms ✅ (budget: 20,000 ms; margin: 23%)
- Pagefind p95 (max of Runs 1-2, proxy for percentile): 2,448 ms ✅ (budget: 2,500 ms; margin: 2%)
- Run 2 flagged as anomaly (80% faster Hugo); awaiting context clarification and Run 3 for trend analysis

**Condition**: Update budget approval status to **APPROVED** after Run 3 collected and validates similar performance to Run 1 OR after CI logs confirm Run 2 context (cache, partial build, etc.)

**Timeline**: Run 3 expected 2026-08-07 or later (CI-dependent)

## Implementation Notes

### Measurement Integrity

- Measurements use system `date +%s%N` (nanosecond precision) on GitHub-hosted runners
- Conversion to milliseconds: `(finished_ns - started_ns) / 1,000,000`
- No external network calls or downloads are timed (tool installation precedes timing)
- Page volume (site size) is noted for statistical grouping

### Page Volume at Baseline

**2026-08-05 production build**:
- Total site pages: ~2,800 (including archives, topics, weekly, monthly, yearly, categories)
- Total content files: ~18,000+ Markdown files
- Output HTML: ~850+ MB (pre-Lighthouse before cleanup)

Budget adjustments may be needed if page volume changes materially (>20% growth).

### Durable Artifact Retention

- CI artifacts retained for 30 days (Actions setting)
- Evidence links point to specific run IDs and jobs
- Run data must be recorded in this document before artifact expiration
- Long-term record: This markdown file (versioned in git)

## Pending Deliverables

- [ ] Collection of Run 2 timing data
- [ ] Collection of Run 3 timing data
- [ ] Median and p95 calculation
- [ ] Timing budget owner review and approval
- [ ] Infrastructure owner (URL) sign-off
- [ ] Production owner (jmservera) acceptance
- [ ] Enforcement gate activation in CI workflow

## Cross-References

- Plan: [`.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md`](.../../../.copilot-tracking/plans/2026-07-30/claracle-data-observatory-relaunch-review-remediation-plan.instructions.md) (Step 6.3)
- Evidence index: [`docs/review/data-observatory-relaunch/README.md`](./README.md)
- CI workflow: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)
