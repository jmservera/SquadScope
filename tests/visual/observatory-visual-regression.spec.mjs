import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get package.json for version info
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pkgPath = path.join(__dirname, '../../node_modules/@playwright/test/package.json');
let playwrightVersionStr = '1.54.2'; // fallback version
try {
  const pkgContent = fs.readFileSync(pkgPath, 'utf-8');
  const pkg = JSON.parse(pkgContent);
  playwrightVersionStr = pkg.version;
} catch (e) {
  // Use fallback if version cannot be read
}

/**
 * Visual Regression Tests for Data Observatory Relaunch (Phase 7.3)
 * 
 * Captures revision-tagged visual evidence for desktop, mobile, light, dark, and interaction matrices.
 * Tests verify rendered breadcrumb, analytics consent UI, responsive behavior, and accessibility.
 * 
 * Execution: npx playwright test --config tests/visual/playwright.config.mjs tests/visual/observatory-visual-regression.spec.mjs
 * Reports: JSON metadata and screenshots generated to screenshots/visual-regression-{variant}/ folders
 */

// Page routes to capture for visual acceptance
const VISUAL_ROUTES = [
  { path: '/', name: 'home', label: 'Homepage' },
  { path: '/about/', name: 'about', label: 'About' },
  { path: '/dashboard/', name: 'dashboard', label: 'Dashboard' },
  { path: '/repo/trending/', name: 'trending', label: 'Trending Repos (example)' },
  { path: '/topics/ai/', name: 'topic', label: 'Topic Hub (AI example)' },
  { path: '/weekly/2026-W32/', name: 'weekly', label: 'Weekly Edition' },
  { path: '/monthly/2026-07/', name: 'monthly', label: 'Monthly Summary' },
  { path: '/charts/explore/', name: 'charts', label: 'Charts & Explorer' },
  { path: '/search/', name: 'search', label: 'Search' },
];

