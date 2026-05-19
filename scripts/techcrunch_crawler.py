#!/usr/bin/env python3
"""TechCrunch RSS crawler with entity extraction for SquadScope.

Fetches articles from TechCrunch RSS feed, extracts structured metadata,
GitHub URLs, and entities (company/project names).

Usage:
    python scripts/techcrunch_crawler.py [--topic ai-ml] \
        [--output data/raw/ai-ml/2026-W21-techcrunch.json] [--since 2026-05-11]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import feedparser

from scripts.topic_paths import raw_dir

FEED_URL = "https://techcrunch.com/feed/"

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


def fetch_feed(url: str = FEED_URL, retries: int = 1) -> Any:
    """Fetch and parse RSS feed with retry on failure."""
    for attempt in range(retries + 1):
        feed = feedparser.parse(url)
        if feed.bozo and not feed.entries:
            if attempt < retries:
                time.sleep(2)
                continue
            # Return partial result even on failure
            return feed
        return feed
    return feed  # pragma: no cover


class TechCrunchSource:
    """TechCrunch RSS data source following the DataSource protocol."""

    def get_name(self) -> str:
        return "techcrunch"

    def get_rate_limits(self) -> dict:
        return {"requests_per_minute": 10}

    def crawl(
        self,
        since: datetime,
        until: datetime,
        feed_url: str = FEED_URL,
    ) -> list[dict[str, Any]]:
        """Crawl TechCrunch RSS feed and return structured articles."""
        feed = fetch_feed(feed_url)
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


def build_output(
    articles: list[dict[str, Any]],
    crawled_at: datetime,
) -> dict[str, Any]:
    """Build the final output structure with metadata."""
    relevant = [a for a in articles if a["relevance_score"] >= 0.4]
    all_github_links = set()
    for a in articles:
        all_github_links.update(a.get("github_links", []))

    return {
        "week": week_slug(crawled_at),
        "source": "techcrunch",
        "crawled_at": iso_timestamp(crawled_at),
        "articles": articles,
        "metadata": {
            "total_articles": len(articles),
            "relevant_articles": len(relevant),
            "github_links_found": len(all_github_links),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Crawl TechCrunch RSS feed for SquadScope"
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

    source = TechCrunchSource()
    articles = source.crawl(since=since, until=until)
    output = build_output(articles, crawled_at=now)

    if args.output:
        out_path = Path(args.output)
    else:
        out_dir = raw_dir(args.topic)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{week_slug(now)}-techcrunch.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Crawled {output['metadata']['total_articles']} articles "
          f"({output['metadata']['relevant_articles']} relevant) → {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
