"""Tests for generated Data Observatory ranking pages."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA_PAGES = [
    ROOT / "content/data/top-ai-repositories-this-month/index.md",
    ROOT / "content/data/fastest-growing-ai-repositories-this-year/index.md",
    ROOT / "content/data/most-starred-mcp-projects/index.md",
]


def test_data_pages_are_regenerated_from_artifacts() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_data_pages.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("page", DATA_PAGES)
def test_data_page_frontmatter_has_provenance(page: Path) -> None:
    content = page.read_text(encoding="utf-8")

    assert "metric_definition =" in content
    assert re.search(r'as_of_week = "\d{4}-W\d{2}"', content)
    assert 'methodology_url = "/methodology/"' in content
    assert "source =" in content
    assert "[[ranking]]" in content
    assert "python3 scripts/generate_data_pages.py" in content


def test_data_page_layout_renders_provenance_and_ranking_table() -> None:
    layout = (ROOT / "layouts/data/single.html").read_text(encoding="utf-8")

    assert "Provenance" in layout
    assert "Metric" in layout
    assert "Source" in layout
    assert "Methodology" in layout
    assert "<table>" in layout
    assert ".Params.ranking" in layout


def test_hugo_builds_generated_data_pages_when_available() -> None:
    if shutil.which("hugo") is None:
        pytest.skip("hugo binary is not installed in this test environment")

    destination = ROOT / "public-test-data-pages"
    if destination.exists():
        shutil.rmtree(destination)
    result = subprocess.run(
        ["hugo", "--minify", "--destination", str(destination)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        assert result.returncode == 0, result.stderr
        rendered = (
            destination / "data/top-ai-repositories-this-month/index.html"
        ).read_text(encoding="utf-8")
        assert "Provenance" in rendered
        assert "BreadcrumbList" in rendered
    finally:
        if destination.exists():
            shutil.rmtree(destination)
