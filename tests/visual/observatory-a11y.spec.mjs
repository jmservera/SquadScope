import AxeBuilder from '@axe-core/playwright';
import { test, expect } from '@playwright/test';

const OBSERVATORY_PAGES = [
  { key: 'topic', path: '/topics/ai-coding-agents/' },
  { key: 'data', path: '/data/fastest-growing-ai-repositories-this-year/' },
  { key: 'repository', path: '/repo/anthropics-claude-code/' },
  { key: 'chart', path: '/embeds/fastest-growing-ai-repositories-chart/' },
  { key: 'tool', path: '/tools/star-velocity-explorer/' },
];

async function settle(page) {
  await page.waitForLoadState('networkidle').catch(() => page.waitForTimeout(1000));
}

for (const pageConfig of OBSERVATORY_PAGES) {
  test(`${pageConfig.key} has no serious WCAG 2.1 A/AA violations`, async ({ page }) => {
    await page.goto(pageConfig.path);
    await settle(page);

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();
    const blockingViolations = results.violations.filter(({ impact }) =>
      ['serious', 'critical'].includes(impact),
    );

    expect(
      blockingViolations,
      `${pageConfig.path} axe violations: ${JSON.stringify(blockingViolations, null, 2)}`,
    ).toEqual([]);
  });

  test(`${pageConfig.key} has no responsive horizontal overflow`, async ({ page }) => {
    await page.goto(pageConfig.path);
    await settle(page);

    const overflow = await page.evaluate(() => ({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
    }));
    expect(overflow.scrollWidth, `${pageConfig.path} overflow: ${JSON.stringify(overflow)}`).toBeLessThanOrEqual(
      overflow.clientWidth,
    );
  });
}

test('tool controls have labels and work by keyboard', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop-light', 'One Chromium project covers keyboard semantics.');
  await page.goto('/tools/star-velocity-explorer/');
  await settle(page);

  for (const selector of ['[data-trend-search]', '[data-trend-language]', '[data-trend-topic]']) {
    const control = page.locator(selector);
    await expect(control).toHaveAccessibleName(/\S/);
    await control.focus();
    await expect(control).toBeFocused();
    const visibleFocus = await control.evaluate((element) => {
      const style = getComputedStyle(element);
      return style.outlineStyle !== 'none' || style.boxShadow !== 'none';
    });
    expect(visibleFocus, `${selector} must retain a visible focus indicator`).toBe(true);
  }

  await page.locator('[data-trend-search]').fill('anthropics');
  await expect(page.locator('[data-trend-results]')).not.toBeEmpty();
});

test('consent modal traps keyboard focus and restores it when closed', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop-light', 'One Chromium project covers modal keyboard behavior.');
  await page.context().clearCookies();
  await page.goto('/topics/ai-coding-agents/');

  const dialog = page.getByRole('dialog').first();
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole('button', { name: /accept all/i })).toBeVisible();
  await expect(dialog.getByRole('button', { name: /reject all/i })).toBeVisible();
  await expect(dialog.getByRole('button', { name: /customize/i })).toBeVisible();

  await page.keyboard.press('Tab');
  await expect(dialog.locator(':focus')).toBeVisible();
  await dialog.getByRole('button', { name: /reject all/i }).click();
  await expect(dialog).toBeHidden();

  const manageCookies = page.getByRole('button', { name: /manage cookies/i });
  await manageCookies.focus();
  await manageCookies.press('Enter');
  const preferences = page.getByRole('dialog').first();
  await expect(preferences).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(preferences).toBeHidden();
  await expect(manageCookies).toBeFocused();
});

test('breadcrumb is unique, semantic, marker-free, and wrapping', async ({ page }) => {
  await page.goto('/topics/ai-coding-agents/');
  await settle(page);

  const breadcrumbs = page.locator('nav.breadcrumbs[aria-label="Breadcrumb"]');
  await expect(breadcrumbs).toHaveCount(1);
  await expect(breadcrumbs.locator(':scope > ol')).toHaveCount(1);
  await expect(breadcrumbs.locator('li a')).not.toHaveCount(0);
  await expect(breadcrumbs.locator('li:last-child [aria-current="page"]')).toHaveCount(1);
  await expect(breadcrumbs.locator('li:last-child [aria-current="page"]')).toHaveText(/\S/);
  await expect(breadcrumbs.locator('li:last-child a')).toHaveCount(0);

  const schemaBreadcrumbCount = await page
    .locator('script[type="application/ld+json"]')
    .evaluateAll((scripts) =>
      scripts.filter((script) => JSON.parse(script.textContent || '{}')['@type'] === 'BreadcrumbList')
        .length,
    );
  expect(schemaBreadcrumbCount).toBe(1);

  const itemCount = await breadcrumbs.locator('li').count();
  const separators = breadcrumbs.locator('.breadcrumb-separator[aria-hidden="true"]');
  await expect(separators).toHaveCount(itemCount - 1);

  const styles = await breadcrumbs.locator(':scope > ol').evaluate((list) => {
    const style = getComputedStyle(list);
    return {
      display: style.display,
      flexWrap: style.flexWrap,
      listStyleType: style.listStyleType,
    };
  });
  expect(styles).toEqual({ display: 'flex', flexWrap: 'wrap', listStyleType: 'none' });

  const overflow = await breadcrumbs.evaluate((nav) => ({
    documentClientWidth: document.documentElement.clientWidth,
    documentScrollWidth: document.documentElement.scrollWidth,
    navClientWidth: nav.clientWidth,
    navScrollWidth: nav.scrollWidth,
  }));
  expect(overflow.navScrollWidth).toBeLessThanOrEqual(overflow.navClientWidth);
  expect(overflow.documentScrollWidth).toBeLessThanOrEqual(overflow.documentClientWidth);
});

test('chart exposes an accessible image alternative and source caption', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop-light', 'One Chromium project covers chart semantics.');
  await page.goto('/embeds/fastest-growing-ai-repositories-chart/');

  const chart = page.locator('[data-observatory-chart-id]');
  await expect(chart.getByRole('img')).toHaveAccessibleName(/fastest-growing|repositories/i);
  await expect(chart.locator('figcaption')).toContainText(/Source:/);
});