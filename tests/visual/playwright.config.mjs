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

export default defineConfig({
  testDir: '.',          // relative to this config file: tests/visual/
  snapshotDir: 'snapshots',
  outputDir: '../../screenshots/playwright-output',

  // Retry once on CI to reduce font-rendering flakiness
  retries: process.env.CI ? 1 : 0,

  // Run tests sequentially — Hugo is on localhost, parallelism adds noise
  workers: 1,

  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:1313/SquadScope',
    // Wait for network to settle before screenshotting
    actionTimeout: 15000,
  },

  expect: {
    toHaveScreenshot: {
      // Allow ~150 pixel diff for anti-aliasing and sub-pixel font rendering
      maxDiffPixels: 150,
      // Timeout for screenshot comparison
      timeout: 10000,
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
        ...devices['iPhone 13'],
        colorScheme: 'light',
      },
    },
    // Mobile — dark
    {
      name: 'mobile-dark',
      use: {
        ...devices['iPhone 13'],
        colorScheme: 'dark',
      },
    },
    // Wide — light (for the wide editorial layout)
    {
      name: 'wide-light',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
        colorScheme: 'light',
      },
    },
    // Wide — dark
    {
      name: 'wide-dark',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
        colorScheme: 'dark',
      },
    },
  ],
});
