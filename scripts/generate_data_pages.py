#!/usr/bin/env python3
"""Generate read-only Claracle data pages from checked-in data artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
ARCHIVE_DIR = REPO_ROOT / "data" / "archive" / "recovered-W23-W29"
CONTENT_DIR = REPO_ROOT / "content" / "data"
METHODOLOGY_PATH = "/methodology/"
MAX_RANKING_ROWS = 100

WEEK_RE = re.compile(r"^\d{4}-W\d{2}$")
MCP_RE = re.compile(r"\bmcp\b", re.IGNORECASE)
AI_TEXT_RE = re.compile(
    r"\b(ai|agent|agents|llm|llms|openai|claude|codex|ollama|huggingface|"
    r"langchain|transformers|machine learning|machine-learning|deep learning|"
    r"neural|rag|mcp|model context protocol)\b",
    re.IGNORECASE,
)
AI_TOPIC_PARTS = {
    "ai",
    "agent",
    "agents",
    "llm",
    "openai",
    "claude",
    "codex",
    "ollama",
    "huggingface",
    "transformers",
    "machine-learning",
    "deep-learning",
    "rag",
    "mcp",
}


@dataclass(frozen=True)
class WeekArtifact:
    week: str
    crawled_at: datetime
    path: Path
    payload: dict[str, Any]


@dataclass(frozen=True)
class RepoObservation:
    week: str
    crawled_at: datetime
    source_bucket: str
    source_path: Path
    full_name: str
    display_name: str
    url: str
    description: str
    language: str
    stars: int
    forks: int | None
    created_at: str
    topics: tuple[str, ...]


def parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(UTC)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def repo_slug(full_name: str) -> str:
    normalized = unicodedata.normalize("NFKD", full_name.lower())
    slug = re.sub(r"[^a-z0-9]+", "-", normalized)
    return re.sub(r"-+", "-", slug).strip("-")


def toml_string(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list | tuple):
        return "[" + ", ".join(toml_value(item) for item in value) + "]"
    return toml_string(value)


def frontmatter(data: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = ["+++"]
    for key, value in data.items():
        lines.append(f"{key} = {toml_value(value)}")
    for row in rows:
        lines.append("")
        lines.append("[[ranking]]")
        for key, value in row.items():
            lines.append(f"{key} = {toml_value(value)}")
    lines.append("+++")
    return "\n".join(lines) + "\n\n"


def discover_week_artifacts() -> list[WeekArtifact]:
    selected: dict[str, Path] = {}
    for path in sorted(RAW_DIR.glob("*.json")):
        week = path.stem
        if WEEK_RE.match(week):
            selected[week] = path
    if ARCHIVE_DIR.exists():
        for path in sorted(ARCHIVE_DIR.glob("*/????-W??.json")):
            week = path.stem
            if WEEK_RE.match(week) and week not in selected:
                selected[week] = path

    artifacts: list[WeekArtifact] = []
    for week, path in sorted(selected.items()):
        payload = json.loads(path.read_text(encoding="utf-8"))
        crawled_at = parse_datetime(
            payload.get("crawled_at") or payload.get("metadata", {}).get("crawled_at")
        )
        artifacts.append(WeekArtifact(week=week, crawled_at=crawled_at, path=path, payload=payload))
    if not artifacts:
        raise SystemExit("No weekly raw artifacts found under data/raw or recovered archive.")
    return artifacts


def coerce_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def collect_observations(artifacts: list[WeekArtifact]) -> list[RepoObservation]:
    observations: list[RepoObservation] = []
    seen_week_repo: dict[tuple[str, str], RepoObservation] = {}
    for artifact in artifacts:
        for bucket in ("trending_repos", "new_repos"):
            for repo in artifact.payload.get(bucket, []) or []:
                full_name = str(
                    repo.get("full_name") or f"{repo.get('owner', '')}/{repo.get('name', '')}"
                ).strip("/")
                if "/" not in full_name:
                    continue
                key = (artifact.week, full_name.lower())
                topics = tuple(str(topic) for topic in (repo.get("topics") or []))
                observation = RepoObservation(
                    week=artifact.week,
                    crawled_at=artifact.crawled_at,
                    source_bucket=bucket,
                    source_path=artifact.path,
                    full_name=full_name,
                    display_name=full_name,
                    url=str(repo.get("url") or f"https://github.com/{full_name}"),
                    description=str(repo.get("description") or ""),
                    language=str(repo.get("language") or "Unknown"),
                    stars=coerce_int(repo.get("stars")),
                    forks=coerce_int(repo.get("forks")) if repo.get("forks") is not None else None,
                    created_at=str(repo.get("created_at") or ""),
                    topics=topics,
                )
                existing = seen_week_repo.get(key)
                if existing is None or observation.stars > existing.stars:
                    seen_week_repo[key] = observation
    observations.extend(seen_week_repo.values())
    return sorted(observations, key=lambda item: (item.week, item.full_name.lower()))


def latest_by_repo(observations: list[RepoObservation]) -> dict[str, RepoObservation]:
    latest: dict[str, RepoObservation] = {}
    for obs in observations:
        key = obs.full_name.lower()
        if key not in latest or (obs.week, obs.stars) > (latest[key].week, latest[key].stars):
            latest[key] = obs
    return latest


def grouped_by_repo(observations: list[RepoObservation]) -> dict[str, list[RepoObservation]]:
    grouped: dict[str, list[RepoObservation]] = defaultdict(list)
    for obs in observations:
        grouped[obs.full_name.lower()].append(obs)
    return {key: sorted(value, key=lambda item: item.week) for key, value in grouped.items()}


def format_int(value: int) -> str:
    return f"{value:,}"


def source_summary(paths: set[Path]) -> str:
    relative = sorted(path.relative_to(REPO_ROOT).as_posix() for path in paths)
    if len(relative) <= 3:
        return ", ".join(relative)
    return f"{relative[0]} through {relative[-1]} ({len(relative)} weekly raw artifacts)"


def row(
    rank: int,
    obs: RepoObservation,
    metric_value: int,
    metric_label: str,
    context: str,
) -> dict[str, Any]:
    return {
        "rank": rank,
        "repo": obs.display_name,
        "repo_key": obs.full_name.lower(),
        "repo_slug": repo_slug(obs.full_name),
        "url": obs.url,
        "metric_value": metric_value,
        "metric_label": metric_label,
        "context": context,
        "language": obs.language,
        "latest_stars": obs.stars,
        "last_seen_week": obs.week,
    }


def page_content(summary: str) -> str:
    return (
        f"{summary}\n\n"
        "This page is generated from checked-in Claracle artifacts. It does not "
        "perform a fresh crawl and can be regenerated with "
        "`python3 scripts/generate_data_pages.py`.\n"
    )


def render_page(
    path: Path,
    *,
    title: str,
    description: str,
    summary: str,
    date: datetime,
    ranking_id: str,
    metric_definition: str,
    as_of_week: str,
    as_of: str,
    source: str,
    cadence: str,
    rows: list[dict[str, Any]],
) -> str:
    data = {
        "title": title,
        "date": date.isoformat().replace("+00:00", "Z"),
        "lastmod": date.isoformat().replace("+00:00", "Z"),
        "draft": False,
        "summary": summary,
        "description": description,
        "layout": "single",
        "ranking_id": ranking_id,
        "metric_definition": metric_definition,
        "as_of": as_of,
        "as_of_week": as_of_week,
        "methodology_url": METHODOLOGY_PATH,
        "source": source,
        "cadence": cadence,
        "categories": ["Data Observatory"],
        "tags": ["data-pages", "github-trends", "rankings"],
        "keywords": [
            "Claracle data pages",
            "GitHub AI repository ranking",
            ranking_id.replace("-", " "),
        ],
        "hideMeta": True,
    }
    return frontmatter(data, rows) + page_content(summary)


def build_pages() -> dict[Path, str]:
    artifacts = discover_week_artifacts()
    observations = collect_observations(artifacts)
    latest_week = max(artifact.week for artifact in artifacts)
    latest_artifact = max(artifacts, key=lambda item: item.week)
    as_of = latest_artifact.crawled_at.date().isoformat()
    cadence = "Monthly regeneration from checked-in data/raw and recovered archive artifacts."
    all_source = source_summary({artifact.path for artifact in artifacts})

    latest_month = latest_artifact.crawled_at.strftime("%Y-%m")
    month_observations = [
        obs
        for obs in observations
        if obs.crawled_at.strftime("%Y-%m") == latest_month and is_ai_project(obs)
    ]
    month_latest = latest_by_repo(month_observations)
    top_month_rows = [
        row(
            rank=index,
            obs=obs,
            metric_value=obs.stars,
            metric_label=f"{format_int(obs.stars)} stars",
            context=f"Latest observed in {obs.week}; {obs.language}; {len(obs.topics)} raw topics.",
        )
        for index, obs in enumerate(
            sorted(month_latest.values(), key=lambda item: (-item.stars, item.full_name.lower()))[
                :MAX_RANKING_ROWS
            ],
            start=1,
        )
    ]

    grouped = grouped_by_repo(observations)
    fastest_candidates: list[tuple[int, RepoObservation, RepoObservation]] = []
    latest_year = latest_artifact.crawled_at.year
    for repo_observations in grouped.values():
        year_obs = [obs for obs in repo_observations if obs.crawled_at.year == latest_year]
        if len(year_obs) < 2 or not any(is_ai_project(obs) for obs in year_obs):
            continue
        first, latest = year_obs[0], year_obs[-1]
        delta = latest.stars - first.stars
        if delta > 0:
            fastest_candidates.append((delta, first, latest))
    fastest_rows = [
        row(
            rank=index,
            obs=latest,
            metric_value=delta,
            metric_label=f"+{format_int(delta)} stars",
            context=(
                f"{format_int(first.stars)} → {format_int(latest.stars)} stars "
                f"from {first.week} to {latest.week}."
            ),
        )
        for index, (delta, first, latest) in enumerate(
            sorted(
                fastest_candidates,
                key=lambda item: (-item[0], -item[2].stars, item[2].full_name.lower()),
            )[:MAX_RANKING_ROWS],
            start=1,
        )
    ]

    mcp_latest = [obs for obs in latest_by_repo(observations).values() if is_mcp_project(obs)]
    mcp_rows = [
        row(
            rank=index,
            obs=obs,
            metric_value=obs.stars,
            metric_label=f"{format_int(obs.stars)} stars",
            context=f"Matched MCP signal; latest observed in {obs.week}; {obs.language}.",
        )
        for index, obs in enumerate(
            sorted(mcp_latest, key=lambda item: (-item.stars, item.full_name.lower()))[
                :MAX_RANKING_ROWS
            ],
            start=1,
        )
    ]

    pages = {
        CONTENT_DIR / "_index.md": frontmatter(
            {
                "title": "Data pages",
                "date": latest_artifact.crawled_at.isoformat().replace("+00:00", "Z"),
                "draft": False,
                "summary": "Citable Claracle rankings generated from checked-in GitHub trend artifacts.",
                "description": "Browse read-only GitHub trend rankings with source provenance, as-of dates, and metric definitions.",
                "categories": ["Data Observatory"],
                "tags": ["data-pages", "github-trends"],
            },
            [],
        )
        + (
            "These data pages are generated from checked-in weekly raw artifacts, "
            "not from live GitHub API calls.\n"
        ),
        CONTENT_DIR / "top-ai-repositories-this-month" / "index.md": render_page(
            CONTENT_DIR / "top-ai-repositories-this-month" / "index.md",
            title="Top 100 AI repositories this month",
            description=(
                "The most-starred repositories observed by Claracle in the latest monthly "
                "GitHub trend window."
            ),
            summary=(
                f"Top {len(top_month_rows)} repositories observed in {latest_month}, ranked by "
                "latest checked-in star count."
            ),
            date=latest_artifact.crawled_at,
            ranking_id="top-ai-repositories-this-month",
            metric_definition=(
                "Latest absolute GitHub stars for repositories observed in the latest crawl month."
            ),
            as_of_week=latest_week,
            as_of=as_of,
            source=source_summary({obs.source_path for obs in month_observations}),
            cadence=cadence,
            rows=top_month_rows,
        ),
        CONTENT_DIR / "fastest-growing-ai-repositories-this-year" / "index.md": render_page(
            CONTENT_DIR / "fastest-growing-ai-repositories-this-year" / "index.md",
            title="Fastest-growing AI repositories this year",
            description=(
                "AI and developer-tool repositories with the largest observed star gains "
                "across the current year's checked-in Claracle data."
            ),
            summary=(
                f"Top {len(fastest_rows)} repositories ranked by derived star gain across "
                f"{latest_year} observations."
            ),
            date=latest_artifact.crawled_at,
            ranking_id="fastest-growing-ai-repositories-this-year",
            metric_definition=(
                "Derived star gain: latest observed stars minus earliest observed stars in the year."
            ),
            as_of_week=latest_week,
            as_of=as_of,
            source=all_source,
            cadence=cadence,
            rows=fastest_rows,
        ),
        CONTENT_DIR / "most-starred-mcp-projects" / "index.md": render_page(
            CONTENT_DIR / "most-starred-mcp-projects" / "index.md",
            title="Most-starred MCP projects",
            description=(
                "Model Context Protocol projects ranked by latest observed GitHub stars "
                "from Claracle raw artifacts."
            ),
            summary=(
                f"Top {len(mcp_rows)} MCP-related repositories ranked by latest checked-in stars."
            ),
            date=latest_artifact.crawled_at,
            ranking_id="most-starred-mcp-projects",
            metric_definition=(
                "Latest absolute GitHub stars for repositories with MCP or Model Context Protocol signals."
            ),
            as_of_week=latest_week,
            as_of=as_of,
            source=all_source,
            cadence=cadence,
            rows=mcp_rows,
        ),
    }
    return pages


def is_mcp_project(obs: RepoObservation) -> bool:
    topic_blob = " ".join(obs.topics).lower()
    text_blob = f"{obs.full_name} {obs.description}".lower()
    return (
        "mcp" in {topic.lower() for topic in obs.topics}
        or "modelcontextprotocol" in topic_blob
        or "modelcontextprotocol" in text_blob
        or "model context protocol" in text_blob
        or bool(MCP_RE.search(text_blob))
    )


def is_ai_project(obs: RepoObservation) -> bool:
    topics = {topic.lower() for topic in obs.topics}
    if any(any(part in topic for part in AI_TOPIC_PARTS) for topic in topics):
        return True
    text_blob = f"{obs.full_name} {obs.description}".lower()
    return bool(AI_TEXT_RE.search(text_blob))


def write_pages(pages: dict[Path, str], check: bool = False) -> int:
    changed: list[Path] = []
    for path, content in pages.items():
        existing = path.read_text(encoding="utf-8") if path.exists() else None
        if existing != content:
            changed.append(path)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    if check and changed:
        for path in changed:
            print(f"stale: {path.relative_to(REPO_ROOT)}", file=sys.stderr)
        return 1
    for path in sorted(pages):
        print(path.relative_to(REPO_ROOT))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated pages are stale.")
    args = parser.parse_args()
    return write_pages(build_pages(), check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
