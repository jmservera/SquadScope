"""Tests for baseline telemetry collection and reporting.

Verifies that the baseline telemetry module correctly:
- Loads observability ledger entries
- Computes p50/p95 statistics per pipeline stage
- Enforces the minimum-runs requirement
- Evaluates trigger thresholds
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.baseline_telemetry import (
    build_baseline_report,
    check_trigger_thresholds,
    compute_stage_baseline,
    load_ledger_entries,
    percentile,
)


def _sample_ledger(
    *,
    github_duration: float = 45.0,
    rss_duration: float = 1.2,
    analysis_duration: float = 120.0,
    timestamp: str = "2026-06-10T12:00:00Z",
) -> dict[str, Any]:
    return {
        "schema_version": "observability_v1",
        "run_id": "test",
        "week": "2026-W24",
        "timestamp": timestamp,
        "crawl_metrics": [
            {
                "duration_seconds": github_duration,
                "api_calls": 100,
                "cache_hits": 40,
                "cache_misses": 60,
                "stale_cache_hits": 2,
                "rate_limit_events": 0,
                "secondary_rate_limit_hit": False,
                "source_type": "github",
            },
            {
                "duration_seconds": rss_duration,
                "api_calls": 5,
                "cache_hits": 0,
                "cache_misses": 5,
                "stale_cache_hits": 0,
                "rate_limit_events": 0,
                "secondary_rate_limit_hit": False,
                "source_type": "rss",
            },
        ],
        "analysis_metrics": {
            "duration_seconds": analysis_duration,
            "token_ledger": {"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500},
            "map_stages": [],
        },
        "environment": {},
    }


class TestPercentile:
    def test_p50_odd(self):
        assert percentile([1.0, 2.0, 3.0, 4.0, 5.0], 50) == 3.0

    def test_p95_small_sample(self):
        assert percentile([10.0, 20.0, 30.0, 40.0, 50.0], 95) == 50.0

    def test_empty(self):
        assert percentile([], 50) == 0.0


class TestComputeStageBaseline:
    def test_valid_durations(self):
        durations = [10.0, 20.0, 30.0, 40.0, 50.0]
        baseline = compute_stage_baseline("test", durations)
        assert baseline.stage == "test"
        assert baseline.sample_count == 5
        assert baseline.min_seconds == 10.0
        assert baseline.max_seconds == 50.0
        assert baseline.p50_seconds == 30.0

    def test_empty_durations(self):
        baseline = compute_stage_baseline("test", [])
        assert baseline.sample_count == 0
        assert baseline.p50_seconds == 0.0


class TestLoadLedgerEntries:
    def test_loads_json_files(self, tmp_path: Path):
        ledger = _sample_ledger()
        (tmp_path / "run1.json").write_text(json.dumps(ledger))
        (tmp_path / "run2.json").write_text(json.dumps(ledger))
        entries = load_ledger_entries(tmp_path)
        assert len(entries) == 2

    def test_skips_invalid_json(self, tmp_path: Path):
        (tmp_path / "bad.json").write_text("not json")
        (tmp_path / "good.json").write_text(json.dumps(_sample_ledger()))
        entries = load_ledger_entries(tmp_path)
        assert len(entries) == 1

    def test_missing_dir_returns_empty(self, tmp_path: Path):
        entries = load_ledger_entries(tmp_path / "nonexistent")
        assert entries == []


class TestBuildBaselineReport:
    def test_sufficient_runs(self):
        entries = [_sample_ledger(timestamp=f"2026-06-{10 + i}T12:00:00Z") for i in range(5)]
        report = build_baseline_report(entries, min_runs=5)
        assert report.sufficient
        assert report.total_runs == 5
        assert len(report.stages) == 4

    def test_insufficient_runs(self):
        entries = [_sample_ledger() for _ in range(3)]
        report = build_baseline_report(entries, min_runs=5)
        assert not report.sufficient
        assert report.total_runs == 3

    def test_stage_durations_collected(self):
        entries = [
            _sample_ledger(github_duration=40.0),
            _sample_ledger(github_duration=50.0),
            _sample_ledger(github_duration=60.0),
            _sample_ledger(github_duration=70.0),
            _sample_ledger(github_duration=80.0),
        ]
        report = build_baseline_report(entries)
        github_stage = next(s for s in report.stages if s.stage == "github_crawl")
        assert github_stage.sample_count == 5
        assert github_stage.min_seconds == 40.0
        assert github_stage.max_seconds == 80.0


class TestTriggerThresholds:
    def test_rss_not_triggered_below_threshold(self):
        entries = [_sample_ledger(rss_duration=1.0) for _ in range(5)]
        report = build_baseline_report(entries)
        thresholds = check_trigger_thresholds(report)
        assert not thresholds["rss_matrix_triggers"]["triggered"]

    def test_rss_triggered_above_threshold(self):
        entries = [_sample_ledger(rss_duration=65.0) for _ in range(5)]
        report = build_baseline_report(entries)
        thresholds = check_trigger_thresholds(report)
        assert thresholds["rss_matrix_triggers"]["triggered"]

    def test_github_shard_not_auto_triggered(self):
        entries = [_sample_ledger() for _ in range(5)]
        report = build_baseline_report(entries)
        thresholds = check_trigger_thresholds(report)
        # GitHub shard requires experiment comparison, never auto-triggers
        assert not thresholds["github_shard_triggers"]["triggered"]

    def test_baseline_sufficient_flag(self):
        entries = [_sample_ledger() for _ in range(5)]
        report = build_baseline_report(entries)
        thresholds = check_trigger_thresholds(report)
        assert thresholds["baseline_sufficient"]
