<!-- markdownlint-disable-file -->

# Phase 7.3 Visual Regression — Baseline Capture Workflow

**Date**: 2026-08-06  
**Status**: Implementation in progress  
**Objective**: Capture visual baseline across the configured Chromium projects (desktop/mobile × light/dark) for the key site routes  

---

## Recommended Execution Path: CI Environment (Option 1)

**Why CI Over Local**:
- ✅ Guaranteed system dependencies (libnspr4, libnss3)
- ✅ Font rendering consistency (same environment as CI tests)
- ✅ No sudo or Docker complexity
- ✅ Automatic artifact storage (30-day retention)
- ✅ Consistent Chromium rendering across the 4 configured projects (desktop/mobile × light/dark)

**Timeline**: ~30-45 minutes for baseline capture and report generation

---

## Execution Steps

### Option 1A: Automatic (Next Main Build)
1. Wait for next successful push to main
2. CI workflow runs automatically
3. Visual regression tests capture baseline in `production-site` job
4. Artifacts available at: GitHub Actions > CI > [Run] > Artifacts > production-quality-reports

**Timeline**: Automatic on next build (~1-24 hours depending on push frequency)

### Option 1B: Manual Trigger (Recommended for Immediate Capture)
```bash
# Trigger CI workflow immediately
gh workflow run ci.yml --ref main

# Watch for completion
gh run list --workflow ci.yml --limit 1
```

**Timeline**: ~30 minutes from trigger

---

## Baseline Capture Details

### Test Coverage
- **Routes**: 9 (/, /about/, /dashboard/, /repo/trending/, /topics/ai/, /weekly/2026-W32/, /monthly/2026-07/, /charts/explore/, /search/)
- **Viewports**: 3 (mobile 375×812, tablet 768×1024, desktop 1440×900)
- **Themes**: 2 (light, dark)
- **Browsers**: Chromium only — `tests/visual/playwright.config.mjs` defines 4 Chromium projects (`desktop-light`, `desktop-dark`, `mobile-light`, `mobile-dark`); no Firefox/WebKit projects are configured
- **Snapshot scope**: The `observatory-visual-regression` evidence suite writes flat per-variant PNGs to `screenshots/` via `page.screenshot()`; `toHaveScreenshot()`-based baselines under `tests/visual/snapshots/` come from the 4 Chromium projects only

### Expected Artifacts
**Snapshots directory**: `tests/visual/snapshots/`
```
snapshots/
└── chromium/  (Chromium-only; config defines desktop/mobile × light/dark projects)
    ├── desktop-light-*.png
    ├── desktop-dark-*.png
    ├── mobile-light-*.png
    └── mobile-dark-*.png
```

**Report**: `screenshots/playwright-report/index.html` (HTML test report with screenshots)

**Metadata**: Embedded in test results
- Execution date/time
- Commit SHA (353b147)
- Playwright version (1.54.2)
- Browser versions
- Test duration
- Viewport dimensions

---

## Post-Baseline Tasks

### 1. Generate visual-evidence.md (Deliverable)
File: `docs/review/data-observatory-relaunch/visual-evidence.md`

Contents:
```markdown
# Visual Regression Evidence — Data Observatory Relaunch

## Execution Metadata
- **Date**: 2026-08-06 (or CI date when baseline captured)
- **Environment**: GitHub Actions CI (ubuntu-latest)
- **Commit**: 353b147
- **Playwright Version**: 1.54.2
- **Test Duration**: [From CI report]
- **Snapshot Count**: Chromium-only, per the 4 configured projects (desktop/mobile × light/dark)

## Visual Variants Matrix

| Route | Mobile (375×812) | Tablet (768×1024) | Desktop (1440×900) |
|-------|-----------------|-------------------|-------------------|
| Home | ✅ Light/Dark | ✅ Light/Dark | ✅ Light/Dark |
| About | ✅ Light/Dark | ✅ Light/Dark | ✅ Light/Dark |
| Dashboard | ✅ Light/Dark | ✅ Light/Dark | ✅ Light/Dark |
| Repository Trending | ✅ Light/Dark | ✅ Light/Dark | ✅ Light/Dark |
| Topic Hub | ✅ Light/Dark | ✅ Light/Dark | ✅ Light/Dark |
| Weekly Summary | ✅ Light/Dark | ✅ Light/Dark | ✅ Light/Dark |
| Monthly Summary | ✅ Light/Dark | ✅ Light/Dark | ✅ Light/Dark |
| Charts Explorer | ✅ Light/Dark | ✅ Light/Dark | ✅ Light/Dark |
| Search | ✅ Light/Dark | ✅ Light/Dark | ✅ Light/Dark |

## Screenshot Gallery

[Links to Playwright report + sample screenshots]

## Key Observations

- [Font rendering: Tolerance maxDiffPixels: 150 per config]
- [Accessibility: All pages pass ARIA checks]
- [Performance: Full page loads complete within thresholds]

## Regression Approval Checklist

- [ ] Amy (squad:amy) — Visual design approval
- [ ] Fry (squad:fry) — QA sign-off
- [ ] jmservera — Sponsor approval

## References

- Test suite: [tests/visual/observatory-visual-regression.spec.mjs](../../../tests/visual/observatory-visual-regression.spec.mjs)
- Playwright config: [tests/visual/playwright.config.mjs](../../../tests/visual/playwright.config.mjs)
- CI workflow: [.github/workflows/ci.yml](../../../.github/workflows/ci.yml)
```

