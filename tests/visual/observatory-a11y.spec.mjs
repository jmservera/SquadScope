import AxeBuilder from '@axe-core/playwright';
import { test, expect } from '@playwright/test';

const OBSERVATORY_PAGES = [
  { key: 'topic', path: '/topics/ai-coding-agents/' },
  { key: 'data', path: '/data/fastest-growing-ai-repositories-this-year/' },
  { key: 'repository', path: '/repo/' },
  { key: 'chart', path: '/embeds/fastest-growing-ai-repositories-chart/' },
  { key: 'tool', path: '/tools/star-velocity-explorer/' },
];

async function settle(page) {
  await page.waitForLoadState('networkidle').catch(() => page.waitForTimeout(1000));
}

async function expectVisibleFocus(locator) {
  await locator.focus();
  await expect(locator).toBeFocused();
  await expect
    .poll(() =>
      locator.evaluate((element) => {
        const style = getComputedStyle(element);
        return (
          element.matches(':focus-visible') &&
          (style.outlineStyle !== 'none' || style.boxShadow !== 'none')
        );
      }),
    )
    .toBe(true);
}

async function firstSameOriginLink(page, selector = 'main a[href]') {
  const links = page.locator(selector);
  const index = await links.evaluateAll((elements) =>
    elements.findIndex((element) => {
      const url = new URL(element.href, location.href);
      return url.origin === location.origin && url.hash === '';
    }),
  );
  expect(index, `Expected a same-origin link matching ${selector}`).toBeGreaterThanOrEqual(0);
  return links.nth(index);
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

  const hasVisibleDialogFocus = () =>
    dialog.evaluate((element) => {
      const activeElement = element.ownerDocument.activeElement;
      return Boolean(activeElement && element.contains(activeElement) && activeElement.matches(':focus-visible'));
    });

  await page.keyboard.press('Tab');
  await expect.poll(hasVisibleDialogFocus).toBe(true);
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

test('fresh consent stays within the mobile viewport below the page header', async ({ page }, testInfo) => {
  test.skip(!testInfo.project.name.startsWith('mobile-'), 'Mobile projects cover consent geometry.');
  await page.context().clearCookies();
  await page.goto('/topics/ai-coding-agents/');

  const dialog = page.getByRole('dialog').first();
  await expect(dialog).toBeVisible();
  for (const name of [/accept all/i, /reject all/i, /customize/i]) {
    await expect(dialog.getByRole('button', { name })).toBeVisible();
  }

  const geometry = await dialog.evaluate((element) => {
    const bounds = element.getBoundingClientRect();
    const header = document.querySelector('.post-header');
    const description = element.querySelector('.cm__desc');
    return {
      dialog: { top: bounds.top, right: bounds.right, bottom: bounds.bottom, left: bounds.left },
      headerBottom: header?.getBoundingClientRect().bottom ?? 0,
      viewport: { width: window.innerWidth, height: window.innerHeight },
      descriptionScrollable: description
        ? description.scrollHeight > description.clientHeight
          ? ['auto', 'scroll'].includes(getComputedStyle(description).overflowY)
          : true
        : false,
    };
  });

  expect(geometry.dialog.left).toBeGreaterThanOrEqual(0);
  expect(geometry.dialog.right).toBeLessThanOrEqual(geometry.viewport.width);
  expect(geometry.dialog.top).toBeGreaterThanOrEqual(geometry.headerBottom);
  expect(geometry.dialog.bottom).toBeLessThanOrEqual(geometry.viewport.height);
  expect(geometry.descriptionScrollable).toBe(true);
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

test('embed repository summaries support focus, touch, and Escape', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop-light', 'One Chromium project covers disclosure behavior.');
  await page.goto('/embeds/fastest-growing-ai-repositories-chart/');

  const wrapper = page.locator('[data-observatory-tooltip]').first();
  const link = wrapper.getByRole('link');
  const tooltip = wrapper.locator('[role="tooltip"]');
  await expect(link).toHaveAttribute('href', /^https:\/\/github\.com\//);
  await expect(link).toHaveAttribute('aria-describedby', await tooltip.getAttribute('id'));

  await link.focus();
  await expect(tooltip).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(tooltip).toBeHidden();
  await expect(link).not.toBeFocused();

  await link.dispatchEvent('touchstart');
  await expect(wrapper).toHaveClass(/is-open/);
  await page.keyboard.press('Escape');
  await expect(wrapper).not.toHaveClass(/is-open/);
});

test('current provenance and repository-context disclosures work by pointer and keyboard', async ({
  page,
}, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop-light', 'One Chromium project covers disclosures.');

  await page.goto('/repo/');
  const repository = page.locator('[data-repository-explorer]');
  await expect(repository.locator('[data-repo-record]').first()).toBeVisible();
  await expect(repository.locator('.repository-index__summary').first()).toHaveText(/\S/);
  await expect(repository.locator('.repository-index__evidence').first()).toContainText(
    /weekly observations|W\d{2}/i,
  );
  await expect(page.getByRole('link', { name: /download.*repository dataset/i })).toBeVisible();
  await expect(page.getByRole('link', { name: /read the methodology/i })).toBeVisible();

  await page.goto('/data/fastest-growing-ai-repositories-this-year/');
  await expect(page.locator('.data-page__provenance')).toBeVisible();
  const rankingLink = page.locator('.ranking-table__repo-link').first();
  const rankingTooltip = rankingLink.locator('xpath=following-sibling::*[@role="tooltip"]');
  await rankingLink.hover();
  await expect(rankingTooltip).toBeVisible();
  await rankingLink.focus();
  await expect(rankingTooltip).toBeVisible();

  await page.goto('/embeds/fastest-growing-ai-repositories-chart/');
  const embedLink = page.locator('[data-observatory-tooltip] a').first();
  const embedTooltip = embedLink.locator('xpath=following-sibling::*[@role="tooltip"]');
  await embedLink.hover();
  await expect(embedTooltip).toBeVisible();
  await embedLink.focus();
  await expect(embedTooltip).toBeVisible();

  await page.goto('/charts/embeddable-rankings/');
  const panel = page.locator('.observatory-chart__embed-panel');
  await expect(panel).toContainText(/attribution and a backlink/i);
  await expect(panel.locator('[data-embed-snippet]')).toContainText('<iframe');
  await expectVisibleFocus(panel.locator('[data-copy-target]'));
});

test('copy reports success and failure while retaining keyboard focus', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop-light', 'One Chromium project covers copy behavior.');
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {
        writeText: async (value) => {
          if (window.__copyShouldFail) {
            throw new Error('clipboard denied');
          }
          window.__copiedText = value;
        },
      },
    });
  });
  await page.goto('/charts/embeddable-rankings/');

  const button = page.locator('[data-copy-target]');
  const status = page.locator('[data-copy-status]');
  await button.focus();
  await page.keyboard.press('Enter');
  await expect(status).toHaveText('Embed snippet copied to the clipboard.');
  await expect(button).toBeFocused();
  await expect
    .poll(() => page.evaluate(() => window.__copiedText))
    .toContain('<iframe');

  await page.evaluate(() => {
    window.__copyShouldFail = true;
  });
  await page.keyboard.press('Enter');
  await expect(status).toHaveText('Copy failed. Select and copy the embed snippet manually.');
  await expect(button).toBeFocused();
});

