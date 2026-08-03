import assert from 'node:assert/strict';
import test from 'node:test';

import {
  getFailures,
  mapWithConcurrency,
  median,
  PAGES,
  THRESHOLDS,
} from '../scripts/design/lighthouse-gates.mjs';

test('median and thresholds retain the quality-gate contract', () => {
  assert.equal(median([0.95, 0.9, 0.92]), 0.92);
  assert.deepEqual(
    getFailures({
      performance: THRESHOLDS.performance,
      accessibility: THRESHOLDS.accessibility,
      bestPractices: THRESHOLDS.bestPractices,
      cls: THRESHOLDS.cls,
    }),
    [],
  );
  assert.deepEqual(
    getFailures({ performance: 0.89, accessibility: 0.94, bestPractices: 0.94, cls: 0.101 })
      .map((failure) => failure.category),
    ['performance', 'accessibility', 'best-practices', 'cumulative-layout-shift'],
  );
  assert.equal(PAGES.length, 9);
});

test('bounded page work preserves input order', async () => {
  let active = 0;
  let maximumActive = 0;
  const completionOrder = [];
  const pages = ['slow', 'fast', 'middle', 'last'];

  const results = await mapWithConcurrency(pages, 2, async (page, index) => {
    active += 1;
    maximumActive = Math.max(maximumActive, active);
    await new Promise((resolve) => setTimeout(resolve, [30, 5, 15, 1][index]));
    completionOrder.push(page);
    active -= 1;
    return page.toUpperCase();
  });

  assert.equal(maximumActive, 2);
  assert.notDeepEqual(completionOrder, pages);
  assert.deepEqual(results, ['SLOW', 'FAST', 'MIDDLE', 'LAST']);
});