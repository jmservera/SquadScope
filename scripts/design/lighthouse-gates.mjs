#!/usr/bin/env node

import { execSync } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join } from 'node:path';

const args = process.argv.slice(2);

function getArg(name, fallback) {
  const index = args.indexOf(name);
  return index !== -1 && args[index + 1] ? args[index + 1] : fallback;
}

const BASE_URL = getArg('--base', 'http://localhost:1313/SquadScope').replace(/\/$/, '');
const OUTPUT_DIR = join('screenshots', 'lighthouse-results');
// Single Lighthouse runs vary by several points on shared CI runners; the median of
// repeated runs is Lighthouse's recommended stable measurement. Thresholds are unchanged.
const RUNS = Math.max(1, Number.parseInt(getArg('--runs', '3'), 10) || 3);
const THRESHOLDS = {
  performance: 0.9,
  accessibility: 0.95,
  bestPractices: 0.95,
  cls: 0.1,
};

const PAGES = [
  { key: 'home', path: '/' },
  { key: 'weekly', path: '/weekly/2026/w22/' },
  { key: 'monthly', path: '/monthly/2026/05/' },
  { key: 'yearly', path: '/yearly/2026/' },
  { key: 'topic', path: '/topics/ai-coding-agents/' },
  { key: 'data', path: '/data/fastest-growing-ai-repositories-this-year/' },
  { key: 'repository', path: '/repo/anthropics-claude-code/' },
  { key: 'chart', path: '/embeds/fastest-growing-ai-repositories-chart/' },
  { key: 'tool', path: '/tools/star-velocity-explorer/' },
];

function ensureDir(path) {
  if (!existsSync(path)) {
    return mkdir(path, { recursive: true });
  }

  return Promise.resolve();
}

function runLighthouse(url) {
  const command = [
    'npx --no-install lighthouse',
    JSON.stringify(url),
    '--quiet',
    '--output=json',
    '--output-path=stdout',
    '--only-categories=accessibility,best-practices,performance',
    '--chrome-flags="--headless --no-sandbox"',
    '--form-factor=mobile',
  ].join(' ');

  const output = execSync(command, {
    cwd: process.cwd(),
    encoding: 'utf8',
    maxBuffer: 20 * 1024 * 1024,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  return JSON.parse(output);
}

function getScores(report) {
  return {
    performance: report.categories.performance?.score ?? 0,
    accessibility: report.categories.accessibility?.score ?? 0,
    bestPractices: report.categories['best-practices']?.score ?? 0,
    cls: report.audits['cumulative-layout-shift']?.numericValue ?? Number.POSITIVE_INFINITY,
  };
}

function median(values) {
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
}

// Run Lighthouse RUNS times and return the median score per metric plus the report
// whose performance is closest to the median (kept as the uploaded artifact).
function runLighthouseMedian(url) {
  const runs = [];

  for (let attempt = 0; attempt < RUNS; attempt += 1) {
    const report = runLighthouse(url);
    runs.push({ report, scores: getScores(report) });
  }

  const scores = {
    performance: median(runs.map(run => run.scores.performance)),
    accessibility: median(runs.map(run => run.scores.accessibility)),
    bestPractices: median(runs.map(run => run.scores.bestPractices)),
    cls: median(runs.map(run => run.scores.cls)),
  };

  const representative = runs.reduce((best, current) =>
    Math.abs(current.scores.performance - scores.performance)
      < Math.abs(best.scores.performance - scores.performance)
      ? current
      : best);

  return { report: representative.report, scores };
}

function getFailures(scores) {
  const failures = [];

  if (scores.performance < THRESHOLDS.performance) {
    failures.push({ category: 'performance', actual: scores.performance, minimum: THRESHOLDS.performance });
  }

  if (scores.accessibility < THRESHOLDS.accessibility) {
    failures.push({ category: 'accessibility', actual: scores.accessibility, minimum: THRESHOLDS.accessibility });
  }

  if (scores.bestPractices < THRESHOLDS.bestPractices) {
    failures.push({ category: 'best-practices', actual: scores.bestPractices, minimum: THRESHOLDS.bestPractices });
  }

  if (scores.cls > THRESHOLDS.cls) {
    failures.push({ category: 'cumulative-layout-shift', actual: scores.cls, maximum: THRESHOLDS.cls });
  }

  return failures;
}

function formatPercent(score) {
  return `${(score * 100).toFixed(0)}%`;
}

function formatCls(value) {
  return Number.isFinite(value) ? value.toFixed(3) : 'n/a';
}

async function main() {
  await ensureDir(OUTPUT_DIR);

  const results = [];

  for (const page of PAGES) {
    const url = `${BASE_URL}${page.path}`;
    const { report, scores } = runLighthouseMedian(url);
    const failures = getFailures(scores);
    const result = {
      page: page.key,
      route: page.path,
      url,
      performance: scores.performance,
      accessibility: scores.accessibility,
      bestPractices: scores.bestPractices,
      cls: scores.cls,
      ok: failures.length === 0,
      failures,
    };

    results.push(result);
    await writeFile(join(OUTPUT_DIR, `${page.key}.json`), JSON.stringify(report, null, 2));
  }

  await writeFile(join(OUTPUT_DIR, 'summary.json'), JSON.stringify({ baseUrl: BASE_URL, runs: RUNS, thresholds: THRESHOLDS, results }, null, 2));

  console.log(`Lighthouse gates for ${BASE_URL} (median of ${RUNS} run${RUNS === 1 ? '' : 's'})`);
  console.table(results.map(result => ({
    page: result.page,
    performance: formatPercent(result.performance),
    accessibility: formatPercent(result.accessibility),
    bestPractices: formatPercent(result.bestPractices),
    cls: formatCls(result.cls),
    status: result.ok ? 'PASS' : `FAIL (${result.failures.map(failure => failure.category).join(', ')})`,
  })));

  if (results.some(result => !result.ok)) {
    process.exit(1);
  }
}

main().catch(error => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
