from __future__ import annotations

import json
import shutil
import subprocess
import tomllib
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
    registry = json.loads((ROOT / "data" / "taxonomy" / "topics.json").read_text(encoding="utf-8"))
    seed_topics = {
        slug: term["display_name"]
        for slug, term in registry["terms"].items()
        if term["is_hub"] and term["promoted"]
    }
    assert seed_topics == SEED_HUBS

    descriptions: set[str] = set()
    for slug, title in seed_topics.items():
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
        """,
        encoding="utf-8",
    )
    (WORKSPACE / "data" / "taxonomy").mkdir(parents=True)
    (WORKSPACE / "content" / "topics" / "quiet-existing" / "_index.md").write_text(
        '---\ntitle: "Quiet Existing"\n---\n',
        encoding="utf-8",
    )
    (WORKSPACE / "data" / "taxonomy" / "topics.json").write_text(
        json.dumps(
            {
                "terms": {
                    "edge-ai-workflows": {
                        "display_name": "Edge AI Workflows",
                        "slug": "edge-ai-workflows",
                        "first_seen": "2026-07-01",
                        "last_used": "2026-07-27",
                        "count": 4,
                        "times_used": 4,
                        "weekly_issue_count": 4,
                        "is_hub": False,
                        "promoted": False,
                    },
                    "quiet-existing": {
                        "display_name": "Quiet Existing",
                        "slug": "quiet-existing",
                        "first_seen": "2026-07-01",
                        "last_used": "2026-07-27",
                        "count": 4,
                        "times_used": 4,
                        "weekly_issue_count": 4,
                        "is_hub": False,
                        "promoted": False,
                    },
                    "forked-candidate-source": {
                        "display_name": "Forked Candidate Source",
                        "slug": "forked-candidate-source",
                        "first_seen": "2026-07-01",
                        "last_used": "2026-07-27",
                        "count": 0,
                        "times_used": 0,
                        "weekly_issue_count": 0,
                        "is_hub": False,
                        "promoted": False,
                    },
                }
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
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
    registry = json.loads(
        (WORKSPACE / "data" / "taxonomy" / "topics.json").read_text(encoding="utf-8")
    )
    assert registry["terms"]["edge-ai-workflows"]["is_hub"] is True
    assert registry["terms"]["edge-ai-workflows"]["promoted"] is True
    from scripts.generate_content import load_topic_vocabulary

    topic_titles, topic_aliases = load_topic_vocabulary(
        registry_path=WORKSPACE / "data" / "taxonomy" / "topics.json"
    )
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
        """,
        encoding="utf-8",
    )
    (WORKSPACE / "data" / "taxonomy").mkdir(parents=True)
    (WORKSPACE / "data" / "taxonomy" / "topics.json").write_text(
        json.dumps(
            {
                "terms": {
                    "three-week-trend": {
                        "display_name": "Three Week Trend",
                        "slug": "three-week-trend",
                        "first_seen": "2026-07-01",
                        "last_used": "2026-07-27",
                        "count": 3,
                        "times_used": 3,
                        "weekly_issue_count": 3,
                        "is_hub": False,
                        "promoted": False,
                    }
                }
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    created = create_dynamic_hubs(
        root=WORKSPACE,
        config_path=WORKSPACE / "config" / "observatory.toml",
        current_date="2026-07-29T12:57:30Z",
    )

    assert created == []
    assert not (WORKSPACE / "content" / "topics" / "three-week-trend").exists()


def test_dynamic_topic_creation_preserves_parseable_seed_topics_without_trailing_comma() -> None:
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    (WORKSPACE / "config").mkdir(parents=True)
    (WORKSPACE / "content" / "topics").mkdir(parents=True)
    (WORKSPACE / "data" / "taxonomy").mkdir(parents=True)
    config_path = WORKSPACE / "config" / "observatory.toml"
    config_path.write_text(
        """[topic_hubs]
seed_topics = [
  "AI Coding Agents"
]

[topic_hubs.dynamic_creation]
enabled = true
min_weekly_issues = 4
lookback_days = 62
log_path = "data/topic-hubs/dynamic-topic-creation.log"
ignore_topics = []
""",
        encoding="utf-8",
    )
    (WORKSPACE / "data" / "taxonomy" / "topics.json").write_text(
        json.dumps(
            {
                "terms": {
                    "edge-ai-workflows": {
                        "display_name": "Edge AI Workflows",
                        "slug": "edge-ai-workflows",
                        "first_seen": "2026-07-01",
                        "last_used": "2026-07-27",
                        "count": 4,
                        "times_used": 4,
                        "weekly_issue_count": 4,
                        "is_hub": False,
                        "promoted": False,
                    }
                }
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    created = create_dynamic_hubs(
        root=WORKSPACE,
        config_path=config_path,
        current_date="2026-07-29T12:57:30Z",
    )

    assert created == [WORKSPACE / "content" / "topics" / "edge-ai-workflows" / "_index.md"]
    parsed = tomllib.loads(config_path.read_text(encoding="utf-8"))
    assert parsed["topic_hubs"]["seed_topics"] == ["AI Coding Agents"]
    registry = json.loads((WORKSPACE / "data" / "taxonomy" / "topics.json").read_text())
    assert registry["terms"]["edge-ai-workflows"]["promoted"] is True


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


@pytest.mark.skipif(shutil.which("hugo") is None, reason="hugo is not installed")
def test_hugo_home_topic_display_is_safe_without_topic_content_page() -> None:
    destination = ROOT / ".test-workspaces" / "hugo-unpaged-topic-public"
    temp_weekly = ROOT / "content" / "weekly" / "2026" / "W99.md"
    if destination.exists():
        shutil.rmtree(destination)
    temp_weekly.write_text(
        """---
title: "Temporary Unpaged Topic"
date: 2026-07-28T00:00:00+00:00
week: "2026-W99"
tags: ["temporary"]
categories: ["weekly"]
topics: ["Unpaged Topic"]
repos_featured: 1
stars_tracked: 1
top_repo: "example/repo"
summary: "Temporary taxonomy regression fixture."
draft: false
---
""",
        encoding="utf-8",
    )
    try:
        subprocess.run(
            ["hugo", "--minify", "--destination", str(destination)],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
    finally:
        temp_weekly.unlink(missing_ok=True)

    home = (destination / "index.html").read_text(encoding="utf-8")
    assert "Unpaged Topic" in home
