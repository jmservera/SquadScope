#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import UTC, datetime
from pathlib import Path

from scripts.model_pricing import estimate_cost_usd

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_USAGE_FILE = ROOT / "data" / "metrics" / "token-usage.jsonl"
CHARS_PER_TOKEN = 4


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Track token usage and estimated cost per pipeline run."
    )
    parser.add_argument(
        "--stage", required=True, help="Pipeline stage (for example: analysis, reskill)."
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Execution source (for example: copilot-cli, github-models).",
    )
    parser.add_argument("--model", required=True, help="Model name used for cost rates.")
    parser.add_argument("--current-datetime", required=True, help="ISO-8601 timestamp for the run.")
    parser.add_argument(
        "--week", help="Week slug (YYYY-WNN). If omitted, inferred from current datetime."
    )
    parser.add_argument(
        "--prompt-file", type=Path, help="Prompt file used to estimate input tokens."
    )
    parser.add_argument(
        "--output-file", type=Path, help="Output file used to estimate output tokens."
    )
    parser.add_argument("--input-tokens", type=int, help="Explicit input token count.")
    parser.add_argument("--output-tokens", type=int, help="Explicit output token count.")
    parser.add_argument(
        "--api-response",
        type=Path,
        help="GitHub Models API response JSON for extracting usage data.",
    )
    parser.add_argument(
        "--input-manifest",
        type=Path,
        help="analysis-input-manifest JSON used to validate final prompt input tokens within 10%.",
    )
    parser.add_argument(
        "--usage-file", type=Path, default=DEFAULT_USAGE_FILE, help="JSONL path for usage ledger."
    )
    parser.add_argument("--workflow-run-id", help="GitHub Actions workflow run ID.")
    parser.add_argument("--run-attempt", type=int, help="GitHub Actions workflow run attempt.")
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
    workflow_run_id = getattr(args, "workflow_run_id", None)
    run_attempt = getattr(args, "run_attempt", None)
    if (workflow_run_id is None) != (run_attempt is None):
        raise ValueError("workflow run ID and run attempt must be provided together")
    if run_attempt is not None and run_attempt < 1:
        raise ValueError("run attempt must be at least 1")

    # Priority: 1) explicit flags, 2) trusted API response, 3) file-size estimate.
    # Never derive authoritative usage from agent-authored output.
    estimated = True
    input_tokens: int | None = None
    output_tokens: int | None = None

    # Highest priority: explicit --input-tokens / --output-tokens
    if args.input_tokens is not None and args.output_tokens is not None:
        input_tokens = args.input_tokens
        output_tokens = args.output_tokens
        estimated = False

    # Second priority: parsed from a structured provider response.
    if input_tokens is None or output_tokens is None:
        parsed = None
        api_response_path = getattr(args, "api_response", None)
        if api_response_path is not None:
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
    record: dict[str, object] = {
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
    if workflow_run_id is not None:
        record["workflow_run_id"] = str(workflow_run_id)
        record["run_attempt"] = run_attempt
    validation = validate_input_manifest(args.input_manifest, input_tokens)
    if validation is not None:
        record["input_manifest_validation"] = validation
    return record


def _manifest_prompt_tokens(manifest: dict[str, object]) -> int | None:
    rendered = manifest.get("rendered_prompt_estimate")
    if isinstance(rendered, dict) and isinstance(rendered.get("tokens"), int):
        return int(rendered["tokens"])
    value = manifest.get("prompt_tokens")
    return int(value) if isinstance(value, int) else None


def validate_input_manifest(path: Path | None, input_tokens: int) -> dict[str, object] | None:
    if path is None:
        return None
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError(f"Input manifest must be an object: {path}")
    estimated_tokens = _manifest_prompt_tokens(manifest)
    if estimated_tokens is None:
        raise ValueError(f"Input manifest missing rendered prompt token estimate: {path}")
    delta = abs(input_tokens - estimated_tokens)
    ratio = delta / max(input_tokens, 1)
    degraded = bool(manifest.get("degraded")) or not bool(
        manifest.get("prompt_within_budget", True)
    )
    passed = ratio <= 0.10
    reason = None
    if not passed:
        reason = (
            f"Final input usage differs from manifest by {ratio:.1%} "
            f"({input_tokens} actual vs {estimated_tokens} estimated)."
        )
        if degraded:
            reason += (
                " Manifest is degraded/compacted, so the run is already marked candidate-only."
            )
    return {
        "manifest_path": path.as_posix(),
        "estimated_input_tokens": estimated_tokens,
        "actual_input_tokens": input_tokens,
        "delta_tokens": delta,
        "delta_ratio": round(ratio, 6),
        "within_10_percent": passed,
        "degraded_or_compacted": degraded,
        "reason": reason,
    }


def append_record(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True))
        handle.write("\n")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        record = build_record(args)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"::error::Token usage manifest validation failed: {exc}", file=sys.stderr)
        return 1
    validation = record.get("input_manifest_validation")
    if (
        isinstance(validation, dict)
        and not validation.get("within_10_percent")
        and not validation.get("degraded_or_compacted")
    ):
        print(f"::error::{validation.get('reason')}", file=sys.stderr)
        return 1
    append_record(args.usage_file, record)
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
