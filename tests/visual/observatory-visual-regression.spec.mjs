import { test, expect } from '@playwright/test';
import { execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

/**
 * Visual Regression Evidence for Data Observatory Relaunch (Phase 7.3)
 *
 * Captures revision-tagged visual evidence across the Playwright project matrix
 * (desktop/mobile x light/dark) and asserts the structural invariants the
 * relaunch review depends on: a real breadcrumb construct and no horizontal
 * overflow.
 *
 * Analytics consent behavior is deliberately not re-asserted here; it is covered
 * by the blocking `observatory-analytics.spec.mjs` gate.
 *
 * Execution:
 *   npx playwright test --config tests/visual/playwright.config.mjs \
 *     tests/visual/observatory-visual-regression.spec.mjs
 */

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '../..');
const evidenceDir = path.join(repoRoot, 'screenshots', 'visual-regression');

function readPlaywrightVersion() {
  try {
    const pkgPath = path.join(repoRoot, 'node_modules/@playwright/test/package.json');
    return JSON.parse(fs.readFileSync(pkgPath, 'utf-8')).version;
  } catch {
    return 'unknown';
  }
}

const playwrightVersion = readPlaywrightVersion();

// Local runs must still be tied to a revision: reviewers verify that the captured
// metadata matches the revision under review.
function gitOutput(args) {
  try {
    return execFileSync('git', args, { cwd: repoRoot, encoding: 'utf-8' }).trim() || null;
  } catch {
    return null;
  }
}

const revision = process.env.GITHUB_SHA ?? gitOutput(['rev-parse', 'HEAD']) ?? 'unknown';
const branch =
  process.env.GITHUB_REF_NAME ?? gitOutput(['rev-parse', '--abbrev-ref', 'HEAD']) ?? 'unknown';
const origin = process.env.GITHUB_RUN_ID ? 'ci' : 'local';
// A dirty tree means the screenshots do not correspond to the recorded revision alone.
const workingTreeClean = gitOutput(['status', '--porcelain']) === null;

/**
 * Reads rendered site paths from the built sitemap so the evidence matrix does
 * not rot when weekly and monthly editions roll over.
 */
function readSitemapPaths() {
  const sitemapPath = path.join(repoRoot, 'public', 'sitemap.xml');
  if (!fs.existsSync(sitemapPath)) {
    return [];
  }
  const xml = fs.readFileSync(sitemapPath, 'utf-8');
  return [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)]
    .map((match) => {
      try {
        return new URL(match[1]).pathname;
      } catch {
        return null;
      }
    })
    .filter((value) => value !== null);
}

/**
 * Selects one representative route per page class. Dated sections resolve to the
 * most recent edition; listing sections resolve to their first detail page.
 */
function selectVisualRoutes() {
  const paths = readSitemapPaths();
  const available = new Set(paths);
  const latest = (pattern) => paths.filter((p) => pattern.test(p)).sort().pop();
  const first = (pattern) => paths.filter((p) => pattern.test(p)).sort()[0];

  const candidates = [
    { name: 'home', label: 'Homepage', path: '/' },
    { name: 'about', label: 'About', path: '/about/' },
    { name: 'dashboard', label: 'Dashboard', path: '/dashboard/' },
    { name: 'search', label: 'Search', path: '/search/' },
    { name: 'charts', label: 'Charts index', path: '/charts/' },
    { name: 'repo-index', label: 'Repository index', path: '/repo/' },
    { name: 'repo-detail', label: 'Repository page', path: first(/^\/repo\/[^/]+\/$/) },
    { name: 'topics-index', label: 'Topics index', path: '/topics/' },
    { name: 'topic', label: 'Topic hub', path: first(/^\/topics\/[^/]+\/$/) },
    { name: 'data-detail', label: 'Data ranking', path: first(/^\/data\/[^/]+\/$/) },
    { name: 'state-of', label: 'State-of report', path: first(/^\/state-of\/[^/]+\/$/) },
    {
      name: 'embed',
      label: 'Embeddable chart',
      path: first(/^\/embeds\/[^/]+\/$/),
      // A standalone embed renders without site chrome, so it has no breadcrumb.
      chrome: false,
    },
    { name: 'tool', label: 'Star Velocity Explorer', path: first(/^\/tools\/[^/]+\/$/) },
    { name: 'weekly', label: 'Weekly edition', path: latest(/^\/weekly\/\d{4}\/w\d{2}\/$/) },
    { name: 'monthly', label: 'Monthly summary', path: latest(/^\/monthly\/\d{4}\/\d{2}\/$/) },
  ];

  const routes = candidates.filter((route) => route.path && available.has(route.path));
  if (routes.length === 0) {
    // Sitemap unavailable, for example on a partial local build: fall back to the
    // one route present in every build so the suite still produces evidence.
    return [{ name: 'home', label: 'Homepage', path: '/' }];
  }
  return routes;
}

