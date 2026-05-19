"""Tests for the prediction ledger module."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.prediction_ledger import (
    MAX_PREDICTIONS,
    MIN_PREDICTIONS,
    PREDICTION_TYPES,
    append_predictions,
    build_repo_index,
    classify_prediction,
    extract_repos_from_summary,
    extract_week,
    generate_predictions,
    infer_raw_path,
    main,
    parse_summary,
    score_breakout_candidate,
    score_momentum_shift,
    score_rising_star,
)

SAMPLE_SUMMARY = """\
---
title: "Week 21, 2026 Analysis"
date: 2026-05-18T12:07:20.778+02:00
week: "2026-W21"
year: 2026
tags: [ai, agents]
top_repo: "vercel-labs/zero"
quality_score: 76
summary: "Strong week for agent tooling."
---

## Notable New Repositories

[vercel-labs/zero](https://github.com/vercel-labs/zero) is the top new repo.
Also notable: [org/rising-repo](https://github.com/org/rising-repo) and
[bigcorp/established](https://github.com/bigcorp/established).
"""

SAMPLE_RAW = {
    "week": "2026-W21",
    "crawled_at": "2026-05-18T08:54:09Z",
    "new_repos": [
        {
            "name": "zero",
            "owner": "vercel-labs",
            "full_name": "vercel-labs/zero",
            "description": "Agent infra",
            "language": "TypeScript",
            "stars": 2500,
            "forks": 150,
            "created_at": "2026-05-10T00:00:00Z",
            "topics": ["ai", "agents"],
            "license": "MIT",
            "url": "https://github.com/vercel-labs/zero",
        },
        {
            "name": "rising-repo",
            "owner": "org",
            "full_name": "org/rising-repo",
            "description": "Hot new project",
            "language": "Python",
            "stars": 800,
            "forks": 120,
            "created_at": "2026-05-12T00:00:00Z",
            "topics": ["ml"],
            "license": "Apache-2.0",
            "url": "https://github.com/org/rising-repo",
        },
    ],
    "trending_repos": [
        {
            "name": "established",
            "owner": "bigcorp",
            "full_name": "bigcorp/established",
            "description": "Major framework",
            "language": "JavaScript",
            "stars": 50000,
            "forks": 8000,
            "created_at": "2020-01-01T00:00:00Z",
            "topics": ["framework"],
            "license": "MIT",
            "url": "https://github.com/bigcorp/established",
        },
    ],
    "signals": {"top_topics": ["ai", "agents"]},
    "metadata": {"api_calls_used": 10, "rate_limit_remaining": 4990},
}


class TestExtractWeek:
    def test_extracts_from_filename(self):
        assert extract_week("2026-W21-summary.md") == "2026-W21"

    def test_extracts_from_text(self):
        assert extract_week("week: 2025-W03") == "2025-W03"

    def test_returns_none_for_no_match(self):
        assert extract_week("no week here") is None


class TestParseSummary:
    def test_parses_frontmatter(self):
        result = parse_summary(SAMPLE_SUMMARY)
        assert result["frontmatter"]["week"] == "2026-W21"
        assert result["frontmatter"]["top_repo"] == "vercel-labs/zero"

    def test_parses_body(self):
        result = parse_summary(SAMPLE_SUMMARY)
        assert "Notable New Repositories" in result["body"]

    def test_handles_no_frontmatter(self):
        result = parse_summary("# Just a header\nSome content.")
        assert result["frontmatter"] == {}
        assert "Just a header" in result["body"]


class TestExtractRepos:
    def test_extracts_repo_links(self):
        body = parse_summary(SAMPLE_SUMMARY)["body"]
        repos = extract_repos_from_summary(body)
        assert "vercel-labs/zero" in repos
        assert "org/rising-repo" in repos
        assert "bigcorp/established" in repos

    def test_deduplicates(self):
        text = (
            "[a/b](https://github.com/a/b) and [a/b](https://github.com/a/b)"
        )
        repos = extract_repos_from_summary(text)
        assert repos == ["a/b"]

    def test_empty_for_no_links(self):
        assert extract_repos_from_summary("no repos here") == []


class TestBuildRepoIndex:
    def test_indexes_by_full_name(self):
        index = build_repo_index(SAMPLE_RAW)
        assert "vercel-labs/zero" in index
        assert "bigcorp/established" in index

    def test_marks_source(self):
        index = build_repo_index(SAMPLE_RAW)
        assert index["vercel-labs/zero"]["_source"] == "new_repos"
        assert index["bigcorp/established"]["_source"] == "trending_repos"

    def test_empty_data(self):
        assert build_repo_index({}) == {}


class TestScoring:
    def test_rising_star_high_stars_new(self):
        repo = {"stars": 3000, "_source": "new_repos"}
        score = score_rising_star(repo)
        assert 0.5 <= score <= 0.9

    def test_rising_star_low_stars(self):
        repo = {"stars": 10, "_source": "new_repos"}
        score = score_rising_star(repo)
        assert score < 0.4

    def test_breakout_high_fork_ratio(self):
        repo = {"stars": 500, "forks": 100, "_source": "new_repos"}
        score = score_breakout_candidate(repo)
        assert score >= 0.4

    def test_momentum_shift_trending_big(self):
        repo = {"stars": 50000, "_source": "trending_repos"}
        score = score_momentum_shift(repo)
        assert score >= 0.5

    def test_momentum_shift_not_trending(self):
        repo = {"stars": 50000, "_source": "new_repos"}
        score = score_momentum_shift(repo)
        assert score < 0.3


class TestClassifyPrediction:
    def test_returns_valid_type(self):
        repo = {"stars": 3000, "forks": 100, "_source": "new_repos"}
        pred_type, confidence, reason = classify_prediction(repo)
        assert pred_type in PREDICTION_TYPES
        assert 0.0 <= confidence <= 1.0
        assert len(reason) > 0

    def test_new_high_star_is_rising_star(self):
        repo = {"stars": 5000, "forks": 50, "_source": "new_repos"}
        pred_type, _, _ = classify_prediction(repo)
        assert pred_type == "rising_star"

    def test_trending_established_is_momentum(self):
        repo = {"stars": 50000, "forks": 1000, "_source": "trending_repos"}
        pred_type, _, _ = classify_prediction(repo)
        assert pred_type == "momentum_shift"


class TestGeneratePredictions:
    def test_generates_predictions(self):
        preds = generate_predictions(SAMPLE_SUMMARY, SAMPLE_RAW, "2026-W21")
        assert MIN_PREDICTIONS <= len(preds) <= MAX_PREDICTIONS

    def test_prediction_structure(self):
        preds = generate_predictions(SAMPLE_SUMMARY, SAMPLE_RAW, "2026-W21")
        for p in preds:
            assert p["week"] == "2026-W21"
            assert p["prediction"] in PREDICTION_TYPES
            assert 0.0 <= p["confidence"] <= 1.0
            assert p["validated"] is None
            assert "repo" in p
            assert "reason" in p

    def test_sorted_by_confidence(self):
        preds = generate_predictions(SAMPLE_SUMMARY, SAMPLE_RAW, "2026-W21")
        confidences = [p["confidence"] for p in preds]
        assert confidences == sorted(confidences, reverse=True)


class TestAppendPredictions:
    def test_appends_to_file(self, tmp_path):
        output = tmp_path / "predictions.jsonl"
        preds = [
            {
                "week": "2026-W21",
                "repo": "a/b",
                "prediction": "rising_star",
                "confidence": 0.7,
                "reason": "test",
                "validated": None,
            }
        ]
        append_predictions(preds, output)
        lines = output.read_text().strip().splitlines()
        assert len(lines) == 1
        assert json.loads(lines[0])["repo"] == "a/b"

    def test_appends_multiple_calls(self, tmp_path):
        output = tmp_path / "predictions.jsonl"
        pred = {
            "week": "2026-W21",
            "repo": "x/y",
            "prediction": "rising_star",
            "confidence": 0.5,
            "reason": "r",
            "validated": None,
        }
        append_predictions([pred], output)
        append_predictions([pred], output)
        lines = output.read_text().strip().splitlines()
        assert len(lines) == 2

    def test_creates_parent_dirs(self, tmp_path):
        output = tmp_path / "nested" / "dir" / "predictions.jsonl"
        append_predictions([], output)
        assert output.parent.exists()


class TestInferRawPath:
    def test_infers_from_summary(self):
        summary = Path("data/analyzed/2026-W21-summary.md")
        raw = infer_raw_path(summary, None)
        assert raw == Path("data/raw/2026-W21.json")

    def test_infers_with_topic(self):
        summary = Path("data/analyzed/ai-ml/2026-W21-summary.md")
        raw = infer_raw_path(summary, "ai-ml")
        assert raw == Path("data/raw/ai-ml/2026-W21.json")

    def test_raises_on_no_week(self):
        with pytest.raises(ValueError):
            infer_raw_path(Path("bad-name.md"), None)


class TestMain:
    def test_end_to_end(self, tmp_path):
        # Set up files
        summary_path = tmp_path / "analyzed" / "2026-W21-summary.md"
        summary_path.parent.mkdir(parents=True)
        summary_path.write_text(SAMPLE_SUMMARY)

        raw_path = tmp_path / "raw" / "2026-W21.json"
        raw_path.parent.mkdir(parents=True)
        raw_path.write_text(json.dumps(SAMPLE_RAW))

        metrics_path = tmp_path / "metrics"

        with patch("scripts.prediction_ledger.metrics_dir", return_value=metrics_path):
            preds = main([
                "--input", str(summary_path),
                "--raw", str(raw_path),
            ])

        assert len(preds) >= MIN_PREDICTIONS
        output_file = metrics_path / "predictions.jsonl"
        assert output_file.exists()
        lines = output_file.read_text().strip().splitlines()
        assert len(lines) == len(preds)
