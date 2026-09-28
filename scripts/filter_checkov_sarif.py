"""Filter accepted in-source Checkov suppressions from SARIF before upload."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _has_in_source_suppression(result: dict[str, Any]) -> bool:
    suppressions = result.get("suppressions")
    if not isinstance(suppressions, list):
        return False
    return any(
        isinstance(suppression, dict) and suppression.get("kind") == "inSource"
        for suppression in suppressions
    )


def filter_in_source_suppressions(sarif: dict[str, Any]) -> int:
    """Remove SARIF results that Checkov already accepted via inline skips."""

    removed = 0
    runs = sarif.get("runs")
    if not isinstance(runs, list):
        return removed

    for run in runs:
        if not isinstance(run, dict):
            continue
        results = run.get("results")
        if not isinstance(results, list):
            continue
        kept: list[Any] = []
        for result in results:
            if isinstance(result, dict) and _has_in_source_suppression(result):
                removed += 1
            else:
                kept.append(result)
        run["results"] = kept
    return removed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Remove in-source-suppressed Checkov SARIF results before upload."
    )
    parser.add_argument("sarif", type=Path, help="SARIF file to update in place")
    args = parser.parse_args(argv)

    data = json.loads(args.sarif.read_text(encoding="utf-8"))
    removed = filter_in_source_suppressions(data)
    args.sarif.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Removed {removed} in-source-suppressed Checkov SARIF result(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
