"""Tests for scripts/load_scorecard.py"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.load_scorecard import (
    format_scorecard_summary,
    load_scorecards,
    render_scorecard_section,
    scorecard_dir,
)


def _make_scorecard(
    week: str,
    topic: str = "ai-ml",
    validated: int = 5,
    correct: int = 3,
    incorrect: int = 2,
    by_type: dict | None = None,
) -> dict:
    return {
        "week": week,
        "topic": topic,
        "total_predictions": validated + 2,
        "validated": validated,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy": correct / validated if validated else 0,
        "by_type": by_type
        or {
            "rising_star": {"total": 3, "correct": 2},
            "declining_signal": {"total": 2, "correct": 1},
        },
        "details": [],
    }


@pytest.fixture
def scorecards_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a fake scorecards directory and patch metrics_dir."""
    topic = "ai-ml"
    sc_dir = tmp_path / "data" / "metrics" / topic / "scorecards"
    sc_dir.mkdir(parents=True)

    monkeypatch.setattr(
        "scripts.load_scorecard.metrics_dir",
        lambda topic_id=None: tmp_path / "data" / "metrics" / (topic_id or "general"),
    )

    return sc_dir


class TestScorecardDir:
    def test_returns_scorecards_subdir(self):
        path = scorecard_dir("ai-ml")
        assert path.name == "scorecards"
        assert "ai-ml" in str(path)

    def test_general_topic(self):
        path = scorecard_dir(None)
        assert "scorecards" in str(path)


class TestLoadScorecards:
    def test_empty_when_no_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "scripts.load_scorecard.metrics_dir", lambda topic_id=None: tmp_path / "nonexistent"
        )
        result = load_scorecards("ai-ml")
        assert result == []

    def test_loads_recent_scorecards(self, scorecards_dir: Path):
        for i, week in enumerate(["2026-W18", "2026-W19", "2026-W20", "2026-W21", "2026-W22"]):
            card = _make_scorecard(week, correct=i + 1, validated=5)
            (scorecards_dir / f"{week}-scorecard.json").write_text(json.dumps(card))

        cards = load_scorecards("ai-ml", count=4)
        assert len(cards) == 4
        assert cards[0]["week"] == "2026-W19"
        assert cards[-1]["week"] == "2026-W22"

    def test_loads_all_when_fewer_than_count(self, scorecards_dir: Path):
        card = _make_scorecard("2026-W21")
        (scorecards_dir / "2026-W21-scorecard.json").write_text(json.dumps(card))

        cards = load_scorecards("ai-ml", count=4)
        assert len(cards) == 1

    def test_skips_invalid_json(self, scorecards_dir: Path):
        (scorecards_dir / "2026-W20-scorecard.json").write_text("not json")
        card = _make_scorecard("2026-W21")
        (scorecards_dir / "2026-W21-scorecard.json").write_text(json.dumps(card))

        cards = load_scorecards("ai-ml", count=4)
        assert len(cards) == 1
        assert cards[0]["week"] == "2026-W21"


class TestFormatScorecardSummary:
    def test_empty_cards_returns_empty(self):
        assert format_scorecard_summary([]) == ""

    def test_zero_validated_returns_empty(self):
        card = _make_scorecard("2026-W21", validated=0, correct=0, incorrect=0)
        assert format_scorecard_summary([card]) == ""

    def test_single_card_summary(self):
        card = _make_scorecard("2026-W21", validated=5, correct=3, incorrect=2)
        result = format_scorecard_summary([card])

        assert "## Prediction Performance (last 1 week)" in result
        assert "Overall accuracy: 60% (3/5 correct)" in result
        assert "rising_star" in result
        assert "declining_signal" in result

    def test_multiple_cards_aggregate(self):
        cards = [
            _make_scorecard(
                "2026-W20",
                validated=5,
                correct=4,
                incorrect=1,
                by_type={
                    "rising_star": {"total": 3, "correct": 2},
                    "breakout": {"total": 2, "correct": 2},
                },
            ),
            _make_scorecard(
                "2026-W21",
                validated=5,
                correct=3,
                incorrect=2,
                by_type={
                    "rising_star": {"total": 3, "correct": 1},
                    "breakout": {"total": 2, "correct": 2},
                },
            ),
        ]
        result = format_scorecard_summary(cards)

        assert "last 2 weeks" in result
        assert "70% (7/10 correct)" in result
        # rising_star: 3/6 = 50%
        assert '"rising_star" predictions: 50%' in result
        # breakout: 4/4 = 100%
        assert '"breakout" predictions: 100%' in result

    def test_recommendations_for_low_accuracy(self):
        cards = [
            _make_scorecard(
                "2026-W21",
                validated=10,
                correct=3,
                incorrect=7,
                by_type={"rising_star": {"total": 10, "correct": 3}},
            ),
        ]
        result = format_scorecard_summary(cards)
        assert "raise confidence threshold" in result

    def test_recommendations_for_high_accuracy(self):
        cards = [
            _make_scorecard(
                "2026-W21",
                validated=10,
                correct=9,
                incorrect=1,
                by_type={"declining_signal": {"total": 10, "correct": 9}},
            ),
        ]
        result = format_scorecard_summary(cards)
        assert "reliable" in result


class TestRenderScorecardSection:
    def test_returns_empty_when_no_scorecards(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(
            "scripts.load_scorecard.metrics_dir", lambda topic_id=None: tmp_path / "nonexistent"
        )
        result = render_scorecard_section("ai-ml")
        assert result == ""

    def test_returns_formatted_summary(self, scorecards_dir: Path):
        card = _make_scorecard("2026-W21", validated=5, correct=4, incorrect=1)
        (scorecards_dir / "2026-W21-scorecard.json").write_text(json.dumps(card))

        result = render_scorecard_section("ai-ml")
        assert "Prediction Performance" in result
        assert "80%" in result
