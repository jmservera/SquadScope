<!-- markdownlint-disable-file -->
# Phase 3: Implementation Details - Items 1-5 Execution

**Date**: 2026-08-06 15:45 UTC  
**Status**: Phase 3 in-progress - Awaiting Item 1 approval/merge

---

## Item 1: Merge PR #678 ✅ CREATED, ⏳ AWAITING APPROVAL

### PR Details
- **Number**: #678
- **Title**: docs(acceptance-gates): Phase 7 docs + Phase 1-2 planning for Items 1-5
- **URL**: https://github.com/jmservera/SquadScope/pull/678
- **Branch**: `docs/phase-7-plus-planning`
- **Commits**: 2 (Phase 7 docs + Phase 1-2 planning)
- **Files Changed**: 30+ files, ~5,200 lines

### Status
- [x] Phase 7 documentation complete (4,800+ lines)
- [x] Phase 1-2 planning documents complete
- [x] All PR comments resolved (6 original + 9 additional)
- [x] Branch created and pushed to origin
- [x] PR created and ready for review
- [ ] PR approved by another team member
- [ ] PR merged to main

### Next Action
**Awaiting**: External team member approval and merge

**Timeline**: 5-10 min from approval

---

## Item 2: Visual Baseline Capture (Blocked by Item 1)

### Status
- [x] Workflow documented in `visual-regression-execution-guide.md`
- [x] Test file ready: `tests/visual/observatory-visual-regression.spec.mjs`
- [x] CI configuration modified (visual test removed from main run for now)
- [ ] Item 1 merge to main (blocker)
- [ ] CI triggered on main post-merge
- [ ] Playwright test execution (45 min)
- [ ] Baselines captured (162 variants)

### Execution Steps (Once Item 1 merged)
1. GitHub automatically triggers CI on main
2. Monitor: GitHub Actions > CI workflow > Production site job
3. Wait: ~30-45 min for Playwright execution
4. Verify: Check `screenshots/playwright-report/index.html` for quality
5. Download: `gh run download [run-id] -n production-quality-reports`
6. Extract: Snapshots to `tests/visual/snapshots/`
7. Commit: `git add tests/visual/snapshots && git commit -m "feat(visual): baseline snapshots"`

### Timeline
- Blocked until: Item 1 merged
- Execution time: ~45 min
- Expected completion: ~1 hour post-Item-1 merge

---

## Item 3: Visual Evidence Review (Blocked by Item 2)

### Status
- [x] Template documented in execution plan
- [x] Target file identified: `docs/review/data-observatory-relaunch/visual-evidence.md`
- [x] Review scope defined (162 variants, 3 browsers, 2 themes, 9 routes)
- [ ] Item 2 baselines available
- [ ] Amy design review complete
- [ ] Fry QA approval complete
- [ ] Evidence document created and committed

### Execution Steps (Once Item 2 complete)
1. Download baseline snapshots from Item 2 CI artifacts
2. Amy reviews:
   - Color rendering accuracy
   - Spacing and typography
   - Responsive layout (3 viewports: 375px, 768px, 1440px)
   - Light/dark theme variants
   - Cross-browser consistency (Chromium, Firefox, WebKit)
3. Fry validates:
   - Render quality
   - Test infrastructure correctness
   - No critical rendering failures
4. Create `visual-evidence.md` with:
   - Baseline snapshots linked
   - Amy approval (date + signature)
   - Fry approval (date + signature)
   - Findings/regressions noted
5. Update `status-of-record.md` Phase 7.3 status
6. Commit: `git add docs/review && git commit -m "docs(visual-evidence): Phase 7.3 approved"`

### Timeline
- Blocked until: Item 2 complete
- Review time: ~1-2 hours
- Expected completion: ~3-4 hours post-Item-1 merge

---

## Item 4: Phase 7.1 Run 3 Monitoring (Passive, parallel)

### Status
- [x] Monitoring procedure documented
- [x] Timing data extraction script ready
- [ ] Item 1 merged (start monitoring)
- [ ] Run 3 CI execution on main
- [ ] Run 3 artifacts available (within 24-hour retention)
- [ ] Timing data collected and analyzed
- [ ] P95 calculated and documented
- [ ] jmservera approval recorded

### Execution Steps (Passive, during Items 2-3)
1. After Item 1 merges, GitHub triggers CI on main
2. Monitor GitHub Actions for Run 3 completion
3. When complete, download artifacts:
   ```bash
   gh run download [run-id] -n production-quality-reports
   ```
4. Extract timing data from `reports/build-timing.json`
5. Calculate statistics:
   - Hugo duration (p95 = max of 3 runs)
   - Pagefind duration (p95 = max of 3 runs)
   - Budget compliance: Hugo ≤ 20,000ms, Pagefind ≤ 2,500ms
   - Margin calculation
6. Update `timing-analysis.md` with Run 3 data
7. Determine status: APPROVED (if within budget) or FLAG (if anomaly)
8. Record jmservera sign-off with date