test('reduced motion and touch input preserve repository-context operation', async ({
  page,
}, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile-light', 'Mobile Chromium covers touch equivalence.');
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/embeds/fastest-growing-ai-repositories-chart/');

  const wrapper = page.locator('[data-observatory-tooltip]').first();
  const link = wrapper.getByRole('link');
  const tooltip = wrapper.locator('[role="tooltip"]');
  await link.tap();
  await expect(tooltip).toBeVisible();
  const transitionSeconds = await tooltip.evaluate((element) =>
    Math.max(
      ...getComputedStyle(element)
        .transitionDuration.split(',')
        .map((duration) => Number.parseFloat(duration) * (duration.includes('ms') ? 0.001 : 1)),
    ),
  );
  expect(transitionSeconds).toBeLessThanOrEqual(0.001);
  await page.keyboard.press('Escape');
  await expect(tooltip).toBeHidden();
});

const FOCUS_SURFACES = [
  { key: 'home', path: '/', selector: 'main a[href]' },
  { key: 'article', path: '/topics/ai-coding-agents/', selector: 'article a[href]' },
  { key: 'repository', path: '/repo/', selector: 'main a[href]' },
  {
    key: 'ranking',
    path: '/data/fastest-growing-ai-repositories-this-year/',
    selector: 'main a[href]',
  },
  {
    key: 'embed',
    path: '/embeds/fastest-growing-ai-repositories-chart/',
    selector: 'a[href]',
  },
  { key: 'navigation', path: '/', selector: 'header a[href]' },
];

test('representative internal links retain visible focus across required viewports', async ({
  page,
}, testInfo) => {
  const modes = {
    'desktop-light': 'desktop',
    'mobile-light': 'mobile',
    'desktop-dark': 'zoom-200',
  };
  const mode = modes[testInfo.project.name];
  test.skip(!mode, 'Three projects cover desktop, mobile, and 200% equivalent viewport.');
  if (mode === 'zoom-200') {
    await page.setViewportSize({ width: 640, height: 800 });
  }

  for (const surface of FOCUS_SURFACES) {
    await page.goto(surface.path);
    await settle(page);
    const link = await firstSameOriginLink(page, surface.selector);
    await expectVisibleFocus(link);
    await page.screenshot({
      path: testInfo.outputPath(`${mode}-${surface.key}-focus.png`),
      fullPage: false,
    });
  }
});