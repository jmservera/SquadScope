import { test, expect } from '@playwright/test';

const NOISE_SUPPRESSION_CSS = `
  .cost-dashboard__date,
  [data-cost-date],
  .run-date,
  .last-updated { visibility: hidden !important; }
  .dynamic-counter, .repo-count, [data-live] { visibility: hidden !important; }
  *, *::before, *::after { animation-duration: 0s !important; transition-duration: 0s !important; }
`;

const VIEWPORTS = [
  { width: 320, height: 568 },
  { width: 360, height: 640 },
  { width: 390, height: 844 },
  { width: 414, height: 896 },
  { width: 768, height: 1024 },
];

const PAGES = [
  { key: 'home', label: 'home', path: '/' },
  { key: 'weekly', label: 'weekly', path: '/weekly/2026/w22/' },
  { key: 'monthly', label: 'monthly', path: '/monthly/2026/05/' },
  { key: 'yearly', label: 'yearly', path: '/yearly/2026/' },
];

async function settle(page) {
  await page.waitForLoadState('networkidle').catch(() => page.waitForTimeout(1000));
  await page.addStyleTag({ content: NOISE_SUPPRESSION_CSS });
  await page.waitForTimeout(300);
}

async function openPage(page, path, viewport) {
  await page.setViewportSize(viewport);
  await page.emulateMedia({ colorScheme: 'light' });
  await page.goto(path);
  await settle(page);
}

function formatViewport({ width }) {
  return `${width}px`;
}

function skipNonMatrixProject(testInfo) {
  test.skip(testInfo.project.name !== 'desktop-light', 'A11y matrix is defined in-spec.');
}

for (const pageConfig of PAGES) {
  test.describe(pageConfig.label, () => {
    for (const viewport of VIEWPORTS) {
      const viewportLabel = formatViewport(viewport);

      test(`${pageConfig.label} — no horizontal overflow at ${viewportLabel}`, async ({ page }, testInfo) => {
        skipNonMatrixProject(testInfo);
        await openPage(page, pageConfig.path, viewport);

        const hasNoOverflow = await page.evaluate(() => {
          const root = document.documentElement;
          return root.scrollWidth <= root.clientWidth;
        });

        expect(hasNoOverflow).toBe(true);
      });

      test(`${pageConfig.label} — tap targets ≥ 44x44 at ${viewportLabel}`, async ({ page }, testInfo) => {
        skipNonMatrixProject(testInfo);
        await openPage(page, pageConfig.path, viewport);

        const violations = await page.evaluate(() => {
          const minSize = 44;
          const round = value => Math.round(value * 10) / 10;

          return Array.from(document.querySelectorAll('a, button'))
            .filter(element => !element.hasAttribute('data-small-ok'))
            .map(element => {
              const rect = element.getBoundingClientRect();
              const style = window.getComputedStyle(element);

              if (
                style.display === 'none' ||
                style.visibility === 'hidden' ||
                rect.width <= 0 ||
                rect.height <= 0
              ) {
                return null;
              }

              if (rect.width >= minSize && rect.height >= minSize) {
                return null;
              }

              const label =
                element.getAttribute('aria-label') ||
                element.textContent?.replace(/\s+/g, ' ').trim() ||
                element.getAttribute('href') ||
                element.tagName.toLowerCase();

              return {
                tag: element.tagName.toLowerCase(),
                label,
                width: round(rect.width),
                height: round(rect.height),
              };
            })
            .filter(Boolean);
        });

        expect(violations, `Tap target violations: ${JSON.stringify(violations, null, 2)}`).toEqual([]);
      });

      if (pageConfig.key === 'home' && viewport.width <= 414) {
        test(`${pageConfig.label} — main content starts within 600px at ${viewportLabel}`, async ({ page }, testInfo) => {
          skipNonMatrixProject(testInfo);
          await openPage(page, pageConfig.path, viewport);

          const mainTop = await page.evaluate(() => {
            const main =
              document.querySelector('.main') ||
              document.querySelector('main') ||
              document.querySelector('#main-content');

            if (!main) {
              throw new Error('No main content element found');
            }

            return main.getBoundingClientRect().top;
          });

          expect(mainTop).toBeLessThanOrEqual(600);
        });
      }
    }
  });
}