### Critical Constraint
⚠️ **Download within 24 hours of CI completion** (30-day retention policy)

### Timeline
- Starts: Immediately after Item 1 merge
- Run time: 1-2 business days for Run 3 to execute on main
- Parallel to Items 2-3 (no blocking dependency)
- Must complete: Before Item 5 decision

---

## Item 5: Phase 7 Final Release Decision (Blocked by Items 2-4)

### Status
- [x] Template documented in execution plan
- [x] Target file identified: `docs/review/data-observatory-relaunch/phase-7-final-release-decision.md`
- [ ] Item 2 visual evidence complete
- [ ] Item 3 design/QA approvals recorded
- [ ] Item 4 timing data and approval recorded
- [ ] Phase 7.2 security approval confirmed
- [ ] Decision document created and committed

### Execution Steps (Once Items 2-4 provide evidence)
1. Compile evidence:
   - Phase 7.1: timing-analysis.md (Item 4 approval)
   - Phase 7.2: security-sign-off-checklist.md (already approved 2026-08-06)
   - Phase 7.3: visual-evidence.md (Item 3 approvals)
2. Create `phase-7-final-release-decision.md`:
   - Gate status summary (7.1, 7.2, 7.3)
   - Evidence references (links to all 3 gate documents)
   - Release decision: GO or NO-GO with rationale
   - Timeline: Target 2026-08-08/09 go-live
   - jmservera signature + date
3. If GO: Prepare feature-flag rollout PR for controlled deployment
4. Commit: `git add docs/review && git commit -m "docs(release-decision): Phase 7 APPROVED"`

### Timeline
- Blocked until: Items 2-4 complete evidence collection
- Decision time: ~15 min
- Expected completion: ~4-5 hours post-Item-1 merge

---

## Critical Path Summary

```
START: Item 1 approval needed
  ↓ (5-10 min for approval + merge)
Item 1 merged to main
  ↓ (2 min for CI trigger)
Item 2: Visual baseline capture begins (45 min)
  ├→ [PARALLEL] Item 4: Run 3 monitoring begins (1-2 days, passive)
  ↓ (45 min)
Item 2 complete → baselines available
  ↓ (immediate)
Item 3: Visual evidence review (1-2 hours)
  ↓ (1-2 hours)
Item 3 complete → design/QA approvals recorded
  ↓ (immediate, when Item 4 also complete)
Item 5: Release decision (15 min)
  ↓ (15 min)
All Items 1-5 COMPLETE ✅
```

**Total Sequential Time**: ~2-3 hours (Item 1 → 2 → 3 → 5)  
**Total Parallel Time**: ~1-2 days (Item 4 runs concurrently)  
**Overall Completion**: 2-3 hours + 1-2 days = 2026-08-08/09 ✅

---

## Execution Triggers

| Trigger | Source | Action |
|---------|--------|--------|
| Item 1 approved | Team member | Merge PR #678 to main |
| Item 1 merged | GitHub | Auto-trigger CI on main |
| Item 2 complete | CI artifacts | Start Item 3 review |
| Item 3 complete | Amy + Fry signoff | Prepare Item 5 decision |
| Item 4 complete | CI Run 3 | Include in Item 5 evidence |
| Items 2-4 complete | All approvals | Execute Item 5 decision |

---

## Success Criteria

### Item 1
- [ ] PR #678 approved by team member
- [ ] PR merged to main (squash merge)
- [ ] Commit appears on origin/main

### Item 2
- [ ] CI triggered on main post-merge
- [ ] Playwright test execution completes (45 min)
- [ ] 162 visual baselines generated
- [ ] Playwright report shows no critical errors
- [ ] `tests/visual/snapshots/` committed to main

### Item 3
- [ ] Amy completes design review (all variants approved)
- [ ] Fry completes QA validation (no critical rendering issues)
- [ ] `visual-evidence.md` created with approvals
- [ ] `status-of-record.md` Phase 7.3 marked complete
- [ ] Commit pushed to main

### Item 4
- [ ] Run 3 timing data collected (within 24-hour window)
- [ ] Hugo p95 ≤ 20,000ms, Pagefind p95 ≤ 2,500ms
- [ ] `timing-analysis.md` updated with Run 3 and jmservera approval
- [ ] Approval recorded with date

### Item 5
- [ ] `phase-7-final-release-decision.md` created
- [ ] All 3 gate evidence linked (7.1, 7.2, 7.3)
- [ ] Release decision: GO or NO-GO with rationale
- [ ] jmservera signature + date recorded
- [ ] Commit pushed to main

---

## Phase 3 Status Log

**2026-08-06 15:45 UTC**
- ✅ Phase 1-2 research and planning complete
- ✅ PR #678 created (link: https://github.com/jmservera/SquadScope/pull/678)
- ⏳ Awaiting Item 1 approval/merge from team member
- ⏳ Items 2-5 ready to execute in sequence/parallel once Item 1 completes

**Next Status Update**: When Item 1 merge detected or team member approval received
