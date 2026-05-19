"""Tests for hype_risk scoring model."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from hype_risk import classify_repo, extract_week, score_hype_risk  # noqa: E402


class TestClassifyRepo:
    """Test individual repo classification paths."""

    def test_no_press_correlation(self):
        """Not press_correlated → risk = 'none'."""
        result = classify_repo("org/repo", press_correlated=False)
        assert result["hype_risk"] == "none"
        assert result["label"] == "No press signal"
        assert result["press_correlated"] is False

    def test_press_correlated_no_previous_data(self):
        """Press correlated but no previous data → risk = 'medium'."""
        result = classify_repo(
            "org/repo",
            press_correlated=True,
            current_stars=1000,
            current_stars_gained=200,
            previous_stars=None,
            previous_stars_gained=None,
        )
        assert result["hype_risk"] == "medium"
        assert result["press_correlated"] is True
        assert result["confidence"] < 0.6

    def test_organic_growth_before_press(self):
        """Stars already growing before press → risk = 'very_low'."""
        result = classify_repo(
            "org/repo",
            press_correlated=True,
            current_stars=2000,
            current_stars_gained=100,
            previous_stars=1900,
            previous_stars_gained=80,  # Already had strong growth
        )
        assert result["hype_risk"] == "very_low"
        assert result["label"] == "Organic growth"
        assert result["stars_trend"] == "organic"

    def test_sustained_growth_after_press(self):
        """Stars spike after article and sustain → risk = 'low'."""
        result = classify_repo(
            "org/repo",
            press_correlated=True,
            current_stars=5000,
            current_stars_gained=500,
            previous_stars=4500,
            previous_stars_gained=100,  # Small growth before, big growth now
        )
        assert result["hype_risk"] == "low"
        assert result["label"] == "Press-validated, community-sustained"
        assert result["stars_trend"] == "sustained"

    def test_decaying_growth_after_press(self):
        """Stars spiked but now fading → risk = 'high'."""
        result = classify_repo(
            "org/repo",
            press_correlated=True,
            current_stars=5000,
            current_stars_gained=50,  # Much lower than previous
            previous_stars=4950,
            previous_stars_gained=500,  # Big spike last week
        )
        assert result["hype_risk"] == "high"
        assert result["label"] == "Press-driven hype, fading"
        assert result["stars_trend"] == "decaying"

    def test_press_correlated_no_activity_spike(self):
        """Press coverage but no GitHub activity spike → risk = 'medium'."""
        result = classify_repo(
            "org/repo",
            press_correlated=True,
            current_stars=100,
            current_stars_gained=0,
            previous_stars=100,
            previous_stars_gained=0,
        )
        assert result["hype_risk"] == "medium"
        assert result["label"] == "Announced but unbuilt"

    def test_assessment_has_all_fields(self):
        """Every assessment should have all required fields."""
        result = classify_repo("org/repo", press_correlated=False)
        assert "repo" in result
        assert "hype_risk" in result
        assert "label" in result
        assert "press_correlated" in result
        assert "stars_trend" in result
        assert "confidence" in result
        assert "reasoning" in result


class TestScoreHypeRisk:
    """Test the batch scoring function."""

    def test_empty_correlations(self):
        result = score_hype_risk({"correlations": []}, None, None)
        assert result == []

    def test_scores_correlated_repos(self):
        correlations = {
            "correlations": [
                {"repo": "org/alpha", "press_correlated": True},
                {"repo": "org/beta", "press_correlated": False},
            ]
        }
        raw_data = [
            {"full_name": "org/alpha", "stars": 1000, "stars_gained": 200},
            {"full_name": "org/beta", "stars": 500, "stars_gained": 10},
        ]
        result = score_hype_risk(correlations, raw_data, None)
        assert len(result) == 2

        alpha = next(a for a in result if a["repo"] == "org/alpha")
        beta = next(a for a in result if a["repo"] == "org/beta")

        assert alpha["hype_risk"] == "medium"  # correlated, no previous
        assert beta["hype_risk"] == "none"  # not correlated

    def test_with_previous_data(self):
        correlations = {
            "correlations": [
                {"repo": "org/sustained", "press_correlated": True},
            ]
        }
        raw_data = [
            {"full_name": "org/sustained", "stars": 3000, "stars_gained": 400},
        ]
        previous_data = [
            {"full_name": "org/sustained", "stars": 2600, "stars_gained": 50},
        ]
        result = score_hype_risk(correlations, raw_data, previous_data)
        sustained = next(a for a in result if a["repo"] == "org/sustained")
        assert sustained["hype_risk"] == "low"

    def test_raw_data_wrapped_in_dict(self):
        """Raw data may be wrapped in a dict with 'repos' key."""
        correlations = {"correlations": [{"repo": "x/y", "press_correlated": False}]}
        raw_data = {"repos": [{"full_name": "x/y", "stars": 10, "stars_gained": 1}]}
        result = score_hype_risk(correlations, raw_data, None)
        assert len(result) == 1
        assert result[0]["hype_risk"] == "none"


class TestExtractWeek:
    def test_simple_week(self):
        assert extract_week("data/raw/ai-ml/2026-W21.json") == "2026-W21"

    def test_correlations_suffix(self):
        assert extract_week("data/analyzed/ai-ml/2026-W21-correlations.json") == "2026-W21"

    def test_none_path(self):
        assert extract_week(None) == "unknown"


class TestCLI:
    """Test CLI main function."""

    def test_main_with_files(self, tmp_path):
        from hype_risk import main

        corr_file = tmp_path / "correlations.json"
        raw_file = tmp_path / "2026-W21.json"
        out_file = tmp_path / "output.json"

        corr_file.write_text(json.dumps({
            "correlations": [{"repo": "org/repo", "press_correlated": True}]
        }))
        raw_file.write_text(json.dumps([
            {"full_name": "org/repo", "stars": 500, "stars_gained": 100}
        ]))

        main([
            "--correlations", str(corr_file),
            "--raw", str(raw_file),
            "--output", str(out_file),
        ])

        output = json.loads(out_file.read_text())
        assert output["week"] == "2026-W21"
        assert len(output["assessments"]) == 1
        assert output["assessments"][0]["repo"] == "org/repo"
