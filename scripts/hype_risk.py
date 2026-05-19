#!/usr/bin/env python3
"""Hype risk scoring model for SquadScope.

Classifies repos based on the relationship between press coverage
and GitHub activity patterns.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import topic_paths  # noqa: E402


# Risk level definitions
RISK_LEVELS = {
    "very_low": "Organic growth",
    "low": "Press-validated, community-sustained",
    "medium": "Announced but unbuilt",
    "high": "Press-driven hype, fading",
    "none": "No press signal",
}


def classify_repo(
    repo_name: str,
    press_correlated: bool,
    current_stars: int | None = None,
    current_stars_gained: int | None = None,
    previous_stars: int | None = None,
    previous_stars_gained: int | None = None,
) -> dict:
    """Classify a single repo's hype risk.

    Returns an assessment dict with risk level, label, confidence, and reasoning.
    """
    if not press_correlated:
        return _assessment(
            repo_name,
            risk="none",
            press_correlated=False,
            stars_trend="unknown",
            confidence=0.9,
            reasoning="No press correlation detected",
        )

    # Press correlated but no previous data
    if previous_stars is None or previous_stars_gained is None:
        return _assessment(
            repo_name,
            risk="medium",
            press_correlated=True,
            stars_trend="unknown",
            confidence=0.4,
            reasoning="Press correlated but insufficient historical data to assess sustainability",
        )

    # Press correlated with previous data available
    current_gained = current_stars_gained or 0
    previous_gained = previous_stars_gained or 0

    # Check decay first: previous spike much larger than current → fading
    if previous_gained > 0 and current_gained < previous_gained * 0.5:
        return _assessment(
            repo_name,
            risk="high",
            press_correlated=True,
            stars_trend="decaying",
            confidence=0.7,
            reasoning=(
                f"Stars spiked after press but are fading "
                f"(previous: +{previous_gained}, current: +{current_gained})"
            ),
        )

    # Check if stars were already growing before press (organic)
    if previous_gained > 0 and current_gained > 0:
        if previous_gained >= current_gained * 0.5:
            # Growth was already happening before press
            return _assessment(
                repo_name,
                risk="very_low",
                press_correlated=True,
                stars_trend="organic",
                confidence=0.8,
                reasoning=(
                    f"Stars were already growing before press coverage "
                    f"(previous: +{previous_gained}, current: +{current_gained})"
                ),
            )

    # Stars spiked after article - check sustainability
    if current_gained > 0 and previous_gained >= 0:
        total_recent_gain = current_gained + previous_gained
        if total_recent_gain > 0 and current_gained > total_recent_gain * 0.5:
            # Current week still has significant growth - sustained
            return _assessment(
                repo_name,
                risk="low",
                press_correlated=True,
                stars_trend="sustained",
                confidence=0.75,
                reasoning=(
                    f"Stars grew after press coverage and maintained "
                    f"(+{current_gained} this week, +{previous_gained} previous)"
                ),
            )

    # Fallback: press correlated but no clear activity spike
    return _assessment(
        repo_name,
        risk="medium",
        press_correlated=True,
        stars_trend="flat",
        confidence=0.5,
        reasoning="Press coverage detected but no significant GitHub activity spike",
    )


def _assessment(
    repo: str,
    risk: str,
    press_correlated: bool,
    stars_trend: str,
    confidence: float,
    reasoning: str,
) -> dict:
    return {
        "repo": repo,
        "hype_risk": risk,
        "label": RISK_LEVELS[risk],
        "press_correlated": press_correlated,
        "stars_trend": stars_trend,
        "confidence": confidence,
        "reasoning": reasoning,
    }


def _find_repo_in_raw(raw_repos: list[dict], repo_name: str) -> dict | None:
    """Find a repo entry in raw data by name."""
    for repo in raw_repos:
        name = repo.get("full_name") or repo.get("repo") or repo.get("name", "")
        if name == repo_name:
            return repo
    return None


def score_hype_risk(
    correlations: dict,
    raw_data: dict | list | None = None,
    previous_data: dict | list | None = None,
) -> list[dict]:
    """Score hype risk for all repos in correlations data.

    Args:
        correlations: Correlation analysis output with correlated repos.
        raw_data: Current week raw GitHub data.
        previous_data: Previous week raw GitHub data.

    Returns:
        List of assessment dicts.
    """
    # Extract correlated repos
    correlated_repos = set()
    corr_entries = correlations.get("correlations", correlations.get("repos", []))
    if isinstance(corr_entries, list):
        for entry in corr_entries:
            repo_name = entry.get("repo") or entry.get("full_name", "")
            if entry.get("press_correlated", False):
                correlated_repos.add(repo_name)

    # Normalize raw data to lists
    raw_repos = _normalize_raw(raw_data)
    prev_repos = _normalize_raw(previous_data)

    # Collect all repo names from raw data
    all_repos = set()
    for repo in raw_repos:
        name = repo.get("full_name") or repo.get("repo") or repo.get("name", "")
        if name:
            all_repos.add(name)
    # Also include correlated repos even if not in current raw
    all_repos.update(correlated_repos)

    assessments = []
    for repo_name in sorted(all_repos):
        press_correlated = repo_name in correlated_repos

        current = _find_repo_in_raw(raw_repos, repo_name)
        previous = _find_repo_in_raw(prev_repos, repo_name)

        current_stars = current.get("stars") if current else None
        current_gained = current.get("stars_gained") if current else None
        prev_stars = previous.get("stars") if previous else None
        prev_gained = previous.get("stars_gained") if previous else None

        assessment = classify_repo(
            repo_name,
            press_correlated=press_correlated,
            current_stars=current_stars,
            current_stars_gained=current_gained,
            previous_stars=prev_stars,
            previous_stars_gained=prev_gained,
        )
        assessments.append(assessment)

    return assessments


def _normalize_raw(data: dict | list | None) -> list[dict]:
    """Normalize raw data to a list of repo dicts."""
    if data is None:
        return []
    if isinstance(data, list):
        return data
    # Could be wrapped in a dict with 'repos' or 'repositories' key
    if isinstance(data, dict):
        for key in ("repos", "repositories", "items"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return []
    return []


def extract_week(filepath: str | Path | None) -> str:
    """Try to extract week identifier from a filepath like 2026-W21.json."""
    if filepath is None:
        return "unknown"
    name = Path(filepath).stem
    # Remove suffixes like -correlations, -hype-risk
    for suffix in ("-correlations", "-hype-risk", "-metrics"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Hype risk scoring model")
    parser.add_argument(
        "--correlations",
        help="Path to correlations JSON file",
    )
    parser.add_argument(
        "--raw",
        help="Path to current week raw data JSON",
    )
    parser.add_argument(
        "--previous",
        help="Path to previous week raw data JSON",
    )
    parser.add_argument(
        "--output",
        help="Output path for hype risk JSON",
    )
    parser.add_argument(
        "--topic",
        help="Topic ID for path resolution",
    )
    args = parser.parse_args(argv)

    # Resolve paths
    topic = args.topic
    corr_path = Path(args.correlations) if args.correlations else None
    raw_path = Path(args.raw) if args.raw else None
    prev_path = Path(args.previous) if args.previous else None
    out_path = Path(args.output) if args.output else None

    if corr_path is None:
        print("Error: --correlations is required", file=sys.stderr)
        sys.exit(1)

    # Load data
    with open(corr_path, encoding="utf-8") as f:
        correlations = json.load(f)

    raw_data = None
    if raw_path and raw_path.exists():
        with open(raw_path, encoding="utf-8") as f:
            raw_data = json.load(f)

    previous_data = None
    if prev_path and prev_path.exists():
        with open(prev_path, encoding="utf-8") as f:
            previous_data = json.load(f)

    # Score
    assessments = score_hype_risk(correlations, raw_data, previous_data)

    # Build output
    week = extract_week(args.raw or args.correlations)
    output = {
        "week": week,
        "assessments": assessments,
    }

    # Write or print
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        print(f"Wrote {len(assessments)} assessments to {out_path}")
    else:
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
