#!/usr/bin/env python3
"""Validate predictions from N weeks ago against actual outcomes.

Reads predictions.jsonl, finds unvalidated predictions older than --weeks-ago,
checks whether predicted outcomes occurred by comparing raw data from the
prediction week against subsequent weeks, and writes a scorecard summary.

Usage:
    python scripts/hindsight_validation.py [--topic ai-ml] [--weeks-ago 4] [--data-dir data/]
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from scripts.topic_paths import metrics_dir, raw_dir


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate predictions against actual outcomes."
    )
    parser.add_argument(
        "--topic",
        default=None,
        help="Topic ID for path resolution. Defaults to general.",
    )
    parser.add_argument(
        "--weeks-ago",
        type=int,
        default=4,
        help="Minimum age in weeks for predictions to validate (default: 4).",
    )
    parser.add_argument(
        "--data-dir",
        default="data/",
        help="Base data directory (default: data/).",
    )
    return parser.parse_args(argv)


def iso_week_to_date(week_str: str) -> datetime:
    """Convert YYYY-WNN to a datetime (Monday of that week)."""
    year, week_num = week_str.split("-W")
    return datetime.strptime(f"{year}-W{int(week_num):02d}-1", "%G-W%V-%u")


def current_iso_week() -> str:
    """Return the current ISO week as YYYY-WNN."""
    now = datetime.now()
    cal = now.isocalendar()
    return f"{cal[0]}-W{cal[1]:02d}"


def week_offset(week_str: str, offset: int) -> str:
    """Return a week string offset by N weeks."""
    dt = iso_week_to_date(week_str)
    new_dt = dt + timedelta(weeks=offset)
    cal = new_dt.isocalendar()
    return f"{cal[0]}-W{cal[1]:02d}"


def load_predictions(path: Path) -> list[dict[str, Any]]:
    """Load predictions from a JSONL file."""
    if not path.exists():
        return []
    predictions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                predictions.append(json.loads(line))
    return predictions


def save_predictions(predictions: list[dict[str, Any]], path: Path) -> None:
    """Write predictions back to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for pred in predictions:
            f.write(json.dumps(pred, ensure_ascii=False) + "\n")


def load_raw_week(raw_directory: Path, week_str: str) -> dict[str, Any] | None:
    """Load raw JSON for a given week. Returns None if missing."""
    path = raw_directory / f"{week_str}.json"
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def build_repo_stars(raw_data: dict[str, Any]) -> dict[str, int]:
    """Extract repo -> stars mapping from raw data."""
    stars: dict[str, int] = {}
    for section in ("new_repos", "trending_repos"):
        for repo in raw_data.get(section, []):
            name = repo.get("full_name", "")
            if name:
                stars[name] = repo.get("stars", 0)
    return stars


def build_repo_set(raw_data: dict[str, Any]) -> set[str]:
    """Extract the set of repo names present in raw data."""
    repos: set[str] = set()
    for section in ("new_repos", "trending_repos"):
        for repo in raw_data.get(section, []):
            name = repo.get("full_name", "")
            if name:
                repos.add(name)
    return repos


def validate_rising_star(
    repo: str,
    prediction_stars: int,
    raw_directory: Path,
    prediction_week: str,
    weeks_ahead: int,
) -> bool | None:
    """Validate rising_star: stars grew 20%+ in subsequent weeks."""
    for i in range(weeks_ahead, 0, -1):
        w = week_offset(prediction_week, i)
        raw_data = load_raw_week(raw_directory, w)
        if raw_data is None:
            continue
        current_stars = build_repo_stars(raw_data).get(repo)
        if current_stars is not None:
            if prediction_stars == 0:
                return current_stars > 0
            growth = (current_stars - prediction_stars) / prediction_stars
            return growth >= 0.20
    return None


def validate_breakout_candidate(
    repo: str,
    raw_directory: Path,
    prediction_week: str,
    weeks_ahead: int,
) -> bool | None:
    """Validate breakout_candidate: appeared in trending in subsequent weeks."""
    for i in range(1, weeks_ahead + 1):
        w = week_offset(prediction_week, i)
        raw_data = load_raw_week(raw_directory, w)
        if raw_data is None:
            continue
        trending = {
            r.get("full_name", "")
            for r in raw_data.get("trending_repos", [])
        }
        if repo in trending:
            return True
    return False


def validate_momentum_shift(
    repo: str,
    prediction_stars: int,
    raw_directory: Path,
    prediction_week: str,
    weeks_ahead: int,
) -> bool | None:
    """Validate momentum_shift: trend continued in same direction."""
    star_history = [prediction_stars]
    for i in range(1, weeks_ahead + 1):
        w = week_offset(prediction_week, i)
        raw_data = load_raw_week(raw_directory, w)
        if raw_data is None:
            continue
        s = build_repo_stars(raw_data).get(repo)
        if s is not None:
            star_history.append(s)

    if len(star_history) < 2:
        return None
    return star_history[-1] >= star_history[0]


def validate_declining_signal(
    repo: str,
    raw_directory: Path,
    prediction_week: str,
    weeks_ahead: int,
) -> bool | None:
    """Validate declining_signal: repo disappeared from subsequent crawls."""
    found_count = 0
    checked_count = 0
    for i in range(1, weeks_ahead + 1):
        w = week_offset(prediction_week, i)
        raw_data = load_raw_week(raw_directory, w)
        if raw_data is None:
            continue
        checked_count += 1
        if repo in build_repo_set(raw_data):
            found_count += 1

    if checked_count == 0:
        return None
    return found_count <= checked_count // 2


