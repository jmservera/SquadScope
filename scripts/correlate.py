#!/usr/bin/env python3
"""Cross-source correlation engine for SquadScope.

Matches external news articles to GitHub repo activity using fuzzy matching
heuristics to identify press-correlated repositories.

Usage:
    python scripts/correlate.py [--raw data/raw/ai-ml/2026-W21.json] \
        [--techcrunch data/raw/ai-ml/2026-W21-external-news.json] \
        [--output data/analyzed/ai-ml/2026-W21-correlations.json] \
        [--topic ai-ml]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from scripts.topic_paths import analyzed_dir, raw_dir

MAX_ARTICLES_FOR_CORRELATION = 80
MAX_CORRELATIONS = 50
MAX_MATCHED_ARTICLES_PER_REPO = 5
MAX_DIVERGENCE_ARTICLES = 30
WEAK_MATCH_TYPES = {"category", "project_name"}


def log(message: str) -> None:
    print(f"[correlate] {message}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Heuristic matchers
# ---------------------------------------------------------------------------


def match_direct_link(repo: dict[str, Any], articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Match articles that contain a direct GitHub link to the repo."""
    repo_url = (repo.get("url") or "").rstrip("/").lower()
    full_name = (repo.get("full_name") or "").lower()
    if not repo_url and not full_name:
        return []

    matches = []
    for article in articles:
        for link in article.get("github_links", []):
            normalized = link.rstrip("/").lower()
            if normalized == repo_url or normalized.endswith(f"/{full_name}"):
                matches.append(article)
                break
    return matches


