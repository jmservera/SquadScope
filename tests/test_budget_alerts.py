"""Tests for scripts/budget_alerts.py."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from scripts.budget_alerts import (
    MONTHLY_RECOMMEND_SWITCH,
    MONTHLY_WARNING,
    SINGLE_RUN_FAIL,
    SINGLE_RUN_WARNING,
    evaluate,
    load_monthly_spend,
    main,
)


@pytest.fixture
def metrics_file(tmp_path: Path) -> Path:
    return tmp_path / "token-usage.jsonl"


class TestLoadMonthlySpend:
    def test_missing_file(self, tmp_path: Path):
        assert load_monthly_spend(tmp_path / "nonexistent.jsonl") == 0.0

    def test_empty_file(self, metrics_file: Path):
        metrics_file.write_text("")
        assert load_monthly_spend(metrics_file) == 0.0

    def test_sums_current_month(self, metrics_file: Path):
        now = datetime(2026, 5, 19, tzinfo=UTC)
        entries = [
            {"timestamp": "2026-05-01T10:00:00Z", "estimated_cost": 0.30},
            {"timestamp": "2026-05-15T10:00:00Z", "estimated_cost": 0.50},
            {"timestamp": "2026-04-28T10:00:00Z", "estimated_cost": 1.00},  # prev month
        ]
        metrics_file.write_text("\n".join(json.dumps(e) for e in entries))
        assert load_monthly_spend(metrics_file, now=now) == pytest.approx(0.80)

    def test_handles_malformed_lines(self, metrics_file: Path):
        now = datetime(2026, 5, 19, tzinfo=UTC)
        metrics_file.write_text("not json\n" + json.dumps({"timestamp": "2026-05-01T10:00:00Z", "estimated_cost": 0.25}))
        assert load_monthly_spend(metrics_file, now=now) == pytest.approx(0.25)


class TestEvaluate:
    def test_no_alerts_under_thresholds(self):
        annotations, code = evaluate(0.10, 2.00)
        assert annotations == []
        assert code == 0

    def test_single_run_warning(self):
        annotations, code = evaluate(0.60, 2.00)
        assert any("::warning::" in a and "Single run" in a for a in annotations)
        assert code == 0

    def test_single_run_fail(self):
        annotations, code = evaluate(1.50, 2.00)
        assert any("::error::" in a for a in annotations)
        assert code == 1

    def test_monthly_warning(self):
        annotations, code = evaluate(None, 6.00)
        assert any("::warning::" in a and "cumulative" in a for a in annotations)
        assert code == 0

    def test_monthly_recommend_switch(self):
        annotations, code = evaluate(None, 11.00)
        assert any("cheaper model" in a for a in annotations)
        assert code == 0

    def test_both_single_and_monthly(self):
        annotations, code = evaluate(0.60, 6.00)
        assert len(annotations) == 2
        assert code == 0


class TestMain:
    def test_exit_0_no_issues(self, metrics_file: Path):
        metrics_file.write_text("")
        code = main(["--run-cost", "0.10", "--metrics", str(metrics_file)])
        assert code == 0

    def test_exit_1_over_cap(self, metrics_file: Path):
        metrics_file.write_text("")
        code = main(["--run-cost", "1.50", "--metrics", str(metrics_file)])
        assert code == 1

    def test_missing_metrics_file(self, tmp_path: Path):
        code = main(["--run-cost", "0.10", "--metrics", str(tmp_path / "missing.jsonl")])
        assert code == 0
