"""Generate read-only Claracle Data Observatory repository pages from checked-in crawl data."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tomllib
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG = Path("config/observatory.toml")
GENERATED_BY = "observatory_repo_pages"
WEEKLY_LINK_PREFIX = "/weekly"


@dataclass(frozen=True)
class RepoObservation:
    week: str
    source_bucket: str
    owner: str
    name: str
    full_name: str
    url: str
    description: str | None
    language: str | None
    stars: int | None
    forks: int | None
    created_at: str | None
    topics: tuple[str, ...]
    source_path: str
    archived: bool = False
    disabled: bool = False


@dataclass
class RepositoryHistory:
    key: str
    display_name: str
    owner: str
    name: str
    slug: str
    url: str
    description: str | None = None
    observations: list[RepoObservation] = field(default_factory=list)
    topics: Counter[str] = field(default_factory=Counter)
    languages: Counter[str] = field(default_factory=Counter)
    lifecycle: dict[str, Any] = field(default_factory=dict)
    related_repos: list[dict[str, Any]] = field(default_factory=list)

    @property
    def distinct_weeks(self) -> set[str]:
        return {observation.week for observation in self.observations}

    @property
    def first_seen_week(self) -> str:
        return min(self.distinct_weeks)

    @property
    def last_seen_week(self) -> str:
        return max(self.distinct_weeks)

    @property
    def latest_observation(self) -> RepoObservation:
        return sorted(self.observations, key=lambda item: item.week)[-1]

    @property
    def star_history(self) -> list[dict[str, int | str | None]]:
        by_week: dict[str, int | None] = {}
        for observation in sorted(self.observations, key=lambda item: item.week):
            if observation.stars is not None:
                by_week[observation.week] = observation.stars
        history: list[dict[str, int | str | None]] = []
        previous: int | None = None
        for week, stars in sorted(by_week.items()):
            delta = None if previous is None or stars is None else stars - previous
            history.append({"week": week, "stars": stars, "delta": delta})
            previous = stars
        return history


def slug_component(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9-]+", "-", normalized.lower())
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    return normalized or "repo"


def repo_slug(full_name: str) -> str:
    owner, name = split_full_name(full_name)
    return f"{slug_component(owner)}-{slug_component(name)}"


def split_full_name(full_name: str) -> tuple[str, str]:
    if "/" not in full_name:
        return "unknown", full_name
    owner, name = full_name.split("/", 1)
    return owner, name


def normalize_full_name(full_name: str) -> str:
    return full_name.strip().lower()


def topic_slug(topic: str) -> str:
    return slug_component(topic)


def weekly_permalink(week: str) -> str:
    year, week_id = week.split("-", 1)
    return f"{WEEKLY_LINK_PREFIX}/{year}/{week_id.lower()}/"


def week_start_date(week: str) -> date:
    year, week_id = week.split("-W", 1)
    return date.fromisocalendar(int(year), int(week_id), 1)


def add_years(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year + years)
    except ValueError:
        return day.replace(month=2, day=28, year=day.year + years)


def load_config(root: Path, config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or root / DEFAULT_CONFIG
    data: dict[str, Any] = {}
    if path.exists():
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    repo_pages = data.get("repo_pages", {})
    threshold = int(repo_pages.get("recurrence_threshold_distinct_weekly_issues", 3))
    operator = repo_pages.get("recurrence_threshold_operator", ">")
    if operator != ">":
        raise ValueError("repo page recurrence threshold currently supports only '>' semantics")
    return {
        "threshold": threshold,
        "operator": operator,
        "minimum_weeks": threshold + 1,
        "retention_years": int(repo_pages.get("retention_years", 3)),
        "lifecycle": repo_pages.get("lifecycle", {}),
    }


def raw_week_files(root: Path) -> list[Path]:
    candidates: dict[str, Path] = {}
    raw_dir = root / "data" / "raw"
    for path in sorted(raw_dir.glob("*.json")):
        candidates[path.stem] = path
    archive_dir = root / "data" / "archive" / "recovered-W23-W29"
    for path in sorted(archive_dir.glob("*/**/*.json")):
        candidates.setdefault(path.stem, path)
    return [candidates[week] for week in sorted(candidates)]


def observation_from_record(
    week: str, bucket: str, record: dict[str, Any], source_path: Path, root: Path
) -> RepoObservation | None:
    full_name = str(record.get("full_name") or "").strip()
    if not full_name:
        owner = str(record.get("owner") or "").strip()
        name = str(record.get("name") or "").strip()
        full_name = f"{owner}/{name}" if owner and name else ""
    if not full_name:
        return None
    owner, name = split_full_name(full_name)
    raw_topics = record.get("topics") or []
    topics = tuple(
        sorted({str(topic).strip().lower() for topic in raw_topics if str(topic).strip()})
    )
    stars = record.get("stars")
    forks = record.get("forks")
    return RepoObservation(
        week=week,
        source_bucket=bucket,
        owner=str(record.get("owner") or owner),
        name=str(record.get("name") or name),
        full_name=full_name,
        url=str(record.get("url") or f"https://github.com/{full_name}"),
        description=record.get("description"),
        language=record.get("language"),
        stars=int(stars) if isinstance(stars, int | float) else None,
        forks=int(forks) if isinstance(forks, int | float) else None,
        created_at=record.get("created_at"),
        topics=topics,
        source_path=str(source_path.relative_to(root)),
        archived=bool(record.get("archived", False)),
        disabled=bool(record.get("disabled", False)),
    )


def load_repository_histories(
    root: Path, lifecycle: dict[str, Any] | None = None
) -> dict[str, RepositoryHistory]:
    histories: dict[str, RepositoryHistory] = {}
    for path in raw_week_files(root):
        payload = json.loads(path.read_text(encoding="utf-8"))
        week = str(payload.get("week") or path.stem)
        seen_this_week: set[tuple[str, str]] = set()
        for bucket in ("trending_repos", "new_repos"):
            for record in payload.get(bucket, []) or []:
                observation = observation_from_record(week, bucket, record, path, root)
                if observation is None:
                    continue
                key = normalize_full_name(observation.full_name)
                if (key, week) in seen_this_week:
                    continue
                seen_this_week.add((key, week))
                history = histories.get(key)
                if history is None:
                    history = RepositoryHistory(
                        key=key,
                        display_name=observation.full_name,
                        owner=observation.owner,
                        name=observation.name,
                        slug=repo_slug(observation.full_name),
                        url=observation.url,
                        description=observation.description,
                    )
                    histories[key] = history
                history.observations.append(observation)
                history.display_name = observation.full_name
                history.owner = observation.owner
                history.name = observation.name
                history.url = observation.url
                history.description = observation.description or history.description
                history.topics.update(observation.topics)
                if observation.language:
                    history.languages.update([observation.language])
                if observation.archived:
                    history.lifecycle["status"] = "archived"
    for key, override in (lifecycle or {}).items():
        normalized = normalize_full_name(key)
        if normalized in histories and isinstance(override, dict):
            histories[normalized].lifecycle.update(override)
    apply_rename_lifecycle(histories)
    return histories


def apply_rename_lifecycle(histories: dict[str, RepositoryHistory]) -> None:
    for source in list(histories.values()):
        if source.lifecycle.get("status") != "renamed":
            continue
        renamed_to = source.lifecycle.get("renamed_to")
        if not renamed_to:
            continue
        target_key = normalize_full_name(renamed_to)
        target = histories.get(target_key)
        if target is None:
            owner, name = split_full_name(renamed_to)
            target = RepositoryHistory(
                key=target_key,
                display_name=renamed_to,
                owner=owner,
                name=name,
                slug=repo_slug(renamed_to),
                url=f"https://github.com/{renamed_to}",
                description=source.description,
            )
            histories[target_key] = target
        target.observations = source.observations + target.observations
        target.topics.update(source.topics)
        target.languages.update(source.languages)
        target.lifecycle.setdefault("renamed_from", source.display_name)


def eligible_repositories(
    histories: dict[str, RepositoryHistory], minimum_weeks: int
) -> list[RepositoryHistory]:
    return sorted(
        [
            history
            for history in histories.values()
            if len(history.distinct_weeks) >= minimum_weeks
            and history.lifecycle.get("status") != "renamed"
        ],
        key=lambda history: (-len(history.distinct_weeks), history.display_name.lower()),
    )


def attach_related_repositories(
    histories: dict[str, RepositoryHistory], eligible: list[RepositoryHistory]
) -> None:
    eligible_keys = {history.key for history in eligible}
    weeks: dict[str, list[str]] = defaultdict(list)
    for key, history in histories.items():
        for week in history.distinct_weeks:
            weeks[week].append(key)

    related: dict[str, Counter[str]] = {key: Counter() for key in eligible_keys}
    for keys in weeks.values():
        present_eligible = [key for key in keys if key in eligible_keys]
        for source in present_eligible:
            for target in keys:
                if source != target and target in eligible_keys:
                    related[source][target] += 1

    topic_sets = {key: set(history.topics) for key, history in histories.items()}
    for source in eligible_keys:
        source_topics = topic_sets[source]
        if not source_topics:
            continue
        for target, target_topics in topic_sets.items():
            if source == target or target not in eligible_keys:
                continue
            overlap = source_topics.intersection(target_topics)
            if overlap:
                related[source][target] += min(len(overlap), 4)

    for history in eligible:
        entries: list[dict[str, Any]] = []
        for target, score in related[history.key].most_common(8):
            target_history = histories[target]
            shared_weeks = sorted(
                history.distinct_weeks.intersection(target_history.distinct_weeks)
            )
            shared_topics = sorted(set(history.topics).intersection(target_history.topics))[:6]
            entries.append(
                {
                    "full_name": target_history.display_name,
                    "slug": target_history.slug,
                    "url": target_history.url,
                    "score": score,
                    "shared_weeks": shared_weeks[:6],
                    "shared_topics": shared_topics,
                }
            )
        history.related_repos = entries


def page_params(
    history: RepositoryHistory,
    config: dict[str, Any],
    rename_aliases: dict[str, list[str]],
    generated_at: datetime,
) -> dict[str, Any]:
    latest = history.latest_observation
    top_topics = [topic for topic, _count in history.topics.most_common(12)]
    lifecycle_status = history.lifecycle.get("status") or (
        "archived" if latest.archived else "active"
    )
    retained_until = None
    if lifecycle_status == "deleted":
        retained_until = add_years(
            week_start_date(history.last_seen_week), config["retention_years"]
        ).isoformat()
    title = f"{history.display_name} repository trend history"
    description = (
        f"Evergreen Claracle Observatory page for {history.display_name}: "
        f"{len(history.distinct_weeks)} weekly appearances, stars, velocity, topics, and related repos."
    )
    params: dict[str, Any] = {
        "title": title,
        "description": description,
        "date": generated_at.date().isoformat(),
        "draft": False,
        "layout": "repo",
        "generated_by": GENERATED_BY,
        "repo_owner": history.owner,
        "repo_name": history.name,
        "repo_full_name": history.display_name,
        "repo_url": history.url,
        "repo_slug": history.slug,
        "repo_description": history.description or "",
        "repo_language": history.languages.most_common(1)[0][0] if history.languages else "",
        "topics": top_topics,
        "first_seen_week": history.first_seen_week,
        "last_seen_week": history.last_seen_week,
        "as_of_week": history.last_seen_week,
        "source_paths": sorted({observation.source_path for observation in history.observations}),
        "distinct_weekly_issues": len(history.distinct_weeks),
        "recurrence_threshold": {
            "operator": config["operator"],
            "distinct_weekly_issues": config["threshold"],
            "minimum_weeks": config["minimum_weeks"],
        },
        "star_history": history.star_history,
        "weekly_appearances": [
            {"week": week, "url": weekly_permalink(week)} for week in sorted(history.distinct_weeks)
        ],
        "topic_links": [
            {"name": topic, "url": f"/topics/{topic_slug(topic)}/"} for topic in top_topics
        ],
        "related_repos": history.related_repos,
        "lifecycle": {
            "status": lifecycle_status,
            "as_of_week": history.last_seen_week,
            "retention_years": config["retention_years"],
            "retained_until": retained_until,
            "renamed_from": history.lifecycle.get("renamed_from"),
            "renamed_to": history.lifecycle.get("renamed_to"),
            "note": history.lifecycle.get("note", ""),
        },
        "methodology_url": "/methodology/",
    }
    aliases = rename_aliases.get(history.key, [])
    if aliases:
        params["aliases"] = aliases
    return params


def markdown_body(params: dict[str, Any]) -> str:
    name = params["repo_full_name"]
    status = params["lifecycle"]["status"]
    lines = [
        f"{name} has appeared in {params['distinct_weekly_issues']} Claracle weekly issues.",
        "",
    ]
    if status == "archived":
        lines.extend(
            [
                f"Lifecycle note: this repository is marked archived as of {params['as_of_week']}.",
                "",
            ]
        )
    if status == "deleted":
        lines.extend(
            [
                "Lifecycle note: this repository is marked deleted or inaccessible; current availability is not claimed.",
                f"This page is retained until at least {params['lifecycle']['retained_until']} based on the last seen week {params['last_seen_week']}.",
                "",
            ]
        )
    lines.extend(
        [
            "See the generated Observatory sections below for growth history, derived star velocity, weekly appearances, related repositories, and provenance.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def write_yaml_page(path: Path, params: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = yaml.safe_dump(params, sort_keys=False, allow_unicode=True, width=120)
    path.write_text(f"---\n{frontmatter}---\n\n{markdown_body(params)}", encoding="utf-8")


def clean_generated_repo_pages(content_repo: Path) -> None:
    if not content_repo.exists():
        return
    for index_path in content_repo.glob("*/index.md"):
        if f"generated_by: {GENERATED_BY}" in index_path.read_text(encoding="utf-8"):
            shutil.rmtree(index_path.parent)


def rename_aliases(histories: dict[str, RepositoryHistory]) -> dict[str, list[str]]:
    aliases: dict[str, list[str]] = defaultdict(list)
    for history in histories.values():
        if history.lifecycle.get("status") != "renamed":
            continue
        renamed_to = history.lifecycle.get("renamed_to")
        if not renamed_to:
            continue
        aliases[normalize_full_name(renamed_to)].append(f"/repo/{history.slug}/")
    return aliases


def repository_index_content(generated_count: int, config: dict[str, Any]) -> str:
    params = {
        "title": "Repository Observatory",
        "description": "Evergreen Claracle pages for recurring GitHub repositories tracked across weekly issues.",
        "generated_by": GENERATED_BY,
        "repo_pages_generated": generated_count,
        "recurrence_threshold": {
            "operator": config["operator"],
            "distinct_weekly_issues": config["threshold"],
            "minimum_weeks": config["minimum_weeks"],
        },
    }
    frontmatter = yaml.safe_dump(params, sort_keys=False, width=120)
    return (
        f"---\n{frontmatter}---\n\n"
        "Claracle generates repository pages only after a project appears in more than three distinct weekly issues.\n"
    )


def write_repository_pages(
    root: Path, histories: dict[str, RepositoryHistory], config: dict[str, Any]
) -> list[Path]:
    generated_at = datetime.now(timezone.utc)
    eligible = eligible_repositories(histories, config["minimum_weeks"])
    attach_related_repositories(histories, eligible)
    aliases = rename_aliases(histories)
    content_repo = root / "content" / "repo"
    clean_generated_repo_pages(content_repo)
    content_repo.mkdir(parents=True, exist_ok=True)
    (content_repo / "_index.md").write_text(
        repository_index_content(len(eligible), config), encoding="utf-8"
    )
    written: list[Path] = []
    derived: list[dict[str, Any]] = []
    for history in eligible:
        params = page_params(history, config, aliases, generated_at)
        output_path = content_repo / history.slug / "index.md"
        write_yaml_page(output_path, params)
        written.append(output_path)
        derived.append(params)
    derived_path = root / "data" / "derived" / "observatory" / "repositories.json"
    derived_path.parent.mkdir(parents=True, exist_ok=True)
    derived_path.write_text(json.dumps(derived, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return written


def generate(root: Path, config_path: Path | None = None) -> list[Path]:
    config = load_config(root, config_path)
    histories = load_repository_histories(root, config["lifecycle"])
    return write_repository_pages(root, histories, config)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    written = generate(args.root.resolve(), args.config)
    print(f"Generated {len(written)} repository pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
