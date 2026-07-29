#!/usr/bin/env python3
"""Export static data for the client-side Claracle Star Velocity Explorer."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_ROOT = PROJECT_ROOT / "data"
DEFAULT_OUTPUT = PROJECT_ROOT / "static" / "tools" / "star-velocity-explorer.json"
MAX_REPOSITORIES = 100
WEEK_RE = re.compile(r"^\d{4}-W\d{2}$")


@dataclass
class RepoTrend:
    repository: str
    url: str = ""
    description: str = ""
    first_seen_week: str = ""
    last_seen_week: str = ""
    stars_by_week: dict[str, int] = field(default_factory=dict)
    languages: Counter[str] = field(default_factory=Counter)
    topics: Counter[str] = field(default_factory=Counter)

    def add(self, week: str, record: dict[str, Any]) -> None:
        self.first_seen_week = min(self.first_seen_week or week, week)
        self.last_seen_week = max(self.last_seen_week or week, week)
        self.url = str(record.get("url") or self.url or f"https://github.com/{self.repository}")
        self.description = str(record.get("description") or self.description)

        stars = coerce_int(record.get("stars"))
        if stars is not None:
            self.stars_by_week[week] = max(stars, self.stars_by_week.get(week, stars))

        language = record.get("language")
        if isinstance(language, str) and language.strip():
            self.languages[language.strip()] += 1

        for topic in record.get("topics") or []:
            if isinstance(topic, str) and topic.strip():
                self.topics[topic.strip().lower()] += 1

    @property
    def first_stars(self) -> int:
        if not self.stars_by_week:
            return 0
        return self.stars_by_week[sorted(self.stars_by_week)[0]]

    @property
    def latest_stars(self) -> int:
        if not self.stars_by_week:
            return 0
        return self.stars_by_week[sorted(self.stars_by_week)[-1]]

    @property
    def observed_star_change(self) -> int:
        return self.latest_stars - self.first_stars

    def row(self) -> dict[str, Any]:
        series = [
            {"week": week, "stars": self.stars_by_week[week]} for week in sorted(self.stars_by_week)
        ]
        return {
            "repository": self.repository,
            "url": self.url,
            "description": self.description,
            "primary_language": self.languages.most_common(1)[0][0]
            if self.languages
            else "Unknown",
            "top_topics": [topic for topic, _count in self.topics.most_common(8)],
            "first_seen_week": self.first_seen_week,
            "last_seen_week": self.last_seen_week,
            "weeks_observed": len(self.stars_by_week),
            "first_observed_stars": self.first_stars,
            "latest_stars": self.latest_stars,
            "observed_star_change": self.observed_star_change,
            "series": series,
        }


def coerce_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def discover_source_paths(data_root: Path) -> list[Path]:
    selected: dict[str, Path] = {}
    raw_dir = data_root / "raw"
    for path in sorted(raw_dir.glob("*.json")):
        if WEEK_RE.match(path.stem):
            selected[path.stem] = path

    archive_dir = data_root / "archive" / "recovered-W23-W29"
    if archive_dir.exists():
        for path in sorted(archive_dir.glob("*/????-W??.json")):
            if WEEK_RE.match(path.stem) and path.stem not in selected:
                selected[path.stem] = path

    return [selected[week] for week in sorted(selected)]


def repository_slug(repository: str) -> str:
    normalized = unicodedata.normalize("NFKD", repository.lower())
    slug = re.sub(r"[^a-z0-9]+", "-", normalized)
    return re.sub(r"-+", "-", slug).strip("-")


def load_trends(source_paths: list[Path]) -> dict[str, RepoTrend]:
    trends: dict[str, RepoTrend] = {}
    for source_path in source_paths:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        week = str(payload.get("week") or source_path.stem)
        for bucket in ("trending_repos", "new_repos"):
            for record in payload.get(bucket, []) or []:
                full_name = str(
                    record.get("full_name") or f"{record.get('owner', '')}/{record.get('name', '')}"
                ).strip("/")
                if "/" not in full_name:
                    continue
                key = full_name.lower()
                trends.setdefault(key, RepoTrend(repository=full_name)).add(week, record)
    return trends


def build_payload(data_root: Path = DEFAULT_DATA_ROOT) -> dict[str, Any]:
    source_paths = discover_source_paths(data_root)
    trends = load_trends(source_paths)
    eligible = [trend for trend in trends.values() if len(trend.stars_by_week) >= 2]
    ranked = sorted(
        eligible,
        key=lambda trend: (
            -trend.observed_star_change,
            -trend.latest_stars,
            trend.repository.lower(),
        ),
    )[:MAX_REPOSITORIES]

    weeks = [path.stem for path in source_paths]
    languages: Counter[str] = Counter()
    topic_counts: Counter[str] = Counter()
    for trend in ranked:
        if trend.languages:
            languages[trend.languages.most_common(1)[0][0]] += 1
        topic_counts.update(dict(trend.topics.most_common(5)))

    return {
        "tool": "star-velocity-explorer",
        "version": "1",
        "as_of_week": weeks[-1] if weeks else "",
        "weeks": weeks,
        "source_files": [path.relative_to(PROJECT_ROOT).as_posix() for path in source_paths],
        "methodology": (
            "Derived from checked-in weekly raw GitHub trend artifacts. Velocity is latest "
            "observed stars minus first observed stars; no live GitHub API calls are made."
        ),
        "repository_count": len(ranked),
        "language_filters": sorted(languages),
        "topic_filters": [topic for topic, _count in topic_counts.most_common(24)],
        "repositories": [
            trend.row() | {"slug": repository_slug(trend.repository)} for trend in ranked
        ],
    }


def write_payload(output: Path, payload: dict[str, Any]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Fail if the exported JSON is stale.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload(args.data_root)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        existing = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        if existing != rendered:
            print(f"stale: {args.output.relative_to(PROJECT_ROOT)}")
            return 1
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Exported {payload['repository_count']} repositories to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
