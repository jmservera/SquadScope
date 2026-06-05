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
DEFAULT_MAX_WORKERS = 8
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
    retries: int = 1,
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
            return feed
        return feed
    return feed  # pragma: no cover


class NewsFeedSource:
    """RSS data source following the DataSource protocol."""

    def __init__(self, config: NewsSourceConfig) -> None:
        self.config = config

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
        feed = fetch_feed(resolved_feed_url)
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
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Crawl configured RSS sources concurrently and return articles plus errors."""
    if not sources:
        return [], []

    if max_workers is not None and max_workers < 1:
        raise ValueError("--max-workers must be at least 1")
    workers = min(max_workers or len(sources), len(sources), DEFAULT_MAX_WORKERS)
    articles: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(NewsFeedSource(source).crawl, since, until): source
            for source in sources
        }
        for future in as_completed(futures):
            source = futures[future]
            try:
                articles.extend(future.result())
            except Exception as exc:  # pragma: no cover - defensive around network/parser failures
                errors.append({"source": source.name, "error": str(exc)})

    articles.sort(
        key=lambda article: (article.get("published_at", ""), article.get("source", "")),
        reverse=True,
    )
    return articles, errors


def build_output(
    articles: list[dict[str, Any]],
    crawled_at: datetime,
    *,
    source: str = "techcrunch",
    source_count: int = 1,
    errors: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Build the final output structure with metadata."""
    relevant = [a for a in articles if a["relevance_score"] >= 0.4]
    all_github_links = set()
    for a in articles:
        all_github_links.update(a.get("github_links", []))

    by_source = Counter(str(article.get("source", source)) for article in articles)
    return {
        "week": week_slug(crawled_at),
        "source": source,
        "crawled_at": iso_timestamp(crawled_at),
        "articles": articles,
        "metadata": {
            "source_count": source_count,
            "sources_with_articles": dict(sorted(by_source.items())),
            "total_articles": len(articles),
            "relevant_articles": len(relevant),
            "github_links_found": len(all_github_links),
            "errors": errors or [],
        },
    }


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
    articles, errors = crawl_sources_parallel(
        source_configs, since=since, until=until, max_workers=args.max_workers
    )
    output = build_output(
        articles,
        crawled_at=now,
        source="external_news",
        source_count=len(source_configs),
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
          f"({output['metadata']['relevant_articles']} relevant) → {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
