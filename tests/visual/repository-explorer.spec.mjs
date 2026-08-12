import { test, expect } from '@playwright/test';

const PAGE = '/repo/';
const records = [
  {
    full_name: 'example/alpha',
    github_url: 'https://github.com/example/alpha',
    context_summary: 'Alpha AI skills repository.',
    language: 'Python',
    topics: ['ai-skills', 'agents'],
    status: 'active',
    first_seen_period: '2026-W29',
    last_seen_period: '2026-W33',
    recent_momentum: 40,
    star_history: [{ period: '2026-W33', stars: 140 }],
  },
  {
    full_name: 'example/beta',
    github_url: 'https://github.com/example/beta',
    context_summary: 'Beta AI skills repository.',
    language: 'TypeScript',
    topics: ['ai-skills'],
    status: 'retained',
    first_seen_period: '2026-W28',
    last_seen_period: '2026-W32',
    recent_momentum: 30,
    star_history: [{ period: '2026-W32', stars: 130 }],
  },
  {
    full_name: 'example/gamma',
    github_url: 'https://github.com/example/gamma',
    context_summary: 'Gamma systems repository.',
    language: 'Rust',
    topics: ['systems'],
    status: 'archived',
    first_seen_period: '2026-W27',
    last_seen_period: '2026-W31',
    recent_momentum: 20,
    star_history: [{ period: '2026-W31', stars: 120 }],
  },
  {
    full_name: 'example/delta',
    github_url: 'https://github.com/example/delta',
    context_summary: 'Delta tooling repository.',
    language: 'Python',
    topics: ['tooling'],
    status: 'active',
    first_seen_period: '2026-W26',
    last_seen_period: '2026-W30',
    recent_momentum: 10,
    star_history: [{ period: '2026-W30', stars: 110 }],
  },
  {
    full_name: 'example/epsilon',
    github_url: 'https://github.com/example/epsilon',
    context_summary: 'Epsilon historical repository.',
    language: 'Go',
    topics: ['systems'],
    status: 'disabled',
    first_seen_period: '2026-W20',
    last_seen_period: '2026-W29',
    recent_momentum: 0,
    star_history: [{ period: '2026-W29', stars: 100 }],
  },
];

async function mockRepositories(page) {
  await page.route('**/data/repositories.json', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        schema_version: '1.0.0',
        artifact_type: 'repositories',
        covered_period: { start: '2026-07-13', end: '2026-08-10', label: '2026-W29–2026-W33' },
        records,
      }),
    }),
  );
}

async function expectVisibleRepositories(explorer, expectedNames) {
  const visible = explorer.locator('[data-repo-record]:visible');
  await expect(visible).toHaveCount(expectedNames.length);
  await expect(visible.locator('.repository-index__heading')).toHaveText(expectedNames);
  await expect(explorer.locator('[data-repo-result-status]')).toHaveText(
    `Showing ${expectedNames.length} of ${records.length} repositories.`,
  );
}

test.beforeEach(async ({}, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop-light', 'One Chromium project covers filter semantics.');
});

test('URL topic filter hides non-matching repositories and keeps count aligned', async ({ page }) => {
  await mockRepositories(page);
  await page.addInitScript(() => history.replaceState({}, '', `${location.pathname}?topic=ai-skills`));
  await page.goto(PAGE);

  const explorer = page.locator('[data-repository-explorer]');
  await expect(explorer.locator('[data-repo-topic]')).toHaveValue('ai-skills');
  await expectVisibleRepositories(explorer, ['example/alpha', 'example/beta']);
});

test('every filter dimension and reset update visible records semantically', async ({ page }) => {
  await mockRepositories(page);
  await page.goto(PAGE);
  const explorer = page.locator('[data-repository-explorer]');
  const reset = explorer.locator('[data-repo-reset]');

  await explorer.locator('[data-repo-language]').selectOption('Python');
  await expectVisibleRepositories(explorer, ['example/alpha', 'example/delta']);
  await reset.click();

  await explorer.locator('[data-repo-topic]').selectOption('systems');
  await expectVisibleRepositories(explorer, ['example/gamma', 'example/epsilon']);
  await reset.click();

  await explorer.locator('[data-repo-status]').selectOption('archived');
  await expectVisibleRepositories(explorer, ['example/gamma']);
  await reset.click();

  await explorer.locator('[data-repo-period]').selectOption('current');
  await expectVisibleRepositories(explorer, ['example/alpha']);
  await reset.click();

  await explorer.locator('[data-repo-period]').selectOption('recent');
  await expectVisibleRepositories(explorer, [
    'example/alpha',
    'example/beta',
    'example/gamma',
    'example/delta',
  ]);
  await reset.click();

  await explorer.locator('[data-repo-search]').fill('historical');
  await expectVisibleRepositories(explorer, ['example/epsilon']);
  await reset.click();

  await expectVisibleRepositories(explorer, records.map((record) => record.full_name));
  await expect(explorer.locator('[data-repo-search]')).toBeFocused();
  await expect(page).toHaveURL(PAGE);
});

test('combined keyboard-operated filters preserve URL and visible result state', async ({ page }) => {
  await mockRepositories(page);
  await page.goto(PAGE);
  const explorer = page.locator('[data-repository-explorer]');

  await explorer.locator('[data-repo-search]').focus();
  await page.keyboard.press('Tab');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('ArrowDown');
  await expect(explorer.locator('[data-repo-language]')).toHaveValue('Python');
  await page.keyboard.press('Tab');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('ArrowDown');
  await expect(explorer.locator('[data-repo-topic]')).toHaveValue('ai-skills');
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');
  await page.keyboard.press('End');
  await expect(explorer.locator('[data-repo-period]')).toHaveValue('recent');

  await expectVisibleRepositories(explorer, ['example/alpha']);
  await expect(page).toHaveURL(/\?language=Python&topic=ai-skills&period=recent$/);
});
