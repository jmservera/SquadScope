#!/usr/bin/env python3
"""Backfill canonical topics in weekly Hugo frontmatter without rewriting content."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_content import derive_canonical_topics, yaml_quote

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTMATTER_RE = re.compile(r"\A---\n(?P<frontmatter>.*?)\n---\n", re.DOTALL)
TOPICS_LINE_RE = re.compile(r"^topics:.*$", re.MULTILINE)
CATEGORIES_LINE_RE = re.compile(r"^categories:.*$", re.MULTILINE)


def _parse_frontmatter(document: str, path: Path) -> tuple[dict[str, object], re.Match[str]]:
    match = FRONTMATTER_RE.match(document)
    if not match:
        raise ValueError(f"{path}: missing YAML frontmatter")
    parsed = yaml.safe_load(match.group("frontmatter"))
    if not isinstance(parsed, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    return parsed, match


def _hub_slugs(registry_path: Path) -> dict[str, str]:
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    terms = payload.get("terms", {}) if isinstance(payload, dict) else {}
    if not isinstance(terms, dict):
        raise ValueError(f"{registry_path}: terms must be a mapping")
    return {
        str(raw.get("display_name")): str(raw.get("slug") or slug)
        for slug, raw in terms.items()
        if isinstance(raw, dict) and isinstance(raw.get("display_name"), str)
    }


def render_topics_line(topics: list[str]) -> str:
    """Render the canonical inline topics frontmatter field."""
    return f"topics: [{', '.join(yaml_quote(topic) for topic in topics)}]"


def backfill_document(
    document: str,
    *,
    path: Path,
    registry_path: Path,
    content_root: Path,
) -> str:
    """Return a weekly document with only its topics frontmatter field changed."""
    frontmatter, match = _parse_frontmatter(document, path)
    tags = frontmatter.get("tags")
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        raise ValueError(f"{path}: tags must be a list of strings")
    topics = derive_canonical_topics(frontmatter, tags, registry_path=registry_path)
    slugs = _hub_slugs(registry_path)
    for topic in topics:
        slug = slugs.get(topic)
        if not slug or not (content_root / "topics" / slug / "_index.md").is_file():
            raise ValueError(f"{path}: canonical topic hub does not exist for {topic!r}")

    frontmatter_text = match.group("frontmatter")
    topics_line = render_topics_line(topics)
    if TOPICS_LINE_RE.search(frontmatter_text):
        updated_frontmatter = TOPICS_LINE_RE.sub(topics_line, frontmatter_text, count=1)
    else:
        category_match = CATEGORIES_LINE_RE.search(frontmatter_text)
        if not category_match:
            raise ValueError(f"{path}: categories field is required before topics")
        updated_frontmatter = (
            frontmatter_text[: category_match.end()]
            + "\n"
            + topics_line
            + frontmatter_text[category_match.end() :]
        )
    return (
        document[: match.start("frontmatter")]
        + updated_frontmatter
        + document[match.end("frontmatter") :]
    )


def backfill_weekly_topics(*, root: Path = PROJECT_ROOT, check: bool = False) -> list[Path]:
    """Backfill every weekly file and return paths that were stale."""
    registry_path = root / "data" / "taxonomy" / "topics.json"
    changed: list[Path] = []
    weekly_root = root / "content" / "weekly"
    for path in sorted(weekly_root.glob("[0-9][0-9][0-9][0-9]/W[0-9][0-9].md")):
        original = path.read_text(encoding="utf-8")
        updated = backfill_document(
            original,
            path=path,
            registry_path=registry_path,
            content_root=root / "content",
        )
        if updated == original:
            continue
        changed.append(path)
        if not check:
            path.write_text(updated, encoding="utf-8")
    return changed


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--check", action="store_true", help="Fail when weekly topics are stale.")
    return parser


def main() -> int:
    """Run the weekly topic backfill."""
    args = create_parser().parse_args()
    try:
        changed = backfill_weekly_topics(root=args.root, check=args.check)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    for path in changed:
        print(path.relative_to(args.root))
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
