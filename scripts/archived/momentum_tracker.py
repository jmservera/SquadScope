#!/usr/bin/env python3
"""Track press-correlated repo momentum over time.

Reads correlation data to find press-correlated repos, checks their star
trajectory at week +2 and +4, and classifies growth as "sustained" or "faded".

Usage:
    python scripts/momentum_tracker.py [--topic ai-ml] [--week 2026-W21] [--lag 4]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from scripts import topic_paths


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Track press-correlated repo momentum"
    )
    parser.add_argument(
        "--topic",
        default=None,
        help="Topic ID for path resolution (default: from config or general).",
    )
    parser.add_argument(
        "--week",
        default=None,
        help="Base week to track from (YYYY-WNN). Defaults to current ISO week.",
    )
    parser.add_argument(
        "--lag",
        type=int,
        default=4,
        help="Maximum lag in weeks to check trajectory (default: 4).",
    )
    return parser.parse_args(argv)


def current_iso_week() -> str:
    """Return the current ISO week as YYYY-WNN."""
    now = datetime.now()
    cal = now.isocalendar()
    return f"{cal[0]}-W{cal[1]:02d}"


def iso_week_to_date(week_str: str) -> datetime:
    """Convert YYYY-WNN to a datetime (Monday of that week)."""
    year, week_num = week_str.split("-W")
    return datetime.strptime(f"{year}-W{int(week_num):02d}-1", "%G-W%V-%u")


def week_offset(week_str: str, offset: int) -> str:
    """Return a week string offset by N weeks."""
    dt = iso_week_to_date(week_str)
    new_dt = dt + timedelta(weeks=offset)
    cal = new_dt.isocalendar()
    return f"{cal[0]}-W{cal[1]:02d}"


def load_json_safe(path: Path) -> dict[str, Any] | None:
    """Load JSON file, returning None on missing or invalid."""
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def find_correlation_file(analyzed_dir: Path, week: str) -> Path | None:
    """Find correlation file for a given week."""
    path = analyzed_dir / f"{week}-correlations.json"
    if path.exists():
        return path
    matches = sorted(analyzed_dir.glob(f"{week}*correlation*.json"))
    return matches[0] if matches else None


def extract_correlated_repos(correlations: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract press-correlated repos from correlation data."""
    repos = []
    entries = correlations.get("correlations", [])
    for entry in entries:
        if entry.get("press_correlated", False):
            repos.append(entry)
    return repos


def get_repo_stars_gained(raw_data: dict[str, Any] | None, repo_name: str) -> int | None:
    """Extract stars_gained for a repo from raw week data."""
    if raw_data is None:
        return None
    for key in ("repos", "repositories", "new_repos", "trending_repos"):
        for repo in raw_data.get(key, []):
            name = repo.get("full_name") or repo.get("repo") or repo.get("name", "")
            if name == repo_name:
                return repo.get("stars_gained")
    if isinstance(raw_data, list):
        for repo in raw_data:
            name = repo.get("full_name") or repo.get("repo") or repo.get("name", "")
            if name == repo_name:
                return repo.get("stars_gained")
    return None


def compute_decay_rate(initial: int, current: int) -> float:
    """Compute decay rate: 1 - (current / initial). Clamped to [0, 1]."""
    if initial <= 0:
        return 0.0
    rate = 1.0 - (current / initial)
    return round(max(0.0, min(1.0, rate)), 4)


def classify_momentum(
    initial_gained: int,
    week2_gained: int | None,
    week4_gained: int | None,
    lag: int,
) -> str:
    """Classify as 'sustained' or 'faded' based on trajectory."""
    if initial_gained <= 0:
        return "faded"

    check_gained = None
    if lag >= 4 and week4_gained is not None:
        check_gained = week4_gained
    elif week2_gained is not None:
        check_gained = week2_gained

    if check_gained is None:
        return "faded"

    if check_gained >= initial_gained * 0.2:
        return "sustained"
    return "faded"


