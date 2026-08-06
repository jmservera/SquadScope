<!-- markdownlint-disable-file -->

# Phase 7.3: Visual Regression Test Execution Guide

**Date**: 2026-08-06  
**Status**: Ready for execution (infrastructure delivered)  
**Deployment**: CI pipeline or local environment with Playwright dependencies

---

## Executive Summary

Phase 7.3 visual regression test infrastructure has been **successfully delivered and integrated into main**. The Playwright test suite captures revision-tagged visual evidence across desktop, mobile, light, and dark theme variants for all key site routes.

**Test Coverage**: 9 routes × 3 viewports × 2 themes = **54 visual variants per browser**

**Current State**: 
- ✅ Test file syntax validated (`observatory-visual-regression.spec.mjs`)
- ✅ Hugo server verified operational (0.146.0)
- ✅ Playwright installation confirmed (1.54.2)
- ⏳ Baseline capture blocked on system-level Playwright dependencies (requires `libnspr4`, `libnss3`)

---

## Execution Requirements

### Option 1: CI Environment (Recommended)

The `.github/workflows/ci.yml` includes necessary system dependencies and Playwright configuration. Baseline capture will execute automatically on the next successful CI run:

```bash
# CI automatically runs:
npx playwright test --config tests/visual/playwright.config.mjs \
  --update-snapshots  # Generate initial baseline
```

**Artifacts Generated**:
- `screenshots/playwright-output/` — JSON report + HTML report
- `screenshots/visual-regression-*/` — Variant folders with metadata
- `tests/visual/snapshots/` — Baseline image files for regression detection

### Option 2: Local Execution (Linux/macOS with sudo)

```bash
# Step 1: Install system dependencies
sudo npx playwright install-deps

# Step 2: Start Hugo server (in background)
hugo server -D --bind 0.0.0.0 --port 1313 &

# Step 3: Generate baseline snapshots
npx playwright test --config tests/visual/playwright.config.mjs \
  --update-snapshots

# Step 4: Review captured variants
ls -la screenshots/visual-regression-*/

# Step 5: Commit baseline snapshots to repo
git add tests/visual/snapshots/
git commit -m "feat(visual): capture baseline snapshots for regression detection"
```

### Option 3: Docker (If Using Containerfile)

```dockerfile
# Containerfile includes:
RUN npx playwright install --with-deps
```

Then run tests via Docker:
```bash
docker build -t squadscope-test .
docker run -e CI=true squadscope-test npx playwright test --config tests/visual/playwright.config.mjs
```

---

## Test Routes and Coverage Matrix

### Captured Routes (9)

| Route | Label | Purpose |
|-------|-------|---------|
| `/` | Homepage | Hero, navigation, analytics consent |
| `/about/` | About | Breadcrumbs, page layout |
| `/dashboard/` | Dashboard | Interactive elements, responsive grid |
| `/repo/trending/` | Trending Repos | Content card rendering |
| `/topics/ai/` | Topic Hub | Topic-specific styling |
| `/weekly/2026-W32/` | Weekly Edition | Archive navigation, pagination |
| `/monthly/2026-07/` | Monthly Summary | Multi-section layout |
| `/charts/explore/` | Charts Explorer | Chart rendering, interactions |
| `/search/` | Search | Form styling, results layout |

### Viewport Variants

| Viewport | Width | Height | Device | Purpose |
|----------|-------|--------|--------|---------|
| Mobile | 375px | 812px | iPhone-like | Mobile responsiveness |
| Tablet | 768px | 1024px | iPad-like | Tablet layout |
| Desktop | 1440px | 900px | Wide screen | Full-width rendering |

### Theme Variants

- **Light** — Default system theme
- **Dark** — User preference (CSS `prefers-color-scheme: dark`)

---

## Test Execution Output

### Expected Report Structure

After visual regression tests complete, evidence is written to:

```
screenshots/
├── visual-regression-chromium-home-desktop-light.png
├── visual-regression-chromium-home-desktop-dark.png
├── visual-regression-chromium-home-mobile-light.png
├── visual-regression-chromium-about-desktop-light.png
├── visual-regression-firefox-home-desktop-light.png
├── visual-regression-webkit-home-desktop-light.png
├── visual-regression-metadata-chromium.json     # Metadata per browser
├── visual-regression-metadata-firefox.json
├── visual-regression-metadata-webkit.json
├── playwright-report/                           # HTML report
│   ├── index.html
│   └── trace.zip
└── playwright-output/
    ├── test-results-index.json
    └── index.html
```

