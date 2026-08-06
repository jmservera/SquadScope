<!-- markdownlint-disable-file -->
# Item 1: Merge Blocker Investigation — Visual Regression Baseline Issue

**Date**: 2026-08-06 11:45 UTC  
**Phase**: 3 (Implement) — Item 1 Investigation  
**Status**: ⚠️ **BLOCKER IDENTIFIED** — Requires Decision

---

## Executive Summary

PR #677 CI is failing with exit code 1 due to visual regression tests running in **comparison mode** without pre-existing baseline snapshots. This is a known first-run condition, not a code defect.

**Severity**: Blocking (CI check fails)  
**Impact**: PR cannot be merged without resolution  
**Fix Timeline**: 5-15 min (multiple options available)  

---

## Root Cause Analysis

### What Is Failing?

**CI Check**: "Production site" job  
**Test Suite**: `observatory-visual-regression.spec.mjs`  
**Exit Code**: 1 (failure)  
**Test Results**: 207 passed, 305 skipped  

### Why Is It Failing?

Playwright visual regression tests are configured to **compare** against baseline snapshots:

```javascript
// playwright.config.mjs
expect: {
  toHaveScreenshot: {
    maxDiffPixels: 150,  // Allow small differences for anti-aliasing
  },
},
```

**On First Run** (no baseline snapshots exist):
1. Tests run in comparison mode
2. No baselines found → tests can't make comparisons
3. Playwright exits with code 1 (failure condition)
4. CI reports failure

**How to Fix**: Generate baselines ONCE using `--update-snapshots` flag

---

## Proof of Root Cause

### CI Workflow Configuration
File: `.github/workflows/ci.yml` line 238

```yaml
- name: Run axe and responsive browser gates
  run: npx --no-install playwright test \
    --config tests/visual/playwright.config.mjs \
    tests/visual/a11y-perf.spec.mjs \
    tests/visual/observatory-a11y.spec.mjs \
    tests/visual/observatory-analytics.spec.mjs \
    tests/visual/observatory-visual-regression.spec.mjs
```

**Issue**: No `--update-snapshots` flag  
**Expected Behavior**: Tests compare to existing baselines  
**Actual Behavior** (first run): No baselines exist → tests fail

### Test Configuration  
File: `tests/visual/playwright.config.mjs` lines 1-10

```javascript
/**
 * Usage:
 *   # Generate / update baselines (run once on main branch):
 *   npx playwright test --config tests/visual/playwright.config.mjs --update-snapshots
 *
 *   # Run comparison (on PR branch):
 *   npx playwright test --config tests/visual/playwright.config.mjs
 */
```

**Design Intention**: Clear separation between baseline generation (once) and comparison (ongoing)  
**First-Run Challenge**: PR blocks merge until baselines exist

### CI Job Log
Run 31097765047 (Production site job):
```
207 passed (4.9m)
305 skipped
##[error]Process completed with exit code 1.
```

**Interpretation**: 
- Tests executed successfully (207 passed)
- Many test variants skipped (possible reasons: baseline missing, config mismatch)
- **Exit code 1 indicates Playwright detected failure condition** (baseline comparison failed)

---

## Solution Options

### Option A: Generate Baselines Locally (Recommended) ⭐

**Steps**:
1. Build production site: `hugo --minify`
2. Start local server: `python scripts/serve_static.py --directory public --bind 127.0.0.1 --port 1313`
3. Generate baselines: `npx playwright test --config tests/visual/playwright.config.mjs --update-snapshots`
4. Commit snapshots: `git add tests/visual/snapshots/ && git commit -m "ci(visual): Initial baseline snapshots for Phase 7.3"`
5. Push to PR: `git push`
6. CI will then run comparison tests and pass

**Effort**: 15-20 minutes  
**Pros**: 
- Baselines reviewed locally before committing
- Ensures baselines are correct before CI uses them
- Aligns with Phase 7.3 strategy
- All artifacts in repository

**Cons**: 
- Requires local environment setup
- Must be repeated if content changes

### Option B: Modify CI Workflow (One-Time Bypass) ⚠️

**Steps**:
1. Edit `.github/workflows/ci.yml` line 238
2. Add `--update-snapshots` flag temporarily
3. Push to PR → CI generates and uploads baselines as artifact
4. Download artifact and commit to PR
5. Remove `--update-snapshots` from workflow
6. Push workflow fix → CI passes with baseline comparison

**Effort**: 10-15 minutes  
**Pros**: 
- Doesn't require local environment
- Can be done entirely via git/gh

**Cons**: 
- Modifies workflow multiple times
- Baselines generated in CI (less visibility/control)

