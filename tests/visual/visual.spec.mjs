/**
 * Visual spec for SquadScope — home page
 *
 * Run with:
 *   npx playwright test --config tests/visual/playwright.config.mjs
 */

import { test, expect } from '@playwright/test';

// CSS injected into every page to suppress dynamic / noisy elements
const NOISE_SUPPRESSION_CSS = `
  .cost-dashboard__date,
  [data-cost-date],
  .run-date,
  .last-updated { visibility: hidden !important; }
  .dynamic-counter, .repo-count, [data-live] { visibility: hidden !important; }
  *, *::before, *::after { animation-duration: 0s !important; transition-duration: 0s !important; }
`;

async function settle(page) {
  await page.waitForLoadState('networkidle').catch(() => page.waitForTimeout(1000));
  await page.addStyleTag({ content: NOISE_SUPPRESSION_CSS });
  await page.waitForTimeout(300); // font settle
}

// ---------------------------------------------------------------------------
// Home
// ---------------------------------------------------------------------------

test('home — full page', async ({ page }) => {
  await page.goto('/');
  await settle(page);
  await expect(page).toHaveScreenshot('home.png', { fullPage: true });
});

// ---------------------------------------------------------------------------
// About / cost transparency
// ---------------------------------------------------------------------------

test('about — full page', async ({ page }) => {
  await page.goto('/about/');
  await settle(page);
  await expect(page).toHaveScreenshot('about.png', { fullPage: true });
});

// ---------------------------------------------------------------------------
// Latest weekly
// ---------------------------------------------------------------------------

test('weekly w22 — full page', async ({ page }) => {
  await page.goto('/weekly/2026/w22/');
  await settle(page);
  await expect(page).toHaveScreenshot('weekly-w22.png', { fullPage: true });
});

// ---------------------------------------------------------------------------
// Monthly rollup
// ---------------------------------------------------------------------------

test('monthly may 2026 — full page', async ({ page }) => {
  await page.goto('/monthly/2026/05/');
  await settle(page);
  await expect(page).toHaveScreenshot('monthly-may.png', { fullPage: true });
});

// ---------------------------------------------------------------------------
// Yearly rollup
// ---------------------------------------------------------------------------

test('yearly 2026 — full page', async ({ page }) => {
  await page.goto('/yearly/2026/');
  await settle(page);
  await expect(page).toHaveScreenshot('yearly-2026.png', { fullPage: true });
});

// ---------------------------------------------------------------------------
// Cover image / fallback visual placement (#358)
// ---------------------------------------------------------------------------

test('weekly article — cover card renders above content', async ({ page }) => {
  await page.goto('/weekly/2026/w22/');
  await settle(page);
  const cover = page.locator('.article-cover');
  await expect(cover).toBeVisible();
  // Verify the cover is spatially above the article content
  const content = page.locator('.post-content, article .content, .entry-content').first();
  const coverBox = await cover.boundingBox();
  const contentBox = await content.boundingBox();
  if (coverBox && contentBox) {
    expect(coverBox.y).toBeLessThan(contentBox.y);
  }
  await expect(cover).toHaveScreenshot('weekly-cover-card.png');
});

test('weekly article — cover card responsive (mobile)', async ({ page, browserName }, testInfo) => {
  // Only run in mobile projects to avoid redundant viewport override
  test.skip(!testInfo.project.name.includes('mobile'), 'mobile-only test');
  await page.goto('/weekly/2026/w22/');
  await settle(page);
  const cover = page.locator('.article-cover');
  await expect(cover).toBeVisible();
  await expect(cover).toHaveScreenshot('weekly-cover-card-mobile.png');
});
