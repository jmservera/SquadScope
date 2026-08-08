<!-- markdownlint-disable-file -->
# Phase 2 Plan: Items 1-5 Execution Sequence

> **STATUS — CLOSED 2026-08-08.** The PR #677 merge blocker is long resolved and Items 2-5
> (visual capture/review, timing monitoring, release decision) are superseded by the Phase 7
> dispositions; the remaining named-review and GO/NO-GO items are migrated to
> [BRD-CLARACLE-003 §3](../../../docs/brds/claracle-post-relaunch-consolidation-brd.md#3-carried-over-requirements-remaining-relaunch-work) (CR-02/CR-03). Do not resume here.

**Date**: 2026-08-06 15:20 UTC  
**Status**: Plan created; decision required before Phase 3 execution  

---

## User Requests (From continue=all)

- ✅ "fix all PR comments" → Completed (all 6 original + 9 additional comments fixed)
- ✅ "continue with all" → Items 1-5 execution planned

---

## Execution Approach

**Critical Blocker**: PR #677 merge requires external approval due to repository rule.

**Decision Required**: 
1. **Option A (Recommended)**: Get team approval for PR #677 merge → execute Items 1-5 normally
2. **Option B**: Document blocker and defer Items 1-5 to next session when approval obtained

**This Plan Assumes Option A**: Proceeding with execution sequence that awaits approval.

---

## Phase 2 Execution Checklist

### ✅ Completed Pre-Work (Prior Sessions)
- [x] Phase 7 documentation created (4,800+ lines)
- [x] All PR #677 review comments resolved
- [x] Local main branch merged with documentation
- [x] Commits ready for push (blocked by merge rule)

### 🔴 **DECISION POINT**: Item 1 Approval Required

**Action Required From User**:
```
Get approval for PR #677 from another team member:
1. Visit: https://github.com/jmservera/SquadScope/pull/677
2. Ask reviewer to click "Approve"
3. Ask reviewer to click "Merge pull request" → "Squash and merge"
```

**Estimated Time to Approval**: 5-10 minutes

---

## Items 1-5 Execution Plan (Post-Approval)

### Item 1: Merge PR #677 ✅ (Content Ready)

**Status**: Awaiting external approval  
**Work**: Already complete (local commit `64f29d7`)  
**Blockers**: Repository merge rule (non-technical)

**Phase 3 Step**:
1. Another team member approves PR #677
2. GitHub merges squash commit to main
3. CI automatically triggers on main

**Success Criteria**: Commit `64f29d7` appears on origin/main

**Timeline**: ~5 min (approval + merge) + ~2 min (CI trigger)

---

### Item 2: Visual Baseline Capture (45 min post-Item-1)

**Status**: Ready for execution  
**Owner**: jmservera (trigger), CI (execution)

**Phase 3 Steps**:
1. Verify CI triggered on main (automatic post-merge)
2. Monitor GitHub Actions > CI workflow > Production site job
3. Wait for Playwright test execution (~30-45 min)
4. When complete: CI uploads production-quality-reports artifact
5. Download: `gh run download [run-id] -n production-quality-reports`
6. Extract: Baseline snapshots from `tests/visual/snapshots/`
7. Review: Check `screenshots/playwright-report/index.html` for render quality
8. Commit: `git add tests/visual/snapshots && git commit -m "feat(visual): baseline snapshots"`

**Success Criteria**: 
- 162 visual snapshots generated (9 routes × 3 viewports × 2 themes × 3 browsers)
- No rendering errors in playwright report
- Baseline files committed to main

**Timeline**: ~45 min CI execution

---

### Item 3: Visual Evidence Documentation (1-2 hrs post-Item-2)

**Status**: Ready for execution  
**Owner**: Amy (design review), Fry (QA sign-off), jmservera (documentation)

**Phase 3 Steps**:
1. Download & extract baseline snapshots from Item 2
2. Amy reviews visual variants against design specification
   - Check color rendering, spacing, typography, responsive layout
   - Verify light/dark theme variants
   - Confirm all 3 browsers (Chromium, Firefox, WebKit) render correctly
3. Fry validates render quality and test infrastructure
4. Create `docs/review/data-observatory-relaunch/visual-evidence.md`
   - Link baseline snapshots
   - Include design approval with date + Amy signature
   - Include QA approval with date + Fry signature
   - Record any regressions or rendering issues
5. Update `docs/review/data-observatory-relaunch/status-of-record.md`
   - Phase 7.3 row: Mark ✅ complete
   - Link to visual-evidence.md
   - Record Amy + Fry approval dates
6. Commit: `git add docs/review && git commit -m "docs(visual-evidence): Phase 7.3 baseline capture approved"`

**Success Criteria**:
- visual-evidence.md created and committed to main
- Amy + Fry approvals recorded with signatures/dates
- All 162 variants reviewed without critical rendering issues

**Timeline**: ~1-2 hours (review) after Item 2 completes

---

### Item 4: Monitor Phase 7.1 Run 3 (Passive, 1-2 days)

**Status**: Ready for passive monitoring  
**Owner**: jmservera (monitoring)

**Phase 3 Steps** (execute in parallel with Items 2-3):
1. Monitor GitHub Actions for CI runs on main
2. When Run 3 completes on main:
   - Download artifact: `gh run download [run-id] -n production-quality-reports`
   - Extract: `reports/build-timing.json`
   - Parse Hugo duration + Pagefind duration
   - Record in `docs/review/data-observatory-relaunch/timing-analysis.md`
3. When 3 data points collected, calculate statistics:
   - P95 (max of 3 runs): Hugo, Pagefind
   - Compare vs. budget: Hugo ≤ 20,000ms, Pagefind ≤ 2,500ms
   - Margin: Calculate percentage headroom
4. Determine provisional vs. approved status:
   - If p95 within budget: ✅ APPROVED
   - If anomaly detected: Flag + await Run 4 for trend validation
5. Update timing-analysis.md "Approval Status" section
6. Document jmservera sign-off with date

**Success Criteria**:
- Runs 1-3 timing data collected
- P95 calculated and documented
- Budget thresholds met (Hugo ≤ 20,000ms, Pagefind ≤ 2,500ms)
- jmservera approval recorded

⚠️ **Critical Constraint**: Download artifact within 24 hours of CI completion (30-day retention)

**Timeline**: 1-2 business days (parallel to Items 2-3, starting post-Item-1 merge)

---

### Item 5: Phase 7 Release Decision (15 min post-Items-2-4)

**Status**: Ready for execution  
**Owner**: jmservera (decision authority)

**Phase 3 Steps** (execute when Items 2, 3, 4 provide evidence):
1. Review Phase 7.1 evidence: timing-analysis.md (Item 4 approval)
2. Review Phase 7.2 evidence: security-sign-off-checklist.md (already approved 2026-08-06)
3. Review Phase 7.3 evidence: visual-evidence.md (Item 3 approvals)
4. Create `docs/review/data-observatory-relaunch/phase-7-final-release-decision.md`
   - Gate status summary (7.1, 7.2, 7.3)
   - Evidence references
   - Release decision: GO or NO-GO
   - Rationale + date
   - jmservera signature
5. If GO: Add flag to next feature-flag PR for controlled rollout
6. Commit: `git add docs/review && git commit -m "docs(release-decision): Phase 7 acceptance gates APPROVED"`

**Success Criteria**:
- All 3 gates have approvals recorded
- phase-7-final-release-decision.md created and committed to main
- jmservera release decision signed and dated
- Readiness status: APPROVED or DEFERRED with clear rationale

**Timeline**: 15 min (once Items 2-4 evidence collected)

---

## Sequential vs. Parallel Execution

```
CRITICAL PATH (Sequential - must complete in order):
Item 1: PR merge (awaits approval) ← START HERE
    ↓ (2 min for CI trigger)
Item 2: Visual baseline capture (45 min)
    ↓ (immediate upon completion)
Item 3: Visual evidence review (1-2 hours)
    ↓ (immediate upon completion)  
Item 5: Release decision (15 min)

PARALLEL TRACK (Can run simultaneously):
Item 4: Monitor Phase 7.1 Run 3 (1-2 days, passive)
        ↑ (starts after Item 1 merge, runs in background)
```

---

## Timeline Summary

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Item 1 Approval | 5-10 min | External |
| Item 1 Merge | 2 min | Item 1 approval |
| Item 2 Execution | 45 min | Item 1 complete |
| Item 3 Execution | 1-2 hours | Item 2 complete |
| Item 5 Execution | 15 min | Items 3-4 complete |
| Item 4 Monitoring | 1-2 days | Starts after Item 1, parallel |

**Total Sequence Time (Items 1-5)**: ~2-3 hours + 1-2 days (Item 4 passive)  
**Expected Completion**: 2026-08-08/09

---

## Decision Required Before Phase 3

**Must resolve this before proceeding**:

Option A: **Get External Approval (Recommended)**
- Action: Contact team member to approve/merge PR #677
- Timeline: 5-10 min
- Result: Items 1-5 proceed as planned

Option B: **Defer Execution**
- Action: Document blocker; revisit when approval available
- Timeline: When approval obtained
- Result: Items 1-5 deferred

**Which option shall we proceed with?**