def validate_prediction(
    prediction: dict[str, Any],
    raw_directory: Path,
    weeks_ahead: int,
) -> bool | None:
    """Validate a single prediction. Returns True/False or None if insufficient data."""
    repo = prediction.get("repo", "")
    prediction_week = prediction.get("week", "")
    pred_type = prediction.get("prediction", "")

    if not repo or not prediction_week:
        return None

    pred_raw = load_raw_week(raw_directory, prediction_week)
    prediction_stars = 0
    if pred_raw:
        prediction_stars = build_repo_stars(pred_raw).get(repo, 0)

    if pred_type == "rising_star":
        return validate_rising_star(
            repo, prediction_stars, raw_directory, prediction_week, weeks_ahead
        )
    elif pred_type == "breakout_candidate":
        return validate_breakout_candidate(
            repo, raw_directory, prediction_week, weeks_ahead
        )
    elif pred_type == "momentum_shift":
        return validate_momentum_shift(
            repo, prediction_stars, raw_directory, prediction_week, weeks_ahead
        )
    elif pred_type in ("declining_signal", "emerging_topic"):
        return validate_declining_signal(
            repo, raw_directory, prediction_week, weeks_ahead
        )
    return None


def is_old_enough(prediction_week: str, weeks_ago: int) -> bool:
    """Check if a prediction is at least weeks_ago weeks old."""
    try:
        pred_date = iso_week_to_date(prediction_week)
        cutoff = datetime.now() - timedelta(weeks=weeks_ago)
        return pred_date <= cutoff
    except (ValueError, AttributeError):
        return False


def generate_scorecard(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate a scorecard summary from validated predictions."""
    validated = [p for p in predictions if p.get("validated") is not None]
    correct = [p for p in validated if p.get("validated") is True]

    by_type: dict[str, dict[str, int]] = {}
    for p in validated:
        t = p.get("prediction", "unknown")
        if t not in by_type:
            by_type[t] = {"total": 0, "correct": 0}
        by_type[t]["total"] += 1
        if p.get("validated") is True:
            by_type[t]["correct"] += 1

    total = len(validated)
    accuracy = round(len(correct) / total, 4) if total > 0 else 0.0

    return {
        "total_validated": total,
        "correct": len(correct),
        "incorrect": total - len(correct),
        "accuracy": accuracy,
        "by_type": {
            k: {
                **v,
                "accuracy": round(v["correct"] / v["total"], 4) if v["total"] > 0 else 0.0,
            }
            for k, v in by_type.items()
        },
    }


def save_scorecard(scorecard: dict[str, Any], metrics_directory: Path) -> Path:
    """Save scorecard to data/metrics/{topic}/scorecards/YYYY-WNN-scorecard.json."""
    week = current_iso_week()
    scorecards_dir = metrics_directory / "scorecards"
    scorecards_dir.mkdir(parents=True, exist_ok=True)
    path = scorecards_dir / f"{week}-scorecard.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(scorecard, f, indent=2, ensure_ascii=False)
    return path


def run_validation(
    topic_id: str | None = None,
    weeks_ago: int = 4,
    data_dir: str = "data/",
) -> dict[str, Any]:
    """Main validation logic. Returns the scorecard."""
    import scripts.topic_paths as tp

    original_root = tp.DATA_ROOT
    tp.DATA_ROOT = Path(data_dir)

    try:
        mdir = metrics_dir(topic_id)
        rdir = raw_dir(topic_id)

        predictions_path = mdir / "predictions.jsonl"
        predictions = load_predictions(predictions_path)

        if not predictions:
            scorecard = generate_scorecard([])
            save_scorecard(scorecard, mdir)
            return scorecard

        validated_count = 0
        for pred in predictions:
            if pred.get("validated") is not None:
                continue
            pred_week = pred.get("week", "")
            if not pred_week or not is_old_enough(pred_week, weeks_ago):
                continue

            result = validate_prediction(pred, rdir, weeks_ago)
            if result is not None:
                pred["validated"] = result
                validated_count += 1

        save_predictions(predictions, predictions_path)

        scorecard = generate_scorecard(predictions)
        scorecard_path = save_scorecard(scorecard, mdir)

        print(f"Validated {validated_count} predictions")
        print(f"Overall accuracy: {scorecard['accuracy']:.1%}")
        print(f"  Correct: {scorecard['correct']}")
        print(f"  Incorrect: {scorecard['incorrect']}")
        for ptype, stats in scorecard.get("by_type", {}).items():
            print(f"  [{ptype}] {stats['correct']}/{stats['total']} ({stats['accuracy']:.1%})")
        print(f"Scorecard saved to {scorecard_path}")

        return scorecard
    finally:
        tp.DATA_ROOT = original_root


def main(argv: list[str] | None = None) -> dict[str, Any]:
    """CLI entry point."""
    args = parse_args(argv)
    return run_validation(
        topic_id=args.topic,
        weeks_ago=args.weeks_ago,
        data_dir=args.data_dir,
    )


if __name__ == "__main__":
    main()
