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


def identity_artifact(
    week: str, repos: list[dict], *, crawled_at: str | None = None
) -> generate_data_pages.WeekArtifact:
    return generate_data_pages.WeekArtifact(
        week=week,
        crawled_at=generate_data_pages.parse_datetime(crawled_at, week),
        path=ROOT / f"data/raw/{week}.json",
        payload={"trending_repos": repos},
    )


def test_stable_identity_latest_dedup_does_not_merge_historical_growth() -> None:
    artifacts = [
        identity_artifact(
            "2026-W43",
            [{"id": 1157102282, "full_name": "diegosouzapw/OmniRoute", "stars": 78202}],
        ),
        identity_artifact(
            "2026-W44",
            [{"id": 1157102282, "full_name": "cheaper-inference/OmniRoute", "stars": 81193}],
        ),
    ]
    observations = generate_data_pages.collect_observations(artifacts)
    latest = list(generate_data_pages.latest_by_repo(observations).values())
    assert [(obs.full_name, obs.stars) for obs in latest] == [
        ("cheaper-inference/OmniRoute", 81193)
    ]
    history = list(generate_data_pages.grouped_by_repo(observations).values())
    assert len(history) == 2
    assert all(len(group) == 1 for group in history)


def test_stable_identity_uses_latest_crawl_before_highest_star_count() -> None:
    artifacts = [
        identity_artifact(
            "2026-W44",
            [{"id": 42, "full_name": "old/project", "stars": 200}],
            crawled_at="2026-10-26T01:00:00Z",
        ),
        identity_artifact(
            "2026-W44",
            [
                {
                    "id": "42",
                    "full_name": "new/project",
                    "stars": 100,
                    "description": "Latest MCP description",
                    "language": "Rust",
                    "topics": ["mcp"],
                }
            ],
            crawled_at="2026-10-26T02:00:00Z",
        ),
    ]
    for ordering in (artifacts, artifacts[::-1]):
        observations = generate_data_pages.collect_observations(ordering)
        latest = list(generate_data_pages.latest_by_repo(observations).values())
        assert [(obs.full_name, obs.stars) for obs in latest] == [("new/project", 100)]
        assert latest[0].description == "Latest MCP description"
        assert latest[0].language == "Rust"
        assert latest[0].topics == ("mcp",)
        assert latest[0].url == "https://github.com/new/project"


def test_stable_identity_deduplicates_names_across_source_buckets() -> None:
    artifact = identity_artifact(
        "2026-W44",
        [{"id": 42, "full_name": "old/project", "stars": 100}],
    )
    artifact.payload["new_repos"] = [
        {"id": 42, "full_name": "new/project", "stars": 200},
        {"id": 42, "full_name": "new/project", "stars": 150},
    ]
    observations = generate_data_pages.collect_observations([artifact])
    latest = generate_data_pages.latest_by_repo(observations).values()
    assert [(obs.full_name, obs.stars) for obs in latest] == [("new/project", 200)]


@pytest.mark.parametrize("invalid_id", [None, 0, -1, True, 1.5, "", "invalid"])
def test_identity_fallback_preserves_legacy_case_insensitive_names(invalid_id: object) -> None:
    observations = generate_data_pages.collect_observations(
        [
            identity_artifact(
                "2026-W43",
                [{"id": invalid_id, "full_name": "Owner/Project", "stars": 50}],
            ),
            identity_artifact(
                "2026-W44",
                [{"full_name": "owner/project", "stars": 40}],
            ),
        ]
    )
    assert len(generate_data_pages.grouped_by_repo(observations)) == 1
    latest = list(generate_data_pages.latest_by_repo(observations).values())
    assert [(obs.full_name, obs.stars) for obs in latest] == [("owner/project", 40)]


