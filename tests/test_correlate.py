"""Tests for the cross-source correlation engine."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.correlate import (
    assess_hype_risk,
    correlate_all,
    correlate_repo,
    extract_week_from_filename,
    fuzzy_name_score,
    has_temporal_spike,
    match_category,
    match_direct_link,
    match_org_name,
    match_project_name,
    _token_overlap_ratio,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _repo(
    name: str = "cool-project",
    owner: str = "acme",
    full_name: str | None = None,
    url: str | None = None,
    topics: list[str] | None = None,
    stars_gained: int | None = None,
    stars: int = 100,
) -> dict:
    fn = full_name or f"{owner}/{name}"
    return {
        "name": name,
        "owner": owner,
        "full_name": fn,
        "url": url or f"https://github.com/{fn}",
        "topics": topics or [],
        "stars_gained": stars_gained,
        "stars": stars,
    }


def _article(
    title: str = "Acme launches Cool Project",
    url: str = "https://techcrunch.com/2026/05/20/acme-cool-project/",
    github_links: list[str] | None = None,
    entities: list[str] | None = None,
    categories: list[str] | None = None,
) -> dict:
    return {
        "title": title,
        "url": url,
        "github_links": github_links or [],
        "entities": entities or [],
        "categories": categories or [],
    }


# ---------------------------------------------------------------------------
# Heuristic 1: Direct GitHub link match
# ---------------------------------------------------------------------------


class TestDirectLinkMatch:
    def test_exact_url_match(self):
        repo = _repo(url="https://github.com/acme/cool-project")
        article = _article(github_links=["https://github.com/acme/cool-project"])
        assert match_direct_link(repo, [article]) == [article]

    def test_trailing_slash_normalization(self):
        repo = _repo(url="https://github.com/acme/cool-project/")
        article = _article(github_links=["https://github.com/acme/cool-project"])
        assert match_direct_link(repo, [article]) == [article]

    def test_case_insensitive(self):
        repo = _repo(url="https://github.com/Acme/Cool-Project")
        article = _article(github_links=["https://github.com/acme/cool-project"])
        assert match_direct_link(repo, [article]) == [article]

    def test_no_match(self):
        repo = _repo(name="other-project", owner="acme", url="https://github.com/acme/other-project")
        article = _article(github_links=["https://github.com/acme/cool-project"])
        assert match_direct_link(repo, [article]) == []


# ---------------------------------------------------------------------------
# Heuristic 2: Organization name match
# ---------------------------------------------------------------------------


class TestOrgNameMatch:
    def test_owner_in_entities(self):
        repo = _repo(owner="OpenAI")
        article = _article(entities=["OpenAI", "Google"])
        assert match_org_name(repo, [article]) == [article]

    def test_case_insensitive_match(self):
        repo = _repo(owner="openai")
        article = _article(entities=["OpenAI"])
        assert match_org_name(repo, [article]) == [article]

    def test_no_match(self):
        repo = _repo(owner="acme")
        article = _article(entities=["Google", "Meta"])
        assert match_org_name(repo, [article]) == []

    def test_short_owner_skipped(self):
        repo = _repo(owner="x")
        article = _article(entities=["x"])
        assert match_org_name(repo, [article]) == []


# ---------------------------------------------------------------------------
# Heuristic 3: Project name fuzzy match
# ---------------------------------------------------------------------------


class TestProjectNameMatch:
    def test_exact_name_in_entity(self):
        repo = _repo(name="langchain")
        article = _article(entities=["LangChain"])
        assert match_project_name(repo, [article]) == [article]

    def test_fuzzy_name_in_title(self):
        repo = _repo(name="tensorflow")
        article = _article(title="TensorFlow 3.0 released with new features")
        assert match_project_name(repo, [article]) == [article]

    def test_no_match_different_name(self):
        repo = _repo(name="pytorch")
        article = _article(title="React 20 is out", entities=["React"])
        assert match_project_name(repo, [article]) == []

    def test_short_name_skipped(self):
        repo = _repo(name="go")
        article = _article(entities=["Go"])
        assert match_project_name(repo, [article]) == []


# ---------------------------------------------------------------------------
# Heuristic 4: Category correlation
# ---------------------------------------------------------------------------


class TestCategoryMatch:
    def test_topic_category_overlap(self):
        repo = _repo(topics=["machine-learning", "python"])
        article = _article(categories=["machine-learning", "startups"])
        assert match_category(repo, [article]) == [article]

    def test_no_overlap(self):
        repo = _repo(topics=["rust", "systems"])
        article = _article(categories=["machine-learning", "startups"])
        assert match_category(repo, [article]) == []

    def test_empty_topics(self):
        repo = _repo(topics=[])
        article = _article(categories=["ai"])
        assert match_category(repo, [article]) == []


# ---------------------------------------------------------------------------
# Heuristic 5: Temporal spike
# ---------------------------------------------------------------------------


class TestTemporalSpike:
    def test_spike_detected(self):
        repo = _repo(stars_gained=50)
        assert has_temporal_spike(repo) is True

    def test_no_spike(self):
        repo = _repo(stars_gained=5)
        assert has_temporal_spike(repo) is False

    def test_none_stars_gained(self):
        repo = _repo(stars_gained=None)
        assert has_temporal_spike(repo) is False


# ---------------------------------------------------------------------------
# Hype risk assessment
# ---------------------------------------------------------------------------


class TestHypeRisk:
    def test_high_confidence_high_stars(self):
        assert assess_hype_risk(0.9, 200) == "high"

    def test_high_confidence_low_stars(self):
        assert assess_hype_risk(0.8, 50) == "medium"

    def test_medium_confidence(self):
        assert assess_hype_risk(0.6, 10) == "medium"

    def test_low_confidence(self):
        assert assess_hype_risk(0.4, 5) == "low"

    def test_none_risk(self):
        assert assess_hype_risk(0.2, 0) == "none"


# ---------------------------------------------------------------------------
# Integration: correlate_repo
# ---------------------------------------------------------------------------


class TestCorrelateRepo:
    def test_direct_link_takes_priority(self):
        repo = _repo(owner="acme", name="cool-project", stars_gained=5)
        article = _article(
            github_links=["https://github.com/acme/cool-project"],
            entities=["Acme"],
        )
        result = correlate_repo(repo, [article])
        assert result is not None
        assert result["match_type"] == "direct_link"
        assert result["correlation_confidence"] == 1.0

    def test_no_match_returns_none(self):
        repo = _repo(owner="nobody", name="nothing", topics=[])
        article = _article(entities=["Google"], categories=["finance"])
        assert correlate_repo(repo, [article]) is None

    def test_temporal_boost(self):
        repo = _repo(owner="acme", name="something", stars_gained=50)
        article = _article(entities=["Acme"])
        result = correlate_repo(repo, [article])
        assert result is not None
        assert result["correlation_confidence"] == 1.0  # 0.8 + 0.2


# ---------------------------------------------------------------------------
# Integration: correlate_all
# ---------------------------------------------------------------------------


class TestCorrelateAll:
    def test_full_pipeline(self):
        repos = [
            _repo(owner="acme", name="project-a"),
            _repo(owner="nobody", name="unrelated", topics=[]),
        ]
        articles = [_article(entities=["Acme"])]
        result = correlate_all(repos, articles, "2026-W21")
        assert result["week"] == "2026-W21"
        assert len(result["correlations"]) == 1
        assert result["correlations"][0]["repo"] == "acme/project-a"
        assert "nobody/unrelated" in result["uncorrelated_repos"]
        assert result["metadata"]["repos_analyzed"] == 2
        assert result["metadata"]["correlations_found"] == 1

    def test_empty_articles(self):
        repos = [_repo()]
        result = correlate_all(repos, [], "2026-W21")
        assert result["correlations"] == []
        assert len(result["uncorrelated_repos"]) == 1


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


class TestUtilities:
    def test_extract_week_from_filename(self):
        assert extract_week_from_filename(Path("2026-W21.json")) == "2026-W21"
        assert extract_week_from_filename(Path("data.json")) == "unknown"

    def test_token_overlap_ratio(self):
        assert _token_overlap_ratio("machine-learning", "machine learning") == 1.0
        assert _token_overlap_ratio("foo-bar", "baz-qux") == 0.0

    def test_fuzzy_name_score_identical(self):
        assert fuzzy_name_score("langchain", "langchain") == 1.0

    def test_fuzzy_name_score_empty(self):
        assert fuzzy_name_score("", "something") == 0.0
