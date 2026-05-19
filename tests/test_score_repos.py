"""Tests for scripts/score_repos.py scoring pipeline."""

from __future__ import annotations

import json
import math
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.score_repos import (
    compute_relevance_score,
    find_latest_raw_json,
    get_scoring_config,
    load_config,
    main,
    score_age,
    score_language,
    score_repos,
    score_stars,
    score_stars_gained,
    score_topics,
)


# --- Fixtures ---


@pytest.fixture
def scoring_config():
    """Default scoring config matching squadscope.topic.yml."""
    return {
        "min_stars": 20,
        "min_stars_gained": 10,
        "max_age_days": 365,
        "min_relevance_score": 40,
        "language_boost": {"Python": 1.2, "Jupyter Notebook": 1.1},
        "topic_relevance": [
            "machine-learning",
            "deep-learning",
            "artificial-intelligence",
            "neural-network",
            "llm",
            "transformers",
        ],
    }


@pytest.fixture
def sample_repo():
    """A typical high-quality AI/ML repo record."""
    return {
        "name": "awesome-ml",
        "owner": "researcher",
        "full_name": "researcher/awesome-ml",
        "description": "A machine learning framework",
        "language": "Python",
        "stars": 500,
        "forks": 50,
        "created_at": (datetime.now(UTC) - timedelta(days=30)).isoformat(),
        "topics": ["machine-learning", "deep-learning", "python"],
        "license": "MIT",
        "url": "https://github.com/researcher/awesome-ml",
        "stars_gained": 100,
    }


@pytest.fixture
def config_file(tmp_path):
    """Create a temporary config YAML file."""
    config = {
        "topic": {
            "id": "ai-ml",
            "name": "AI & ML",
            "description": "Test topic",
        },
        "queries": {"primary": ["topic:machine-learning"]},
        "scoring": {
            "min_stars": 20,
            "min_stars_gained": 10,
            "max_age_days": 365,
            "min_relevance_score": 40,
            "language_boost": {"Python": 1.2},
            "topic_relevance": ["machine-learning", "deep-learning"],
        },
    }
    path = tmp_path / "test_config.yml"
    import yaml

    path.write_text(yaml.dump(config), encoding="utf-8")
    return path


# --- Test score_stars ---


class TestScoreStars:
    def test_zero_stars(self):
        assert score_stars(0) == 0.0

    def test_negative_stars(self):
        assert score_stars(-5) == 0.0

    def test_low_stars(self):
        score = score_stars(10)
        assert 0 < score < 25

    def test_high_stars(self):
        score = score_stars(10000)
        assert score == 25.0

    def test_very_high_stars_capped(self):
        score = score_stars(1_000_000)
        assert score == 25.0

    def test_diminishing_returns(self):
        s10 = score_stars(10)
        s100 = score_stars(100)
        s1000 = score_stars(1000)
        # Log scale means equal absolute gains per 10x, but relative gains shrink
        assert s100 > s10
        assert s1000 > s100
        # Verify sublinear: doubling stars doesn't double score
        assert score_stars(200) < score_stars(100) * 2


# --- Test score_stars_gained ---


class TestScoreStarsGained:
    def test_zero_gained(self):
        assert score_stars_gained(0) == 0.0

    def test_negative_gained(self):
        assert score_stars_gained(-10) == 0.0

    def test_moderate_gained(self):
        score = score_stars_gained(50)
        assert 0 < score < 25

    def test_high_gained_capped(self):
        score = score_stars_gained(10000)
        assert score == 25.0


# --- Test score_language ---


class TestScoreLanguage:
    def test_no_language(self):
        assert score_language(None, {"Python": 1.2}) == 7.5

    def test_no_boost_config(self):
        assert score_language("Python", {}) == 7.5

    def test_matching_language_boost(self):
        score = score_language("Python", {"Python": 1.2})
        assert score == pytest.approx(9.0)

    def test_non_matching_language(self):
        score = score_language("Rust", {"Python": 1.2})
        assert score == 7.5

    def test_high_boost_capped(self):
        score = score_language("Python", {"Python": 3.0})
        assert score == 15.0


