"""Generate the versioned BR-003 repository explorer artifact."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import observatory_repos

SCHEMA_VERSION = "1.0.0"
SOURCE_PATH = "data/derived/observatory/repositories.json"
DEFAULT_OUTPUTS = (
    Path("data/observatory/repository_summary.json"),
    Path("static/data/repositories.json"),
)


def _week_date(period: str, weekday: int) -> date:
    year, week = period.split("-W", 1)
    return date.fromisocalendar(int(year), int(week), weekday)


def _summary(value: str, limit: int = 240) -> str:
    text = re.sub(r"<[^>]+>", " ", html.unescape(value))
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    clipped = text[:limit].rsplit(" ", 1)[0].rstrip(" ,.;:-")
    return f"{clipped}…"


def _record(source: dict[str, Any]) -> dict[str, Any]:
    history = source.get("star_history") or []
    deltas = [point.get("delta") for point in history[-4:] if point.get("delta") is not None]
    lifecycle = source.get("lifecycle") or {}
    status = str(lifecycle.get("status") or "active")
    if status not in {"active", "archived", "disabled", "deleted", "renamed", "retained"}:
        status = "active"
    github_url = str(source["repo_url"])
    parsed_url = urlparse(github_url)
    if parsed_url.scheme != "https" or parsed_url.netloc.lower() != "github.com":
        raise ValueError(f"Repository URL must use https://github.com: {github_url}")
    return {
        "id": source["repo_slug"],
        "full_name": source["repo_full_name"],
        "name": source["repo_name"],
        "owner": source["repo_owner"],
        "github_url": github_url,
        "language": source.get("repo_language"),
        "topics": sorted({str(topic) for topic in source.get("tags") or []}),
        "status": status,
        "first_seen_period": source["first_seen_week"],
        "last_seen_period": source["last_seen_week"],
        "recent_momentum": sum(int(delta) for delta in deltas) if deltas else None,
        "context_summary": _summary(str(source.get("repo_description") or "")),
        "star_history": [
            {
                "period": point["week"],
                "stars": int(point["stars"]),
                "delta": point.get("delta"),
            }
            for point in history
        ],
    }


def _crawl_source(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    config = observatory_repos.load_config(root)
    identity_backfill = observatory_repos.load_identity_backfill(config["identity_backfill_path"])
    lifecycle = observatory_repos.merge_identity_backfill_overrides(
        config["lifecycle"], identity_backfill
    )
    ledger = observatory_repos.load_lifecycle_ledger(config["ledger_path"])
    histories = observatory_repos.load_repository_histories(
        root,
        lifecycle,
        ledger,
        identity_backfill,
    )
    as_of = max(
        observatory_repos.week_start_date(history.last_seen_week) for history in histories.values()
    )
    observatory_repos.reconcile_lifecycle(histories, config, as_of)
    eligible = observatory_repos.eligible_repositories(histories, config["minimum_weeks"])
    source_paths = sorted(
        {observation.source_path for history in eligible for observation in history.observations}
    )
    source = []
    for history in eligible:
        latest = history.latest_observation
        source.append(
            {
                "date": observatory_repos.week_start_date(history.last_seen_week).isoformat(),
                "repo_slug": history.slug,
                "repo_full_name": history.display_name,
                "repo_name": history.name,
                "repo_owner": history.owner,
                "repo_url": history.url,
                "repo_description": history.description or latest.description or "",
                "repo_language": latest.language,
                "tags": sorted(history.topics),
                "first_seen_week": history.first_seen_week,
                "last_seen_week": history.last_seen_week,
                "lifecycle": history.lifecycle,
                "star_history": history.star_history,
            }
        )
    return source, source_paths


def build_payload(root: Path, *, from_crawl: bool = False) -> dict[str, Any]:
    if from_crawl:
        source, source_paths = _crawl_source(root)
        source_bytes = json.dumps(source, sort_keys=True, separators=(",", ":")).encode()
    else:
        source_path = root / SOURCE_PATH
        source_bytes = source_path.read_bytes()
        source = json.loads(source_bytes)
        source_paths = [SOURCE_PATH]
    if not isinstance(source, list) or not source:
        raise ValueError("Repository source must be a non-empty list")

    records = sorted(
        (_record(item) for item in source),
        key=lambda item: (
            -(item["recent_momentum"] if item["recent_momentum"] is not None else -1),
            item["full_name"].lower(),
        ),
    )
    first_period = min(item["first_seen_period"] for item in records)
    last_period = max(item["last_seen_period"] for item in records)
    generated_date = max(str(item["date"]) for item in source)
    generated_at = datetime.combine(
        date.fromisoformat(generated_date),
        datetime.min.time(),
        tzinfo=timezone.utc,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "repositories",
        "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
        "covered_period": {
            "start": _week_date(first_period, 1).isoformat(),
            "end": _week_date(last_period, 7).isoformat(),
            "label": f"{first_period}–{last_period}",
        },
        "provenance": {
            "generator": "scripts/generate_repository_summary.py",
            "source_paths": source_paths,
            "methodology_url": "/methodology/",
            "source_checksum": hashlib.sha256(source_bytes).hexdigest(),
        },
        "records": records,
    }


def rendered_payload(root: Path, *, from_crawl: bool = False) -> str:
    return json.dumps(build_payload(root, from_crawl=from_crawl), indent=2, sort_keys=True) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--from-crawl",
        action="store_true",
        help="Build from the current crawl corpus even when detail-page generation is disabled.",
    )
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    rendered = rendered_payload(root, from_crawl=args.from_crawl)
    stale = []
    for relative in DEFAULT_OUTPUTS:
        output = root / relative
        if args.check:
            if not output.exists() or output.read_text(encoding="utf-8") != rendered:
                stale.append(str(relative))
            continue
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    if stale:
        raise SystemExit(f"Repository summary is stale: {', '.join(stale)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
