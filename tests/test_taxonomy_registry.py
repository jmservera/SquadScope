from __future__ import annotations

import json
import shutil
from pathlib import Path

from scripts.taxonomy_registry import update_taxonomy_registries

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT / ".test-workspaces" / "taxonomy-registry"


def _write_workspace() -> None:
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    (WORKSPACE / "config").mkdir(parents=True)
    (WORKSPACE / "content" / "weekly" / "2026").mkdir(parents=True)
    (WORKSPACE / "content" / "topics" / "mcp-ecosystem").mkdir(parents=True)
    (WORKSPACE / "data" / "raw").mkdir(parents=True)
    (WORKSPACE / "config" / "observatory.toml").write_text(
        """[topic_hubs]
seed_topics = ["MCP Ecosystem"]

[topic_hubs.dynamic_creation]
enabled = true
min_weekly_issues = 4
lookback_days = 62
log_path = "data/topic-hubs/dynamic-topic-creation.log"
ignore_topics = []
""",
        encoding="utf-8",
    )
    (WORKSPACE / "content" / "topics" / "mcp-ecosystem" / "_index.md").write_text(
        '---\ntitle: "MCP Ecosystem"\n---\n',
        encoding="utf-8",
    )
    for week, day, topics, tags in (
        ("2026-W27", "2026-07-01", ["MCP Ecosystem"], ["mcp", "agents"]),
        ("2026-W28", "2026-07-08", ["MCP Ecosystem", "Edge AI Workflows"], ["mcp"]),
        ("2026-W29", "2026-07-15", ["Edge AI Workflows"], ["agents"]),
    ):
        year, week_number = week.split("-W")
        (WORKSPACE / "content" / "weekly" / year / f"W{week_number}.md").write_text(
            f"""---
title: "{week}"
date: {day}T00:00:00+00:00
week: "{week}"
topics: {json.dumps(topics)}
tags: {json.dumps(tags)}
---
""",
            encoding="utf-8",
        )
    (WORKSPACE / "data" / "raw" / "2026-W29.json").write_text(
        json.dumps(
            {
                "week": "2026-W29",
                "crawled_at": "2026-07-15T12:00:00+00:00",
                "trending_repos": [{"topics": ["mcp", "python"]}],
                "new_repos": [{"topics": ["python"]}],
            }
        ),
        encoding="utf-8",
    )


def test_taxonomy_registry_is_deterministic_and_computes_stats() -> None:
    _write_workspace()
    update_taxonomy_registries(
        root=WORKSPACE,
        config_path=WORKSPACE / "config" / "observatory.toml",
    )
    first_topics = (WORKSPACE / "data" / "taxonomy" / "topics.json").read_text(encoding="utf-8")
    first_tags = (WORKSPACE / "data" / "taxonomy" / "tags.json").read_text(encoding="utf-8")

    update_taxonomy_registries(
        root=WORKSPACE,
        config_path=WORKSPACE / "config" / "observatory.toml",
    )

    assert (WORKSPACE / "data" / "taxonomy" / "topics.json").read_text(
        encoding="utf-8"
    ) == first_topics
    assert (WORKSPACE / "data" / "taxonomy" / "tags.json").read_text(encoding="utf-8") == first_tags

    topics = json.loads(first_topics)["terms"]
    assert topics["mcp-ecosystem"]["display_name"] == "MCP Ecosystem"
    assert topics["mcp-ecosystem"]["count"] == 2
    assert topics["mcp-ecosystem"]["weekly_issue_count"] == 2
    assert topics["mcp-ecosystem"]["first_seen"] == "2026-07-01"
    assert topics["mcp-ecosystem"]["last_used"] == "2026-07-08"
    assert topics["mcp-ecosystem"]["is_hub"] is True

    assert topics["edge-ai-workflows"]["count"] == 2
    assert topics["edge-ai-workflows"]["weekly_issue_count"] == 2
    assert topics["edge-ai-workflows"]["last_used"] == "2026-07-15"

    tags = json.loads(first_tags)["terms"]
    assert tags["mcp"]["count"] == 3
    assert tags["mcp"]["weekly_issue_count"] == 3
    assert tags["python"]["count"] == 2
    assert tags["python"]["last_used"] == "2026-07-15"
