import { test, expect } from '@playwright/test';

const TEST_MEASUREMENT_ID = 'G-TEST-OBSERVATORY';

function desktopOnly(testInfo) {
  test.skip(
    testInfo.project.name !== 'desktop-light',
    'Analytics behavior is viewport-independent.',
  );
}

async function interceptGoogleEndpoints(page) {
  const requests = [];
  await page.route('https://www.googletagmanager.com/**', async (route) => {
    requests.push({ kind: 'script', url: route.request().url() });
    await route.fulfill({
      contentType: 'application/javascript',
      body: `
        window.SquadScopeGA4TestStubLoaded = true;
        function sendEvent(args) {
          if (args[0] === 'event') {
            var params = new URLSearchParams({ en: args[1] });
            Object.keys(args[2] || {}).forEach(function (key) {
              params.set('ep.' + key, args[2][key]);
            });
            fetch('https://www.google-analytics.com/g/collect?' + params, {
              mode: 'no-cors',
              keepalive: true
            });
          }
        }
        var queuedEntries = (window.dataLayer || []).slice();
        window.gtag = function () {
          window.dataLayer = window.dataLayer || [];
          window.dataLayer.push(arguments);
          sendEvent(arguments);
        };
        queuedEntries.forEach(sendEvent);
      `,
    });
  });
  await page.route('https://www.google-analytics.com/**', async (route) => {
    requests.push({ kind: 'collect', url: route.request().url() });
    await route.fulfill({ status: 204, body: '' });
  });
  return requests;
}

// These helpers also run against cross-origin subframes, where waitForFunction can bind
// to the frame's pre-navigation execution context and never resolve. expect.poll calls
// evaluate again on each attempt, so it always targets the frame's current context.
async function waitForConsentUi(page) {
  await expect
    .poll(
      () => page.evaluate(() => Boolean(window.CookieConsent && window.ObservatoryAnalytics)),
      { timeout: 15000 },
    )
    .toBe(true);
  return page.getByRole('dialog').first();
}

async function waitForGa4Stub(page) {
  await expect
    .poll(() => page.evaluate(() => window.SquadScopeGA4TestStubLoaded === true), {
      timeout: 15000,
    })
    .toBe(true);
}

