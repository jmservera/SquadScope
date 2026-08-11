#!/usr/bin/env node

import { execFile } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { existsSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);

const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const LIGHTHOUSE_BIN = join(REPO_ROOT, 'node_modules', '.bin', 'lighthouse');

// Under WSL, chrome-launcher rewrites TEMP to a Windows-style path and then mkdirs
// it with a relative join, creating a literal 'C:\\Users\\...' directory in the
// child's working directory. Running from a scratch directory keeps that out of the
// repository; TMPDIR does not help because that code path never reads it.
const CHILD_CWD = mkdtempSync(join(tmpdir(), 'lighthouse-cwd-'));
process.on('exit', () => rmSync(CHILD_CWD, { recursive: true, force: true }));

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
const CONCURRENCY = Math.max(1, Number.parseInt(getArg('--concurrency', '3'), 10) || 3);
export const THRESHOLDS = {
  performance: 0.9,
  accessibility: 0.95,
  bestPractices: 0.95,
  cls: 0.1,
};

export const PAGES = [
  { key: 'home', path: '/' },
  { key: 'about', path: '/about/' },
  { key: 'weekly', path: '/weekly/2026/w22/' },
  { key: 'monthly', path: '/monthly/2026/05/' },
  { key: 'yearly', path: '/yearly/2026/' },
  { key: 'topic', path: '/topics/ai-coding-agents/' },
  { key: 'data', path: '/data/fastest-growing-ai-repositories-this-year/' },
  { key: 'repository', path: '/repo/' },
  { key: 'chart', path: '/embeds/fastest-growing-ai-repositories-chart/' },
  { key: 'tool', path: '/tools/star-velocity-explorer/' },
];

function ensureDir(path) {
  if (!existsSync(path)) {
    return mkdir(path, { recursive: true });
  }

  return Promise.resolve();
}

async function runLighthouse(url) {
  if (!existsSync(LIGHTHOUSE_BIN)) {
    throw new Error(
      `Lighthouse binary not found at ${LIGHTHOUSE_BIN}. Install it first, for example ` +
        'npm install --no-save --no-package-lock lighthouse@12.8.2',
    );
  }

  const lighthouseArgs = [
    url,
    '--quiet',
    '--output=json',
    '--output-path=stdout',
    '--only-categories=accessibility,best-practices,performance',
    '--chrome-flags=--headless --no-sandbox',
    '--form-factor=mobile',
  ];

  const { stdout } = await execFileAsync(LIGHTHOUSE_BIN, lighthouseArgs, {
    cwd: CHILD_CWD,
    encoding: 'utf8',
    maxBuffer: 20 * 1024 * 1024,
  });

  return JSON.parse(stdout);
}

function getScores(report) {
  return {
    performance: report.categories.performance?.score ?? 0,
    accessibility: report.categories.accessibility?.score ?? 0,
    bestPractices: report.categories['best-practices']?.score ?? 0,
    cls: report.audits['cumulative-layout-shift']?.numericValue ?? Number.POSITIVE_INFINITY,
  };
}

export function median(values) {
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
}

// Run Lighthouse RUNS times and return the median score per metric plus the report
// whose performance is closest to the median (kept as the uploaded artifact).
async function runLighthouseMedian(url) {
  const runs = [];

  for (let attempt = 0; attempt < RUNS; attempt += 1) {
    const report = await runLighthouse(url);
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

export function getFailures(scores) {
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

export async function mapWithConcurrency(items, concurrency, mapper) {
  const results = new Array(items.length);
  let nextIndex = 0;

  async function worker() {
    while (nextIndex < items.length) {
      const index = nextIndex;
      nextIndex += 1;
      results[index] = await mapper(items[index], index);
    }
  }

  const workerCount = Math.min(Math.max(1, concurrency), items.length);
  await Promise.all(Array.from({ length: workerCount }, () => worker()));
  return results;
}

async function main() {
  await ensureDir(OUTPUT_DIR);

  const results = await mapWithConcurrency(PAGES, CONCURRENCY, async (page) => {
    const url = `${BASE_URL}${page.path}`;
    const { report, scores } = await runLighthouseMedian(url);
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

    await writeFile(join(OUTPUT_DIR, `${page.key}.json`), JSON.stringify(report, null, 2));
    return result;
  });

  await writeFile(join(OUTPUT_DIR, 'summary.json'), JSON.stringify({ baseUrl: BASE_URL, runs: RUNS, concurrency: CONCURRENCY, thresholds: THRESHOLDS, results }, null, 2));

  console.log(`Lighthouse gates for ${BASE_URL} (median of ${RUNS} run${RUNS === 1 ? '' : 's'}, ${CONCURRENCY} pages at a time)`);
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

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === resolve(process.argv[1]);
if (isMain) {
  main().catch(error => {
    console.error(error instanceof Error ? error.message : error);
    process.exit(1);
  });
}
