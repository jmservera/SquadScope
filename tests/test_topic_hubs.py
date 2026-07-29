from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from scripts.manage_topic_hubs import create_dynamic_hubs

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT / ".test-workspaces" / "topic-hub-lifecycle"

SEED_HUBS = {
    "ai-coding-agents": "AI Coding Agents",
    "mcp-ecosystem": "MCP Ecosystem",
    "open-source-llms": "Open-Source LLMs",
    "developer-tools": "Developer Tools",
    "ai-agents-in-healthcare": "AI Agents in Healthcare",
}


def test_seed_topic_hubs_have_unique_metadata_and_dataset_links() -> None:
    descriptions: set[str] = set()
    for slug, title in SEED_HUBS.items():
        hub_path = ROOT / "content" / "topics" / slug / "_index.md"
        content = hub_path.read_text(encoding="utf-8")
        assert f'title: "{title}"' in content
        assert "description:" in content
        assert "dataset_highlights:" in content
        assert "/state-of/open-source-ai-2026/" in content
        description_line = next(
            line for line in content.splitlines() if line.startswith("description:")
        )
        descriptions.add(description_line)

    assert len(descriptions) == len(SEED_HUBS)


def test_dynamic_topic_creation_is_threshold_driven_and_additive() -> None:
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    (WORKSPACE / "config").mkdir(parents=True)
    (WORKSPACE / "content" / "weekly" / "2026").mkdir(parents=True)
    (WORKSPACE / "content" / "topics" / "quiet-existing").mkdir(parents=True)

    (WORKSPACE / "config" / "observatory.toml").write_text(
        """[topic_hubs.dynamic_creation]
        enabled = true
        min_weekly_issues = 4
        lookback_days = 62
        log_path = "data/topic-hubs/dynamic-topic-creation.log"
        ignore_topics = []
        source_globs = ["content/weekly/**/*.md"]
        """,
        encoding="utf-8",
    )
    (WORKSPACE / "content" / "topics" / "quiet-existing" / "_index.md").write_text(
        '---\ntitle: "Quiet Existing"\n---\n',
        encoding="utf-8",
    )

    weeks = ["2026-W27", "2026-W28", "2026-W29", "2026-W30"]
    for week in weeks:
        year, week_number = week.split("-W")
        (WORKSPACE / "content" / "weekly" / year / f"W{week_number}.md").write_text(
            f'''---
title: "{week}"
date: 2026-07-01T00:00:00+00:00
week: "{week}"
candidate_topics: ["Edge AI Workflows", "Quiet Existing"]
---

Body.
''',
            encoding="utf-8",
        )

    created = create_dynamic_hubs(
        root=WORKSPACE,
        config_path=WORKSPACE / "config" / "observatory.toml",
        current_date="2026-07-29T12:57:30Z",
    )

    assert created == [WORKSPACE / "content" / "topics" / "edge-ai-workflows" / "_index.md"]
    new_hub = created[0].read_text(encoding="utf-8")
    assert "Edge AI Workflows" in new_hub
    assert "min_weekly_issues: 4" in new_hub
    assert "persists through quiet weeks" in new_hub.lower()
    assert (WORKSPACE / "content" / "topics" / "quiet-existing" / "_index.md").exists()

    log = (WORKSPACE / "data" / "topic-hubs" / "dynamic-topic-creation.log").read_text(
        encoding="utf-8"
    )
    assert "threshold=4" in log
    assert "create topic='Edge AI Workflows'" in log


def test_dynamic_topic_creation_does_not_create_below_threshold() -> None:
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    (WORKSPACE / "config").mkdir(parents=True)
    (WORKSPACE / "content" / "weekly" / "2026").mkdir(parents=True)
    (WORKSPACE / "content" / "topics").mkdir(parents=True)
    (WORKSPACE / "config" / "observatory.toml").write_text(
        """[topic_hubs.dynamic_creation]
        enabled = true
        min_weekly_issues = 4
        lookback_days = 62
        log_path = "data/topic-hubs/dynamic-topic-creation.log"
        ignore_topics = []
        source_globs = ["content/weekly/**/*.md"]
        """,
        encoding="utf-8",
    )
    for week in ("2026-W29", "2026-W30", "2026-W31"):
        year, week_number = week.split("-W")
        (WORKSPACE / "content" / "weekly" / year / f"W{week_number}.md").write_text(
            f'---\ntitle: "{week}"\nweek: "{week}"\ncandidate_topics: ["Three Week Trend"]\n---\n',
            encoding="utf-8",
        )

    created = create_dynamic_hubs(
        root=WORKSPACE,
        config_path=WORKSPACE / "config" / "observatory.toml",
        current_date="2026-07-29T12:57:30Z",
    )

    assert created == []
    assert not (WORKSPACE / "content" / "topics" / "three-week-trend").exists()


@pytest.mark.skipif(shutil.which("hugo") is None, reason="hugo is not installed")
def test_hugo_renders_topic_hubs_with_issue_cards_and_rss() -> None:
    destination = ROOT / ".test-workspaces" / "hugo-topic-hubs-public"
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["hugo", "--minify", "--destination", str(destination)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    page = (destination / "topics" / "ai-coding-agents" / "index.html").read_text(encoding="utf-8")
    rss = destination / "topics" / "ai-coding-agents" / "index.xml"
    assert "Topic hub" in page
    assert "Recent weekly issues" in page
    assert "Agent Work Moved Into the Operating Room" in page
    assert "Dataset highlights" in page
    assert "rel=canonical href=https://claracle.com/topics/ai-coding-agents/" in page
    assert rss.exists()
    assert "Agent Work Moved Into the Operating Room" in rss.read_text(encoding="utf-8")
