"""Tests for scripts/quality_gate.py"""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

import scripts.quality_gate as quality_gate


def make_scored_repos(count: int, score: float = 65.0) -> list[dict]:
    """Generate a list of scored repo dicts."""
    return [{"name": f"org/repo-{i}", "relevance_score": score} for i in range(count)]


class TestGetQualityConfig:
    def test_defaults_when_empty(self):
        config = quality_gate.get_quality_config({})
        assert config["min_repos_per_week"] == 5
        assert config["max_repos_per_week"] == 30
        assert config["min_quality_score"] == 60

    def test_overrides(self):
        config = quality_gate.get_quality_config({"quality": {"min_repos_per_week": 10}})
        assert config["min_repos_per_week"] == 10
        assert config["max_repos_per_week"] == 30


class TestCheckQuality:
    def test_ok_status(self):
        repos = make_scored_repos(10, score=50.0)
        result = quality_gate.check_quality(
            repos,
            {"min_repos_per_week": 5, "max_repos_per_week": 30},
            {"min_relevance_score": 40},
        )
        assert result["status"] == "ok"
        assert result["repos_passing"] == 10
        assert result["repos_scored"] == 10
        assert result["warnings"] == []

    def test_below_threshold(self):
        repos = make_scored_repos(3, score=50.0)
        result = quality_gate.check_quality(
            repos,
            {"min_repos_per_week": 5, "max_repos_per_week": 30},
            {"min_relevance_score": 40},
        )
        assert result["status"] == "below_threshold"
        assert result["repos_passing"] == 3
        assert len(result["warnings"]) == 1
        assert "threshold is 5" in result["warnings"][0]

    def test_above_maximum(self):
        repos = make_scored_repos(35, score=50.0)
        result = quality_gate.check_quality(
            repos,
            {"min_repos_per_week": 5, "max_repos_per_week": 30},
            {"min_relevance_score": 40},
        )
        assert result["status"] == "above_maximum"
        assert result["repos_passing"] == 35
        assert len(result["warnings"]) == 1
        assert "noise" in result["warnings"][0].lower()

    def test_repos_below_score_not_counted(self):
        repos = make_scored_repos(10, score=30.0)
        result = quality_gate.check_quality(
            repos,
            {"min_repos_per_week": 5, "max_repos_per_week": 30},
            {"min_relevance_score": 40},
        )
        assert result["repos_passing"] == 0
        assert result["status"] == "below_threshold"

    def test_empty_repos(self):
        result = quality_gate.check_quality(
            [],
            {"min_repos_per_week": 5, "max_repos_per_week": 30},
            {"min_relevance_score": 40},
        )
        assert result["status"] == "below_threshold"
        assert result["repos_passing"] == 0
        assert result["repos_scored"] == 0


class TestEmitWarnings:
    def test_prints_annotations(self, capsys):
        quality_gate.emit_warnings(["Something is wrong", "Another issue"])
        captured = capsys.readouterr()
        assert "::warning::Something is wrong" in captured.out
        assert "::warning::Another issue" in captured.out

    def test_no_output_when_empty(self, capsys):
        quality_gate.emit_warnings([])
        captured = capsys.readouterr()
        assert captured.out == ""


class TestWriteMetric:
    def test_writes_json(self, tmp_path, monkeypatch):
        monkeypatch.setattr(quality_gate, "metrics_dir", lambda t: tmp_path / "metrics" / t)
        metric = {"repos_scored": 10, "repos_passing": 8, "threshold": 5, "status": "ok", "warnings": []}
        path = quality_gate.write_metric("ai-ml", metric, "2026-W21")
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["week"] == "2026-W21"
        assert data["topic"] == "ai-ml"
        assert data["repos_passing"] == 8
        assert data["status"] == "ok"
        assert "warnings" not in data


class TestLoadScoredRepos:
    def test_loads_valid_json(self, tmp_path):
        path = tmp_path / "scored.json"
        repos = make_scored_repos(5)
        path.write_text(json.dumps(repos))
        result = quality_gate.load_scored_repos(path)
        assert len(result) == 5

    def test_missing_file(self, tmp_path):
        result = quality_gate.load_scored_repos(tmp_path / "missing.json")
        assert result == []

    def test_invalid_json(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("not json")
        result = quality_gate.load_scored_repos(path)
        assert result == []

    def test_non_list_json(self, tmp_path):
        path = tmp_path / "obj.json"
        path.write_text(json.dumps({"repos": []}))
        result = quality_gate.load_scored_repos(path)
        assert result == []


class TestMain:
    def test_with_input_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(quality_gate, "metrics_dir", lambda t: tmp_path / "metrics" / t)
        scored_path = tmp_path / "scored.json"
        scored_path.write_text(json.dumps(make_scored_repos(10, score=50.0)))

        config_path = tmp_path / "config.yml"
        config_path.write_text(
            "topic:\n  id: ai-ml\nscoring:\n  min_relevance_score: 40\n"
            "quality:\n  min_repos_per_week: 5\n  max_repos_per_week: 30\n"
        )

        result = quality_gate.main(["--input", str(scored_path), "--config", str(config_path)])
        assert result == 0

    def test_missing_input_no_crash(self, tmp_path, monkeypatch):
        monkeypatch.setattr(quality_gate, "metrics_dir", lambda t: tmp_path / "metrics" / t)
        config_path = tmp_path / "config.yml"
        config_path.write_text("topic:\n  id: test\n")

        result = quality_gate.main(["--input", str(tmp_path / "nope.json"), "--config", str(config_path)])
        assert result == 0

    def test_always_exits_zero(self, tmp_path, monkeypatch):
        monkeypatch.setattr(quality_gate, "metrics_dir", lambda t: tmp_path / "metrics" / t)
        scored_path = tmp_path / "scored.json"
        scored_path.write_text(json.dumps(make_scored_repos(2, score=50.0)))

        config_path = tmp_path / "config.yml"
        config_path.write_text(
            "topic:\n  id: ai-ml\nscoring:\n  min_relevance_score: 40\n"
            "quality:\n  min_repos_per_week: 10\n  max_repos_per_week: 30\n"
        )

        result = quality_gate.main(["--input", str(scored_path), "--config", str(config_path)])
        assert result == 0

    def test_topic_override(self, tmp_path, monkeypatch):
        monkeypatch.setattr(quality_gate, "metrics_dir", lambda t: tmp_path / "metrics" / t)
        scored_path = tmp_path / "scored.json"
        scored_path.write_text(json.dumps(make_scored_repos(10, score=50.0)))

        config_path = tmp_path / "config.yml"
        config_path.write_text("topic:\n  id: ai-ml\nscoring:\n  min_relevance_score: 40\n")

        result = quality_gate.main([
            "--input", str(scored_path),
            "--config", str(config_path),
            "--topic", "custom-topic",
        ])
        assert result == 0
        # Verify metric written with correct topic
        files = list((tmp_path / "metrics" / "custom-topic").glob("quality-*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text())
        assert data["topic"] == "custom-topic"


class TestWeekSlug:
    def test_format(self):
        from datetime import datetime, timezone
        dt = datetime(2026, 5, 18, tzinfo=timezone.utc)
        result = quality_gate.week_slug(dt)
        assert result == "2026-W21"
