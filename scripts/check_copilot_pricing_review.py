#!/usr/bin/env python3
"""Check whether the Copilot model pricing table is due for manual review."""
from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime
from pathlib import Path

from scripts.model_pricing import (
    MODEL_PRICING,
    PRICING_FETCHED_DATE,
    PRICING_REVIEW_INTERVAL_MONTHS,
    PRICING_SOURCE_URL,
    TieredModelRate,
)


def parse_source_headers(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    metadata: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        normalized = name.strip().lower()
        if normalized in {"etag", "last-modified"}:
            metadata[normalized] = value.strip()
    return metadata


def parse_date(value: str) -> date:
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = f"{candidate[:-1]}+00:00"
    if "T" in candidate:
        return datetime.fromisoformat(candidate).date()
    return date.fromisoformat(candidate)


def add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    month_lengths = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return date(year, month, min(value.day, month_lengths[month - 1]))


def pricing_status(
    current_date: date,
    source_url: str = PRICING_SOURCE_URL,
    source_headers: dict[str, str] | None = None,
) -> dict[str, object]:
    fetched_date = parse_date(PRICING_FETCHED_DATE)
    due_date = add_months(fetched_date, PRICING_REVIEW_INTERVAL_MONTHS)
    source_url_matches = source_url == PRICING_SOURCE_URL
    due = current_date >= due_date
    tiered_models = sorted(model for model, pricing in MODEL_PRICING.items() if isinstance(pricing, TieredModelRate))
    return {
        "needs_review": due or not source_url_matches,
        "review_due": due,
        "source_url_matches": source_url_matches,
        "source_url": PRICING_SOURCE_URL,
        "requested_source_url": source_url,
        "fetched_date": PRICING_FETCHED_DATE,
        "review_interval_months": PRICING_REVIEW_INTERVAL_MONTHS,
        "due_date": due_date.isoformat(),
        "current_date": current_date.isoformat(),
        "model_count": len(MODEL_PRICING),
        "tiered_models": tiered_models,
        "source_headers": source_headers or {},
    }


def render_report(status: dict[str, object]) -> str:
    result = "required" if status["needs_review"] else "not due"
    return "\n".join(
        [
            "# Copilot model pricing review",
            "",
            f"**Status:** Review {result}.",
            f"**Source:** {status['source_url']}",
            f"**Repository pricing fetched:** {status['fetched_date']}",
            f"**Review interval:** every {status['review_interval_months']} months",
            f"**Next/due review date:** {status['due_date']}",
            f"**Workflow check date:** {status['current_date']}",
            f"**Tracked pricing entries:** {status['model_count']}",
            f"**Long-context pricing entries:** {', '.join(status['tiered_models'])}",
            f"**Observed source metadata:** {json.dumps(status['source_headers'], sort_keys=True) if status['source_headers'] else 'not captured'}",
            "",
            "This workflow does not change pricing automatically. Please compare the repository pricing table against the GitHub docs, update code/docs/tests if needed, and open a PR.",
            "",
            "Checklist:",
            "- Review `scripts/model_pricing.py` against the source URL.",
            "- Update cost documentation and tests if rates, model names, or thresholds changed.",
            "- Keep the source URL and fetched date in sync with the reviewed table.",
        ]
    ) + "\n"


def write_github_output(path: Path, status: dict[str, object]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"needs_review={str(status['needs_review']).lower()}\n")
        handle.write(f"due_date={status['due_date']}\n")
        handle.write(f"fetched_date={status['fetched_date']}\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check whether Copilot model pricing needs manual review.")
    parser.add_argument("--current-date", default=datetime.now(UTC).date().isoformat(), help="Current UTC date.")
    parser.add_argument("--source-url", default=PRICING_SOURCE_URL, help="Expected GitHub Copilot pricing source URL.")
    parser.add_argument("--output", type=Path, help="Write a Markdown review report to this path.")
    parser.add_argument("--json-output", type=Path, help="Write machine-readable status JSON to this path.")
    parser.add_argument("--github-output", type=Path, help="Append step outputs for GitHub Actions.")
    parser.add_argument("--source-headers", type=Path, help="Optional HTTP response headers captured from the source URL.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    status = pricing_status(parse_date(args.current_date), args.source_url, parse_source_headers(args.source_headers))
    report = render_report(status)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")

    if args.json_output:
        args.json_output.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.github_output:
        write_github_output(args.github_output, status)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