def test_legacy_observations_join_only_unambiguous_stable_ids() -> None:
    artifacts = [
        identity_artifact(
            "2026-W42",
            [
                {"full_name": "old/project", "stars": 10},
                {"full_name": "reused/name", "stars": 20},
            ],
        ),
        identity_artifact(
            "2026-W43",
            [
                {"id": 1, "full_name": "old/project", "stars": 30},
                {"id": 2, "full_name": "reused/name", "stars": 40},
            ],
        ),
        identity_artifact(
            "2026-W44",
            [
                {"id": 1, "full_name": "new/project", "stars": 50},
                {"id": 3, "full_name": "REUSED/Name", "stars": 60},
            ],
        ),
    ]
    for ordering in (artifacts, artifacts[::-1]):
        observations = generate_data_pages.collect_observations(ordering)
        latest = generate_data_pages.latest_by_repo(observations).values()
        assert sorted((obs.full_name, obs.stars) for obs in latest) == [
            ("REUSED/Name", 60),
            ("new/project", 50),
            ("reused/name", 20),
            ("reused/name", 40),
        ]


def test_distinct_stable_ids_are_not_collapsed_within_a_week() -> None:
    artifact = identity_artifact(
        "2026-W44",
        [
            {"id": 1, "full_name": "owner/project", "stars": 100},
            {"id": 2, "full_name": "owner/project", "stars": 90},
        ],
    )
    expected = generate_data_pages.latest_by_repo(
        generate_data_pages.collect_observations([artifact])
    )
    artifact.payload["trending_repos"].reverse()
    assert len(expected) == 2
    assert (
        generate_data_pages.latest_by_repo(generate_data_pages.collect_observations([artifact]))
        == expected
    )


def test_latest_snapshot_ties_are_independent_of_input_order() -> None:
    artifact = identity_artifact(
        "2026-W44",
        [
            {"id": 42, "full_name": "owner/project", "stars": 100, "description": "AI tool"},
            {"id": 42, "full_name": "owner/project", "stars": 100, "description": "MCP tool"},
        ],
    )
    first = generate_data_pages.latest_by_repo(generate_data_pages.collect_observations([artifact]))
    artifact.payload["trending_repos"].reverse()
    assert (
        generate_data_pages.latest_by_repo(generate_data_pages.collect_observations([artifact]))
        == first
    )


def test_historical_growth_keeps_weekly_name_and_highest_star_baseline() -> None:
    artifacts = [
        identity_artifact(
            "2026-W43",
            [
                {"id": 1, "full_name": "old/project", "stars": 100},
                {"id": 2, "full_name": "reused/name", "stars": 50},
            ],
        ),
        identity_artifact(
            "2026-W44",
            [
                {"id": 1, "full_name": "old/project", "stars": 200},
                {"id": 1, "full_name": "new/project", "stars": 300},
                {"id": 3, "full_name": "REUSED/Name", "stars": 80},
            ],
            crawled_at="2026-10-26T01:00:00Z",
        ),
        identity_artifact(
            "2026-W44",
            [{"id": 1, "full_name": "old/project", "stars": 150}],
            crawled_at="2026-10-26T02:00:00Z",
        ),
    ]
    observations = generate_data_pages.collect_observations(artifacts)
    latest = generate_data_pages.latest_by_repo(observations)
    assert latest["github:1"].stars == 150
    assert latest["github:1"].full_name == "old/project"
    histories = generate_data_pages.grouped_by_repo(observations)
    assert {name: [obs.stars for obs in group] for name, group in histories.items()} == {
        "old/project": [100, 200],
        "new/project": [300],
        "reused/name": [50, 80],
    }


def test_historical_growth_page_remains_byte_identical_to_committed_output() -> None:
    path = ROOT / "content/data/fastest-growing-ai-repositories-this-year/index.md"
    assert generate_data_pages.build_pages()[path] == path.read_text(encoding="utf-8")


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


def test_source_summary_uses_week_range_across_source_directories() -> None:
    paths = {
        ROOT / "data/raw/2026-W21.json",
        ROOT / "data/raw/2026-W22.json",
        ROOT / "data/archive/recovered-W23-W29/2026-W23/2026-W23.json",
        ROOT / "data/raw/2026-W24.json",
    }

    assert generate_data_pages.source_summary(paths) == (
        "2026-W21 through 2026-W24 (4 weekly raw artifacts from "
        "data/archive/recovered-W23-W29 and data/raw)"
    )


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
