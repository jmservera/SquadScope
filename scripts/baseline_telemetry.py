#!/usr/bin/env python3
"""Baseline telemetry collection and reporting for crawl matrix readiness.

Records p50/p95 timings across pipeline stages:
- GitHub crawl
- RSS/news crawl
- Correlation / press context rendering
- Analysis (map/reduce dry-run)

The baseline window requires at least 5 representative runs (or explicit
rationale for fewer). Telemetry is read from the observability ledger
artifacts in data/metrics/observability/.

Usage:
    python -m scripts.baseline_telemetry report
    python -m scripts.baseline_telemetry check --min-runs 5

References:
    - Issue #333: Define crawl matrix readiness and fan-in validation path
    - scripts/observability_metrics.py: Ledger schema
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_METRICS_DIR = ROOT / "data" / "metrics" / "observability"

# Minimum number of runs for a valid baseline
MINIMUM_BASELINE_RUNS = 5


@dataclass(slots=True)
class StageBaseline:
    """Timing baseline for a single pipeline stage."""

    stage: str
    sample_count: int
    p50_seconds: float
    p95_seconds: float
    min_seconds: float
    max_seconds: float
    mean_seconds: float


@dataclass(slots=True)
class BaselineReport:
    """Complete baseline telemetry report across all stages."""

    total_runs: int
    observation_window_start: str
    observation_window_end: str
    stages: list[StageBaseline]
    sufficient: bool
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_runs": self.total_runs,
            "observation_window_start": self.observation_window_start,
            "observation_window_end": self.observation_window_end,
            "stages": [asdict(s) for s in self.stages],
            "sufficient": self.sufficient,
            "rationale": self.rationale,
        }


def percentile(values: list[float], pct: float) -> float:
    """Compute percentile from sorted values."""
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * pct / 100.0) - 1)
    return round(ordered[index], 3)


def load_ledger_entries(metrics_dir: Path) -> list[dict[str, Any]]:
    """Load all observability ledger JSON files from the metrics directory."""
    entries = []
    if not metrics_dir.exists():
        return entries

    for f in sorted(metrics_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "crawl_metrics" in data:
                entries.append(data)
        except (json.JSONDecodeError, OSError):
            continue

    return entries


def compute_stage_baseline(stage: str, durations: list[float]) -> StageBaseline:
    """Compute baseline statistics for a pipeline stage."""
    if not durations:
        return StageBaseline(
            stage=stage,
            sample_count=0,
            p50_seconds=0.0,
            p95_seconds=0.0,
            min_seconds=0.0,
            max_seconds=0.0,
            mean_seconds=0.0,
        )

    return StageBaseline(
        stage=stage,
        sample_count=len(durations),
        p50_seconds=percentile(durations, 50),
        p95_seconds=percentile(durations, 95),
        min_seconds=round(min(durations), 3),
        max_seconds=round(max(durations), 3),
        mean_seconds=round(sum(durations) / len(durations), 3),
    )


def build_baseline_report(
    entries: list[dict[str, Any]],
    min_runs: int = MINIMUM_BASELINE_RUNS,
    rationale: str = "",
) -> BaselineReport:
    """Build a baseline telemetry report from observability ledger entries."""
    github_durations: list[float] = []
    rss_durations: list[float] = []
    correlation_durations: list[float] = []
    analysis_durations: list[float] = []
    timestamps: list[str] = []

    for entry in entries:
        ts = entry.get("timestamp", "")
        if ts:
            timestamps.append(ts)

        crawl_metrics = entry.get("crawl_metrics", [])
        for cm in crawl_metrics:
            if not isinstance(cm, dict):
                continue
            duration = cm.get("duration_seconds", 0)
            source_type = cm.get("source_type", "")
            if source_type == "github":
                github_durations.append(float(duration))
            elif source_type in ("rss", "external_news", "techcrunch"):
                rss_durations.append(float(duration))
            elif source_type in ("correlation", "press_context"):
                correlation_durations.append(float(duration))

        analysis = entry.get("analysis_metrics")
        if isinstance(analysis, dict):
            ad = analysis.get("duration_seconds", 0)
            if ad:
                analysis_durations.append(float(ad))

    total_runs = len(entries)
    window_start = min(timestamps) if timestamps else ""
    window_end = max(timestamps) if timestamps else ""

    stages = [
        compute_stage_baseline("github_crawl", github_durations),
        compute_stage_baseline("rss_news_crawl", rss_durations),
        compute_stage_baseline("correlation_press_context", correlation_durations),
        compute_stage_baseline("analysis", analysis_durations),
    ]

    sufficient = total_runs >= min_runs

    return BaselineReport(
        total_runs=total_runs,
        observation_window_start=window_start,
        observation_window_end=window_end,
        stages=stages,
        sufficient=sufficient,
        rationale=rationale,
    )


def check_trigger_thresholds(report: BaselineReport) -> dict[str, Any]:
    """Evaluate trigger thresholds against baseline telemetry.

    Returns a dict with threshold status for each experiment gate.
    """
    rss_stage = next((s for s in report.stages if s.stage == "rss_news_crawl"), None)
    github_stage = next((s for s in report.stages if s.stage == "github_crawl"), None)

    return {
        "rss_matrix_triggers": {
            "p95_exceeds_60s": rss_stage.p95_seconds > 60.0 if rss_stage else False,
            "p95_value": rss_stage.p95_seconds if rss_stage else 0.0,
            "threshold": 60.0,
            "triggered": (rss_stage.p95_seconds > 60.0) if rss_stage else False,
        },
        "github_shard_triggers": {
            "baseline_p95": github_stage.p95_seconds if github_stage else 0.0,
            "speedup_threshold_pct": 25.0,
            "api_growth_ceiling_pct": 10.0,
            "secondary_rate_limit_regression": False,
            "triggered": False,  # Requires experiment comparison
        },
        "baseline_sufficient": report.sufficient,
        "total_runs": report.total_runs,
        "minimum_required": MINIMUM_BASELINE_RUNS,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Crawl matrix baseline telemetry")
    sub = parser.add_subparsers(dest="command")

    report_cmd = sub.add_parser("report", help="Generate baseline telemetry report")
    report_cmd.add_argument(
        "--metrics-dir", type=Path, default=DEFAULT_METRICS_DIR,
        help="Path to observability metrics directory",
    )
    report_cmd.add_argument("--output", type=Path, help="Write report JSON to file")

    check_cmd = sub.add_parser("check", help="Check baseline readiness")
    check_cmd.add_argument(
        "--metrics-dir", type=Path, default=DEFAULT_METRICS_DIR,
        help="Path to observability metrics directory",
    )
    check_cmd.add_argument(
        "--min-runs", type=int, default=MINIMUM_BASELINE_RUNS,
        help="Minimum number of runs required",
    )

    args = parser.parse_args()

    if args.command == "report":
        entries = load_ledger_entries(args.metrics_dir)
        report = build_baseline_report(entries)
        output = json.dumps(report.to_dict(), indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output + "\n", encoding="utf-8")
            print(f"Report written to {args.output}")
        else:
            print(output)
        return 0

    elif args.command == "check":
        entries = load_ledger_entries(args.metrics_dir)
        report = build_baseline_report(entries, min_runs=args.min_runs)
        thresholds = check_trigger_thresholds(report)

        if report.sufficient:
            print(f"✅ Baseline sufficient: {report.total_runs} runs (minimum: {args.min_runs})")
            for stage in report.stages:
                if stage.sample_count > 0:
                    print(f"   {stage.stage}: p50={stage.p50_seconds}s p95={stage.p95_seconds}s")
        else:
            print(
                f"❌ Baseline insufficient: {report.total_runs} runs "
                f"(minimum: {args.min_runs} required)"
            )
            return 1

        # Check triggers
        rss_triggered = thresholds["rss_matrix_triggers"]["triggered"]
        print(f"\n   RSS matrix trigger: {'🔴 TRIGGERED' if rss_triggered else '🟢 not triggered'}")
        print(f"   GitHub shard trigger: 🟢 requires experiment comparison")
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
