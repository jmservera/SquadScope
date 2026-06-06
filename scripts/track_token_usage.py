#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path

from scripts.model_pricing import MODEL_RATES, estimate_cost_usd

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_USAGE_FILE = ROOT / "data" / "metrics" / "token-usage.jsonl"
CHARS_PER_TOKEN = 4


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
    parser.add_argument("--transcript", type=Path, help="Copilot CLI --share transcript file for parsing token usage.")
    parser.add_argument("--api-response", type=Path, help="GitHub Models API response JSON for extracting usage data.")
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


def parse_copilot_transcript(path: Path) -> tuple[int, int] | None:
    """Parse a Copilot CLI --share transcript for token usage metadata.

    Searches for patterns like:
      - "Input tokens: 1234" / "Output tokens: 567"
      - "prompt_tokens: 1234" / "completion_tokens: 567"
      - "Tokens used: 1234 input, 567 output"
    Returns (input_tokens, output_tokens) or None if not found.
    """
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    input_tokens: int | None = None
    output_tokens: int | None = None

    # Pattern: "Input tokens: N" and "Output tokens: N"
    m_input = re.search(r"[Ii]nput[\s_]tokens[\s:]+(\d+)", text)
    m_output = re.search(r"[Oo]utput[\s_]tokens[\s:]+(\d+)", text)
    if m_input and m_output:
        return int(m_input.group(1)), int(m_output.group(1))

    # Pattern: "prompt_tokens: N" and "completion_tokens: N"
    m_prompt = re.search(r"prompt_tokens[\"'\s:]+(\d+)", text)
    m_completion = re.search(r"completion_tokens[\"'\s:]+(\d+)", text)
    if m_prompt and m_completion:
        return int(m_prompt.group(1)), int(m_completion.group(1))

    # Pattern: "Tokens used: N input, N output"
    m_combined = re.search(r"[Tt]okens\s+used[\s:]+(\d+)\s+input[,;\s]+(\d+)\s+output", text)
    if m_combined:
        return int(m_combined.group(1)), int(m_combined.group(2))

    # Pattern: "Usage: N/N tokens (input/output)"
    m_usage = re.search(r"[Uu]sage[\s:]+(\d+)\s*/\s*(\d+)\s*tokens", text)
    if m_usage:
        return int(m_usage.group(1)), int(m_usage.group(2))

    return None


def parse_api_response(path: Path) -> tuple[int, int] | None:
    """Parse a GitHub Models API response JSON for usage data.

    Expects OpenAI-compatible format with usage.prompt_tokens and
    usage.completion_tokens fields.
    Returns (input_tokens, output_tokens) or None if not found.
    """
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    usage = data.get("usage") if isinstance(data, dict) else None
    if not isinstance(usage, dict):
        return None

    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    if isinstance(prompt_tokens, int) and isinstance(completion_tokens, int):
        return prompt_tokens, completion_tokens

    return None


def build_record(args: argparse.Namespace) -> dict[str, object]:
    parsed_datetime = parse_datetime(args.current_datetime).astimezone(UTC)
    week = args.week or week_slug(parsed_datetime)

    # Priority: 1) explicit flags, 2) transcript/api-response, 3) file-size estimate
    estimated = True
    input_tokens: int | None = None
    output_tokens: int | None = None

    # Highest priority: explicit --input-tokens / --output-tokens
    if args.input_tokens is not None and args.output_tokens is not None:
        input_tokens = args.input_tokens
        output_tokens = args.output_tokens
        estimated = False

    # Second priority: parsed from transcript or API response
    if input_tokens is None or output_tokens is None:
        parsed = None
        transcript_path = getattr(args, "transcript", None)
        api_response_path = getattr(args, "api_response", None)
        if transcript_path is not None:
            parsed = parse_copilot_transcript(transcript_path)
        if parsed is None and api_response_path is not None:
            parsed = parse_api_response(api_response_path)
        if parsed is not None:
            input_tokens = parsed[0]
            output_tokens = parsed[1]
            estimated = False

    # Lowest priority: file-size estimation
    if input_tokens is None:
        input_tokens = estimate_tokens_from_path(args.prompt_file)
    if output_tokens is None:
        output_tokens = estimate_tokens_from_path(args.output_file)

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
        "estimated": estimated,
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
