#!/usr/bin/env python3
"""Tiered degradation selector.

Determines the appropriate service tier based on estimated cost and
monthly budget consumption, outputting a JSON configuration.
"""

from __future__ import annotations

import argparse
import json
import sys

# Tier definitions
TIERS = {
    "normal": {"model": "claude-sonnet-4", "max_repos": None, "skip_ai": False},
    "budget": {"model": "gpt-5.4-mini", "max_repos": 100, "skip_ai": False},
    "minimal": {"model": "gpt-5-mini", "max_repos": 30, "skip_ai": False},
    "emergency": {"model": None, "max_repos": None, "skip_ai": True},
}

DEFAULT_MONTHLY_BUDGET = 10.00


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select service tier based on budget status.")
    parser.add_argument(
        "--estimated-cost",
        type=float,
        default=0.0,
        help="Estimated cost of the upcoming run in USD.",
    )
    parser.add_argument(
        "--monthly-spent",
        type=float,
        default=0.0,
        help="Total USD spent this month so far.",
    )
    parser.add_argument(
        "--monthly-budget",
        type=float,
        default=DEFAULT_MONTHLY_BUDGET,
        help="Monthly budget cap in USD.",
    )
    return parser.parse_args(argv)


def select_tier(
    estimated_cost: float, monthly_spent: float, monthly_budget: float = DEFAULT_MONTHLY_BUDGET
) -> str:
    """Determine tier based on thresholds."""
    if monthly_spent >= monthly_budget:
        return "emergency"
    if monthly_spent >= 8.00:
        return "minimal"
    if estimated_cost >= 0.50 or monthly_spent >= 5.00:
        return "budget"
    return "normal"


def build_config(tier: str) -> dict:
    """Build output config dict for the given tier."""
    cfg = TIERS[tier].copy()
    cfg["tier"] = tier
    return {
        "tier": cfg["tier"],
        "model": cfg["model"],
        "max_repos": cfg["max_repos"],
        "skip_ai": cfg["skip_ai"],
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    tier = select_tier(args.estimated_cost, args.monthly_spent, args.monthly_budget)
    config = build_config(tier)
    print(json.dumps(config))
    return 0


if __name__ == "__main__":
    sys.exit(main())
