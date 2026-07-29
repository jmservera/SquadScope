from __future__ import annotations

import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

from scripts.manage_topic_hubs import create_dynamic_hubs, load_config, normalized_key

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
    config = load_config(ROOT / "config" / "observatory.toml")
    assert {normalized_key(title) for title in config.seed_topics} == set(SEED_HUBS)

    raw_config = tomllib.loads((ROOT / "config" / "observatory.toml").read_text(encoding="utf-8"))
    assert tuple(raw_config["topic_hubs"]["seed_topics"]) == config.seed_topics

    descriptions: set[str] = set()
    for title in config.seed_topics:
        slug = normalized_key(title)
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
        """[topic_hubs]
        seed_topics = [
          "AI Coding Agents",
          "MCP Ecosystem",
          "Open-Source LLMs",
          "Developer Tools",
          "AI Agents in Healthcare",
        ]

        [topic_hubs.dynamic_creation]
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
topics: ["Edge AI Workflows", "Quiet Existing"]
candidate_topics: ["Forked Candidate Source"]
tags: ["tag-only-signal"]
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
    config = (WORKSPACE / "config" / "observatory.toml").read_text(encoding="utf-8")
    assert '"Edge AI Workflows",' in config
    from scripts.generate_content import load_topic_vocabulary

    topic_titles, topic_aliases = load_topic_vocabulary(WORKSPACE / "config" / "observatory.toml")
    assert "Edge AI Workflows" in topic_titles
    assert topic_aliases["edge-ai-workflows"] == "Edge AI Workflows"
    assert not (WORKSPACE / "content" / "topics" / "forked-candidate-source").exists()
    assert not (WORKSPACE / "content" / "topics" / "tag-only-signal").exists()


def test_dynamic_topic_creation_does_not_create_below_threshold() -> None:
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    (WORKSPACE / "config").mkdir(parents=True)
    (WORKSPACE / "content" / "weekly" / "2026").mkdir(parents=True)
    (WORKSPACE / "content" / "topics").mkdir(parents=True)
    (WORKSPACE / "config" / "observatory.toml").write_text(
        """[topic_hubs]
        seed_topics = [
          "AI Coding Agents",
          "MCP Ecosystem",
          "Open-Source LLMs",
          "Developer Tools",
          "AI Agents in Healthcare",
        ]

        [topic_hubs.dynamic_creation]
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
            f'---\ntitle: "{week}"\nweek: "{week}"\ntopics: ["Three Week Trend"]\n---\n',
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
    assert "Dataset highlights" in page
    assert "rel=canonical href=https://claracle.com/topics/ai-coding-agents/" in page
    assert rss.exists()
    rss_content = rss.read_text(encoding="utf-8")
    assert "AI Coding Agents" in rss_content
    assert "https://claracle.com/topics/ai-coding-agents/" in rss_content
