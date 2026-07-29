#!/usr/bin/env python3
"""Build deterministic file-based taxonomy registries from checked-in data."""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "observatory.toml"
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
WEEK_RE = re.compile(r"(?P<year>\d{4})-W(?P<week>\d{2})")
SLUG_RE = re.compile(r"[^a-z0-9]+")


@dataclass
class TermStats:
    display_name: str
    slug: str
    first_seen: str | None = None
    last_used: str | None = None
    count: int = 0
    times_used: int = 0
    weekly_issue_count: int = 0
    is_hub: bool = False
    promoted: bool = False
    order: int | None = None
    aliases: list[str] = field(default_factory=list)
    weeks: set[str] = field(default_factory=set, repr=False)


def slugify(value: str) -> str:
    return SLUG_RE.sub("-", value.strip().lower()).strip("-")[:80].strip("-")


def parse_week_date(week: str) -> str:
    match = WEEK_RE.fullmatch(week)
    if not match:
        return ""
    return date.fromisocalendar(int(match.group("year")), int(match.group("week")), 1).isoformat()


def normalize_date(value: object, fallback_week: str = "") -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            return value[:10]
    return parse_week_date(fallback_week)


def read_frontmatter(path: Path) -> dict[str, Any]:
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        return {}
    parsed = yaml.safe_load(match.group(1))
    return parsed if isinstance(parsed, dict) else {}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"terms": {}}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {"terms": {}}


def load_seed_topics(config_path: Path) -> list[str]:
    if not config_path.exists():
        return []
    raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    topics = raw.get("topic_hubs", {}).get("seed_topics", [])
    return [topic for topic in topics if isinstance(topic, str) and topic]


def raw_week_files(root: Path) -> list[Path]:
    candidates: dict[str, Path] = {}
    for path in sorted((root / "data" / "raw").glob("*.json")):
        if WEEK_RE.fullmatch(path.stem):
            candidates[path.stem] = path
    archive_dir = root / "data" / "archive" / "recovered-W23-W29"
    for path in sorted(archive_dir.glob("*/**/*.json")):
        if WEEK_RE.fullmatch(path.stem):
            candidates.setdefault(path.stem, path)
    return [candidates[week] for week in sorted(candidates)]


def get_term(
    terms: dict[str, TermStats],
    value: str,
    *,
    display_name: str | None = None,
) -> TermStats | None:
    if not isinstance(value, str) or not value.strip():
        return None
    slug = slugify(value)
    if not slug:
        return None
    term = terms.get(slug)
    if term is None:
        term = TermStats(display_name=display_name or value.strip(), slug=slug)
        terms[slug] = term
    elif display_name:
        term.display_name = display_name
    return term


def merge_existing(path: Path) -> dict[str, TermStats]:
    terms: dict[str, TermStats] = {}
    for slug, raw in load_json(path).get("terms", {}).items():
        if not isinstance(raw, dict):
            continue
        key = str(raw.get("slug") or slug)
        term = TermStats(
            display_name=str(raw.get("display_name") or key),
            slug=key,
            first_seen=raw.get("first_seen"),
            last_used=raw.get("last_used"),
            is_hub=bool(raw.get("is_hub", False)),
            promoted=bool(raw.get("promoted", False)),
            order=raw.get("order") if isinstance(raw.get("order"), int) else None,
            aliases=[str(alias) for alias in raw.get("aliases", []) if isinstance(alias, str)],
        )
        terms[key] = term
    return terms


def record_usage(term: TermStats, week: str, used_on: str) -> None:
    term.count += 1
    term.times_used += 1
    if week:
        term.weeks.add(week)
    if used_on:
        term.first_seen = min(filter(None, [term.first_seen, used_on]), default=used_on)
        term.last_used = max(filter(None, [term.last_used, used_on]), default=used_on)


def scan_weekly_frontmatter(
    root: Path, topic_terms: dict[str, TermStats], tag_terms: dict[str, TermStats]
) -> None:
    for path in sorted((root / "content" / "weekly").glob("**/*.md")):
        frontmatter = read_frontmatter(path)
        week = str(frontmatter.get("week") or "")
        used_on = normalize_date(frontmatter.get("date"), week)
        for field_name, terms in (("topics", topic_terms), ("tags", tag_terms)):
            values = frontmatter.get(field_name)
            if not isinstance(values, list):
                continue
            for value in values:
                term = get_term(terms, str(value))
                if term:
                    record_usage(term, week, used_on)