# --- Test score_topics ---


class TestScoreTopics:
    def test_no_repo_topics(self):
        assert score_topics([], ["machine-learning"]) == 0.0

    def test_no_relevance_list(self):
        assert score_topics(["python"], []) == 0.0

    def test_single_match(self):
        score = score_topics(["machine-learning"], ["machine-learning", "deep-learning", "llm"])
        assert score == pytest.approx(25.0 / 3)

    def test_full_match(self):
        topics = ["machine-learning", "deep-learning", "llm"]
        relevance = ["machine-learning", "deep-learning", "llm", "transformers"]
        score = score_topics(topics, relevance)
        assert score == 25.0  # 3 matches, capped at 3

    def test_case_insensitive(self):
        score = score_topics(["Machine-Learning"], ["machine-learning", "deep-learning", "llm"])
        assert score > 0

    def test_no_overlap(self):
        assert score_topics(["rust", "wasm"], ["machine-learning", "deep-learning", "llm"]) == 0.0


# --- Test score_age ---


class TestScoreAge:
    def test_no_created_at(self):
        assert score_age(None, 365) == 5.0

    def test_invalid_date(self):
        assert score_age("not-a-date", 365) == 5.0

    def test_brand_new_repo(self):
        now_iso = datetime.now(UTC).isoformat()
        score = score_age(now_iso, 365)
        assert score == pytest.approx(10.0, abs=0.1)

    def test_old_repo_at_max_age(self):
        old = (datetime.now(UTC) - timedelta(days=365)).isoformat()
        score = score_age(old, 365)
        assert score == pytest.approx(5.0, abs=0.1)

    def test_very_old_repo_penalized(self):
        ancient = (datetime.now(UTC) - timedelta(days=730)).isoformat()
        score = score_age(ancient, 365)
        assert score < 5.0

    def test_extremely_old_repo_zero(self):
        ancient = (datetime.now(UTC) - timedelta(days=1000)).isoformat()
        score = score_age(ancient, 365)
        assert score == pytest.approx(0.0, abs=0.5)


# --- Test compute_relevance_score ---


class TestComputeRelevanceScore:
    def test_high_quality_repo(self, sample_repo, scoring_config):
        score = compute_relevance_score(sample_repo, scoring_config)
        assert 60 <= score <= 100

    def test_low_quality_repo(self, scoring_config):
        repo = {
            "name": "old-thing",
            "stars": 5,
            "stars_gained": 0,
            "language": "Shell",
            "topics": [],
            "created_at": (datetime.now(UTC) - timedelta(days=800)).isoformat(),
        }
        score = compute_relevance_score(repo, scoring_config)
        assert score < 40

    def test_empty_repo(self, scoring_config):
        score = compute_relevance_score({}, scoring_config)
        assert 0 <= score <= 100

    def test_score_bounded(self, scoring_config):
        repo = {
            "stars": 1_000_000,
            "stars_gained": 100_000,
            "language": "Python",
            "topics": ["machine-learning", "deep-learning", "llm", "transformers"],
            "created_at": datetime.now(UTC).isoformat(),
        }
        score = compute_relevance_score(repo, scoring_config)
        assert score <= 100.0


# --- Test score_repos ---


