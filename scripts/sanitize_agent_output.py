#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

META_LINE_PATTERNS = [
    re.compile(r"^✅\s+.+\bis done\..*$"),
    re.compile(r"^Quality score:\s+.*$", re.IGNORECASE),
    re.compile(r"^Editorial thesis:\s+.*$", re.IGNORECASE),
    re.compile(r"^data/analyzed/.+\.md is written.*$", re.IGNORECASE),
    re.compile(r"^\.squad/reskill/.+\.md is written.*$", re.IGNORECASE),
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Strip leaked Copilot/Farnsworth meta lines from markdown outputs.")
    parser.add_argument("--path", required=True, type=Path, help="File to sanitize in place.")
    return parser.parse_args(argv)


def sanitize_text(text: str) -> str:
    sanitized_lines: list[str] = []
    changed = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and any(pattern.match(stripped) for pattern in META_LINE_PATTERNS):
            changed = True
            continue
        sanitized_lines.append(line)
    sanitized = "\n".join(sanitized_lines)
    if text.endswith("\n"):
        sanitized += "\n"
    if changed:
        sanitized = re.sub(r"\n{3,}", "\n\n", sanitized)
    return sanitized


def sanitize_file(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    original = path.read_text(encoding="utf-8")
    sanitized = sanitize_text(original)
    if sanitized == original:
        return False
    path.write_text(sanitized, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    sanitize_file(args.path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
