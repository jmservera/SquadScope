<!-- markdownlint-disable-file -->
# Phase 5 Suggested Work Items 3-5 — Dependencies & Readiness Status

**Date**: 2026-08-06  
**Session**: Continue-all Phase 3 execution  
**Status**: ✅ **PLANNED** (awaiting Item 2 unblock for execution)

---

## Item 3: Create Visual Evidence Document Post-Baseline

**Status**: ⏳ Awaiting Phase 7.3 Baseline Capture Completion  
**Owner**: Amy (design review), Fry (QA sign-off)  
**Timeline**: After Item 2 baseline completion (~12:15 UTC if PR merged now) + 1-2 hours review

### Prerequisites
- [ ] PR #677 merged to main
- [ ] CI workflow executes visual regression tests (baseline capture)
- [ ] 162 visual snapshots available in `tests/visual/snapshots/`
- [ ] Artifacts downloaded or reviewed in GitHub Actions UI

### Deliverable Template

**File**: `docs/review/data-observatory-relaunch/visual-evidence.md`

**Structure**:
1. **Overview** — Phase 7.3 acceptance gate closure documentation
2. **Baseline Metadata**
   - Capture date and CI run ID
   - Browsers tested (Chromium, Firefox, WebKit)
   - Routes tested (9 total: /, /about/, /dashboard/, /repo/trending/, etc.)
   - Viewports (mobile, tablet, desktop)
   - Themes (light, dark)
   - Total snapshots: 162

3. **Screenshot Matrix** — Visual reference table
   ```
   | Route | Mobile | Tablet | Desktop |
   |-------|--------|--------|---------|
   | / | ✅ | ✅ | ✅ |
   | /about/ | ✅ | ✅ | ✅ |
   ...
   ```

4. **Design Approval Checklist** (Amy)
   - [ ] No visual regressions identified
   - [ ] Responsive design validation passed
   - [ ] Theme contrast and readability acceptable
   - [ ] Asset rendering correct (images, icons, fonts)
   - [ ] Approved by Amy on [DATE]

5. **QA Regression Testing** (Fry)
   - [ ] Baseline snapshots reviewed against design specifications
   - [ ] No rendering errors or layout issues detected
   - [ ] Visual consistency across browsers confirmed
   - [ ] Performance baseline established
   - [ ] Approved by Fry on [DATE]

6. **Release Readiness Statement**
   ```
   Phase 7.3 Visual Acceptance Gate: ✅ APPROVED
   - Baseline captured: [DATE TIME]
   - CI Run: [LINK]
   - Amy Sign-Off: ✅ [DATE]
   - Fry Sign-Off: ✅ [DATE]
   - Variance Analysis: [NOTES]
   ```

7. **Artifact References**
   - Link to CI artifacts: `https://github.com/jmservera/SquadScope/actions/runs/[RUN_ID]`
   - Baseline snapshots directory: `tests/visual/snapshots/`
   - GitHub Actions workflow: `.github/workflows/ci.yml`

### Success Criteria
- [ ] All 162 snapshots reviewed
- [ ] No visual regressions identified
- [ ] Amy + Fry sign-off recorded with dates
- [ ] Document committed to main branch
- [ ] Phase 7.3 gate marked as CLOSED

### Blockers
- **Primary**: Item 2 baseline capture must complete
- **Secondary**: GitHub CI artifacts must remain available (30-day retention)

---

## Item 4: Monitor & Collect Phase 7.1 Run 3 Timing Data

**Status**: ⏳ Passively Monitoring (CI-Dependent)  
**Owner**: jmservera  
**Timeline**: Expected 2026-08-07+ (next natural CI execution on main)  
**Action Type**: Passive monitoring + manual data collection

### Prerequisites
- [ ] Next successful CI build on main branch completes
- [ ] Production site job finishes (includes build-timing.json artifact capture)
- [ ] Artifact available in GitHub Actions > CI > production-quality-reports
- [ ] Within 24 hours of CI completion (30-day retention policy)

