from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

import yaml

from scripts.backfill_weekly_topics import (
    backfill_document,
    backfill_weekly_topics,
    render_topics_line,
)
from scripts.generate_content import FRONTMATTER_PATTERN

ROOT = Path(__file__).resolve().parent.parent
SEED_TOPICS = set(
    tomllib.loads((ROOT / "config" / "observatory.toml").read_text(encoding="utf-8"))["topic_hubs"][
        "seed_topics"
    ]
)

EXPECTED_TOPICS = {
    "W21.md": ["AI Coding Agents", "MCP Ecosystem"],
    "W22.md": ["AI Coding Agents", "Open-Source LLMs", "Developer Tools", "Local First"],
    "W23.md": ["AI Coding Agents"],
    "W24.md": ["AI Coding Agents", "Local First"],
    "W25.md": ["AI Coding Agents", "Open-Source LLMs"],
    "W26.md": ["AI Coding Agents", "MCP Ecosystem", "Open-Source LLMs"],
    "W27.md": ["AI Coding Agents", "Local First"],
    "W28.md": ["AI Coding Agents", "Local First"],
    "W29.md": ["AI Coding Agents", "Developer Tools", "Local First"],
    "W30.md": ["AI Coding Agents", "Open-Source LLMs", "Local First"],
    "W31.md": [
        "AI Coding Agents",
        "Developer Tools",
        "AI Agents in Healthcare",
        "Local First",
    ],
    "W32.md": ["AI Coding Agents", "Developer Tools", "Local First"],
    "W33.md": ["AI Coding Agents", "Developer Tools", "Local First"],
    "W34.md": ["AI Coding Agents", "MCP Ecosystem", "Developer Tools", "Local First"],
    "W35.md": ["AI Coding Agents", "MCP Ecosystem", "Developer Tools", "Local First"],
}


def _without_topics(document: str) -> str:
    return re.sub(r"^topics:.*\n", "", document, count=1, flags=re.MULTILINE)


def _without_seed_topics(document: str) -> str:
    match = re.search(r"^topics:.*\n", document, flags=re.MULTILINE)
    assert match
    topics = yaml.safe_load(match.group())["topics"]
    retained = [topic for topic in topics if topic not in SEED_TOPICS]
    replacement = f"{render_topics_line(retained)}\n" if retained else ""
    return document[: match.start()] + replacement + document[match.end() :]


def test_backfill_document_preserves_body_and_unrelated_frontmatter() -> None:
    path = ROOT / "content" / "weekly" / "2026" / "W31.md"
    original = _without_topics(path.read_text(encoding="utf-8"))
    updated = backfill_document(
        original,
        path=path,
        registry_path=ROOT / "data" / "taxonomy" / "topics.json",
        content_root=ROOT / "content",
    )

    original_match = FRONTMATTER_PATTERN.match(original)
    updated_match = FRONTMATTER_PATTERN.match(updated)
    assert original_match and updated_match
    assert original_match.group(2) == updated_match.group(2)
    assert (
        updated.replace(
            'topics: ["AI Coding Agents", "Developer Tools", '
            '"AI Agents in Healthcare", "Local First"]\n',
            "",
        )
        == original
    )


def test_backfill_is_idempotent_and_assigns_expected_topics(tmp_path: Path) -> None:
    weekly_root = tmp_path / "content" / "weekly" / "2026"
    weekly_root.mkdir(parents=True)
    for source in sorted((ROOT / "content" / "weekly" / "2026").glob("W*.md")):
        (weekly_root / source.name).write_text(
            _without_seed_topics(source.read_text(encoding="utf-8")), encoding="utf-8"
        )
    for source in sorted((ROOT / "content" / "topics").glob("*/_index.md")):
        target = tmp_path / "content" / "topics" / source.parent.name / "_index.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    registry = tmp_path / "data" / "taxonomy" / "topics.json"
    registry.parent.mkdir(parents=True)
    registry.write_bytes((ROOT / "data" / "taxonomy" / "topics.json").read_bytes())

    assert len(backfill_weekly_topics(root=tmp_path)) == 15
    first_bytes = {path.name: path.read_bytes() for path in sorted(weekly_root.glob("W*.md"))}
    assert backfill_weekly_topics(root=tmp_path) == []
    assert first_bytes == {
        path.name: path.read_bytes() for path in sorted(weekly_root.glob("W*.md"))
    }

    for path in sorted(weekly_root.glob("W*.md")):
        frontmatter = FRONTMATTER_PATTERN.match(path.read_text(encoding="utf-8"))
        assert frontmatter
        assert yaml.safe_load(frontmatter.group(1))["topics"] == EXPECTED_TOPICS[path.name]


def test_check_reports_stale_without_mutating(tmp_path: Path) -> None:
    source = ROOT / "content" / "weekly" / "2026" / "W21.md"
    target = tmp_path / "content" / "weekly" / "2026" / "W21.md"
    target.parent.mkdir(parents=True)
    target.write_text(_without_topics(source.read_text(encoding="utf-8")), encoding="utf-8")
    for hub in (ROOT / "content" / "topics").glob("*/_index.md"):
        copied = tmp_path / "content" / "topics" / hub.parent.name / "_index.md"
        copied.parent.mkdir(parents=True, exist_ok=True)
        copied.write_bytes(hub.read_bytes())
    registry = tmp_path / "data" / "taxonomy" / "topics.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(json.loads((ROOT / "data" / "taxonomy" / "topics.json").read_text())),
        encoding="utf-8",
    )
    before = target.read_bytes()

    assert backfill_weekly_topics(root=tmp_path, check=True) == [target]
    assert target.read_bytes() == before


def test_backfill_restores_seed_topics_and_keeps_promoted_dynamic_topic(tmp_path: Path) -> None:
    weekly = tmp_path / "content" / "weekly" / "2026" / "W22.md"
    weekly.parent.mkdir(parents=True)
    weekly.write_text(
        '---\ntitle: "2026-W22"\ndate: 2026-05-25\nweek: "2026-W22"\n'
        'tags: ["agent-skills", "open-source", "developer-tooling", "local-first"]\n'
        'categories: ["weekly"]\ntopics: ["Local First"]\n---\nBody\n',
        encoding="utf-8",
    )
    for slug, title in (
        ("ai-coding-agents", "AI Coding Agents"),
        ("open-source-llms", "Open-Source LLMs"),
        ("developer-tools", "Developer Tools"),
        ("local-first", "Local First"),
    ):
        hub = tmp_path / "content" / "topics" / slug / "_index.md"
        hub.parent.mkdir(parents=True, exist_ok=True)
        hub.write_text(f'---\ntitle: "{title}"\n---\n', encoding="utf-8")
    registry = tmp_path / "data" / "taxonomy" / "topics.json"
    registry.parent.mkdir(parents=True)
    source_registry = json.loads(
        (ROOT / "data" / "taxonomy" / "topics.json").read_text(encoding="utf-8")
    )
    source_registry["terms"]["local-first"] = {
        "aliases": ["local-first"],
        "display_name": "Local First",
        "is_hub": True,
        "promoted": True,
        "slug": "local-first",
    }
    registry.write_text(json.dumps(source_registry), encoding="utf-8")

    changed = backfill_weekly_topics(root=tmp_path)

    assert changed == [weekly]
    assert (
        'topics: ["AI Coding Agents", "Open-Source LLMs", "Developer Tools", "Local First"]'
        in weekly.read_text(encoding="utf-8")
    )
    assert backfill_weekly_topics(root=tmp_path) == []
