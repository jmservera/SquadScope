"""Tests for topic config schema validation."""

import pytest
from pydantic import ValidationError

from scripts.validate_topic_config import TopicConfig, validate_file

# --- Valid configs pass ---


def test_valid_ai_ml_config():
    config = validate_file("examples/topics/ai-ml.yml")
    assert config.topic.id == "ai-ml"
    assert config.topic.name == "AI & Machine Learning"
    assert len(config.queries.primary) >= 1


def test_valid_rust_config():
    config = validate_file("examples/topics/rust.yml")
    assert config.topic.id == "rust"
    assert config.scoring.min_stars == 30


def test_valid_root_config():
    config = validate_file("squadscope.topic.yml")
    assert config.topic.id == "ai-ml"


def test_minimal_config():
    """Only required fields — scoring/quality/learning get defaults."""
    data = {
        "topic": {"id": "minimal", "name": "Minimal Topic"},
        "queries": {"primary": ["stars:>100"]},
    }
    config = TopicConfig.model_validate(data)
    assert config.scoring.min_stars == 20
    assert config.quality.min_repos_per_week == 5
    assert "{topic_id}" in config.learning.wisdom_file


# --- Invalid configs fail with correct errors ---


def test_invalid_topic_id_uppercase():
    data = {
        "topic": {"id": "AI-ML", "name": "Test"},
        "queries": {"primary": ["stars:>10"]},
    }
    with pytest.raises(ValidationError, match="URL-safe"):
        TopicConfig.model_validate(data)


def test_invalid_topic_id_spaces():
    data = {
        "topic": {"id": "ai ml", "name": "Test"},
        "queries": {"primary": ["stars:>10"]},
    }
    with pytest.raises(ValidationError, match="URL-safe"):
        TopicConfig.model_validate(data)


def test_invalid_topic_id_special_chars():
    data = {
        "topic": {"id": "ai_ml!", "name": "Test"},
        "queries": {"primary": ["stars:>10"]},
    }
    with pytest.raises(ValidationError, match="URL-safe"):
        TopicConfig.model_validate(data)


def test_missing_topic_name():
    data = {
        "topic": {"id": "test"},
        "queries": {"primary": ["stars:>10"]},
    }
    with pytest.raises(ValidationError, match="name"):
        TopicConfig.model_validate(data)


def test_empty_topic_name():
    data = {
        "topic": {"id": "test", "name": "   "},
        "queries": {"primary": ["stars:>10"]},
    }
    with pytest.raises(ValidationError, match="must not be empty"):
        TopicConfig.model_validate(data)


def test_missing_primary_queries():
    data = {
        "topic": {"id": "test", "name": "Test"},
        "queries": {"secondary": ["stars:>100"]},
    }
    with pytest.raises(ValidationError, match="primary"):
        TopicConfig.model_validate(data)


def test_empty_primary_queries_list():
    data = {
        "topic": {"id": "test", "name": "Test"},
        "queries": {"primary": []},
    }
    with pytest.raises(ValidationError, match="least"):
        TopicConfig.model_validate(data)


def test_empty_string_in_primary():
    data = {
        "topic": {"id": "test", "name": "Test"},
        "queries": {"primary": [""]},
    }
    with pytest.raises(ValidationError, match="empty string"):
        TopicConfig.model_validate(data)


def test_invalid_language_boost_too_high():
    data = {
        "topic": {"id": "test", "name": "Test"},
        "queries": {"primary": ["stars:>10"]},
        "scoring": {"language_boost": {"Python": 50.0}},
    }
    with pytest.raises(ValidationError, match="between 0.1 and 10.0"):
        TopicConfig.model_validate(data)


def test_invalid_language_boost_too_low():
    data = {
        "topic": {"id": "test", "name": "Test"},
        "queries": {"primary": ["stars:>10"]},
        "scoring": {"language_boost": {"Go": 0.0}},
    }
    with pytest.raises(ValidationError, match="between 0.1 and 10.0"):
        TopicConfig.model_validate(data)


def test_invalid_quality_min_greater_than_max():
    data = {
        "topic": {"id": "test", "name": "Test"},
        "queries": {"primary": ["stars:>10"]},
        "quality": {"min_repos_per_week": 50, "max_repos_per_week": 10},
    }
    with pytest.raises(ValidationError, match="must be <="):
        TopicConfig.model_validate(data)


def test_invalid_relevance_score_out_of_range():
    data = {
        "topic": {"id": "test", "name": "Test"},
        "queries": {"primary": ["stars:>10"]},
        "scoring": {"min_relevance_score": 150},
    }
    with pytest.raises(ValidationError, match="less than or equal to 100"):
        TopicConfig.model_validate(data)


def test_missing_topic_section():
    data = {"queries": {"primary": ["stars:>10"]}}
    with pytest.raises(ValidationError, match="topic"):
        TopicConfig.model_validate(data)


def test_missing_queries_section():
    data = {"topic": {"id": "test", "name": "Test"}}
    with pytest.raises(ValidationError, match="queries"):
        TopicConfig.model_validate(data)


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        validate_file("nonexistent.yml")


def test_cli_exit_code_valid(monkeypatch):
    """CLI returns 0 for valid config."""
    from scripts.validate_topic_config import main

    monkeypatch.setattr("sys.argv", ["validate", "examples/topics/ai-ml.yml"])
    assert main() == 0


def test_cli_exit_code_invalid(monkeypatch):
    """CLI returns 1 for missing file."""
    from scripts.validate_topic_config import main

    monkeypatch.setattr("sys.argv", ["validate", "nonexistent.yml"])
    assert main() == 1