### Workflow Steps

**Step 1: Monitor for Run 3 (Passive)**
- **Where**: GitHub Actions > CI workflow
- **Watch For**: Next successful run after Run 2 (31095474806)
- **Timeline**: Expected 2026-08-07 or later (depends on commit frequency to main)
- **Trigger**: Automatic on `git push` to main

**Step 2: Download Artifact (When Ready)**
```bash
# List recent runs
gh run list --workflow ci.yml -L 3

# Find new run ID (should be higher than 31095474806)
RUN_ID="[NEW_RUN_ID]"

# Download timing artifact
gh run download "$RUN_ID" --name production-quality-reports --dir /tmp/timing-run-3

# Extract timing data
cat /tmp/timing-run-3/reports/build-timing.json
```

**Step 3: Record Run 3 in timing-analysis.md**
- Location: `docs/review/data-observatory-relaunch/timing-analysis.md`
- Section: "Run 3: Production CI"
- Fields:
  - Run ID (from gh run output)
  - Commit hash
  - Branch (should be main)
  - Date/time
  - Hugo duration (ms)
  - Pagefind duration (ms)
  - Total build time

**Step 4: Recalculate p95**
```
Runs 1-3: [value1], [value2], [value3]
P95 (max): [highest value]
Budget: 20,000 ms (Hugo) / 2,500 ms (Pagefind)
Status: ✅ / ❌
```

**Step 5: Update Approval Status**
- If p95 still within budget: Change to **FINAL APPROVAL**
- If p95 exceeds budget: Flag for investigation
- Record update timestamp

### Data Fields Required

```markdown
### Run 3: Production CI ([DATE])

**Run ID**: [GITHUB_RUN_ID]
**Commit**: [FULL_COMMIT_HASH]
**Branch**: main
**Date**: [YYYY-MM-DD] ([HH:MM:SS UTC])
**Status**: ✅ Captured

Captured timing:
- Hugo: [XXX] ms (0.161.1)
- Pagefind: [XXX] ms (1.5.2)
- Total build: [XXX] ms

Artifact location: [GitHub Actions run XXX](https://github.com/jmservera/SquadScope/actions/runs/[RUN_ID])
```

### Success Criteria
- [ ] Run 3 timing captured
- [ ] Data recorded in timing-analysis.md
- [ ] p95 recalculated with three-point average
- [ ] Status updated (provisional → final or flagged)
- [ ] Changes committed to main

### Critical Constraint
- **30-Day Artifact Retention**: Must download within 24 hours of CI completion
- **Fallback**: If missed, timing data permanently lost

### Blockers
- **Time-Based**: Awaits next CI pipeline execution (1-2 business days)
- **No Action Needed**: Passive wait; jmservera monitors and acts when available

---

## Item 5: Record Final Phase 7 Release Decision

**Status**: ⏳ Awaiting Items 2-4 Completion  
**Owner**: jmservera  
**Timeline**: After Items 2-4 deliver evidence (expected 2026-08-08/09)  
**Action Type**: Executive decision + documentation

### Prerequisites
- [ ] Phase 7.1 Timing: p95 recalculated with Run 3 (or provisional approved)
- [ ] Phase 7.2 Security: All 10 findings approved, NFR-004 APPROVED ✅
- [ ] Phase 7.3 Visual: Baseline reviewed, Amy + Fry signed off ✅

### Deliverable

**File**: `docs/review/data-observatory-relaunch/phase-7-final-release-decision.md`

