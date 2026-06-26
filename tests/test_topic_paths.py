"""Tests for scripts/topic_paths.py — topic-aware data directory resolution."""

from __future__ import annotations

import pytest

from scripts.topic_paths import (
    DATA_ROOT,
    DEFAULT_TOPIC,
    analyzed_dir,
    cache_dir,
    ensure_dirs,
    load_topic_id,
    metrics_dir,
    raw_dir,
    snapshots_dir,
)


class TestDefaultTopic:
    """When topic is None or 'general', use legacy flat paths."""

    def test_raw_dir_none(self):
        assert raw_dir(None) == DATA_ROOT / "raw"

    def test_raw_dir_general(self):
        assert raw_dir("general") == DATA_ROOT / "raw"

    def test_analyzed_dir_default(self):
        assert analyzed_dir() == DATA_ROOT / "analyzed"

    def test_metrics_dir_default(self):
        assert metrics_dir() == DATA_ROOT / "metrics"

    def test_snapshots_dir_default(self):
        assert snapshots_dir() == DATA_ROOT / "snapshots"

    def test_cache_dir_default(self):
        assert cache_dir() == DATA_ROOT / "cache"


class TestNamespacedTopic:
    """When a specific topic is given, paths include the topic subdirectory."""

    def test_raw_dir_ai_ml(self):
        assert raw_dir("ai-ml") == DATA_ROOT / "raw" / "ai-ml"

    def test_analyzed_dir_rust(self):
        assert analyzed_dir("rust") == DATA_ROOT / "analyzed" / "rust"

    def test_metrics_dir_topic(self):
        assert metrics_dir("web-dev") == DATA_ROOT / "metrics" / "web-dev"

    def test_snapshots_dir_topic(self):
        assert snapshots_dir("ai-ml") == DATA_ROOT / "snapshots" / "ai-ml"

    def test_cache_dir_topic(self):
        assert cache_dir("rust") == DATA_ROOT / "cache" / "rust"

    def test_case_normalization(self):
        assert raw_dir("AI-ML") == DATA_ROOT / "raw" / "ai-ml"

    def test_whitespace_stripped(self):
        assert raw_dir("  rust  ") == DATA_ROOT / "raw" / "rust"


class TestEnsureDirs:
    """ensure_dirs creates all required directories."""

    def test_creates_all_dirs(self, tmp_path, monkeypatch):
        monkeypatch.setattr("scripts.topic_paths.DATA_ROOT", tmp_path / "data")
        ensure_dirs("ai-ml")
        for subdir in ("raw", "analyzed", "metrics", "snapshots", "cache"):
            assert (tmp_path / "data" / subdir / "ai-ml").is_dir()

    def test_creates_flat_dirs_for_general(self, tmp_path, monkeypatch):
        monkeypatch.setattr("scripts.topic_paths.DATA_ROOT", tmp_path / "data")
        ensure_dirs(None)
        for subdir in ("raw", "analyzed", "metrics", "snapshots", "cache"):
            assert (tmp_path / "data" / subdir).is_dir()


class TestLoadTopicId:
    """load_topic_id reads the topic.id from YAML config."""

    def test_reads_valid_config(self, tmp_path):
        config = tmp_path / "topic.yml"
        config.write_text("topic:\n  id: rust\n  name: Rust\n")
        assert load_topic_id(config) == "rust"

    def test_missing_file_returns_default(self, tmp_path):
        assert load_topic_id(tmp_path / "nope.yml") == DEFAULT_TOPIC

    def test_malformed_yaml_returns_default(self, tmp_path):
        config = tmp_path / "bad.yml"
        config.write_text("{{invalid yaml")
        assert load_topic_id(config) == DEFAULT_TOPIC

    def test_missing_topic_key_returns_default(self, tmp_path):
        config = tmp_path / "empty.yml"
        config.write_text("scoring:\n  min_stars: 10\n")
        assert load_topic_id(config) == DEFAULT_TOPIC


class TestTopicIdValidation:
    """_resolve must reject topic IDs that could cause path traversal."""

    def test_dotdot_raises(self):
        from scripts.topic_paths import DATA_ROOT, _resolve

        with pytest.raises(ValueError, match="Invalid topic ID"):
            _resolve(DATA_ROOT / "raw", "../../../etc")

    def test_absolute_path_raises(self):
        from scripts.topic_paths import DATA_ROOT, _resolve

        with pytest.raises(ValueError, match="Invalid topic ID"):
            _resolve(DATA_ROOT / "raw", "/etc/passwd")

    def test_slash_in_id_raises(self):
        from scripts.topic_paths import DATA_ROOT, _resolve

        with pytest.raises(ValueError, match="Invalid topic ID"):
            _resolve(DATA_ROOT / "raw", "valid/subdir")

    def test_null_byte_raises(self):
        from scripts.topic_paths import DATA_ROOT, _resolve

        with pytest.raises(ValueError, match="Invalid topic ID"):
            _resolve(DATA_ROOT / "raw", "evil\x00byte")

    def test_leading_hyphen_raises(self):
        from scripts.topic_paths import DATA_ROOT, _resolve

        with pytest.raises(ValueError, match="Invalid topic ID"):
            _resolve(DATA_ROOT / "raw", "-bad")

    def test_valid_hyphenated_id_passes(self):
        from scripts.topic_paths import DATA_ROOT, _resolve

        result = _resolve(DATA_ROOT / "raw", "ai-ml")
        assert result == DATA_ROOT / "raw" / "ai-ml"

    def test_valid_underscore_id_passes(self):
        from scripts.topic_paths import DATA_ROOT, _resolve

        result = _resolve(DATA_ROOT / "raw", "rust_2026")
        assert result == DATA_ROOT / "raw" / "rust_2026"
