#!/usr/bin/env python3
"""Generate versioned BR-004 ranking artifacts from checked-in Claracle raw data."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import generate_data_pages

SCHEMA_VERSION = "1.0.0"
DEFAULT_OUTPUT_DIR = Path("static/data/rankings")
SUMMARY_OUTPUT = Path("data/observatory/ranking_summary.json")
METHODOLOGY_URL = "/methodology/"
MAX_RANKING_ROWS = generate_data_pages.MAX_RANKING_ROWS


@dataclass(frozen=True)
class RankingSpec:
    ranking_id: str
    title: str
    url: str
    metric_label: str
    metric_definition: str


RANKING_SPECS = (
    RankingSpec(
        ranking_id="top-ai-repositories-this-month",
        title="Top AI repositories this month",
        url="/data/top-ai-repositories-this-month/",
        metric_label="Stars",
        metric_definition="Latest absolute GitHub stars for repositories observed in the latest crawl month.",
    ),
    RankingSpec(
        ranking_id="most-starred-mcp-projects",
        title="Most starred MCP projects",
        url="/data/most-starred-mcp-projects/",
        metric_label="Stars",
        metric_definition="Latest absolute GitHub stars for repositories with MCP or Model Context Protocol signals.",
    ),
    RankingSpec(
        ranking_id="fastest-growing-ai-repositories-this-year",
        title="Fastest-growing AI repositories this year",
        url="/data/fastest-growing-ai-repositories-this-year/",
        metric_label="Star growth",
        metric_definition="Derived star gain: latest observed stars minus earliest observed stars in the year.",
    ),
)
SPEC_BY_ID = {spec.ranking_id: spec for spec in RANKING_SPECS}


def _week_date(period: str, weekday: int) -> date:
    year, week = period.split("-W", 1)
    return date.fromisocalendar(int(year), int(week), weekday)


def _relative_paths(root: Path, paths: set[Path]) -> list[str]:
    return sorted(path.resolve().relative_to(root).as_posix() for path in paths)


def _checksum(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def discover_week_artifacts(
    *,
    raw_dir: Path | None = None,
    archive_dir: Path | None = None,
) -> list[generate_data_pages.WeekArtifact]:
    raw_dir = (raw_dir or generate_data_pages.RAW_DIR).resolve()
    archive_dir = (archive_dir or generate_data_pages.ARCHIVE_DIR).resolve()
    selected: dict[str, Path] = {}
    for path in sorted(raw_dir.glob("*.json")):
        if generate_data_pages.WEEK_RE.match(path.stem):
            selected[path.stem] = path
    if archive_dir.exists():
        for path in sorted(archive_dir.glob("*/????-W??.json")):
            if generate_data_pages.WEEK_RE.match(path.stem) and path.stem not in selected:
                selected[path.stem] = path

    artifacts: list[generate_data_pages.WeekArtifact] = []
    for week, path in sorted(selected.items()):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("artifact payload must be an object")
            crawled_at = generate_data_pages.parse_datetime(
                payload.get("crawled_at") or payload.get("metadata", {}).get("crawled_at"),
                week,
            )
        except (json.JSONDecodeError, OSError, ValueError) as error:
            print(f"Skipping malformed raw artifact {path}: {error}", file=sys.stderr)
            continue
        artifacts.append(
            generate_data_pages.WeekArtifact(
                week=week,
                crawled_at=crawled_at,
                path=path,
                payload=payload,
            )
        )
    if not artifacts:
        raise ValueError("No valid weekly raw artifacts found under data/raw or recovered archive.")
    return artifacts


def ranking_record(
    *,
    rank: int,
    obs: generate_data_pages.RepoObservation,
    metric_key: str,
    metric_value: int,
    metric_label: str,
    comparison_value: int | None = None,
    comparison_label: str | None = None,
) -> dict[str, Any]:
    return {
        "rank": rank,
        "repository_id": generate_data_pages.repo_slug(obs.full_name),
        "full_name": obs.full_name,
        "github_url": generate_data_pages.validate_github_url(obs.url),
        "metric_key": metric_key,
        "metric_value": metric_value,
        "metric_label": metric_label,
        "comparison_value": comparison_value,
        "comparison_label": comparison_label,
        "language": obs.language,
        "context_summary": generate_data_pages.build_context_summary(obs.description),
        "context_accessible_text": generate_data_pages.build_context_accessible_text(
            obs.description
        ),
    }


def ranking_envelope(
    *,
    root: Path,
    spec: RankingSpec,
    generated_at: datetime,
    covered_start: date,
    covered_end: date,
    covered_label: str,
    source_paths: set[Path],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    resolved_paths = sorted(path.resolve() for path in source_paths)
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "ranking",
        "ranking_id": spec.ranking_id,
        "metric_label": spec.metric_label,
        "metric_definition": spec.metric_definition,
        "generated_at": generated_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "covered_period": {
            "start": covered_start.isoformat(),
            "end": covered_end.isoformat(),
            "label": covered_label,
        },
        "provenance": {
            "generator": "scripts/generate_ranking_artifacts.py",
            "source_paths": _relative_paths(root, set(resolved_paths)),
            "methodology_url": METHODOLOGY_URL,
            "source_checksum": _checksum(resolved_paths),
        },
        "records": sorted(records, key=lambda item: (item["rank"], item["full_name"].lower())),
    }


def build_ranking_payloads(
    root: Path,
    *,
    raw_dir: Path | None = None,
    archive_dir: Path | None = None,
) -> dict[str, dict[str, Any]]:
    artifacts = discover_week_artifacts(
        raw_dir=raw_dir or (root / "data/raw"),
        archive_dir=archive_dir or (root / "data/archive/recovered-W23-W29"),
    )
    observations = generate_data_pages.collect_observations(artifacts)
    latest_artifact = max(artifacts, key=lambda item: item.week)
    latest_week = latest_artifact.week
    latest_month = latest_artifact.crawled_at.strftime("%Y-%m")
    latest_year = latest_artifact.crawled_at.year
    first_artifact = min(artifacts, key=lambda item: item.week)
    first_date = first_artifact.crawled_at.date()
    latest_date = latest_artifact.crawled_at.date()

    month_observations = [
        obs
        for obs in observations
        if obs.crawled_at.strftime("%Y-%m") == latest_month
        and generate_data_pages.is_ai_project(obs)
    ]
    month_latest = generate_data_pages.latest_by_repo(month_observations)
    top_month_records = [
        ranking_record(
            rank=index,
            obs=obs,
            metric_key="stars",
            metric_value=obs.stars,
            metric_label=f"{generate_data_pages.format_int(obs.stars)} stars",
        )
        for index, obs in enumerate(
            sorted(month_latest.values(), key=lambda item: (-item.stars, item.full_name.lower()))[
                :MAX_RANKING_ROWS
            ],
            start=1,
        )
    ]
    top_month_paths = {obs.source_path.resolve() for obs in month_observations} or {
        latest_artifact.path.resolve()
    }
    if month_observations:
        top_month_start = min(obs.crawled_at.date() for obs in month_observations)
        top_month_end = max(obs.crawled_at.date() for obs in month_observations)
    else:
        top_month_start = latest_date
        top_month_end = latest_date

    mcp_latest = [
        obs
        for obs in generate_data_pages.latest_by_repo(observations).values()
        if generate_data_pages.is_mcp_project(obs)
    ]
    mcp_records = [
        ranking_record(
            rank=index,
            obs=obs,
            metric_key="stars",
            metric_value=obs.stars,
            metric_label=f"{generate_data_pages.format_int(obs.stars)} stars",
        )
        for index, obs in enumerate(
            sorted(mcp_latest, key=lambda item: (-item.stars, item.full_name.lower()))[
                :MAX_RANKING_ROWS
            ],
            start=1,
        )
    ]
    mcp_paths = {artifact.path.resolve() for artifact in artifacts}

    grouped = generate_data_pages.grouped_by_repo(observations)
    fastest_candidates: list[
        tuple[int, generate_data_pages.RepoObservation, generate_data_pages.RepoObservation]
    ] = []
    fastest_source_paths: set[Path] = set()
    for repo_observations in grouped.values():
        year_obs = [obs for obs in repo_observations if obs.crawled_at.year == latest_year]
        if len(year_obs) < 2 or not any(generate_data_pages.is_ai_project(obs) for obs in year_obs):
            continue
        first, latest = year_obs[0], year_obs[-1]
        delta = latest.stars - first.stars
        if delta > 0:
            fastest_candidates.append((delta, first, latest))
            for observation in year_obs:
                fastest_source_paths.add(observation.source_path.resolve())
    fastest_records = [
        ranking_record(
            rank=index,
            obs=latest,
            metric_key="period_growth",
            metric_value=delta,
            metric_label=f"+{generate_data_pages.format_int(delta)} stars",
            comparison_value=first.stars,
            comparison_label=(
                f"{generate_data_pages.format_int(first.stars)} → "
                f"{generate_data_pages.format_int(latest.stars)} stars"
            ),
        )
        for index, (delta, first, latest) in enumerate(
            sorted(fastest_candidates, key=lambda item: (-item[0], item[2].full_name.lower()))[
                :MAX_RANKING_ROWS
            ],
            start=1,
        )
    ]

    payloads = {
        "top-ai-repositories-this-month": ranking_envelope(
            root=root,
            spec=SPEC_BY_ID["top-ai-repositories-this-month"],
            generated_at=latest_artifact.crawled_at,
            covered_start=top_month_start,
            covered_end=top_month_end,
            covered_label=latest_week,
            source_paths=top_month_paths,
            records=top_month_records,
        ),
        "most-starred-mcp-projects": ranking_envelope(
            root=root,
            spec=SPEC_BY_ID["most-starred-mcp-projects"],
            generated_at=latest_artifact.crawled_at,
            covered_start=first_date,
            covered_end=latest_date,
            covered_label=latest_week,
            source_paths=mcp_paths,
            records=mcp_records,
        ),
        "fastest-growing-ai-repositories-this-year": ranking_envelope(
            root=root,
            spec=SPEC_BY_ID["fastest-growing-ai-repositories-this-year"],
            generated_at=latest_artifact.crawled_at,
            covered_start=date(latest_year, 1, 1),
            covered_end=latest_date,
            covered_label=latest_week,
            source_paths=fastest_source_paths or {latest_artifact.path.resolve()},
            records=fastest_records,
        ),
    }
    return payloads


def build_ranking_summary(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    latest_generated = max(payload["generated_at"] for payload in payloads.values())
    records = [
        {
            "ranking_id": spec.ranking_id,
            "title": spec.title,
            "url": spec.url,
            "record_count": len(payloads[spec.ranking_id]["records"]),
            "metric_definition": payloads[spec.ranking_id]["metric_definition"],
            "as_of_week": payloads[spec.ranking_id]["covered_period"]["label"],
        }
        for spec in RANKING_SPECS
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "ranking_summary",
        "generated_at": latest_generated,
        "records": records,
    }


def build_outputs(root: Path, *, output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[Path, str]:
    payloads = build_ranking_payloads(root)
    outputs = {
        root / output_dir / f"{ranking_id}.json": _render(payload)
        for ranking_id, payload in payloads.items()
    }
    outputs[root / SUMMARY_OUTPUT] = _render(build_ranking_summary(payloads))
    return outputs


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    outputs = build_outputs(root, output_dir=args.output_dir)
    stale: list[Path] = []
    for path, content in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    if stale:
        for path in stale:
            print(f"stale: {path.relative_to(root)}", file=sys.stderr)
        return 1
    for path in sorted(outputs):
        print(path.relative_to(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
