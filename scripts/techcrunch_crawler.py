#!/usr/bin/env python3
"""External news RSS crawler with entity extraction for SquadScope.

Fetches configured RSS feeds in parallel, extracts structured metadata,
GitHub URLs, and entities (company/project names).

Usage:
    python scripts/techcrunch_crawler.py [--topic ai-ml] \
        [--output data/raw/ai-ml/2026-W21-external-news.json] [--since 2026-05-11]
"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import feedparser

from scripts.topic_paths import raw_dir

FEED_URL = "https://techcrunch.com/feed/"
DEFAULT_SOURCES_PATH = Path("config/external_news_sources.json")
DEFAULT_FETCH_TIMEOUT_SECONDS = 15
DEFAULT_FETCH_RETRIES = 1
DEFAULT_MAX_WORKERS = 8
CANONICAL_SCHEMA_VERSION = 2
APPROVED_FEED_HOSTS = frozenset({
    "techcrunch.com",
    "blogs.nvidia.com",
    "huggingface.co",
    "www.technologyreview.com",
    "github.blog",
})

GITHUB_URL_RE = re.compile(
    r"https?://github\.com/[a-zA-Z0-9_.\-]+/[a-zA-Z0-9_.\-]+"
)

TECH_KEYWORDS = {
    "ai", "ml", "machine learning", "deep learning", "open-source",
    "open source", "github", "developer", "api", "framework", "sdk",
    "llm", "gpt", "model", "neural", "transformer", "cloud", "devops",
    "kubernetes", "docker", "rust", "python", "javascript", "typescript",
    "golang", "database", "vector", "embedding", "agent", "rag",
    "fine-tuning", "inference", "startup", "oss",
}

# Common lowercase words that should not be treated as entities
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "has", "have", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "this", "that", "these", "those",
    "it", "its", "new", "how", "why", "what", "when", "where", "who",
    "all", "just", "more", "most", "some", "any", "no", "not", "than",
    "too", "very", "also", "about", "up", "out", "into", "over", "after",
    "before", "between", "under", "again", "here", "there", "now", "then",
    "once", "well", "back", "still", "even", "big", "first", "last",
    "next", "says", "said", "gets", "got", "makes", "made", "takes",
    "took", "goes", "went", "comes", "came", "wants", "launches",
    "raises", "builds", "looks", "like", "use", "using", "used",
}


@dataclass(frozen=True, slots=True)
class NewsSourceConfig:
    """Configuration for one external RSS source."""

    name: str
    feed_url: str
    requests_per_minute: int = 10

    def __post_init__(self) -> None:
        validate_feed_url(self.feed_url)

    @property
    def host(self) -> str:
        """Return the normalized feed host."""
        return (urlparse(self.feed_url).hostname or "").rstrip(".").lower()


def validate_feed_url(url: str) -> None:
    """Validate an external RSS URL against the approved egress allowlist."""
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https":
        raise ValueError(f"External RSS feed URL must use HTTPS: {url}")
    if parsed.username or parsed.password:
        raise ValueError(f"External RSS feed URL must not include credentials: {url}")
    host = (parsed.hostname or "").rstrip(".").lower()
    if not host:
        raise ValueError(f"External RSS feed URL must include a hostname: {url}")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"External RSS feed URL has an invalid port: {url}") from exc
    if port not in (None, 443):
        raise ValueError(f"External RSS feed URL must not use unexpected ports: {url}")
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise ValueError(f"External RSS feed URL must not target local hosts: {url}")
    try:
        ip_addr = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        if ip_addr.is_private or ip_addr.is_loopback or ip_addr.is_link_local:
            raise ValueError(
                f"External RSS feed URL must not target private/local IPs: {url}"
            )
    if host not in APPROVED_FEED_HOSTS:
        approved = ", ".join(sorted(APPROVED_FEED_HOSTS))
        raise ValueError(
            f"External RSS feed host is not approved: {host} (approved: {approved})"
        )


def load_source_configs(path: Path = DEFAULT_SOURCES_PATH) -> list[NewsSourceConfig]:
    """Load external RSS source config from JSON."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Expected a list of source configs in {path}")

    sources: list[NewsSourceConfig] = []
    seen_names: set[str] = set()
    for raw in payload:
        if not isinstance(raw, dict):
            raise ValueError(f"Invalid source config in {path}: {raw!r}")
        name = str(raw.get("name", "")).strip()
        feed_url = str(raw.get("feed_url", "")).strip()
        if not name or not feed_url:
            raise ValueError(f"Source configs require name and feed_url: {raw!r}")
        if name in seen_names:
            raise ValueError(f"Duplicate external news source name: {name}")
        seen_names.add(name)
        sources.append(NewsSourceConfig(
            name=name,
            feed_url=feed_url,
            requests_per_minute=int(raw.get("requests_per_minute", 10)),
        ))
    return sources


