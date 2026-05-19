#!/usr/bin/env python3
"""Budget alerts for GitHub Actions CI.

Evaluates current run cost and monthly cumulative spend against thresholds,
emitting GitHub Actions annotations (::warning:: / ::error::) as appropriate.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_METRICS = ROOT / "data" / "metrics" / "token-usage.jsonl"

# Thresholds
SINGLE_RUN_WARNING = 0.50
SINGLE_RUN_FAIL = 1.00
MONTHLY_WARNING = 5.00
MONTHLY_RECOMMEND_SWITCH = 10.00


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Budget alerts for CI cost control.")
    parser.add_argument(
        "--run-cost",
        type=float,
        default=None,
        help="Cost of the current run in USD.",
    )
    parser.add_argument(
        "--metrics",
        type=Path,
        default=DEFAULT_METRICS,
        help="Path to token-usage.jsonl ledger.",
    )
    return parser.parse_args(argv)


def load_monthly_spend(metrics_path: Path, now: datetime | None = None) -> float:
    """Sum estimated_cost for entries in the current month."""
    if not metrics_path.exists():
        return 0.0
    now = now or datetime.now(UTC)
    total = 0.0
    for line in metrics_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = entry.get("timestamp", "")
        try:
            entry_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            continue
        if entry_dt.year == now.year and entry_dt.month == now.month:
            total += entry.get("estimated_cost", 0.0)
    return total


def evaluate(run_cost: float | None, monthly_spent: float) -> tuple[list[str], int]:
    """Return (annotations, exit_code)."""
    annotations: list[str] = []
    exit_code = 0

    if run_cost is not None:
        if run_cost > SINGLE_RUN_FAIL:
            annotations.append(
                f"::error::Single run cost ${run_cost:.2f} exceeds hard cap ${SINGLE_RUN_FAIL:.2f}"
            )
            exit_code = 1
        elif run_cost > SINGLE_RUN_WARNING:
            annotations.append(
                f"::warning::Single run cost ${run_cost:.2f} exceeds warning threshold ${SINGLE_RUN_WARNING:.2f}"
            )

    if monthly_spent > MONTHLY_RECOMMEND_SWITCH:
        annotations.append(
            f"::warning::Monthly spend ${monthly_spent:.2f} exceeds ${MONTHLY_RECOMMEND_SWITCH:.2f} — consider switching to a cheaper model"
        )
    elif monthly_spent > MONTHLY_WARNING:
        annotations.append(
            f"::warning::Monthly cumulative spend ${monthly_spent:.2f} exceeds ${MONTHLY_WARNING:.2f}"
        )

    return annotations, exit_code


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    monthly_spent = load_monthly_spend(args.metrics)
    if args.run_cost is not None:
        monthly_spent += args.run_cost
    annotations, exit_code = evaluate(args.run_cost, monthly_spent)
    for ann in annotations:
        print(ann)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
