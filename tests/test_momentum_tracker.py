"""Tests for momentum_tracker and calibrate_hype_risk."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from momentum_tracker import (  # noqa: E402
    classify_momentum,
    compute_decay_rate,
    current_iso_week,
    extract_correlated_repos,
    find_correlation_file,
    get_repo_stars_gained,
    iso_week_to_date,
    load_json_safe,
    run_momentum_tracking,
    track_repo_momentum,
    update_predictions_validated,
    week_offset,
)
from calibrate_hype_risk import (  # noqa: E402
    build_actual_outcomes,
    build_predictions,
    compute_calibration,
    generate_recommendations,
    risk_to_expected_outcome,
    run_calibration,
)


# ---------------------------------------------------------------------------
# momentum_tracker tests
# ---------------------------------------------------------------------------


class TestWeekUtils:
    """Test ISO week utility functions."""

    def test_current_iso_week_format(self):
        """current_iso_week returns YYYY-WNN format."""
        week = current_iso_week()
        assert len(week) >= 7
        assert "-W" in week

    def test_week_offset_forward(self):
        """week_offset moves forward correctly."""
        assert week_offset("2026-W21", 2) == "2026-W23"

    def test_week_offset_backward(self):
        """week_offset moves backward correctly."""
        assert week_offset("2026-W03", -2) == "2026-W01"

    def test_week_offset_year_boundary(self):
        """week_offset crosses year boundary."""
        result = week_offset("2025-W52", 2)
        assert result.startswith("2026-W")

    def test_iso_week_to_date(self):
        """iso_week_to_date returns correct Monday."""
        dt = iso_week_to_date("2026-W01")
        assert dt.weekday() == 0  # Monday


class TestClassifyMomentum:
    """Test momentum classification logic."""

    def test_sustained_strong_growth(self):
        """Still gaining 20%+ of initial → sustained."""
        assert classify_momentum(100, 50, 30, lag=4) == "sustained"

    def test_faded_no_growth(self):
        """Zero growth at checkpoints → faded."""
        assert classify_momentum(100, 5, 3, lag=4) == "faded"

    def test_faded_zero_initial(self):
        """Zero initial gained → faded."""
        assert classify_momentum(0, 10, 5, lag=4) == "faded"

    def test_sustained_week2_only(self):
        """With lag=2, only week2 data used."""
        assert classify_momentum(100, 30, None, lag=2) == "sustained"

    def test_faded_no_data(self):
        """No follow-up data → faded (conservative)."""
        assert classify_momentum(100, None, None, lag=4) == "faded"

    def test_sustained_at_threshold(self):
        """Exactly 20% of initial → sustained."""
        assert classify_momentum(100, 20, 20, lag=4) == "sustained"

    def test_faded_below_threshold(self):
        """Just below 20% → faded."""
        assert classify_momentum(100, 19, 19, lag=4) == "faded"


class TestDecayRate:
    """Test decay rate computation."""

    def test_no_decay(self):
        assert compute_decay_rate(100, 100) == 0.0

    def test_full_decay(self):
        assert compute_decay_rate(100, 0) == 1.0

    def test_partial_decay(self):
        assert compute_decay_rate(100, 50) == 0.5

    def test_zero_initial(self):
        assert compute_decay_rate(0, 50) == 0.0

    def test_negative_clamped(self):
        assert compute_decay_rate(100, 150) == 0.0


class TestExtractCorrelatedRepos:
    """Test extraction from correlation data."""

    def test_extracts_correlated(self):
        data = {
            "correlations": [
                {"repo": "org/a", "press_correlated": True},
                {"repo": "org/b", "press_correlated": False},
                {"repo": "org/c", "press_correlated": True},
            ]
        }
        result = extract_correlated_repos(data)
        assert len(result) == 2
        assert result[0]["repo"] == "org/a"
        assert result[1]["repo"] == "org/c"

    def test_empty_correlations(self):
        assert extract_correlated_repos({"correlations": []}) == []


class TestGetRepoStarsGained:
    """Test star extraction from raw data."""

    def test_from_repos_key(self):
        data = {"repos": [{"full_name": "org/x", "stars_gained": 42}]}
        assert get_repo_stars_gained(data, "org/x") == 42

    def test_missing_repo(self):
        data = {"repos": [{"full_name": "org/x", "stars_gained": 42}]}
        assert get_repo_stars_gained(data, "org/y") is None

    def test_none_data(self):
        assert get_repo_stars_gained(None, "org/x") is None


class TestTrackRepoMomentum:
    """Test single repo momentum tracking."""

    def test_with_data(self, tmp_path):
        w2_data = {"repos": [{"full_name": "org/x", "stars_gained": 50}]}
        (tmp_path / "2026-W23.json").write_text(json.dumps(w2_data))
        w4_data = {"repos": [{"full_name": "org/x", "stars_gained": 30}]}
        (tmp_path / "2026-W25.json").write_text(json.dumps(w4_data))

        result = track_repo_momentum("org/x", 200, tmp_path, "2026-W21", lag=4)
        assert result["repo"] == "org/x"
        assert result["initial_stars_gained"] == 200
        assert result["week2_stars_gained"] == 50
        assert result["week4_stars_gained"] == 30
        assert result["classification"] == "faded"
        assert result["decay_rate"] > 0

    def test_missing_weeks(self, tmp_path):
        result = track_repo_momentum("org/x", 100, tmp_path, "2026-W21", lag=4)
        assert result["week2_stars_gained"] is None
        assert result["week4_stars_gained"] is None
        assert result["classification"] == "faded"


class TestUpdatePredictions:
    """Test predictions.jsonl update."""

    def test_updates_matching(self, tmp_path):
        preds = [
            {"repo": "org/a", "prediction": "rising_star", "week": "2026-W20"},
            {"repo": "org/b", "prediction": "rising_star", "week": "2026-W20"},
        ]
        pred_path = tmp_path / "predictions.jsonl"
        pred_path.write_text("\n".join(json.dumps(p) for p in preds) + "\n")

        tracked = [
            {"repo": "org/a", "classification": "sustained"},
            {"repo": "org/b", "classification": "faded"},
        ]
        updated = update_predictions_validated(pred_path, tracked)
        assert updated == 2

        lines = pred_path.read_text().strip().split("\n")
        result = [json.loads(line) for line in lines]
        assert result[0]["validated"] is True
        assert result[1]["validated"] is False

    def test_skips_already_validated(self, tmp_path):
        preds = [{"repo": "org/a", "validated": True, "week": "2026-W20"}]
        pred_path = tmp_path / "predictions.jsonl"
        pred_path.write_text(json.dumps(preds[0]) + "\n")

        tracked = [{"repo": "org/a", "classification": "faded"}]
        updated = update_predictions_validated(pred_path, tracked)
        assert updated == 0

    def test_missing_file(self, tmp_path):
        updated = update_predictions_validated(tmp_path / "nope.jsonl", [])
        assert updated == 0


class TestRunMomentumTracking:
    """Integration test for full tracking run."""

    def test_no_correlations(self, tmp_path, monkeypatch):
        import scripts.topic_paths as tp

        monkeypatch.setattr(tp, "DATA_ROOT", tmp_path / "data")
        (tmp_path / "data" / "raw").mkdir(parents=True)
        (tmp_path / "data" / "analyzed").mkdir(parents=True)
        (tmp_path / "data" / "metrics").mkdir(parents=True)

        result = run_momentum_tracking(topic_id=None, week="2026-W21", lag=4)
        assert result["week"] == "2026-W21"
        assert result["tracked_repos"] == []
        assert result["summary"]["total"] == 0


# ---------------------------------------------------------------------------
# calibrate_hype_risk tests
# ---------------------------------------------------------------------------


class TestBuildActualOutcomes:
    """Test outcome extraction from momentum data."""

    def test_extracts_outcomes(self):
        data = [
            {
                "tracked_repos": [
                    {"repo": "org/a", "classification": "sustained"},
                    {"repo": "org/b", "classification": "faded"},
                ]
            }
        ]
        outcomes = build_actual_outcomes(data)
        assert outcomes["org/a"] == "sustained"
        assert outcomes["org/b"] == "faded"

    def test_latest_wins(self):
        data = [
            {"tracked_repos": [{"repo": "org/a", "classification": "faded"}]},
            {"tracked_repos": [{"repo": "org/a", "classification": "sustained"}]},
        ]
        outcomes = build_actual_outcomes(data)
        assert outcomes["org/a"] == "sustained"


class TestBuildPredictions:
    """Test prediction extraction from hype risk data."""

    def test_extracts_risks(self):
        data = [
            {
                "assessments": [
                    {"repo": "org/a", "hype_risk": "high"},
                    {"repo": "org/b", "hype_risk": "low"},
                ]
            }
        ]
        preds = build_predictions(data)
        assert preds["org/a"] == "high"
        assert preds["org/b"] == "low"


class TestRiskToExpectedOutcome:
    """Test risk level to outcome mapping."""

    def test_high_expects_faded(self):
        assert risk_to_expected_outcome("high") == "faded"

    def test_low_expects_sustained(self):
        assert risk_to_expected_outcome("low") == "sustained"

    def test_very_low_expects_sustained(self):
        assert risk_to_expected_outcome("very_low") == "sustained"

    def test_medium_uncertain(self):
        assert risk_to_expected_outcome("medium") is None

    def test_none_uncertain(self):
        assert risk_to_expected_outcome("none") is None


class TestComputeCalibration:
    """Test calibration computation."""

    def test_perfect_accuracy(self):
        predictions = {"org/a": "high", "org/b": "low"}
        actuals = {"org/a": "faded", "org/b": "sustained"}
        result = compute_calibration(predictions, actuals)
        assert result["samples"] == 2
        assert result["accuracy_by_category"]["high"]["accuracy"] == 1.0
        assert result["accuracy_by_category"]["low"]["accuracy"] == 1.0

    def test_partial_accuracy(self):
        predictions = {"org/a": "high", "org/b": "high"}
        actuals = {"org/a": "faded", "org/b": "sustained"}
        result = compute_calibration(predictions, actuals)
        assert result["samples"] == 2
        assert result["accuracy_by_category"]["high"]["correct"] == 1
        assert result["accuracy_by_category"]["high"]["predicted"] == 2

    def test_no_overlap(self):
        predictions = {"org/a": "high"}
        actuals = {"org/z": "faded"}
        result = compute_calibration(predictions, actuals)
        assert result["samples"] == 0


class TestGenerateRecommendations:
    """Test recommendation generation."""

    def test_low_high_accuracy_triggers_adjustment(self):
        calibration = {
            "accuracy_by_category": {
                "high": {"predicted": 10, "correct": 5, "accuracy": 0.5}
            }
        }
        actuals = {"org/a": "sustained", "org/b": "faded"}
        recs = generate_recommendations(calibration, actuals)
        params = [r["parameter"] for r in recs]
        assert "high_risk_decay_threshold" in params

    def test_good_accuracy_no_changes(self):
        calibration = {
            "accuracy_by_category": {
                "high": {"predicted": 10, "correct": 9, "accuracy": 0.9},
                "low": {"predicted": 10, "correct": 9, "accuracy": 0.9},
            }
        }
        actuals = {"org/a": "sustained", "org/b": "faded"}
        recs = generate_recommendations(calibration, actuals)
        params = [r["parameter"] for r in recs]
        assert "no_changes" in params


class TestRunCalibration:
    """Integration test for calibration."""

    def test_no_data(self, tmp_path, monkeypatch):
        import scripts.topic_paths as tp

        monkeypatch.setattr(tp, "DATA_ROOT", tmp_path / "data")
        (tmp_path / "data" / "metrics").mkdir(parents=True)
        (tmp_path / "data" / "analyzed").mkdir(parents=True)

        result = run_calibration(topic_id=None, output_path=str(tmp_path / "out.json"))
        assert result["samples"] == 0
        assert result["recommended_adjustments"] == []