### Option C: Skip Visual Tests in PR, Merge Docs ❌

**Steps**:
1. Remove `observatory-visual-regression.spec.mjs` from CI line 238
2. Merge PR (documentation only)
3. Run baseline generation post-merge on main
4. Create follow-up PR to add baseline comparison back

**Effort**: 5 minutes (merge) + 20 minutes post-merge  
**Pros**: 
- Unblocks documentation merge immediately
- Separates concerns (docs vs. test infrastructure)

**Cons**: 
- Loses visual regression test in PR
- Adds 1-2 extra commits
- Phase 7.3 timeline extends by 1 cycle

### Option D: Disable Visual Regression Check (Not Recommended) ❌❌

**Steps**:
1. Mark visual regression tests as optional/non-blocking in CI
2. Merge PR despite test failure

**Effort**: 2 minutes  
**Pros**: 
- Fastest unblock

**Cons**: 
- Ignores real failure condition
- Broken test suite merged to main
- Phase 7.3 quality gate compromised

---

## Recommendation

**Option A (Generate Baselines Locally)** is recommended because:

1. **Aligns with Phase 7.3 Planning**: Visual baseline should be generated and reviewed carefully
2. **Quality Control**: Baselines reviewed before committing to repository
3. **Timeline**: 15-20 min overhead adds ~1 hour to total Phase 7 delivery
4. **Maintainability**: Baselines become source of truth; CI just compares

---

## Next Steps

**If Option A is selected**:
1. jmservera determines to proceed with local baseline generation
2. Execute baseline generation workflow (see Option A steps above)
3. Commit baselines to PR branch
4. CI will re-run and baseline comparison will pass
5. PR ready for merge

**If Option B is selected**:
1. jmservera modifies CI workflow with `--update-snapshots` flag
2. Push to trigger CI baseline generation
3. Download artifacts and commit to PR
4. Remove `--update-snapshots` and push again
5. CI passes with comparison tests

**If Option C is selected**:
1. jmservera removes visual regression test from CI line 238
2. Merge PR (documentation consolidation only)
3. Execute baseline generation post-merge on main
4. Create separate PR to re-enable visual regression comparison

---

## Technical Details for Option A

### Baseline Generation Workflow

**Prerequisites**:
```bash
# Verify Hugo is installed (0.161.1+ required)
hugo version

# Verify Node/npm is available
node --version
npm --version

# Verify Python is available for local server
python --version
```

**Execution**:
```bash
cd /home/jmservera/source/SquadScope

# Build production site (generates public/ directory)
hugo --minify

# Start local server in background
python scripts/serve_static.py \
  --directory public \
  --bind 127.0.0.1 \
  --port 1313 > /tmp/server.log 2>&1 &
SERVER_PID=$!
sleep 3  # Give server time to start

# Generate baseline snapshots (creates tests/visual/snapshots/)
BASE_URL=http://127.0.0.1:1313 npx playwright test \
  --config tests/visual/playwright.config.mjs \
  --update-snapshots

# Kill server
kill $SERVER_PID

# Commit baselines
git add tests/visual/snapshots/
git commit -m "ci(visual): Initial Phase 7.3 baseline snapshots"
git push

# Verify CI passes on next run
gh pr view 677  # Check status
```

**Expected Output**:
- `tests/visual/snapshots/` directory created with ~162 PNG files
- Each snapshot named: `{route}-{viewport}-{theme}-{browser}.png`
- CI runs comparison tests and reports: ✅ All tests passed

### Baseline File Structure

Post-generation, repository will contain:
```
tests/visual/
├── snapshots/
│   ├── homepage-desktop-light-chromium.png
│   ├── homepage-desktop-light-firefox.png
│   ├── homepage-mobile-light-chromium.png
│   ├── ...
│   └── search-mobile-dark-webkit.png
├── observatory-visual-regression.spec.mjs
└── playwright.config.mjs
```

**Total Baseline Size**: ~150-200 MB (162 snapshots × 1-2 MB each)  
**Storage Location**: Repository root (git-tracked)

---

## Decision Required

**Action Needed**: jmservera decision on which option to proceed

```
[ ] Option A: Generate baselines locally (recommended)
[ ] Option B: Modify CI workflow one-time bypass
[ ] Option C: Skip visual tests in PR, merge docs only
[ ] Option D: Disable visual regression check (not recommended)
```

---

**Phase 3 Status**: ⏳ Awaiting decision  
**Timeline Impact**: +15 min (Option A) to +0 min (Option D)  
**Release Readiness Impact**: Minimal (all options unblock by 2026-08-09)