**Decision Template**:
```markdown
# Phase 7 Release Authorization — Final Decision

**Date**: [YYYY-MM-DD]
**Decided By**: jmservera
**Status**: ✅ APPROVED FOR GO-LIVE

## Gate Closure Checklist

### Phase 7.1: Timing Evidence Collection ✅
- Metric: Hugo build time
  - Run 1: 15,339 ms
  - Run 2: 3,015 ms (anomaly context: [context])
  - Run 3: [XXX] ms
  - **P95 (Max)**: [HIGHEST] ms
  - **Budget**: 20,000 ms
  - **Status**: ✅ APPROVED (margin: X%)

- Metric: Pagefind indexing
  - Run 1: 1,631 ms
  - Run 2: 2,448 ms
  - Run 3: [XXX] ms
  - **P95 (Max)**: [HIGHEST] ms
  - **Budget**: 2,500 ms
  - **Status**: ✅ APPROVED (margin: X%)

### Phase 7.2: Security Dispositions ✅
- Finding Count: 10/10 approved
- SEC-01 to SEC-10: All dispositions recorded
- NFR-004 Status: ✅ APPROVED by jmservera
- Conditions: None outstanding
- **Status**: ✅ APPROVED

### Phase 7.3: Visual Regression Baseline ✅
- Snapshots Captured: 162/162
- Browsers: Chromium, Firefox, WebKit
- Routes: 9/9 tested
- Regressions Detected: None
- Amy Sign-Off: ✅ [DATE]
- Fry Sign-Off: ✅ [DATE]
- **Status**: ✅ APPROVED

## Release Authorization

**Overall Decision**: ✅ **APPROVED FOR GO-LIVE**

- All three acceptance gates closed ✅
- No security, timing, or visual blockers
- Production readiness confirmed
- Deployment authorization: Proceed

**Next Step**: Execute go-live coordination
```

### Go-Live Execution Steps
1. **Flag Flip** (deploy-site.yml or manual update)
   ```
   repo_pages.enabled = true
   topic_hubs.dynamic_creation.enabled = true
   ```

2. **Rollout Announcement** (optional)
   - Internal team notification
   - Release notes
   - Monitoring dashboards activation

3. **Post-Deployment Validation** (1-2 hours post-go-live)
   - Monitor error rates
   - Confirm feature functionality
   - Validate performance metrics

### Success Criteria
- [ ] Release decision documented and committed
- [ ] All Phase 7 gates recorded as APPROVED
- [ ] Go-live timeline established
- [ ] Deployment team notified
- [ ] Post-deployment monitoring activated

### Blockers
- **Hard Blockers**: Items 2-4 must deliver evidence
- **Optional Blockers**: Additional stakeholder approvals (if required by governance)

---

## Summary Table

| Item | Title | Owner | Status | Blocker | Timeline |
|------|-------|-------|--------|---------|----------|
| 1 | Merge PR #677 | jmservera | ✅ Ready | None | Immediate (~5 min) |
| 2 | Trigger Visual Baseline | jmservera | ⏳ Blocked | Item 1 merge | Post-merge (~30 min) |
| 3 | Create Visual Evidence | Amy + Fry | ⏳ Blocked | Item 2 complete | 1-2 hours post-baseline |
| 4 | Collect Run 3 Timing | jmservera | ⏳ Waiting | CI execution | 1-2 business days |
| 5 | Record Release Decision | jmservera | ⏳ Blocked | Items 2-4 complete | 2026-08-08/09 |

---

## Critical Path to Release Readiness

```
Item 1: Merge PR #677 ✅
   ↓ (automatic CI trigger)
Item 2: CI Baseline Capture ⏳ (30-45 min)
   ↓
Item 3: Amy/Fry Visual Review ⏳ (1-2 hours)
   ↓
Item 4: Monitor Run 3 Collection ⏳ (1-2 days, parallel)
   ↓
Item 5: Record Release Decision ✅ (immediate once 2-4 complete)
   ↓
Go-Live Authorization Complete ✅
```

**Expected Release Readiness**: 2026-08-08 to 2026-08-09 (achievable per current timeline)

---

**Status**: ✅ All items planned and ready for execution upon Item 1-2 unblock.