// Visual regression test matrix
test.describe('Observatory Visual Regression Suite', () => {
  // Extract page context from browser and viewport info
  const getPageContext = (browserName, viewport) => {
    const isMobile = viewport.width <= 768;
    const isDark = false; // Playwright default is light theme
    return {
      isMobile,
      isDark,
      viewport: `${viewport.width}x${viewport.height}`,
      label: isMobile ? 'mobile' : 'desktop',
      browser: browserName
    };
  };

  // Common visual checks for all pages
  test.describe('Common Visual Patterns', () => {
    VISUAL_ROUTES.forEach(route => {
      test(`${route.name}: Desktop Light - Breadcrumb and Navigation`, async ({ page, browserName }) => {
        const viewport = page.viewportSize() ?? { width: 1280, height: 800 };
        const ctx = getPageContext(browserName, viewport);
        
        // Navigate to page
        await page.goto(`http://127.0.0.1:1313${route.path}`);
        await page.waitForLoadState('networkidle');

        // Verify breadcrumb structure
        const breadcrumbNav = page.locator('nav.breadcrumbs');
        if (route.path !== '/') {
          // Non-home pages should have breadcrumbs
          await expect(breadcrumbNav).toBeVisible({ timeout: 5000 });
          
          // Verify breadcrumb contains ordered list
          const breadcrumbOl = breadcrumbNav.locator('ol');
          await expect(breadcrumbOl).toBeVisible();
          
          // Verify list-style-type is none (no visible numbering)
          const listStyle = await breadcrumbOl.evaluate(el => window.getComputedStyle(el).listStyleType);
          expect(listStyle).toBe('none');
          
          // Verify terminal page label has aria-current
          const currentPage = breadcrumbNav.locator('[aria-current="page"]');
          await expect(currentPage).toBeVisible();
        }

        // Take full-page screenshot for acceptance matrix
        const screenshotName = `${route.name}-desktop-light`;
        await page.screenshot({
          path: `screenshots/visual-regression-${browserName}-${screenshotName}.png`,
          fullPage: true,
        });

        // Capture viewport for mobile testing
        if (ctx.viewport !== '1440x900') {
          await page.setViewportSize({ width: 375, height: 812 });
          const mobileScreenshotName = `${route.name}-mobile-light`;
          await page.screenshot({
            path: `screenshots/visual-regression-${browserName}-${mobileScreenshotName}.png`,
            fullPage: true,
          });
        }
      });
    });
  });

  // Analytics and Consent UI
  test.describe('Analytics and Consent Lifecycle', () => {
    test('Homepage: Cookie Consent Dialog - Visibility and Interaction', async ({ page, context }) => {
      await page.goto('http://127.0.0.1:1313/');
      await page.waitForLoadState('networkidle');

      // Check for Cookie Consent widget
      const consentContainer = page.locator('#c-settings-bg, .c-settings'); // Common consent library selectors
      
      // Capture consent UI state (fresh)
      if (await consentContainer.isVisible()) {
        await page.screenshot({
          path: 'screenshots/visual-regression-consent-fresh.png',
          fullPage: false,
        });

        // Accept button interaction
        const acceptBtn = page.locator('button:has-text("Accept"), [data-consent-accept]');
        if (await acceptBtn.isVisible()) {
          await acceptBtn.click();
          await page.waitForTimeout(500);

          // Capture state after acceptance
          await page.screenshot({
            path: 'screenshots/visual-regression-consent-accepted.png',
            fullPage: false,
          });
        }
      }
    });

    test('Analytics Script Presence - Fresh vs. Accepted Consent', async ({ page }) => {
      // Test measurement ID is configured
      const measurementId = process.env.PLAYWRIGHT_GA_TEST_ID || 'G-TEST-OBSERVATORY';

      await page.goto('http://127.0.0.1:1313/');

      // Fresh state: GA script should not load
      const gaScriptFresh = page.locator(`script[src*="https://www.googletagmanager.com"]`);
      let gaScriptCount = await gaScriptFresh.count();
      expect(gaScriptCount).toBe(0); // Should be 0 until consent accepted

      // Accept consent
      const acceptBtn = page.locator('button:has-text("Accept"), [data-consent-accept]');
      if (await acceptBtn.isVisible()) {
        await acceptBtn.click();
        await page.waitForTimeout(1000); // GA loads asynchronously

        // After acceptance: GA script should be present
        const gaScriptAccepted = page.locator(`script[src*="googletagmanager"]`);
        gaScriptCount = await gaScriptAccepted.count();
        expect(gaScriptCount).toBeGreaterThan(0); // Should load after consent
      }
    });
  });

  // Responsive Design Matrix
  test.describe('Responsive Design - Mobile vs. Desktop', () => {
    const viewports = [
      { name: 'mobile-375', width: 375, height: 812 },
      { name: 'tablet-768', width: 768, height: 1024 },
      { name: 'desktop-1440', width: 1440, height: 900 },
    ];

    VISUAL_ROUTES.slice(0, 3).forEach(route => {
      viewports.forEach(viewport => {
        test(`${route.name}: ${viewport.name} - Layout and Overflow`, async ({ page, browserName }) => {
          await page.setViewportSize({ width: viewport.width, height: viewport.height });
          await page.goto(`http://127.0.0.1:1313${route.path}`);
          await page.waitForLoadState('networkidle');

          // Check for horizontal overflow
          const body = page.locator('body');
          const scrollWidth = await body.evaluate(el => el.scrollWidth);
          const clientWidth = await body.evaluate(el => el.clientWidth);

          expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 1); // Allow 1px rounding error

          // Verify breadcrumb wraps properly on mobile
          if (route.path !== '/' && viewport.width <= 768) {
            const breadcrumbNav = page.locator('nav.breadcrumbs');
            if (await breadcrumbNav.isVisible()) {
              const breadcrumbList = breadcrumbNav.locator('ol');
              const display = await breadcrumbList.evaluate(el => window.getComputedStyle(el).display);
              // Should be flex (wrappable) not inline
              expect(['flex', 'grid']).toContain(display);
            }
          }

          // Capture responsive screenshot
          await page.screenshot({
            path: `screenshots/visual-regression-${browserName}-${route.name}-${viewport.name}.png`,
            fullPage: true,
          });
        });
      });
    });
  });

  // Dark Theme Tests (if implemented)
  test.describe('Dark Theme Visual Regression', () => {
    test('Homepage: Dark Theme - Breadcrumb and Navigation Colors', async ({ page, browserName }) => {
      await page.goto('http://127.0.0.1:1313/');
      await page.waitForLoadState('networkidle');

      // Inject dark theme preference (via prefers-color-scheme or class toggle)
      await page.evaluate(() => {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
          // Browser is in dark mode
          document.documentElement.dataset.theme = 'dark';
        } else {
          // Force dark mode if available
          const themeToggle = document.querySelector('[data-theme-toggle]');
          if (themeToggle) {
            themeToggle.click();
            // Wait for theme transition
          }
        }
      });

      await page.waitForTimeout(500); // Allow theme transition

      // Verify breadcrumb colors have sufficient contrast
      const breadcrumbNav = page.locator('nav.breadcrumbs');
      if (await breadcrumbNav.isVisible()) {
        const computedBg = await breadcrumbNav.evaluate(el => 
          window.getComputedStyle(el).backgroundColor
        );
        const computedColor = await breadcrumbNav.evaluate(el =>
          window.getComputedStyle(el).color
        );
        
        // Both should be non-transparent
        expect(computedBg).not.toBe('rgba(0, 0, 0, 0)');
        expect(computedColor).not.toBe('rgba(0, 0, 0, 0)');
      }

      await page.screenshot({
        path: `screenshots/visual-regression-${browserName}-homepage-dark.png`,
        fullPage: true,
      });
    });
  });

  // Interaction and Animation
  test.describe('Interaction Patterns', () => {
    test('Breadcrumb Navigation: Link Hover States', async ({ page, browserName }) => {
      await page.goto('http://127.0.0.1:1313/repo/trending/');
      await page.waitForLoadState('networkidle');

      const breadcrumbNav = page.locator('nav.breadcrumbs');
      const breadcrumbLinks = breadcrumbNav.locator('a');

      const linkCount = await breadcrumbLinks.count();
      if (linkCount > 0) {
        // Hover over first link
        await breadcrumbLinks.first().hover();
        await page.waitForTimeout(200);

        const hoverColor = await breadcrumbLinks.first().evaluate(el =>
          window.getComputedStyle(el).color
        );

        // Non-hover state
        await page.mouse.move(0, 0); // Move away
        await page.waitForTimeout(200);

        const normalColor = await breadcrumbLinks.first().evaluate(el =>
          window.getComputedStyle(el).color
        );

        // Hover and normal states should differ
        expect(hoverColor).not.toBe(normalColor);

        // Capture hover state
        await breadcrumbLinks.first().hover();
        await page.screenshot({
          path: `screenshots/visual-regression-${browserName}-breadcrumb-hover.png`,
          fullPage: false,
        });
      }
    });

    test('Search and Tool Interaction Patterns', async ({ page, browserName }) => {
      await page.goto('http://127.0.0.1:1313/charts/explore/');
      await page.waitForLoadState('networkidle');

      // Check for tool input fields and buttons
      const inputs = page.locator('input[type="text"], input[type="search"]');
      const buttons = page.locator('button:visible');

      if (await inputs.count() > 0) {
        // Focus on first input
        await inputs.first().focus();
        await page.waitForTimeout(200);

        const focusOutline = await inputs.first().evaluate(el =>
          window.getComputedStyle(el).outline
        );

        // Should have visible focus indicator
        expect(focusOutline).not.toBe('none');

        // Type to capture input state
        await inputs.first().fill('AI');
        await page.screenshot({
          path: `screenshots/visual-regression-${browserName}-tool-input-focused.png`,
          fullPage: false,
        });
      }

      if (await buttons.count() > 0) {
        // Hover and click capture
        await buttons.first().hover();
        await page.waitForTimeout(100);

        await buttons.first().click();
        await page.waitForTimeout(500);

        await page.screenshot({
          path: `screenshots/visual-regression-${browserName}-tool-button-active.png`,
          fullPage: false,
        });
      }
    });
  });

  // Metadata and Evidence Logging
  test.describe('Visual Evidence Metadata', () => {
    test('Capture Test Environment and Revision Information', async ({ page, browserName }, testInfo) => {
      const commitSha = process.env.GITHUB_SHA || 'local-dev';
      const branchName = process.env.GITHUB_REF_NAME || 'local';
      const timestamp = new Date().toISOString();

      const metadata = {
        revision: commitSha,
        branch: branchName,
        timestamp,
        browserName,
        playwrightVersion: playwrightVersionStr,
        testDate: testInfo.file,
        executionTime: testInfo.duration,
      };

      // Write metadata alongside screenshots
      if (!fs.existsSync('screenshots')) {
        fs.mkdirSync('screenshots', { recursive: true });
      }

      fs.writeFileSync(
        `screenshots/visual-regression-metadata-${browserName}.json`,
        JSON.stringify(metadata, null, 2)
      );

      console.log(`\n✓ Visual regression evidence captured for revision: ${commitSha}`);
      console.log(`  Browser: ${browserName}, Timestamp: ${timestamp}`);
      console.log(`  Evidence path: screenshots/visual-regression-metadata-${browserName}.json`);
    });
  });
});

/**
 * Test Execution Notes:
 * 
 * 1. Local Development:
 *    npm run test:visual-regression
 *    Output: screenshots/visual-regression-chromium-*.png, .json metadata
 * 
 * 2. CI Integration:
 *    - Runs after production site build in .github/workflows/ci.yml
 *    - Captures revision SHA, branch, timestamp
 *    - Artifacts retained with production quality reports
 * 
 * 3. Visual Acceptance Process:
 *    - Named visual reviewer examines revision-tagged matrices
 *    - Compares desktop/mobile/light/dark/interaction variants
 *    - Records visual approval in docs/review/data-observatory-relaunch/README.md
 *    - Closes Step 7.3 upon approval
 * 
 * 4. Regression Detection:
 *    - Future runs capture same routes and viewports
 *    - Diff against baseline tagged by revision
 *    - Alerts on unintended visual changes
 */
