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
const THRESHOLDS = {
  accessibility: 0.95,
  bestPractices: 0.95,
  cls: 0.1,
};

const PAGES = [
  { key: 'home', path: '/' },
  { key: 'weekly', path: '/weekly/2026/w22/' },
  { key: 'monthly', path: '/monthly/2026/05/' },
  { key: 'yearly', path: '/yearly/2026/' },
];

function ensureDir(path) {
  if (!existsSync(path)) {
    return mkdir(path, { recursive: true });
  }

  return Promise.resolve();
}

function runLighthouse(url) {
  const command = [
    'npx -y lighthouse',
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
    accessibility: report.categories.accessibility?.score ?? 0,
    bestPractices: report.categories['best-practices']?.score ?? 0,
    cls: report.audits['cumulative-layout-shift']?.numericValue ?? Number.POSITIVE_INFINITY,
  };
}

function getFailures(scores) {
  const failures = [];

  if (scores.accessibility < THRESHOLDS.accessibility) {
    failures.push(`a11y ${(scores.accessibility * 100).toFixed(0)} < 95`);
  }

  if (scores.bestPractices < THRESHOLDS.bestPractices) {
    failures.push(`best ${(scores.bestPractices * 100).toFixed(0)} < 95`);
  }

  if (scores.cls > THRESHOLDS.cls) {
    failures.push(`cls ${scores.cls.toFixed(3)} > 0.100`);
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
    const report = runLighthouse(url);
    const scores = getScores(report);
    const failures = getFailures(scores);
    const result = {
      page: page.key,
      url,
      accessibility: scores.accessibility,
      bestPractices: scores.bestPractices,
      cls: scores.cls,
      ok: failures.length === 0,
      failures,
    };

    results.push(result);
    await writeFile(join(OUTPUT_DIR, `${page.key}.json`), JSON.stringify(report, null, 2));
  }

  await writeFile(join(OUTPUT_DIR, 'summary.json'), JSON.stringify({ baseUrl: BASE_URL, thresholds: THRESHOLDS, results }, null, 2));

  console.log(`Lighthouse gates for ${BASE_URL}`);
  console.table(results.map(result => ({
    page: result.page,
    accessibility: formatPercent(result.accessibility),
    bestPractices: formatPercent(result.bestPractices),
    cls: formatCls(result.cls),
    status: result.ok ? 'PASS' : `FAIL (${result.failures.join(', ')})`,
  })));

  if (results.some(result => !result.ok)) {
    process.exit(1);
  }
}

main().catch(error => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
