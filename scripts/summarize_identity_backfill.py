#!/usr/bin/env python3
"""Print a status-count summary of a repo-identity-backfill.json file."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


def summarize(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("entries", {})
    counts = Counter(entry.get("status") for entry in entries.values())
    lines = [f"total entries: {len(entries)}"]
    lines.extend(f"{status}: {count}" for status, count in sorted(counts.items()))
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "usage: summarize_identity_backfill.py <path-to-repo-identity-backfill.json>",
            file=sys.stderr,
        )
        return 2
    print(summarize(Path(sys.argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
