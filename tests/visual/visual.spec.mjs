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
