<!-- markdownlint-disable-file -->
# Phase 7.3 Item 2: Visual Baseline Trigger — Execution Blocked (Awaiting PR Merge)

**Date**: 2026-08-06  
**Status**: ⏳ **BLOCKED** — Awaiting PR #677 merge to main  
**Item**: Phase 5 Suggested Work Item 2  

---

## Execution Attempt

**Timestamp**: 2026-08-06 ~11:35 UTC  
**Attempted Action**: Manual workflow trigger via `gh workflow run ci.yml --ref main`  
**Result**: ❌ FAILED

**Error**:
```
could not create workflow dispatch event: HTTP 422: Workflow does not have 'workflow_dispatch' trigger
```

**Root Cause**: `.github/workflows/ci.yml` does not have `workflow_dispatch` configured. CI workflow only triggers on:
- `push` to main branch
- `pull_request` events (PR to main)

---

## Blocking Dependency

### CI Workflow Trigger Configuration
```yaml
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
```

**Analysis**: No `workflow_dispatch` entry in trigger configuration.

**Impact**: Cannot manually trigger CI; only automatic triggers available.

---

## Required Unblock

**Prerequisite**: PR #677 must be merged to main branch

**When Merged**:
1. GitHub automatically triggers CI workflow on `push` event
2. Production site CI job runs (includes visual regression test)
3. Baseline capture executes automatically (~30-45 min from CI start)
4. Artifacts available in GitHub Actions > CI > production-quality-reports/

**Timeline**:
- **Merge Time**: Immediate (jmservera approval + merge decision)
- **CI Execution**: Automatic upon merge (< 1 min after merge)
- **Baseline Completion**: ~30-45 min from CI start
- **Expected Completion**: 2026-08-06 ~12:15-12:30 UTC (if merged now)

---

## Decision Path

### Option A: Merge PR #677 Now (RECOMMENDED)
- **Action**: Execute merge (jmservera decision)
- **Timeline**: Immediate
- **Next Step**: Monitor CI for baseline completion
- **Owner**: jmservera or any repo maintainer

### Option B: Wait for Additional Changes
- **Rationale**: If additional docs need to be added to PR #677
- **Timeline**: +N hours per change batch
- **Impact**: Delays Phase 7.3 baseline by N hours

### Option C: Add workflow_dispatch Trigger to CI
- **Action**: Modify `.github/workflows/ci.yml` to add `workflow_dispatch`
- **Timeline**: +5-10 min for change + CI execution
- **Risk**: Introduces manual trigger capability (may not be desired for current workflow)
- **Recommendation**: Not recommended unless broader workflow changes planned

---

## Recommended Action

**Proceed with Option A (Merge PR #677)**

**Rationale**:
1. PR #677 CI checks nearly complete (Checkov + Production site job in progress)
2. No blockers identified in review
3. Phase 7 documentation comprehensive and ready
4. Phase 7.3 infrastructure ready for baseline capture
5. Only 1-2 minute delay awaiting final CI checks to complete
6. Merge enables automatic baseline capture without additional changes

**Next Workflow**:
1. ✅ jmservera approves and merges PR #677 to main (~5 min)
2. ✅ GitHub Actions automatically triggers CI on `push` (~1 min)
3. ⏳ Production site job executes (includes visual regression test) (~30-45 min)
4. ✅ Baseline snapshots captured in `tests/visual/snapshots/` (162 total)
5. ✅ Artifacts available in CI run (30-day retention)
6. ✅ Create visual-evidence.md for Amy/Fry review (post-baseline)

---

## Item 2 Status Summary

| Status | Metric |
|--------|--------|
| **Phase 7.3 Item 2 Execution** | ⏳ Blocked |
| **Blocking Condition** | PR #677 not yet merged to main |
| **Prerequisites Met** | ✅ Yes (all docs ready, CI nearly complete) |
| **Estimated Unblock Time** | 1-2 minutes (after PR merge) |
| **Estimated Baseline Completion** | 30-45 min after merge (~12:15 UTC if merged now) |
| **Owner Decision Required** | jmservera (merge approval) |
| **Can Proceed Without Decision** | No (merge is hard requirement) |

---

## References

- PR #677 Merge Readiness: `.copilot-tracking/reviews/2026-08-06/pr-677-merge-readiness.md`
- CI Workflow: `.github/workflows/ci.yml`
- Visual Test: `tests/visual/observatory-visual-regression.spec.mjs`
- Phase 7.3 Workflow: `.copilot-tracking/plans/2026-08-06/phase-7-3-visual-baseline-capture-workflow.md`

---

**Status**: ✅ **READY FOR MERGE DECISION** — All prerequis prerequisites met; awaiting jmservera merge approval.