async function acceptAnalytics(page) {
  const dialog = await waitForConsentUi(page);
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', { name: /accept all/i }).click();
  await expect(dialog).toBeHidden();
  await expect
    .poll(() => page.locator(`script[src*="gtag/js?id=${TEST_MEASUREMENT_ID}"]`).count())
    .toBe(1);
  await waitForGa4Stub(page);
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

async function analyticsCookies(page) {
  const cookies = await page.context().cookies();
  return cookies.filter(({ name }) => /^_ga/.test(name));
}

test('fresh and rejected consent send no analytics data', async ({ page }, testInfo) => {
  desktopOnly(testInfo);
  const requests = await interceptGoogleEndpoints(page);
  await page.goto('/state-of/open-source-ai-2026/');
  const dialog = await waitForConsentUi(page);
  const csvLink = 'a[href*="top-github-projects.csv"]';

  await clickWithoutNavigation(page, csvLink);
  expect(await customEvents(page)).toEqual([]);
  expect(requests).toEqual([]);
  expect(await analyticsCookies(page)).toEqual([]);

  await dialog.getByRole('button', { name: /reject all/i }).click();
  await expect(dialog).toBeHidden();
  await clickWithoutNavigation(page, csvLink);

  expect(await customEvents(page)).toEqual([]);
  expect(requests).toEqual([]);
  expect(await analyticsCookies(page)).toEqual([]);
  await expect
    .poll(async () => (await page.context().cookies()).map(({ name }) => name))
    .toContain('squadscope_cookie_consent');
});

test('acceptance, reload, and withdrawal enforce the analytics boundary', async ({
  page,
}, testInfo) => {
  desktopOnly(testInfo);
  const requests = await interceptGoogleEndpoints(page);
  const csvLink = 'a[href*="top-github-projects.csv"]';
  await page.goto('/state-of/open-source-ai-2026/');
  await acceptAnalytics(page);

  await clickWithoutNavigation(page, csvLink);
  await expect.poll(() => requests.filter(({ kind }) => kind === 'collect').length).toBe(1);
  expect(await customEvents(page)).toEqual([
    {
      name: 'dataset_download',
      payload: {
        dataset_id: 'open-source-ai-github-projects-2026',
        path: '/datasets/open-source-ai-github-projects-2026/top-github-projects.csv',
      },
    },
  ]);
  expect(requests.filter(({ kind }) => kind === 'script')).toHaveLength(1);
  expect(requests.find(({ kind }) => kind === 'collect').url).not.toContain('private');

  await page.context().addCookies([
    { name: '_ga', value: 'GA1.1.123.456', domain: '127.0.0.1', path: '/' },
    { name: '_ga_TEST', value: 'GS1.1.123.1.0.0.0', domain: '127.0.0.1', path: '/' },
  ]);
  await page.reload();
  await page.waitForFunction(() => window.CookieConsent && window.ObservatoryAnalytics);
  await expect(page.getByRole('dialog').first()).toBeHidden();
  await expect.poll(() => requests.filter(({ kind }) => kind === 'script').length).toBe(2);
  const initCalls = await page.evaluate(() =>
    (window.dataLayer || []).filter((entry) => entry[0] === 'config'),
  );
  expect(initCalls).toHaveLength(1);
  expect(initCalls[0][1]).toBe(TEST_MEASUREMENT_ID);

  await page.getByRole('button', { name: /manage cookies/i }).click();
  const preferences = page.getByRole('dialog').first();
  const analyticsToggle = preferences.getByRole('checkbox', { name: /analytics/i });
  await expect(analyticsToggle).toBeChecked();
  await analyticsToggle.uncheck();
  await preferences.getByRole('button', { name: /save preferences/i }).click();
  await expect(preferences).toBeHidden();

  await expect
    .poll(() => page.evaluate((id) => window[`ga-disable-${id}`], TEST_MEASUREMENT_ID))
    .toBe(true);
  await expect.poll(() => analyticsCookies(page)).toEqual([]);
  const eventCount = (await customEvents(page)).length;
  const collectCount = requests.filter(({ kind }) => kind === 'collect').length;
  await clickWithoutNavigation(page, csvLink);
  expect(await customEvents(page)).toHaveLength(eventCount);
  expect(requests.filter(({ kind }) => kind === 'collect')).toHaveLength(collectCount);
});

test('tool interactions use real handlers and bounded fields', async ({ page }, testInfo) => {
  desktopOnly(testInfo);
  await interceptGoogleEndpoints(page);
  await page.goto('/tools/star-velocity-explorer/');
  await acceptAnalytics(page);
  await expect(page.locator('[data-trend-status]')).not.toHaveText(/Loading static trend data/);

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

test('standalone frame uses only its own explicit analytics consent', async ({ page }, testInfo) => {
  desktopOnly(testInfo);
  const requests = await interceptGoogleEndpoints(page);
  const embedUrl = new URL(
    '/embeds/fastest-growing-ai-repositories-chart/',
    testInfo.project.use.baseURL,
  );
  const publisherUrl = new URL('/charts/embeddable-rankings/', embedUrl);
  publisherUrl.hostname = embedUrl.hostname === 'localhost' ? '127.0.0.1' : 'localhost';
  expect(publisherUrl.origin).not.toBe(embedUrl.origin);

  await page.goto(publisherUrl.href);
  await acceptAnalytics(page);
  const parentRequestCount = requests.length;
  const parentAnalyticsCookies = await analyticsCookies(page);
  expect(requests.filter(({ kind }) => kind === 'script')).toHaveLength(1);
  expect(parentAnalyticsCookies).toEqual([]);

  await page.locator('body').evaluate((body, src) => {
    const iframe = document.createElement('iframe');
    iframe.title = 'Cross-origin Claracle chart';
    iframe.src = src;
    iframe.referrerPolicy = 'no-referrer';
    body.appendChild(iframe);
  }, embedUrl.href);

  await expect
    .poll(() =>
      page
        .frames()
        .some((candidate) =>
          candidate.url().includes('/embeds/fastest-growing-ai-repositories-chart/'),
        ),
    )
    .toBe(true);
  const frame = page
    .frames()
    .find((candidate) =>
      candidate.url().includes('/embeds/fastest-growing-ai-repositories-chart/'),
    );
  expect(frame).toBeDefined();
  await waitForConsentUi(frame);

  expect(await customEvents(frame)).toEqual([]);
  await expect(frame.locator(`script[src*="gtag/js?id=${TEST_MEASUREMENT_ID}"]`)).toHaveCount(0);
  expect(requests.slice(parentRequestCount)).toEqual([]);
  expect(await analyticsCookies(page)).toEqual(parentAnalyticsCookies);

  await frame.evaluate(() => window.CookieConsent.acceptCategory('all'));
  await expect
    .poll(() => frame.evaluate(() => window.CookieConsent.acceptedCategory('analytics')))
    .toBe(true);
  await expect
    .poll(() => frame.locator(`script[src*="gtag/js?id=${TEST_MEASUREMENT_ID}"]`).count())
    .toBe(1);
  await waitForGa4Stub(frame);
  await expect
    .poll(() => requests.slice(parentRequestCount).filter(({ kind }) => kind === 'collect').length)
    .toBe(1);
  expect(requests.slice(parentRequestCount).filter(({ kind }) => kind === 'script')).toHaveLength(1);
  expect(await customEvents(frame)).toEqual([
    {
      name: 'chart_embed_view',
      payload: {
        chart_id: 'fastest-growing-ai-repositories-this-year',
        path: '/embeds/fastest-growing-ai-repositories-chart/',
      },
    },
  ]);
});
