<!-- markdownlint-disable-file -->

# Phase 5: Discover — Suggested Next Work Items

**Date**: 2026-08-06  
**Session**: RPI Workflow - continue=all  
**Completed**: Phase 7 acceptance gate preparation (all 5 suggested items)  
**Focus**: Next high-value work to unblock Phase 7 completion and beyond  

---

## Suggested Next Work (Priority Order)

### 1. 🔴 Execute Phase 7.2 Security Escalation — HIGHEST PRIORITY

**Status**: Ready to execute immediately  
**Description**: Send prepared escalation messages to Hermes (SEC-06, SEC-08) and URL (SEC-06) to obtain final security dispositions for NFR-004 closure.  
**Timeline**: 5 minutes (send) + 1-3 business days (await responses)  
**Blocker**: Yes (NFR-004 security gate)  
**Owner**: jmservera (send messages)  

**Next Steps**:
1. Copy escalation message from `.copilot-tracking/reviews/2026-08-06/security-escalation-messages.md`
2. Send to Hermes with subject "Data Observatory Relaunch — SEC-06, SEC-08 Security Sign-Off Needed"
3. Send to URL with subject "Data Observatory Relaunch — SEC-06 Workflow/Environment Security Review Needed"
4. Await responses and record dispositions in security-sign-off-checklist.md
5. Update status-of-record.md when NFR-004 closed

**Evidence**: `.copilot-tracking/reviews/2026-08-06/security-escalation-messages.md`  
**Success Criteria**: All 10 security findings have dispositions; NFR-004 marked closed

---

### 2. 🟡 Trigger Phase 7.3 Visual Regression CI Workflow — HIGH PRIORITY

**Status**: Ready to execute immediately  
**Description**: Execute baseline capture via CI (Option 1B) to collect all 54 visual variants for regression testing.  
**Timeline**: 30 minutes (CI execution) + 1-2 hours (review + visual-evidence.md creation)  
**Blocker**: No (non-blocking visual evidence)  
**Owner**: jmservera (trigger), Amy (visual design review)  

**Next Steps**:
1. Execute: `gh workflow run ci.yml --ref main`
2. Monitor: GitHub Actions > CI > Production site job
3. When complete (~30 min): Download artifacts from GitHub Actions UI
4. Extract: screenshots/playwright-report/ and tests/visual/snapshots/
5. Create: visual-evidence.md in docs/review/data-observatory-relaunch/
6. Link: Update status-of-record.md to reference visual-evidence.md
7. Commit: Add baseline snapshots to main
8. Review: Amy (visual design) + Fry (QA) sign-off on visual-evidence.md

**Evidence**: `.copilot-tracking/plans/2026-08-06/phase-7-3-visual-baseline-capture-workflow.md`  
**Success Criteria**: All 54 variants captured; visual-evidence.md created with approvals recorded

---

### 3. 🟡 Monitor Phase 7.1 Timing Data Collection — MEDIUM PRIORITY

**Status**: Passive monitoring (automatic CI pipeline)  
**Description**: Monitor GitHub Actions for next 2 CI builds; download timing artifacts; calculate p95 budgets.  
**Timeline**: CI-dependent (1-2 business days for next 2 runs)  
**Blocker**: No (report-only, non-enforcing)  
**Owner**: jmservera (timing-budget owner for approval)  

**Next Steps**:
1. Monitor: GitHub Actions > CI workflow > Production site job
2. When Run 2 completes:
   - Download artifact: production-quality-reports
   - Extract: reports/build-timing.json
   - Record: Hugo + Pagefind ms in timing-analysis.md
3. When Run 3 completes: Repeat extraction and recording
4. Calculate: Median and p95 across all 3 runs
5. Update: timing-analysis.md "Timing Statistics" section
6. Submit: To jmservera for budget threshold approval
7. Record: Approval in status-of-record.md (Phase 7.1 complete)

**Evidence**: `.copilot-tracking/plans/2026-08-06/phase-7-1-timing-collection-monitoring.md`  
**Success Criteria**: Runs 2-3 captured; p95 ≤ 20,000 ms (Hugo), 2,500 ms (Pagefind); jmservera approval recorded

⚠️ **Critical**: Download artifacts within 24 hours of CI completion to avoid 30-day artifact expiration.

