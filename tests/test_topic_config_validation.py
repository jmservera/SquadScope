"""Integration tests: validate ai-ml and rust topic configs end-to-end.

Verifies schema validation passes and scoring pipeline produces reasonable
results with mock repo data for both topics, plus cross-topic isolation.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from scripts.score_repos import (
    compute_relevance_score,
    get_scoring_config,
    load_config,
    score_repos,
)
from scripts.validate_topic_config import validate_file

# --- Helpers ---


def _make_repo(
    name: str,
    language: str,
    stars: int,
    stars_gained: int,
    topics: list[str],
    age_days: int = 30,
) -> dict:
    """Create a mock repo dict with given characteristics."""
    return {
        "name": name,
        "owner": "mock-org",
        "full_name": f"mock-org/{name}",
        "description": f"Mock repo: {name}",
        "language": language,
        "stars": stars,
        "forks": stars // 10,
        "created_at": (datetime.now(UTC) - timedelta(days=age_days)).isoformat(),
        "topics": topics,
        "license": "MIT",
        "url": f"https://github.com/mock-org/{name}",
        "stars_gained": stars_gained,
    }


# --- AI/ML Config Fixtures ---


@pytest.fixture
def aiml_root_config():
    return validate_file("squadscope.topic.yml")


@pytest.fixture
def aiml_example_config():
    return validate_file("examples/topics/ai-ml.yml")


@pytest.fixture
def aiml_scoring_config():
    config = load_config("squadscope.topic.yml")
    return get_scoring_config(config)


@pytest.fixture
def rust_config():
    return validate_file("examples/topics/rust.yml")


@pytest.fixture
def rust_scoring_config():
    config = load_config("examples/topics/rust.yml")
    return get_scoring_config(config)


@pytest.fixture
def aiml_repos():
    """Sample repos matching AI/ML profile."""
    return [
        _make_repo(
            "transformer-lib",
            "Python",
            500,
            120,
            ["machine-learning", "transformers", "deep-learning"],
        ),
        _make_repo(
            "llm-toolkit", "Python", 1200, 300, ["llm", "artificial-intelligence", "python"]
        ),
        _make_repo(
            "ml-starter", "Jupyter Notebook", 150, 40, ["machine-learning", "neural-network"]
        ),
        _make_repo("data-pipeline", "Python", 80, 20, ["machine-learning"], age_days=60),
        _make_repo(
            "ai-research",
            "Python",
            3000,
            500,
            ["deep-learning", "llm", "transformers"],
            age_days=10,
        ),
        _make_repo("small-ml", "Python", 50, 15, ["machine-learning"], age_days=90),
        _make_repo("mid-ml", "Python", 200, 50, ["deep-learning", "neural-network"], age_days=45),
    ]


@pytest.fixture
def rust_repos():
    """Sample repos matching Rust profile."""
    return [
        _make_repo("fast-cli", "Rust", 400, 80, ["rust", "cli", "systems-programming"]),
        _make_repo("async-runtime", "Rust", 2000, 200, ["rust", "async-rust", "cargo"]),
        _make_repo("wasm-toolkit", "Rust", 600, 100, ["rust", "wasm", "cargo"]),
        _make_repo("rust-game", "Rust", 150, 40, ["rust", "systems-programming"]),
        _make_repo("tiny-crate", "Rust", 50, 20, ["rust", "cargo"], age_days=60),
    ]


# =============================================================================
# 1. AI/ML Schema Validation
# =============================================================================


class TestAimlSchemaValidation:
    """Issue #70: Validate ai-ml configs pass schema validation."""

    def test_root_config_passes_validation(self, aiml_root_config):
        assert aiml_root_config.topic.id == "ai-ml"
        assert aiml_root_config.topic.name == "AI & Machine Learning"
        assert len(aiml_root_config.queries.primary) >= 2

    def test_example_config_passes_validation(self, aiml_example_config):
        assert aiml_example_config.topic.id == "ai-ml"
        assert aiml_example_config.scoring.min_stars == 20
        assert aiml_example_config.scoring.min_relevance_score == 40

    def test_root_config_scoring_section(self, aiml_root_config):
        assert aiml_root_config.scoring.language_boost.get("Python") == 1.2
        assert "machine-learning" in aiml_root_config.scoring.topic_relevance

    def test_root_config_quality_section(self, aiml_root_config):
        assert aiml_root_config.quality.min_repos_per_week == 5
        assert aiml_root_config.quality.max_repos_per_week == 30

    def test_root_config_learning_section(self, aiml_root_config):
        assert "ai-ml" in aiml_root_config.learning.wisdom_file


# =============================================================================
# 2. AI/ML Scoring Pipeline
# =============================================================================


class TestAimlScoringPipeline:
    """Issue #70: AI/ML repos get reasonable scores with mock data."""

    def test_typical_aiml_repos_score_above_threshold(self, aiml_scoring_config, aiml_repos):
        scored = score_repos(aiml_repos, aiml_scoring_config)
        # All well-formed AI/ML repos should pass the min_relevance_score (40)
        assert len(scored) >= 5

    def test_high_quality_repo_scores_above_40(self, aiml_scoring_config):
        repo = _make_repo(
            "top-ml", "Python", 500, 100, ["machine-learning", "deep-learning", "llm"]
        )
        score = compute_relevance_score(repo, aiml_scoring_config)
        assert score >= 40

    def test_min_repos_per_week_achievable(self, aiml_scoring_config, aiml_repos):
        """With typical data, at least min_repos_per_week pass threshold."""
        min_required = 5  # from config quality.min_repos_per_week
        scored = score_repos(aiml_repos, aiml_scoring_config)
        assert len(scored) >= min_required

    def test_python_language_boost_applies(self, aiml_scoring_config):
        python_repo = _make_repo("py-ml", "Python", 200, 50, ["machine-learning"])
        other_repo = _make_repo("go-ml", "Go", 200, 50, ["machine-learning"])

        py_score = compute_relevance_score(python_repo, aiml_scoring_config)
        go_score = compute_relevance_score(other_repo, aiml_scoring_config)
        assert py_score > go_score

    def test_topic_relevance_boosts_score(self, aiml_scoring_config):
        relevant = _make_repo(
            "relevant", "Python", 200, 50, ["machine-learning", "deep-learning", "llm"]
        )
        irrelevant = _make_repo("irrelevant", "Python", 200, 50, ["cooking", "recipes"])

        rel_score = compute_relevance_score(relevant, aiml_scoring_config)
        irr_score = compute_relevance_score(irrelevant, aiml_scoring_config)
        assert rel_score > irr_score


