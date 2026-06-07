#!/usr/bin/env python3
"""Pre-flight cost estimation for the analyze workflow.

Estimates total input tokens from assembled context files, calculates
expected cost, and aborts (exit 1) if the estimate exceeds the hard cap.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.model_pricing import (
    MODEL_RATES,
    estimate_cost_usd,
)
from scripts.track_token_usage import (
    estimate_tokens_from_path,
)

DEFAULT_OUTPUT_TOKENS = 2000
DEFAULT_MODEL = "copilot-default"
HARD_CAP_USD = 1.00


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pre-flight token cost estimation. Aborts if estimate exceeds hard cap."
    )
    parser.add_argument(
        "--context-files",
        nargs="+",
        type=Path,
        required=True,
        help="Paths to context files that will be sent as input (raw JSON, prompt, wisdom, etc.).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Model or rate profile name for cost lookup (default: copilot-default).",
    )
    parser.add_argument(
        "--output-tokens",
        type=int,
        default=DEFAULT_OUTPUT_TOKENS,
        help=f"Estimated output tokens (default: {DEFAULT_OUTPUT_TOKENS}).",
    )
    parser.add_argument(
        "--hard-cap",
        type=float,
        default=HARD_CAP_USD,
        help=f"Maximum allowed estimated cost in USD (default: {HARD_CAP_USD}).",
    )
    return parser.parse_args(argv)


def estimate_input_tokens(context_files: list[Path]) -> int:
    """Sum estimated tokens across all context files."""
    return sum(estimate_tokens_from_path(p) for p in context_files)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    input_tokens = estimate_input_tokens(args.context_files)
    output_tokens = args.output_tokens
    total_tokens = input_tokens + output_tokens
    cost = estimate_cost_usd(args.model, input_tokens, output_tokens)

    if cost is None:
        print(
            f"::warning::Unknown model '{args.model}' — cannot estimate cost. "
            f"Known models: {', '.join(sorted(MODEL_RATES.keys()))}",
            file=sys.stderr,
        )
        return 1

    print(
        f"::notice::Pre-flight estimate: {input_tokens} input + {output_tokens} output "
        f"= {total_tokens} tokens → ${cost:.4f} (cap: ${args.hard_cap:.2f}, model: {args.model})"
    )

    if cost > args.hard_cap:
        print(
            f"::error::Estimated cost ${cost:.4f} exceeds hard cap ${args.hard_cap:.2f}. Aborting.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
