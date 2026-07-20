"""Tests for TechCrunch RSS crawler — no live feed fetching."""

from __future__ import annotations

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import pytest

import scripts.techcrunch_crawler as techcrunch_crawler
from scripts.techcrunch_crawler import (
    DEFAULT_FETCH_RETRIES,
    DEFAULT_FETCH_TIMEOUT_SECONDS,
    DEFAULT_SOURCES_PATH,
    NewsFeedSource,
    NewsSourceConfig,
    TechCrunchSource,
    build_output,
    compute_relevance_score,
    crawl_sources_parallel,
    dedupe_articles,
    extract_entities,
    extract_github_urls,
    fetch_feed,
    iso_timestamp,
    load_source_configs,
    parse_published_date,
    source_config_checksum,
    source_reuse_decisions,
    validate_feed_url,
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
        entry_in_range = _make_entry(published_parsed=(2026, 5, 15, 10, 0, 0, 3, 135, 0))
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
        assert articles[0]["source"] == "techcrunch"
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
        assert output["metadata"]["source_count"] == 1
        assert output["metadata"]["total_articles"] == 2
        assert output["metadata"]["relevant_articles"] == 1
        assert output["metadata"]["github_links_found"] == 1
        assert output["metadata"]["errors"] == []
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


# --- Config and parallel crawl tests ---


class TestExternalNewsSources:
    def test_load_default_source_configs(self):
        sources = load_source_configs(DEFAULT_SOURCES_PATH)
        names = {source.name for source in sources}

        assert "techcrunch" in names
        assert "nvidia_blog" in names
        assert "hugging_face_blog" in names
        assert "mit_technology_review" in names
        assert "github_blog" in names

    def test_source_reuse_decisions_reuses_successful_same_day_sources_and_refreshes_failed(self):
        sources = [
            NewsSourceConfig("techcrunch", "https://techcrunch.com/feed/"),
            NewsSourceConfig("github-blog", "https://github.blog/feed/"),
        ]
        since = datetime(2026, 5, 11, tzinfo=UTC)
        until = datetime(2026, 5, 18, tzinfo=UTC)
        payload = {
            "week": "2026-W21",
            "crawled_at": "2026-05-18T08:00:00Z",
            "crawl_window": {"since": iso_timestamp(since), "until": iso_timestamp(until)},
            "articles": [
                {"source": "techcrunch", "title": "Reused", "published_at": "2026-05-17T00:00:00Z"}
            ],
            "metadata": {
                "source_config_checksum": source_config_checksum(sources),
                "source_status": [
                    {"source": "techcrunch", "success": True},
                    {"source": "github-blog", "success": False},
                ],
            },
        }

        reused, to_crawl, reused_statuses, decisions = source_reuse_decisions(
            payload,
            sources,
            week="2026-W21",
            run_date=datetime(2026, 5, 18, tzinfo=UTC).date(),
            since=since,
            until=until,
            policy="reuse-same-day",
            current_config_checksum=source_config_checksum(sources),
            current_code_sha=None,
        )

        assert [article["title"] for article in reused] == ["Reused"]
        assert [source.name for source in to_crawl] == ["github-blog"]
        assert reused_statuses[0]["reused_same_day"] is True
        assert {decision["source"]: decision["decision"] for decision in decisions} == {
            "techcrunch": "reuse",
            "github-blog": "refresh",
        }

    def test_source_reuse_decisions_refreshes_malformed_article_artifact(self):
        sources = [NewsSourceConfig("techcrunch", "https://techcrunch.com/feed/")]
        since = datetime(2026, 5, 11, tzinfo=UTC)
        until = datetime(2026, 5, 18, tzinfo=UTC)
        payload = {
            "week": "2026-W21",
            "crawled_at": "2026-05-18T08:00:00Z",
            "crawl_window": {"since": iso_timestamp(since), "until": iso_timestamp(until)},
            "articles": [{"source": "techcrunch", "sources": 1, "title": "Malformed"}],
            "metadata": {
                "source_config_checksum": source_config_checksum(sources),
                "source_status": [{"source": "techcrunch", "success": True}],
            },
        }

        reused, to_crawl, reused_statuses, decisions = source_reuse_decisions(
            payload,
            sources,
            week="2026-W21",
            run_date=datetime(2026, 5, 18, tzinfo=UTC).date(),
            since=since,
            until=until,
            policy="reuse-same-day",
            current_config_checksum=source_config_checksum(sources),
            current_code_sha=None,
        )

        assert reused == []
        assert [source.name for source in to_crawl] == ["techcrunch"]
        assert reused_statuses == []
        assert decisions == [
            {
                "source": "techcrunch",
                "decision": "refresh",
                "reasons": ["artifact articles malformed"],
            }
        ]

    def test_source_reuse_decisions_refreshes_missing_code_fingerprint_when_required(self):
        sources = [NewsSourceConfig("techcrunch", "https://techcrunch.com/feed/")]
        since = datetime(2026, 5, 11, tzinfo=UTC)
        until = datetime(2026, 5, 18, tzinfo=UTC)
        payload = {
            "week": "2026-W21",
            "crawled_at": "2026-05-18T08:00:00Z",
            "crawl_window": {"since": iso_timestamp(since), "until": iso_timestamp(until)},
            "articles": [
                {"source": "techcrunch", "title": "Reused", "published_at": "2026-05-17T00:00:00Z"}
            ],
            "metadata": {
                "source_config_checksum": source_config_checksum(sources),
                "source_status": [{"source": "techcrunch", "success": True}],
            },
        }

        reused, to_crawl, reused_statuses, decisions = source_reuse_decisions(
            payload,
            sources,
            week="2026-W21",
            run_date=datetime(2026, 5, 18, tzinfo=UTC).date(),
            since=since,
            until=until,
            policy="reuse-same-day",
            current_config_checksum=source_config_checksum(sources),
            current_code_sha="sha",
        )

        assert reused == []
        assert [source.name for source in to_crawl] == ["techcrunch"]
        assert reused_statuses == []
        assert decisions == [
            {
                "source": "techcrunch",
                "decision": "refresh",
                "reasons": ["crawler/config fingerprint mismatch"],
            }
        ]

    @pytest.mark.parametrize(
        "feed_url",
        [
            "http://techcrunch.com/feed/",
            "https://user:pass@techcrunch.com/feed/",
            "https://localhost/feed/",
            "https://127.0.0.1/feed/",
            "https://169.254.169.254/feed/",
            "https://example.com/feed/",
            "https://techcrunch.com:8443/feed/",
        ],
    )
    def test_rejects_invalid_or_unapproved_feed_urls(self, feed_url):
        with pytest.raises(ValueError):
            validate_feed_url(feed_url)

    def test_load_source_configs_rejects_unapproved_hosts(self):
        payload = json.dumps(
            [
                {
                    "name": "evil",
                    "feed_url": "https://example.com/feed.xml",
                    "requests_per_minute": 10,
                }
            ]
        )

        with patch("pathlib.Path.read_text", return_value=payload):
            with pytest.raises(ValueError, match="not approved"):
                load_source_configs(DEFAULT_SOURCES_PATH)

    def test_fetch_feed_uses_explicit_timeout(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return None

            def read(self):
                return b"<rss><channel></channel></rss>"

        feed = _make_feed()
        with (
            patch(
                "scripts.techcrunch_crawler.urlopen",
                return_value=FakeResponse(),
            ) as mock_urlopen,
            patch("scripts.techcrunch_crawler.feedparser.parse", return_value=feed),
        ):
            result = fetch_feed("https://techcrunch.com/feed/")

        assert result is feed
        assert mock_urlopen.call_args.kwargs["timeout"] == DEFAULT_FETCH_TIMEOUT_SECONDS

    def test_fetch_feed_retries_transient_error_with_backoff(self):
        """A transient network error is retried with backoff and can then succeed."""
        feed = _make_feed()

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return None

            def read(self):
                return b"<rss><channel></channel></rss>"

        attempts = {"n": 0}

        def flaky_urlopen(request, timeout=None):
            attempts["n"] += 1
            if attempts["n"] == 1:
                raise URLError("temporary DNS failure")
            return FakeResponse()

        with (
            patch("scripts.techcrunch_crawler.urlopen", side_effect=flaky_urlopen),
            patch("scripts.techcrunch_crawler.feedparser.parse", return_value=feed),
            patch("scripts.techcrunch_crawler._sleep_before_retry", return_value=0.0) as sleeper,
        ):
            result = fetch_feed("https://techcrunch.com/feed/", retries=2)

        assert result is feed
        assert attempts["n"] == 2
        assert sleeper.called

    def test_fetch_feed_fails_fast_on_non_retryable_status(self):
        """Permanent HTTP errors (e.g. 404) must not be retried."""
        attempts = {"n": 0}

        def not_found(request, timeout=None):
            attempts["n"] += 1
            raise HTTPError("https://techcrunch.com/feed/", 404, "Not Found", {}, None)

        with (
            patch("scripts.techcrunch_crawler.urlopen", side_effect=not_found),
            patch("scripts.techcrunch_crawler._sleep_before_retry") as sleeper,
        ):
            with pytest.raises(HTTPError):
                fetch_feed("https://techcrunch.com/feed/", retries=3)

        assert attempts["n"] == 1
        assert not sleeper.called

    def test_fetch_feed_retries_retryable_status(self):
        """Retryable HTTP statuses (e.g. 503) are retried with backoff."""
        attempts = {"n": 0}

        def unavailable(request, timeout=None):
            attempts["n"] += 1
            raise HTTPError("https://techcrunch.com/feed/", 503, "Unavailable", {}, None)

        with (
            patch("scripts.techcrunch_crawler.urlopen", side_effect=unavailable),
            patch("scripts.techcrunch_crawler._sleep_before_retry", return_value=0.0) as sleeper,
        ):
            with pytest.raises(HTTPError):
                fetch_feed("https://techcrunch.com/feed/", retries=2)

        assert attempts["n"] == 3
        assert sleeper.call_count == 2

    def test_crawl_sources_parallel_combines_sources(self):
        alpha_entry = _make_entry(
            title="Alpha AI framework",
            link="https://example.com/alpha",
            published_parsed=(2026, 5, 16, 10, 0, 0, 4, 136, 0),
        )
        beta_entry = _make_entry(
            title="Beta developer API",
            link="https://example.com/beta",
            published_parsed=(2026, 5, 17, 10, 0, 0, 5, 137, 0),
        )
        feeds = {
            "https://techcrunch.com/feed/": _make_feed(entries=[alpha_entry]),
            "https://github.blog/feed/": _make_feed(entries=[beta_entry]),
        }

        def fake_fetch(url, retries=1, timeout=DEFAULT_FETCH_TIMEOUT_SECONDS):
            return feeds[url]

        sources = [
            NewsSourceConfig("alpha", "https://techcrunch.com/feed/"),
            NewsSourceConfig("beta", "https://github.blog/feed/"),
        ]
        with patch("scripts.techcrunch_crawler.fetch_feed", side_effect=fake_fetch):
            articles, errors, statuses = crawl_sources_parallel(
                sources,
                since=datetime(2026, 5, 10, tzinfo=UTC),
                until=datetime(2026, 5, 20, tzinfo=UTC),
                max_workers=2,
            )

        assert errors == []
        assert {status["source"] for status in statuses} == {"alpha", "beta"}
        assert all(status["success"] for status in statuses)
        assert [article["source"] for article in articles] == ["beta", "alpha"]
        assert {article["title"] for article in articles} == {
            "Alpha AI framework",
            "Beta developer API",
        }

    def test_external_news_output_metadata(self):
        now = datetime(2026, 5, 19, 10, 0, 0, tzinfo=UTC)
        output = build_output(
            [
                {
                    "source": "alpha",
                    "title": "AI framework",
                    "summary": "open source",
                    "categories": [],
                    "github_links": [],
                    "relevance_score": 0.4,
                },
                {
                    "source": "beta",
                    "title": "Developer API",
                    "summary": "sdk",
                    "categories": [],
                    "github_links": [],
                    "relevance_score": 0.4,
                },
            ],
            crawled_at=now,
            source="external_news",
            source_count=2,
            crawl_window={
                "since": "2026-05-12T00:00:00Z",
                "until": "2026-05-19T00:00:00Z",
            },
            source_config_checksum_value="abc123",
            requested_sources=["alpha", "beta", "gamma"],
            source_statuses=[
                {
                    "source": "alpha",
                    "host": "techcrunch.com",
                    "success": True,
                    "attempts": 1,
                    "timeout_seconds": 15,
                    "total_articles": 1,
                    "relevant_articles": 1,
                    "github_links_found": 0,
                    "started_at": "2026-05-19T10:00:00Z",
                    "ended_at": "2026-05-19T10:00:01Z",
                    "duration_seconds": 1.0,
                    "error_class": "",
                    "error_message": "",
                },
                {
                    "source": "beta",
                    "host": "github.blog",
                    "success": True,
                    "attempts": 1,
                    "timeout_seconds": 15,
                    "total_articles": 1,
                    "relevant_articles": 1,
                    "github_links_found": 0,
                    "started_at": "2026-05-19T10:00:00Z",
                    "ended_at": "2026-05-19T10:00:01Z",
                    "duration_seconds": 1.0,
                    "error_class": "",
                    "error_message": "",
                },
                {
                    "source": "gamma",
                    "host": "example.com",
                    "success": False,
                    "attempts": 2,
                    "timeout_seconds": 15,
                    "total_articles": 0,
                    "relevant_articles": 0,
                    "github_links_found": 0,
                    "started_at": "2026-05-19T10:00:00Z",
                    "ended_at": "2026-05-19T10:00:01Z",
                    "duration_seconds": 1.0,
                    "error_class": "TimeoutError",
                    "error_message": "timeout",
                },
            ],
            errors=[{"source": "gamma", "error": "timeout"}],
        )

        assert output["schema_version"] == 2
        assert output["source"] == "external_news"
        assert output["metadata"]["source_count"] == 2
        assert output["metadata"]["source_config_checksum"] == "abc123"
        assert output["metadata"]["sources_requested"] == ["alpha", "beta", "gamma"]
        assert output["metadata"]["sources_succeeded"] == ["alpha", "beta"]
        assert output["metadata"]["sources_failed"] == ["gamma"]
        assert output["metadata"]["artifact_checksum"]
        assert output["metadata"]["sources_with_articles"] == {"alpha": 1, "beta": 1}
        assert output["metadata"]["errors"] == [{"source": "gamma", "error": "timeout"}]

    def test_dedupe_articles_preserves_sources(self):
        articles, deduped = dedupe_articles(
            [
                {
                    "source": "alpha",
                    "title": "Same story",
                    "url": "https://example.com/story/",
                    "published_at": "2026-05-15T10:00:00Z",
                    "github_links": ["https://github.com/a/b"],
                    "relevance_score": 0.4,
                },
                {
                    "source": "beta",
                    "title": "Same story mirror",
                    "url": "https://example.com/story",
                    "published_at": "2026-05-15T10:00:00Z",
                    "github_links": ["https://github.com/c/d"],
                    "relevance_score": 0.8,
                },
            ]
        )

        assert deduped == 1
        assert len(articles) == 1
        assert articles[0]["sources"] == ["alpha", "beta"]
        assert articles[0]["relevance_score"] == 0.8

    def test_failed_source_reports_bounded_retry_attempts(self):
        source = NewsSourceConfig("alpha", "https://techcrunch.com/feed/")
        with patch("scripts.techcrunch_crawler.fetch_feed", side_effect=TimeoutError("boom")):
            articles, errors, statuses = crawl_sources_parallel(
                [source],
                since=datetime(2026, 5, 10, tzinfo=UTC),
                until=datetime(2026, 5, 20, tzinfo=UTC),
                max_workers=1,
            )

        assert articles == []
        assert errors[0]["error_class"] == "TimeoutError"
        assert statuses[0]["attempts"] == DEFAULT_FETCH_RETRIES + 1
        assert statuses[0]["success"] is False

    def test_failed_feed_fetch_records_attempts_on_source(self):
        source = NewsFeedSource(NewsSourceConfig("alpha", "https://techcrunch.com/feed/"))

        with patch("scripts.techcrunch_crawler.fetch_feed", side_effect=TimeoutError("boom")):
            with pytest.raises(TimeoutError):
                source.crawl(
                    since=datetime(2026, 5, 10, tzinfo=UTC),
                    until=datetime(2026, 5, 20, tzinfo=UTC),
                )

        assert source.last_attempts == DEFAULT_FETCH_RETRIES + 1
        assert source.last_timeout_seconds == DEFAULT_FETCH_TIMEOUT_SECONDS


class TestSameDaySourceReuse:
    def _sources(self):
        return [
            NewsSourceConfig("alpha", "https://techcrunch.com/feed/"),
            NewsSourceConfig("beta", "https://github.blog/feed/"),
        ]

    def _article(self, source, title, url):
        return {
            "source": source,
            "title": title,
            "url": url,
            "published_at": "2026-05-19T10:00:00Z",
            "categories": ["AI"],
            "summary": "open source AI framework",
            "github_links": [],
            "entities": [],
            "relevance_score": 0.6,
        }

    def _write_previous(self, path, *, crawled_at, statuses=None, articles=None, sources=None):
        from scripts.techcrunch_crawler import source_config_checksum

        sources = sources or self._sources()
        output = build_output(
            articles or [self._article("alpha", "Alpha", "https://example.com/alpha")],
            crawled_at=crawled_at,
            source="external_news",
            source_count=len(sources),
            crawl_window={
                "since": "2026-05-12T00:00:00Z",
                "until": "2026-05-19T00:00:00Z",
            },
            source_config_checksum_value=source_config_checksum(sources),
            requested_sources=[source.name for source in sources],
            source_statuses=statuses
            or [
                {
                    "source": "alpha",
                    "host": "techcrunch.com",
                    "success": True,
                    "attempts": 1,
                    "timeout_seconds": 15,
                    "total_articles": 1,
                    "relevant_articles": 1,
                    "github_links_found": 0,
                    "started_at": "2026-05-19T08:00:00Z",
                    "ended_at": "2026-05-19T08:00:01Z",
                    "duration_seconds": 1.0,
                    "error_class": "",
                    "error_message": "",
                },
                {
                    "source": "beta",
                    "host": "github.blog",
                    "success": True,
                    "attempts": 1,
                    "timeout_seconds": 15,
                    "total_articles": 0,
                    "relevant_articles": 0,
                    "github_links_found": 0,
                    "started_at": "2026-05-19T08:00:00Z",
                    "ended_at": "2026-05-19T08:00:01Z",
                    "duration_seconds": 1.0,
                    "error_class": "",
                    "error_message": "",
                },
            ],
            source_reuse_summary=[],
            source_artifact_provenance=[],
            run_id="111",
        )
        path.write_text(json.dumps(output), encoding="utf-8")

    def test_reuses_successful_same_day_sources(self, tmp_path):
        from scripts.techcrunch_crawler import plan_source_reuse, source_config_checksum

        sources = self._sources()
        path = tmp_path / "external.json"
        now = datetime(2026, 5, 19, 9, 0, tzinfo=UTC)
        self._write_previous(path, crawled_at=now)

        reused, pending, summary, provenance, _ = plan_source_reuse(
            path,
            sources,
            now=now,
            since=datetime(2026, 5, 12, tzinfo=UTC),
            until=datetime(2026, 5, 19, tzinfo=UTC),
            config_checksum=source_config_checksum(sources),
        )

        assert [item["action"] for item in summary] == ["reused", "reused"]
        assert pending == []
        assert [article["title"] for article in reused] == ["Alpha"]
        assert provenance[0]["original_run_id"] == "111"
        assert provenance[0]["content_checksum"]

    def test_rejects_yesterday_artifact_as_stale(self, tmp_path):
        from scripts.techcrunch_crawler import plan_source_reuse, source_config_checksum

        sources = self._sources()
        path = tmp_path / "external.json"
        self._write_previous(path, crawled_at=datetime(2026, 5, 18, 9, 0, tzinfo=UTC))

        reused, pending, summary, _, _ = plan_source_reuse(
            path,
            sources,
            now=datetime(2026, 5, 19, 9, 0, tzinfo=UTC),
            since=datetime(2026, 5, 12, tzinfo=UTC),
            until=datetime(2026, 5, 19, tzinfo=UTC),
            config_checksum=source_config_checksum(sources),
        )

        assert reused == []
        assert [source.name for source in pending] == ["alpha", "beta"]
        assert {item["action"] for item in summary} == {"stale"}

    def test_rejects_missing_code_fingerprint_when_required(self, tmp_path):
        from scripts.techcrunch_crawler import plan_source_reuse, source_config_checksum

        sources = self._sources()
        path = tmp_path / "external.json"
        now = datetime(2026, 5, 19, 9, 0, tzinfo=UTC)
        self._write_previous(path, crawled_at=now)

        reused, pending, summary, _, _ = plan_source_reuse(
            path,
            sources,
            now=now,
            since=datetime(2026, 5, 12, tzinfo=UTC),
            until=datetime(2026, 5, 19, tzinfo=UTC),
            config_checksum=source_config_checksum(sources),
            current_code_sha="sha",
        )

        assert reused == []
        assert [source.name for source in pending] == ["alpha", "beta"]
        assert {item["action"] for item in summary} == {"stale"}
        assert all("crawler/config fingerprint mismatch" in item["reasons"] for item in summary)

    def test_partial_rerun_reuses_success_and_fetches_failed(self, tmp_path):
        from scripts.techcrunch_crawler import plan_source_reuse, source_config_checksum

        sources = self._sources()
        path = tmp_path / "external.json"
        self._write_previous(
            path,
            crawled_at=datetime(2026, 5, 19, 9, 0, tzinfo=UTC),
            statuses=[
                {
                    "source": "alpha",
                    "host": "techcrunch.com",
                    "success": True,
                    "attempts": 1,
                    "timeout_seconds": 15,
                    "total_articles": 1,
                    "relevant_articles": 1,
                    "github_links_found": 0,
                    "started_at": "2026-05-19T08:00:00Z",
                    "ended_at": "2026-05-19T08:00:01Z",
                    "duration_seconds": 1.0,
                    "error_class": "",
                    "error_message": "",
                },
                {
                    "source": "beta",
                    "host": "github.blog",
                    "success": False,
                    "attempts": 2,
                    "timeout_seconds": 15,
                    "total_articles": 0,
                    "relevant_articles": 0,
                    "github_links_found": 0,
                    "started_at": "2026-05-19T08:00:00Z",
                    "ended_at": "2026-05-19T08:00:01Z",
                    "duration_seconds": 1.0,
                    "error_class": "TimeoutError",
                    "error_message": "timeout",
                },
            ],
        )

        reused, pending, summary, _, _ = plan_source_reuse(
            path,
            sources,
            now=datetime(2026, 5, 19, 10, 0, tzinfo=UTC),
            since=datetime(2026, 5, 12, tzinfo=UTC),
            until=datetime(2026, 5, 19, tzinfo=UTC),
            config_checksum=source_config_checksum(sources),
        )

        assert [article["source"] for article in reused] == ["alpha"]
        assert [source.name for source in pending] == ["beta"]
        assert {item["source"]: item["action"] for item in summary} == {
            "alpha": "reused",
            "beta": "failed",
        }

    def test_deterministic_fan_in_dedupes_reused_and_refreshed_articles(self):
        first = self._article("alpha", "Same", "https://example.com/story/")
        second = self._article("beta", "Same mirror", "https://example.com/story")
        deduped_once, count_once = dedupe_articles([first, second])
        deduped_twice, count_twice = dedupe_articles([second, first])

        assert count_once == count_twice == 1
        assert deduped_once == deduped_twice
        assert deduped_once[0]["sources"] == ["alpha", "beta"]


def test_main_emits_observability_ledger() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        base = Path(tmpdir)
        sources_path = base / "sources.json"
        output_path = base / "2026-W21-external-news.json"
        sources_path.write_text(
            json.dumps(
                [
                    {"name": "alpha", "feed_url": "https://techcrunch.com/feed/"},
                    {"name": "beta", "feed_url": "https://github.blog/feed/"},
                ]
            ),
            encoding="utf-8",
        )
        statuses = [
            {
                "source": "alpha",
                "host": "techcrunch.com",
                "success": True,
                "attempts": 1,
                "timeout_seconds": 15,
                "total_articles": 1,
                "relevant_articles": 1,
                "github_links_found": 1,
                "started_at": "2026-05-19T08:00:00Z",
                "ended_at": "2026-05-19T08:00:01Z",
                "duration_seconds": 1.0,
                "error_class": "",
                "error_message": "",
            },
            {
                "source": "beta",
                "host": "github.blog",
                "success": True,
                "attempts": 2,
                "timeout_seconds": 15,
                "total_articles": 1,
                "relevant_articles": 1,
                "github_links_found": 0,
                "started_at": "2026-05-19T08:00:00Z",
                "ended_at": "2026-05-19T08:00:02Z",
                "duration_seconds": 2.0,
                "error_class": "",
                "error_message": "",
            },
        ]
        articles = [
            {
                "source": "alpha",
                "title": "Alpha",
                "url": "https://example.com/alpha",
                "published_at": "2026-05-19T10:00:00Z",
                "categories": ["AI"],
                "summary": "alpha summary",
                "github_links": ["https://github.com/octo/alpha"],
                "entities": ["Alpha"],
                "relevance_score": 0.8,
            }
        ]
        with (
            patch.object(
                techcrunch_crawler, "crawl_sources_parallel", return_value=(articles, [], statuses)
            ),
            patch.object(techcrunch_crawler, "emit_ledger") as emit_mock,
            patch.object(techcrunch_crawler, "print"),
        ):
            rc = techcrunch_crawler.main(
                [
                    "--sources",
                    sources_path.as_posix(),
                    "--output",
                    output_path.as_posix(),
                    "--since",
                    "2026-05-12",
                    "--until",
                    "2026-05-19",
                ]
            )

    assert rc == 0
    ledger = emit_mock.call_args.args[0]
    assert ledger.schema_version == "observability_v1"
    assert ledger.crawl_metrics[0].source_type == "external-news"
    assert ledger.crawl_metrics[0].api_calls == 3
    assert ledger.crawl_metrics[0].duration_p95_seconds == 2.0
