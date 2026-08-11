from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def test_repository_summary_is_current_and_schema_valid() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_repository_summary.py", "--from-crawl", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(
        (ROOT / "data/observatory/repository_summary.json").read_text(encoding="utf-8")
    )
    envelope_schema = json.loads(
        (ROOT / "data/schemas/observatory-envelope.schema.json").read_text(encoding="utf-8")
    )
    record_schema = json.loads(
        (ROOT / "data/schemas/repository-record.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator(envelope_schema).validate(payload)
    validator = Draft202012Validator(record_schema)
    for record in payload["records"]:
        validator.validate(record)


def test_repository_page_renders_complete_no_javascript_index() -> None:
    if shutil.which("hugo") is None:
        pytest.skip("hugo binary is not installed in this test environment")

    destination = ROOT / "public-test-repository-explorer"
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
        rendered = (destination / "repo/index.html").read_text(encoding="utf-8")
        payload = json.loads(
            (ROOT / "data/observatory/repository_summary.json").read_text(encoding="utf-8")
        )
        assert rendered.count("data-repo-record") == len(payload["records"])
        assert "data-repository-explorer" in rendered
        assert "Download the versioned repository dataset" in rendered
        assert "https://github.com/2dust/v2rayN" in rendered
        assert "repository-explorer.min." in rendered
    finally:
        shutil.rmtree(destination, ignore_errors=True)


def test_client_resets_invalid_state_and_reports_empty_results() -> None:
    if shutil.which("node") is None:
        pytest.skip("node is not installed in this test environment")

    result = subprocess.run(
        ["node", "-e", _node_smoke_script()],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def _node_smoke_script() -> str:
    return r"""
const fs = require('fs');
const vm = require('vm');
const script = fs.readFileSync('assets/js/repository-explorer.js', 'utf8');

class Element {
  constructor(attributes = {}) {
    this.attributes = attributes;
    this.value = '';
    this.textContent = '';
    this.hidden = false;
    this.children = [];
    this.listeners = {};
  }
  getAttribute(name) { return this.attributes[name] || ''; }
  querySelector(selector) { return this.map[selector] || null; }
  querySelectorAll(selector) { return selector === '[data-repo-record]' ? this.children : []; }
  addEventListener(name, listener) { this.listeners[name] = listener; }
  appendChild(child) {
    this.children = this.children.filter((item) => item !== child);
    this.children.push(child);
  }
  focus() {}
}

const list = new Element();
list.children = [
  new Element({
    'data-name': 'example/alpha',
    'data-search': 'example alpha python',
    'data-language': 'python',
    'data-topics': 'ai|tools',
    'data-status': 'active',
    'data-last-period': '2026-W33',
    'data-recent': 'true',
    'data-momentum': '10',
    'data-stars': '100',
    'data-appearances': '4',
  }),
  new Element({
    'data-name': 'example/beta',
    'data-search': 'example beta rust',
    'data-language': 'rust',
    'data-topics': 'systems',
    'data-status': 'archived',
    'data-last-period': '2026-W30',
    'data-recent': 'false',
    'data-momentum': '2',
    'data-stars': '200',
    'data-appearances': '8',
  }),
];

const root = new Element({'data-latest-period': '2026-W33'});
root.map = {
  '[data-repo-search]': new Element(),
  '[data-repo-language]': new Element(),
  '[data-repo-topic]': new Element(),
  '[data-repo-status]': new Element(),
  '[data-repo-period]': new Element(),
  '[data-repo-sort]': new Element(),
  '[data-repo-reset]': new Element(),
  '[data-repo-results]': list,
  '[data-repo-result-status]': new Element(),
};
root.map['[data-repo-period]'].value = 'all';
root.map['[data-repo-sort]'].value = 'momentum';

let pushed = 0;
let replaced = 0;
global.window = {
  location: {search: '?period=invalid&sort=invalid', pathname: '/repo/'},
  history: {
    replaceState: () => { replaced += 1; },
    pushState: () => { pushed += 1; },
  },
  addEventListener: () => {},
  clearTimeout: clearTimeout,
  setTimeout: (callback) => { callback(); return 1; },
};
global.document = {
  addEventListener: () => {},
  querySelectorAll: () => [],
};
global.URLSearchParams = URLSearchParams;
vm.runInThisContext(script);

window.initRepositoryExplorer(root);
if (root.map['[data-repo-period]'].value !== 'all') {
  throw new Error('invalid period was not reset');
}
if (root.map['[data-repo-sort]'].value !== 'momentum') {
  throw new Error('invalid sort was not reset');
}
root.map['[data-repo-search]'].value = 'no-match';
root.listeners.input();
if (!root.map['[data-repo-result-status]'].textContent.includes('No repositories')) {
  throw new Error('empty-result guidance was not rendered');
}
if (replaced !== 1 || pushed !== 1) {
  throw new Error(`unexpected history writes: replace=${replaced}, push=${pushed}`);
}
console.log('ok');
"""