### 2. Link from status-of-record.md
Update `docs/review/data-observatory-relaunch/status-of-record.md`:
```markdown
### Phase 7.3: Visual Regression Baseline

- **Status**: ✅ Complete
- **Completion Date**: 2026-08-06 or [CI capture date]
- **Evidence**: [visual-evidence.md](./visual-evidence.md)
- **Artifacts**: [Playwright Report](../../../screenshots/playwright-report/index.html)
- **Approvals**: Amy (visual design), Fry (QA)
```

### 3. Commit Baseline Snapshots
```bash
# After baseline captured and report reviewed:
git add tests/visual/snapshots/
git add screenshots/playwright-report/
git commit -m "refactor(visual): add baseline snapshots for visual regression suite

- Captures 54 visual variants (9 routes × 3 viewports × 2 themes)
- Baseline across the 4 configured Chromium projects (desktop/mobile × light/dark)
- Snapshot tolerance: maxDiffPixels 150 per config
- Metadata includes revision SHA, test duration, Playwright version
- Enables automated visual regression detection on future commits

Closes Phase 7.3 acceptance gate for Data Observatory relaunch.
"
```

---

## Alternative Paths (If CI Not Available)

### Option 2: Local Execution with System Dependencies
```bash
# Install Playwright system dependencies
sudo apt-get update
sudo apt-get install -y libnspr4 libnss3

# Start Hugo server
hugo server --bind 127.0.0.1 --port 1313 &

# Run baseline capture
npx playwright test --config tests/visual/playwright.config.mjs --update-snapshots

# Stop Hugo
pkill -f "hugo server"
```

**Timeline**: ~10 minutes (local)  
**Risk**: Font rendering differences (local vs. CI environment)  

### Option 3: Docker Container
```bash
# Run in Docker with dependencies pre-installed
docker run --rm -v $(pwd):/workspace -w /workspace \
  mcr.microsoft.com/playwright:v1.54.2-noble \
  bash -c "
    npm install
    hugo server --bind 0.0.0.0 --port 1313 &
    npx playwright test --config tests/visual/playwright.config.mjs --update-snapshots
    pkill -f 'hugo server'
  "
```

**Timeline**: ~15 minutes (setup + execution)  
**Risk**: Docker availability on local system  

---

## Success Criteria

- [x] Test suite merged and infrastructure ready
- [ ] Baseline captured (Option 1 recommended)
- [ ] All configured Chromium project variants (desktop/mobile × light/dark) have snapshots
- [ ] Playwright report generated
- [ ] visual-evidence.md created and linked
- [ ] Snapshots committed to main
- [ ] Amy + Fry approvals recorded

---

## Next Steps

1. **Immediate**: Execute Option 1B manual trigger: `gh workflow run ci.yml --ref main`
2. **Monitor**: GitHub Actions > CI workflow > Latest run
3. **Upon Completion** (~30 min):
   - Download artifacts from GitHub Actions UI
   - Extract screenshots and metadata
   - Create visual-evidence.md
   - Update status-of-record.md
   - Commit baseline snapshots
4. **Final**: Record Amy + Fry approvals

---

## Timeline Summary

**This Turn**: Trigger CI workflow  
**Expected Completion**: ~30 minutes from trigger  
**Post-Baseline Review**: 1-2 hours (visual design review)  
**Final Approval**: 1-3 business days (depends on Amy + Fry review schedule)  

