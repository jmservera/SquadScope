from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import export_trend_explorer_data

ROOT = Path(__file__).resolve().parents[1]


def test_trend_explorer_export_is_deterministic() -> None:
    scratch = ROOT / ".pytest-trend-explorer"
    data_root = scratch / "data"
    raw_dir = data_root / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "2026-W01.json").write_text(sample_week("2026-W01", 10), encoding="utf-8")
    (raw_dir / "2026-W02.json").write_text(sample_week("2026-W02", 25), encoding="utf-8")
    try:
        first = export_trend_explorer_data.build_payload(data_root)
        second = export_trend_explorer_data.build_payload(data_root)

        assert first == second
        assert first["repositories"][0]["repository"] == "example/ai-tool"
        assert first["repositories"][0]["observed_star_change"] == 15
        assert first["source_files"] == [
            ".pytest-trend-explorer/data/raw/2026-W01.json",
            ".pytest-trend-explorer/data/raw/2026-W02.json",
        ]
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def sample_week(week: str, stars: int) -> str:
    return json.dumps(
        {
            "week": week,
            "trending_repos": [
                {
                    "owner": "example",
                    "name": "ai-tool",
                    "full_name": "example/ai-tool",
                    "url": "https://github.com/example/ai-tool",
                    "description": "AI developer tool",
                    "language": "Python",
                    "stars": stars,
                    "topics": ["ai", "developer-tools"],
                }
            ],
            "new_repos": [],
        }
    )


def test_trend_explorer_export_is_current() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/export_trend_explorer_data.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout


def test_tool_page_renders_static_client_bootstrap() -> None:
    if shutil.which("hugo") is None:
        pytest.skip("hugo binary is not installed in this test environment")

    destination = ROOT / "public-test-trend-explorer"
    shutil.rmtree(destination, ignore_errors=True)
    result = subprocess.run(
        ["hugo", "--minify", "--destination", str(destination)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        assert result.returncode == 0, result.stderr
        rendered = (destination / "tools/star-velocity-explorer/index.html").read_text(
            encoding="utf-8"
        )
        assert "Star Velocity Explorer" in rendered
        assert "/tools/star-velocity-explorer.json" in rendered
        assert "Loading static trend data" in rendered
    finally:
        shutil.rmtree(destination, ignore_errors=True)


def test_client_handles_malformed_and_empty_data_without_uncaught_errors() -> None:
    if shutil.which("node") is None:
        pytest.skip("node is not installed in this test environment")

    result = subprocess.run(
        ["node", "-e", node_smoke_script()],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def node_smoke_script() -> str:
    return r"""
const fs = require('fs');
const vm = require('vm');
const script = fs.readFileSync('assets/js/star-velocity-explorer.js', 'utf8');

class Element {
  constructor() {
    this.textContent = '';
    this.value = '';
    this.children = [];
    this.attributes = {};
    this.style = {};
    this.className = '';
    this.listeners = {};
  }
  querySelector(selector) { return this.map[selector] || null; }
  getAttribute(name) { return this.attributes[name] || ''; }
  setAttribute(name, value) { this.attributes[name] = value; }
  appendChild(child) { this.children.push(child); return child; }
  append(...children) { this.children.push(...children); }
  addEventListener(name, listener) { this.listeners[name] = listener; }
  matches(selector) { return this.selector === selector; }
}

function rootFor(payload) {
  const root = new Element();
  root.attributes['data-source'] = '/tools/star-velocity-explorer.json';
  root.map = {
    '[data-trend-status]': new Element(),
    '[data-trend-results]': new Element(),
    '[data-trend-language]': new Element(),
    '[data-trend-topic]': new Element(),
    '[data-trend-search]': new Element(),
  };
  global.fetch = async () => ({ ok: true, json: async () => payload });
  return root;
}

global.window = {};
global.document = {
  addEventListener: () => {},
  querySelectorAll: () => [],
  createElement: () => new Element(),
};
vm.runInThisContext(script);

(async () => {
  const malformed = rootFor({ broken: true });
  await window.initTrendExplorer(malformed);
  if (!malformed.map['[data-trend-status]'].textContent.includes('malformed')) {
    throw new Error('malformed payload was not handled');
  }
  const empty = rootFor({ repositories: [] });
  await window.initTrendExplorer(empty);
  if (!empty.map['[data-trend-status]'].textContent.includes('No trend data')) {
    throw new Error('empty payload was not handled');
  }
  const unsafe = rootFor({
    language_filters: [],
    topic_filters: [],
    repositories: [{
      repository: 'example/bad',
      url: 'javascript:alert(1)',
      primary_language: 'JavaScript',
      observed_star_change: 1,
      latest_stars: 2,
      series: [{ week: '2026-W01', stars: 1 }],
    }],
  });
  await window.initTrendExplorer(unsafe);
  const link = unsafe.map['[data-trend-results]'].children[0].children[0];
  if (link.href !== '#') {
    throw new Error('unsafe repository URL was not sanitized');
  }
  const scaled = rootFor({
    language_filters: ['Python', 'Rust'],
    topic_filters: [],
    repositories: [
      {
        repository: 'example/scale',
        url: 'https://github.com/example/scale',
        primary_language: 'Python',
        observed_star_change: 75,
        latest_stars: 100,
        series: [
          { week: '2026-W01', stars: 25 },
          { week: '2026-W02', stars: 50 },
          { week: '2026-W03', stars: 100 },
        ],
      },
      {
        repository: 'example/larger',
        url: 'https://github.com/example/larger',
        primary_language: 'Rust',
        observed_star_change: 0,
        latest_stars: 200,
        series: [{ week: '2026-W03', stars: 200 }],
      },
    ],
  });
  await window.initTrendExplorer(scaled);
  const firstSparkline = scaled.map['[data-trend-results]'].children[0].children[2];
  const initialHeights = firstSparkline.children.map((bar) => bar.style.height);
  if (initialHeights.join(',') !== '12.5%,25%,50%') {
    throw new Error(`dataset scale produced unexpected heights: ${initialHeights}`);
  }
  if (!firstSparkline.attributes['aria-label'].includes('dataset maximum of 200 stars')) {
    throw new Error('sparkline semantics do not describe the dataset scale');
  }
  scaled.map['[data-trend-language]'].value = 'Python';
  scaled.map['[data-trend-language]'].selector = '[data-trend-language]';
  scaled.listeners.change({ target: scaled.map['[data-trend-language]'] });
  const filteredHeights = scaled.map['[data-trend-results]'].children[0].children[2].children
    .map((bar) => bar.style.height);
  if (filteredHeights.join(',') !== initialHeights.join(',')) {
    throw new Error('filtering changed the dataset-wide scale');
  }
  console.log('ok');
})().catch((error) => { console.error(error); process.exit(1); });
"""
