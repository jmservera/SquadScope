#!/usr/bin/env python3
"""Load and summarize prediction scorecards for reskill integration.

Reads scorecard JSON files from data/metrics/{topic}/scorecards/ and produces
a markdown summary suitable for injection into reskill prompts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.topic_paths import metrics_dir

DEFAULT_SCORECARD_COUNT = 4


def scorecard_dir(topic_id: str | None = None) -> Path:
    """Return the scorecards directory for a given topic."""
    return metrics_dir(topic_id) / "scorecards"


def load_scorecards(topic_id: str | None = None, count: int = DEFAULT_SCORECARD_COUNT) -> list[dict[str, Any]]:
    """Load the most recent N scorecards for a topic, sorted oldest-first."""
    directory = scorecard_dir(topic_id)
    if not directory.exists():
        return []
    files = sorted(directory.glob("*-scorecard.json"))
    if count > 0:
        files = files[-count:]
    cards: list[dict[str, Any]] = []
    for path in files:
        try:
            with open(path, encoding="utf-8") as f:
                cards.append(json.load(f))
        except (json.JSONDecodeError, OSError):
            continue
    return cards


def _aggregate_stats(cards: list[dict[str, Any]]) -> tuple[int, int, int, dict[str, dict[str, int]]]:
    """Aggregate totals across multiple scorecards.

    Returns (total_validated, total_correct, total_incorrect, by_type).
    """
    total_validated = 0
    total_correct = 0
    total_incorrect = 0
    by_type: dict[str, dict[str, int]] = {}

    for card in cards:
        total_validated += card.get("validated", 0)
        total_correct += card.get("correct", 0)
        total_incorrect += card.get("incorrect", 0)
        for pred_type, stats in card.get("by_type", {}).items():
            if pred_type not in by_type:
                by_type[pred_type] = {"total": 0, "correct": 0}
            by_type[pred_type]["total"] += stats.get("total", 0)
            by_type[pred_type]["correct"] += stats.get("correct", 0)

    return total_validated, total_correct, total_incorrect, by_type


def _format_by_type_analysis(by_type: dict[str, dict[str, int]]) -> list[str]:
    """Produce per-type accuracy lines for the summary."""
    lines: list[str] = []
    for pred_type, stats in sorted(by_type.items()):
        total = stats["total"]
        correct = stats["correct"]
        if total == 0:
            continue
        accuracy = correct / total
        pct = int(round(accuracy * 100))
        lines.append(f"- \"{pred_type}\" predictions: {pct}% accurate ({correct}/{total})")
    return lines


def _format_recommendations(by_type: dict[str, dict[str, int]], overall_accuracy: float) -> list[str]:
    """Generate adjustment recommendations based on type performance."""
    recs: list[str] = []
    for pred_type, stats in sorted(by_type.items()):
        total = stats["total"]
        correct = stats["correct"]
        if total == 0:
            continue
        accuracy = correct / total
        if accuracy < 0.5:
            recs.append(
                f"- \"{pred_type}\" predictions are underperforming ({int(round(accuracy * 100))}%) "
                f"— raise confidence threshold or require additional signals"
            )
        elif accuracy >= 0.8:
            recs.append(
                f"- \"{pred_type}\" predictions are strong ({int(round(accuracy * 100))}%) "
                f"— current heuristics are reliable"
            )
    if not recs:
        if overall_accuracy < 0.6:
            recs.append("- Overall accuracy is low — review signal weighting across all prediction types")
        else:
            recs.append("- No specific type-level adjustments needed at this time")
    return recs


def format_scorecard_summary(cards: list[dict[str, Any]]) -> str:
    """Format loaded scorecards into a markdown summary section.

    Returns empty string if cards is empty.
    """
    if not cards:
        return ""

    total_validated, total_correct, total_incorrect, by_type = _aggregate_stats(cards)

    if total_validated == 0:
        return ""

    overall_accuracy = total_correct / total_validated if total_validated else 0.0
    pct = int(round(overall_accuracy * 100))
    weeks = len(cards)
    week_range = f"last {weeks} week{'s' if weeks != 1 else ''}"

    lines: list[str] = []
    lines.append(f"## Prediction Performance ({week_range})")
    lines.append(f"Overall accuracy: {pct}% ({total_correct}/{total_validated} correct)")
    lines.append("")
    lines.append("### Per-Type Accuracy:")
    lines.extend(_format_by_type_analysis(by_type))
    lines.append("")
    lines.append("### Recommended Adjustments:")
    lines.extend(_format_recommendations(by_type, overall_accuracy))

    return "\n".join(lines)


def render_scorecard_section(topic_id: str | None = None, count: int = DEFAULT_SCORECARD_COUNT) -> str:
    """Load scorecards and return formatted summary, or empty string if none exist."""
    cards = load_scorecards(topic_id, count)
    return format_scorecard_summary(cards)
