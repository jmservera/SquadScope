#!/usr/bin/env python3
"""Calibrate hype risk scoring using accumulated momentum data.

Reads momentum data from data/metrics/{topic}/momentum-*.json, compares
hype risk predictions vs actual outcomes, and outputs a calibration report
with recommended threshold adjustments.

Usage:
    python scripts/calibrate_hype_risk.py [--topic ai-ml] [--output calibration.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import topic_paths  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calibrate hype risk scoring model"
    )
    parser.add_argument(
        "--topic",
        default=None,
        help="Topic ID for path resolution.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path for calibration report JSON.",
    )
    return parser.parse_args(argv)


def load_momentum_files(metrics_directory: Path) -> list[dict[str, Any]]:
    """Load all momentum-*.json files from a metrics directory."""
    files = sorted(metrics_directory.glob("momentum-*.json"))
    results = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
                results.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return results


def load_hype_risk_files(analyzed_directory: Path) -> list[dict[str, Any]]:
    """Load all *-hype-risk.json or hype risk assessment files."""
    files = sorted(analyzed_directory.glob("*hype*risk*.json"))
    results = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
                results.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return results


def build_actual_outcomes(momentum_data: list[dict[str, Any]]) -> dict[str, str]:
    """Build repo -> actual outcome mapping from momentum data."""
    outcomes: dict[str, str] = {}
    for report in momentum_data:
        for repo in report.get("tracked_repos", []):
            repo_name = repo.get("repo", "")
            classification = repo.get("classification", "")
            if repo_name and classification:
                outcomes[repo_name] = classification
    return outcomes


def build_predictions(
    hype_risk_data: list[dict[str, Any]],
    correlation_data: list[dict[str, Any]] | None = None,
) -> dict[str, str]:
    """Build repo -> predicted risk level mapping from hype risk assessments."""
    predictions: dict[str, str] = {}
    for data in hype_risk_data:
        assessments = data.get("assessments", [])
        for assessment in assessments:
            repo = assessment.get("repo", "")
            risk = assessment.get("hype_risk", "")
            if repo and risk:
                predictions[repo] = risk
    return predictions


def risk_to_expected_outcome(risk: str) -> str | None:
    """Map risk level to expected momentum outcome."""
    if risk in ("high",):
        return "faded"
    if risk in ("low", "very_low"):
        return "sustained"
    return None


def compute_calibration(
    predictions: dict[str, str],
    actuals: dict[str, str],
) -> dict[str, Any]:
    """Compare predictions vs actuals and compute accuracy by category."""
    accuracy_by_category: dict[str, dict[str, int]] = {}
    total_samples = 0

    for repo, risk_level in predictions.items():
        if repo not in actuals:
            continue
        expected = risk_to_expected_outcome(risk_level)
        if expected is None:
            continue

        actual = actuals[repo]
        total_samples += 1

        if risk_level not in accuracy_by_category:
            accuracy_by_category[risk_level] = {"predicted": 0, "correct": 0}

        accuracy_by_category[risk_level]["predicted"] += 1
        if expected == actual:
            accuracy_by_category[risk_level]["correct"] += 1

    for cat in accuracy_by_category.values():
        predicted = cat["predicted"]
        cat["accuracy"] = round(cat["correct"] / predicted, 4) if predicted > 0 else 0.0

    return {
        "samples": total_samples,
        "accuracy_by_category": accuracy_by_category,
    }


def generate_recommendations(
    calibration: dict[str, Any],
    actuals: dict[str, str],
) -> list[dict[str, Any]]:
    """Generate threshold adjustment recommendations based on calibration."""
    recommendations = []
    accuracy_by_cat = calibration.get("accuracy_by_category", {})

    high_stats = accuracy_by_cat.get("high", {})
    if high_stats.get("predicted", 0) > 0:
        high_acc = high_stats.get("accuracy", 0)
        if high_acc < 0.7:
            recommendations.append({
                "parameter": "high_risk_decay_threshold",
                "current": 0.5,
                "recommended": 0.6,
                "reason": (
                    f"High-risk accuracy is {high_acc:.0%}, below 70% target. "
                    "Raise decay threshold to reduce false positives."
                ),
            })

    low_stats = accuracy_by_cat.get("low", {})
    if low_stats.get("predicted", 0) > 0:
        low_acc = low_stats.get("accuracy", 0)
        if low_acc < 0.7:
            recommendations.append({
                "parameter": "sustained_threshold_weeks",
                "current": 2,
                "recommended": 3,
                "reason": (
                    f"Low-risk (sustained) accuracy is {low_acc:.0%}. "
                    "Extend observation window to improve confidence."
                ),
            })

    total_sustained = sum(1 for v in actuals.values() if v == "sustained")
    total_faded = sum(1 for v in actuals.values() if v == "faded")
    if total_sustained + total_faded > 0:
        sustained_ratio = total_sustained / (total_sustained + total_faded)
        if sustained_ratio > 0.7:
            recommendations.append({
                "parameter": "press_correlation_confidence_floor",
                "current": 0.4,
                "recommended": 0.5,
                "reason": (
                    f"Sustained ratio is {sustained_ratio:.0%}, suggesting most "
                    "press-correlated repos maintain growth. Raise confidence "
                    "floor to only flag truly risky repos."
                ),
            })

    if not recommendations:
        recommendations.append({
            "parameter": "no_changes",
            "current": None,
            "recommended": None,
            "reason": "Calibration shows acceptable accuracy. No adjustments needed.",
        })

    return recommendations


def run_calibration(
    topic_id: str | None = None,
    output_path: str | None = None,
) -> dict[str, Any]:
    """Main calibration logic."""
    metrics_directory = topic_paths.metrics_dir(topic_id)
    analyzed_directory = topic_paths.analyzed_dir(topic_id)

    momentum_data = load_momentum_files(metrics_directory)
    if not momentum_data:
        print(f"No momentum data found in {metrics_directory}", file=sys.stderr)
        report = {
            "calibration_date": datetime.now().strftime("%Y-%m-%d"),
            "samples": 0,
            "accuracy_by_category": {},
            "recommended_adjustments": [],
        }
        if output_path:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                f.write("\n")
        return report

    hype_risk_data = load_hype_risk_files(analyzed_directory)

    actuals = build_actual_outcomes(momentum_data)
    predictions = build_predictions(hype_risk_data)

    calibration = compute_calibration(predictions, actuals)
    recommendations = generate_recommendations(calibration, actuals)

    report = {
        "calibration_date": datetime.now().strftime("%Y-%m-%d"),
        "samples": calibration["samples"],
        "accuracy_by_category": calibration["accuracy_by_category"],
        "recommended_adjustments": recommendations,
    }

    if output_path:
        out = Path(output_path)
    else:
        metrics_directory.mkdir(parents=True, exist_ok=True)
        out = metrics_directory / "calibration-report.json"

    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Calibration report: {calibration['samples']} samples")
    for cat, stats in calibration["accuracy_by_category"].items():
        print(f"  [{cat}] {stats['correct']}/{stats['predicted']} ({stats['accuracy']:.0%})")
    print(f"Wrote report to {out}")

    return report


def main(argv: list[str] | None = None) -> dict[str, Any]:
    """CLI entry point."""
    args = parse_args(argv)
    return run_calibration(
        topic_id=args.topic,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
