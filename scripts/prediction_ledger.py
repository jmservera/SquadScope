#!/usr/bin/env python3
"""Generate prediction ledger entries from analyzed summaries and raw data.

Reads an analyzed summary markdown and its corresponding raw JSON to produce
3-5 heuristic predictions about repos likely to gain momentum. Predictions
are appended to a per-topic JSONL file for later validation.

Usage:
    python scripts/prediction_ledger.py [--input FILE] [--topic TOPIC] [--raw FILE]
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from scripts.topic_paths import analyzed_dir, metrics_dir, raw_dir

FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n(.*)\Z", re.DOTALL)
WEEK_PATTERN = re.compile(r"\d{4}-W\d{2}")
REPO_LINK_PATTERN = re.compile(r"\[(?P<full_name>[^\]]+/[^\]]+)\]\(https://github\.com/[^\)]+\)")

PREDICTION_TYPES = [
    "rising_star",
    "emerging_topic",
    "momentum_shift",
    "breakout_candidate",
    "declining_signal",
]

MAX_PREDICTIONS = 5
MIN_PREDICTIONS = 3


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate prediction ledger entries from analyzed summaries."
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Path to analyzed summary markdown (data/analyzed/{topic}/YYYY-WNN-summary.md).",
    )
    parser.add_argument(
        "--topic",
        default=None,
        help="Topic ID for path resolution. Defaults to general.",
    )
    parser.add_argument(
        "--raw",
        default=None,
        help="Path to raw JSON data. Inferred from summary week if not given.",
    )
    return parser.parse_args(argv)


def find_latest_summary(topic_id: str | None) -> Path:
    """Find the most recent analyzed summary for a topic."""
    search = analyzed_dir(topic_id)
    candidates = sorted(search.glob("*-summary.md"))
    if not candidates:
        raise FileNotFoundError(f"No summaries found in {search}")
    return candidates[-1]


def extract_week(text: str) -> str | None:
    """Extract YYYY-WNN week identifier from text."""
    match = WEEK_PATTERN.search(text)
    return match.group(0) if match else None


def infer_raw_path(summary_path: Path, topic_id: str | None) -> Path:
    """Infer the raw JSON path from the summary filename."""
    week = extract_week(summary_path.name)
    if not week:
        raise ValueError(f"Cannot infer week from {summary_path.name}")
    return raw_dir(topic_id) / f"{week}.json"


def parse_summary(content: str) -> dict[str, Any]:
    """Parse an analyzed summary markdown into frontmatter and body."""
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {"frontmatter": {}, "body": content}

    fm_text, body = match.group(1), match.group(2)
    frontmatter: dict[str, Any] = {}
    for line in fm_text.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            value = value.strip().strip('"').strip("'")
            frontmatter[key.strip()] = value
    return {"frontmatter": frontmatter, "body": body}


def extract_repos_from_summary(body: str) -> list[str]:
    """Extract repo full_names mentioned in the summary body."""
    seen: set[str] = set()
    repos: list[str] = []
    for match in REPO_LINK_PATTERN.finditer(body):
        name = match.group("full_name")
        if name not in seen:
            seen.add(name)
            repos.append(name)
    return repos


def load_raw_data(raw_path: Path) -> dict[str, Any]:
    """Load and return raw JSON data."""
    with open(raw_path, encoding="utf-8") as f:
        return json.load(f)


def build_repo_index(raw_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index repos from raw data by full_name for quick lookup."""
    index: dict[str, dict[str, Any]] = {}
    for section in ("new_repos", "trending_repos"):
        for repo in raw_data.get(section, []):
            full_name = repo.get("full_name", "")
            if full_name:
                entry = index.get(full_name, {})
                entry.update(repo)
                entry["_source"] = section
                index[full_name] = entry
    return index


def score_rising_star(repo: dict[str, Any]) -> float:
    """Score a repo for rising_star potential."""
    stars = repo.get("stars", 0)
    is_new = repo.get("_source") == "new_repos"
    # High stars on a new repo is a strong signal
    if is_new and stars >= 1000:
        return min(0.9, 0.5 + (stars / 10000))
    if is_new and stars >= 100:
        return min(0.7, 0.3 + (stars / 5000))
    if stars >= 5000:
        return 0.4
    return 0.2


def score_breakout_candidate(repo: dict[str, Any]) -> float:
    """Score a repo for breakout_candidate potential."""
    stars = repo.get("stars", 0)
    forks = repo.get("forks", 0)
    is_new = repo.get("_source") == "new_repos"
    fork_ratio = forks / max(stars, 1)
    if is_new and fork_ratio > 0.1 and stars >= 50:
        return min(0.8, 0.4 + fork_ratio)
    if stars >= 500 and fork_ratio > 0.15:
        return 0.6
    return 0.2


