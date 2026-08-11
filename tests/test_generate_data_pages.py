"""Tests for generated Data Observatory ranking pages."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import generate_data_pages

ROOT = Path(__file__).resolve().parents[1]
DATA_PAGES = [
    ROOT / "content/data/top-ai-repositories-this-month/index.md",
    ROOT / "content/data/fastest-growing-ai-repositories-this-year/index.md",
    ROOT / "content/data/most-starred-mcp-projects/index.md",
]


def repo_observation(
    *, topics: tuple[str, ...], description: str = ""
) -> generate_data_pages.RepoObservation:
    return generate_data_pages.RepoObservation(
        week="2026-W01",
        crawled_at=generate_data_pages.parse_datetime(None, "2026-W01"),
        source_bucket="trending_repos",
        source_path=ROOT / "data/raw/2026-W01.json",
        full_name="owner/project",
        display_name="owner/project",
        url="https://github.com/owner/project",
        description=description,
        language="Python",
        stars=100,
        forks=1,
        created_at="2026-01-01T00:00:00Z",
        topics=topics,
    )


def test_ai_topic_detection_uses_whole_tokens() -> None:
    assert not generate_data_pages.is_ai_project(repo_observation(topics=("blockchain",)))
    assert generate_data_pages.is_ai_project(repo_observation(topics=("ai",)))
    assert generate_data_pages.is_ai_project(repo_observation(topics=("machine-learning",)))


def test_missing_crawled_at_uses_stable_week_start() -> None:
    assert generate_data_pages.parse_datetime(None, "2026-W01").isoformat() == (
        "2025-12-29T00:00:00+00:00"
    )


def test_generation_is_deterministic_without_crawled_at(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scratch = ROOT / ".pytest-data-pages-determinism"
    if scratch.exists():
        shutil.rmtree(scratch)
    raw_dir = scratch / "data/raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "2026-W01.json").write_text(
        json_payload_without_crawled_at(),
        encoding="utf-8",
    )
    try:
        monkeypatch.setattr(generate_data_pages, "RAW_DIR", raw_dir)
        monkeypatch.setattr(generate_data_pages, "ARCHIVE_DIR", scratch / "data/archive")
        monkeypatch.setattr(generate_data_pages, "CONTENT_DIR", scratch / "content/data")

        first = generate_data_pages.build_pages()
        second = generate_data_pages.build_pages()

        assert first == second
    finally:
        if scratch.exists():
            shutil.rmtree(scratch)


def json_payload_without_crawled_at() -> str:
    return """{
  "week": "2026-W01",
  "trending_repos": [
    {
      "owner": "example",
      "name": "ai-tool",
      "full_name": "example/ai-tool",
      "description": "AI developer tool",
      "language": "Python",
      "stars": 100,
      "forks": 10,
      "created_at": "2026-01-01T00:00:00Z",
      "topics": ["ai"],
      "url": "javascript:alert(1)"
    }
  ],
  "new_repos": [],
  "metadata": {}
}
"""


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
    assert "ranking-table" in layout
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
        rendered = (destination / "data/top-ai-repositories-this-month/index.html").read_text(
            encoding="utf-8"
        )
        assert "Provenance" in rendered
        assert "BreadcrumbList" in rendered
    finally:
        if destination.exists():
            shutil.rmtree(destination)


def test_data_page_frontmatter_has_context_summary() -> None:
    content = DATA_PAGES[0].read_text(encoding="utf-8")

    assert "context_summary =" in content
    assert 'github_url = "https://github.com/' in content


def test_data_page_layout_renders_context_tooltip() -> None:
    layout = (ROOT / "layouts/data/single.html").read_text(encoding="utf-8")

    assert "data-context-summary" in layout
    assert 'role="tooltip"' in layout
    assert "Download JSON" in layout