def source_config_checksum(sources: list[NewsSourceConfig]) -> str:
    """Return a stable checksum for the effective source config."""
    canonical = [
        {
            "feed_url": source.feed_url,
            "name": source.name,
            "requests_per_minute": source.requests_per_minute,
        }
        for source in sorted(sources, key=lambda item: item.name)
    ]
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def iso_timestamp(value: datetime) -> str:
    """Format datetime as ISO 8601 UTC string."""
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def week_slug(value: datetime) -> str:
    """Return ISO week string like '2026-W21'."""
    year, week, _ = value.isocalendar()
    return f"{year}-W{week:02d}"


def extract_github_urls(text: str) -> list[str]:
    """Extract unique GitHub repository URLs from text."""
    if not text:
        return []
    urls = GITHUB_URL_RE.findall(text)
    # Deduplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for url in urls:
        # Strip trailing periods/commas that may be captured
        url = url.rstrip(".,;)")
        if url not in seen:
            seen.add(url)
            result.append(url)
    return result


def extract_entities(title: str) -> list[str]:
    """Extract likely entity names (companies, projects) from a title.

    Heuristic: capitalized words that aren't common English words.
    """
    if not title:
        return []
    words = re.findall(r"\b[A-Z][a-zA-Z0-9]*(?:\.[a-zA-Z]+)*\b", title)
    entities: list[str] = []
    seen: set[str] = set()
    for word in words:
        lower = word.lower()
        if lower in STOP_WORDS:
            continue
        if len(word) < 2:
            continue
        if word not in seen:
            seen.add(word)
            entities.append(word)
    return entities


def compute_relevance_score(article: dict[str, Any]) -> float:
    """Compute a 0-1 relevance score based on tech/OSS keyword density."""
    text = " ".join([
        article.get("title", ""),
        article.get("summary", ""),
        " ".join(article.get("categories", [])),
    ]).lower()

    if not text.strip():
        return 0.0

    matches = sum(1 for kw in TECH_KEYWORDS if kw in text)
    # Normalize: cap at 1.0, scale so 5+ keywords = 1.0
    score = min(matches / 5.0, 1.0)
    # Boost if GitHub links found
    if article.get("github_links"):
        score = min(score + 0.2, 1.0)
    return round(score, 2)


def parse_published_date(entry: Any) -> datetime | None:
    """Parse the published date from a feedparser entry."""
    published_parsed = getattr(entry, "published_parsed", None)
    if published_parsed:
        return datetime(*published_parsed[:6], tzinfo=UTC)
    # Fallback: try updated_parsed
    updated_parsed = getattr(entry, "updated_parsed", None)
    if updated_parsed:
        return datetime(*updated_parsed[:6], tzinfo=UTC)
    return None


def fetch_feed(
    url: str = FEED_URL,
    retries: int = DEFAULT_FETCH_RETRIES,
    timeout: int = DEFAULT_FETCH_TIMEOUT_SECONDS,
) -> Any:
    """Fetch and parse RSS feed with bounded retries and an explicit timeout."""
    validate_feed_url(url)
    if timeout <= 0:
        raise ValueError("RSS fetch timeout must be greater than zero")
    for attempt in range(retries + 1):
        try:
            request = Request(url, headers={"User-Agent": "SquadScope RSS crawler"})
            with urlopen(request, timeout=timeout) as response:
                feed = feedparser.parse(response.read())
            setattr(feed, "squad_fetch_attempts", attempt + 1)
            setattr(feed, "squad_fetch_timeout_seconds", timeout)
        except Exception:
            if attempt < retries:
                time.sleep(2)
                continue
            raise
        if feed.bozo and not feed.entries:
            if attempt < retries:
                time.sleep(2)
                continue
            # Return partial result even on failure
            setattr(feed, "squad_fetch_attempts", attempt + 1)
            setattr(feed, "squad_fetch_timeout_seconds", timeout)
            return feed
        return feed
    return feed  # pragma: no cover