def match_org_name(repo: dict[str, Any], articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Match articles whose entities contain the repo owner name."""
    owner = (repo.get("owner") or "").lower()
    if not owner or len(owner) < 2:
        return []

    matches = []
    for article in articles:
        entities = [e.lower() for e in article.get("entities", [])]
        if owner in entities:
            matches.append(article)
    return matches


def _token_overlap_ratio(a: str, b: str) -> float:
    """Compute token overlap ratio between two strings."""
    tokens_a = set(re.split(r"[\s\-_]+", a.lower()))
    tokens_b = set(re.split(r"[\s\-_]+", b.lower()))
    tokens_a.discard("")
    tokens_b.discard("")
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    return len(intersection) / min(len(tokens_a), len(tokens_b))


def fuzzy_name_score(repo_name: str, text: str) -> float:
    """Compute fuzzy match score between repo name and text."""
    if not repo_name or not text:
        return 0.0
    # SequenceMatcher ratio
    seq_score = SequenceMatcher(None, repo_name.lower(), text.lower()).ratio()
    # Token overlap
    token_score = _token_overlap_ratio(repo_name, text)
    return max(seq_score, token_score)


def match_project_name(repo: dict[str, Any], articles: list[dict[str, Any]], threshold: float = 0.6) -> list[dict[str, Any]]:
    """Match articles by fuzzy matching repo name against title/entities."""
    repo_name = repo.get("name") or ""
    if not repo_name or len(repo_name) < 3:
        return []

    matches = []
    for article in articles:
        title = article.get("title") or ""
        entities = article.get("entities", [])

        # Check title
        if fuzzy_name_score(repo_name, title) >= threshold:
            matches.append(article)
            continue

        # Check individual entities
        for entity in entities:
            if fuzzy_name_score(repo_name, entity) >= threshold:
                matches.append(article)
                break
    return matches


def match_category(repo: dict[str, Any], articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Match articles whose categories overlap with repo topics."""
    topics = {t.lower() for t in (repo.get("topics") or [])}
    if not topics:
        return []

    matches = []
    for article in articles:
        categories = {c.lower() for c in (article.get("categories") or [])}
        if topics & categories:
            matches.append(article)
    return matches


def _normalized_article_url(url: str) -> str:
    """Normalize an article URL for dedupe and citation joins."""
    if not url:
        return ""
    from urllib.parse import urlparse

    parsed = urlparse(url.strip())
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{parsed.path.rstrip('/')}"


def dedupe_articles(articles: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Deduplicate cross-source/mirrored stories by normalized URL."""
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
            key = str(article.get("title", "")).strip().lower()
        if key not in grouped:
            current = dict(article)
            current["sources"] = sorted({
                str(current.get("source", "")) or "unknown",
                *[str(source) for source in current.get("sources", [])],
            })
            grouped[key] = current
            continue
        duplicates += 1
        existing = grouped[key]
        sources = set(existing.get("sources", []))
        sources.add(str(article.get("source", "")) or "unknown")
        sources.update(str(source) for source in article.get("sources", []))
        existing["sources"] = sorted(sources)
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
        key=lambda item: (
            item.get("published_at", ""),
            item.get("source", ""),
            item.get("url", ""),
            item.get("title", ""),
        ),
        reverse=True,
    )
    return deduped, duplicates


def _article_citation(article: dict[str, Any]) -> dict[str, Any]:
    """Return the bounded citation fields downstream renderers are allowed to use."""
    return {
        "title": article.get("title", ""),
        "url": article.get("url", ""),
        "source": article.get("source", "unknown"),
        "sources": article.get("sources", [article.get("source", "unknown")]),
        "published_at": article.get("published_at", ""),
        "relevance_score": article.get("relevance_score", 0),
    }


def _unique_articles(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return URL-deduped articles preserving order."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for article in articles:
        key = _normalized_article_url(str(article.get("url", ""))) or str(article)
        if key in seen:
            continue
        seen.add(key)
        unique.append(article)
    return unique


def correlation_strength(
    match_type: str,
    matched_articles: list[dict[str, Any]],
    *,
    temporal_spike: bool,
) -> str:
    """Label strong vs weak correlations without letting fuzzy/category inflate claims."""
    source_names = {
        source
        for article in matched_articles
        for source in article.get("sources", [article.get("source", "unknown")])
    }
    corroborated = len(source_names) >= 2 or len(_unique_articles(matched_articles)) >= 2
    if match_type in WEAK_MATCH_TYPES:
        return "strong" if corroborated else "weak"
    if match_type in {"direct_link", "org_name"} or temporal_spike or corroborated:
        return "strong"
    return "weak"


def has_temporal_spike(repo: dict[str, Any], stars_threshold: int = 10) -> bool:
    """Check if repo had a stars_gained spike in the same week."""
    stars_gained = repo.get("stars_gained")
    if stars_gained is None:
        return False
    return stars_gained >= stars_threshold


# ---------------------------------------------------------------------------
# Hype risk assessment
# ---------------------------------------------------------------------------


def assess_hype_risk(confidence: float, stars_gained: int | None) -> str:
    """Assess hype risk based on correlation confidence and star velocity."""
    if confidence >= 0.8:
        if stars_gained is not None and stars_gained > 100:
            return "high"
        return "medium"
    if confidence >= 0.6:
        return "medium"
    if confidence >= 0.4:
        return "low"
    return "none"


# ---------------------------------------------------------------------------
# Main correlation logic
# ---------------------------------------------------------------------------


def correlate_repo(repo: dict[str, Any], articles: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Correlate a single repo against all articles. Returns correlation or None."""
    best_confidence = 0.0
    best_type = ""
    matched_articles: list[str] = []
    matched_article_objs: list[dict[str, Any]] = []

    # Priority 1: Direct link match (confidence 1.0)
    direct = match_direct_link(repo, articles)
    if direct:
        best_confidence = 1.0
        best_type = "direct_link"
        matched_article_objs = _unique_articles(direct)[:MAX_MATCHED_ARTICLES_PER_REPO]
        matched_articles = [a["url"] for a in matched_article_objs]

    # Priority 2: Org name match (confidence 0.8)
    if not matched_articles:
        org = match_org_name(repo, articles)
        if org:
            best_confidence = 0.8
            best_type = "org_name"
            matched_article_objs = _unique_articles(org)[:MAX_MATCHED_ARTICLES_PER_REPO]
            matched_articles = [a["url"] for a in matched_article_objs]

    # Priority 3: Project name fuzzy match (confidence 0.6)
    if not matched_articles:
        fuzzy = match_project_name(repo, articles)
        if fuzzy:
            best_confidence = 0.6
            best_type = "project_name"
            matched_article_objs = _unique_articles(fuzzy)[:MAX_MATCHED_ARTICLES_PER_REPO]
            matched_articles = [a["url"] for a in matched_article_objs]

    # Priority 4: Category correlation (confidence 0.4)
    if not matched_articles:
        cat = match_category(repo, articles)
        if cat:
            best_confidence = 0.4
            best_type = "category"
            matched_article_objs = _unique_articles(cat)[:MAX_MATCHED_ARTICLES_PER_REPO]
            matched_articles = [a["url"] for a in matched_article_objs]

    if not matched_articles:
        return None

    # Priority 5: Temporal lag bonus
    press_correlated = True
    temporal_spike = has_temporal_spike(repo)
    if temporal_spike and best_type not in WEAK_MATCH_TYPES:
        best_confidence = min(best_confidence + 0.2, 1.0)
        press_correlated = True
    strength = correlation_strength(
        best_type,
        matched_article_objs,
        temporal_spike=temporal_spike,
    )

    return {
        "repo": repo.get("full_name") or f"{repo.get('owner')}/{repo.get('name')}",
        "press_correlated": press_correlated,
        "correlation_confidence": round(best_confidence, 2),
        "matched_articles": matched_articles,
        "matched_article_details": [
            _article_citation(article) for article in matched_article_objs
        ],
        "match_type": best_type,
        "correlation_strength": strength,
        "confidence_label": strength,
        "temporal_spike": temporal_spike,
        "hype_risk": assess_hype_risk(best_confidence, repo.get("stars_gained")),
    }


def _extract_article_topic(article: dict[str, Any]) -> str:
    """Extract a representative topic string from an article."""
    categories = article.get("categories", [])
    if categories:
        return categories[0]
    entities = article.get("entities", [])
    if entities:
        return entities[0]
    title = article.get("title", "")
    # Use first few meaningful words from title as fallback
    words = [w for w in re.split(r"\s+", title) if len(w) > 3]
    return " ".join(words[:3]) if words else "unknown"


def _extract_repo_topic(repo: dict[str, Any]) -> str:
    """Extract a representative topic string from a repo."""
    topics = repo.get("topics", [])
    if topics:
        return topics[0]
    description = repo.get("description") or ""
    words = [w for w in re.split(r"\s+", description) if len(w) > 3]
    return " ".join(words[:3]) if words else repo.get("name", "unknown")


def detect_divergences(
    repos: list[dict[str, Any]],
    articles: list[dict[str, Any]],
    correlations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Detect divergences — gaps between press coverage and dev activity.

    Returns two lists:
    - uncovered_tech_trends: articles/topics with no matching GitHub activity
    - unpublicized_dev_activity: repos/trends with no matching press coverage
    """
    # Find article URLs that were matched by at least one correlation
    matched_article_urls: set[str] = set()
    for corr in correlations:
        matched_article_urls.update(corr.get("matched_articles", []))

    # Unmatched articles → uncovered tech trends
    unmatched_articles = [
        a for a in articles
        if a.get("url") not in matched_article_urls
    ][:MAX_DIVERGENCE_ARTICLES]

    # Group unmatched articles by topic
    topic_articles: dict[str, list[dict[str, Any]]] = {}
    for article in unmatched_articles:
        topic = _extract_article_topic(article)
        topic_articles.setdefault(topic, []).append(article)

    uncovered_tech_trends = [
        {
            "topic": topic,
            "news_articles": [
                {"title": a.get("title", ""), "url": a.get("url", "")}
                for a in arts
            ],
            "techcrunch_articles": [
                {"title": a.get("title", ""), "url": a.get("url", "")}
                for a in arts
            ],
            "signal": "No matching GitHub activity",
        }
        for topic, arts in sorted(topic_articles.items(), key=lambda x: -len(x[1]))
    ]

    # Find repos that had no correlation match
    correlated_repo_names: set[str] = {c.get("repo", "") for c in correlations}
    unmatched_repos = [
        r for r in repos
        if (r.get("full_name") or f"{r.get('owner')}/{r.get('name')}") not in correlated_repo_names
    ]

    # Group unmatched repos by topic
    topic_repos: dict[str, list[dict[str, Any]]] = {}
    for repo in unmatched_repos:
        topic = _extract_repo_topic(repo)
        topic_repos.setdefault(topic, []).append(repo)

    unpublicized_dev_activity = [
        {
            "topic": topic,
            "github_repos": [
                {
                    "full_name": r.get("full_name") or f"{r.get('owner')}/{r.get('name')}",
                    "stars": r.get("stars", 0),
                    "stars_gained": r.get("stars_gained"),
                }
                for r in reps
            ],
            "signal": "No external press coverage",
        }
        for topic, reps in sorted(topic_repos.items(), key=lambda x: -len(x[1]))
    ]

    return {
        "uncovered_tech_trends": uncovered_tech_trends,
        "unpublicized_dev_activity": unpublicized_dev_activity,
    }


def correlate_all(repos: list[dict[str, Any]], articles: list[dict[str, Any]], week: str) -> dict[str, Any]:
    """Run correlation engine across all repos and articles."""
    articles, dedupe_count = dedupe_articles(articles)
    articles = articles[:MAX_ARTICLES_FOR_CORRELATION]
    correlations: list[dict[str, Any]] = []
    uncorrelated: list[str] = []

    for repo in repos:
        result = correlate_repo(repo, articles)
        if result:
            correlations.append(result)
        else:
            name = repo.get("full_name") or f"{repo.get('owner')}/{repo.get('name')}"
            uncorrelated.append(name)

    # Sort by confidence descending
    correlations.sort(
        key=lambda c: (
            c.get("correlation_strength") != "strong",
            -c["correlation_confidence"],
            c.get("repo", ""),
        )
    )
    correlations = correlations[:MAX_CORRELATIONS]

    articles_matched = len({url for c in correlations for url in c["matched_articles"]})

    # Detect divergences
    divergences = detect_divergences(repos, articles, correlations)

    return {
        "week": week,
        "correlations": correlations,
        "divergences": divergences,
        "uncorrelated_repos": uncorrelated,
        "metadata": {
            "repos_analyzed": len(repos),
            "articles_analyzed": len(articles),
            "correlations_found": len(correlations),
            "strong_correlations": sum(
                1 for corr in correlations
                if corr.get("correlation_strength") == "strong"
            ),
            "weak_correlations": sum(
                1 for corr in correlations
                if corr.get("correlation_strength") == "weak"
            ),
            "articles_matched": articles_matched,
            "dedupe_count": dedupe_count,
            "limits": {
                "max_articles": MAX_ARTICLES_FOR_CORRELATION,
                "max_correlations": MAX_CORRELATIONS,
                "max_matched_articles_per_repo": MAX_MATCHED_ARTICLES_PER_REPO,
            },
            "uncovered_tech_trends": len(divergences["uncovered_tech_trends"]),
            "unpublicized_dev_activity": len(divergences["unpublicized_dev_activity"]),
        },
    }


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------


def find_latest_file(directory: Path, pattern: str) -> Path | None:
    """Find the latest file matching a glob pattern in directory."""
    if not directory.exists():
        return None
    files = sorted(directory.glob(pattern), reverse=True)
    return files[0] if files else None


def load_json(path: Path) -> dict[str, Any]:
    """Load and return parsed JSON from a file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def extract_news_metadata(news_data: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any]:
    """Extract source/failure metadata from canonical or legacy news payloads."""
    if isinstance(news_data, list):
        return {
            "schema_version": 1,
            "sources_requested": ["techcrunch"],
            "sources_succeeded": ["techcrunch"],
            "sources_failed": [],
            "source_status": [],
            "errors": [],
        }
    metadata = news_data.get("metadata", {})
    return {
        "schema_version": news_data.get("schema_version", 1),
        "source_config_checksum": metadata.get("source_config_checksum", ""),
        "sources_requested": metadata.get("sources_requested", [news_data.get("source", "techcrunch")]),
        "sources_succeeded": metadata.get("sources_succeeded", []),
        "sources_failed": metadata.get("sources_failed", []),
        "source_status": metadata.get("source_status", []),
        "errors": metadata.get("errors", []),
        "artifact_checksum": metadata.get("artifact_checksum", ""),
    }


def extract_week_from_filename(path: Path) -> str:
    """Extract week slug from filename like '2026-W21.json'."""
    match = re.search(r"(\d{4}-W\d{2})", path.name)
    return match.group(1) if match else "unknown"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Cross-source correlation engine for SquadScope"
    )
    parser.add_argument(
        "--raw", default=None,
        help="Path to raw GitHub repos JSON file",
    )
    parser.add_argument(
        "--techcrunch", default=None,
        help="Path to external news articles JSON file",
    )
    parser.add_argument(
        "--output", default=None,
        help="Output file path for correlations",
    )
    parser.add_argument(
        "--topic", default="general",
        help="Topic ID for path resolution (default: general)",
    )

    args = parser.parse_args(argv)
    topic = args.topic

    # Resolve raw repos file
    if args.raw:
        raw_path = Path(args.raw)
    else:
        raw_path = find_latest_file(raw_dir(topic), "[0-9]*-W[0-9]*.json")
        if raw_path is None:
            log(f"No raw data found in {raw_dir(topic)}")
            return 1

    if not raw_path.exists():
        log(f"Raw file not found: {raw_path}")
        return 1

    # Resolve external news file, with TechCrunch-only legacy fallback.
    if args.techcrunch:
        tc_path = Path(args.techcrunch)
    else:
        tc_path = find_latest_file(raw_dir(topic), "*-external-news.json")
        if tc_path is None:
            tc_path = find_latest_file(raw_dir(topic), "*-techcrunch.json")

    # Load repos
    raw_data = load_json(raw_path)
    if isinstance(raw_data, list):
        repos = raw_data
    else:
        # The crawl output stores repos under "new_repos" and "trending_repos"
        repos = raw_data.get("repos", raw_data.get("repositories", []))
        if not repos:
            new_repos = raw_data.get("new_repos", [])
            trending_repos = raw_data.get("trending_repos", [])
            repos = new_repos + trending_repos

    # Load articles (graceful if missing)
    articles: list[dict[str, Any]] = []
    news_metadata: dict[str, Any] = {}
    if tc_path and tc_path.exists():
        tc_data = load_json(tc_path)
        news_metadata = extract_news_metadata(tc_data)
        articles = tc_data if isinstance(tc_data, list) else tc_data.get("articles", [])
    else:
        log("No external news data found; producing empty correlations")

    # Determine week
    week = extract_week_from_filename(raw_path)

    # Run correlation
    result = correlate_all(repos, articles, week)
    if news_metadata:
        result["metadata"]["news_sources"] = news_metadata

    # Write output
    if args.output:
        output_path = Path(args.output)
    else:
        out_dir = analyzed_dir(topic)
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"{week}-correlations.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.write("\n")

    log(f"Wrote {output_path}: {result['metadata']['correlations_found']} correlations from {result['metadata']['repos_analyzed']} repos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
