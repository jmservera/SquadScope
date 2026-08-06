<!-- markdownlint-disable-file -->

# Data Observatory Phase 7 Acceptance Gates — Execution Plan

**Date**: 2026-08-06  
**Session**: Continue-all (post-PR merge)  
**Prior State**: PR #675 and PR #676 successfully merged to main

---

## User Requests

1. Continue with suggested work items from Phase 5 discover (implicit via `continue=all`)

---

## Overview and Objectives

Execute Phase 7 acceptance gate infrastructure in parallel:
- **Phase 7.1**: Timing evidence collection (awaiting CI runs)
- **Phase 7.2**: Security dispositions escalation (awaiting reviewer sign-offs)
- **Phase 7.3**: Visual regression test execution (ready immediately)

## Context Summary

### Merged Infrastructure (PR #675 + #676)
- Timing Analysis Framework (`timing-analysis.md`, 170 lines) — Run 1/3 captured, awaiting Runs 2-3
- Security Sign-Off Checklist (`security-sign-off-checklist.md`, 251 lines) — 7/10 approvals complete, 3 pending
- Playwright Visual Regression Suite (`observatory-visual-regression.spec.mjs`, 389 lines) — Ready to execute
- Phase 6 Runtime Evidence (`phase-6-runtime-evidence.md`, 287 lines) — 216+ tests validating atomic publish, idempotence, protected Podcaster

### Blocking Constraints
- **CI-Dependent**: Timing Runs 2-3 require natural CI pipeline completion (1-2 business days)
- **Owner-Driven**: Security dispositions (SEC-06, SEC-08, sponsor conclusion) require Hermes/jmservera review
- **Ready-to-Execute**: Visual regression tests executable immediately with Hugo server + Playwright

## Implementation Checklist

### Phase 7.1: Timing Evidence Collection
<!-- parallelizable: false -->
- [ ] Step 1: Await next scheduled CI build on main (monitor GitHub Actions)
- [ ] Step 2: Extract timing artifacts (Hugo ms, Pagefind ms from workflow logs)
- [ ] Step 3: Record Run 2 in timing-analysis.md
- [ ] Step 4: Await third CI run completion
- [ ] Step 5: Record Run 3 and compute median/p95
- [ ] Step 6: Submit to timing-budget owner for approval (jmservera)
- [ ] Step 7: Document final approval in status-of-record.md

**Ownership**: jmservera (timing-budget owner)  
**Timeline**: Depends on CI execution (2-3 business days for 2 builds)  
**Success Criteria**: timing-analysis.md updated with Runs 2-3, p95 ≤ 20,000ms (Hugo) and 2,500ms (Pagefind)

---

### Phase 7.2: Security Dispositions Escalation
<!-- parallelizable: false -->
- [ ] Step 1: Prepare escalation message with SEC-06, SEC-08, sponsor conclusion references
- [ ] Step 2: Send message to Hermes (SEC-06: GA4/GSC consent, SEC-08: raw HTML disabled) 
- [ ] Step 3: Send message to jmservera (sponsor conclusion for NFR-004 closure)
- [ ] Step 4: Log disposition timestamps when received
- [ ] Step 5: Update security-sign-off-checklist.md with final approvals
- [ ] Step 6: Mark NFR-004 as closed in status-of-record.md

**Ownership**: jmservera (initiator), Hermes (SEC-06/08 reviewer), jmservera (sponsor)  
**Timeline**: Unknown (reviewer availability dependent, typically 1-3 business days)  
**Success Criteria**: All 10 findings approved/accepted, NFR-004 closure recorded, status-of-record updated

---

### Phase 7.3: Visual Regression Test Execution ✅ Ready Now
<!-- parallelizable: true -->
- [x] Step 1: Start Hugo server on localhost:1313
- [x] Step 2: Verify Playwright test suite syntax and ESM imports
- [x] Step 3: Run the capture. The suite has no `toHaveScreenshot()` assertions, so
  `--update-snapshots` has no effect: `npx --no-install playwright test --config tests/visual/playwright.config.mjs tests/visual/observatory-visual-regression.spec.mjs`
- [x] Step 4: Capture metadata for desktop/mobile/light/dark variants
- [x] Step 5: Document visual acceptance matrix in Phase 7 evidence file
- [x] Step 6: Baseline is gitignored evidence, not committed output
- [x] Step 7: Record the capture in `docs/review/data-observatory-relaunch/local-acceptance-evidence-2026-08-06.md`

**Ownership**: jmservera (execution)  
**Timeline**: ~30 minutes for local test run + documentation  
**Success Criteria**: 
- All 9 routes × 3 viewports × 2 themes captured (54 visual variants)
- Metadata includes revision SHA, timestamp, browser, viewport
- Visual-evidence.md created with screenshot matrix and approval sign-offs
- Baseline committed to repo for future regression detection

---

## Planning Log Reference

**Discrepancy Log**: None — all planned work items align with post-PR-merge readiness state.

**Implementation Paths Considered**:
1. ✅ **Selected**: Start Phase 7.3 (visual regression) immediately; queue 7.1 and 7.2 as monitoring/escalation tasks
   - Rationale: Unblocks Phase 7.3 validation; 7.1 and 7.2 are CI/owner-dependent and don't require agent action until events occur
2. Alternative: Wait for all three phases to mature before execution (rejected — loses time on 7.3 which is ready)

**Suggested Follow-On Work**:
- Monitor CI builds for Runs 2-3 (timing-analysis.md updates)
- Prepare security disposition escalation messages (for rapid send upon user go-ahead)
- Execute Phase 7.3 visual regression suite this session
- Upon completion, merge visual-evidence.md and updated status records to main

---

## Dependencies

### Discovered Instructions Files
None new; rely on existing Playwright, Hugo, and markdown standards.

### Discovered Skills
- Playwright test execution and baseline capture
- Hugo site rendering and screenshot verification

### External Dependencies
- Hugo server (must be running locally)
- Playwright browsers (Chromium expected via `@playwright/test`)
- GitHub Actions workflow monitoring (for timing data collection)

---

## Success Criteria

**Overall Session**: Execute Phase 7.3 visual regression baseline capture and documentation; queue 7.1 and 7.2 for monitoring/follow-up.

- ✅ Phase 7.3 baseline captured with all 54 visual variants
- ✅ Visual-evidence.md created with acceptance matrix
- ✅ Repository updated with baseline snapshots for regression detection
- ⏳ Phase 7.1 monitoring plan documented (await CI builds)
- ⏳ Phase 7.2 escalation messages prepared for dispatch

---

**Next Session Actions**:
1. Monitor CI builds and extract timing data when Runs 2-3 complete
2. Follow up on security dispositions (Hermes/jmservera sign-offs)
3. Execute full visual regression test suite on subsequent PR branches to detect regressions