def track_repo_momentum(
    repo_name: str,
    initial_gained: int,
    raw_dir: Path,
    base_week: str,
    lag: int,
) -> dict[str, Any]:
    """Track a single repo's momentum over time."""
    w2 = week_offset(base_week, 2)
    w2_data = load_json_safe(raw_dir / f"{w2}.json")
    week2_gained = get_repo_stars_gained(w2_data, repo_name)

    w4 = week_offset(base_week, 4)
    w4_data = load_json_safe(raw_dir / f"{w4}.json")
    week4_gained = get_repo_stars_gained(w4_data, repo_name)

    classification = classify_momentum(initial_gained, week2_gained, week4_gained, lag)

    best_later = week4_gained if (lag >= 4 and week4_gained is not None) else week2_gained
    decay_rate = compute_decay_rate(initial_gained, best_later or 0) if initial_gained > 0 else 0.0

    return {
        "repo": repo_name,
        "initial_stars_gained": initial_gained,
        "week2_stars_gained": week2_gained,
        "week4_stars_gained": week4_gained,
        "classification": classification,
        "decay_rate": decay_rate,
    }


def update_predictions_validated(
    predictions_path: Path,
    tracked_repos: list[dict[str, Any]],
) -> int:
    """Update predictions.jsonl with momentum validation results."""
    if not predictions_path.exists():
        return 0

    predictions = []
    with open(predictions_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                predictions.append(json.loads(line))

    if not predictions:
        return 0

    repo_results = {r["repo"]: r["classification"] for r in tracked_repos}

    updated = 0
    for pred in predictions:
        if pred.get("validated") is not None:
            continue
        repo = pred.get("repo", "")
        if repo in repo_results:
            pred["validated"] = repo_results[repo] == "sustained"
            updated += 1

    if updated > 0:
        with open(predictions_path, "w", encoding="utf-8") as f:
            for pred in predictions:
                f.write(json.dumps(pred, ensure_ascii=False) + "\n")

    return updated


def run_momentum_tracking(
    topic_id: str | None = None,
    week: str | None = None,
    lag: int = 4,
) -> dict[str, Any]:
    """Main tracking logic. Returns momentum report."""
    base_week = week or current_iso_week()
    raw_directory = topic_paths.raw_dir(topic_id)
    analyzed_directory = topic_paths.analyzed_dir(topic_id)
    metrics_directory = topic_paths.metrics_dir(topic_id)

    corr_file = find_correlation_file(analyzed_directory, base_week)
    if corr_file is None:
        print(f"No correlation data for week {base_week} in {analyzed_directory}", file=sys.stderr)
        return {"week": base_week, "tracked_repos": [], "summary": {"total": 0, "sustained": 0, "faded": 0}}

    correlations = load_json_safe(corr_file)
    if correlations is None:
        print(f"Failed to load {corr_file}", file=sys.stderr)
        return {"week": base_week, "tracked_repos": [], "summary": {"total": 0, "sustained": 0, "faded": 0}}

    correlated = extract_correlated_repos(correlations)
    if not correlated:
        print(f"No press-correlated repos found for {base_week}", file=sys.stderr)
        return {"week": base_week, "tracked_repos": [], "summary": {"total": 0, "sustained": 0, "faded": 0}}

    base_raw = load_json_safe(raw_directory / f"{base_week}.json")

    tracked_repos = []
    for entry in correlated:
        repo_name = entry.get("repo", "")
        if not repo_name:
            continue

        initial_gained = get_repo_stars_gained(base_raw, repo_name)
        if initial_gained is None:
            initial_gained = entry.get("stars_gained", 0) or 0

        result = track_repo_momentum(repo_name, initial_gained, raw_directory, base_week, lag)
        tracked_repos.append(result)

    sustained = sum(1 for r in tracked_repos if r["classification"] == "sustained")
    faded = sum(1 for r in tracked_repos if r["classification"] == "faded")

    report = {
        "week": base_week,
        "tracked_repos": tracked_repos,
        "summary": {
            "total": len(tracked_repos),
            "sustained": sustained,
            "faded": faded,
        },
    }

    metrics_directory.mkdir(parents=True, exist_ok=True)
    output_path = metrics_directory / f"momentum-{base_week}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote momentum report to {output_path}")

    predictions_path = metrics_directory / "predictions.jsonl"
    updated = update_predictions_validated(predictions_path, tracked_repos)
    if updated:
        print(f"Updated {updated} predictions in {predictions_path}")

    return report


def main(argv: list[str] | None = None) -> dict[str, Any]:
    """CLI entry point."""
    args = parse_args(argv)
    return run_momentum_tracking(
        topic_id=args.topic,
        week=args.week,
        lag=args.lag,
    )


if __name__ == "__main__":
    main()
