#!/usr/bin/env python3
"""Prepare AI prompts with canaries and reject unsafe generated output."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    from scripts.analyze_fallback import estimate_tokens, validate_output_safety
    from scripts.canary_token import generate_canary
except ModuleNotFoundError:  # pragma: no cover - direct script execution path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts.analyze_fallback import estimate_tokens, validate_output_safety
    from scripts.canary_token import generate_canary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    rotate = subparsers.add_parser("rotate", help="Rotate a prompt canary for a retry.")
    rotate.add_argument("--prompt", required=True, type=Path)
    rotate.add_argument("--token-file", required=True, type=Path)
    rotate.add_argument("--preflight-report", required=True, type=Path)

    validate = subparsers.add_parser("validate", help="Validate generated output.")
    validate.add_argument("--output", required=True, type=Path)
    validate.add_argument("--token-file", required=True, type=Path)

    return parser.parse_args(argv)


def rotate_canary(prompt_path: Path, token_path: Path, preflight_path: Path) -> None:
    prompt = prompt_path.read_text(encoding="utf-8")
    old_canary = token_path.read_text(encoding="utf-8").strip()
    new_canary = generate_canary()
    if not old_canary or old_canary not in prompt:
        raise ValueError("Existing prompt canary was not found in the prompt file.")
    prompt = prompt.replace(old_canary, new_canary)
    prompt_path.write_text(prompt, encoding="utf-8")
    token_path.write_text(new_canary + "\n", encoding="utf-8")

    report = json.loads(preflight_path.read_text(encoding="utf-8"))
    prompt_bytes = len(prompt.encode("utf-8"))
    prompt_tokens = estimate_tokens(prompt)
    checksum = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    report["prompt_bytes"] = prompt_bytes
    report["prompt_tokens"] = prompt_tokens
    report["prompt_checksum_sha256"] = checksum
    report["rendered_prompt_estimate"] = {
        "bytes": prompt_bytes,
        "tokens": prompt_tokens,
        "checksum_sha256": checksum,
    }
    report["prompt_within_budget"] = prompt_tokens <= report["prompt_token_budget"]
    report["publish_eligible"] = report["prompt_within_budget"]
    for component in report.get("components", []):
        if component.get("name") == "rendered_prompt":
            component["bytes"] = prompt_bytes
            component["token_estimate"] = prompt_tokens
            component["checksum_sha256"] = checksum
    preflight_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["prompt_within_budget"]:
        raise ValueError("Rotated prompt exceeds the configured token budget.")


def validate_output(output_path: Path, token_path: Path) -> list[str]:
    output = output_path.read_text(encoding="utf-8")
    canary = token_path.read_text(encoding="utf-8").strip()
    return validate_output_safety(output, canary)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "rotate":
        rotate_canary(args.prompt, args.token_file, args.preflight_report)
        return 0

    violations = validate_output(args.output, args.token_file)
    if violations:
        for violation in violations:
            print(f"::error::AI output safety violation: {violation}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