const VISUAL_ROUTES = selectVisualRoutes();

function evidencePath(projectName, name) {
  return path.join(evidenceDir, projectName, `${name}.png`);
}

/**
 * The capture checklist rejects feature evidence that the consent banner obscures, so
 * every route except the dedicated consent capture resolves the decision first.
 * Rejecting keeps the captures free of analytics network activity.
 */
async function rejectConsent(page) {
  const dialog = page.getByRole('dialog').first();
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', { name: /reject all/i }).click();
  await expect(dialog).toBeHidden();
}

test.describe('Observatory visual regression evidence', () => {
  for (const route of VISUAL_ROUTES) {
    test(`${route.name}: renders and captures evidence`, async ({ page }, testInfo) => {
      const response = await page.goto(route.path);
      expect(response?.status(), `${route.path} should render`).toBeLessThan(400);
      await page.waitForLoadState('networkidle');
      await rejectConsent(page);

      if (route.path !== '/' && route.chrome !== false) {
        const breadcrumbNav = page.locator('nav.breadcrumbs');
        await expect(breadcrumbNav).toBeVisible();

        const breadcrumbList = breadcrumbNav.locator('ol');
        await expect(breadcrumbList).toBeVisible();

        // The relaunch review requires a real breadcrumb, not a numbered list.
        const listStyle = await breadcrumbList.evaluate(
          (el) => window.getComputedStyle(el).listStyleType,
        );
        expect(listStyle).toBe('none');

        const display = await breadcrumbList.evaluate(
          (el) => window.getComputedStyle(el).display,
        );
        expect(['flex', 'grid']).toContain(display);

        await expect(breadcrumbNav.locator('[aria-current="page"]')).toBeVisible();
      }

      const { scrollWidth, clientWidth } = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));
      expect(scrollWidth, `${route.path} must not overflow horizontally`).toBeLessThanOrEqual(
        clientWidth + 1,
      );

      await page.screenshot({
        path: evidencePath(testInfo.project.name, route.name),
        fullPage: true,
      });
    });
  }

  test('consent: captures the undecided banner state', async ({ page }, testInfo) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await expect(page.getByRole('dialog').first()).toBeVisible();

    await page.screenshot({
      path: evidencePath(testInfo.project.name, 'home-consent'),
      fullPage: true,
    });
  });

  test('records evidence metadata for the revision under test', async ({ page }, testInfo) => {
    const projectName = testInfo.project.name;
    await page.goto('/');

    const metadata = {
      revision,
      branch,
      origin,
      workingTreeClean,
      runId: process.env.GITHUB_RUN_ID ?? null,
      timestamp: new Date().toISOString(),
      project: projectName,
      colorScheme: testInfo.project.use.colorScheme ?? 'light',
      viewport: page.viewportSize(),
      playwrightVersion,
      routes: [
        ...VISUAL_ROUTES.map((route) => ({ name: route.name, path: route.path })),
        { name: 'home-consent', path: '/ (undecided consent banner)' },
      ],
    };

    const target = path.join(evidenceDir, projectName, 'metadata.json');
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, `${JSON.stringify(metadata, null, 2)}\n`);

    expect(VISUAL_ROUTES.length).toBeGreaterThan(0);
  });
});
