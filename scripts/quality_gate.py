#!/usr/bin/env python3
"""Quality threshold enforcement for SquadScope (warn-only).

Checks whether scored repos meet minimum coverage thresholds defined in
the topic config. Emits GitHub Actions warning annotations but never
blocks the pipeline (always exits 0).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from scripts.topic_paths import load_topic_id, metrics_dir

DEFAULT_QUALITY = {
    "min_repos_per_week": 5,
    "max_repos_per_week": 30,
    "min_quality_score": 60,
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quality threshold gate (warn-only).")
    parser.add_argument("--input", default=None, type=Path, help="Path to scored repos JSON file.")
    parser.add_argument(
        "--config", default="squadscope.topic.yml", type=Path, help="Path to topic config YAML."
    )
    parser.add_argument("--topic", default=None, help="Topic ID override.")
    return parser.parse_args(argv)


def load_config(path: Path) -> dict[str, Any]:
    """Load topic config YAML. Returns empty dict on failure."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        try:
            return yaml.safe_load(text) or {}
        except Exception:
            return {}
    # Minimal fallback: not needed in practice since yaml is available in CI
    return {}  # pragma: no cover


def get_quality_config(config: dict[str, Any]) -> dict[str, Any]:
    """Extract quality section with defaults."""
    quality = config.get("quality", {})
    return {**DEFAULT_QUALITY, **quality}


def get_scoring_config(config: dict[str, Any]) -> dict[str, Any]:
    """Extract scoring section."""
    return config.get("scoring", {})


def load_scored_repos(path: Path) -> list[dict[str, Any]]:
    """Load scored repos from JSON file."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def week_slug(dt: datetime | None = None) -> str:
    """Return current ISO week slug like '2026-W21'."""
    dt = dt or datetime.now(tz=UTC)
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def check_quality(
    scored_repos: list[dict[str, Any]],
    quality_config: dict[str, Any],
    scoring_config: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate quality thresholds. Returns metric dict."""
    min_repos = quality_config.get("min_repos_per_week", 5)
    max_repos = quality_config.get("max_repos_per_week", 30)
    min_score = scoring_config.get("min_relevance_score", 40)

    # Count repos passing the relevance score threshold
    repos_passing = sum(1 for r in scored_repos if r.get("relevance_score", 0) >= min_score)
    repos_scored = len(scored_repos)

    warnings: list[str] = []
    status = "ok"

    if repos_passing < min_repos:
        status = "below_threshold"
        warnings.append(
            f"Only {repos_passing} repos pass min_relevance_score ({min_score}), "
            f"threshold is {min_repos}."
        )

    if repos_passing > max_repos:
        status = "above_maximum" if status == "ok" else status
        warnings.append(
            f"{repos_passing} repos pass min_relevance_score ({min_score}), "
            f"exceeds max_repos_per_week ({max_repos}). Potential noise."
        )

    return {
        "repos_scored": repos_scored,
        "repos_passing": repos_passing,
        "threshold": min_repos,
        "status": status,
        "warnings": warnings,
    }


def emit_warnings(warnings: list[str]) -> None:
    """Print GitHub Actions warning annotations."""
    for warning in warnings:
        print(f"::warning::{warning}")


def write_metric(topic_id: str, metric: dict[str, Any], week: str) -> Path:
    """Write quality metric JSON to the metrics directory."""
    out_dir = metrics_dir(topic_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"quality-{week}.json"
    out_path = out_dir / filename
    payload = {
        "week": week,
        "topic": topic_id,
        **{k: v for k, v in metric.items() if k != "warnings"},
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out_path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    config = load_config(args.config)
    quality_config = get_quality_config(config)
    scoring_config = get_scoring_config(config)
    topic_id = args.topic or load_topic_id(args.config)

    if args.input:
        scored_repos = load_scored_repos(args.input)
    else:
        # Try to find scored output in analyzed dir
        scored_repos = []
        print("::warning::No --input provided and no scored repos found.", file=sys.stderr)

    metric = check_quality(scored_repos, quality_config, scoring_config)
    week = week_slug()

    emit_warnings(metric["warnings"])
    write_metric(topic_id, metric, week)

    if metric["status"] == "ok":
        print(
            f"✅ Quality gate passed: {metric['repos_passing']}/{metric['repos_scored']} repos meet threshold."
        )
    else:
        print(
            f"⚠️  Quality gate warning: {metric['status']} ({metric['repos_passing']}/{metric['repos_scored']} repos)."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
