import { test, expect } from '@playwright/test';

function desktopOnly(testInfo) {
  test.skip(
    testInfo.project.name !== 'desktop-light',
    'Analytics behavior is viewport-independent.',
  );
}

async function installEventRecorder(page) {
  await page.waitForFunction(() => window.CookieConsent && window.ObservatoryAnalytics);
  await page.evaluate(() => {
    delete window.dataLayer;
    window.gtag = (...args) => {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push(args);
    };
  });
}

async function customEvents(page) {
  return page.evaluate(() =>
    (window.dataLayer || [])
      .filter((entry) => entry[0] === 'event')
      .map((entry) => ({ name: entry[1], payload: entry[2] })),
  );
}

async function clickWithoutNavigation(page, selector) {
  await page.locator(selector).evaluate((link) => {
    link.addEventListener('click', (event) => event.preventDefault(), { once: true });
    link.click();
  });
}

test('dataset events require current consent and contain bounded fields', async ({
  page,
}, testInfo) => {
  desktopOnly(testInfo);
  const analyticsRequests = [];
  page.on('request', (request) => {
    if (request.url().includes('google-analytics.com/g/collect')) {
      analyticsRequests.push(request.url());
    }
  });

  await page.goto('/state-of/open-source-ai-2026/');
  await installEventRecorder(page);
  const csvLink = 'a[href*="top-github-projects.csv"]';
  await page.locator(csvLink).evaluate((link) => {
    link.href = `${link.href}?repository=private-owner/private-repository`;
  });

  await clickWithoutNavigation(page, csvLink);
  expect(await customEvents(page)).toEqual([]);
  expect(analyticsRequests).toEqual([]);

  await page.evaluate(() => window.ObservatoryAnalytics.setConsent(true));
  await clickWithoutNavigation(page, csvLink);
  expect(await customEvents(page)).toEqual([
    {
      name: 'dataset_download',
      payload: {
        dataset_id: 'open-source-ai-github-projects-2026',
        path: '/datasets/open-source-ai-github-projects-2026/top-github-projects.csv',
      },
    },
  ]);

  await page.evaluate(() => window.ObservatoryAnalytics.setConsent(false));
  await clickWithoutNavigation(page, csvLink);
  expect(await customEvents(page)).toHaveLength(1);
});

test('tool interactions never include repository names or search input', async ({
  page,
}, testInfo) => {
  desktopOnly(testInfo);
  await page.goto('/tools/star-velocity-explorer/');
  await installEventRecorder(page);
  await expect(page.locator('[data-trend-status]')).not.toHaveText(/Loading static trend data/);
  await page.evaluate(() => window.ObservatoryAnalytics.setConsent(true));

  const search = page.locator('[data-trend-search]');
  await search.fill('private-owner/private-repository?token=secret');

  const events = await customEvents(page);
  const searchEvent = events.find((event) => event.payload.action === 'search');
  expect(searchEvent).toEqual({
    name: 'tool_interaction',
    payload: {
      tool_id: 'star-velocity-explorer',
      action: 'search',
      path: '/tools/star-velocity-explorer/',
    },
  });
  expect(JSON.stringify(events)).not.toContain('private-owner');
  expect(JSON.stringify(events)).not.toContain('private-repository');
  expect(JSON.stringify(events)).not.toContain('token=secret');
});

test('standalone chart view fires only after consent', async ({ page }, testInfo) => {
  desktopOnly(testInfo);
  await page.goto('/embeds/fastest-growing-ai-repositories-chart/');
  await installEventRecorder(page);

  expect(await customEvents(page)).toEqual([]);
  await page.evaluate(() => window.ObservatoryAnalytics.setConsent(true));

  expect(await customEvents(page)).toEqual([
    {
      name: 'chart_embed_view',
      payload: {
        chart_id: 'fastest-growing-ai-repositories-this-year',
        path: '/embeds/fastest-growing-ai-repositories-chart/',
      },
    },
  ]);
});