def scan_raw_repo_topics(root: Path, tag_terms: dict[str, TermStats]) -> None:
    for path in raw_week_files(root):
        payload = json.loads(path.read_text(encoding="utf-8"))
        week = str(payload.get("week") or "")
        used_on = normalize_date(payload.get("crawled_at"), week)
        for bucket in ("trending_repos", "new_repos"):
            for repo in payload.get(bucket, []):
                if not isinstance(repo, dict) or not isinstance(repo.get("topics"), list):
                    continue
                for value in repo["topics"]:
                    term = get_term(tag_terms, str(value))
                    if term:
                        record_usage(term, week, used_on)


def apply_seed_topics(root: Path, config_path: Path, topic_terms: dict[str, TermStats]) -> None:
    for index, title in enumerate(load_seed_topics(config_path)):
        term = get_term(topic_terms, title, display_name=title)
        if term:
            term.is_hub = True
            term.promoted = True
            term.order = index
    for index_path in sorted((root / "content" / "topics").glob("*/_index.md")):
        frontmatter = read_frontmatter(index_path)
        title = frontmatter.get("title")
        if isinstance(title, str) and title:
            term = get_term(topic_terms, title, display_name=title)
        else:
            term = get_term(topic_terms, index_path.parent.name)
        if term:
            term.is_hub = True
            term.promoted = True


def finalize_terms(existing: dict[str, TermStats], terms: dict[str, TermStats]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    all_slugs = sorted(set(existing) | set(terms))
    for slug in all_slugs:
        term = terms.get(slug) or existing[slug]
        previous = existing.get(slug)
        first_seen = term.first_seen
        if previous and previous.first_seen and first_seen:
            first_seen = min(previous.first_seen, first_seen)
        elif previous and previous.first_seen:
            first_seen = previous.first_seen
        last_used = term.last_used or (previous.last_used if previous else None)
        aliases = sorted(set(term.aliases or (previous.aliases if previous else [])))
        term.weekly_issue_count = len(term.weeks)
        output[slug] = {
            "display_name": term.display_name,
            "slug": slug,
            "first_seen": first_seen,
            "last_used": last_used,
            "count": term.count,
            "times_used": term.times_used,
            "weekly_issue_count": term.weekly_issue_count,
            "is_hub": term.is_hub or bool(previous and previous.is_hub),
            "promoted": term.promoted or bool(previous and previous.promoted),
        }
        order = term.order if term.order is not None else (previous.order if previous else None)
        if order is not None:
            output[slug]["order"] = order
        if aliases:
            output[slug]["aliases"] = aliases
    return output


def write_registry(path: Path, terms: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"terms": terms}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_display_names(path: Path) -> dict[str, str]:
    terms = load_json(path).get("terms", {})
    if not isinstance(terms, dict):
        return {}
    display_names: dict[str, str] = {}
    for slug, raw in terms.items():
        if not isinstance(raw, dict):
            continue
        key = str(raw.get("slug") or slug)
        display_names[key] = str(raw.get("display_name") or key)
    return display_names


def update_taxonomy_registries(
    *,
    root: Path = PROJECT_ROOT,
    config_path: Path = DEFAULT_CONFIG,
) -> tuple[Path, Path]:
    registry_dir = root / "data" / "taxonomy"
    topics_path = registry_dir / "topics.json"
    tags_path = registry_dir / "tags.json"
    existing_topics = merge_existing(topics_path)
    existing_tags = merge_existing(tags_path)
    topic_terms: dict[str, TermStats] = defaultdict()
    tag_terms: dict[str, TermStats] = defaultdict()

    for slug, term in existing_topics.items():
        if term.aliases or term.is_hub or term.promoted:
            topic_terms[slug] = TermStats(
                display_name=term.display_name,
                slug=term.slug,
                is_hub=term.is_hub,
                promoted=term.promoted,
                order=term.order,
                aliases=term.aliases,
            )

    apply_seed_topics(root, config_path, topic_terms)
    scan_weekly_frontmatter(root, topic_terms, tag_terms)
    scan_raw_repo_topics(root, tag_terms)
    write_registry(topics_path, finalize_terms(existing_topics, topic_terms))
    write_registry(tags_path, finalize_terms(existing_tags, tag_terms))
    return topics_path, tags_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update deterministic taxonomy registries.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for path in update_taxonomy_registries(config_path=args.config):
        print(path.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