**Note**: Baseline snapshots are stored in `tests/visual/snapshots/` (committed to repo).
Evidence and reports are generated to `screenshots/` during CI execution.

---

## Evidence Collection Workflow

The visual regression test (`tests/visual/observatory-visual-regression.spec.mjs`) collects evidence by:

1. Navigating to each route in VISUAL_ROUTES
2. Waiting for network idle (all resources loaded)
3. Taking full-page screenshots via `page.screenshot()`
4. Writing evidence to `screenshots/visual-regression-{browser}-{route}-{viewport}-{theme}.png`
5. Generating metadata JSON files with execution details

### Verification Steps for Amy/Fry

After baseline capture completes (post-PR-merge, post-CI):

1. Download CI artifacts from GitHub Actions run
2. Review `screenshots/playwright-report/index.html` in browser
3. Compare visual render against design specification
4. Verify all 162 variants rendered correctly (9 routes × 3 browsers × 2 themes × 3 viewports)
5. Sign off in `docs/review/data-observatory-relaunch/visual-evidence.md`

---

## Metadata Captured Per Test

Each visual variant records:

```json
{
  "revision": "git SHA from GITHUB_SHA",
  "branch": "git branch from GITHUB_REF_NAME",
  "timestamp": "ISO 8601 datetime",
  "browserName": "chromium | firefox | webkit",
  "playwrightVersion": "1.54.2",
  "testDate": "test/visual/observatory-visual-regression.spec.mjs",
  "executionTime": "ms (test duration)",
  "viewport": "375x812 | 768x1024 | 1440x900",
  "theme": "light | dark",
  "route": "/ | /about/ | ... (9 routes)"
}
```

---

## Acceptance Checklist for Phase 7.3

- [ ] Baseline snapshots captured for all 54 variants (9 routes × 3 viewports × 2 themes)
- [ ] Metadata JSON includes revision SHA and timestamp
- [ ] Baseline committed to `tests/visual/snapshots/` on main
- [ ] HTML report reviewed; no unexpected rendering issues
- [ ] Playwright regression test suite ready for future PR validation
- [ ] Phase 7.3 evidence documented in status-of-record.md
- [ ] Visual acceptance sign-off recorded with date + approver

---

## Known Limitations & Future Work

1. **System Dependencies**: Local execution requires sudo to install Playwright dependencies. Recommend CI execution.
2. **Route URL Validation**: Test file contains hardcoded `http://127.0.0.1:1313` for local Hugo. CI uses dynamic baseURL from Playwright config.
3. **Font Rendering**: Playwright may capture slight font rasterization differences across systems. CI applies standardized retry logic (`retries: 1` on CI).
4. **Interaction Tests**: Current suite captures static visual states. Interactive element testing (e.g., dropdown toggle, modal open) deferred to Phase 8.

---

## Next Steps (Post-Execution)

1. **On Baseline Capture Success**:
   - Commit snapshots: `git add tests/visual/snapshots/ && git commit -m "feat(visual): baseline snapshots for regression detection"`
   - Push to main
   - Create `visual-evidence.md` with acceptance matrix and sign-offs

2. **On Future PR Branches**:
   - Run without `--update-snapshots` to detect regressions
   - If visual diff detected, review diffs in HTML report
   - Approve or reject changes based on acceptance criteria

3. **Ongoing Maintenance**:
   - Re-run baseline after major design changes to site
   - Monitor regression test results in CI
   - Update test routes if new key pages added to site

---

## References

- **Test File**: [tests/visual/observatory-visual-regression.spec.mjs](../../tests/visual/observatory-visual-regression.spec.mjs)
- **Playwright Config**: [tests/visual/playwright.config.mjs](../../tests/visual/playwright.config.mjs)
- **Phase 6 Evidence**: [docs/review/data-observatory-relaunch/phase-6-runtime-evidence.md](../review/data-observatory-relaunch/phase-6-runtime-evidence.md)
- **Status of Record**: [docs/review/data-observatory-relaunch/status-of-record.md](../review/data-observatory-relaunch/status-of-record.md)

---

**Prepared By**: RPI Agent  
**Date**: 2026-08-06  
**Infrastructure Status**: ✅ Delivered and Merged (PR #676)
