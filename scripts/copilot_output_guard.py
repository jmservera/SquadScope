#!/usr/bin/env python3
"""Generate per-invocation canaries and fail closed on unsafe Copilot output."""

from __future__ import annotations

import argparse
import re
import secrets
import unicodedata
from pathlib import Path

CANARY_PREFIX = "SQSC-CANARY"
CANARY_RE = re.compile(r"SQSC-CANARY-[0-9a-f]{16}", re.IGNORECASE)
BOUNDARY_MARKERS = ("<untrusted-content>", "</untrusted-content>")


def generate_canary() -> str:
    return f"{CANARY_PREFIX}-{secrets.token_hex(8)}"


def _canonicalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    return "".join(
        character for character in normalized if not unicodedata.category(character).startswith("C")
    ).casefold()


def validate_output(output: str, canary: str) -> list[str]:
    if not CANARY_RE.fullmatch(canary):
        return ["invalid current invocation canary"]

    violations: list[str] = []
    canonical_output = _canonicalize(output)
    canonical_canary = _canonicalize(canary)
    if canonical_canary in canonical_output:
        violations.append("current invocation canary leaked")
    elif f"{CANARY_PREFIX}-".casefold() in canonical_output:
        violations.append("unknown canary pattern found")
    for marker in BOUNDARY_MARKERS:
        if marker.casefold() in canonical_output:
            violations.append(f"prompt boundary marker leaked: {marker}")
    return violations


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument("--output", type=Path, required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--output", type=Path, required=True)
    validate_parser.add_argument("--canary-file", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "generate":
        args.output.write_text(generate_canary() + "\n", encoding="utf-8")
        return 0

    canary = args.canary_file.read_text(encoding="utf-8").strip()
    output = args.output.read_text(encoding="utf-8")
    violations = validate_output(output, canary)
    if violations:
        for violation in violations:
            print(f"::error::Copilot output safety violation: {violation}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