# =============================================================================
# 3. Rust Schema Validation
# =============================================================================


class TestRustSchemaValidation:
    """Issue #71: Validate rust config passes schema validation."""

    def test_rust_config_passes_validation(self, rust_config):
        assert rust_config.topic.id == "rust"
        assert rust_config.topic.name == "Rust Ecosystem"
        assert len(rust_config.queries.primary) >= 2

    def test_rust_scoring_section(self, rust_config):
        assert rust_config.scoring.language_boost.get("Rust") == 1.3
        assert rust_config.scoring.min_stars == 30
        assert rust_config.scoring.max_age_days == 730

    def test_rust_topic_relevance(self, rust_config):
        assert "rust" in rust_config.scoring.topic_relevance
        assert "cargo" in rust_config.scoring.topic_relevance
        assert "wasm" in rust_config.scoring.topic_relevance

    def test_rust_quality_section(self, rust_config):
        assert rust_config.quality.min_repos_per_week == 5
        assert rust_config.quality.max_repos_per_week == 25
        assert rust_config.quality.min_quality_score == 55


# =============================================================================
# 4. Rust Scoring Pipeline
# =============================================================================


class TestRustScoringPipeline:
    """Issue #71: Rust repos score reasonably with language_boost."""

    def test_typical_rust_repos_score_above_threshold(self, rust_scoring_config, rust_repos):
        scored = score_repos(rust_repos, rust_scoring_config)
        # Most Rust repos should pass the lower threshold (35)
        assert len(scored) >= 3

    def test_rust_language_boost_applies(self, rust_scoring_config):
        rust_repo = _make_repo("cli-tool", "Rust", 300, 60, ["rust", "cli"])
        go_repo = _make_repo("cli-tool-go", "Go", 300, 60, ["go", "cli"])

        rust_score = compute_relevance_score(rust_repo, rust_scoring_config)
        go_score = compute_relevance_score(go_repo, rust_scoring_config)
        assert rust_score > go_score

    def test_narrower_topic_still_produces_results(self, rust_scoring_config, rust_repos):
        """Rust is narrower than AI/ML but should still yield min_repos_per_week."""
        min_required = 5  # from config quality.min_repos_per_week
        scored = score_repos(rust_repos, rust_scoring_config)
        assert len(scored) >= min_required

    def test_high_quality_rust_repo_scores_above_40(self, rust_scoring_config):
        repo = _make_repo("blazing-fast", "Rust", 1000, 150, ["rust", "async-rust", "cargo"])
        score = compute_relevance_score(repo, rust_scoring_config)
        assert score >= 40


# =============================================================================
# 5. Cross-Topic Isolation
# =============================================================================


class TestCrossTopicIsolation:
    """Verify configs don't score repos from other domains highly."""

    def test_aiml_config_does_not_score_rust_repos_highly(self, aiml_scoring_config, rust_repos):
        """Rust repos should score lower under ai-ml config due to no topic overlap."""
        scored = score_repos(rust_repos, aiml_scoring_config)
        # Rust repos lack AI/ML topics, so fewer should pass threshold
        for repo in scored:
            # No Rust repo should score as high as a good AI/ML repo would
            assert repo["relevance_score"] < 70

    def test_rust_config_does_not_score_python_ml_repos_highly(
        self, rust_scoring_config, aiml_repos
    ):
        """Python ML repos should score lower under rust config due to topic/lang mismatch."""
        scored = score_repos(aiml_repos, rust_scoring_config)
        # Python repos don't get Rust language boost and lack rust topics
        for repo in scored:
            assert repo["relevance_score"] < 75

    def test_aiml_repos_score_higher_with_own_config(
        self, aiml_scoring_config, rust_scoring_config, aiml_repos
    ):
        """AI/ML repos should score higher with ai-ml config than rust config."""
        aiml_scored = score_repos(aiml_repos, aiml_scoring_config)
        rust_scored = score_repos(aiml_repos, rust_scoring_config)

        avg_aiml = sum(r["relevance_score"] for r in aiml_scored) / max(len(aiml_scored), 1)
        avg_rust = (
            sum(r["relevance_score"] for r in rust_scored) / max(len(rust_scored), 1)
            if rust_scored
            else 0
        )
        assert avg_aiml > avg_rust

    def test_rust_repos_score_higher_with_own_config(
        self, aiml_scoring_config, rust_scoring_config, rust_repos
    ):
        """Rust repos should score higher with rust config than ai-ml config."""
        rust_scored = score_repos(rust_repos, rust_scoring_config)
        aiml_scored = score_repos(rust_repos, aiml_scoring_config)

        avg_rust = sum(r["relevance_score"] for r in rust_scored) / max(len(rust_scored), 1)
        avg_aiml = (
            sum(r["relevance_score"] for r in aiml_scored) / max(len(aiml_scored), 1)
            if aiml_scored
            else 0
        )
        assert avg_rust > avg_aiml
