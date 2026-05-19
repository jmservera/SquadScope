"""Tests for scripts/hindsight_validation.py"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from scripts.hindsight_validation import (
    build_repo_set,
    build_repo_stars,
    current_iso_week,
    generate_scorecard,
    is_old_enough,
    iso_week_to_date,
    load_predictions,
    run_validation,
    save_predictions,
    validate_breakout_candidate,
    validate_declining_signal,
    validate_momentum_shift,
    validate_prediction,
    validate_rising_star,
    week_offset,
)


def _old_week(weeks_back: int = 5) -> str:
    """Return a week string N weeks in the past."""
    dt = datetime.now() - timedelta(weeks=weeks_back)
    cal = dt.isocalendar()
    return f"{cal[0]}-W{cal[1]:02d}"


def _make_raw_data(repos: list[dict[str, Any]], section: str = "trending_repos") -> dict[str, Any]:
    return {section: repos, "new_repos": [] if section != "new_repos" else repos,
            "trending_repos": [] if section != "trending_repos" else repos}


def _write_raw(raw_dir: Path, week: str, data: dict[str, Any]) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    with open(raw_dir / f"{week}.json", "w") as f:
        json.dump(data, f)


def _write_predictions(metrics_dir: Path, predictions: list[dict[str, Any]]) -> None:
    metrics_dir.mkdir(parents=True, exist_ok=True)
    with open(metrics_dir / "predictions.jsonl", "w") as f:
        for p in predictions:
            f.write(json.dumps(p) + "\n")


class TestIsoWeekConversion:
    def test_round_trip(self):
        week = "2026-W21"
        dt = iso_week_to_date(week)
        assert dt.year == 2026

    def test_week_offset_forward(self):
        result = week_offset("2026-W10", 4)
        assert result == "2026-W14"

    def test_week_offset_backward(self):
        result = week_offset("2026-W10", -2)
        assert result == "2026-W08"

    def test_current_iso_week_format(self):
        week = current_iso_week()
        assert len(week.split("-W")) == 2


class TestLoadSavePredictions:
    def test_load_missing_file(self, tmp_path: Path):
        result = load_predictions(tmp_path / "nonexistent.jsonl")
        assert result == []

    def test_round_trip(self, tmp_path: Path):
        preds = [
            {"week": "2026-W21", "repo": "org/a", "prediction": "rising_star",
             "confidence": 0.7, "reason": "test", "validated": None},
        ]
        path = tmp_path / "predictions.jsonl"
        save_predictions(preds, path)
        loaded = load_predictions(path)
        assert loaded == preds

    def test_empty_lines_ignored(self, tmp_path: Path):
        path = tmp_path / "predictions.jsonl"
        path.write_text('{"week":"2026-W01","repo":"x/y","prediction":"rising_star","confidence":0.5,"reason":"r","validated":null}\n\n')
        loaded = load_predictions(path)
        assert len(loaded) == 1


class TestBuildRepoHelpers:
    def test_build_repo_stars(self):
        raw = {"trending_repos": [{"full_name": "a/b", "stars": 100}], "new_repos": []}
        assert build_repo_stars(raw) == {"a/b": 100}

    def test_build_repo_set(self):
        raw = {"trending_repos": [{"full_name": "a/b", "stars": 100}],
               "new_repos": [{"full_name": "c/d", "stars": 50}]}
        assert build_repo_set(raw) == {"a/b", "c/d"}


class TestValidateRisingStar:
    def test_growth_above_threshold(self, tmp_path: Path):
        pred_week = _old_week(5)
        later_week = week_offset(pred_week, 4)
        _write_raw(tmp_path, later_week, _make_raw_data(
            [{"full_name": "org/repo", "stars": 150}]))
        result = validate_rising_star("org/repo", 100, tmp_path, pred_week, 4)
        assert result is True  # 50% growth >= 20%

    def test_growth_below_threshold(self, tmp_path: Path):
        pred_week = _old_week(5)
        later_week = week_offset(pred_week, 4)
        _write_raw(tmp_path, later_week, _make_raw_data(
            [{"full_name": "org/repo", "stars": 110}]))
        result = validate_rising_star("org/repo", 100, tmp_path, pred_week, 4)
        assert result is False

    def test_no_data_returns_none(self, tmp_path: Path):
        pred_week = _old_week(5)
        result = validate_rising_star("org/repo", 100, tmp_path, pred_week, 4)
        assert result is None

    def test_zero_stars_baseline(self, tmp_path: Path):
        pred_week = _old_week(5)
        later_week = week_offset(pred_week, 4)
        _write_raw(tmp_path, later_week, _make_raw_data(
            [{"full_name": "org/repo", "stars": 10}]))
        result = validate_rising_star("org/repo", 0, tmp_path, pred_week, 4)
        assert result is True


class TestValidateBreakoutCandidate:
    def test_found_in_trending(self, tmp_path: Path):
        pred_week = _old_week(5)
        w2 = week_offset(pred_week, 2)
        _write_raw(tmp_path, w2, _make_raw_data(
            [{"full_name": "org/repo", "stars": 200}], "trending_repos"))
        result = validate_breakout_candidate("org/repo", tmp_path, pred_week, 4)
        assert result is True

    def test_not_found(self, tmp_path: Path):
        pred_week = _old_week(5)
        w1 = week_offset(pred_week, 1)
        _write_raw(tmp_path, w1, _make_raw_data(
            [{"full_name": "other/repo", "stars": 200}], "trending_repos"))
        result = validate_breakout_candidate("org/repo", tmp_path, pred_week, 4)
        assert result is False


class TestValidateMomentumShift:
    def test_continued_growth(self, tmp_path: Path):
        pred_week = _old_week(5)
        w2 = week_offset(pred_week, 2)
        _write_raw(tmp_path, w2, _make_raw_data(
            [{"full_name": "org/repo", "stars": 1200}]))
        result = validate_momentum_shift("org/repo", 1000, tmp_path, pred_week, 4)
        assert result is True

    def test_declined(self, tmp_path: Path):
        pred_week = _old_week(5)
        w2 = week_offset(pred_week, 2)
        _write_raw(tmp_path, w2, _make_raw_data(
            [{"full_name": "org/repo", "stars": 800}]))
        result = validate_momentum_shift("org/repo", 1000, tmp_path, pred_week, 4)
        assert result is False

    def test_no_data(self, tmp_path: Path):
        pred_week = _old_week(5)
        result = validate_momentum_shift("org/repo", 1000, tmp_path, pred_week, 4)
        assert result is None


class TestValidateDecliningSignal:
    def test_repo_disappeared(self, tmp_path: Path):
        pred_week = _old_week(5)
        for i in range(1, 5):
            w = week_offset(pred_week, i)
            _write_raw(tmp_path, w, _make_raw_data(
                [{"full_name": "other/repo", "stars": 50}]))
        result = validate_declining_signal("org/repo", tmp_path, pred_week, 4)
        assert result is True

    def test_repo_still_present(self, tmp_path: Path):
        pred_week = _old_week(5)
        for i in range(1, 5):
            w = week_offset(pred_week, i)
            _write_raw(tmp_path, w, _make_raw_data(
                [{"full_name": "org/repo", "stars": 50}]))
        result = validate_declining_signal("org/repo", tmp_path, pred_week, 4)
        assert result is False

    def test_no_data(self, tmp_path: Path):
        pred_week = _old_week(5)
        result = validate_declining_signal("org/repo", tmp_path, pred_week, 4)
        assert result is None


class TestIsOldEnough:
    def test_old_prediction(self):
        week = _old_week(6)
        assert is_old_enough(week, 4) is True

    def test_recent_prediction(self):
        week = current_iso_week()
        assert is_old_enough(week, 4) is False

    def test_invalid_week(self):
        assert is_old_enough("", 4) is False
        assert is_old_enough("not-a-week", 4) is False


class TestGenerateScorecard:
    def test_empty(self):
        sc = generate_scorecard([])
        assert sc["total_validated"] == 0
        assert sc["accuracy"] == 0.0

    def test_mixed_results(self):
        preds = [
            {"prediction": "rising_star", "validated": True},
            {"prediction": "rising_star", "validated": False},
            {"prediction": "momentum_shift", "validated": True},
            {"prediction": "rising_star", "validated": None},  # not counted
        ]
        sc = generate_scorecard(preds)
        assert sc["total_validated"] == 3
        assert sc["correct"] == 2
        assert sc["incorrect"] == 1
        assert sc["accuracy"] == pytest.approx(2 / 3, abs=0.001)
        assert sc["by_type"]["rising_star"]["total"] == 2
        assert sc["by_type"]["rising_star"]["correct"] == 1
        assert sc["by_type"]["momentum_shift"]["total"] == 1


class TestValidatePrediction:
    def test_unknown_type(self, tmp_path: Path):
        pred = {"week": _old_week(5), "repo": "org/repo", "prediction": "unknown_type"}
        result = validate_prediction(pred, tmp_path, 4)
        assert result is None

    def test_missing_repo(self, tmp_path: Path):
        pred = {"week": _old_week(5), "repo": "", "prediction": "rising_star"}
        result = validate_prediction(pred, tmp_path, 4)
        assert result is None

    def test_emerging_topic_uses_declining_logic(self, tmp_path: Path):
        pred_week = _old_week(5)
        pred = {"week": pred_week, "repo": "org/repo", "prediction": "emerging_topic"}
        for i in range(1, 5):
            w = week_offset(pred_week, i)
            _write_raw(tmp_path, w, _make_raw_data(
                [{"full_name": "other/repo", "stars": 50}]))
        result = validate_prediction(pred, tmp_path, 4)
        assert result is True


class TestRunValidation:
    def test_full_run(self, tmp_path: Path):
        pred_week = _old_week(5)
        raw = tmp_path / "raw"
        metrics = tmp_path / "metrics"

        # Write prediction-week raw data
        _write_raw(raw, pred_week, _make_raw_data(
            [{"full_name": "org/star", "stars": 100}]))

        # Write later-week raw data with growth
        later = week_offset(pred_week, 4)
        _write_raw(raw, later, _make_raw_data(
            [{"full_name": "org/star", "stars": 200}]))

        # Write predictions
        preds = [
            {"week": pred_week, "repo": "org/star", "prediction": "rising_star",
             "confidence": 0.7, "reason": "test", "validated": None},
        ]
        _write_predictions(metrics, preds)

        scorecard = run_validation(topic_id=None, weeks_ago=4, data_dir=str(tmp_path))

        assert scorecard["total_validated"] == 1
        assert scorecard["correct"] == 1
        assert scorecard["accuracy"] == 1.0

        # Check predictions file was updated
        updated = load_predictions(metrics / "predictions.jsonl")
        assert updated[0]["validated"] is True

        # Check scorecard file was written
        scorecards = list((metrics / "scorecards").glob("*-scorecard.json"))
        assert len(scorecards) == 1

    def test_skips_recent_predictions(self, tmp_path: Path):
        raw = tmp_path / "raw"
        metrics = tmp_path / "metrics"
        raw.mkdir(parents=True, exist_ok=True)

        recent_week = current_iso_week()
        preds = [
            {"week": recent_week, "repo": "org/new", "prediction": "rising_star",
             "confidence": 0.7, "reason": "too new", "validated": None},
        ]
        _write_predictions(metrics, preds)

        scorecard = run_validation(topic_id=None, weeks_ago=4, data_dir=str(tmp_path))
        assert scorecard["total_validated"] == 0

        # Prediction should remain unvalidated
        updated = load_predictions(metrics / "predictions.jsonl")
        assert updated[0]["validated"] is None

    def test_empty_predictions(self, tmp_path: Path):
        metrics = tmp_path / "metrics"
        metrics.mkdir(parents=True, exist_ok=True)
        scorecard = run_validation(topic_id=None, weeks_ago=4, data_dir=str(tmp_path))
        assert scorecard["total_validated"] == 0

    def test_topic_path_resolution(self, tmp_path: Path):
        pred_week = _old_week(5)
        topic = "ai-ml"
        raw = tmp_path / "raw" / topic
        metrics = tmp_path / "metrics" / topic

        _write_raw(raw, pred_week, _make_raw_data(
            [{"full_name": "org/ai", "stars": 100}]))
        later = week_offset(pred_week, 4)
        _write_raw(raw, later, _make_raw_data(
            [{"full_name": "org/ai", "stars": 130}]))

        preds = [
            {"week": pred_week, "repo": "org/ai", "prediction": "rising_star",
             "confidence": 0.6, "reason": "test", "validated": None},
        ]
        _write_predictions(metrics, preds)

        scorecard = run_validation(topic_id=topic, weeks_ago=4, data_dir=str(tmp_path))
        assert scorecard["total_validated"] == 1
        # 30% growth >= 20% threshold
        assert scorecard["correct"] == 1

    def test_already_validated_skipped(self, tmp_path: Path):
        raw = tmp_path / "raw"
        metrics = tmp_path / "metrics"
        raw.mkdir(parents=True, exist_ok=True)

        pred_week = _old_week(5)
        preds = [
            {"week": pred_week, "repo": "org/done", "prediction": "rising_star",
             "confidence": 0.7, "reason": "already done", "validated": True},
        ]
        _write_predictions(metrics, preds)

        scorecard = run_validation(topic_id=None, weeks_ago=4, data_dir=str(tmp_path))
        # Already validated, so it counts in scorecard but wasn't re-processed
        assert scorecard["total_validated"] == 1
        assert scorecard["correct"] == 1
