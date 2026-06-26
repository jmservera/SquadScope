#!/usr/bin/env python3
"""Score crawled repositories on topic relevance for SquadScope.

Reads raw crawl JSON, applies scoring criteria from squadscope.topic.yml,
and outputs a ranked list of repos with relevance_score field.

Usage:
    python scripts/score_repos.py [--config squadscope.topic.yml] \
        [--input data/raw/ai-ml/2026-W21.json] [--output scored.json] [--topic ai-ml]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from scripts.topic_paths import load_topic_id, raw_dir


def load_config(config_path: str | Path) -> dict[str, Any]:
    """Load and return the full config from a YAML file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_scoring_config(config: dict[str, Any]) -> dict[str, Any]:
    """Extract scoring section with defaults."""
    defaults = {
        "min_stars": 20,
        "min_stars_gained": 10,
        "max_age_days": 365,
        "min_relevance_score": 40,
        "language_boost": {},
        "topic_relevance": [],
    }
    scoring = config.get("scoring", {})
    return {**defaults, **scoring}


def find_latest_raw_json(topic_id: str | None) -> Path | None:
    """Find the most recent raw JSON file for a topic."""
    directory = raw_dir(topic_id)
    if not directory.exists():
        return None
    json_files = sorted(directory.glob("*.json"), reverse=True)
    return json_files[0] if json_files else None


def score_stars(stars: int) -> float:
    """Score based on star count with diminishing returns (0-25 points)."""
    if stars <= 0:
        return 0.0
    # Log scale: 100 stars ≈ 12.5, 1000 stars ≈ 18.7, 10000 stars ≈ 25
    return min(25.0, 25.0 * math.log10(stars) / math.log10(10000))


def score_stars_gained(stars_gained: int) -> float:
    """Score based on stars gained velocity (0-25 points)."""
    if stars_gained <= 0:
        return 0.0
    # Log scale with faster saturation
    return min(25.0, 25.0 * math.log10(1 + stars_gained) / math.log10(1000))


def score_language(language: str | None, language_boost: dict[str, float]) -> float:
    """Score based on language match (0-15 points)."""
    if not language or not language_boost:
        return 7.5  # neutral score when no language info or no config
    multiplier = language_boost.get(language, 1.0)
    return min(15.0, 7.5 * multiplier)


def score_topics(repo_topics: list[str], topic_relevance: list[str]) -> float:
    """Score based on topic overlap (0-25 points)."""
    if not topic_relevance or not repo_topics:
        return 0.0
    repo_set = set(t.lower() for t in repo_topics)
    relevance_set = set(t.lower() for t in topic_relevance)
    matches = len(repo_set & relevance_set)
    max_possible = min(len(relevance_set), 3)  # cap at 3 matches for full score
    if max_possible == 0:
        return 0.0
    return min(25.0, 25.0 * matches / max_possible)


def score_age(created_at: str | None, max_age_days: int) -> float:
    """Score based on repo age (0-10 points). Newer repos get a boost."""
    if not created_at:
        return 5.0  # neutral when unknown
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return 5.0
    now = datetime.now(UTC)
    age_days = (now - created).days
    if age_days < 0:
        age_days = 0
    if age_days > max_age_days:
        # Penalty for old repos: scale down from 5 to 0
        penalty_ratio = min((age_days - max_age_days) / max_age_days, 1.0)
        return max(0.0, 5.0 * (1.0 - penalty_ratio))
    # Boost for newer repos: 0 days = 10, max_age_days = 5
    freshness = 1.0 - (age_days / max_age_days)
    return 5.0 + 5.0 * freshness


def compute_relevance_score(repo: dict[str, Any], scoring_config: dict[str, Any]) -> float:
    """Compute a 0-100 relevance score for a single repo."""
    stars = repo.get("stars", 0) or 0
    stars_gained = repo.get("stars_gained", 0) or 0
    language = repo.get("language")
    topics = repo.get("topics", []) or []
    created_at = repo.get("created_at")

    s_stars = score_stars(stars)
    s_gained = score_stars_gained(stars_gained)
    s_lang = score_language(language, scoring_config.get("language_boost", {}))
    s_topics = score_topics(topics, scoring_config.get("topic_relevance", []))
    s_age = score_age(created_at, scoring_config.get("max_age_days", 365))

    raw_score = s_stars + s_gained + s_lang + s_topics + s_age
    return round(min(100.0, max(0.0, raw_score)), 1)


def score_repos(
    repos: list[dict[str, Any]], scoring_config: dict[str, Any]
) -> list[dict[str, Any]]:
    """Score and filter a list of repos. Returns sorted list with relevance_score."""
    min_score = scoring_config.get("min_relevance_score", 40)
    scored = []
    for repo in repos:
        score = compute_relevance_score(repo, scoring_config)
        if score >= min_score:
            scored.append({**repo, "relevance_score": score})
    scored.sort(key=lambda r: r["relevance_score"], reverse=True)
    return scored


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score repos on topic relevance")
    parser.add_argument(
        "--config", default="squadscope.topic.yml", help="Path to topic config YAML"
    )
    parser.add_argument("--input", default=None, help="Path to raw crawl JSON file")
    parser.add_argument("--output", default=None, help="Output file path (default: stdout)")
    parser.add_argument("--topic", default=None, help="Topic ID override")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    scoring_config = get_scoring_config(config)

    topic_id = args.topic or load_topic_id(args.config)

    if args.input:
        input_path = Path(args.input)
    else:
        input_path = find_latest_raw_json(topic_id)
        if input_path is None:
            print(f"Error: No raw JSON found for topic '{topic_id}'", file=sys.stderr)
            return 1

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    with open(input_path, encoding="utf-8") as f:
        repos = json.load(f)

    if not isinstance(repos, list):
        print("Error: Input JSON must be a list of repo objects", file=sys.stderr)
        return 1

    scored = score_repos(repos, scoring_config)

    output_json = json.dumps(scored, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json + "\n")
    else:
        print(output_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
