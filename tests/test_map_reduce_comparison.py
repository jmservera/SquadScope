"""Tests for the map/reduce comparison framework and promotion logic."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.map_reduce_comparison import (
    COMPARISON_SCHEMA,
    PROMOTION_HARD_FLOOR_COVERAGE,
    PROMOTION_HARD_FLOOR_QUALITY,
    PROMOTION_MIN_COVERAGE,
    PROMOTION_MIN_QUALITY,
    check_promotion_eligibility,
    compute_verdict,
    generate_comparison_report,
    should_rollback,
    ArtifactInfo,
)


def _make_artifact_info(
    *,
    quality_score: int = 70,
    gate_passed: bool = True,
    evidence_coverage: float = 0.90,
    citation_count: int = 12,
    word_count: int = 1800,
) -> ArtifactInfo:
    return ArtifactInfo(
        path="test/artifact.md",
        sha256="abc123",
        quality_score=quality_score,
        gate_passed=gate_passed,
        evidence_coverage=evidence_coverage,
        citation_count=citation_count,
        word_count=word_count,
    )


def _make_comparison_report(
    *,
    week: str = "2026-W24",
    verdict: str = "pass",
    quality_score: int = 70,
    evidence_coverage: float = 0.90,
    gate_regression: bool = False,
    run_datetime: str | None = None,
) -> dict:
    if run_datetime is None:
        run_datetime = datetime.now(UTC).isoformat()
    return {
        "schema_version": COMPARISON_SCHEMA,
        "week": week,
        "run_datetime": run_datetime,
        "single_pass": {
            "artifact_path": "data/analyzed/summary.md",
            "sha256": "sp_hash",
            "quality_score": 72,
            "gate_passed": True,
            "evidence_coverage": 0.92,
            "citation_count": 14,
            "word_count": 1850,
        },
        "map_reduce": {
            "artifact_path": "data/map-reduce-candidates/candidate.md",
            "sha256": "mr_hash",
            "quality_score": quality_score,
            "gate_passed": not gate_regression,
            "evidence_coverage": evidence_coverage,
            "citation_count": 12,
            "word_count": 1720,
            "mapper_errors": {},
            "contradictions_resolved": 2,
            "claims_rejected": 5,
        },
        "deltas": {
            "quality_score": quality_score - 72,
            "evidence_coverage": evidence_coverage - 0.92,
            "citation_count": -2,
            "word_count": -130,
            "gate_regression": gate_regression,
        },
        "verdict": verdict,
        "blockers": [],
    }


class TestComputeVerdict:
    """Tests for verdict computation logic."""

    def test_pass_when_all_criteria_met(self):
        sp = _make_artifact_info(quality_score=72, evidence_coverage=0.92)
        mr = _make_artifact_info(quality_score=68, evidence_coverage=0.88)
        deltas = {"gate_regression": False}
        verdict, blockers = compute_verdict(sp, mr, deltas)
        assert verdict == "pass"
        assert blockers == []

    def test_fail_on_gate_regression(self):
        sp = _make_artifact_info(gate_passed=True)
        mr = _make_artifact_info(gate_passed=False)
        deltas = {"gate_regression": False}
        verdict, blockers = compute_verdict(sp, mr, deltas)
        assert verdict == "fail"
        assert any("Gate regression" in b for b in blockers)

    def test_fail_on_low_quality_score(self):
        sp = _make_artifact_info()
        mr = _make_artifact_info(quality_score=55)
        deltas = {"gate_regression": False}
        verdict, blockers = compute_verdict(sp, mr, deltas)
        assert verdict == "fail"
        assert any("Quality score" in b for b in blockers)

    def test_fail_on_hard_quality_floor(self):
        sp = _make_artifact_info()
        mr = _make_artifact_info(quality_score=50)
        deltas = {"gate_regression": False}
        verdict, blockers = compute_verdict(sp, mr, deltas)
        assert verdict == "fail"
        assert any("hard floor" in b for b in blockers)

    def test_fail_on_low_coverage(self):
        sp = _make_artifact_info()
        mr = _make_artifact_info(evidence_coverage=0.80)
        deltas = {"gate_regression": False}
        verdict, blockers = compute_verdict(sp, mr, deltas)
        assert verdict == "fail"
        assert any("Evidence coverage" in b for b in blockers)

    def test_fail_on_hard_coverage_floor(self):
        sp = _make_artifact_info()
        mr = _make_artifact_info(evidence_coverage=0.60)
        deltas = {"gate_regression": False}
        verdict, blockers = compute_verdict(sp, mr, deltas)
        assert verdict == "fail"
        assert any("hard floor" in b for b in blockers)


class TestShouldRollback:
    """Tests for automatic rollback trigger logic."""

    def test_no_rollback_on_passing_report(self):
        report = _make_comparison_report(verdict="pass")
        rollback, reason = should_rollback(report)
        assert rollback is False
        assert reason == ""

    def test_rollback_on_gate_regression(self):
        report = _make_comparison_report(gate_regression=True)
        report["deltas"]["gate_regression"] = True
        rollback, reason = should_rollback(report)
        assert rollback is True
        assert "Gate regression" in reason

    def test_rollback_on_hard_quality_floor(self):
        report = _make_comparison_report(quality_score=50)
        rollback, reason = should_rollback(report)
        assert rollback is True
        assert "hard floor" in reason

    def test_rollback_on_hard_coverage_floor(self):
        report = _make_comparison_report(evidence_coverage=0.60)
        rollback, reason = should_rollback(report)
        assert rollback is True
        assert "hard floor" in reason

    def test_rollback_on_mapper_failure(self):
        report = _make_comparison_report()
        report["map_reduce"]["mapper_errors"] = {
            "new_repos": ["schema_version mismatch"]
        }
        rollback, reason = should_rollback(report)
        assert rollback is True
        assert "Mapper failures" in reason

    def test_no_rollback_on_empty_mapper_errors(self):
        report = _make_comparison_report()
        report["map_reduce"]["mapper_errors"] = {"new_repos": [], "trending_repos": []}
        rollback, reason = should_rollback(report)
        assert rollback is False


class TestCheckPromotionEligibility:
    """Tests for promotion eligibility across multiple runs."""

    def test_not_eligible_with_fewer_than_3_runs(self):
        reports = [_make_comparison_report(week=f"2026-W{i}") for i in range(2)]
        result = check_promotion_eligibility(reports)
        assert result["eligible"] is False
        assert "need ≥ 3" in result["reason"]

    def test_not_eligible_with_insufficient_passing_runs(self):
        reports = [
            _make_comparison_report(week="2026-W21", verdict="pass"),
            _make_comparison_report(week="2026-W22", verdict="fail"),
            _make_comparison_report(week="2026-W23", verdict="fail"),
        ]
        result = check_promotion_eligibility(reports)
        assert result["eligible"] is False
        assert "Only 1/" in result["reason"]

    def test_eligible_with_3_passing_runs(self):
        reports = [
            _make_comparison_report(week=f"2026-W{21+i}", quality_score=70)
            for i in range(3)
        ]
        result = check_promotion_eligibility(reports)
        assert result["eligible"] is True
        assert "operator opt-in" in result["reason"]

    def test_not_eligible_with_low_average_quality(self):
        reports = [
            _make_comparison_report(week=f"2026-W{21+i}", quality_score=62)
            for i in range(3)
        ]
        result = check_promotion_eligibility(reports)
        assert result["eligible"] is False
        assert "Average quality" in result["reason"]

    def test_not_eligible_with_stale_runs(self):
        old_dt = "2026-04-01T00:00:00+00:00"
        reports = [
            _make_comparison_report(
                week=f"2026-W{13+i}", run_datetime=old_dt, quality_score=70
            )
            for i in range(3)
        ]
        result = check_promotion_eligibility(reports)
        assert result["eligible"] is False
        assert "older than 28 days" in result["reason"]


class TestGenerateComparisonReport:
    """Tests for report generation."""

    def test_schema_version_present(self):
        sp = _make_artifact_info()
        mr = _make_artifact_info()
        report = generate_comparison_report(
            week="2026-W24",
            single_pass=sp,
            map_reduce=mr,
            map_reduce_extra={},
            run_datetime="2026-06-14T07:00:00Z",
        )
        assert report["schema_version"] == COMPARISON_SCHEMA
        assert report["week"] == "2026-W24"

    def test_deltas_computed_correctly(self):
        sp = _make_artifact_info(quality_score=72, citation_count=14, word_count=1850)
        mr = _make_artifact_info(quality_score=68, citation_count=12, word_count=1720)
        report = generate_comparison_report(
            week="2026-W24",
            single_pass=sp,
            map_reduce=mr,
            map_reduce_extra={},
            run_datetime="2026-06-14T07:00:00Z",
        )
        assert report["deltas"]["quality_score"] == -4
        assert report["deltas"]["citation_count"] == -2
        assert report["deltas"]["word_count"] == -130

    def test_pass_verdict_when_criteria_met(self):
        sp = _make_artifact_info(quality_score=72, evidence_coverage=0.92)
        mr = _make_artifact_info(quality_score=68, evidence_coverage=0.88)
        report = generate_comparison_report(
            week="2026-W24",
            single_pass=sp,
            map_reduce=mr,
            map_reduce_extra={},
            run_datetime="2026-06-14T07:00:00Z",
        )
        assert report["verdict"] == "pass"
        assert report["blockers"] == []


class TestOperatorControls:
    """Tests for environment variable controls."""

    def test_default_values(self):
        assert PROMOTION_MIN_QUALITY == 60
        assert PROMOTION_MIN_COVERAGE == 0.85
        assert PROMOTION_HARD_FLOOR_QUALITY == 55
        assert PROMOTION_HARD_FLOOR_COVERAGE == 0.70
