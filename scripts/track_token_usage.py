#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_USAGE_FILE = ROOT / "data" / "metrics" / "token-usage.jsonl"
CHARS_PER_TOKEN = 4
MODEL_RATES = {
    "claude-sonnet-4": {"input": 3.00, "output": 15.00},
    "openai/gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "openai/gpt-5-mini": {"input": 0.25, "output": 2.00},
    "gpt-5-mini": {"input": 0.25, "output": 2.00},
    "claude-haiku-4.5": {"input": 1.00, "output": 5.00},
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Track token usage and estimated cost per pipeline run.")
    parser.add_argument("--stage", required=True, help="Pipeline stage (for example: analysis, reskill).")
    parser.add_argument("--source", required=True, help="Execution source (for example: copilot-cli, github-models).")
    parser.add_argument("--model", required=True, help="Model name used for cost rates.")
    parser.add_argument("--current-datetime", required=True, help="ISO-8601 timestamp for the run.")
    parser.add_argument("--week", help="Week slug (YYYY-WNN). If omitted, inferred from current datetime.")
    parser.add_argument("--prompt-file", type=Path, help="Prompt file used to estimate input tokens.")
    parser.add_argument("--output-file", type=Path, help="Output file used to estimate output tokens.")
    parser.add_argument("--input-tokens", type=int, help="Explicit input token count.")
    parser.add_argument("--output-tokens", type=int, help="Explicit output token count.")
    parser.add_argument("--usage-file", type=Path, default=DEFAULT_USAGE_FILE, help="JSONL path for usage ledger.")
    return parser.parse_args(argv)


def parse_datetime(value: str) -> datetime:
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = f"{candidate[:-1]}+00:00"
    parsed = datetime.fromisoformat(candidate)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def week_slug(value: datetime) -> str:
    year, week, _ = value.isocalendar()
    return f"{year}-W{week:02d}"


def estimate_tokens_from_text(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    return max(1, math.ceil(len(stripped) / CHARS_PER_TOKEN))


def estimate_tokens_from_path(path: Path | None) -> int:
    if path is None or not path.exists():
        return 0
    return estimate_tokens_from_text(path.read_text(encoding="utf-8"))


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float | None:
    rates = MODEL_RATES.get(model)
    if not rates:
        return None
    total = (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000
    return round(total, 6)


def build_record(args: argparse.Namespace) -> dict[str, object]:
    parsed_datetime = parse_datetime(args.current_datetime).astimezone(UTC)
    input_tokens = args.input_tokens if args.input_tokens is not None else estimate_tokens_from_path(args.prompt_file)
    output_tokens = args.output_tokens if args.output_tokens is not None else estimate_tokens_from_path(args.output_file)
    week = args.week or week_slug(parsed_datetime)
    cost = estimate_cost_usd(args.model, input_tokens, output_tokens)
    return {
        "timestamp": parsed_datetime.isoformat().replace("+00:00", "Z"),
        "month": parsed_datetime.strftime("%Y-%m"),
        "week": week,
        "stage": args.stage,
        "source": args.source,
        "model": args.model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_usd": cost,
        "estimated": args.input_tokens is None or args.output_tokens is None,
    }


def append_record(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True))
        handle.write("\n")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    record = build_record(args)
    append_record(args.usage_file, record)
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