class TestScoreRepos:
    def test_filters_below_threshold(self, scoring_config):
        repos = [
            {"name": "good", "stars": 500, "stars_gained": 100, "language": "Python",
             "topics": ["machine-learning", "deep-learning"], "created_at": datetime.now(UTC).isoformat()},
            {"name": "bad", "stars": 2, "stars_gained": 0, "language": "Shell",
             "topics": [], "created_at": (datetime.now(UTC) - timedelta(days=800)).isoformat()},
        ]
        scored = score_repos(repos, scoring_config)
        names = [r["name"] for r in scored]
        assert "good" in names
        assert "bad" not in names

    def test_sorted_descending(self, scoring_config):
        repos = [
            {"name": "medium", "stars": 100, "stars_gained": 20, "language": "Python",
             "topics": ["machine-learning"], "created_at": datetime.now(UTC).isoformat()},
            {"name": "high", "stars": 5000, "stars_gained": 500, "language": "Python",
             "topics": ["machine-learning", "deep-learning", "llm"], "created_at": datetime.now(UTC).isoformat()},
        ]
        scored = score_repos(repos, scoring_config)
        assert len(scored) >= 1
        if len(scored) >= 2:
            assert scored[0]["relevance_score"] >= scored[1]["relevance_score"]

    def test_adds_relevance_score_field(self, scoring_config):
        repos = [
            {"name": "test", "stars": 500, "stars_gained": 50, "language": "Python",
             "topics": ["machine-learning"], "created_at": datetime.now(UTC).isoformat()},
        ]
        scored = score_repos(repos, scoring_config)
        assert len(scored) > 0
        assert "relevance_score" in scored[0]
        assert isinstance(scored[0]["relevance_score"], float)

    def test_empty_input(self, scoring_config):
        assert score_repos([], scoring_config) == []


# --- Test load_config ---


class TestLoadConfig:
    def test_load_valid_config(self, config_file):
        config = load_config(config_file)
        assert "scoring" in config
        assert config["scoring"]["min_stars"] == 20

    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent.yml")


# --- Test get_scoring_config ---


class TestGetScoringConfig:
    def test_with_scoring_section(self):
        config = {"scoring": {"min_stars": 50, "language_boost": {"Go": 1.3}}}
        sc = get_scoring_config(config)
        assert sc["min_stars"] == 50
        assert sc["language_boost"] == {"Go": 1.3}

    def test_without_scoring_section(self):
        sc = get_scoring_config({})
        assert sc["min_stars"] == 20
        assert sc["min_relevance_score"] == 40


# --- Test find_latest_raw_json ---


class TestFindLatestRawJson:
    def test_no_directory(self):
        assert find_latest_raw_json("nonexistent-topic-xyz") is None

    def test_finds_latest(self, tmp_path, monkeypatch):
        topic_dir = tmp_path / "raw" / "test-topic"
        topic_dir.mkdir(parents=True)
        (topic_dir / "2026-W20.json").write_text("[]")
        (topic_dir / "2026-W21.json").write_text("[]")

        monkeypatch.setattr("scripts.score_repos.raw_dir", lambda tid: topic_dir)
        result = find_latest_raw_json("test-topic")
        assert result is not None
        assert "W21" in result.name


# --- Test CLI (main) ---


class TestMain:
    def test_with_input_file(self, tmp_path, config_file):
        repos = [
            {"name": "repo1", "stars": 500, "stars_gained": 100, "language": "Python",
             "topics": ["machine-learning", "deep-learning"], "created_at": datetime.now(UTC).isoformat()},
        ]
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(repos))
        output_file = tmp_path / "output.json"

        result = main(["--config", str(config_file), "--input", str(input_file),
                       "--output", str(output_file)])
        assert result == 0
        scored = json.loads(output_file.read_text())
        assert len(scored) == 1
        assert "relevance_score" in scored[0]

    def test_missing_input_file(self, config_file):
        result = main(["--config", str(config_file), "--input", "no_such_file.json"])
        assert result == 1

    def test_invalid_json_content(self, tmp_path, config_file):
        input_file = tmp_path / "bad.json"
        input_file.write_text('{"not": "a list"}')
        result = main(["--config", str(config_file), "--input", str(input_file)])
        assert result == 1

    def test_stdout_output(self, tmp_path, config_file, capsys):
        repos = [
            {"name": "repo1", "stars": 1000, "stars_gained": 200, "language": "Python",
             "topics": ["machine-learning", "llm"], "created_at": datetime.now(UTC).isoformat()},
        ]
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(repos))

        result = main(["--config", str(config_file), "--input", str(input_file)])
        assert result == 0
        output = capsys.readouterr().out
        parsed = json.loads(output)
        assert len(parsed) >= 1

    def test_no_input_no_raw_files(self, config_file):
        result = main(["--config", str(config_file), "--topic", "nonexistent-xyz-topic"])
        assert result == 1
