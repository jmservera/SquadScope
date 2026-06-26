#!/usr/bin/env python3
"""Wisdom.md size cap and retirement management.

Checks wisdom.md file size against a soft limit and retires oldest
heuristics to an archive file when the limit is exceeded.

CLI:
    python scripts/wisdom_cap.py --topic ai-ml [--limit 5120] [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

SQUAD_DIR = Path(".squad/topics")
DEFAULT_LIMIT = 5120  # 5KB soft limit


def get_wisdom_path(topic: str) -> Path:
    return SQUAD_DIR / topic / "wisdom.md"


def get_archive_path(topic: str) -> Path:
    return SQUAD_DIR / topic / "wisdom-archive.md"


def parse_heuristics(content: str) -> list[dict]:
    """Parse wisdom.md into sections with their heuristic bullet points.

    Returns a list of dicts with 'section', 'line', and 'text' keys.
    """
    heuristics = []
    current_section = ""
    for i, line in enumerate(content.splitlines()):
        if line.startswith("## "):
            current_section = line.strip("# ").strip()
        elif line.startswith("- "):
            heuristics.append(
                {
                    "section": current_section,
                    "line": i,
                    "text": line,
                }
            )
    return heuristics


def select_for_retirement(heuristics: list[dict], bytes_to_free: int) -> list[dict]:
    """Select heuristics from the end of the list (oldest/least-referenced first).

    Strategy: retire from the bottom of each section first, working backwards.
    """
    # Retire from the end of the file upward until we've freed enough bytes
    retired = []
    freed = 0
    for h in reversed(heuristics):
        if freed >= bytes_to_free:
            break
        retired.append(h)
        freed += len(h["text"].encode("utf-8")) + 1  # +1 for newline
    return retired


def retire_heuristics(
    wisdom_path: Path, archive_path: Path, limit: int, dry_run: bool = False
) -> dict:
    """Check wisdom size and retire heuristics if over limit.

    Returns a summary dict with action details.
    """
    if not wisdom_path.exists():
        return {"status": "skip", "reason": "wisdom.md not found", "path": str(wisdom_path)}

    content = wisdom_path.read_text(encoding="utf-8")
    current_size = len(content.encode("utf-8"))

    if current_size <= limit:
        return {
            "status": "ok",
            "size": current_size,
            "limit": limit,
            "message": f"Under limit ({current_size}/{limit} bytes)",
        }

    bytes_over = current_size - limit
    heuristics = parse_heuristics(content)

    if not heuristics:
        return {
            "status": "warn",
            "size": current_size,
            "message": "Over limit but no parseable heuristics to retire",
        }

    to_retire = select_for_retirement(heuristics, bytes_over)

    if dry_run:
        return {
            "status": "dry_run",
            "size": current_size,
            "limit": limit,
            "would_retire": len(to_retire),
            "items": [h["text"] for h in to_retire],
        }

    # Build archive entry
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    archive_entry = (
        f"\n## Retired {timestamp}\n\nReason: wisdom.md exceeded {limit} byte soft limit\n\n"
    )
    archive_entry += "\n".join(h["text"] for h in to_retire) + "\n"

    # Write archive
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        existing = archive_path.read_text(encoding="utf-8")
        archive_path.write_text(existing + archive_entry, encoding="utf-8")
    else:
        header = "# Wisdom Archive\n\nRetired heuristics from wisdom.md.\n"
        archive_path.write_text(header + archive_entry, encoding="utf-8")

    # Remove retired lines from wisdom content
    lines = content.splitlines()
    retired_lines = {h["line"] for h in to_retire}
    new_lines = [ln for i, ln in enumerate(lines) if i not in retired_lines]
    # Clean up any trailing empty lines in sections
    new_content = "\n".join(new_lines).rstrip() + "\n"
    wisdom_path.write_text(new_content, encoding="utf-8")

    new_size = len(new_content.encode("utf-8"))
    return {
        "status": "retired",
        "original_size": current_size,
        "new_size": new_size,
        "retired_count": len(to_retire),
        "archive_path": str(archive_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Wisdom.md size cap management")
    parser.add_argument("--topic", required=True, help="Topic ID (e.g., ai-ml)")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Size limit in bytes")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be retired")
    args = parser.parse_args(argv)

    wisdom_path = get_wisdom_path(args.topic)
    archive_path = get_archive_path(args.topic)

    result = retire_heuristics(wisdom_path, archive_path, args.limit, dry_run=args.dry_run)

    if result["status"] == "skip":
        print(f"Skipped: {result['reason']}")
    elif result["status"] == "ok":
        print(result["message"])
    elif result["status"] == "dry_run":
        print(f"DRY RUN: Would retire {result['would_retire']} heuristics")
        for item in result.get("items", []):
            print(f"  {item}")
    elif result["status"] == "retired":
        print(f"Retired {result['retired_count']} heuristics")
        print(f"  Size: {result['original_size']} -> {result['new_size']} bytes")
        print(f"  Archive: {result['archive_path']}")
    else:
        print(f"Warning: {result.get('message', 'unknown status')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