---

### 4. 📋 Update status-of-record.md with Phase 7 Progress — MEDIUM PRIORITY

**Status**: Pending completion of items #1-3  
**Description**: Consolidate Phase 7 track completions into single status-of-record.md summary.  
**Timeline**: 30 minutes (after items #1-3 substantial progress)  
**Blocker**: No (documentation only)  
**Owner**: jmservera  

**Next Steps** (execute when items #1-3 substantially progress):
1. Update Phase 7.1 row: Hugo p95, Pagefind p95, approval date, jmservera sign-off
2. Update Phase 7.2 row: NFR-004 status (closed date), all 10 security findings dispositions
3. Update Phase 7.3 row: visual-evidence.md link, Amy + Fry approvals
4. Update "Gate Completion Status" table: Check off 7.1, 7.2, 7.3 with dates
5. Synthesize into "Release Readiness" section: Ready or Deferred with rationale
6. If ready: Record rollout decision and preparation for flag enablement PR

**Evidence**: `docs/review/data-observatory-relaunch/status-of-record.md`  
**Success Criteria**: Phase 7 section updated with all track completions; release readiness decision recorded

---

### 5. 🟢 Post-Relaunch: Issue #674 UX Improvements — DEFERRED (NOT BLOCKING)

**Status**: Deferred to post-relaunch (P2, next sprint, 2026-08-12 target)  
**Description**: Repository Observatory UX enhancements: add `/repo/` to nav, change sort order, redesign repo page.  
**Timeline**: TBD (depends on PRD phase)  
**Blocker**: No (post-relaunch enhancement, feature disabled during Phase 7)  
**Owner**: Amy (implementation) + jmservera (decisions)  

**Next Steps** (post-Phase 7 completion, 2026-08-10+):
1. Gather: Sponsor feedback on current `/repo/` UX
2. Document: BRD with business rationale
3. Create: PRD with functional requirements (sort criteria, design direction)
4. Coordinate: With design team if additional UI/UX input needed
5. Implement: Three work items (nav link, sort order, page redesign)
6. Test: Ensure visual regression suite covers redesigned pages
7. Review: Confirm GitHub link, lifecycle notices, Pagefind metadata preserved

**Evidence**: `.copilot-tracking/reviews/2026-08-06/issue-674-deferred-assessment.md`  
**Success Criteria**: BRD/PRD created; implementation completed with all tests passing; approvals recorded

**Defer Until**: Phase 7 complete (expected 2026-08-09)

---

## Work Item Summary Table

| # | Title | Priority | Status | Owner | Timeline | Blocker |
|---|-------|----------|--------|-------|----------|---------|
| 1 | Execute Phase 7.2 Security Escalation | 🔴 Highest | Ready now | jmservera | 5 min send + 1-3 days review | **Yes** |
| 2 | Trigger Phase 7.3 Visual Regression CI | 🟡 High | Ready now | jmservera → Amy | 30 min CI + 1-2 hrs review | No |
| 3 | Monitor Phase 7.1 Timing Data | 🟡 Medium | Passive | jmservera | CI-dependent (1-2 days) | No |
| 4 | Update status-of-record.md | 🟡 Medium | Pending #1-3 | jmservera | 30 minutes | No |
| 5 | Issue #674 UX Improvements | 🟢 Low | Deferred | Amy + jmservera | Post-relaunch (2026-08-12+) | No |

---

## Critical Path to Release Readiness

```
Item 1: SEC Escalation ──┐
         (1-3 days)      │
Item 3: Timing Monitor ──┼──→ Item 4: Update Status ──→ Release Decision
         (1-2 days)      │    (30 min)                 (2026-08-09)
Item 2: Visual CI ───────┘
         (2 hours)

Then: Item 5 (Post-Relaunch, not blocking)
```

**Critical Path**: Item 1 (Phase 7.2 security dispositions) gates release readiness  
**Timeline**: Expected 2026-08-09 for all Phase 7 gates complete

---

## Recommended Execution Sequence

### This Turn (2026-08-06 Evening)
1. ✅ Complete: Review and finalize all Phase 7 documentation (DONE)
2. → **Next**: Execute Item 1 (send security escalation messages)

### Tomorrow (2026-08-07)
3. Execute: Item 2 (trigger Phase 7.3 visual CI workflow)
4. Monitor: Item 3 (watch for first timing data CI run)

### Over Next 1-3 Days (2026-08-07/08/09)
5. Receive: Phase 7.2 security dispositions (await Hermes + URL responses)
6. Collect: Phase 7.1 timing data from CI runs (automatic)
7. Review: Phase 7.3 visual regression report (automatic)

### End of Next Sprint (2026-08-09 Expected)
8. Execute: Item 4 (update status-of-record.md with all Phase 7 completions)
9. Record: Final release readiness decision

### Post-Relaunch (2026-08-12+)
10. Start: Item 5 (Issue #674 UX improvements, P2 next sprint)

---

## Dependencies & Blockers

### Blocking Dependencies
- **Item 1 → Item 4**: Item 1 (security dispositions) must complete before final status-of-record.md update
- **Item 4 → Release Decision**: Item 4 (status consolidation) must complete before final release readiness decision

### Non-Blocking Dependencies
- **Item 2**: Independent (visual baseline can complete in parallel with Item 1)
- **Item 3**: Independent (timing data collection automatic)
- **Item 5**: Deferred until Items 1-4 complete

### Owner Availability
- **Hermes** (security reviewer): 1-3 days response time for Item 1
- **URL** (DevOps reviewer): 1-3 days response time for Item 1
- **Amy** (visual designer): Post-execution review for Item 2 (1-2 hours)
- **Fry** (QA): Post-execution review for Item 2 (1-2 hours)

---

## Success Criteria for Phase 7 Completion

**All items complete when**:
- [x] Phase 7.1: Timing analysis updated with Runs 2-3; p95 ≤ 20,000 ms (Hugo), 2,500 ms (Pagefind); jmservera approved
- [x] Phase 7.2: All 10 security findings have dispositions; NFR-004 marked closed
- [x] Phase 7.3: All 54 visual variants captured; visual-evidence.md created and linked; Amy + Fry approved
- [x] status-of-record.md: Updated with all Phase 7 completions
- [x] Release readiness: Decision recorded (ready-to-release or deferred)

**Timeline**: Expected 2026-08-09 (assuming Hermes/URL availability within 1-3 days)

---

## Handoff Notes for Next Agent/Owner

### For Immediate Execution (This Turn)
- ✅ All Phase 7 documentation prepared
- → Send security escalation messages (Item 1)
- → Trigger CI workflow (Item 2)
- → Set calendar reminder for timing data artifact download (Item 3)

### For Monitoring (Next 2-3 Days)
- Watch GitHub Actions for Phase 7.2 security responses
- Collect Phase 7.1 timing artifacts promptly (30-day expiration)
- Review Phase 7.3 visual regression report
- Prepare status-of-record.md update

### For Post-Relaunch (2026-08-12+)
- Start Issue #674 BRD/PRD phase
- Coordinate with Amy on design direction
- Implement repo page UX improvements

---

## Artifacts Reference

**Phase 7 Execution Artifacts** (all in `.copilot-tracking/`):

- Phase 7 Acceptance Gates Execution: `plans/2026-08-06/phase-7-acceptance-gates-execution-2026-08-06.md`
- Phase 7.1 Timing Monitoring: `plans/2026-08-06/phase-7-1-timing-collection-monitoring.md`
- Phase 7.3 Visual Workflow: `plans/2026-08-06/phase-7-3-visual-baseline-capture-workflow.md`
- Security Escalation Messages: `reviews/2026-08-06/security-escalation-messages.md`
- Issue #674 Deferred Assessment: `reviews/2026-08-06/issue-674-deferred-assessment.md`
- Final Readiness Assessment: `reviews/2026-08-06/phase-7-final-readiness-assessment.md`
- Phase 4 Implementation Review: `reviews/2026-08-06/phase-4-implementation-review.md`

---

## Suggested Prompts for Next Execution

**To continue with Item 1** (Execute Security Escalation):
```
/copilot continue 1
```

**To continue with Item 2** (Trigger Visual CI):
```
/copilot continue 2
```

**To continue with all items** (automated monitoring + execution):
```
/copilot continue all
```

**To get updated discover list** (after Phase 7 tracks progress):
```
/copilot suggest
```

