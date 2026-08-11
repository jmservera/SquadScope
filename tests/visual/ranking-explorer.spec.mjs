import { test, expect } from '@playwright/test';

const PAGE = '/data/fastest-growing-ai-repositories-this-year/';
const records = [
  {
    rank: 1,
    full_name: 'example/alpha',
    github_url: 'https://github.com/example/alpha',
    metric_value: 20,
    metric_label: '+20 stars',
    comparison_label: '10 → 30 stars',
    language: 'Python',
    context_summary: 'Alpha summary for accessible disclosure.',
  },
  {
    rank: 2,
    full_name: 'example/beta',
    github_url: 'https://github.com/example/beta',
    metric_value: 10,
    metric_label: '+10 stars',
    comparison_label: '5 → 15 stars',
    language: 'TypeScript',
    context_summary: 'Beta summary for accessible disclosure.',
  },
];

function payload(overrides = {}) {
  return {
    schema_version: '1.0.0',
    records,
    ...overrides,
  };
}

async function mockRanking(page, body, status = 200) {
  await page.route('**/data/rankings/*.json', (route) =>
    route.fulfill({
      status,
      contentType: 'application/json',
      body: typeof body === 'string' ? body : JSON.stringify(body),
    }),
  );
}

test.beforeEach(async ({}, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop-light', 'One Chromium project covers interactions.');
});

test('filters, URL state, reset, and rerendered tooltips remain operable', async ({ page }) => {
  await mockRanking(page, payload());
  await page.addInitScript(() => {
    if (location.pathname.includes('/data/fastest-growing-ai-repositories-this-year/')) {
      history.replaceState({}, '', `${location.pathname}?q=beta&sort=name&lang=Rust`);
    }
  });
  await page.goto(PAGE);

  const explorer = page.locator('[data-ranking-explorer]');
  await expect(explorer.locator('[data-ranking-status]')).toHaveText('Showing 1 of 2 repositories.');
  await expect(explorer.locator('[data-ranking-search]')).toHaveValue('beta');
  await expect(explorer.locator('[data-ranking-language]')).toHaveValue('');
  await expect(page).toHaveURL(/\?sort=name&q=beta$/);
  await expect(explorer.locator('.ranking-results__item')).toHaveCount(1);

  await explorer.locator('[data-ranking-search]').fill('alpha');
  await expect(page).toHaveURL(/\?sort=name&q=alpha$/);
  const alpha = explorer.getByRole('link', { name: 'example/alpha' });
  const alphaTooltip = alpha.locator('xpath=following-sibling::*[@role="tooltip"]');
  await alpha.focus();
  await expect(alphaTooltip).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(alphaTooltip).toBeHidden();

  await alpha.dispatchEvent('touchstart');
  await expect(alpha.locator('xpath=..')).toHaveClass(/is-open/);
  await page.keyboard.press('Escape');

  await explorer.locator('[data-ranking-reset]').click();
  await expect(page).toHaveURL(PAGE);
  await expect(explorer.locator('.ranking-results__item')).toHaveCount(2);
  await expect(explorer.locator('[data-ranking-search]')).toBeFocused();
});

test('malformed and future datasets preserve the server-rendered fallback', async ({ page }) => {
  await mockRanking(page, '{not-json');
  await page.goto(PAGE);
  const explorer = page.locator('[data-ranking-explorer]');
  await expect(explorer.locator('[data-ranking-error]')).toBeVisible();
  await expect(explorer.locator('table tbody tr')).not.toHaveCount(0);

  await page.unroute('**/data/rankings/*.json');
  await mockRanking(page, payload({ records: [{ ...records[0], github_url: 'not-a-url' }] }));
  await page.reload();
  await expect(explorer.locator('[data-ranking-error]')).toBeVisible();
  await expect(explorer.locator('[data-ranking-status]')).toHaveText('Ranking data is malformed.');
  await expect(explorer.locator('table tbody tr')).not.toHaveCount(0);

  await page.unroute('**/data/rankings/*.json');
  await mockRanking(page, payload({ schema_version: '2.0.0' }));
  await page.reload();
  await expect(explorer.locator('[data-ranking-future-version]')).toBeVisible();
  await expect(explorer.locator('table tbody tr')).not.toHaveCount(0);
});

test('unavailable datasets expose a clear warning and preserve SSR facts', async ({ page }) => {
  await mockRanking(page, {}, 503);
  await page.goto(PAGE);
  const explorer = page.locator('[data-ranking-explorer]');
  await expect(explorer.locator('[data-ranking-unavailable]')).toBeVisible();
  await expect(explorer.locator('[data-ranking-status]')).toContainText('server-rendered table');
  await expect(explorer.locator('table tbody tr')).not.toHaveCount(0);
});