class NewsFeedSource:
    """RSS data source following the DataSource protocol."""

    def __init__(self, config: NewsSourceConfig) -> None:
        self.config = config
        self.last_attempts = 0
        self.last_timeout_seconds = DEFAULT_FETCH_TIMEOUT_SECONDS

    def get_name(self) -> str:
        return self.config.name

    def get_rate_limits(self) -> dict:
        return {"requests_per_minute": self.config.requests_per_minute}

    def crawl(
        self,
        since: datetime,
        until: datetime,
        feed_url: str | None = None,
    ) -> list[dict[str, Any]]:
        """Crawl an RSS feed and return structured articles."""
        resolved_feed_url = feed_url or self.config.feed_url
        validate_feed_url(resolved_feed_url)
        try:
            feed = fetch_feed(resolved_feed_url)
        except Exception:
            self.last_attempts = DEFAULT_FETCH_RETRIES + 1
            self.last_timeout_seconds = DEFAULT_FETCH_TIMEOUT_SECONDS
            raise
        self.last_attempts = int(getattr(feed, "squad_fetch_attempts", 1))
        self.last_timeout_seconds = int(
            getattr(feed, "squad_fetch_timeout_seconds", DEFAULT_FETCH_TIMEOUT_SECONDS)
        )
        articles: list[dict[str, Any]] = []

        for entry in feed.entries:
            pub_date = parse_published_date(entry)
            if pub_date is None:
                continue
            if pub_date < since or pub_date >= until:
                continue

            # Get content for GitHub URL extraction
            content_text = ""
            if hasattr(entry, "content") and entry.content:
                content_text = entry.content[0].get("value", "")
            elif hasattr(entry, "summary"):
                content_text = entry.summary or ""

            categories = [
                tag.term for tag in getattr(entry, "tags", [])
                if hasattr(tag, "term")
            ]

            summary = getattr(entry, "summary", "") or ""
            # Strip HTML tags from summary
            summary = re.sub(r"<[^>]+>", "", summary).strip()
            if len(summary) > 500:
                summary = summary[:497] + "..."

            article: dict[str, Any] = {
                "source": self.get_name(),
                "title": getattr(entry, "title", ""),
                "url": getattr(entry, "link", ""),
                "published_at": iso_timestamp(pub_date),
                "categories": categories,
                "summary": summary,
                "github_links": extract_github_urls(content_text),
                "entities": extract_entities(getattr(entry, "title", "")),
            }
            article["relevance_score"] = compute_relevance_score(article)
            articles.append(article)

        return articles


class TechCrunchSource(NewsFeedSource):
    """Backward-compatible TechCrunch RSS source."""

    def __init__(self) -> None:
        super().__init__(NewsSourceConfig("techcrunch", FEED_URL, 10))


def crawl_sources_parallel(
    sources: list[NewsSourceConfig],
    since: datetime,
    until: datetime,
    max_workers: int | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[dict[str, Any]]]:
    """Crawl configured RSS sources concurrently and return articles, errors, statuses."""
    if not sources:
        return [], [], []

    if max_workers is not None and max_workers < 1:
        raise ValueError("--max-workers must be at least 1")
    workers = min(max_workers or len(sources), len(sources), DEFAULT_MAX_WORKERS)
    articles: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    statuses: list[dict[str, Any]] = []

    def crawl_one(source: NewsSourceConfig) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, str] | None]:
        started = datetime.now(UTC)
        source_client = NewsFeedSource(source)
        status: dict[str, Any] = {
            "source": source.name,
            "host": source.host,
            "started_at": iso_timestamp(started),
            "timeout_seconds": DEFAULT_FETCH_TIMEOUT_SECONDS,
            "attempts": 0,
            "total_articles": 0,
            "relevant_articles": 0,
            "github_links_found": 0,
            "success": False,
            "error_class": "",
            "error_message": "",
        }
        try:
            source_articles = source_client.crawl(since, until)
            status["attempts"] = source_client.last_attempts or 1
            status["timeout_seconds"] = source_client.last_timeout_seconds
            status["total_articles"] = len(source_articles)
            status["relevant_articles"] = sum(
                1 for article in source_articles
                if article.get("relevance_score", 0) >= 0.4
            )
            github_links: set[str] = set()
            for article in source_articles:
                github_links.update(article.get("github_links", []))
            status["github_links_found"] = len(github_links)
            status["success"] = True
            return source_articles, status, None
        except Exception as exc:  # pragma: no cover - defensive around network/parser failures
            status["attempts"] = source_client.last_attempts or (DEFAULT_FETCH_RETRIES + 1)
            status["error_class"] = exc.__class__.__name__
            status["error_message"] = str(exc)
            error = {
                "source": source.name,
                "error_class": exc.__class__.__name__,
                "error": str(exc),
            }
            return [], status, error
        finally:
            ended = datetime.now(UTC)
            status["ended_at"] = iso_timestamp(ended)
            status["duration_seconds"] = round((ended - started).total_seconds(), 3)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(crawl_one, source): source
            for source in sources
        }
        for future in as_completed(futures):
            source_articles, status, error = future.result()
            articles.extend(source_articles)
            statuses.append(status)
            if error:
                errors.append(error)

    articles.sort(
        key=lambda article: (
            article.get("published_at", ""),
            article.get("source", ""),
            article.get("url", ""),
            article.get("title", ""),
        ),
        reverse=True,
    )
    statuses.sort(key=lambda status: status["source"])
    errors.sort(key=lambda error: error["source"])
    for status in statuses:
        state = "ok" if status["success"] else f"failed:{status['error_class']}"
        print(
            "[external-news] "
            f"{status['source']} host={status['host']} status={state} "
            f"duration={status['duration_seconds']:.3f}s attempts={status['attempts']} "
            f"articles={status['total_articles']} relevant={status['relevant_articles']} "
            f"github_links={status['github_links_found']}",
            file=sys.stderr,
        )
    return articles, errors, statuses


