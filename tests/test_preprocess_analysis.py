"""Tests for scripts/preprocess_for_analysis.py."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys_path_fix = True  # noqa: E402
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.preprocess_for_analysis import (
    compact_repo,
    compute_age_days,
    compute_signals,
    estimate_tokens,
    preprocess,
    main,
)


class TestEstimateTokens:
    def test_basic(self):
        assert estimate_tokens("abcd") == 1
        assert estimate_tokens("a" * 400) == 100

    def test_empty(self):
        assert estimate_tokens("") == 0


class TestComputeAgeDays:
    def test_valid_date(self):
        ref = datetime(2026, 5, 20, tzinfo=timezone.utc)
        assert compute_age_days("2026-05-10T00:00:00Z", ref) == 10

    def test_none(self):
        assert compute_age_days(None) is None

    def test_invalid(self):
        assert compute_age_days("not-a-date") is None


class TestCompactRepo:
    def test_extracts_needed_fields(self):
        repo = {
            "name": "test-repo",
            "owner": "someone",
            "full_name": "someone/test-repo",
            "description": "A very long description " * 20,
            "language": "Python",
            "stars": 500,
            "forks": 100,
            "created_at": "2026-05-01T00:00:00Z",
            "topics": ["ml", "ai"],
            "license": "MIT",
            "url": "https://github.com/someone/test-repo",
        }
        ref = datetime(2026, 5, 20, tzinfo=timezone.utc)
        result = compact_repo(repo, max_desc=200, reference_date=ref)

        assert result["name"] == "test-repo"
        assert len(result["desc"]) <= 200
        assert result["stars"] == 500
        assert result["topics"] == ["ml", "ai"]
        assert result["lang"] == "Python"
        assert result["age_days"] == 19
        # Removed fields should not be present
        assert "owner" not in result
        assert "full_name" not in result
        assert "forks" not in result
        assert "license" not in result
        assert "url" not in result

    def test_handles_missing_fields(self):
        result = compact_repo({}, max_desc=200)
        assert result["name"] == ""
        assert result["desc"] == ""
        assert result["stars"] == 0


class TestComputeSignals:
    def test_top_topics(self):
        repos = [
            {"topics": ["ml", "python"]},
            {"topics": ["ml", "ai"]},
            {"topics": ["python"]},
        ]
        signals = compute_signals(repos)
        # ml and python appear twice each
        assert "ml" in signals["top_topics"]
        assert "python" in signals["top_topics"]


class TestPreprocess:
    def test_reduction_in_expected_range(self):
        """Token reduction should be 40-60% for typical data."""
        # Build a realistic raw JSON
        repos = []
        for i in range(50):
            repos.append({
                "name": f"repo-{i}",
                "owner": f"owner-{i}",
                "full_name": f"owner-{i}/repo-{i}",
                "description": f"Description for repo {i} with extra detail " * 5,
                "language": "Python",
                "stars": 100 + i * 10,
                "forks": 50 + i,
                "created_at": "2026-05-01T00:00:00Z",
                "topics": ["ml", "deep-learning"],
                "license": "MIT",
                "url": f"https://github.com/owner-{i}/repo-{i}",
            })
        data = {
            "week": "2026-W21",
            "crawled_at": "2026-05-18T08:54:09Z",
            "new_repos": repos,
            "trending_repos": [],
            "signals": {"top_topics": ["ml"]},
            "metadata": {"api_calls_used": 10, "rate_limit_remaining": 50},
        }

        result = preprocess(data, max_desc=200)
        stats = result["stats"]
        assert 30 <= stats["reduction_pct"] <= 70, (
            f"Reduction {stats['reduction_pct']}% not in expected range"
        )

    def test_output_structure(self):
        data = {
            "week": "2026-W21",
            "new_repos": [{"name": "x", "description": "hello", "stars": 10,
                           "topics": [], "language": "Go", "created_at": "2026-05-01T00:00:00Z"}],
            "trending_repos": [],
        }
        result = preprocess(data)
        assert result["week"] == "2026-W21"
        assert len(result["repos"]) == 1
        assert "signals" in result
        assert "stats" in result

    def test_deduplicates_repos(self):
        repo = {"name": "dup", "description": "x", "stars": 1, "topics": [],
                "language": "Rust", "created_at": "2026-05-01T00:00:00Z"}
        data = {"week": "2026-W21", "new_repos": [repo], "trending_repos": [repo]}
        result = preprocess(data)
        assert len(result["repos"]) == 1


class TestMainCLI:
    def test_end_to_end(self, tmp_path):
        raw = {
            "week": "2026-W21",
            "crawled_at": "2026-05-18T00:00:00Z",
            "new_repos": [
                {"name": "r", "owner": "o", "full_name": "o/r",
                 "description": "d" * 300, "language": "Python",
                 "stars": 100, "forks": 10, "created_at": "2026-05-01T00:00:00Z",
                 "topics": ["ai"], "license": "MIT", "url": "https://github.com/o/r"}
            ],
            "trending_repos": [],
            "signals": {"top_topics": ["ai"]},
            "metadata": {"api_calls_used": 1},
        }
        input_file = tmp_path / "raw.json"
        output_file = tmp_path / "compact.json"
        input_file.write_text(json.dumps(raw))

        rc = main(["--input", str(input_file), "--output", str(output_file)])
        assert rc == 0
        assert output_file.exists()

        result = json.loads(output_file.read_text())
        assert result["week"] == "2026-W21"
        assert len(result["repos"][0]["desc"]) <= 200

    def test_missing_input(self, tmp_path):
        rc = main(["--input", str(tmp_path / "nope.json")])
        assert rc == 1
