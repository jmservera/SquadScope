from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.backfill_weekly_topics import backfill_document, backfill_weekly_topics
from scripts.generate_content import FRONTMATTER_PATTERN

ROOT = Path(__file__).resolve().parent.parent

EXPECTED_TOPICS = {
    "W21.md": ["AI Coding Agents", "MCP Ecosystem"],
    "W22.md": ["AI Coding Agents", "Open-Source LLMs", "Developer Tools"],
    "W23.md": ["AI Coding Agents"],
    "W24.md": ["AI Coding Agents", "Local First"],
    "W25.md": ["AI Coding Agents", "Open-Source LLMs"],
    "W26.md": ["AI Coding Agents", "MCP Ecosystem", "Open-Source LLMs"],
    "W27.md": ["AI Coding Agents", "Local First"],
    "W28.md": ["AI Coding Agents", "Local First"],
    "W29.md": ["AI Coding Agents", "Developer Tools", "Local First"],
    "W30.md": ["AI Coding Agents", "Open-Source LLMs"],
    "W31.md": [
        "AI Coding Agents",
        "Developer Tools",
        "AI Agents in Healthcare",
        "Local First",
    ],
    "W32.md": ["AI Coding Agents", "Developer Tools"],
    "W33.md": ["AI Coding Agents", "Developer Tools"],
}


def _without_topics(document: str) -> str:
    return re.sub(r"^topics:.*\n", "", document, count=1, flags=re.MULTILINE)


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
            _without_topics(source.read_text(encoding="utf-8")), encoding="utf-8"
        )
    for source in sorted((ROOT / "content" / "topics").glob("*/_index.md")):
        target = tmp_path / "content" / "topics" / source.parent.name / "_index.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    registry = tmp_path / "data" / "taxonomy" / "topics.json"
    registry.parent.mkdir(parents=True)
    registry.write_bytes((ROOT / "data" / "taxonomy" / "topics.json").read_bytes())

    assert len(backfill_weekly_topics(root=tmp_path)) == 13
    first_bytes = {path.name: path.read_bytes() for path in sorted(weekly_root.glob("W*.md"))}
    assert backfill_weekly_topics(root=tmp_path) == []
    assert first_bytes == {
        path.name: path.read_bytes() for path in sorted(weekly_root.glob("W*.md"))
    }

    for path in sorted(weekly_root.glob("W*.md")):
        frontmatter = FRONTMATTER_PATTERN.match(path.read_text(encoding="utf-8"))
        assert frontmatter
        import yaml

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
