#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import analysis_gate  # noqa: E402

DEFAULT_ANALYZED_DIR = ROOT / "data" / "analyzed"


@dataclass(frozen=True)
class QualityEntry:
    week: str
    score: int
    path: Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a quality trend report from analyzed summaries."
    )
    parser.add_argument(
        "--analyzed-dir",
        type=Path,
        default=DEFAULT_ANALYZED_DIR,
        help="Directory containing analyzed weekly summaries.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the markdown report. Defaults to stdout.",
    )
    return parser.parse_args(argv)


def load_quality_entries(analyzed_dir: Path) -> list[QualityEntry]:
    if not analyzed_dir.exists():
        return []

    entries: list[QualityEntry] = []
    for path in sorted(analyzed_dir.glob("*-summary.md")):
        frontmatter, _ = analysis_gate.extract_frontmatter(path.read_text(encoding="utf-8"))
        week = frontmatter.get("week")
        score = frontmatter.get("quality_score")
        if isinstance(week, str) and isinstance(score, int):
            entries.append(QualityEntry(week=week, score=score, path=path))
    return sorted(entries, key=lambda entry: entry.week)


def classify_trend(entries: list[QualityEntry]) -> str:
    if len(entries) < 2:
        return "insufficient history"

    change = entries[-1].score - entries[0].score
    if change >= 5:
        return "improving"
    if change <= -5:
        return "declining"
    return "stable"


def build_quality_report(analyzed_dir: Path) -> str:
    from scripts.sanitize_repo_content import _escape_untrusted_boundaries

    entries = load_quality_entries(analyzed_dir)
    lines = ["# Quality Trend Report", ""]

    if not entries:
        lines.extend(
            [
                "No analyzed summaries with a parseable `quality_score` were found.",
                "",
                "## Weekly Scores",
                "",
                "_No data available._",
            ]
        )
        return "\n".join(lines) + "\n"

    average_score = sum(entry.score for entry in entries) / len(entries)
    trend = classify_trend(entries)
    best = max(entries, key=lambda entry: entry.score)
    worst = min(entries, key=lambda entry: entry.score)
    latest = entries[-1]

    lines.extend(
        [
            f"- Summaries analyzed: {len(entries)}",
            f"- Average quality score: {average_score:.1f}",
            f"- Trend: {trend}",
            f"- Latest week: {latest.week} ({latest.score})",
            f"- Best week: {best.week} ({best.score})",
            f"- Lowest week: {worst.week} ({worst.score})",
            "",
            "## Weekly Scores",
            "",
            "| Week | Quality Score |",
            "| --- | ---: |",
        ]
    )
    for entry in entries:
        lines.append(f"| {entry.week} | {entry.score} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"Quality is currently **{trend}** based on the available summaries. Use this trend as a calibration aid, not as a substitute for reviewing the underlying Signal/Noise/Gaps calls.",
        ]
    )
    return _escape_untrusted_boundaries("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_quality_report(args.analyzed_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