def score_momentum_shift(repo: dict[str, Any]) -> float:
    """Score a repo for momentum_shift (trending but established)."""
    stars = repo.get("stars", 0)
    is_trending = repo.get("_source") == "trending_repos"
    if is_trending and stars >= 10000:
        return 0.6
    if is_trending and stars >= 1000:
        return 0.5
    return 0.2


def classify_prediction(repo: dict[str, Any]) -> tuple[str, float, str]:
    """Classify a repo into a prediction type with confidence and reason."""
    scores = {
        "rising_star": score_rising_star(repo),
        "breakout_candidate": score_breakout_candidate(repo),
        "momentum_shift": score_momentum_shift(repo),
    }

    best_type = max(scores, key=scores.get)  # type: ignore[arg-type]
    confidence = scores[best_type]

    reasons = {
        "rising_star": f"New repo with {repo.get('stars', 0)} stars and active development",
        "breakout_candidate": (
            f"High fork ratio ({repo.get('forks', 0)} forks / "
            f"{repo.get('stars', 0)} stars) suggests community adoption"
        ),
        "momentum_shift": (f"Established repo ({repo.get('stars', 0)} stars) trending this week"),
    }

    return best_type, round(confidence, 2), reasons[best_type]


def generate_predictions(
    summary_content: str,
    raw_data: dict[str, Any],
    week: str,
) -> list[dict[str, Any]]:
    """Generate 3-5 predictions from analyzed summary and raw data."""
    parsed = parse_summary(summary_content)
    mentioned_repos = extract_repos_from_summary(parsed["body"])
    repo_index = build_repo_index(raw_data)

    predictions: list[dict[str, Any]] = []

    # Score mentioned repos that exist in raw data
    candidates: list[tuple[str, str, float, str]] = []
    for repo_name in mentioned_repos:
        if repo_name in repo_index:
            pred_type, confidence, reason = classify_prediction(repo_index[repo_name])
            candidates.append((repo_name, pred_type, confidence, reason))

    # Sort by confidence descending, take top entries
    candidates.sort(key=lambda x: x[2], reverse=True)

    for repo_name, pred_type, confidence, reason in candidates[:MAX_PREDICTIONS]:
        predictions.append(
            {
                "week": week,
                "repo": repo_name,
                "prediction": pred_type,
                "confidence": confidence,
                "reason": reason,
                "validated": None,
            }
        )

    # If we have fewer than MIN_PREDICTIONS from mentioned repos,
    # supplement from raw data's new_repos
    if len(predictions) < MIN_PREDICTIONS:
        existing = {p["repo"] for p in predictions}
        for repo in raw_data.get("new_repos", []):
            if len(predictions) >= MIN_PREDICTIONS:
                break
            full_name = repo.get("full_name", "")
            if full_name and full_name not in existing:
                pred_type, confidence, reason = classify_prediction(repo)
                if confidence >= 0.3:
                    predictions.append(
                        {
                            "week": week,
                            "repo": full_name,
                            "prediction": pred_type,
                            "confidence": confidence,
                            "reason": reason,
                            "validated": None,
                        }
                    )
                    existing.add(full_name)

    return predictions[:MAX_PREDICTIONS]


def append_predictions(predictions: list[dict[str, Any]], output_path: Path) -> None:
    """Append predictions to a JSONL file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "a", encoding="utf-8") as f:
        for pred in predictions:
            f.write(json.dumps(pred, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> list[dict[str, Any]]:
    """Main entry point. Returns the generated predictions."""
    args = parse_args(argv)
    topic_id = args.topic

    # Resolve input summary
    if args.input:
        summary_path = Path(args.input)
    else:
        summary_path = find_latest_summary(topic_id)

    # Read summary
    summary_content = summary_path.read_text(encoding="utf-8")

    # Resolve raw data path
    if args.raw:
        raw_path = Path(args.raw)
    else:
        raw_path = infer_raw_path(summary_path, topic_id)

    raw_data = load_raw_data(raw_path)

    # Determine week
    week = extract_week(summary_path.name) or raw_data.get("week", "unknown")

    # Generate predictions
    predictions = generate_predictions(summary_content, raw_data, week)

    # Write output
    output_path = metrics_dir(topic_id) / "predictions.jsonl"
    append_predictions(predictions, output_path)

    # Print summary
    print(f"Generated {len(predictions)} predictions for {week}")
    for p in predictions:
        print(f"  [{p['prediction']}] {p['repo']} (confidence: {p['confidence']})")

    return predictions


if __name__ == "__main__":
    main()