def _normalized_article_url(url: str) -> str:
    """Normalize a URL for cross-source dedupe."""
    if not url:
        return ""
    parsed = urlparse(url.strip())
    host = (parsed.netloc or "").lower()
    path = parsed.path.rstrip("/")
    return f"{parsed.scheme.lower()}://{host}{path}"


def dedupe_articles(articles: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Deduplicate mirrored articles by URL while preserving provenance."""
    grouped: dict[str, dict[str, Any]] = {}
    duplicates = 0
    for article in sorted(
        articles,
        key=lambda item: (
            item.get("published_at", ""),
            item.get("source", ""),
            item.get("url", ""),
            item.get("title", ""),
        ),
        reverse=True,
    ):
        key = _normalized_article_url(str(article.get("url", "")))
        if not key:
            key = "|".join([
                str(article.get("source", "")),
                str(article.get("published_at", "")),
                str(article.get("title", "")).lower(),
            ])
        if key not in grouped:
            current = dict(article)
            current["sources"] = sorted({
                str(article.get("source", "")) or "unknown",
                *[str(s) for s in article.get("sources", [])],
            })
            grouped[key] = current
            continue
        duplicates += 1
        existing = grouped[key]
        existing_sources = set(existing.get("sources", []))
        existing_sources.add(str(article.get("source", "")) or "unknown")
        existing_sources.update(str(s) for s in article.get("sources", []))
        existing["sources"] = sorted(existing_sources)
        existing["relevance_score"] = max(
            float(existing.get("relevance_score", 0)),
            float(article.get("relevance_score", 0)),
        )
        existing_links = list(existing.get("github_links", []))
        for link in article.get("github_links", []):
            if link not in existing_links:
                existing_links.append(link)
        existing["github_links"] = existing_links
    deduped = list(grouped.values())
    deduped.sort(
        key=lambda article: (
            article.get("published_at", ""),
            article.get("source", ""),
            article.get("url", ""),
            article.get("title", ""),
        ),
        reverse=True,
    )
    return deduped, duplicates


def _checksum_payload(output: dict[str, Any]) -> dict[str, Any]:
    """Return the deterministic subset covered by artifact_checksum."""
    metadata = dict(output.get("metadata", {}))
    metadata.pop("artifact_checksum", None)
    payload = dict(output)
    payload["metadata"] = metadata
    payload.pop("crawled_at", None)
    return payload


def artifact_checksum(output: dict[str, Any]) -> str:
    """Return a stable checksum for the canonical artifact content."""
    payload = json.dumps(
        _checksum_payload(output),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_output(
    articles: list[dict[str, Any]],
    crawled_at: datetime,
    *,
    source: str = "techcrunch",
    source_count: int = 1,
    crawl_window: dict[str, str] | None = None,
    source_config_checksum_value: str | None = None,
    requested_sources: list[str] | None = None,
    source_statuses: list[dict[str, Any]] | None = None,
    errors: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Build the final output structure with metadata."""
    articles, dedupe_count = dedupe_articles(articles)
    relevant = [a for a in articles if a["relevance_score"] >= 0.4]
    all_github_links = set()
    for a in articles:
        all_github_links.update(a.get("github_links", []))

    statuses = source_statuses or []
    succeeded = [
        str(status.get("source"))
        for status in statuses
        if status.get("success")
    ]
    failed = [
        str(status.get("source"))
        for status in statuses
        if not status.get("success")
    ]
    requested = requested_sources or sorted({
        str(article.get("source", source)) for article in articles
    }) or [source]
    by_source = Counter(str(article.get("source", source)) for article in articles)
    output = {
        "schema_version": CANONICAL_SCHEMA_VERSION,
        "week": week_slug(crawled_at),
        "source": source,
        "crawled_at": iso_timestamp(crawled_at),
        "crawl_window": crawl_window or {},
        "articles": articles,
        "metadata": {
            "source_count": source_count,
            "source_config_checksum": source_config_checksum_value or "",
            "sources_requested": sorted(requested),
            "sources_succeeded": sorted(succeeded or requested),
            "sources_failed": sorted(failed),
            "source_status": sorted(statuses, key=lambda status: status["source"]),
            "sources_with_articles": dict(sorted(by_source.items())),
            "total_articles": len(articles),
            "relevant_articles": len(relevant),
            "github_links_found": len(all_github_links),
            "dedupe_count": dedupe_count,
            "errors": errors or [],
        },
    }
    output["metadata"]["artifact_checksum"] = artifact_checksum(output)
    validate_canonical_output(output)
    return output


def validate_canonical_output(output: dict[str, Any]) -> None:
    """Validate canonical external-news artifact shape."""
    if output.get("schema_version") != CANONICAL_SCHEMA_VERSION:
        raise ValueError("External news artifact has unsupported schema_version")
    if output.get("source") == "external_news" and not output.get("crawl_window"):
        raise ValueError("Canonical external news artifact requires crawl_window")
    metadata = output.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError("External news artifact requires metadata")
    required = {
        "source_config_checksum",
        "sources_requested",
        "sources_succeeded",
        "sources_failed",
        "source_status",
        "total_articles",
        "relevant_articles",
        "dedupe_count",
        "errors",
        "artifact_checksum",
    }
    missing = sorted(required - set(metadata))
    if missing:
        raise ValueError(f"External news artifact missing metadata keys: {missing}")
    expected_checksum = artifact_checksum(output)
    if metadata.get("artifact_checksum") != expected_checksum:
        raise ValueError("External news artifact checksum mismatch")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Crawl external news RSS feeds for SquadScope"
    )
    parser.add_argument(
        "--topic", default="general",
        help="Topic ID for output path (default: general)",
    )
    parser.add_argument(
        "--output", default=None,
        help="Override output file path",
    )
    parser.add_argument(
        "--since", default=None,
        help="Start date filter (YYYY-MM-DD, default: 7 days ago)",
    )
    parser.add_argument(
        "--until", default=None,
        help="End date filter (YYYY-MM-DD, default: now)",
    )
    parser.add_argument(
        "--sources",
        default=str(DEFAULT_SOURCES_PATH),
        help="Path to external RSS source config JSON",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Maximum parallel RSS fetches (default: one per source, capped at 8)",
    )
    args = parser.parse_args(argv)

    now = datetime.now(UTC)
    since = (
        datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=UTC)
        if args.since
        else now - timedelta(days=7)
    )
    until = (
        datetime.strptime(args.until, "%Y-%m-%d").replace(tzinfo=UTC)
        if args.until
        else now
    )

    source_configs = load_source_configs(Path(args.sources))
    articles, errors, statuses = crawl_sources_parallel(
        source_configs, since=since, until=until, max_workers=args.max_workers
    )
    output = build_output(
        articles,
        crawled_at=now,
        source="external_news",
        source_count=len(source_configs),
        crawl_window={
            "since": iso_timestamp(since),
            "until": iso_timestamp(until),
        },
        source_config_checksum_value=source_config_checksum(source_configs),
        requested_sources=[source.name for source in source_configs],
        source_statuses=statuses,
        errors=errors,
    )

    if args.output:
        out_path = Path(args.output)
    else:
        out_dir = raw_dir(args.topic)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{week_slug(now)}-external-news.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Crawled {output['metadata']['total_articles']} articles "
          f"from {output['metadata']['source_count']} sources "
          f"({output['metadata']['relevant_articles']} relevant, "
          f"{output['metadata']['dedupe_count']} deduped) → {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
