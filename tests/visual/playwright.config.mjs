// @ts-check
/**
 * Playwright configuration for SquadScope design visual verification.
 *
 * This config is scoped to tests/visual/ only — it is NOT the project-wide
 * test runner. It runs against a locally running Hugo server.
 *
 * Usage:
 *   # Start Hugo first:
 *   hugo server -D --bind 0.0.0.0
 *
 *   # Generate / update baselines (run once on main branch):
 *   npx playwright test --config tests/visual/playwright.config.mjs --update-snapshots
 *
 *   # Run comparison (on PR branch):
 *   npx playwright test --config tests/visual/playwright.config.mjs
 */

import { defineConfig, devices } from '@playwright/test';

// Several CI steps invoke this config in the same job. Without a distinct suffix
// each run would overwrite the previous run's reports and output directory.
const suffix = process.env.PLAYWRIGHT_REPORT_SUFFIX ?? '';

export default defineConfig({
  testDir: '.',          // relative to this config file: tests/visual/
  snapshotDir: 'snapshots',
  outputDir: `../../screenshots/playwright-output${suffix}`,

  // Retry once on CI to reduce font-rendering flakiness, but never let a retried
  // pass count as green: a retry once hid a real cross-origin consent defect.
  retries: process.env.CI ? 1 : 0,
  failOnFlakyTests: !!process.env.CI,

  // Run tests sequentially — Hugo is on localhost, parallelism adds noise
  workers: 1,

  reporter: process.env.CI
    ? [
        ['line'],
        ['json', { outputFile: `../../screenshots/playwright-report${suffix}.json` }],
        ['html', { outputFolder: `../../screenshots/playwright-report${suffix}`, open: 'never' }],
      ]
    : 'line',

  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:1313/SquadScope',
    // Wait for network to settle before screenshotting
    actionTimeout: 15000,
  },

  expect: {
    toHaveScreenshot: {
      // Allow ~150 pixel diff for anti-aliasing and sub-pixel font rendering
      maxDiffPixels: 150,
    },
  },

  projects: [
    // Desktop — light
    {
      name: 'desktop-light',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 800 },
        colorScheme: 'light',
      },
    },
    // Desktop — dark
    {
      name: 'desktop-dark',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 800 },
        colorScheme: 'dark',
      },
    },
    // Mobile — light
    {
      name: 'mobile-light',
      use: {
        ...devices['Pixel 5'],
        colorScheme: 'light',
      },
    },
    // Mobile — dark
    {
      name: 'mobile-dark',
      use: {
        ...devices['Pixel 5'],
        colorScheme: 'dark',
      },
    },
  ],
});
