"""Tests for TechCrunch RSS crawler — no live feed fetching."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from scripts.techcrunch_crawler import (
    TechCrunchSource,
    build_output,
    compute_relevance_score,
    extract_entities,
    extract_github_urls,
    iso_timestamp,
    parse_published_date,
    week_slug,
)


# --- Fixtures ---

def _make_entry(
    title="Test Article",
    link="https://techcrunch.com/2026/05/15/test/",
    published_parsed=(2026, 5, 15, 10, 0, 0, 3, 135, 0),
    summary="A test summary about AI and open-source projects.",
    content_html="<p>Check out <a href='https://github.com/org/repo'>this repo</a></p>",
    tags=None,
):
    entry = SimpleNamespace(
        title=title,
        link=link,
        published_parsed=published_parsed,
        summary=summary,
        content=[{"value": content_html}],
        tags=tags or [SimpleNamespace(term="AI"), SimpleNamespace(term="Startups")],
    )
    return entry


def _make_feed(entries=None, bozo=False):
    return SimpleNamespace(entries=entries or [], bozo=bozo)


# --- Unit tests: utility functions ---

class TestIsoTimestamp:
    def test_basic(self):
        dt = datetime(2026, 5, 15, 10, 0, 0, tzinfo=UTC)
        assert iso_timestamp(dt) == "2026-05-15T10:00:00Z"


class TestWeekSlug:
    def test_basic(self):
        dt = datetime(2026, 5, 15, tzinfo=UTC)
        result = week_slug(dt)
        assert result.startswith("2026-W")
        assert len(result) == 8


# --- Unit tests: extraction ---

class TestExtractGithubUrls:
    def test_finds_urls(self):
        text = "Check https://github.com/langchain-ai/langchain and https://github.com/openai/openai-python"
        result = extract_github_urls(text)
        assert "https://github.com/langchain-ai/langchain" in result
        assert "https://github.com/openai/openai-python" in result

    def test_deduplicates(self):
        text = "https://github.com/org/repo https://github.com/org/repo"
        result = extract_github_urls(text)
        assert len(result) == 1

    def test_empty_input(self):
        assert extract_github_urls("") == []
        assert extract_github_urls(None) == []

    def test_no_matches(self):
        assert extract_github_urls("No GitHub links here") == []

    def test_strips_trailing_punctuation(self):
        text = "See https://github.com/org/repo."
        result = extract_github_urls(text)
        assert result == ["https://github.com/org/repo"]


class TestExtractEntities:
    def test_finds_proper_nouns(self):
        title = "OpenAI Launches New GPT Model for Developers"
        entities = extract_entities(title)
        assert "OpenAI" in entities
        assert "GPT" in entities
        assert "Model" in entities
        assert "Developers" in entities

    def test_skips_stop_words(self):
        title = "The New AI Framework"
        entities = extract_entities(title)
        # "The" and "New" are stop words
        assert "The" not in entities
        assert "New" not in entities
        assert "AI" in entities
        assert "Framework" in entities

    def test_empty(self):
        assert extract_entities("") == []
        assert extract_entities(None) == []


class TestComputeRelevanceScore:
    def test_high_relevance(self):
        article = {
            "title": "AI startup launches open-source LLM framework",
            "summary": "A new developer API using machine learning",
            "categories": ["AI", "Open Source"],
            "github_links": ["https://github.com/org/repo"],
        }
        score = compute_relevance_score(article)
        assert score >= 0.8

    def test_low_relevance(self):
        article = {
            "title": "Company raises funding round",
            "summary": "The company announced a new funding round today.",
            "categories": ["Funding"],
            "github_links": [],
        }
        score = compute_relevance_score(article)
        assert score < 0.4

    def test_github_boost(self):
        article_no_gh = {
            "title": "AI tool released",
            "summary": "",
            "categories": [],
            "github_links": [],
        }
        article_with_gh = {
            **article_no_gh,
            "github_links": ["https://github.com/org/repo"],
        }
        score_no = compute_relevance_score(article_no_gh)
        score_with = compute_relevance_score(article_with_gh)
        assert score_with > score_no


class TestParsePublishedDate:
    def test_published_parsed(self):
        entry = SimpleNamespace(published_parsed=(2026, 5, 15, 10, 0, 0, 3, 135, 0))
        result = parse_published_date(entry)
        assert result == datetime(2026, 5, 15, 10, 0, 0, tzinfo=UTC)

    def test_fallback_updated(self):
        entry = SimpleNamespace(
            published_parsed=None,
            updated_parsed=(2026, 5, 14, 8, 0, 0, 2, 134, 0),
        )
        result = parse_published_date(entry)
        assert result == datetime(2026, 5, 14, 8, 0, 0, tzinfo=UTC)

    def test_none_when_missing(self):
        entry = SimpleNamespace(published_parsed=None, updated_parsed=None)
        assert parse_published_date(entry) is None


# --- Integration tests: TechCrunchSource.crawl ---

class TestTechCrunchSourceCrawl:
    def test_crawl_filters_by_date(self):
        entry_in_range = _make_entry(
            published_parsed=(2026, 5, 15, 10, 0, 0, 3, 135, 0)
        )
        entry_out_of_range = _make_entry(
            title="Old Article",
            published_parsed=(2026, 4, 1, 10, 0, 0, 1, 91, 0),
        )
        feed = _make_feed(entries=[entry_in_range, entry_out_of_range])

        with patch("scripts.techcrunch_crawler.fetch_feed", return_value=feed):
            source = TechCrunchSource()
            articles = source.crawl(
                since=datetime(2026, 5, 10, tzinfo=UTC),
                until=datetime(2026, 5, 20, tzinfo=UTC),
            )

        assert len(articles) == 1
        assert articles[0]["title"] == "Test Article"

    def test_crawl_extracts_github_links(self):
        entry = _make_entry(
            content_html="<p>See https://github.com/pytorch/pytorch for details</p>"
        )
        feed = _make_feed(entries=[entry])

        with patch("scripts.techcrunch_crawler.fetch_feed", return_value=feed):
            source = TechCrunchSource()
            articles = source.crawl(
                since=datetime(2026, 5, 10, tzinfo=UTC),
                until=datetime(2026, 5, 20, tzinfo=UTC),
            )

        assert "https://github.com/pytorch/pytorch" in articles[0]["github_links"]

    def test_crawl_extracts_entities(self):
        entry = _make_entry(title="OpenAI and LangChain Release New Tools")
        feed = _make_feed(entries=[entry])

        with patch("scripts.techcrunch_crawler.fetch_feed", return_value=feed):
            source = TechCrunchSource()
            articles = source.crawl(
                since=datetime(2026, 5, 10, tzinfo=UTC),
                until=datetime(2026, 5, 20, tzinfo=UTC),
            )

        entities = articles[0]["entities"]
        assert "OpenAI" in entities
        assert "LangChain" in entities

    def test_crawl_strips_html_from_summary(self):
        entry = _make_entry(summary="<p>Hello <b>world</b></p>")
        feed = _make_feed(entries=[entry])

        with patch("scripts.techcrunch_crawler.fetch_feed", return_value=feed):
            source = TechCrunchSource()
            articles = source.crawl(
                since=datetime(2026, 5, 10, tzinfo=UTC),
                until=datetime(2026, 5, 20, tzinfo=UTC),
            )

        assert "<" not in articles[0]["summary"]
        assert "Hello world" == articles[0]["summary"]


# --- Output structure tests ---

class TestBuildOutput:
    def test_structure(self):
        articles = [
            {
                "title": "Test",
                "url": "https://techcrunch.com/test",
                "published_at": "2026-05-15T10:00:00Z",
                "categories": ["AI"],
                "summary": "Test",
                "github_links": ["https://github.com/org/repo"],
                "entities": ["OpenAI"],
                "relevance_score": 0.8,
            },
            {
                "title": "Low relevance",
                "url": "https://techcrunch.com/low",
                "published_at": "2026-05-15T11:00:00Z",
                "categories": [],
                "summary": "Funding",
                "github_links": [],
                "entities": [],
                "relevance_score": 0.2,
            },
        ]
        now = datetime(2026, 5, 19, 10, 0, 0, tzinfo=UTC)
        output = build_output(articles, crawled_at=now)

        assert output["source"] == "techcrunch"
        assert output["week"] == week_slug(now)
        assert output["crawled_at"] == "2026-05-19T10:00:00Z"
        assert output["metadata"]["total_articles"] == 2
        assert output["metadata"]["relevant_articles"] == 1
        assert output["metadata"]["github_links_found"] == 1
        assert len(output["articles"]) == 2


# --- DataSource protocol tests ---

class TestDataSourceProtocol:
    def test_get_name(self):
        source = TechCrunchSource()
        assert source.get_name() == "techcrunch"

    def test_get_rate_limits(self):
        source = TechCrunchSource()
        limits = source.get_rate_limits()
        assert "requests_per_minute" in limits
        assert limits["requests_per_minute"] == 10
