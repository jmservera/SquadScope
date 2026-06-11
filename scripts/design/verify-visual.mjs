#!/usr/bin/env node
/**
 * verify-visual.mjs
 * Playwright-based visual verification for SquadScope design changes.
 *
 * Usage:
 *   node scripts/design/verify-visual.mjs
 *   node scripts/design/verify-visual.mjs --base http://localhost:1313/SquadScope/
 *   node scripts/design/verify-visual.mjs --out screenshots/my-branch/
 *
 * Prerequisites:
 *   npx playwright install chromium
 *
 * Run:
 *   npx -y playwright install chromium --with-deps 2>/dev/null; node scripts/design/verify-visual.mjs
 */

import { chromium } from 'playwright';
import { mkdir, writeFile } from 'fs/promises';
import { existsSync } from 'fs';
import { join } from 'path';

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const args = process.argv.slice(2);

function getArg(name, fallback) {
  const idx = args.indexOf(name);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : fallback;
}

const BASE_URL = getArg('--base', 'http://localhost:1313/SquadScope/').replace(/\/$/, '');
const DATE_SLUG = getArg('--date', '2026-05-25');
const OUT_DIR   = getArg('--out',  join('screenshots', 'design-verification', DATE_SLUG));

const VIEWPORTS = [
  { name: 'mobile-320', width: 320,  height: 568  },
  { name: 'mobile-360', width: 360,  height: 640  },
  { name: 'mobile',     width: 375,  height: 667  },
  { name: 'mobile-390', width: 390,  height: 844  },
  { name: 'mobile-414', width: 414,  height: 896  },
  { name: 'tablet',     width: 768,  height: 1024 },
  { name: 'desktop',    width: 1280, height: 800  },
  { name: 'wide',       width: 1920, height: 1080 },
];

const THEMES = ['light', 'dark'];

const PAGES = [
  { key: 'home',           path: '/'                    },
  { key: 'about',          path: '/about/'              },
  { key: 'weekly-w22',     path: '/weekly/2026/w22/'    },
  { key: 'monthly-may',    path: '/monthly/2026/05/'    },
  { key: 'yearly-2026',    path: '/yearly/2026/'        },
];

/**
 * CSS injected into every page before screenshotting.
 * Hides dynamic content that changes every run and creates screenshot noise.
 */
const NOISE_SUPPRESSION_CSS = `
  /* Cost dashboard run date — changes every crawl */
  .cost-dashboard__date,
  [data-cost-date],
  .run-date,
  .last-updated { visibility: hidden !important; }

  /* Live run counters */
  .dynamic-counter,
  .repo-count,
  [data-live] { visibility: hidden !important; }

  /* Disable CSS animations / transitions for stable screenshots */
  *, *::before, *::after {
    animation-duration: 0s !important;
    transition-duration: 0s !important;
  }
`;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function pad(n) { return String(n).padStart(3, ' '); }

async function ensureDir(dir) {
  if (!existsSync(dir)) await mkdir(dir, { recursive: true });
}

async function captureScreenshot(page, url, viewport, theme, outPath) {
  await page.setViewportSize({ width: viewport.width, height: viewport.height });
  await page.emulateMedia({ colorScheme: theme });

  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 });
  } catch {
    // Fallback for Hugo pages that may not fully reach networkidle
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(800);
  }

  await page.addStyleTag({ content: NOISE_SUPPRESSION_CSS });
  // Extra settle time for web fonts
  await page.waitForTimeout(300);

  await page.screenshot({ path: outPath, fullPage: true });
  return true;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  await ensureDir(OUT_DIR);

  const browser = await chromium.launch({ headless: true });

  const results = [];
  let passed = 0;
  let failed = 0;

  console.log(`\n🎨 SquadScope Visual Verification`);
  console.log(`   Base URL : ${BASE_URL}`);
  console.log(`   Output   : ${OUT_DIR}`);
  console.log(`   Matrix   : ${PAGES.length} pages × ${VIEWPORTS.length} viewports × ${THEMES.length} themes = ${PAGES.length * VIEWPORTS.length * THEMES.length} screenshots\n`);

  for (const theme of THEMES) {
    for (const viewport of VIEWPORTS) {
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height },
        colorScheme: theme,
      });
      const page = await context.newPage();

      for (const pg of PAGES) {
        const filename = `${pg.key}-${viewport.name}-${theme}.png`;
        const outPath   = join(OUT_DIR, filename);
        const url       = `${BASE_URL}${pg.path}`;

        let status = '✅';
        let note   = '';

        try {
          await captureScreenshot(page, url, viewport, theme, outPath);
          passed++;
        } catch (err) {
          status = '❌';
          note   = err.message.split('\n')[0].slice(0, 60);
          failed++;
        }

        results.push({ page: pg.key, viewport: viewport.name, theme, status, note, filename });
        process.stdout.write(`  ${status}  ${filename.padEnd(45)}  ${note}\n`);
      }

      await context.close();
    }
  }

  await browser.close();

  // Summary table
  console.log('\n─────────────────────────────────────────────────────────────');
  console.log('  Page                Viewport   Light  Dark');
  console.log('─────────────────────────────────────────────────────────────');

  for (const pg of PAGES) {
    for (const vp of VIEWPORTS) {
      const light = results.find(r => r.page === pg.key && r.viewport === vp.name && r.theme === 'light');
      const dark  = results.find(r => r.page === pg.key && r.viewport === vp.name && r.theme === 'dark');
      const col1  = `${pg.key}`.padEnd(20);
      const col2  = vp.name.padEnd(10);
      console.log(`  ${col1}${col2} ${light?.status ?? '?'}      ${dark?.status ?? '?'}`);
    }
  }

  console.log('─────────────────────────────────────────────────────────────');
  console.log(`  Total: ${pad(passed + failed)} screenshots — ${pad(passed)} passed, ${pad(failed)} failed`);
  console.log(`  Output dir: ${OUT_DIR}\n`);

  // Write a manifest
  const manifest = {
    generatedAt: DATE_SLUG,
    baseUrl: BASE_URL,
    outDir: OUT_DIR,
    results,
  };
  await writeFile(join(OUT_DIR, 'manifest.json'), JSON.stringify(manifest, null, 2));
  console.log(`  Manifest written to ${join(OUT_DIR, 'manifest.json')}\n`);

  if (failed > 0) process.exit(1);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
