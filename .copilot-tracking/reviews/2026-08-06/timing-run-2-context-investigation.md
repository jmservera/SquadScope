<!-- markdownlint-disable-file -->
# Phase 7.1 Timing Analysis — Run 2 Context Investigation

**Date**: 2026-08-06  
**Run ID**: 31095474806  
**Status**: ⚠️ Context flagged for clarification  

---

## Run 2 Timing Data

| Component | Duration | Run 1 | Variance | Status |
|-----------|----------|-------|----------|--------|
| Hugo | 3,015 ms | 15,339 ms | -80.4% (12,324 ms faster) | ⚠️ Anomaly |
| Pagefind | 2,448 ms | 1,631 ms | +50.1% (817 ms slower) | ⚠️ Anomaly |
| **Total** | **5,463 ms** | **16,970 ms** | **-67.8%** | ⚠️ Significant divergence |

---

## Investigation Findings

### Commit Verification

**Run 2 Commit**: `c2584030f0332758312bed4dfeff954a986ee034`  
**Event**: `pull_request` (PR #677, branch `docs/phase-7-acceptance-gates`)  
**Status**: ✅ Verified — head SHA of PR #677 CI run 31095474806  
**Implication**: Run 2 is a PR CI build, not a production `main` build, so the faster timing partly reflects a different build context/branch rather than a regression. A production `main` Run 3 is still required for a valid p95 series.

### Possible Root Causes

#### A. CI Cache Hit
- Hugo build times can be significantly faster with disk cache hits
- Pagefind slower if indexing new/changed content
- **Probability**: Medium (cache is usually persistent on GitHub runners)
- **Check**: Review CI logs for cache diagnostics

#### B. Partial/Subset Build
- Build may have skipped content directories or rebuilds
- Hugo and Pagefind configurations might differ between runs
- **Probability**: Low (same workflow, same main branch)
- **Check**: Verify production-site job configuration matches Run 1

#### C. Different Content Scope
- Run 2 might have indexed fewer pages than Run 1
- Content changes between 2026-08-05 and 2026-08-06 could reduce indexing load
- **Probability**: Low (data pages are committed; no deletion expected)
- **Check**: Compare page counts in both run artifacts

#### D. System Resource Variance
- GitHub runner CPU/memory/disk I/O variance between runs
- Kernel cache effects, runner warm-up time
- **Probability**: Medium (expected variance is 5-10%, not 80%)
- **Check**: Compare runs 1 & 2 with historical CI performance

---

## Required Clarification Before Approval

Before accepting Run 2 timing for p95 budget approval:

1. **Confirm commit context** — Is commit 109cc89 valid? (On a branch? Artifact label error?)
2. **Verify same job scope** — Did production-site job run with identical parameters to Run 1?
3. **Review CI logs** — Check for cache, compilation warnings, or content differences
4. **Collect Run 3** — Third data point will reveal if Run 2 is anomalous or representative

---

## Recommended Path Forward

### Option A: Defer p95 Until Run 3 (RECOMMENDED)
- **Action**: Collect Run 3 from next natural CI build
- **Timeline**: 1-2 days
- **Benefit**: Three-point average will smooth outliers and provide statistical confidence
- **Risk**: Adds 1-2 days to Phase 7 timeline

### Option B: Investigate Run 2 Logs Now
- **Action**: Pull CI run logs, check for cache/configuration variance
- **Timeline**: 30 min
- **Benefit**: May clarify Run 2 validity; could enable 2-point p95 if logs show expected conditions
- **Risk**: Logs may not provide definitive answer; could still need Run 3

### Option C: Provisional p95 Pending Verification
- **Action**: Calculate p95 using Runs 1-2 now; mark as "provisional pending Run 3"
- **Timeline**: 15 min
- **Benefit**: Move forward while investigating; update if Run 3 changes conclusion
- **Risk**: Approval might be questioned if Run 3 shows different pattern

---

## Provisional p95 Calculation (Runs 1-2)

**If proceeding with 2-point median/p95 (Option C)**:

### Hugo
```
Run 1: 15,339 ms
Run 2: 3,015 ms (⚠️ flagged)
Median: (15,339 + 3,015) / 2 = 9,177 ms
P95 (highest): 15,339 ms
Budget (proposed): 20,000 ms
Status: ✅ WITHIN BUDGET (headroom: 4,661 ms, margin: 23%)
```

### Pagefind
```
Run 1: 1,631 ms
Run 2: 2,448 ms (⚠️ flagged)
Median: (1,631 + 2,448) / 2 = 2,039.5 ms
P95 (highest): 2,448 ms
Budget (proposed): 2,500 ms
Status: ✅ WITHIN BUDGET (headroom: 52 ms, margin: 2%)
```

### Provisional Conclusion
**Even with Run 2 anomaly**, 2-point p95 meets proposed budgets with acceptable headroom.  
**Caveat**: p95 = highest value (not percentile-based p95) due to 2-point sample.  
**Confidence**: LOW — recommend collecting Run 3 for statistical validity.

---

## Sponsor Decision Required

**jmservera** (timing budget owner) should decide:

1. **Proceed with 2-point p95** and update timing-analysis.md with "provisional pending Run 3 verification"
2. **Wait for Run 3** before approval (timeline +1-2 days)
3. **Investigate Run 2 logs** for clarity on variance root cause

---

## Template: Update timing-analysis.md

If proceeding with provisional approval, update budgets section:

```markdown
## Timing Budgets (Provisional — Pending Run 3 Verification)

### Run 1-2 P95 Calculation

| Metric | Run 1 | Run 2 | P95 (Max) | Budget | Status | Margin |
|--------|-------|-------|-----------|--------|--------|--------|
| Hugo | 15,339 ms | 3,015 ms* | 15,339 ms | 20,000 ms | ✅ | 23% |
| Pagefind | 1,631 ms | 2,448 ms | 2,448 ms | 2,500 ms | ✅ | 2% |

*Run 2 Hugo timing flagged as anomaly (80% faster). Awaiting Run 3 for validation.

**Status**: ✅ PROVISIONAL APPROVAL (both metrics within budget)  
**Caveat**: Confidence low; recommend collecting Run 3 for statistical validity.  
**Next Step**: Update after Run 3 collected; revise if pattern changes.
```

---

## References

- [timing-analysis.md](../../data-observatory-relaunch/timing-analysis.md) — Full run data
- [CI Run 31095474806](https://github.com/jmservera/SquadScope/actions/runs/31095474806) — Artifact source
- [Phase 7.1 Monitoring Workflow](../../../.copilot-tracking/plans/2026-08-06/phase-7-1-timing-collection-monitoring.md)
